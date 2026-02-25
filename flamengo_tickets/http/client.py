import time
from typing import Any, Dict, Optional

import requests
from requests import Response, RequestException

from flamengo_tickets.logging_config import logger
from flamengo_tickets.config import BASE_URL
from flamengo_tickets.domain.exceptions import RequestError
from flamengo_tickets.http.session import AJAX_HEADERS_BASE


class HttpClient:
    def __init__(
        self,
        session: requests.Session,
        max_retries: int = 3,
        backoff_base_seconds: float = 1.0,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.session = session
        self.max_retries = max_retries
        self.backoff_base_seconds = backoff_base_seconds
        self.timeout_seconds = timeout_seconds

        self.base_url = BASE_URL
        self.ajax_headers_token: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Util
    # ------------------------------------------------------------------ #
    def set_ajax_token(self, token: str) -> None:
        """Configura o header X-Xml-Http-Request-Token para requisições AJAX."""
        self.ajax_headers_token = token
        logger.debug(f"Header X-Xml-Http-Request-Token configurado: {bool(token)}")

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def _build_headers(self, extra: Optional[Dict[str, str]] = None, is_ajax: bool = False) -> Dict[str, str]:
        headers = dict(self.session.headers)
        if is_ajax:
            headers.update(AJAX_HEADERS_BASE)
            if self.ajax_headers_token:
                headers["X-Xml-Http-Request-Token"] = self.ajax_headers_token
        if extra:
            headers.update(extra)
        return headers

    # ------------------------------------------------------------------ #
    # Core request
    # ------------------------------------------------------------------ #
    def request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        is_ajax: bool = False,
    ) -> Response:
        url = self._build_url(path)
        last_exc: Optional[Exception] = None
        method_upper = method.upper()

        for attempt in range(1, self.max_retries + 1):
            built_headers = self._build_headers(headers, is_ajax=is_ajax)
            logger.debug(
                f"Request iniciado: {method_upper} {url} | tentativa {attempt}/{self.max_retries} "
                f"| ajax={is_ajax} | params={params}"
            )

            start = time.monotonic()
            try:
                if method_upper == "GET":
                    resp = self.session.get(
                        url,
                        params=params,
                        headers=built_headers,
                        timeout=self.timeout_seconds,
                    )
                elif method_upper == "POST":
                    resp = self.session.post(
                        url,
                        params=params,
                        data=data,
                        json=json,
                        headers=built_headers,
                        timeout=self.timeout_seconds,
                    )
                else:
                    # fallback genérico (caso queira usar outros métodos no futuro)
                    resp = self.session.request(
                        method=method_upper,
                        url=url,
                        params=params,
                        data=data,
                        json=json,
                        headers=built_headers,
                        timeout=self.timeout_seconds,
                    )

                elapsed = time.monotonic() - start
                bytes_len = len(resp.content or b"")
                logger.info(
                    f"Request finalizado: {method_upper} {url} | tentativa {attempt}/{self.max_retries} "
                    f"| status={resp.status_code} | tempo={elapsed:.3f}s | bytes={bytes_len}"
                )

                # Retry em 5xx
                if 500 <= resp.status_code < 600 and attempt < self.max_retries:
                    sleep_for = self.backoff_base_seconds * (2 ** (attempt - 1))
                    logger.warning(
                        f"Decisão de retry: status {resp.status_code} em {url} | "
                        f"backoff={sleep_for:.2f}s (tentativa {attempt}/{self.max_retries})"
                    )
                    time.sleep(sleep_for)
                    continue

                resp.raise_for_status()
                return resp

            except RequestException as exc:
                elapsed = time.monotonic() - start
                last_exc = exc
                logger.error(
                    f"RequestError ({type(exc).__name__}): {exc} | "
                    f"{method_upper} {url} | tentativa {attempt}/{self.max_retries} | tempo={elapsed:.3f}s"
                )

                if attempt >= self.max_retries:
                    break

                sleep_for = self.backoff_base_seconds * (2 ** (attempt - 1))
                logger.warning(
                    f"Decisão de retry: exceção em {url} | "
                    f"backoff={sleep_for:.2f}s (tentativa {attempt}/{self.max_retries})"
                )
                time.sleep(sleep_for)

        raise RequestError(f"Falha ao chamar {method_upper} {url}") from last_exc

    # Conveniências
    def get(self, path: str, **kwargs: Any) -> Response:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Response:
        return self.request("POST", path, **kwargs)
