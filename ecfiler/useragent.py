"""ECFiler's identifying User-Agent.

Every request ECFiler makes to PACER or CM/ECF — Playwright or httpx —
identifies itself honestly. One constant, one place, so an emergency change
is a one-line edit.
"""

from ecfiler import __version__

USER_AGENT = (
    f"ECFiler/{__version__} "
    f"(+https://ecfiler.com/automation; contact: support@ecfiler.com)"
)
