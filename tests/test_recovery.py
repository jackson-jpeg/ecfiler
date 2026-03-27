"""Tests for browser error recovery."""

import pytest

from ecfiler.browser.recovery import (
    FilingLockedError,
    SessionExpiredError,
    retry_on_error,
)
from ecfiler.courts.base import ECFFormError


class TestRetryOnError:
    def test_succeeds_first_try(self) -> None:
        result = retry_on_error(lambda: "ok", description="test")
        assert result == "ok"

    def test_retries_on_ecf_error(self) -> None:
        attempts = [0]

        def flaky():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ECFFormError("transient")
            return "recovered"

        result = retry_on_error(flaky, max_retries=2, delay=0.01, description="flaky")
        assert result == "recovered"
        assert attempts[0] == 2

    def test_fails_after_max_retries(self) -> None:
        def always_fails():
            raise ECFFormError("persistent")

        with pytest.raises(ECFFormError, match="persistent"):
            retry_on_error(always_fails, max_retries=1, delay=0.01, description="fail")

    def test_no_retry_on_session_expired(self) -> None:
        attempts = [0]

        def session_dead():
            attempts[0] += 1
            raise SessionExpiredError("expired")

        with pytest.raises(SessionExpiredError):
            retry_on_error(session_dead, max_retries=3, delay=0.01)

        assert attempts[0] == 1  # No retries

    def test_no_retry_on_filing_locked(self) -> None:
        attempts = [0]

        def locked():
            attempts[0] += 1
            raise FilingLockedError("locked")

        with pytest.raises(FilingLockedError):
            retry_on_error(locked, max_retries=3, delay=0.01)

        assert attempts[0] == 1


class TestErrorTypes:
    def test_session_expired_is_ecf_error(self) -> None:
        assert issubclass(SessionExpiredError, ECFFormError)

    def test_filing_locked_is_ecf_error(self) -> None:
        assert issubclass(FilingLockedError, ECFFormError)
