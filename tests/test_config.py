"""Tests for configuration loading."""

import tempfile
from pathlib import Path

import pytest

from ecfiler.config import AppConfig, ConfigError, _parse_config, load_config


class TestParseConfig:
    def test_empty_config(self) -> None:
        cfg = _parse_config({})
        assert isinstance(cfg, AppConfig)
        assert cfg.general.default_court == ""
        assert cfg.pacer.username == ""

    def test_full_config(self) -> None:
        raw = {
            "general": {
                "default_court": "nysd",
                "claude_model": "claude-sonnet-4-20250514",
                "dry_run": True,
            },
            "pacer": {"username": "test@example.com"},
            "attorney": {
                "name": "Jane Smith",
                "bar_number": "JS1234",
                "firm": "Smith & Associates",
            },
            "pdf": {
                "auto_convert_pdfa": True,
                "max_file_size_mb": 50,
                "redaction_check": False,
            },
        }
        cfg = _parse_config(raw)
        assert cfg.general.default_court == "nysd"
        assert cfg.general.dry_run is True
        assert cfg.pacer.username == "test@example.com"
        assert cfg.attorney.name == "Jane Smith"
        assert cfg.pdf.max_file_size_mb == 50
        assert cfg.pdf.redaction_check is False

    def test_partial_config(self) -> None:
        raw = {"general": {"default_court": "cacd"}}
        cfg = _parse_config(raw)
        assert cfg.general.default_court == "cacd"
        assert cfg.pacer.username == ""  # Default

    def test_pacer_has_credentials(self) -> None:
        cfg = AppConfig()
        assert not cfg.pacer.has_credentials
        cfg.pacer.username = "test@example.com"
        assert cfg.pacer.has_credentials


class TestLoadConfig:
    def test_creates_default_on_first_run(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.toml"
        cfg = load_config(str(config_path))
        assert isinstance(cfg, AppConfig)
        assert config_path.exists()

    def test_loads_existing_config(self, tmp_path: Path) -> None:
        config_path = tmp_path / "config.toml"
        config_path.write_text(
            '[general]\ndefault_court = "txsd"\n\n[pacer]\nusername = "user@test.com"\n'
        )
        cfg = load_config(str(config_path))
        assert cfg.general.default_court == "txsd"
        assert cfg.pacer.username == "user@test.com"


class TestApiKey:
    def test_missing_api_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        cfg = AppConfig()
        with pytest.raises(ConfigError):
            _ = cfg.claude_api_key

    def test_api_key_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-123")
        cfg = AppConfig()
        assert cfg.claude_api_key == "sk-test-123"
