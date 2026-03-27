"""PACER Authentication API client.

Uses the PACER REST API to obtain authentication tokens for CM/ECF access.
Docs: https://pacer.uscourts.gov/help/pacer/pacer-authentication-api-user-guide
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import httpx
import keyring

from ecfiler.logging import get_logger

logger = get_logger(__name__)

PACER_AUTH_URL = "https://pacer.login.uscourts.gov/services/cso-auth"
PACER_QA_AUTH_URL = "https://qa-pacer.login.uscourts.gov/services/cso-auth"
KEYRING_SERVICE = "ecfiler-pacer"

# Token lifetime: PACER tokens are valid for ~60 minutes
TOKEN_TTL_SECONDS = 55 * 60  # Refresh 5 min before expiry


@dataclass
class PacerToken:
    """An authenticated PACER session token."""

    token: str
    obtained_at: float

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.obtained_at) > TOKEN_TTL_SECONDS


class PacerAuthError(Exception):
    """Raised when PACER authentication fails."""


class PacerAuth:
    """Manages PACER authentication and token lifecycle."""

    def __init__(self, username: str, use_qa: bool = False) -> None:
        self.username = username
        self.base_url = PACER_QA_AUTH_URL if use_qa else PACER_AUTH_URL
        self._token: PacerToken | None = None
        self._client = httpx.Client(timeout=30.0)

    def store_password(self, password: str) -> None:
        """Store PACER password in the system keyring."""
        keyring.set_password(KEYRING_SERVICE, self.username, password)

    def get_password(self) -> str:
        """Retrieve PACER password from the system keyring."""
        password = keyring.get_password(KEYRING_SERVICE, self.username)
        if not password:
            raise PacerAuthError(
                f"No PACER password found for {self.username}. "
                "Run: ecfiler setup-credentials"
            )
        return password

    def authenticate(self, retries: int = 2) -> PacerToken:
        """Authenticate with PACER and obtain a session token.

        Returns a cached token if still valid. Retries on transient failures.
        """
        if self._token and not self._token.is_expired:
            logger.debug("Using cached PACER token")
            return self._token

        logger.info("Authenticating with PACER as %s", self.username)
        password = self.get_password()
        last_error: Exception | None = None

        for attempt in range(1, retries + 2):
            try:
                response = self._client.post(
                    self.base_url,
                    json={
                        "loginId": self.username,
                        "password": password,
                        "clientCode": "ecfiler",
                        "redactFlag": "1",
                    },
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )
                response.raise_for_status()
                break
            except httpx.HTTPStatusError as e:
                # Don't retry auth failures (wrong password, etc.)
                raise PacerAuthError(f"PACER auth request failed: {e}") from e
            except httpx.RequestError as e:
                last_error = e
                if attempt <= retries:
                    import time
                    time.sleep(2 * attempt)
                    continue
                raise PacerAuthError(
                    f"Cannot reach PACER auth service after {retries + 1} attempts: {e}"
                ) from e

        data = response.json()

        # PACER returns the token in the nextGenCSO field
        token_value = data.get("nextGenCSO")
        if not token_value:
            error_msg = data.get("errorDescription", "Unknown error")
            raise PacerAuthError(f"PACER authentication failed: {error_msg}")

        self._token = PacerToken(token=token_value, obtained_at=time.time())
        return self._token

    def get_token(self) -> str:
        """Get a valid token string, authenticating if needed."""
        return self.authenticate().token

    def invalidate(self) -> None:
        """Clear the cached token (e.g., on logout or session error)."""
        self._token = None

    def close(self) -> None:
        """Clean up HTTP client."""
        self._client.close()
