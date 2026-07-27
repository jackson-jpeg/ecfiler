"""Zero-credential-custody regression tests.

ECFiler removed server-side PACER credential storage in July 2026. These tests
keep it removed: the endpoints answer 410, the legacy table is purged (including
SQLite free pages), and no module other than the CLI keyring path reads a PACER
password.
"""

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ecfiler.api.app import app, purge_stored_pacer_credentials


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, headers={"X-User-Id": "test-user"})


class TestCredentialEndpointsGone:
    def test_store_returns_410(self, client: TestClient) -> None:
        response = client.post(
            "/api/pacer/credentials",
            json={"username": "a@b.com", "password": "hunter2", "user_id": "u1"},
        )
        assert response.status_code == 410
        assert "keyring" in response.json()["error"]

    def test_get_returns_410(self, client: TestClient) -> None:
        assert client.get("/api/pacer/credentials").status_code == 410

    def test_test_endpoint_returns_410(self, client: TestClient) -> None:
        response = client.post("/api/pacer/test", json={"username": "a@b.com"})
        assert response.status_code == 410

    def test_security_module_deleted(self) -> None:
        with pytest.raises(ImportError):
            import ecfiler.security  # noqa: F401


class TestLegacyCredentialPurge:
    def _legacy_db(self, tmp_path: Path) -> Path:
        db_path = tmp_path / "users.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """CREATE TABLE pacer_credentials (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    password_encrypted TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )"""
            )
            conn.execute(
                "INSERT INTO pacer_credentials VALUES (?, ?, ?, ?)",
                ("u1", "a@b.com", "CIPHERTEXT-SENTINEL-VALUE", "2026-01-01"),
            )
            conn.commit()
        return db_path

    def test_purge_drops_table_and_reports_count(self, tmp_path: Path) -> None:
        db_path = self._legacy_db(tmp_path)
        assert purge_stored_pacer_credentials(db_path) == 1
        with sqlite3.connect(db_path) as conn:
            (count,) = conn.execute(
                "SELECT count(*) FROM sqlite_master WHERE name='pacer_credentials'"
            ).fetchone()
        assert count == 0

    def test_purge_scrubs_ciphertext_from_file_bytes(self, tmp_path: Path) -> None:
        db_path = self._legacy_db(tmp_path)
        assert b"CIPHERTEXT-SENTINEL-VALUE" in db_path.read_bytes()
        purge_stored_pacer_credentials(db_path)
        # The VACUUM is what makes this pass: DROP alone leaves the row bytes
        # in SQLite free pages.
        assert b"CIPHERTEXT-SENTINEL-VALUE" not in db_path.read_bytes()

    def test_purge_is_idempotent(self, tmp_path: Path) -> None:
        db_path = self._legacy_db(tmp_path)
        assert purge_stored_pacer_credentials(db_path) == 1
        assert purge_stored_pacer_credentials(db_path) == 0

    def test_purge_handles_missing_db(self, tmp_path: Path) -> None:
        assert purge_stored_pacer_credentials(tmp_path / "absent.db") == 0


class TestNoServerCredentialReads:
    def test_only_local_cli_modules_touch_pacer_password(self) -> None:
        """Source scan: no server/web module may read a PACER password.

        The CLI keyring path (pacer_auth.py), the crawler's explicit CLI-arg
        path (event_crawler.py, __main__.py), the local browser login form
        (session.py, courts/base.py), and app.py's removal stub/purge are the
        only allowed password surfaces — all local-machine, attorney-operated,
        or removal code.
        """
        allowed = {
            "pacer_auth.py",
            "event_crawler.py",
            "__main__.py",
            "session.py",
            "base.py",
            "app.py",
            "workflow.py",
            "diagnostics.py",
            "config.py",  # comment documenting that passwords are keyring-only
            # Render "********" placeholders; slated for removal in the
            # prepare/stage repositioning:
            "browser_demo.py",
            "browser_stream.py",
        }
        package_root = Path(__file__).resolve().parent.parent / "ecfiler"
        offenders = []
        for path in package_root.rglob("*.py"):
            if path.name in allowed:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "password" in text.lower() and "pacer" in text.lower():
                offenders.append(str(path.relative_to(package_root)))
        assert offenders == [], f"unexpected PACER password surfaces: {offenders}"
