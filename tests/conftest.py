"""Shared test configuration.

The API refuses to start without auth configuration (CLERK_ISSUER or an explicit
dev-mode opt-in). Tests run in dev mode: X-User-Id headers are honored.
"""

import os

os.environ.setdefault("ECFILER_DEV_AUTH", "1")
