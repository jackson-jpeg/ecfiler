"""PACER traffic discipline: honest UA, throttling, token hygiene, trace naming."""

from __future__ import annotations

import logging
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from ecfiler.browser.throttle import Throttle, is_bulk_window_open
from ecfiler.logging import TokenRedactionFilter
from ecfiler.useragent import USER_AGENT


class TestUserAgent:
    def test_identifies_ecfiler(self) -> None:
        assert USER_AGENT.startswith("ECFiler/")
        assert "ecfiler.com" in USER_AGENT

    def test_no_browser_spoofing(self) -> None:
        for spoof in ("Mozilla", "Chrome", "Safari", "AppleWebKit"):
            assert spoof not in USER_AGENT

    def test_playwright_context_uses_it(self) -> None:
        import inspect

        from ecfiler.browser import session

        source = inspect.getsource(session)
        assert "USER_AGENT" in source
        assert "Mozilla/5.0" not in source


class TestThrottle:
    def test_pace_enforces_min_interval(self) -> None:
        throttle = Throttle(min_interval=0.2, jitter=0.0)
        throttle.pace("nysd")
        start = time.monotonic()
        throttle.pace("nysd")
        assert time.monotonic() - start >= 0.19

    def test_pace_is_per_key(self) -> None:
        throttle = Throttle(min_interval=5.0, jitter=0.0)
        throttle.pace("nysd")
        start = time.monotonic()
        throttle.pace("cand")  # different court — no wait
        assert time.monotonic() - start < 1.0

    def test_retry_backs_off_and_raises(self) -> None:
        throttle = Throttle(min_interval=0.0, jitter=0.0)
        calls = []

        def failing() -> None:
            calls.append(1)
            raise ValueError("boom")

        try:
            throttle.retry(failing, key="pcl", attempts=2, base_delay=0.01)
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")
        assert len(calls) == 2

    def test_retry_returns_on_success(self) -> None:
        throttle = Throttle(min_interval=0.0, jitter=0.0)
        assert throttle.retry(lambda: 42, key="pcl", attempts=2) == 42


class TestBulkWindow:
    CT = ZoneInfo("America/Chicago")

    def test_evening_is_open(self) -> None:
        assert is_bulk_window_open(datetime(2026, 7, 27, 19, 0, tzinfo=self.CT))

    def test_early_morning_is_open(self) -> None:
        assert is_bulk_window_open(datetime(2026, 7, 27, 5, 59, tzinfo=self.CT))

    def test_business_hours_closed(self) -> None:
        assert not is_bulk_window_open(datetime(2026, 7, 27, 12, 0, tzinfo=self.CT))

    def test_six_am_boundary_closed(self) -> None:
        assert not is_bulk_window_open(datetime(2026, 7, 27, 6, 0, tzinfo=self.CT))

    def test_six_pm_boundary_open(self) -> None:
        assert is_bulk_window_open(datetime(2026, 7, 27, 18, 0, tzinfo=self.CT))

    def test_utc_input_converted(self) -> None:
        # 23:00 UTC == 18:00 CDT in July — window just opened
        utc = datetime(2026, 7, 27, 23, 0, tzinfo=ZoneInfo("UTC"))
        assert is_bulk_window_open(utc)


class TestTokenRedaction:
    def _redact(self, msg: str, *args: object) -> str:
        record = logging.LogRecord(
            name="ecfiler.test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg=msg,
            args=args or None,
            exc_info=None,
        )
        TokenRedactionFilter().filter(record)
        return record.getMessage()

    def test_csession_url_redacted(self) -> None:
        out = self._redact(
            "Token login URL: https://ecf.nysd.uscourts.gov/cgi-bin/login.pl?"
            "csession=AbCdEf0123456789TokenTokenToken"
        )
        assert "TokenToken" not in out
        assert "[REDACTED]" in out

    def test_nextgencso_value_redacted(self) -> None:
        out = self._redact("cookie NextGenCSO=AbCdEf0123456789TokenTokenToken set")
        assert "TokenToken" not in out

    def test_formatted_args_redacted(self) -> None:
        out = self._redact(
            "URL: %s", "https://x.gov/login.pl?csession=AbCdEf0123456789TokenTokenToken"
        )
        assert "TokenToken" not in out

    def test_normal_messages_untouched(self) -> None:
        assert self._redact("Filed case %s", "1:24-cv-01234") == "Filed case 1:24-cv-01234"


class TestTraceNaming:
    def test_safe_label(self) -> None:
        from ecfiler.browser.session import _safe_label

        assert _safe_label("1:24-cv-01234") == "1-24-cv-01234"
        assert _safe_label("") == "session"

    def test_no_fixed_latest_trace_name(self) -> None:
        import inspect

        from ecfiler.browser import session

        assert "latest_trace" not in inspect.getsource(session)
