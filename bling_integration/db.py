"""
Persistência dos pedidos em SQLite.

Usa upsert (INSERT OR REPLACE) pela chave (id, conta) para garantir
idempotência: rodar a sincronização mais de uma vez não gera duplicatas.
"""

from __future__ import annotations
import json
import logging
import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "pedidos_bling.db"

_DDL = """
CREATE TABLE IF NOT EXISTS pedidos (
    id               INTEGER NOT NULL,
    conta            TEXT    NOT NULL,
    numero           TEXT,
    data             TEXT,
    data_saida       TEXT,
    total            REAL,
    total_produtos   REAL,
    situacao_id      INTEGER,
    situacao_valor   TEXT,
    contato_nome     TEXT,
    contato_documento TEXT,
    loja_id          INTEGER,
    vendedor_nome    TEXT,
    payload          TEXT,   -- JSON completo do pedido
    synced_at        TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
    PRIMARY KEY (id, conta)
);

CREATE INDEX IF NOT EXISTS idx_pedidos_conta_data ON pedidos (conta, data);
"""

_UPSERT = """
INSERT INTO pedidos
    (id, conta, numero, data, data_saida, total, total_produtos,
     situacao_id, situacao_valor, contato_nome, contato_documento,
     loja_id, vendedor_nome, payload, synced_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'))
ON CONFLICT(id, conta) DO UPDATE SET
    numero            = excluded.numero,
    data              = excluded.data,
    data_saida        = excluded.data_saida,
    total             = excluded.total,
    total_produtos    = excluded.total_produtos,
    situacao_id       = excluded.situacao_id,
    situacao_valor    = excluded.situacao_valor,
    contato_nome      = excluded.contato_nome,
    contato_documento = excluded.contato_documento,
    loja_id           = excluded.loja_id,
    vendedor_nome     = excluded.vendedor_nome,
    payload           = excluded.payload,
    synced_at         = datetime('now', 'localtime');
"""


class Database:
    def __init__(self, path: Path = DB_PATH):
        self._conn = sqlite3.connect(str(path), check_same_thread=False)
        self._conn.executescript(_DDL)
        self._conn.commit()
        logger.debug("Banco de dados aberto: %s", path)

    # ------------------------------------------------------------------
    # Escrita
    # ------------------------------------------------------------------

    def upsert_pedidos(self, pedidos: list[dict], conta: str) -> None:
        rows = [self._flatten(p, conta) for p in pedidos]
        self._conn.executemany(_UPSERT, rows)
        self._conn.commit()

    # ------------------------------------------------------------------
    # Leitura
    # ------------------------------------------------------------------

    def get_last_sync_date(self, conta: str) -> date | None:
        """Retorna a data do pedido mais recente salvo para a conta."""
        row = self._conn.execute(
            "SELECT MAX(data) FROM pedidos WHERE conta = ?", (conta,)
        ).fetchone()
        if row and row[0]:
            return date.fromisoformat(row[0])
        return None

    def count(self, conta: str | None = None) -> int:
        if conta:
            return self._conn.execute(
                "SELECT COUNT(*) FROM pedidos WHERE conta = ?", (conta,)
            ).fetchone()[0]
        return self._conn.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]

    def to_dataframe(self, conta: str | None = None) -> pd.DataFrame:
        """Retorna todos os pedidos como DataFrame (sem a coluna payload)."""
        query = "SELECT id, conta, numero, data, data_saida, total, total_produtos, situacao_id, situacao_valor, contato_nome, contato_documento, loja_id, vendedor_nome, synced_at FROM pedidos"
        params: list = []
        if conta:
            query += " WHERE conta = ?"
            params.append(conta)
        return pd.read_sql_query(query, self._conn, params=params)

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._conn.close()

    # ------------------------------------------------------------------
    # Interno
    # ------------------------------------------------------------------

    @staticmethod
    def _flatten(p: dict, conta: str) -> tuple:
        situacao = p.get("situacao") or {}
        contato = p.get("contato") or {}
        loja = p.get("loja") or {}
        vendedor = p.get("vendedor") or {}
        return (
            p.get("id"),
            conta,
            p.get("numero"),
            p.get("data"),
            p.get("dataSaida"),
            p.get("total"),
            p.get("totalProdutos"),
            situacao.get("id"),
            situacao.get("valor"),
            contato.get("nome"),
            contato.get("numeroDocumento"),
            loja.get("id"),
            vendedor.get("nome"),
            json.dumps(p, ensure_ascii=False),
        )
