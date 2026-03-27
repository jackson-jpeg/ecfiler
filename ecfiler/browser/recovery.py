"""Error recovery for CM/ECF browser automation.

CM/ECF has several common failure modes that can be recovered from
without restarting the entire filing process:

- Session timeout (re-authenticate and resume)
- Stale page / navigation error (go back and retry)
- Document upload failure (retry upload)
- Transient JavaScript errors (wait and retry)
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Callable, TypeVar

from ecfiler.courts.base import ECFFormError
from ecfiler.logging import get_logger

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = get_logger(__name__)

T = TypeVar("T")


class SessionExpiredError(ECFFormError):
    """Raised when the CM/ECF session has expired."""


class FilingLockedError(ECFFormError):
    """Raised when another user has the filing locked."""


def retry_on_error(
    action: Callable[[], T],
    max_retries: int = 2,
    delay: float = 2.0,
    description: str = "",
) -> T:
    """Retry a browser action on transient failures.

    Args:
        action: The callable to retry
        max_retries: Maximum number of retries
        delay: Seconds between retries (doubles each time)
        description: Human-readable description for logging

    Returns:
        The action's return value

    Raises:
        The last exception if all retries fail
    """
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 2):
        try:
            return action()
        except SessionExpiredError:
            raise  # Don't retry session expiry — need re-auth
        except FilingLockedError:
            raise  # Don't retry locks — need to wait
        except ECFFormError as e:
            last_error = e
            if attempt <= max_retries:
                wait = delay * attempt
                logger.warning(
                    "Attempt %d/%d failed for '%s': %s — retrying in %.1fs",
                    attempt,
                    max_retries + 1,
                    description,
                    e,
                    wait,
                )
                time.sleep(wait)
            else:
                logger.error(
                    "All %d attempts failed for '%s': %s",
                    max_retries + 1,
                    description,
                    e,
                )
        except Exception as e:
            # Non-ECF errors (Playwright timeout, etc.) — retry once
            last_error = e
            if attempt <= 1:
                logger.warning("Unexpected error in '%s': %s — retrying", description, e)
                time.sleep(delay)
            else:
                raise

    raise last_error  # type: ignore[misc]


def detect_session_expired(page: Page) -> bool:
    """Check if the CM/ECF session has expired.

    Common indicators:
    - Redirected to login page
    - "Session expired" message
    - "Please log in" message
    """
    url = page.url.lower()
    if "login" in url or "logout" in url:
        return True

    text = page.inner_text("body").lower()
    expired_indicators = [
        "session expired",
        "session has expired",
        "please log in",
        "login required",
        "your session has timed out",
    ]
    return any(indicator in text for indicator in expired_indicators)


def detect_filing_locked(page: Page) -> bool:
    """Check if the filing is locked by another user."""
    text = page.inner_text("body").lower()
    lock_indicators = [
        "filing is locked",
        "case is locked",
        "another user",
        "locked for editing",
    ]
    return any(indicator in text for indicator in lock_indicators)


def check_page_state(page: Page) -> None:
    """Check the page state and raise appropriate errors.

    Call this after each navigation/action to catch problems early.
    """
    if detect_session_expired(page):
        raise SessionExpiredError("CM/ECF session has expired — re-authentication required")

    if detect_filing_locked(page):
        raise FilingLockedError("Filing is locked by another user — try again later")
