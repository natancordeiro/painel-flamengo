from __future__ import annotations

from typing import Tuple

from flamengo_tickets.config import BASE_URL
from flamengo_tickets.domain.exceptions import LoginError, TermsNotAcceptedError
from flamengo_tickets.flamengo.parsers import extract_security_token, extract_xhr_token, extract_logged_user_name
from flamengo_tickets.http.client import HttpClient
from flamengo_tickets.http.session import AJAX_HEADERS_BASE
from flamengo_tickets.logging_config import logger


class FlamengoLoginService:
    """Versão stateless do serviço de login (sem depender de AppConfig)."""

    def __init__(self, client: HttpClient) -> None:
        self.client = client

    def initial_get(self) -> None:
        logger.info("Efetuando primeira requisição GET /")
        self.client.get("/")

    def _load_login_page(self) -> Tuple[str, str]:
        logger.info("Carregando página de login /login")
        resp = self.client.get("/login")
        html = resp.text

        security_token = extract_security_token(html)
        xhr_token = extract_xhr_token(html)
        self.client.set_ajax_token(xhr_token)
        return security_token, xhr_token

    def _check_unlogged_accept_terms(self, email: str) -> None:
        logger.info("Verificando aceite de termos (check-unlogged-accept-terms)")
        resp = self.client.get(
            "/login/check-unlogged-accept-terms",
            params={"login": email},
            headers=AJAX_HEADERS_BASE,
            is_ajax=True,
        )
        data = resp.json()
        if not data.get("success"):
            raise LoginError("Falha ao verificar aceite de termos (success=false)")
        if not data.get("isTermsAccepted", False):
            raise TermsNotAcceptedError("Usuário ainda não aceitou os termos na plataforma")

    def login(self, *, email: str, password: str) -> str:
        if not email or not password:
            raise LoginError("Credenciais vazias")

        self.initial_get()
        security_token, _ = self._load_login_page()
        self._check_unlogged_accept_terms(email)

        logger.info("Efetuando POST de login")
        post_headers = dict(self.client.session.headers)
        post_headers.update(
            {
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": BASE_URL,
                "Referer": f"{BASE_URL}/login",
            }
        )

        payload = {
            "login": email,
            "pass": password,
            "accept_terms": "security",
            "security": security_token,
        }

        resp = self.client.post("/login", headers=post_headers, data=payload)
        html = resp.text
        user_name = extract_logged_user_name(html)
        logger.info(f"Login bem-sucedido para usuário '{user_name}'")
        return user_name
