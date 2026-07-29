"""Tests for persistent PACER CSO session handling."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from ecfiler.pacer_session import PacerSessionStore, SessionObservation


def _store(tmp_path):
    return PacerSessionStore(log_path=tmp_path / "pacer-session.jsonl")


def _obs(**kw):
    base = dict(
        at=datetime.now(timezone.utc).isoformat(),
        authenticated=True,
        environment="qa",
    )
    base.update(kw)
    return SessionObservation(**base)


def test_record_and_read_back(tmp_path):
    store = _store(tmp_path)
    store.record(_obs(note="interactive-login"))
    obs = store.observations()
    assert len(obs) == 1
    assert obs[0].note == "interactive-login"


def test_log_is_owner_only(tmp_path):
    store = _store(tmp_path)
    store.record(_obs())
    assert oct(store.log_path.stat().st_mode)[-3:] == "600"


def test_corrupt_lines_are_skipped(tmp_path):
    store = _store(tmp_path)
    store.record(_obs())
    with store.log_path.open("a") as fh:
        fh.write("not json\n")
        fh.write(json.dumps({"unexpected": "shape"}) + "\n")
    assert len(store.observations()) == 1


def test_lifetime_unknown_without_data(tmp_path):
    stats = _store(tmp_path).observed_lifetime()
    assert stats["known"] is False
    assert stats["longest_alive_seconds"] is None


def test_lifetime_reports_measured_bounds(tmp_path):
    store = _store(tmp_path)
    store.record(_obs(authenticated=True, age_seconds=3600.0, note="probe"))
    store.record(_obs(authenticated=True, age_seconds=7200.0, note="probe"))
    store.record(_obs(authenticated=False, age_seconds=36000.0, note="probe"))
    stats = store.observed_lifetime()
    assert stats["known"] is True
    assert stats["longest_alive_seconds"] == 7200.0
    assert stats["shortest_expired_seconds"] == 36000.0


def test_last_login_at_ignores_probes(tmp_path):
    store = _store(tmp_path)
    old = (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
    store.record(_obs(at=old, note="interactive-login"))
    store.record(_obs(note="probe"))
    recorded = store.last_login_at()
    assert recorded == datetime.fromisoformat(old).timestamp()


def test_last_login_at_none_when_never_logged_in(tmp_path):
    store = _store(tmp_path)
    store.record(_obs(authenticated=False, note="interactive-login-timeout"))
    assert store.last_login_at() is None


def test_browser_session_accepts_user_data_dir(tmp_path):
    """Persistent-profile plumbing exists and is off by default."""
    from ecfiler.browser.session import BrowserSession

    assert BrowserSession().user_data_dir is None
    assert BrowserSession(user_data_dir=tmp_path / "p").user_data_dir == tmp_path / "p"
