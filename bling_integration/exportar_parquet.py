"""
Exporta os pedidos do SQLite para Parquet, pronto para o Power BI.

Uso:
    python exportar_parquet.py

Gera:
    exports/pedidos.parquet   — todos os pedidos
    exports/itens.parquet     — itens de cada pedido (expandidos)
"""

import json
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / "pedidos_bling.db"
EXPORT_DIR = Path(__file__).parent / "exports"


def exportar_pedidos(conn) -> pd.DataFrame:
    df = pd.read_sql_query("""
        SELECT
            id,
            conta,
            numero,
            data,
            data_saida,
            total,
            total_produtos,
            situacao_id,
            situacao_valor,
            contato_nome,
            contato_documento,
            loja_id,
            vendedor_nome,
            synced_at
        FROM pedidos
        ORDER BY data DESC
    """, conn)

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["data_saida"] = pd.to_datetime(df["data_saida"], errors="coerce")
    df["total"] = pd.to_numeric(df["total"], errors="coerce")
    df["total_produtos"] = pd.to_numeric(df["total_produtos"], errors="coerce")
    return df


def exportar_itens(conn) -> pd.DataFrame:
    """Expande os itens de cada pedido em linhas individuais."""
    rows = conn.execute("SELECT id, conta, data, payload FROM pedidos WHERE payload IS NOT NULL").fetchall()

    itens = []
    for pedido_id, conta, data, payload_str in rows:
        try:
            payload = json.loads(payload_str)
        except Exception:
            continue
        for item in payload.get("itens") or []:
            itens.append({
                "pedido_id":          pedido_id,
                "conta":              conta,
                "pedido_data":        data,
                "item_id":            item.get("id"),
                "codigo":             item.get("codigo"),
                "descricao":          item.get("descricao"),
                "unidade":            item.get("unidade"),
                "quantidade":         item.get("quantidade"),
                "valor_unitario":     item.get("valor"),
                "desconto":           item.get("desconto"),
                "aliquota_ipi":       item.get("aliquotaIPI"),
                "produto_id":         (item.get("produto") or {}).get("id"),
                "comissao_valor":     (item.get("comissao") or {}).get("valor"),
                "comissao_aliquota":  (item.get("comissao") or {}).get("aliquota"),
            })

    df = pd.DataFrame(itens)
    if not df.empty:
        df["pedido_data"] = pd.to_datetime(df["pedido_data"], errors="coerce")
        df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
        df["valor_unitario"] = pd.to_numeric(df["valor_unitario"], errors="coerce")
        df["valor_total"] = df["quantidade"] * df["valor_unitario"]
    return df


def main():
    EXPORT_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))

    print("Exportando pedidos...")
    df_pedidos = exportar_pedidos(conn)
    out_pedidos = EXPORT_DIR / "pedidos.parquet"
    df_pedidos.to_parquet(out_pedidos, index=False)
    print(f"  {len(df_pedidos):,} pedidos -> {out_pedidos}")

    print("Exportando itens...")
    df_itens = exportar_itens(conn)
    out_itens = EXPORT_DIR / "itens.parquet"
    df_itens.to_parquet(out_itens, index=False)
    print(f"  {len(df_itens):,} itens -> {out_itens}")

    conn.close()
    print("\nExportacao concluida! Arquivos em:", EXPORT_DIR.resolve())


if __name__ == "__main__":
    main()
