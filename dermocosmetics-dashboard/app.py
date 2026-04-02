import streamlit as st
import pandas as pd
from data.dados_2025 import gerar_dados
from components.kpi_cards import render_kpi_cards
from components.share_chart import render_share_chart
from components.evolucao_chart import render_evolucao_chart
from components.ranking_chart import render_ranking_chart

st.set_page_config(
    page_title="Dashboard Dermocosméticos 2025",
    page_icon="💊",
    layout="wide",
)

# Cabeçalho
st.title("Dashboard de Share de Mercado — Dermocosméticos 2025")
st.caption("Segmento varejo | Dados de exemplo para análise de mercado")
st.divider()

# Carrega dados
@st.cache_data
def load_data():
    return gerar_dados()

df_2025, df_2024 = load_data()

# ── Sidebar de Filtros ──────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filtros")

    meses_nomes = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                   "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    meses_sel = st.multiselect(
        "Mês",
        options=meses_nomes,
        default=meses_nomes,
    )

    categorias_sel = st.multiselect(
        "Categoria",
        options=sorted(df_2025["categoria"].unique()),
        default=sorted(df_2025["categoria"].unique()),
    )

    canais_sel = st.multiselect(
        "Canal de Venda",
        options=sorted(df_2025["canal"].unique()),
        default=sorted(df_2025["canal"].unique()),
    )

    marcas_sel = st.multiselect(
        "Marcas",
        options=sorted(df_2025["marca"].unique()),
        default=sorted(df_2025["marca"].unique()),
    )

# Aplica filtros
def aplicar_filtros(df):
    return df[
        (df["mes_nome"].isin(meses_sel)) &
        (df["categoria"].isin(categorias_sel)) &
        (df["canal"].isin(canais_sel)) &
        (df["marca"].isin(marcas_sel))
    ]

df_filtrado = aplicar_filtros(df_2025)
df_2024_filtrado = aplicar_filtros(df_2024)

if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com os filtros selecionados.")
    st.stop()

# ── KPI Cards ───────────────────────────────────────────────────────────────
render_kpi_cards(df_filtrado, df_2024_filtrado)
st.divider()

# ── Share de Mercado + Ranking ───────────────────────────────────────────────
col_left, col_right = st.columns([1.2, 1])
with col_left:
    render_share_chart(df_filtrado)
with col_right:
    render_ranking_chart(df_filtrado)

st.divider()

# ── Evolução Mensal ─────────────────────────────────────────────────────────
render_evolucao_chart(df_filtrado)
st.divider()

# ── Tabela Detalhada ────────────────────────────────────────────────────────
with st.expander("Tabela Detalhada", expanded=False):
    tabela = df_filtrado.groupby(["marca", "categoria", "canal"]).agg(
        faturamento=("faturamento", "sum"),
        pedidos=("pedidos", "sum"),
        ticket_medio=("ticket_medio", "mean"),
    ).reset_index()
    tabela["faturamento"] = tabela["faturamento"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    tabela["ticket_medio"] = tabela["ticket_medio"].apply(lambda x: f"R$ {x:.2f}".replace(".", ","))
    tabela["pedidos"] = tabela["pedidos"].apply(lambda x: f"{x:,}".replace(",", "."))
    tabela.columns = ["Marca", "Categoria", "Canal", "Faturamento", "Pedidos", "Ticket Médio"]
    st.dataframe(tabela, use_container_width=True, hide_index=True)

st.caption("Dados fictícios gerados para fins de análise e demonstração.")
