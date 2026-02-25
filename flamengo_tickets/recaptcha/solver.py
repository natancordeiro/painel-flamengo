import os
import re
from twocaptcha import TwoCaptcha

from flamengo_tickets.config import BASE_URL
from flamengo_tickets.logging_config import logger
from flamengo_tickets.http.client import HttpClient

# Regex para extrair data-sitekey
_SITEKEY_PATTERN = re.compile(
    r'<div[^>]+id=["\']recaptcha["\'][^>]+data-sitekey=["\']([^"\']+)["\']',
    re.IGNORECASE,
)

def _get_event_page_url(event_id: int) -> str:
    return f"{BASE_URL}/buy/sector?event={event_id}"

def _fetch_sitekey(client: HttpClient, event_id: int) -> str:
    """
    Usa o MESMO client logado para acessar a página do setor.
    """
    page_url = _get_event_page_url(event_id)
    logger.info(f"Acessando página do setor logado: {page_url}")

    # Usa o client logado (HttpClient)
    resp = client.get(page_url)
    html = resp.text

    match = _SITEKEY_PATTERN.search(html)
    if not match:
        raise RuntimeError("Sitekey não encontrado na página de setor.")

    sitekey = match.group(1)
    logger.info(f"Sitekey encontrado: {sitekey}")
    return sitekey, page_url


def _create_two_captcha_solver() -> TwoCaptcha:
    api_key = os.getenv("APIKEY_2CAPTCHA", "").strip()
    if not api_key:
        raise RuntimeError("APIKEY_2CAPTCHA não definida.")
    return TwoCaptcha(api_key)


def get_recaptcha_token(client: HttpClient, event_id: int, sector_id: int) -> str:
    """
    client → HttpClient já logado
    """
    logger.info(f"Resolvendo reCAPTCHA para event={event_id}, sector={sector_id}")

    # 1) Buscar sitekey na página logado
    sitekey, page_url = _fetch_sitekey(client, event_id)

    # 2) Criar solver
    solver = _create_two_captcha_solver()

    # 3) Solicitar ao 2Captcha
    logger.info(f"Enviando para 2Captcha | sitekey={sitekey} | url={page_url}")

    result = solver.recaptcha(
        sitekey=sitekey,
        url=page_url,
    )

    token = result.get("code") if isinstance(result, dict) else str(result)

    if not token:
        raise RuntimeError(f"2Captcha retornou resposta inválida: {result!r}")

    logger.info("Token reCAPTCHA recebido com sucesso.")
    return token
