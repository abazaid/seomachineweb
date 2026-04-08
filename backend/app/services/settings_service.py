import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import get_settings


settings = get_settings()


def _build_fernet() -> Fernet:
    key_bytes = hashlib.sha256(settings.settings_encryption_key.encode('utf-8')).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


fernet = _build_fernet()


def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode('utf-8')).decode('utf-8')


def decrypt_value(value_encrypted: str) -> str:
    return fernet.decrypt(value_encrypted.encode('utf-8')).decode('utf-8')


def mask_value(value: str | None) -> str | None:
    if not value:
        return None
    if len(value) <= 4:
        return '*' * len(value)
    return f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}"
