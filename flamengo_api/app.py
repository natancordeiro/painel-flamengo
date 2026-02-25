from __future__ import annotations

import os

from flask import Flask, request
from flask_cors import CORS

from flamengo_api.core.errors import ApiError, Unauthorized
from flamengo_api.core.http import err, ok
from flamengo_api.services.storage import init_db
from flamengo_api.services.repositories import AccountRepository, NotificationConfigRepository
from flamengo_api.services.session_manager import SessionManager
from flamengo_api.services.notifier_service import NotifierService
from flamengo_api.monitoring.manager import MonitorManager

from flamengo_api.blueprints.accounts import bp as accounts_bp
from flamengo_api.blueprints.events import bp as events_bp
from flamengo_api.blueprints.monitoring import bp as monitoring_bp
from flamengo_api.blueprints.notifications import bp as notifications_bp


def create_app() -> Flask:
    app = Flask(__name__)

    # CORS para integração com frontend
    CORS(app)

    # DB
    init_db(os.getenv("APP_DB_PATH", "data/app.db"))

    account_repo = AccountRepository()
    notification_repo = NotificationConfigRepository()

    # HTTP defaults
    max_retries = int(os.getenv("REQUEST_MAX_RETRIES", "3"))
    backoff_base = float(os.getenv("REQUEST_BACKOFF_BASE", "1.0"))
    timeout = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))

    session_manager = SessionManager(
        account_repo,
        max_retries=max_retries,
        backoff_base_seconds=backoff_base,
        timeout_seconds=timeout,
    )

    notifier_service = NotifierService(notification_repo)
    monitor_manager = MonitorManager(session_manager, notifier_service)

    app.extensions["account_repo"] = account_repo
    app.extensions["notification_repo"] = notification_repo
    app.extensions["session_manager"] = session_manager
    app.extensions["notifier_service"] = notifier_service
    app.extensions["monitor_manager"] = monitor_manager

    api_key = os.getenv("API_KEY", "").strip()

    @app.before_request
    def _check_api_key():
        if not api_key:
            return None
        if request.path.startswith("/api/"):
            provided = request.headers.get("X-API-Key", "").strip()
            if provided != api_key:
                raise Unauthorized("API key inválida")
        return None

    @app.get("/api/v1/health")
    def health():
        return ok({"status": "ok"})

    # Blueprints
    app.register_blueprint(accounts_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(notifications_bp)

    # Error handlers
    @app.errorhandler(ApiError)
    def _api_error(e: ApiError):
        return err(e.message, status=e.status, code=e.code, details=e.details)

    @app.errorhandler(404)
    def _not_found(_):
        return err("Endpoint não encontrado", status=404, code="not_found")

    @app.errorhandler(Exception)
    def _unhandled(e: Exception):
        # evita vazar stacktrace em produção, mas deixa mensagem genérica
        return err("Erro interno", status=500, code="internal_error")

    return app
