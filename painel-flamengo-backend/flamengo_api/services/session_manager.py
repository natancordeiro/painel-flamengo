from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from flamengo_tickets.http.client import HttpClient
from flamengo_tickets.http.session import create_session
from flamengo_tickets.logging_config import logger

from flamengo_api.services.credentials import decrypt_password
from flamengo_api.services.flamengo_login import FlamengoLoginService
from flamengo_api.services.repositories import AccountRepository


class ThreadSafeHttpClient:
    """Wrapper para evitar uso concorrente da mesma requests.Session."""

    def __init__(self, client: HttpClient) -> None:
        self._client = client
        self._lock = threading.RLock()

    @property
    def session(self):
        return self._client.session

    def set_ajax_token(self, token: str) -> None:
        with self._lock:
            return self._client.set_ajax_token(token)

    def get(self, path: str, **kwargs):
        with self._lock:
            return self._client.get(path, **kwargs)

    def post(self, path: str, **kwargs):
        with self._lock:
            return self._client.post(path, **kwargs)

    def request(self, method: str, path: str, **kwargs):
        with self._lock:
            return self._client.request(method, path, **kwargs)


@dataclass
class AccountSession:
    account_id: str
    client: ThreadSafeHttpClient
    logged_user: Optional[str]
    logged_in_at: Optional[str]


class SessionManager:
    def __init__(self, account_repo: AccountRepository, *, max_retries: int = 3, backoff_base_seconds: float = 1.0, timeout_seconds: float = 30.0) -> None:
        self._account_repo = account_repo
        self._http_defaults = {
            "max_retries": max_retries,
            "backoff_base_seconds": backoff_base_seconds,
            "timeout_seconds": timeout_seconds,
        }
        self._sessions: Dict[str, AccountSession] = {}
        self._lock = threading.RLock()

    def is_logged(self, account_id: str) -> bool:
        with self._lock:
            return account_id in self._sessions and bool(self._sessions[account_id].logged_user)

    def get(self, account_id: str) -> AccountSession:
        with self._lock:
            sess = self._sessions.get(account_id)
        if not sess:
            raise KeyError(account_id)
        return sess

    def logout(self, account_id: str) -> None:
        with self._lock:
            self._sessions.pop(account_id, None)

    def login(self, account_id: str) -> AccountSession:
        record = self._account_repo.get(account_id)
        password = decrypt_password(record.password_enc)

        session = create_session()
        client = HttpClient(session=session, **self._http_defaults)
        ts_client = ThreadSafeHttpClient(client)

        login_service = FlamengoLoginService(client)
        user = login_service.login(email=record.email, password=password)

        now = datetime.utcnow().isoformat(timespec="seconds")
        acc_sess = AccountSession(account_id=account_id, client=ts_client, logged_user=user, logged_in_at=now)

        with self._lock:
            self._sessions[account_id] = acc_sess

        return acc_sess
