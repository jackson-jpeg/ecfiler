"""Tests for ecfiler.security — AES-256-GCM credential encryption."""

from __future__ import annotations

import os

import pytest

from ecfiler.security import (
    EncryptionError,
    decrypt_credential,
    encrypt_credential,
    is_encryption_configured,
)

# A stable test key — never use in production.
_TEST_KEY = "test-key-for-unit-tests-only-32chars!"


@pytest.fixture(autouse=True)
def _set_encryption_key(monkeypatch):
    """Ensure every test has a valid encryption key by default."""
    monkeypatch.setenv("ECFILER_ENCRYPTION_KEY", _TEST_KEY)


# --- Round-trip ---


def test_encrypt_decrypt_round_trip():
    """Encrypting then decrypting should return the original plaintext."""
    password = "s3cret-PACER-p@ss!"
    user_id = "user-42"

    ciphertext = encrypt_credential(password, user_id)
    assert ciphertext != password  # not stored in plaintext
    assert decrypt_credential(ciphertext, user_id) == password


def test_round_trip_unicode():
    """Non-ASCII credentials should survive the round-trip."""
    password = "p\u00e4ssw\u00f6rd-\u2603"
    user_id = "user-unicode"
    ciphertext = encrypt_credential(password, user_id)
    assert decrypt_credential(ciphertext, user_id) == password


# --- Different users produce different ciphertexts ---


def test_different_users_different_ciphertexts():
    """The same password encrypted for two different users must differ."""
    password = "shared-password"
    ct_a = encrypt_credential(password, "alice")
    ct_b = encrypt_credential(password, "bob")
    assert ct_a != ct_b

    # Both should decrypt correctly with their own user_id
    assert decrypt_credential(ct_a, "alice") == password
    assert decrypt_credential(ct_b, "bob") == password


def test_decrypt_wrong_user_fails():
    """Decrypting with a different user_id must fail."""
    ciphertext = encrypt_credential("my-pass", "user-a")
    with pytest.raises(EncryptionError, match="Decryption failed"):
        decrypt_credential(ciphertext, "user-b")


# --- Wrong key ---


def test_decrypt_wrong_key_fails(monkeypatch):
    """Decryption must fail if the encryption key changes."""
    ciphertext = encrypt_credential("my-pass", "user-1")

    monkeypatch.setenv("ECFILER_ENCRYPTION_KEY", "a-completely-different-key!!!")
    with pytest.raises(EncryptionError, match="Decryption failed"):
        decrypt_credential(ciphertext, "user-1")


# --- is_encryption_configured ---


def test_is_encryption_configured_true():
    """Should be True when the env var is set (autouse fixture sets it)."""
    assert is_encryption_configured() is True


def test_is_encryption_configured_false(monkeypatch):
    """Should be False when the env var is unset."""
    monkeypatch.delenv("ECFILER_ENCRYPTION_KEY", raising=False)
    assert is_encryption_configured() is False


# --- Error cases ---


def test_encrypt_empty_plaintext_raises():
    """Encrypting an empty string should raise."""
    with pytest.raises(EncryptionError, match="empty credential"):
        encrypt_credential("", "user-1")


def test_decrypt_empty_ciphertext_raises():
    """Decrypting an empty string should raise."""
    with pytest.raises(EncryptionError, match="empty ciphertext"):
        decrypt_credential("", "user-1")


def test_encrypt_without_key_raises(monkeypatch):
    """Encryption must fail clearly when the env var is missing."""
    monkeypatch.delenv("ECFILER_ENCRYPTION_KEY", raising=False)
    with pytest.raises(EncryptionError, match="ECFILER_ENCRYPTION_KEY"):
        encrypt_credential("password", "user-1")


def test_decrypt_without_key_raises(monkeypatch):
    """Decryption must fail clearly when the env var is missing."""
    monkeypatch.delenv("ECFILER_ENCRYPTION_KEY", raising=False)
    with pytest.raises(EncryptionError, match="ECFILER_ENCRYPTION_KEY"):
        decrypt_credential("some-ciphertext", "user-1")


def test_decrypt_garbage_ciphertext():
    """Decryption of non-base64 data should raise."""
    with pytest.raises(EncryptionError):
        decrypt_credential("not-valid-base64!!!", "user-1")


def test_decrypt_truncated_ciphertext():
    """Ciphertext shorter than nonce size should raise."""
    import base64
    short = base64.b64encode(b"tiny").decode()
    with pytest.raises(EncryptionError, match="too short"):
        decrypt_credential(short, "user-1")


def test_decrypt_valid_base64_but_wrong_ciphertext():
    """Syntactically valid base64 of sufficient length but wrong AESGCM tag should raise."""
    import base64
    # 12-byte nonce + 20 bytes of fake ciphertext (long enough to pass size check)
    fake_data = b"\x00" * 12 + b"\xff" * 20
    fake_ciphertext = base64.b64encode(fake_data).decode()
    with pytest.raises(EncryptionError, match="Decryption failed"):
        decrypt_credential(fake_ciphertext, "user-1")
