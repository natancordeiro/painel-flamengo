import time
from typing import Iterable, Set

from flamengo_tickets.config import MonitorConfig
from flamengo_tickets.domain.models import Event, Sector
from flamengo_tickets.domain.exceptions import BookingError
from flamengo_tickets.flamengo.services import FlamengoTicketService
from flamengo_tickets.http.client import HttpClient
from flamengo_tickets.logging_config import logger
from flamengo_tickets.recaptcha.solver import get_recaptcha_token
from flamengo_tickets.telegram.notifier import TelegramNotifier


class TicketMonitor:
    def __init__(
        self,
        service: FlamengoTicketService,
        notifier: TelegramNotifier,
        monitor_config: MonitorConfig,
        sectors_map: dict[int, Sector],
    ) -> None:
        self.service = service
        self.notifier = notifier
        self.config = monitor_config
        self.sectors_map = sectors_map

    def run(self, event: Event, target_sector_ids: Set[int], client: HttpClient) -> None:
        """
        Loop infinito (até Ctrl+C) consultando get-available-tickets
        e tentando adicionar ingressos ao carrinho até `max_cart_tickets`.
        """
        logger.info(
            f"Iniciando monitoramento | event={event.id} "
            f"| campeonato={event.championship} "
            f"| {event.home_team} x {event.away_team}"
        )

        logger.info(
            f"Setores monitorados: "
            + (", ".join(f"{sid} ({self.sectors_map[sid].name})" for sid in target_sector_ids)
               if target_sector_ids else "TODOS")
        )

        current_cart_total = 0

        try:
            while current_cart_total < self.config.max_cart_tickets:
                avail = self.service.fetch_available_tickets(event.id)

                # Filtra setores ativos
                if target_sector_ids:
                    active_target = [
                        info
                        for sid, info in avail.items()
                        if sid in target_sector_ids and info.active
                    ]
                else:
                    active_target = [info for info in avail.values() if info.active]

                if not active_target:
                    logger.debug(
                        "Nenhum setor monitorado com ingressos disponíveis no momento; "
                        f"aguardando {self.config.poll_interval_seconds}s"
                    )
                    time.sleep(self.config.poll_interval_seconds)
                    continue

                logger.info(
                    f"{len(active_target)} setor(es) monitorado(s) com ingressos disponíveis; "
                    "tentando reservar..."
                )

                for info in active_target:
                    if current_cart_total >= self.config.max_cart_tickets:
                        break

                    sector_name = self.sectors_map.get(info.sector_id, None)
                    sector_name_str = sector_name.name if sector_name else str(info.sector_id)

                    try:
                        recaptcha_token = get_recaptcha_token(client, event.id, info.sector_id)
                    except NotImplementedError as exc:
                        logger.error(
                            f"BookingError ({type(exc).__name__}): {exc} | "
                            f"Não é possível prosseguir sem recaptcha_token"
                        )
                        raise

                    try:
                        result = self.service.book_ticket(
                            sector_id=info.sector_id,
                            recaptcha_token=recaptcha_token,
                            quantity=1,
                        )
                    except BookingError as exc:
                        logger.error(
                            f"BookingError ({type(exc).__name__}): {exc} | "
                            f"sectorId={info.sector_id}"
                        )
                        continue

                    if not result.success:
                        logger.warning(
                            f"Reserva não bem-sucedida | sectorId={info.sector_id} | "
                            f"status={result.status}"
                        )
                        continue

                    current_cart_total = result.cart_total
                    logger.info(
                        f"Ingresso adicionado ao carrinho | sectorId={info.sector_id} "
                        f"({sector_name_str}) | cart_total={current_cart_total}"
                    )

                    # Persistência: aqui o "sink" é Telegram (e eventualmente arquivo, se quiser)
                    msg = (
                        f"🎫 *Ingresso reservado!*\n\n"
                        f"*Jogo:* {event.home_team} x {event.away_team}\n"
                        f"*Campeonato:* {event.championship}\n"
                        f"*Data/Hora:* {event.event_datetime:%d/%m/%Y %H:%M}\n"
                        f"*Estádio:* {event.stadium or 'N/D'}\n"
                        f"*Setor:* {sector_name_str}\n"
                        f"*Preço:* R$ {info.price}\n"
                        f"*Event ID:* {event.id}\n"
                        f"*Sector ID:* {info.sector_id}\n"
                        f"*Ingressos no carrinho:* {current_cart_total}"
                    )
                    logger.info("Persistência: sink=Telegram, tipo=alerta-ingresso, contagem=1")
                    self.notifier.send_message(msg)

                    if current_cart_total >= self.config.max_cart_tickets:
                        logger.info(
                            f"Limite de {self.config.max_cart_tickets} ingressos "
                            "alcançado. Encerrando monitoramento."
                        )
                        return

                logger.debug(
                    f"Iteração de monitoramento concluída; aguardando "
                    f"{self.config.poll_interval_seconds}s para próxima checagem."
                )
                time.sleep(self.config.poll_interval_seconds)

        except KeyboardInterrupt:
            logger.warning("Monitoramento interrompido pelo usuário (KeyboardInterrupt)")
