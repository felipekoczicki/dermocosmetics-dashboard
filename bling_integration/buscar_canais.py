"""
Busca os canais de venda (lojas) cadastrados no Bling e salva o mapeamento
loja_id -> nome em exports/canais.json e exports/canais.csv.

Uso:
    python buscar_canais.py
"""

from __future__ import annotations
import json
import logging
import sys
from pathlib import Path

import pandas as pd

from auth import TokenManager
from client import BlingClient
from config import load_accounts

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

EXPORT_DIR = Path(__file__).parent / "exports"


def buscar_canais(client: BlingClient, conta: str) -> list[dict]:
    """Busca todos os canais de venda via paginação."""
    canais = []
    pagina = 1
    while True:
        resp = client.get("/canais/vendas", {"pagina": pagina, "limite": 100})
        dados = resp.get("data") or []
        if not dados:
            break
        canais.extend(dados)
        logger.info("[%s] Página %d: %d canais", conta, pagina, len(dados))
        if len(dados) < 100:
            break
        pagina += 1
    return canais


def main():
    EXPORT_DIR.mkdir(exist_ok=True)
    accounts = load_accounts()

    mapeamento: dict[str, str] = {}  # loja_id (str) -> nome do canal

    for account in accounts:
        logger.info("Buscando canais da %s...", account.name)
        tm = TokenManager(account)
        client = BlingClient(tm)

        try:
            canais = buscar_canais(client, account.name)
        except Exception as e:
            logger.error("[%s] Erro ao buscar canais: %s", account.name, e)
            continue

        for canal in canais:
            loja_id = str(canal.get("id", ""))
            nome = canal.get("descricao") or canal.get("nome") or canal.get("name") or ""
            if loja_id:
                mapeamento[loja_id] = nome
                logger.info("  %s -> %s", loja_id, nome)

    # Salvar JSON
    out_json = EXPORT_DIR / "canais.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(mapeamento, f, ensure_ascii=False, indent=2)
    logger.info("Salvo: %s (%d canais)", out_json, len(mapeamento))

    # Salvar CSV (para facilitar importação no Power BI)
    df = pd.DataFrame(
        [(k, v) for k, v in mapeamento.items()],
        columns=["loja_id", "canal_nome"]
    )
    df["loja_id"] = pd.to_numeric(df["loja_id"], errors="coerce")
    out_csv = EXPORT_DIR / "canais.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    logger.info("Salvo: %s", out_csv)

    print("\n=== CANAIS ENCONTRADOS ===")
    for loja_id, nome in sorted(mapeamento.items()):
        print(f"  {loja_id:>12} -> {nome}")


if __name__ == "__main__":
    main()
