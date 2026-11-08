"""
Encryption helpers for the vault.

Two SEPARATE concerns live in this app:

  1. The MASTER PASSWORD (user login) — hashed by Django's auth system
     using Argon2 (configured in settings.PASSWORD_HASHERS). One-way.
     This file does not touch it.

  2. The SAVED PASSWORDS (Gmail, bank, etc.) — encrypted here with
     Fernet (AES-128-CBC + HMAC-SHA256). Reversible, because we must
     show them back to the user.

SECURITY NOTE (MVP):
    The Fernet key is derived from Django's SECRET_KEY. If SECRET_KEY
    leaks, every vault is decryptable. If SECRET_KEY changes, every
    existing vault entry becomes unreadable. A production password
    manager would derive the key from the USER'S master password
    instead — see "future enhancements" in the project notes.
"""

import base64
import hashlib

from cryptography.fernet import Fernet
from django.conf import settings


def _get_cipher() -> Fernet:
    """Return a Fernet instance keyed from settings.SECRET_KEY."""
    digest = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    key = base64.urlsafe_b64encode(digest)  # 32-byte key → 44-char urlsafe
    return Fernet(key)


def encrypt_password(plain_text: str) -> str:
    """Encrypt a plaintext password. Returns a base64 string."""
    return _get_cipher().encrypt(plain_text.encode()).decode()


def decrypt_password(encrypted_text: str) -> str:
    """Decrypt a string produced by encrypt_password()."""
    return _get_cipher().decrypt(encrypted_text.encode()).decode()