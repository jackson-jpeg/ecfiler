"""AES-256-GCM encryption for PACER credentials.

Credentials are encrypted at rest and only decrypted at the moment of filing.
The encryption key is derived from ECFILER_ENCRYPTION_KEY env var.
"""

from __future__ import annotations

import base64
import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_ENV_KEY_NAME = "ECFILER_ENCRYPTION_KEY"
_KDF_ITERATIONS = 480_000  # OWASP recommendation for PBKDF2-SHA256


class EncryptionError(Exception):
    """Raised when encryption or decryption fails."""


def is_encryption_configured() -> bool:
    """Return True if the encryption key environment variable is set."""
    return bool(os.environ.get(_ENV_KEY_NAME))


def _get_master_key() -> bytes:
    """Read the master key from the environment.

    Raises EncryptionError if not configured.
    """
    raw = os.environ.get(_ENV_KEY_NAME)
    if not raw:
        raise EncryptionError(
            f"{_ENV_KEY_NAME} environment variable is not set. "
            "PACER credential storage requires an encryption key. "
            "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )
    return raw.encode("utf-8")


def _derive_key(master_key: bytes, salt: bytes) -> bytes:
    """Derive a 256-bit AES key from the master key using PBKDF2."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=_KDF_ITERATIONS,
    )
    return kdf.derive(master_key)


def encrypt_credential(plaintext: str, user_id: str) -> str:
    """Encrypt a credential string using AES-256-GCM.

    Args:
        plaintext: The credential value to encrypt (e.g. a password).
        user_id: Used as the salt for key derivation, binding the
                 ciphertext to a specific user.

    Returns:
        A base64-encoded string containing nonce + ciphertext + tag.
    """
    if not plaintext:
        raise EncryptionError("Cannot encrypt an empty credential")

    master_key = _get_master_key()
    salt = user_id.encode("utf-8")
    derived = _derive_key(master_key, salt)

    # 96-bit random nonce (recommended for AES-GCM)
    nonce = os.urandom(12)
    aesgcm = AESGCM(derived)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    # Pack as: nonce (12 bytes) || ciphertext+tag
    blob = nonce + ciphertext
    return base64.b64encode(blob).decode("ascii")


def decrypt_credential(ciphertext: str, user_id: str) -> str:
    """Decrypt a credential previously encrypted with encrypt_credential.

    Args:
        ciphertext: Base64-encoded blob from encrypt_credential.
        user_id: Must match the user_id used during encryption.

    Returns:
        The original plaintext credential.

    Raises:
        EncryptionError: If decryption fails (wrong key, tampered data, etc.).
    """
    if not ciphertext:
        raise EncryptionError("Cannot decrypt an empty ciphertext")

    master_key = _get_master_key()
    salt = user_id.encode("utf-8")
    derived = _derive_key(master_key, salt)

    try:
        blob = base64.b64decode(ciphertext)
    except Exception as exc:
        raise EncryptionError("Invalid ciphertext encoding") from exc

    if len(blob) < 13:  # 12-byte nonce + at least 1 byte
        raise EncryptionError("Ciphertext too short")

    nonce = blob[:12]
    encrypted = blob[12:]

    try:
        aesgcm = AESGCM(derived)
        plaintext_bytes = aesgcm.decrypt(nonce, encrypted, None)
    except Exception as exc:
        raise EncryptionError(
            "Decryption failed — wrong key, wrong user, or corrupted data"
        ) from exc

    return plaintext_bytes.decode("utf-8")
