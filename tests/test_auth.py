"""API authentication hardening tests.

The rule under test: a verified Clerk JWT is the only production credential;
X-User-Id is honored only under an explicit ECFILER_DEV_AUTH=1 opt-in; missing
auth config aborts startup instead of degrading to unauthenticated.
"""

import pytest
from fastapi.testclient import TestClient

from ecfiler.api.app import app, validate_auth_config


@pytest.fixture
def anon_client() -> TestClient:
    return TestClient(app)


class TestAuthConfigValidation:
    def test_no_config_raises(self) -> None:
        with pytest.raises(RuntimeError, match="auth is not configured"):
            validate_auth_config({})

    def test_dev_auth_must_be_exactly_1(self) -> None:
        with pytest.raises(RuntimeError):
            validate_auth_config({"ECFILER_DEV_AUTH": "true"})

    def test_clerk_issuer_suffices(self) -> None:
        validate_auth_config({"CLERK_ISSUER": "https://clerk.example.com"})

    def test_blank_clerk_issuer_rejected(self) -> None:
        with pytest.raises(RuntimeError):
            validate_auth_config({"CLERK_ISSUER": "   "})

    def test_explicit_dev_auth_suffices(self) -> None:
        validate_auth_config({"ECFILER_DEV_AUTH": "1"})


class TestRequestAuthentication:
    def test_no_credentials_rejected(self, anon_client: TestClient) -> None:
        response = anon_client.get("/api/history")
        assert response.status_code == 401

    def test_spoofed_header_rejected_without_dev_auth(
        self, anon_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("ECFILER_DEV_AUTH", raising=False)
        response = anon_client.get("/api/history", headers={"X-User-Id": "victim"})
        assert response.status_code == 401

    def test_header_honored_only_in_dev_mode(
        self, anon_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("ECFILER_DEV_AUTH", "1")
        response = anon_client.get("/api/history", headers={"X-User-Id": "test-user"})
        assert response.status_code == 200

    def test_invalid_bearer_does_not_fall_back_to_header(
        self, anon_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("ECFILER_DEV_AUTH", raising=False)
        response = anon_client.get(
            "/api/history",
            headers={"Authorization": "Bearer not-a-jwt", "X-User-Id": "victim"},
        )
        assert response.status_code == 401

    def test_public_endpoints_stay_public(self, anon_client: TestClient) -> None:
        assert anon_client.get("/api/health").status_code == 200
        assert anon_client.get("/api/courts").status_code == 200


class TestCORSHardening:
    def test_preflight_advertises_explicit_methods_only(
        self, anon_client: TestClient
    ) -> None:
        response = anon_client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        methods = response.headers.get("access-control-allow-methods", "")
        assert "*" not in methods
        assert "PUT" not in methods

    def test_preflight_rejects_unknown_header(self, anon_client: TestClient) -> None:
        response = anon_client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "X-Evil-Header",
            },
        )
        assert response.status_code == 400
