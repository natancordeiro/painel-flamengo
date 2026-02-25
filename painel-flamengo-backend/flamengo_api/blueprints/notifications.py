from __future__ import annotations

from flask import Blueprint, current_app, request

from flamengo_api.core.errors import ApiError
from flamengo_api.core.http import ok


bp = Blueprint("notifications", __name__, url_prefix="/api/v1/notifications")


def _repos():
    return (
        current_app.extensions["notification_repo"],
        current_app.extensions["notifier_service"],
        current_app.extensions["session_manager"],
    )


@bp.get("/config")
def get_config():
    _, notifier_service, __ = _repos()
    return ok(notifier_service.get_config())


@bp.put("/config")
def update_config():
    repo, notifier_service, __ = _repos()
    payload = request.get_json(silent=True) or {}
    provider = (payload.get("provider") or "telegram").strip().lower()
    if provider not in {"telegram", "evolution"}:
        raise ApiError("provider inválido (use telegram ou evolution)", status=400, code="validation_error")

    rec = repo.update(
        provider=provider,
        telegram_bot_token=(payload.get("telegram_bot_token") or None),
        telegram_chat_id=(payload.get("telegram_chat_id") or None),
        evolution_base_url=(payload.get("evolution_base_url") or None),
        evolution_instance=(payload.get("evolution_instance") or None),
        evolution_api_key=(payload.get("evolution_api_key") or None),
        evolution_number=(payload.get("evolution_number") or None),
    )
    return ok({"updated_at": rec.updated_at, "provider": rec.provider})


@bp.post("/test")
def test_notification():
    repo, notifier_service, sessions = _repos()
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "Teste de notificação ✅").strip()

    notifier = notifier_service.build()

    # opcional: anexar sessão de qualquer conta logada para reusar session
    any_logged = next((aid for aid in [a.id for a in current_app.extensions["account_repo"].list()] if sessions.is_logged(aid)), None)
    if any_logged:
        try:
            notifier.attach_http_client(sessions.get(any_logged).client)
        except Exception:
            pass

    notifier.send_message(text)
    return ok({"sent": True})
