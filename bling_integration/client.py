"""
Cliente HTTP para a API v3 do Bling.

Gerencia rate limiting (3 req/s) e retry automático em caso de HTTP 429.
"""

from __future__ import annotations
import logging
import time

import requests

from auth import TokenManager

logger = logging.getLogger(__name__)

BASE_URL = "https://api.bling.com.br/Api/v3"
_MIN_INTERVAL = 1 / 3          # 3 requisições por segundo
_RETRY_WAIT_429 = 10.0         # segundos de espera ao receber 429
_MAX_RETRIES = 3


class BlingClient:
    def __init__(self, token_manager: TokenManager):
        self._token_manager = token_manager
        self._last_request_at: float = 0.0
        self._session = requests.Session()

    # ------------------------------------------------------------------
    # Método genérico
    # ------------------------------------------------------------------

    def get(self, path: str, params: dict | None = None) -> dict:
        """Executa GET autenticado com rate limiting e retry em 429."""
        url = f"{BASE_URL}{path}"
        params = params or {}

        for attempt in range(1, _MAX_RETRIES + 1):
            self._throttle()
            token = self._token_manager.get_access_token()
            resp = self._session.get(
                url,
                headers={"Authorization": f"Bearer {token}"},
                params=params,
                timeout=30,
            )

            if resp.status_code == 429:
                wait = _RETRY_WAIT_429 * attempt
                logger.warning("Rate limit atingido. Aguardando %.0fs (tentativa %d/%d).", wait, attempt, _MAX_RETRIES)
                time.sleep(wait)
                continue

            resp.raise_for_status()
            return resp.json()

        raise RuntimeError(f"Falha após {_MAX_RETRIES} tentativas em {url}")

    # ------------------------------------------------------------------
    # Endpoints específicos
    # ------------------------------------------------------------------

    def get_pedidos_page(self, pagina: int, data_inicial: str, data_final: str) -> dict:
        """
        Retorna uma página de pedidos de venda.

        Parâmetros de data no formato YYYY-MM-DD.
        O Bling rejeita intervalos maiores que 1 ano (HTTP 400).
        """
        return self.get("/pedidos/vendas", {
            "pagina": pagina,
            "limite": 100,
            "dataInicial": data_inicial,
            "dataFinal": data_final,
        })

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < _MIN_INTERVAL:
            time.sleep(_MIN_INTERVAL - elapsed)
        self._last_request_at = time.monotonic()
