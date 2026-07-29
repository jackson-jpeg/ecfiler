"""Tests for the security-CLI macOS keychain backend."""

from __future__ import annotations

import subprocess
import sys
from unittest import mock

import pytest

from ecfiler.keychain_macos import SecurityCliKeychain


@pytest.fixture
def backend(monkeypatch):
    monkeypatch.setenv("ECFILER_KEYCHAIN", "/tmp/test.keychain-db")
    return SecurityCliKeychain()


def _proc(returncode: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def test_priority_requires_darwin(monkeypatch):
    monkeypatch.setenv("ECFILER_KEYCHAIN", "/tmp/test.keychain-db")
    if sys.platform != "darwin":
        with pytest.raises(RuntimeError):
            _ = SecurityCliKeychain.priority


def test_priority_requires_env(monkeypatch):
    monkeypatch.delenv("ECFILER_KEYCHAIN", raising=False)
    with pytest.raises(RuntimeError):
        _ = SecurityCliKeychain.priority


def test_get_password_found(backend):
    with mock.patch("subprocess.run", return_value=_proc(0, stdout="s3cret\n")) as run:
        assert backend.get_password("ecfiler-pacer", "jmsanger") == "s3cret"
    args = run.call_args[0][0]
    assert args[0] == "/usr/bin/security"
    assert "find-generic-password" in args
    assert "/tmp/test.keychain-db" in args


def test_get_password_missing(backend):
    with mock.patch("subprocess.run", return_value=_proc(44)):
        assert backend.get_password("ecfiler-pacer", "nobody") is None


def test_set_password_deletes_then_adds(backend):
    calls = []

    def record(cmd, **kwargs):
        calls.append(cmd)
        return _proc(0)

    with mock.patch("subprocess.run", side_effect=record):
        backend.set_password("ecfiler-pacer", "jmsanger", "pw")
    assert "delete-generic-password" in calls[0]
    assert "add-generic-password" in calls[1]
    assert "-A" in calls[1]


def test_set_password_failure_raises(backend):
    import keyring.errors

    def run(cmd, **kwargs):
        if "add-generic-password" in cmd:
            return _proc(1, stderr="boom")
        return _proc(0)

    with mock.patch("subprocess.run", side_effect=run):
        with pytest.raises(keyring.errors.PasswordSetError):
            backend.set_password("ecfiler-pacer", "jmsanger", "pw")
