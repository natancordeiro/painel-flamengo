from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict


@dataclass
class Event:
    id: int
    championship: str
    home_team: str
    away_team: str
    event_datetime: datetime
    url: str
    stadium: Optional[str] = None


@dataclass
class Sector:
    id: int
    name: str


@dataclass
class AvailableSectorInfo:
    sector_id: int
    price: str
    active: bool
    total_tickets: int
    sub_sector_totals: Dict[int, int]


@dataclass
class BookingResult:
    success: bool
    status: int
    cart_total: int
