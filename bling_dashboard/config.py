# =============================================================
# config.py — Configurações editáveis da dashboard
# =============================================================

# Caminho para os arquivos Parquet gerados pela integração Bling
PARQUET_DIR = r"C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration\exports"

# ------------------------------------------------------------------
# Arquivo CSV com mapeamento loja_id -> canal_nome
# Edite diretamente o arquivo canais_template.csv para renomear canais
# ------------------------------------------------------------------
CANAIS_CSV = r"C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration\exports\canais_template.csv"

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
