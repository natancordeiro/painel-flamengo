from dataclasses import dataclass
from typing import Optional, Dict, Any, TYPE_CHECKING

import requests
from flamengo_tickets.logging_config import logger

if TYPE_CHECKING:
    # apenas para type hints, evita import em runtime
    from flamengo_tickets.http.client import HttpClient


@dataclass
class EvolutionConfig:
    base_url: str
    instance: str
    api_key: str
    number: str  # número do destinatário no formato internacional, ex: 5591999999999


class EvolutionNotifier:
    """
    Envia alertas através da EvolutionAPI (WhatsApp).

    Endpoint: POST {base_url}/message/sendText/{instance}
    Body:
        {"number": "<remoteJid>", "text": "<mensagem>"}
    Auth:
        via header (ex.: Authorization: Bearer <api_key>)
    """
    def __init__(self, config: EvolutionConfig) -> None:
        self.config = config
        self._session: Optional[requests.Session] = None

    def send_message(self, text: str, parse_mode: str = "Markdown") -> None:
        # parse_mode é ignorado pela EvolutionAPI, mas mantemos a assinatura
        self.notify(text)

    def attach_http_client(self, client: "HttpClient") -> None:
        """
        Reaproveita a mesma requests.Session do HttpClient do app.
        """
        try:
            self._session = client.session
        except Exception:
            logger.debug("Não foi possível anexar HttpClient; criando sessão própria ao enviar.")

    # ainda disponível se quiser anexar sessão direta
    def attach_session(self, session: requests.Session) -> None:
        self._session = session

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
        return self._session

    def notify(self, text: str) -> None:
        url = f"{self.config.base_url.rstrip('/')}/message/sendText/{self.config.instance}"
        headers = {
            # se já vier com "Bearer " ou "ApiKey ", preserva como está; caso contrário, prefixa com Bearer
            "apikey": self.config.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload: Dict[str, Any] = {"number": self.config.number, "text": text}

        logger.info("Enviando alerta via EvolutionAPI")
        try:
            resp = self.session.post(url, json=payload, headers=headers, timeout=30)
            logger.debug(f"EvolutionAPI status={resp.status_code} body={resp.text}")
            resp.raise_for_status()
            if 200 <= resp.status_code < 300:
                logger.info("Mensagem enviada com sucesso via EvolutionAPI")
            else:
                logger.error(f"Falha ao enviar mensagem via EvolutionAPI: {resp.text}")
        except requests.RequestException as exc:
            logger.exception(f"Erro de requisição EvolutionAPI: {exc}")
            raise
