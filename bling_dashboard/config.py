# =============================================================
# config.py — Configurações editáveis da dashboard
# =============================================================

# Caminho para os arquivos Parquet gerados pela integração Bling
PARQUET_DIR = r"C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration\exports"

# ------------------------------------------------------------------
# Mapeamento de canais de venda pelo CNPJ do intermediador
# Edite aqui para renomear ou agrupar canais conforme sua operação
# ------------------------------------------------------------------
CANAL_MAP = {
    "27.415.911/0001-36": "Mercado Livre",
    "35.635.824/0001-12": "Shopee",
    "03.007.331/0001-41": "Amazon",
    "15.436.940/0001-03": "Amazon",
    "39.420.373/0002-38": "Magalu",
    "39.420.373/0001-57": "Magalu",
    "47.960.950/0001-21": "TikTok Shop",
    "01.239.313/0001-60": "Outro",
    "33.041.260/0652-90": "Outro",
}
CANAL_DIRETO = "Venda Direta / Shopify"

# ------------------------------------------------------------------
# Situações de pedido (valores do campo situacao_valor)
# ------------------------------------------------------------------
# Pedidos excluídos do faturamento (ex: cancelados)
SITUACOES_EXCLUIDAS = [2]

# Valor que representa "pedido pago/atendido" no gráfico de comparação
SITUACAO_PAGO = 1

# ------------------------------------------------------------------
# Nomes das contas (aparece nos filtros e tooltips)
# ------------------------------------------------------------------
CONTA_NOMES = {
    "conta_1": "Conta 1",
    "conta_2": "Conta 2",
}
