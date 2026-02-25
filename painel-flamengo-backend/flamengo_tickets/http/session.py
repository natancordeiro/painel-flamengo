import requests

from flamengo_tickets.logging_config import logger

BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/133.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    # IMPORTANTE: só encodings que o requests descomprime sozinho
    "Accept-Encoding": "gzip, deflate",
}

AJAX_HEADERS_BASE = {
    "Accept": "*/*",
    "Accept-Language": BASE_HEADERS["Accept-Language"],
    "Accept-Encoding": BASE_HEADERS["Accept-Encoding"],
    "User-Agent": BASE_HEADERS["User-Agent"],
    "X-Requested-With": "XMLHttpRequest",
}


def create_session() -> requests.Session:
    logger.debug("Criando sessão HTTP com cabeçalhos base")
    session = requests.Session()
    session.headers.update(BASE_HEADERS)
    return session
