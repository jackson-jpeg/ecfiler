"""macOS Keychain backend for non-GUI sessions (SSH, cron, launchd).

The stock ``keyring`` macOS backend cannot target a keychain other than the
default search path (keyring#623) and its lookup aborts with
``errSecInteractionNotAllowed`` (-25308) the moment the search touches the
locked login keychain — which is always the case in an SSH session, where
macOS creates a fresh security session with every keychain locked.

The ``security`` CLI has neither problem: it can address a specific keychain
file directly. This backend shells out to it, targeting the dedicated
``ecfiler.keychain-db`` created by ``scripts/mac/keychain-setup.sh``.

Activated only when both are true (otherwise it reports itself non-viable and
the platform default backend is used, so Linux and interactive GUI terminals
are unaffected):

* the platform is macOS, and
* ``ECFILER_KEYCHAIN`` names the keychain file (set by ``scripts/mac/ecfiler-mac``).
"""

from __future__ import annotations

import os
import subprocess
import sys

import keyring.backend
import keyring.errors
from keyring.compat import properties


def _target_keychain() -> str:
    return os.environ.get("ECFILER_KEYCHAIN", "")


class SecurityCliKeychain(keyring.backend.KeyringBackend):
    """Keychain access via /usr/bin/security, scoped to one keychain file."""

    @properties.classproperty
    def priority(cls) -> float:  # type: ignore[override]
        if sys.platform != "darwin":
            raise RuntimeError("macOS only")
        if not _target_keychain():
            raise RuntimeError("ECFILER_KEYCHAIN not set")
        # Above the stock macOS backend (5) so we win when explicitly enabled.
        return 30.0

    def _run(self, args: list[str], **kwargs) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["/usr/bin/security", *args], capture_output=True, text=True, **kwargs
        )

    def get_password(self, service: str, username: str) -> str | None:
        proc = self._run(
            [
                "find-generic-password",
                "-s", service,
                "-a", username,
                "-w", _target_keychain(),
            ]
        )
        if proc.returncode != 0:
            return None
        return proc.stdout.rstrip("\n")

    def set_password(self, service: str, username: str, password: str) -> None:
        # Delete-then-add: updating an existing item rewrites its ACL, which
        # requires GUI interaction; a fresh add with -A does not.
        self._run(["delete-generic-password", "-s", service, "-a", username, _target_keychain()])
        proc = self._run(
            [
                "add-generic-password",
                "-s", service,
                "-a", username,
                "-w", password,
                "-A",
                _target_keychain(),
            ]
        )
        if proc.returncode != 0:
            raise keyring.errors.PasswordSetError(proc.stderr.strip())

    def delete_password(self, service: str, username: str) -> None:
        proc = self._run(
            ["delete-generic-password", "-s", service, "-a", username, _target_keychain()]
        )
        if proc.returncode != 0:
            raise keyring.errors.PasswordDeleteError(proc.stderr.strip())
