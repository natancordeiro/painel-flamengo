from __future__ import annotations

from flask import Blueprint, current_app, request

from flamengo_api.core.errors import ApiError
from flamengo_api.core.http import ok


bp = Blueprint("monitoring", __name__, url_prefix="/api/v1/monitoring")


def _mgr():
    return current_app.extensions["monitor_manager"]


@bp.get("/jobs")
def list_jobs():
    mgr = _mgr()
    jobs = [j.to_dict() for j in mgr.list_jobs()]
    return ok(jobs)


@bp.post("/jobs")
def start_job():
    mgr = _mgr()
    payload = request.get_json(silent=True) or {}
    try:
        account_id = str(payload.get("account_id") or "").strip()
        event_id = int(payload.get("event_id"))
    except Exception:
        raise ApiError("account_id e event_id são obrigatórios", status=400, code="validation_error")

    sector_ids = payload.get("sector_ids")
    if sector_ids is not None:
        if not isinstance(sector_ids, list):
            raise ApiError("sector_ids deve ser uma lista de inteiros", status=400, code="validation_error")

    job = mgr.start_job(
        account_id=account_id,
        event_id=event_id,
        sector_ids=sector_ids,
        poll_interval_seconds=payload.get("poll_interval_seconds"),
        max_cart_tickets=payload.get("max_cart_tickets"),
    )
    return ok({"job_id": job.id}, status=201)


@bp.get("/jobs/<job_id>")
def get_job(job_id: str):
    mgr = _mgr()
    job = mgr.get_job(job_id)
    return ok(job.to_dict())


@bp.post("/jobs/<job_id>/stop")
def stop_job(job_id: str):
    mgr = _mgr()
    job = mgr.stop_job(job_id)
    return ok({"job_id": job.id, "status": job.status})
