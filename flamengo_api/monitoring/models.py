from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional


def utcnow() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


@dataclass
class Reservation:
    at: str
    event_id: int
    sector_id: int
    sector_name: str
    price: str
    cart_total: int


@dataclass
class MonitorJob:
    id: str
    account_id: str
    event_id: int
    sector_ids: List[int]
    status: str = "running"  # running|stopped|completed|error
    created_at: str = field(default_factory=utcnow)
    started_at: str = field(default_factory=utcnow)
    stopped_at: Optional[str] = None

    poll_interval_seconds: float = 10.0
    max_cart_tickets: int = 3

    last_poll_at: Optional[str] = None
    last_message: Optional[str] = None
    error: Optional[str] = None

    cart_total: int = 0
    reservations: List[Reservation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
