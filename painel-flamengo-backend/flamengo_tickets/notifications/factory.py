from typing import Literal

from flamengo_tickets.telegram.notifier import TelegramNotifier
from flamengo_tickets.evolution.notifier import EvolutionNotifier
from flamengo_tickets.config import AppConfig

Provider = Literal["telegram", "evolution"]

def build_notifier(config: AppConfig):
    provider: Provider = (config.alert_provider or "telegram").lower()  # type: ignore
    if provider == "evolution":
        evo_conf = config.evolution
        if evo_conf is None:
            raise ValueError("Configuração EvolutionAPI ausente, defina variáveis EVOLUTION_*")
        return EvolutionNotifier(evo_conf)
    return TelegramNotifier(config.telegram)
