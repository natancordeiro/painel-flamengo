import re
from datetime import datetime
from typing import List

from bs4 import BeautifulSoup

from flamengo_tickets.domain.exceptions import ParsingError
from flamengo_tickets.domain.models import Event
from flamengo_tickets.logging_config import logger


def extract_security_token(html: str) -> str:
    logger.debug("Parsing iniciado: extração de security_token (login)")
    soup = BeautifulSoup(html, "html.parser")
    inp = soup.find("input", {"id": "security"})
    if not inp or not inp.get("value"):
        raise ParsingError("security_token não encontrado na página de login")
    token = inp["value"]
    logger.debug("Parsing finalizado: security_token extraído")
    return token


def extract_xhr_token(html: str) -> str:
    logger.debug("Parsing iniciado: extração de X-Xml-Http-Request-Token")
    m = re.search(
        r"'X-Xml-Http-Request-Token'\s*:\s*'([^']+)'",
        html,
        flags=re.IGNORECASE,
    )
    if not m:
        raise ParsingError("XHR token não encontrado no HTML")
    token = m.group(1)
    logger.debug("Parsing finalizado: XHR token extraído")
    return token


def extract_logged_user_name(html: str) -> str:
    """
    Extrai o nome do usuário a partir da chamada:
    fcardFacial.upload("Nome...", "CPF", ...)
    """
    logger.debug("Parsing iniciado: extração de nome do usuário logado")
    m = re.search(r'fcardFacial\.upload\("([^"]+)"\s*,', html)
    if not m:
        raise ParsingError("Não foi possível identificar o nome do usuário logado")
    name = m.group(1).strip()
    logger.info(f"Parsing finalizado: usuário logado identificado como '{name}'")
    return name


def _parse_event_datetime(raw: str) -> datetime:
    """
    data-dataevento="29|11|2025 - 15:00"
    """
    try:
        # 29|11|2025 - 15:00  -> 29/11/2025 15:00
        fixed = raw.replace("|", "/").replace(" - ", " ")
        return datetime.strptime(fixed, "%d/%m/%Y %H:%M")
    except Exception as exc:
        raise ParsingError(f"Falha ao converter data do evento: '{raw}' ({type(exc).__name__}: {exc})")


def parse_events(html: str) -> List[Event]:
    logger.debug("Parsing iniciado: extração de campeonatos/partidas (home logada)")
    soup = BeautifulSoup(html, "html.parser")
    wrapper = soup.find("div", class_="swiper-wrapper")
    if not wrapper:
        raise ParsingError("Container de partidas (.swiper-wrapper) não encontrado")

    events: List[Event] = []

    for slide in soup.select("div.swiper-wrapper .swipe-partida"):
        data_campeonato = slide.get("data-campeonato", "").strip()
        mandante = slide.get("data-mandante", "").strip()
        visitante = slide.get("data-visitante", "").strip()
        data_dataevento = slide.get("data-dataevento", "").strip()
        data_url = slide.get("data-url", "").strip()

        if not data_url:
            # fallback para href do botão "Comprar"
            btn = slide.select_one("a.btn.fc-btn-primary, a.btn.fc-btn")
            if btn and btn.get("href"):
                data_url = btn["href"].strip()

        # event ID é o parâmetro "event" na URL
        event_id = None
        m = re.search(r"event=(\d+)", data_url)
        if m:
            event_id = int(m.group(1))
        else:
            # fallback para data-event em algum botão
            btn = slide.select_one("a[data-event]")
            if btn and btn.get("data-event"):
                event_id = int(btn["data-event"])

        if not event_id:
            logger.warning(f"Slide de partida sem event_id detectado: url={data_url}")
            continue

        event_dt = _parse_event_datetime(data_dataevento)

        # Tentativa de encontrar estádio (ex.: "Maracanã - RJ")
        stadium = None
        stadium_el = slide.select_one(".card-infos p")
        if stadium_el:
            stadium = stadium_el.get_text(strip=True)

        evt = Event(
            id=event_id,
            championship=data_campeonato,
            home_team=mandante,
            away_team=visitante,
            event_datetime=event_dt,
            url=data_url,
            stadium=stadium,
        )
        events.append(evt)

    logger.info(f"Parsing finalizado: {len(events)} partidas extraídas")
    return events
