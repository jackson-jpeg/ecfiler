"""Persistent PACER CSO browser session.

PACER's Central Sign-On enforces MFA on production accounts, so an unattended
process cannot authenticate from scratch: something has to read a code from a
phone or authenticator app. Rather than defeat that (which we will not do), we
persist the browser session it produces.

The model:

* A human logs in **once**, in a headed Chromium whose profile lives in
  ``~/.ecfiler/pacer-profile``. They complete username, password, and MFA.
* Chromium writes the CSO session cookies into that on-disk profile.
* Later filing runs reuse the same profile. If the session is still live they
  proceed unattended; if it has expired they stop and ask for one more
  interactive login rather than half-filing.

Session lifetime is **measured, not assumed**: every observation is appended to
``~/.ecfiler/pacer-session.jsonl``, so the real expiry window comes from
evidence collected on this machine. ``PacerSessionStore.observed_lifetime()``
reports what has actually been seen. Until an account has been logged in and
probed, it honestly reports "unknown" rather than a guess.

Note the distinction from ``ecfiler/pacer_auth.py``: that module calls the
PACER *authentication API*, whose tokens are documented at roughly 60 minutes
and which is unrelated to how long a *browser* CSO session stays valid. Do not
conflate the two numbers.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

from ecfiler.config import CONFIG_DIR
from ecfiler.logging import get_logger

logger = get_logger(__name__)

PROFILE_DIR = CONFIG_DIR / "pacer-profile"
OBSERVATION_LOG = CONFIG_DIR / "pacer-session.jsonl"

PACER_CSO_LOGIN_URL = "https://pacer.login.uscourts.gov/csologin/login.jsf"
# QA CSO mirrors production at qa-login.uscourts.gov ("qa-pacer.login"
# does not resolve — measured 2026-07-29, ledger L15).
PACER_QA_CSO_LOGIN_URL = "https://qa-login.uscourts.gov/csologin/login.jsf"
PACER_ACCOUNT_URL = "https://pacer.uscourts.gov/my-account-billing/manage-my-account-login"

# Markers that indicate an authenticated CSO session on the account page.
_AUTHED_MARKERS = ("Log Out", "Logout", "Manage My Account", "Account Balance")
# Markers that indicate we were bounced back to a login form.
_LOGIN_MARKERS = ("loginForm:loginName", "Central Sign-On", "Forgot password")


@dataclass
class SessionObservation:
    """One measurement of whether the persisted session was still valid."""

    at: str
    authenticated: bool
    environment: str
    age_seconds: float | None = None
    note: str = ""


class PacerSessionStore:
    """Records and reports observed CSO session lifetime.

    Everything here is evidence collected on this machine. Nothing is
    extrapolated from PACER documentation, which does not publish the browser
    session timeout.
    """

    def __init__(self, log_path: Path | None = None) -> None:
        self.log_path = log_path or OBSERVATION_LOG

    def record(self, obs: SessionObservation) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a") as fh:
            fh.write(json.dumps(asdict(obs)) + "\n")
        self.log_path.chmod(0o600)

    def observations(self) -> list[SessionObservation]:
        if not self.log_path.exists():
            return []
        out: list[SessionObservation] = []
        for line in self.log_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                out.append(SessionObservation(**json.loads(line)))
            except (json.JSONDecodeError, TypeError):
                continue
        return out

    def last_login_at(self) -> float | None:
        """Epoch seconds of the most recent successful interactive login."""
        for obs in reversed(self.observations()):
            if obs.authenticated and obs.note == "interactive-login":
                return datetime.fromisoformat(obs.at).timestamp()
        return None

    def observed_lifetime(self) -> dict[str, object]:
        """What we have actually measured about session lifetime.

        Returns the longest age at which the session was still valid and the
        shortest age at which it was found expired. With no data, says so.
        """
        obs = self.observations()
        alive = [o.age_seconds for o in obs if o.authenticated and o.age_seconds]
        dead = [o.age_seconds for o in obs if not o.authenticated and o.age_seconds]
        return {
            "observations": len(obs),
            "longest_alive_seconds": max(alive) if alive else None,
            "shortest_expired_seconds": min(dead) if dead else None,
            "known": bool(alive or dead),
        }


def establish_session(
    use_qa: bool = False,
    timeout_seconds: int = 600,
    profile_dir: Path | None = None,
) -> bool:
    """Open a headed browser for a one-time interactive CSO login.

    Blocks until the login lands on an authenticated page or the timeout
    expires. ECFiler never types the password or the MFA code — the human at
    the keyboard does, so the credential and the second factor never pass
    through this process.

    Returns True if an authenticated session was established and persisted.
    """
    from ecfiler.browser.session import BrowserSession

    profile = profile_dir or PROFILE_DIR
    login_url = PACER_QA_CSO_LOGIN_URL if use_qa else PACER_CSO_LOGIN_URL
    env = "qa" if use_qa else "production"
    store = PacerSessionStore()

    session = BrowserSession(headless=False, user_data_dir=profile)
    page = session.start()
    try:
        page.goto(login_url)
        logger.info("Awaiting interactive PACER login (MFA is entered by the user)")
        deadline = time.time() + timeout_seconds
        authenticated = False
        while time.time() < deadline:
            try:
                body = page.inner_text("body")
            except Exception:
                time.sleep(2)
                continue
            if any(m in body for m in _AUTHED_MARKERS) and not any(
                m in body for m in _LOGIN_MARKERS
            ):
                authenticated = True
                break
            time.sleep(2)

        store.record(
            SessionObservation(
                at=datetime.now(timezone.utc).isoformat(),
                authenticated=authenticated,
                environment=env,
                note="interactive-login" if authenticated else "interactive-login-timeout",
            )
        )
        return authenticated
    finally:
        session.stop()


def probe_session(use_qa: bool = False, profile_dir: Path | None = None) -> bool:
    """Check headlessly whether the persisted session is still authenticated.

    Records the result with the session's age so lifetime accumulates as
    measured fact. Cheap enough to call before every filing run.
    """
    from ecfiler.browser.session import BrowserSession

    profile = profile_dir or PROFILE_DIR
    store = PacerSessionStore()
    if not profile.exists():
        return False

    last = store.last_login_at()
    age = (time.time() - last) if last else None

    session = BrowserSession(headless=True, user_data_dir=profile)
    page = session.start()
    try:
        page.goto(PACER_ACCOUNT_URL)
        page.wait_for_load_state("networkidle")
        body = page.inner_text("body")
        authenticated = any(m in body for m in _AUTHED_MARKERS) and not any(
            m in body for m in _LOGIN_MARKERS
        )
    except Exception as e:
        logger.warning("Session probe failed: %s", e)
        authenticated = False
    finally:
        session.stop()

    store.record(
        SessionObservation(
            at=datetime.now(timezone.utc).isoformat(),
            authenticated=authenticated,
            environment="qa" if use_qa else "production",
            age_seconds=age,
            note="probe",
        )
    )
    return authenticated
