from __future__ import annotations

import threading
import time
from datetime import datetime
from typing import List, Set

from flamengo_tickets.domain.exceptions import BookingError
from flamengo_tickets.domain.models import Event, Sector
from flamengo_tickets.flamengo.services import FlamengoTicketService
from flamengo_tickets.logging_config import logger
from flamengo_tickets.recaptcha.solver import get_recaptcha_token

from flamengo_api.monitoring.models import MonitorJob, Reservation


class MonitorWorker:
    def __init__(
        self,
        *,
        job: MonitorJob,
        client,
        event: Event,
        sectors_map: dict[int, Sector],
        notifier,
        stop_event: threading.Event,
    ) -> None:
        self.job = job
        self.client = client
        self.event = event
        self.sectors_map = sectors_map
        self.notifier = notifier
        self.stop_event = stop_event
        # usa wrapper thread-safe (mesma sessão/cookies do login)
        self.service = FlamengoTicketService(client)

    def _now(self) -> str:
        return datetime.utcnow().isoformat(timespec="seconds")

    def run(self) -> None:
        logger.info(f"[job={self.job.id}] Monitoramento iniciado")
        try:
            while not self.stop_event.is_set() and self.job.cart_total < self.job.max_cart_tickets:
                self.job.last_poll_at = self._now()

                avail = self.service.fetch_available_tickets(self.event.id)

                target_set: Set[int] = set(self.job.sector_ids or [])
                if target_set:
                    active_target = [info for sid, info in avail.items() if sid in target_set and info.active]
                else:
                    active_target = [info for info in avail.values() if info.active]

                if not active_target:
                    time.sleep(self.job.poll_interval_seconds)
                    continue

                for info in active_target:
                    if self.stop_event.is_set() or self.job.cart_total >= self.job.max_cart_tickets:
                        break

                    sector = self.sectors_map.get(info.sector_id)
                    sector_name = sector.name if sector else str(info.sector_id)

                    recaptcha_token = get_recaptcha_token(self.service.client, self.event.id, info.sector_id)  # type: ignore[attr-defined]

                    try:
                        result = self.service.book_ticket(
                            sector_id=info.sector_id,
                            recaptcha_token=recaptcha_token,
                            quantity=1,
                        )
                    except BookingError as exc:
                        logger.warning(f"[job={self.job.id}] BookingError: {exc}")
                        continue

                    if not result.success:
                        continue

                    self.job.cart_total = result.cart_total
                    res = Reservation(
                        at=self._now(),
                        event_id=self.event.id,
                        sector_id=info.sector_id,
                        sector_name=sector_name,
                        price=info.price,
                        cart_total=result.cart_total,
                    )
                    self.job.reservations.append(res)

                    msg = (
                        f"🎫 *Ingresso reservado!*\n\n"
                        f"*Jogo:* {self.event.home_team} x {self.event.away_team}\n"
                        f"*Campeonato:* {self.event.championship}\n"
                        f"*Data/Hora:* {self.event.event_datetime:%d/%m/%Y %H:%M}\n"
                        f"*Estádio:* {self.event.stadium or 'N/D'}\n"
                        f"*Setor:* {sector_name}\n"
                        f"*Preço:* R$ {info.price}\n"
                        f"*Event ID:* {self.event.id}\n"
                        f"*Sector ID:* {info.sector_id}\n"
                        f"*Ingressos no carrinho:* {result.cart_total}"
                    )
                    self.job.last_message = msg

                    try:
                        self.notifier.send_message(msg)
                    except Exception as exc:
                        logger.exception(f"[job={self.job.id}] Falha ao enviar notificação: {exc}")

                    if self.job.cart_total >= self.job.max_cart_tickets:
                        break

                time.sleep(self.job.poll_interval_seconds)

            if self.stop_event.is_set():
                self.job.status = "stopped"
                self.job.stopped_at = self._now()
                return

            self.job.status = "completed"
            self.job.stopped_at = self._now()

        except Exception as exc:
            logger.exception(f"[job={self.job.id}] Erro no monitoramento: {exc}")
            self.job.status = "error"
            self.job.error = str(exc)
            self.job.stopped_at = self._now()
