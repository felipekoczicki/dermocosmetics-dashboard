"""
Lógica de sincronização de pedidos.

Divide o intervalo de datas em janelas de até 1 ano (limite da API do Bling)
e itera por todas as páginas de cada janela.
"""

from __future__ import annotations
import logging
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from client import BlingClient
from db import Database

logger = logging.getLogger(__name__)

# O Bling rejeita intervalos > 1 ano; usamos 364 dias por segurança
_MAX_WINDOW_DAYS = 364


def _date_windows(start: date, end: date):
    """Gera tuplas (inicio, fim) com janelas de no máximo _MAX_WINDOW_DAYS dias."""
    current = start
    while current <= end:
        window_end = min(current + timedelta(days=_MAX_WINDOW_DAYS), end)
        yield current, window_end
        current = window_end + timedelta(days=1)


class SyncManager:
    def __init__(self, client: BlingClient, db: Database, account_name: str):
        self._client = client
        self._db = db
        self._account = account_name

    # ------------------------------------------------------------------
    # Modos de sincronização
    # ------------------------------------------------------------------

    def sync_full_history(self, start_date: date = date(2020, 1, 1)) -> int:
        """Importa todos os pedidos desde start_date até hoje."""
        logger.info("[%s] Iniciando importação completa a partir de %s", self._account, start_date)
        return self._sync_range(start_date, date.today())

    def sync_incremental(self) -> int:
        """Importa somente os pedidos novos desde a última sincronização.

        Para garantir que pedidos atualizados (ex.: mudança de status) também
        sejam captados, recua 1 dia em relação à data mais recente salva.
        """
        last = self._db.get_last_sync_date(self._account)
        if last is None:
            logger.info("[%s] Sem dados anteriores. Executando importação completa.", self._account)
            return self.sync_full_history()

        start = last - timedelta(days=1)
        logger.info("[%s] Sincronização incremental a partir de %s", self._account, start)
        return self._sync_range(start, date.today())

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _sync_range(self, start: date, end: date) -> int:
        total = 0
        for window_start, window_end in _date_windows(start, end):
            count = self._sync_window(window_start.isoformat(), window_end.isoformat())
            total += count
        logger.info("[%s] Total sincronizado: %d pedidos", self._account, total)
        return total

    def _sync_window(self, data_inicial: str, data_final: str) -> int:
        logger.info("[%s] Janela: %s ate %s", self._account, data_inicial, data_final)
        pagina = 1
        total = 0

        while True:
            resp = self._client.get_pedidos_page(pagina, data_inicial, data_final)
            pedidos = resp.get("data") or []

            if not pedidos:
                break

            # Busca detalhes completos (itens, parcelas, transporte, etc.)
            detalhados = []
            for p in pedidos:
                try:
                    resp_detalhe = self._client.get_pedido(p["id"])
                    detalhados.append(resp_detalhe.get("data") or p)
                except Exception as exc:
                    logger.warning("[%s] Falha ao detalhar pedido %s: %s", self._account, p.get("id"), exc)
                    detalhados.append(p)

            self._db.upsert_pedidos(detalhados, self._account)
            total += len(detalhados)

            meta = resp.get("meta") or {}
            total_paginas = int(meta.get("totalPaginas", 1))
            logger.debug("[%s] Página %d/%d (%d pedidos)", self._account, pagina, total_paginas, len(pedidos))

            if pagina >= total_paginas:
                break
            pagina += 1

        logger.info("[%s] %s ate %s: %d pedidos importados", self._account, data_inicial, data_final, total)
        return total
