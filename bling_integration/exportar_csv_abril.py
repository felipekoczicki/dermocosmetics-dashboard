"""
Exporta pedidos de abril/2026 enriquecidos (pedidos + itens + parcelas)
separados por conta (matriz / filial).
"""

import sqlite3
import json
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / "pedidos_bling.db"
EXPORT_DIR = Path(__file__).parent / "exports"

DATA_INI = "2026-04-01"
DATA_FIM = "2026-05-01"

CONTAS = [
    ("conta_1", "matriz"),
    ("conta_2", "filial"),
]


def build_pedidos(conn, conta: str) -> pd.DataFrame:
    rows = conn.execute(
        """
        SELECT id, conta, numero, data, data_saida, payload, synced_at
        FROM pedidos
        WHERE conta = ? AND data >= ? AND data < ?
        ORDER BY data DESC
        """,
        (conta, DATA_INI, DATA_FIM),
    ).fetchall()

    registros = []
    for pedido_id, conta_, numero, data, data_saida, payload_str, synced_at in rows:
        p = {}
        if payload_str:
            try:
                p = json.loads(payload_str)
            except Exception:
                pass

        situacao   = p.get("situacao") or {}
        contato    = p.get("contato") or {}
        loja       = p.get("loja") or {}
        vendedor   = p.get("vendedor") or {}
        desconto   = p.get("desconto") or {}
        categoria  = p.get("categoria") or {}
        nota       = p.get("notaFiscal") or {}
        tributacao = p.get("tributacao") or {}
        taxas      = p.get("taxas") or {}
        inter      = p.get("intermediador") or {}
        transp     = p.get("transporte") or {}
        etiqueta   = transp.get("etiqueta") or {}
        transp_c   = transp.get("contato") or {}

        registros.append({
            "id":                    pedido_id,
            "conta":                 conta_,
            "numero":                p.get("numero", numero),
            "numero_loja":           p.get("numeroLoja"),
            "numero_pedido_compra":  p.get("numeroPedidoCompra"),
            "data":                  p.get("data", data),
            "data_saida":            p.get("dataSaida", data_saida),
            "data_prevista":         p.get("dataPrevista"),
            "total_produtos":        p.get("totalProdutos"),
            "total":                 p.get("total"),
            "outras_despesas":       p.get("outrasDespesas"),
            "desconto_valor":        desconto.get("valor"),
            "desconto_unidade":      desconto.get("unidade"),
            "situacao_id":           situacao.get("id"),
            "situacao_valor":        situacao.get("valor"),
            "contato_id":            contato.get("id"),
            "contato_nome":          contato.get("nome"),
            "contato_tipo_pessoa":   contato.get("tipoPessoa"),
            "contato_documento":     contato.get("numeroDocumento"),
            "loja_id":               loja.get("id"),
            "vendedor_id":           vendedor.get("id"),
            "categoria_id":          categoria.get("id"),
            "nota_fiscal_id":        nota.get("id"),
            "total_icms":            tributacao.get("totalICMS"),
            "total_ipi":             tributacao.get("totalIPI"),
            "taxa_comissao":         taxas.get("taxaComissao"),
            "custo_frete":           taxas.get("custoFrete"),
            "valor_base":            taxas.get("valorBase"),
            "frete_por_conta":       transp.get("fretePorConta"),
            "frete":                 transp.get("frete"),
            "qtd_volumes":           transp.get("quantidadeVolumes"),
            "peso_bruto":            transp.get("pesoBruto"),
            "prazo_entrega":         transp.get("prazoEntrega"),
            "transportador_id":      transp_c.get("id"),
            "transportador_nome":    transp_c.get("nome"),
            "entrega_nome":          etiqueta.get("nome"),
            "entrega_endereco":      etiqueta.get("endereco"),
            "entrega_numero":        etiqueta.get("numero"),
            "entrega_complemento":   etiqueta.get("complemento"),
            "entrega_bairro":        etiqueta.get("bairro"),
            "entrega_municipio":     etiqueta.get("municipio"),
            "entrega_uf":            etiqueta.get("uf"),
            "entrega_cep":           etiqueta.get("cep"),
            "intermediador_cnpj":    inter.get("cnpj"),
            "intermediador_usuario": inter.get("nomeUsuario"),
            "observacoes":           p.get("observacoes"),
            "observacoes_internas":  p.get("observacoesInternas"),
            "detalhado":             1 if p.get("itens") is not None else 0,
            "synced_at":             synced_at,
        })

    df = pd.DataFrame(registros)
    for col in ["data", "data_saida", "data_prevista"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def build_itens(conn, conta: str) -> pd.DataFrame:
    rows = conn.execute(
        """
        SELECT id, conta, data, payload
        FROM pedidos
        WHERE conta = ? AND data >= ? AND data < ?
          AND detalhado = 1 AND payload LIKE '%itens%'
        """,
        (conta, DATA_INI, DATA_FIM),
    ).fetchall()

    itens = []
    for pedido_id, conta_, data, payload_str in rows:
        try:
            p = json.loads(payload_str)
        except Exception:
            continue
        for item in p.get("itens") or []:
            produto  = item.get("produto") or {}
            comissao = item.get("comissao") or {}
            nat_op   = item.get("naturezaOperacao") or {}
            itens.append({
                "pedido_id":            pedido_id,
                "conta":                conta_,
                "pedido_data":          data,
                "item_id":              item.get("id"),
                "codigo":               item.get("codigo"),
                "descricao":            item.get("descricao"),
                "descricao_detalhada":  item.get("descricaoDetalhada"),
                "unidade":              item.get("unidade"),
                "quantidade":           item.get("quantidade"),
                "valor_unitario":       item.get("valor"),
                "desconto":             item.get("desconto"),
                "aliquota_ipi":         item.get("aliquotaIPI"),
                "produto_id":           produto.get("id"),
                "comissao_base":        comissao.get("base"),
                "comissao_aliquota":    comissao.get("aliquota"),
                "comissao_valor":       comissao.get("valor"),
                "natureza_operacao_id": nat_op.get("id"),
            })

    df = pd.DataFrame(itens)
    if not df.empty:
        df["pedido_data"]    = pd.to_datetime(df["pedido_data"], errors="coerce")
        df["quantidade"]     = pd.to_numeric(df["quantidade"], errors="coerce")
        df["valor_unitario"] = pd.to_numeric(df["valor_unitario"], errors="coerce")
        df["valor_total"]    = df["quantidade"] * df["valor_unitario"]
    return df


def build_parcelas(conn, conta: str) -> pd.DataFrame:
    rows = conn.execute(
        """
        SELECT id, conta, payload
        FROM pedidos
        WHERE conta = ? AND data >= ? AND data < ?
          AND detalhado = 1 AND payload LIKE '%parcelas%'
        """,
        (conta, DATA_INI, DATA_FIM),
    ).fetchall()

    parcelas = []
    for pedido_id, conta_, payload_str in rows:
        try:
            p = json.loads(payload_str)
        except Exception:
            continue
        for parc in p.get("parcelas") or []:
            forma = parc.get("formaPagamento") or {}
            parcelas.append({
                "pedido_id":         pedido_id,
                "conta":             conta_,
                "parcela_id":        parc.get("id"),
                "data_vencimento":   parc.get("dataVencimento"),
                "valor":             parc.get("valor"),
                "observacoes":       parc.get("observacoes"),
                "forma_pagamento_id": forma.get("id"),
            })

    df = pd.DataFrame(parcelas)
    if not df.empty:
        df["data_vencimento"] = pd.to_datetime(df["data_vencimento"], errors="coerce")
        df["valor"]           = pd.to_numeric(df["valor"], errors="coerce")
    return df


def main():
    EXPORT_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))

    for conta, label in CONTAS:
        print(f"\n[{label}] Processando...")

        df_p    = build_pedidos(conn, conta)
        df_i    = build_itens(conn, conta)
        df_parc = build_parcelas(conn, conta)

        df_p.to_csv(EXPORT_DIR / f"pedidos_abril_2026_{label}.csv",   index=False, encoding="utf-8-sig")
        df_i.to_csv(EXPORT_DIR / f"itens_abril_2026_{label}.csv",     index=False, encoding="utf-8-sig")
        df_parc.to_csv(EXPORT_DIR / f"parcelas_abril_2026_{label}.csv", index=False, encoding="utf-8-sig")

        print(f"  pedidos : {len(df_p):,}  -> pedidos_abril_2026_{label}.csv")
        print(f"  itens   : {len(df_i):,}  -> itens_abril_2026_{label}.csv")
        print(f"  parcelas: {len(df_parc):,}  -> parcelas_abril_2026_{label}.csv")

    conn.close()
    print(f"\nArquivos em: {EXPORT_DIR.resolve()}")


if __name__ == "__main__":
    main()
