from typing import Optional

from flamengo_tickets.config import TelegramConfig
from flamengo_tickets.http.client import HttpClient
from flamengo_tickets.logging_config import logger


class TelegramNotifier:
    def __init__(self, config: TelegramConfig) -> None:
        self.config = config
        self._client: Optional[HttpClient] = None

    def attach_http_client(self, client: HttpClient) -> None:
        """
        Reaproveita o mesmo HttpClient (e sessão) para observabilidade unificada.
        """
        self._client = client

    def send_message(self, text: str, parse_mode: str = "Markdown") -> None:
        if not self.config.bot_token or not self.config.chat_id:
            logger.warning("Telegram não configurado; alerta não será enviado")
            return

        if not self._client:
            raise RuntimeError("HttpClient não associado ao TelegramNotifier")

        path = f"https://api.telegram.org/bot{self.config.bot_token}/sendMessage"

        logger.info("Enviando alerta para Telegram")
        resp = self._client.post(
            path,
            data={
                "chat_id": self.config.chat_id,
                "text": text,
                "parse_mode": parse_mode,
            },
        )

        data = resp.json()
        if not data.get("ok", False):
            logger.error(f"Falha ao enviar mensagem para Telegram: {data}")
        else:
            logger.info("Mensagem enviada com sucesso para Telegram")
