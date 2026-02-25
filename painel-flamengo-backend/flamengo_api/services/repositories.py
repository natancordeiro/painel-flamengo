from __future__ import annotations

import uuid
from dataclasses import asdict
from typing import List, Optional

from flamengo_api.services.storage import (
    AccountRecord,
    NotificationConfigRecord,
    connect,
    DEFAULT_DB_PATH,
    _utcnow,
)


class AccountRepository:
    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path

    def create(self, *, label: str, email: str, password_enc: str) -> AccountRecord:
        account_id = str(uuid.uuid4())
        now = _utcnow()
        with connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO accounts (id, label, email, password_enc, created_at, updated_at) VALUES (?,?,?,?,?,?)",
                (account_id, label, email, password_enc, now, now),
            )
        return self.get(account_id)

    def list(self) -> List[AccountRecord]:
        with connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM accounts ORDER BY created_at DESC").fetchall()
        return [AccountRecord(**dict(r)) for r in rows]

    def get(self, account_id: str) -> AccountRecord:
        with connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM accounts WHERE id=?", (account_id,)).fetchone()
        if row is None:
            raise KeyError(account_id)
        return AccountRecord(**dict(row))

    def update(self, account_id: str, *, label: Optional[str] = None, email: Optional[str] = None, password_enc: Optional[str] = None) -> AccountRecord:
        existing = self.get(account_id)
        new_label = label if label is not None else existing.label
        new_email = email if email is not None else existing.email
        new_password = password_enc if password_enc is not None else existing.password_enc
        now = _utcnow()
        with connect(self.db_path) as conn:
            conn.execute(
                "UPDATE accounts SET label=?, email=?, password_enc=?, updated_at=? WHERE id=?",
                (new_label, new_email, new_password, now, account_id),
            )
        return self.get(account_id)

    def delete(self, account_id: str) -> None:
        with connect(self.db_path) as conn:
            conn.execute("DELETE FROM accounts WHERE id=?", (account_id,))


class NotificationConfigRepository:
    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path

    def get(self) -> NotificationConfigRecord:
        with connect(self.db_path) as conn:
            row = conn.execute("SELECT * FROM notification_config WHERE singleton_id=1").fetchone()
        assert row is not None
        data = dict(row)
        data.pop("singleton_id", None)
        return NotificationConfigRecord(**data)

    def update(
        self,
        *,
        provider: str,
        telegram_bot_token: Optional[str] = None,
        telegram_chat_id: Optional[str] = None,
        evolution_base_url: Optional[str] = None,
        evolution_instance: Optional[str] = None,
        evolution_api_key: Optional[str] = None,
        evolution_number: Optional[str] = None,
    ) -> NotificationConfigRecord:
        now = _utcnow()
        with connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE notification_config
                SET provider=?, telegram_bot_token=?, telegram_chat_id=?,
                    evolution_base_url=?, evolution_instance=?, evolution_api_key=?, evolution_number=?,
                    updated_at=?
                WHERE singleton_id=1
                """,
                (
                    provider,
                    telegram_bot_token,
                    telegram_chat_id,
                    evolution_base_url,
                    evolution_instance,
                    evolution_api_key,
                    evolution_number,
                    now,
                ),
            )
        return self.get()
