"""Client-side throttling for all PACER/CM-ECF traffic.

Policy this module enforces:
- at most one in-flight request per court, at most two globally;
- a minimum interval (with jitter) between requests to the same host;
- exponential backoff with jitter on failures;
- bulk operations (crawls, batch pulls) run in the AO's requested
  6 p.m.–6 a.m. Central window unless explicitly overridden. Interactive
  single filings are exempt — the guidance targets bulk retrieval, and
  attorneys have daytime deadlines.
"""

from __future__ import annotations

import random
import threading
import time
from datetime import datetime
from zoneinfo import ZoneInfo

from ecfiler.logging import get_logger

logger = get_logger(__name__)

CENTRAL_TZ = ZoneInfo("America/Chicago")

# AO bulk guidance: 6 p.m.–6 a.m. Central Time.
BULK_WINDOW_START_HOUR = 18
BULK_WINDOW_END_HOUR = 6


def is_bulk_window_open(now: datetime | None = None) -> bool:
    """True when bulk PACER traffic is within the AO's requested window."""
    now_ct = (now or datetime.now(tz=CENTRAL_TZ)).astimezone(CENTRAL_TZ)
    return now_ct.hour >= BULK_WINDOW_START_HOUR or now_ct.hour < BULK_WINDOW_END_HOUR


class Throttle:
    """Per-key (usually per-court) pacing plus a small global concurrency cap."""

    def __init__(
        self,
        min_interval: float = 1.0,
        jitter: float = 0.5,
        per_key_concurrency: int = 1,
        global_concurrency: int = 2,
    ) -> None:
        self.min_interval = min_interval
        self.jitter = jitter
        self._global_sem = threading.Semaphore(global_concurrency)
        self._per_key_concurrency = per_key_concurrency
        self._key_sems: dict[str, threading.Semaphore] = {}
        self._last_request: dict[str, float] = {}
        self._lock = threading.Lock()

    def _sem_for(self, key: str) -> threading.Semaphore:
        with self._lock:
            if key not in self._key_sems:
                self._key_sems[key] = threading.Semaphore(self._per_key_concurrency)
            return self._key_sems[key]

    def pace(self, key: str) -> None:
        """Block until a request to `key` is allowed, then record it.

        Enforces min_interval (+ random jitter) since the previous request to
        the same key. Callers that need concurrency limits should use
        `slot(key)` around the whole request instead.
        """
        with self._lock:
            last = self._last_request.get(key, 0.0)
        wait = (last + self.min_interval + random.uniform(0, self.jitter)) - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        with self._lock:
            self._last_request[key] = time.monotonic()

    def slot(self, key: str) -> "_ThrottleSlot":
        """Context manager: concurrency caps + pacing for one request."""
        return _ThrottleSlot(self, key)

    def retry(self, fn, *, key: str, attempts: int = 4, base_delay: float = 2.0):
        """Run fn() with pacing and exponential backoff + jitter on exceptions."""
        last_exc: Exception | None = None
        for attempt in range(1, attempts + 1):
            with self.slot(key):
                try:
                    return fn()
                except Exception as exc:
                    last_exc = exc
                    if attempt == attempts:
                        break
                    delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 1)
                    logger.warning(
                        "Request to %s failed (attempt %d/%d): %s — backing off %.1fs",
                        key, attempt, attempts, exc, delay,
                    )
                    time.sleep(delay)
        assert last_exc is not None
        raise last_exc


class _ThrottleSlot:
    def __init__(self, throttle: Throttle, key: str) -> None:
        self._throttle = throttle
        self._key = key
        self._key_sem = throttle._sem_for(key)

    def __enter__(self) -> None:
        self._throttle._global_sem.acquire()
        self._key_sem.acquire()
        self._throttle.pace(self._key)

    def __exit__(self, *args: object) -> None:
        self._key_sem.release()
        self._throttle._global_sem.release()


# Shared default instance for all PACER/CM-ECF clients in this process.
DEFAULT_THROTTLE = Throttle()
