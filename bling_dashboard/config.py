# =============================================================
# config.py — Configurações editáveis da dashboard
# =============================================================
# Edite este arquivo para personalizar a dashboard sem mexer no código.
# Após salvar, recarregue a página no navegador para ver as mudanças.
# =============================================================

# ------------------------------------------------------------------
# Caminhos dos arquivos
# ------------------------------------------------------------------
PARQUET_DIR = r"C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration\exports"
CANAIS_CSV  = r"C:\Users\Lenovo\Desktop\Claude_Cloude_Project\bling_integration\exports\canais_template.csv"

# ------------------------------------------------------------------
# Nomes das contas (aparece nos filtros)
# ------------------------------------------------------------------
CONTA_NOMES = {
    "conta_1": "Conta 1",
    "conta_2": "Conta 2",
}

# ------------------------------------------------------------------
# Situações de pedido
# ------------------------------------------------------------------
SITUACOES_EXCLUIDAS = [2]   # 2 = Cancelado — excluído de todos os cálculos
SITUACAO_PAGO       = 1     # 1 = Atendido  — usado no gráfico de pedidos pagos

# ------------------------------------------------------------------
# GRÁFICOS — altere o tipo sem mexer no código
# ------------------------------------------------------------------
# Opções disponíveis para cada gráfico:
#
#   Gráficos de comparação de períodos:
#     "line"   → Linha
#     "bar"    → Barras verticais
#     "area"   → Área
#
#   Gráficos de canal e produtos:
#     "bar_h"  → Barras horizontais
#     "bar_v"  → Barras verticais
#     "pie"    → Pizza
#     "donut"  → Rosca
# ------------------------------------------------------------------

GRAFICOS = {
    # Aba Receita — Comparação de períodos
    "receita_diaria":         "line",     # line | bar | area
    "pedidos_pagos_diarios":  "bar",      # line | bar | area

    # Aba Receita — Por canal
    "faturamento_canal":      "bar_h",    # bar_h | bar_v | pie | donut
    "ticket_medio_canal":     "bar_h",    # bar_h | bar_v | pie | donut
    "pedidos_canal":          "bar_v",    # bar_h | bar_v | pie | donut

    # Aba Receita — Produtos
    "produtos_faturamento":   "bar_h",    # bar_h | bar_v
    "produtos_quantidade":    "bar_h",    # bar_h | bar_v
}

# ------------------------------------------------------------------
# CORES
# ------------------------------------------------------------------
COR_PERIODO_A   = "#1f77b4"   # Azul  — Período A nos gráficos de comparação
COR_PERIODO_B   = "#ff7f0e"   # Laranja — Período B nos gráficos de comparação
PALETA_CANAIS   = "Set2"      # Paleta dos gráficos de canal
                               # Opções: Set1, Set2, Set3, Pastel1, Pastel2,
                               #         Dark2, Bold, Vivid, Antique, Safe

# ------------------------------------------------------------------
# TÍTULOS DOS GRÁFICOS — altere o texto que aparece em cada gráfico
# ------------------------------------------------------------------
TITULOS = {
    "receita_diaria":         "Receita Diária",
    "pedidos_pagos_diarios":  "Pedidos Pagos por Dia",
    "faturamento_canal":      "Faturamento por Canal",
    "ticket_medio_canal":     "Ticket Médio por Canal",
    "pedidos_canal":          "Quantidade de Pedidos por Canal",
    "produtos_faturamento":   "Produtos Mais Vendidos — Faturamento",
    "produtos_quantidade":    "Produtos Mais Vendidos — Quantidade",
}

# ------------------------------------------------------------------
# QUANTIDADE DE PRODUTOS no ranking
# ------------------------------------------------------------------
TOP_PRODUTOS = 15   # Quantos produtos exibir no ranking (ex: 10, 15, 20)
