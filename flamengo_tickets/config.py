import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

from flamengo_tickets.logging_config import logger

load_dotenv()


BASE_URL = "https://ingressos.flamengo.com.br"


@dataclass
class FlamengoConfig:
    email: str
    password: str


@dataclass
class TelegramConfig:
    bot_token: str
    chat_id: str


# --- NOVO: EvolutionAPI (WhatsApp) ----------------------
@dataclass
class EvolutionConfig:
    base_url: str
    instance: str
    api_key: str
    number: str  # ex.: 5591999999999
# --------------------------------------------------------


@dataclass
class HttpConfig:
    max_retries: int = 3
    backoff_base_seconds: float = 1.0
    timeout_seconds: float = 30.0


@dataclass
class MonitorConfig:
    poll_interval_seconds: float = 10.0
    max_cart_tickets: int = 3


@dataclass
class AppConfig:
    flamengo: FlamengoConfig
    telegram: TelegramConfig
    http: HttpConfig
    monitor: MonitorConfig

    # --- NOVOS CAMPOS: seleção de provedor e config Evolution
    alert_provider: str = "evolution"                   # "telegram" ou "evolution"
    evolution: Optional[EvolutionConfig] = None
    # --------------------------------------------------------

    @classmethod
    def from_env(cls) -> "AppConfig":
        logger.debug("Carregando configurações a partir de variáveis de ambiente")

        email = os.getenv("FLA_EMAIL", "").strip()
        password = os.getenv("FLA_PASSWORD", "").strip()

        if not email or not password:
            logger.warning("Credenciais do Flamengo não configuradas em FLA_EMAIL/FLA_PASSWORD")

        tg_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        tg_chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

        if not tg_token or not tg_chat_id:
            logger.warning("Configuração do Telegram ausente: TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID")

        http = HttpConfig(
            max_retries=int(os.getenv("REQUEST_MAX_RETRIES", "3")),
            backoff_base_seconds=float(os.getenv("REQUEST_BACKOFF_BASE", "1.0")),
            timeout_seconds=float(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
        )

        monitor = MonitorConfig(
            poll_interval_seconds=float(os.getenv("POLL_INTERVAL_SECONDS", "10")),
            max_cart_tickets=int(os.getenv("MAX_CART_TICKETS", "3")),
        )

        # --- NOVO: Provedor de alertas e (se for Evolution) suas variáveis
        alert_provider = os.getenv("ALERT_PROVIDER", "telegram").strip().lower()

        evo_conf: Optional[EvolutionConfig] = None
        if alert_provider == "evolution":
            base_url = os.getenv("EVOLUTION_BASE_URL", "").strip()
            instance = os.getenv("EVOLUTION_INSTANCE", "").strip()
            api_key = os.getenv("EVOLUTION_API_KEY", "").strip()
            number = os.getenv("EVOLUTION_NUMBER", "").strip()
            ...
            evo_conf = EvolutionConfig(
                base_url=base_url,
                instance=instance,
                api_key=api_key,
                number=number,
            )


        evo_conf: Optional[EvolutionConfig] = None
        if alert_provider == "evolution":
            base_url = os.getenv("EVOLUTION_BASE_URL", "").strip()
            instance = os.getenv("EVOLUTION_INSTANCE", "").strip()
            api_key = os.getenv("EVOLUTION_API_KEY", "").strip()
            number = os.getenv("EVOLUTION_NUMBER", "").strip()

            missing = [
                name for name, val in {
                    "EVOLUTION_BASE_URL": base_url,
                    "EVOLUTION_INSTANCE": instance,
                    "EVOLUTION_API_KEY": api_key,
                    "EVOLUTION_NUMBER": number,
                }.items() if not val
            ]
            if missing:
                raise ValueError(f"Faltam variáveis para EvolutionAPI: {', '.join(missing)}")

            evo_conf = EvolutionConfig(
                base_url=base_url,
                instance=instance,
                api_key=api_key,
                number=number,
            )
        # ----------------------------------------------------

        return cls(
            flamengo=FlamengoConfig(email=email, password=password),
            telegram=TelegramConfig(bot_token=tg_token, chat_id=tg_chat_id),
            http=http,
            monitor=monitor,
            alert_provider=alert_provider,
            evolution=evo_conf,
        )