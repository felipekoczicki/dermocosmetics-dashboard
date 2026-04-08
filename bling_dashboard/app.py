# =============================================================
# app.py — Dashboard Bling | Ponto de entrada
# =============================================================
# Para rodar:
#   cd bling_dashboard
#   streamlit run app.py

import streamlit as st
import pandas as pd
from data.loader import carregar_pedidos, carregar_itens, filtrar_periodo, filtrar_periodo_itens
from components.aba_receita import render_receita
from config import CONTA_NOMES

st.set_page_config(
    page_title="Dashboard Bling",
    page_icon="📊",
    layout="wide",
)

# ------------------------------------------------------------------
# Sidebar — Filtros globais
# ------------------------------------------------------------------

with st.sidebar:
    st.title("📊 Dashboard Bling")
    st.divider()

    df_pedidos_raw = carregar_pedidos()
    df_itens_raw = carregar_itens()

    # Filtro de conta
    contas_disponiveis = sorted(df_pedidos_raw["conta"].unique())
    contas_nomes = [CONTA_NOMES.get(c, c) for c in contas_disponiveis]
    contas_sel = st.multiselect(
        "Conta",
        options=contas_disponiveis,
        default=contas_disponiveis,
        format_func=lambda c: CONTA_NOMES.get(c, c),
    )

    # Filtro de período global
    st.markdown("**Período de análise**")
    data_min = df_pedidos_raw["data"].min().date()
    data_max = df_pedidos_raw["data"].max().date()

    data_inicio = st.date_input("De", value=pd.Timestamp("2025-01-01").date(), min_value=data_min, max_value=data_max, format="DD/MM/YYYY")
    data_fim = st.date_input("Até", value=data_max, min_value=data_min, max_value=data_max, format="DD/MM/YYYY")

    st.divider()
    if st.button("🔄 Recarregar dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption(f"Dados atualizados a cada hora automaticamente.\nÚltimo registro: {data_max}")

# ------------------------------------------------------------------
# Aplicar filtros globais
# ------------------------------------------------------------------

df_pedidos = df_pedidos_raw[df_pedidos_raw["conta"].isin(contas_sel)]
df_pedidos = filtrar_periodo(df_pedidos, pd.Timestamp(data_inicio), pd.Timestamp(data_fim))
df_itens = filtrar_periodo_itens(df_itens_raw, df_pedidos)

# ------------------------------------------------------------------
# Abas
# ------------------------------------------------------------------

aba_receita, = st.tabs(["💰 Receita"])

with aba_receita:
    render_receita(df_pedidos, df_itens)
