from typing import Dict, List

from flamengo_tickets.config import BASE_URL
from flamengo_tickets.domain.exceptions import ParsingError, BookingError
from flamengo_tickets.domain.models import (
    Event,
    Sector,
    AvailableSectorInfo,
    BookingResult,
)
from flamengo_tickets.flamengo.parsers import parse_events
from flamengo_tickets.http.client import HttpClient
from flamengo_tickets.logging_config import logger


class FlamengoTicketService:
    def __init__(self, client: HttpClient) -> None:
        self.client = client

    # ---------------------------------------------------------- #
    # Eventos (campeonatos / partidas)
    # ---------------------------------------------------------- #
    def fetch_events(self) -> List[Event]:
        logger.info("Carregando página inicial logada para listar partidas")
        resp = self.client.get("/")
        html = resp.text
        events = parse_events(html)
        return events

    # ---------------------------------------------------------- #
    # Setores
    # ---------------------------------------------------------- #
    def fetch_sectors_map(self, event_id: int) -> Dict[int, Sector]:
        logger.info(f"Buscando mapa de setores para event={event_id}")
        resp = self.client.get("/information/get-map-info", params={"event": event_id})
        data = resp.json()

        logger.debug("Parsing iniciado: setores do mapa (get-map-info)")
        sectors_raw = data.get("sectors", [])
        if not isinstance(sectors_raw, list):
            raise ParsingError("Formato inesperado de 'sectors' em get-map-info")

        sectors: Dict[int, Sector] = {}
        for s in sectors_raw:
            sid = int(s["id"])
            sectors[sid] = Sector(id=sid, name=s.get("name", "").strip())

        logger.info(f"Parsing finalizado: {len(sectors)} setores extraídos do mapa")
        return sectors

    # ---------------------------------------------------------- #
    # Tickets disponíveis
    # ---------------------------------------------------------- #
    def fetch_available_tickets(self, event_id: int) -> Dict[int, AvailableSectorInfo]:
        logger.info(f"Consultando ingressos disponíveis (get-available-tickets) event={event_id}")
        resp = self.client.get(
            "/buy/get-available-tickets",
            params={"event": event_id},
            is_ajax=True,
        )
        data = resp.json()

        logger.debug("Parsing iniciado: setores disponíveis (get-available-tickets)")
        sectors_raw = data.get("sectors", {})
        results: Dict[int, AvailableSectorInfo] = {}

        for sid_str, info in sectors_raw.items():
            sid = int(sid_str)
            price = info.get("price", "").strip()
            active = bool(info.get("active", False))
            total = int(info.get("total", 0))

            sub_totals: Dict[int, int] = {}
            for sub_id_str, sub in info.get("subSectors", {}).items():
                sub_totals[int(sub_id_str)] = int(sub.get("total", 0))

            results[sid] = AvailableSectorInfo(
                sector_id=sid,
                price=price,
                active=active,
                total_tickets=total,
                sub_sector_totals=sub_totals,
            )

        logger.info(
            f"Parsing finalizado: {len(results)} setores com informações de disponibilidade extraídas"
        )
        return results

    # ---------------------------------------------------------- #
    # Booking de ingressos
    # ---------------------------------------------------------- #
    def book_ticket(
        self,
        sector_id: int,
        recaptcha_token: str,
        quantity: int = 1,
    ) -> BookingResult:
        logger.info(f"Tentando reservar ingresso | sectorId={sector_id} | quantity={quantity}")

        if not recaptcha_token:
            raise BookingError("recaptcha_token não informado")

        payload = {
            "sectorId": sector_id,
            "ticketQuantity": quantity,
            "recaptcha_token": recaptcha_token,
        }

        resp = self.client.post(
            "/buy/book-multiple-tickets",
            data=payload,
            is_ajax=True,
        )

        data = resp.json()
        success = bool(data.get("success"))
        status = int(data.get("status", 0))
        cart_total = int(data.get("cart_total", 0))

        logger.info(
            f"Booking retornou: success={success} | status={status} | cart_total={cart_total}"
        )

        return BookingResult(success=success, status=status, cart_total=cart_total)
