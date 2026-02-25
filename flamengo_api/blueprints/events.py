from __future__ import annotations

from flask import Blueprint, current_app, request

from flamengo_api.core.errors import ApiError, NotFound
from flamengo_api.core.http import ok

from flamengo_tickets.flamengo.services import FlamengoTicketService


bp = Blueprint("events", __name__, url_prefix="/api/v1")


def _services():
    return (
        current_app.extensions["account_repo"],
        current_app.extensions["session_manager"],
    )


def _get_service(account_id: str) -> FlamengoTicketService:
    _, sessions = _services()
    if not sessions.is_logged(account_id):
        raise ApiError("Conta não está logada", status=400, code="not_logged")
    client = sessions.get(account_id).client  # wrapper thread-safe
    return FlamengoTicketService(client)


@bp.get("/accounts/<account_id>/events")
def list_events(account_id: str):
    service = _get_service(account_id)
    events = service.fetch_events()
    # serializa
    data = []
    for e in events:
        data.append(
            {
                "id": e.id,
                "championship": e.championship,
                "home_team": e.home_team,
                "away_team": e.away_team,
                "event_datetime": e.event_datetime.isoformat(),
                "stadium": e.stadium,
                "url": e.url,
            }
        )
    return ok(data)


@bp.get("/accounts/<account_id>/events/<int:event_id>/sectors")
def list_sectors(account_id: str, event_id: int):
    service = _get_service(account_id)
    sectors_map = service.fetch_sectors_map(event_id)
    data = [{"id": s.id, "name": s.name} for s in sectors_map.values()]
    return ok(data)


@bp.get("/accounts/<account_id>/events/<int:event_id>/availability")
def availability(account_id: str, event_id: int):
    service = _get_service(account_id)
    sector_ids_raw = (request.args.get("sector_ids") or "").strip()
    sector_ids = None
    if sector_ids_raw:
        sector_ids = {int(x) for x in sector_ids_raw.replace(" ", "").split(",") if x}

    avail = service.fetch_available_tickets(event_id)

    data = []
    for sid, info in avail.items():
        if sector_ids and sid not in sector_ids:
            continue
        data.append(
            {
                "sector_id": info.sector_id,
                "active": info.active,
                "total_tickets": info.total_tickets,
                "price": info.price,
                "sub_sector_totals": info.sub_sector_totals,
            }
        )
    return ok(data)
