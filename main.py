from typing import Dict, List, Set

from flamengo_tickets.config import AppConfig
from flamengo_tickets.domain.models import Event, Sector
from flamengo_tickets.flamengo.auth import FlamengoAuthService
from flamengo_tickets.flamengo.monitor import TicketMonitor
from flamengo_tickets.flamengo.services import FlamengoTicketService
from flamengo_tickets.http.client import HttpClient
from flamengo_tickets.http.session import create_session
from flamengo_tickets.logging_config import logger
from flamengo_tickets.notifications.factory import build_notifier

def _choose_event(events: List[Event]) -> Event:
    print("\n=== Campeonatos / Partidas disponíveis ===")
    for idx, ev in enumerate(events, start=1):
        print(
            f"[{idx}] {ev.championship} | {ev.home_team} x {ev.away_team} "
            f"| {ev.event_datetime:%d/%m/%Y %H:%M} | event={ev.id}"
        )

    while True:
        choice = input("Digite o número da partida que deseja monitorar: ").strip()
        if not choice.isdigit():
            print("Entrada inválida. Informe um número.")
            continue

        idx = int(choice)
        if 1 <= idx <= len(events):
            return events[idx - 1]
        print("Índice fora do intervalo.")


def _choose_sectors(sectors_map: Dict[int, Sector]) -> Set[int]:
    """
    Mostra os setores numerados a partir de 1 (somente para seleção na UI),
    permitindo:
      - 0        -> todos
      - 1,2,4    -> apenas os índices selecionados

    Retorna um conjunto de *IDs reais* de setor.
    """
    # criamos uma lista ordenada apenas para exibir índices sequenciais [1], [2], ...
    sectors_list = list(sectors_map.values())

    print("\n=== Setores disponíveis ===")
    for idx, sector in enumerate(sectors_list, start=1):
        nome = getattr(sector, "name", "Setor")
        print(f"[{idx}] {nome} (id={sector.id})")
    print("[0] Todos")

    raw = input("\nEscolha o(s) setor(es) (0 para todos, ou ex.: 1,2,4): ").strip()

    # 0 (ou vazio) => todos
    if raw == "0" or raw == "":
        return {s.id for s in sectors_list}

    chosen_ids: Set[int] = set()
    parts = [p for p in raw.replace(" ", "").split(",") if p]

    for p in parts:
        if not p.isdigit():
            print(f"Aviso: ignorando entrada inválida: '{p}'")
            continue
        pos = int(p)
        # mapeia o índice mostrado (1-based) para a posição na lista (0-based)
        if 1 <= pos <= len(sectors_list):
            chosen_ids.add(sectors_list[pos - 1].id)
        else:
            print(f"Aviso: índice '{pos}' fora do intervalo 1..{len(sectors_list)}; ignorando.")

    # fallback: se nada válido foi escolhido, assume todos
    if not chosen_ids:
        print("Nenhuma seleção válida; usando todos os setores.")
        return {s.id for s in sectors_list}

    return chosen_ids


def main() -> None:
    logger.info("Iniciando automação de monitoramento de ingressos")

    config = AppConfig.from_env()

    # HTTP + sessão
    session = create_session()
    client = HttpClient(
        session=session,
        max_retries=config.http.max_retries,
        backoff_base_seconds=config.http.backoff_base_seconds,
        timeout_seconds=config.http.timeout_seconds,
    )

    # Notificador Telegram
    notifier = build_notifier(config)
    notifier.attach_http_client(client)

    # Auth + serviços
    auth_service = FlamengoAuthService(client, config)
    ticket_service = FlamengoTicketService(client)

    # Login
    user_name = auth_service.login()
    logger.info(f"Usuário logado: {user_name}")

    # Eventos
    events = ticket_service.fetch_events()
    if not events:
        logger.warning("Nenhuma partida disponível para monitoramento.")
        return

    event = _choose_event(events)

    # Setores
    sectors_map = ticket_service.fetch_sectors_map(event.id)
    if not sectors_map:
        logger.warning("Nenhum setor retornado para o evento selecionado.")
        return

    target_sector_ids = _choose_sectors(sectors_map)

    # Monitor
    monitor = TicketMonitor(
        service=ticket_service,
        notifier=notifier,
        monitor_config=config.monitor,
        sectors_map=sectors_map,
    )

    monitor.run(event, target_sector_ids, client)


if __name__ == "__main__":
    main()
