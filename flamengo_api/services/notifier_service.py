from __future__ import annotations

from dataclasses import asdict

from flamengo_tickets.telegram.notifier import TelegramNotifier
from flamengo_tickets.config import TelegramConfig
from flamengo_tickets.evolution.notifier import EvolutionNotifier, EvolutionConfig as EvoCfg

from flamengo_api.core.errors import ApiError
from flamengo_api.services.repositories import NotificationConfigRepository


class NotifierService:
    def __init__(self, repo: NotificationConfigRepository) -> None:
        self._repo = repo

    def get_config(self) -> dict:
        rec = self._repo.get()
        # não vazar tokens por padrão? Para UI admin interna, ok.
        return asdict(rec)

    def build(self):
        rec = self._repo.get()
        provider = (rec.provider or "telegram").lower()
        if provider == "evolution":
            missing = [
                name
                for name, val in {
                    "evolution_base_url": rec.evolution_base_url,
                    "evolution_instance": rec.evolution_instance,
                    "evolution_api_key": rec.evolution_api_key,
                    "evolution_number": rec.evolution_number,
                }.items()
                if not val
            ]
            if missing:
                raise ApiError("Configuração Evolution incompleta", status=400, code="invalid_config", details={"missing": missing})
            return EvolutionNotifier(
                EvoCfg(
                    base_url=rec.evolution_base_url or "",
                    instance=rec.evolution_instance or "",
                    api_key=rec.evolution_api_key or "",
                    number=rec.evolution_number or "",
                )
            )

        # telegram
        return TelegramNotifier(
            TelegramConfig(
                bot_token=rec.telegram_bot_token or "",
                chat_id=rec.telegram_chat_id or "",
            )
        )
