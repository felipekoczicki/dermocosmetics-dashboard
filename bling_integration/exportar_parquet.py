"""
Exporta os pedidos do SQLite para Parquet, pronto para o Power BI.

Gera dois arquivos:
    exports/pedidos.parquet  — 1 linha por pedido, todos os campos
    exports/itens.parquet    — 1 linha por item (produto), relacionado por pedido_id

Uso:
    python exportar_parquet.py
"""

import json
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent / "pedidos_bling.db"
EXPORT_DIR = Path(__file__).parent / "exports"


def exportar_pedidos(conn) -> pd.DataFrame:
    rows = conn.execute("""
        SELECT id, conta, numero, data, data_saida, payload, synced_at
        FROM pedidos
        ORDER BY data DESC
    """).fetchall()

    registros = []
    for pedido_id, conta, numero, data, data_saida, payload_str, synced_at in rows:
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
        transp_contato = transp.get("contato") or {}

        registros.append({
            # Identificação
            "id":                    pedido_id,
            "conta":                 conta,
            "numero":                p.get("numero", numero),
            "numero_loja":           p.get("numeroLoja"),
            "numero_pedido_compra":  p.get("numeroPedidoCompra"),
            # Datas
            "data":                  p.get("data", data),
            "data_saida":            p.get("dataSaida", data_saida),
            "data_prevista":         p.get("dataPrevista"),
            # Valores
            "total_produtos":        p.get("totalProdutos"),
            "total":                 p.get("total"),
            "outras_despesas":       p.get("outrasDespesas"),
            "desconto_valor":        desconto.get("valor"),
            "desconto_unidade":      desconto.get("unidade"),
            # Situação
            "situacao_id":           situacao.get("id"),
            "situacao_valor":        situacao.get("valor"),
            # Contato
            "contato_id":            contato.get("id"),
            "contato_nome":          contato.get("nome"),
            "contato_tipo_pessoa":   contato.get("tipoPessoa"),
            "contato_documento":     contato.get("numeroDocumento"),
            # Loja / Vendedor
            "loja_id":               loja.get("id"),
            "vendedor_id":           vendedor.get("id"),
            # Categoria / NF
            "categoria_id":          categoria.get("id"),
            "nota_fiscal_id":        nota.get("id"),
            # Tributação
            "total_icms":            tributacao.get("totalICMS"),
            "total_ipi":             tributacao.get("totalIPI"),
            # Taxas
            "taxa_comissao":         taxas.get("taxaComissao"),
            "custo_frete":           taxas.get("custoFrete"),
            "valor_base":            taxas.get("valorBase"),
            # Transporte
            "frete_por_conta":       transp.get("fretePorConta"),
            "frete":                 transp.get("frete"),
            "qtd_volumes":           transp.get("quantidadeVolumes"),
            "peso_bruto":            transp.get("pesoBruto"),
            "prazo_entrega":         transp.get("prazoEntrega"),
            "transportador_id":      transp_contato.get("id"),
            "transportador_nome":    transp_contato.get("nome"),
            "entrega_nome":          etiqueta.get("nome"),
            "entrega_endereco":      etiqueta.get("endereco"),
            "entrega_numero":        etiqueta.get("numero"),
            "entrega_complemento":   etiqueta.get("complemento"),
            "entrega_bairro":        etiqueta.get("bairro"),
            "entrega_municipio":     etiqueta.get("municipio"),
            "entrega_uf":            etiqueta.get("uf"),
            "entrega_cep":           etiqueta.get("cep"),
            # Intermediador
            "intermediador_cnpj":    inter.get("cnpj"),
            "intermediador_usuario": inter.get("nomeUsuario"),
            # Observações
            "observacoes":           p.get("observacoes"),
            "observacoes_internas":  p.get("observacoesInternas"),
            # Controle
            "detalhado":             1 if p.get("itens") is not None else 0,
            "synced_at":             synced_at,
        })

    df = pd.DataFrame(registros)
    for col in ["data", "data_saida", "data_prevista"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["total", "total_produtos", "frete", "total_icms", "total_ipi"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def exportar_itens(conn) -> pd.DataFrame:
    rows = conn.execute("""
        SELECT id, conta, data, payload
        FROM pedidos
        WHERE detalhado = 1 AND payload LIKE '%"itens"%'
    """).fetchall()

    itens = []
    for pedido_id, conta, data, payload_str in rows:
        try:
            p = json.loads(payload_str)
        except Exception:
            continue
        for item in p.get("itens") or []:
            produto   = item.get("produto") or {}
            comissao  = item.get("comissao") or {}
            nat_op    = item.get("naturezaOperacao") or {}
            itens.append({
                "pedido_id":           pedido_id,
                "conta":               conta,
                "pedido_data":         data,
                "item_id":             item.get("id"),
                "codigo":              item.get("codigo"),
                "descricao":           item.get("descricao"),
                "descricao_detalhada": item.get("descricaoDetalhada"),
                "unidade":             item.get("unidade"),
                "quantidade":          item.get("quantidade"),
                "valor_unitario":      item.get("valor"),
                "desconto":            item.get("desconto"),
                "aliquota_ipi":        item.get("aliquotaIPI"),
                "produto_id":          produto.get("id"),
                "comissao_base":       comissao.get("base"),
                "comissao_aliquota":   comissao.get("aliquota"),
                "comissao_valor":      comissao.get("valor"),
                "natureza_operacao_id": nat_op.get("id"),
            })

    df = pd.DataFrame(itens)
    if not df.empty:
        df["pedido_data"]   = pd.to_datetime(df["pedido_data"], errors="coerce")
        df["quantidade"]    = pd.to_numeric(df["quantidade"], errors="coerce")
        df["valor_unitario"] = pd.to_numeric(df["valor_unitario"], errors="coerce")
        df["valor_total"]   = df["quantidade"] * df["valor_unitario"]
    return df


def exportar_parcelas(conn) -> pd.DataFrame:
    rows = conn.execute("""
        SELECT id, conta, payload
        FROM pedidos
        WHERE detalhado = 1 AND payload LIKE '%"parcelas"%'
    """).fetchall()

    parcelas = []
    for pedido_id, conta, payload_str in rows:
        try:
            p = json.loads(payload_str)
        except Exception:
            continue
        for parc in p.get("parcelas") or []:
            forma = parc.get("formaPagamento") or {}
            parcelas.append({
                "pedido_id":          pedido_id,
                "conta":              conta,
                "parcela_id":         parc.get("id"),
                "data_vencimento":    parc.get("dataVencimento"),
                "valor":              parc.get("valor"),
                "observacoes":        parc.get("observacoes"),
                "forma_pagamento_id": forma.get("id"),
            })

    df = pd.DataFrame(parcelas)
    if not df.empty:
        df["data_vencimento"] = pd.to_datetime(df["data_vencimento"], errors="coerce")
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    return df


def main():
    EXPORT_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))

    total = conn.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    detalhados = conn.execute("SELECT COUNT(*) FROM pedidos WHERE detalhado = 1").fetchone()[0]
    print(f"\nPedidos no banco : {total:,}")
    print(f"Com detalhe      : {detalhados:,} ({detalhados/total*100:.1f}%)")
    print(f"Sem detalhe      : {total-detalhados:,}\n")

    print("Exportando pedidos...")
    df_pedidos = exportar_pedidos(conn)
    out = EXPORT_DIR / "pedidos.parquet"
    df_pedidos.to_parquet(out, index=False)
    print(f"  {len(df_pedidos):,} linhas -> {out}")

    print("Exportando itens...")
    df_itens = exportar_itens(conn)
    out = EXPORT_DIR / "itens.parquet"
    df_itens.to_parquet(out, index=False)
    print(f"  {len(df_itens):,} linhas -> {out}")

    print("Exportando parcelas...")
    df_parc = exportar_parcelas(conn)
    out = EXPORT_DIR / "parcelas.parquet"
    df_parc.to_parquet(out, index=False)
    print(f"  {len(df_parc):,} linhas -> {out}")

    conn.close()
    print(f"\nArquivos em: {EXPORT_DIR.resolve()}")


if __name__ == "__main__":
    main()
