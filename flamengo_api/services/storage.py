from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional


DEFAULT_DB_PATH = os.getenv("APP_DB_PATH", "data/app.db")


def _utcnow() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


@contextmanager
def connect(db_path: str = DEFAULT_DB_PATH) -> Iterator[sqlite3.Connection]:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    with connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id TEXT PRIMARY KEY,
                label TEXT,
                email TEXT NOT NULL,
                password_enc TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_config (
                singleton_id INTEGER PRIMARY KEY CHECK(singleton_id=1),
                provider TEXT NOT NULL DEFAULT 'telegram',
                telegram_bot_token TEXT,
                telegram_chat_id TEXT,
                evolution_base_url TEXT,
                evolution_instance TEXT,
                evolution_api_key TEXT,
                evolution_number TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )
        # ensure singleton row exists
        cur.execute("SELECT singleton_id FROM notification_config WHERE singleton_id=1")
        if cur.fetchone() is None:
            cur.execute(
                """
                INSERT INTO notification_config (
                    singleton_id, provider, telegram_bot_token, telegram_chat_id,
                    evolution_base_url, evolution_instance, evolution_api_key, evolution_number,
                    updated_at
                ) VALUES (1, 'telegram', NULL, NULL, NULL, NULL, NULL, NULL, ?)
                """,
                (_utcnow(),),
            )


@dataclass
class AccountRecord:
    id: str
    label: str
    email: str
    password_enc: str
    created_at: str
    updated_at: str


@dataclass
class NotificationConfigRecord:
    provider: str
    telegram_bot_token: Optional[str]
    telegram_chat_id: Optional[str]
    evolution_base_url: Optional[str]
    evolution_instance: Optional[str]
    evolution_api_key: Optional[str]
    evolution_number: Optional[str]
    updated_at: str
