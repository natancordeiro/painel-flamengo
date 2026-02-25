from __future__ import annotations

import os
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken


def generate_key() -> str:
    """Gera uma chave Fernet (base64 urlsafe) para armazenar em CRED_FERNET_KEY."""
    return Fernet.generate_key().decode("utf-8")


def _get_fernet() -> Fernet:
    key = os.getenv("CRED_FERNET_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "CRED_FERNET_KEY não definido. Gere uma chave com: python -c \"from flamengo_api.services.credentials import generate_key; print(generate_key())\""
        )
    return Fernet(key.encode("utf-8"))


def encrypt_password(password: str) -> str:
    f = _get_fernet()
    return f.encrypt(password.encode("utf-8")).decode("utf-8")


def decrypt_password(password_enc: str) -> str:
    f = _get_fernet()
    try:
        return f.decrypt(password_enc.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise RuntimeError("Falha ao descriptografar senha: CRED_FERNET_KEY inválida ou alterada") from exc
