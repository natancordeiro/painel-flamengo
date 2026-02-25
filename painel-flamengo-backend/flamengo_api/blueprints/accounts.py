from __future__ import annotations

from flask import Blueprint, current_app, request

from flamengo_api.core.errors import ApiError, NotFound
from flamengo_api.core.http import ok
from flamengo_api.services.credentials import encrypt_password


bp = Blueprint("accounts", __name__, url_prefix="/api/v1/accounts")


def _repos():
    return (
        current_app.extensions["account_repo"],
        current_app.extensions["session_manager"],
    )


@bp.get("")
def list_accounts():
    repo, sessions = _repos()
    accounts = []
    for a in repo.list():
        accounts.append(
            {
                "id": a.id,
                "label": a.label,
                "email": a.email,
                "created_at": a.created_at,
                "updated_at": a.updated_at,
                "logged": sessions.is_logged(a.id),
            }
        )
    return ok(accounts)


@bp.post("")
def create_account():
    repo, sessions = _repos()
    payload = request.get_json(silent=True) or {}
    label = (payload.get("label") or "").strip() or "Conta"
    email = (payload.get("email") or "").strip()
    password = (payload.get("password") or "").strip()
    if not email or not password:
        raise ApiError("email e password são obrigatórios", status=400, code="validation_error")

    rec = repo.create(label=label, email=email, password_enc=encrypt_password(password))
    return ok({"id": rec.id}, status=201)


@bp.get("/<account_id>")
def get_account(account_id: str):
    repo, sessions = _repos()
    try:
        a = repo.get(account_id)
    except KeyError:
        raise NotFound("Conta não encontrada")

    return ok(
        {
            "id": a.id,
            "label": a.label,
            "email": a.email,
            "created_at": a.created_at,
            "updated_at": a.updated_at,
            "logged": sessions.is_logged(a.id),
            "logged_user": sessions.get(a.id).logged_user if sessions.is_logged(a.id) else None,
            "logged_in_at": sessions.get(a.id).logged_in_at if sessions.is_logged(a.id) else None,
        }
    )


@bp.put("/<account_id>")
def update_account(account_id: str):
    repo, sessions = _repos()
    payload = request.get_json(silent=True) or {}
    label = payload.get("label")
    email = payload.get("email")
    password = payload.get("password")
    password_enc = encrypt_password(password.strip()) if isinstance(password, str) and password.strip() else None

    try:
        rec = repo.update(
            account_id,
            label=(label.strip() if isinstance(label, str) else None),
            email=(email.strip() if isinstance(email, str) else None),
            password_enc=password_enc,
        )
    except KeyError:
        raise NotFound("Conta não encontrada")

    # se alterou credenciais, invalida sessão
    if password_enc is not None or email is not None:
        sessions.logout(account_id)

    return ok({"id": rec.id, "updated_at": rec.updated_at})


@bp.delete("/<account_id>")
def delete_account(account_id: str):
    repo, sessions = _repos()
    try:
        repo.get(account_id)
    except KeyError:
        raise NotFound("Conta não encontrada")

    sessions.logout(account_id)
    repo.delete(account_id)
    return ok({"deleted": True})


@bp.post("/<account_id>/login")
def login_account(account_id: str):
    repo, sessions = _repos()
    try:
        repo.get(account_id)
    except KeyError:
        raise NotFound("Conta não encontrada")

    acc_sess = sessions.login(account_id)
    return ok(
        {
            "account_id": account_id,
            "user": acc_sess.logged_user,
            "logged_in_at": acc_sess.logged_in_at,
        }
    )


@bp.post("/<account_id>/logout")
def logout_account(account_id: str):
    _, sessions = _repos()
    sessions.logout(account_id)
    return ok({"account_id": account_id, "logged": False})
