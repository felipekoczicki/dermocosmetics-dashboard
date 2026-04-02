"""
Enriquecimento incremental de pedidos com detalhe completo.

Busca os campos completos (itens, parcelas, transporte, etc.) para pedidos
que ainda não foram enriquecidos. Para sozinho ao bater o limite diário da API
e retoma de onde parou na próxima execução.

Uso:
    python run_enriquecer.py                  # processa até o limite da API
    python run_enriquecer.py --limite 10000   # processa no máximo N pedidos
    python run_enriquecer.py --conta conta_1  # apenas uma conta
"""

from __future__ import annotations
import argparse
import json
import logging
import sqlite3
import sys
import time
from pathlib import Path

import requests

from auth import TokenManager
from client import BlingClient
from config import load_accounts
from db import Database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "pedidos_bling.db"
# Margem de segurança: para antes de atingir o limite diário
LIMITE_DIARIO = 110_000


def pendentes(conn: sqlite3.Connection, conta: str) -> list[int]:
    rows = conn.execute(
        "SELECT id FROM pedidos WHERE conta = ? AND detalhado = 0 ORDER BY data DESC",
        (conta,),
    ).fetchall()
    return [r[0] for r in rows]


def enriquecer_pedido(conn: sqlite3.Connection, client: BlingClient, pedido_id: int, conta: str) -> bool:
    try:
        resp = client.get_pedido(pedido_id)
        data = resp.get("data")
        if not data:
            return False
        payload_json = json.dumps(data, ensure_ascii=False)
        conn.execute(
            "UPDATE pedidos SET payload = ?, detalhado = 1, synced_at = datetime('now','localtime') WHERE id = ? AND conta = ?",
            (payload_json, pedido_id, conta),
        )
        conn.commit()
        return True
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            # Pedido não existe mais — marca como detalhado para não tentar novamente
            conn.execute("UPDATE pedidos SET detalhado = 1 WHERE id = ? AND conta = ?", (pedido_id, conta))
            conn.commit()
        return False


def progresso(conn: sqlite3.Connection) -> None:
    rows = conn.execute("""
        SELECT conta,
               SUM(CASE WHEN detalhado = 1 THEN 1 ELSE 0 END) AS prontos,
               COUNT(*) AS total
        FROM pedidos
        GROUP BY conta
    """).fetchall()
    for conta, prontos, total in rows:
        pct = prontos / total * 100 if total else 0
        filled = min(int(30 * prontos / total), 30) if total else 0
        bar = "#" * filled + "-" * (30 - filled)
        logger.info("[%s] [%s] %s/%s (%.1f%%)", conta, bar, f"{prontos:,}", f"{total:,}", pct)


def main() -> None:
    parser = argparse.ArgumentParser(description="Enriquecimento incremental de pedidos Bling")
    parser.add_argument("--limite", type=int, default=LIMITE_DIARIO, help="Máximo de pedidos a enriquecer nesta execução")
    parser.add_argument("--conta", default=None, help="Processar apenas esta conta (ex: conta_1)")
    args = parser.parse_args()

    accounts = load_accounts()
    if args.conta:
        accounts = [a for a in accounts if a.name == args.conta]

    conn = sqlite3.connect(str(DB_PATH))
    db = Database()

    logger.info("=" * 60)
    logger.info("Enriquecimento de pedidos — inicio")
    logger.info("=" * 60)
    progresso(conn)

    total_processados = 0
    inicio = time.time()

    try:
        for account in accounts:
            ids = pendentes(conn, account.name)
            if not ids:
                logger.info("[%s] Nenhum pedido pendente.", account.name)
                continue

            logger.info("[%s] %s pedidos para enriquecer.", account.name, f"{len(ids):,}")
            tm = TokenManager(account)
            client = BlingClient(tm)

            for i, pedido_id in enumerate(ids, 1):
                if total_processados >= args.limite:
                    logger.info("Limite de %s atingido. Execute novamente amanha para continuar.", f"{args.limite:,}")
                    break

                ok = enriquecer_pedido(conn, client, pedido_id, account.name)

                if ok:
                    total_processados += 1

                if i % 500 == 0:
                    elapsed = time.time() - inicio
                    velocidade = total_processados / elapsed * 3600 if elapsed > 0 else 0
                    restantes = len(ids) - i
                    eta_horas = restantes / velocidade if velocidade > 0 else 0
                    logger.info(
                        "[%s] %s/%s enriquecidos | %.0f/h | ETA: %.1fh",
                        account.name, f"{i:,}", f"{len(ids):,}", velocidade, eta_horas
                    )

            logger.info("[%s] Concluido nesta execucao.", account.name)

    except KeyboardInterrupt:
        logger.warning("Interrompido pelo usuario.")
    finally:
        logger.info("=" * 60)
        logger.info("Total enriquecidos nesta execucao: %s", f"{total_processados:,}")
        progresso(conn)
        conn.close()
        db.close()


if __name__ == "__main__":
    main()
