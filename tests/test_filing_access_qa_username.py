"""`session filing-access --qa` must never log in to QA with the production account.

Found 2026-11-13 (session 7): with no --username, the command fell back to the
configured production username, which does not exist in the PACER QA realm,
so the documented check (`filing-access --qa --court azttdc`) could only ever
answer "Login Failed".
"""

from __future__ import annotations

from types import SimpleNamespace

from click.testing import CliRunner

import ecfiler.config as config_mod
from ecfiler.__main__ import main as cli


def _prod_config():
    return SimpleNamespace(pacer=SimpleNamespace(username="production-user"))


def test_qa_without_username_refuses_instead_of_using_production(monkeypatch) -> None:
    monkeypatch.setattr(config_mod, "load_config", _prod_config)
    monkeypatch.delenv("ECFILER_PACER_USERNAME", raising=False)
    result = CliRunner().invoke(cli, ["session", "filing-access", "--qa", "--court", "azttdc"])
    assert result.exit_code != 0
    assert "--username" in result.output and "ecfilercom" in result.output
    assert "production-user" not in result.output


def test_qa_username_comes_from_the_qa_env_var(monkeypatch) -> None:
    import ecfiler.pacer_auth as pacer_auth

    used: list[tuple] = []

    class Stop(Exception):
        pass

    def fake_auth(*args, **kwargs):
        used.append((args, kwargs))
        raise Stop

    monkeypatch.setattr(config_mod, "load_config", _prod_config)
    monkeypatch.setenv("ECFILER_PACER_USERNAME", "ecfilercom")
    monkeypatch.setattr(pacer_auth, "PacerAuth", fake_auth)
    result = CliRunner().invoke(cli, ["session", "filing-access", "--qa", "--court", "azttdc"])
    assert "No username" not in result.output
    assert "production-user" not in result.output + repr(used)
