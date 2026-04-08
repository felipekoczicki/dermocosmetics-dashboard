# =============================================================
# components/aba_receita.py — Aba de Receita
# =============================================================

from __future__ import annotations
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import SITUACAO_PAGO


# ------------------------------------------------------------------
# Helpers de formatação
# ------------------------------------------------------------------

def _fmt_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _kpi(col, label: str, valor: str, delta: str | None = None):
    with col:
        st.metric(label=label, value=valor, delta=delta)


# ------------------------------------------------------------------
# Seção: KPIs
# ------------------------------------------------------------------

def _render_kpis(df: pd.DataFrame):
    total_fat = df["total"].sum()
    total_ped = len(df)
    ticket_medio = df["total"].mean() if total_ped else 0

    c1, c2, c3 = st.columns(3)
    _kpi(c1, "Faturamento Total", _fmt_brl(total_fat))
    _kpi(c2, "Qtd. de Pedidos", f"{total_ped:,}")
    _kpi(c3, "Ticket Médio", _fmt_brl(ticket_medio))


# ------------------------------------------------------------------
# Seção: Comparação entre períodos
# ------------------------------------------------------------------

def _render_comparacao(df: pd.DataFrame):
    st.subheader("Comparação entre Períodos")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Período A**")
        ini_a = st.date_input("Início A", value=df["data"].max() - pd.DateOffset(months=1), key="ini_a")
        fim_a = st.date_input("Fim A", value=df["data"].max(), key="fim_a")
    with col_b:
        st.markdown("**Período B**")
        ini_b = st.date_input("Início B", value=df["data"].max() - pd.DateOffset(months=2), key="ini_b")
        fim_b = st.date_input("Fim B", value=df["data"].max() - pd.DateOffset(months=1) - pd.Timedelta(days=1), key="fim_b")

    ini_a = pd.Timestamp(ini_a)
    fim_a = pd.Timestamp(fim_a)
    ini_b = pd.Timestamp(ini_b)
    fim_b = pd.Timestamp(fim_b)

    df_a = df[(df["data"] >= ini_a) & (df["data"] <= fim_a)]
    df_b = df[(df["data"] >= ini_b) & (df["data"] <= fim_b)]

    # Agregar por dia
    fat_a = df_a.groupby(df_a["data"].dt.date)["total"].sum().reset_index()
    fat_b = df_b.groupby(df_b["data"].dt.date)["total"].sum().reset_index()
    fat_a.columns = ["data", "faturamento"]
    fat_b.columns = ["data", "faturamento"]

    ped_a = df_a[df_a["situacao_valor"] == SITUACAO_PAGO].groupby(df_a["data"].dt.date).size().reset_index(name="pedidos")
    ped_b = df_b[df_b["situacao_valor"] == SITUACAO_PAGO].groupby(df_b["data"].dt.date).size().reset_index(name="pedidos")

    label_a = f"Período A ({ini_a.strftime('%d/%m/%y')} – {fim_a.strftime('%d/%m/%y')})"
    label_b = f"Período B ({ini_b.strftime('%d/%m/%y')} – {fim_b.strftime('%d/%m/%y')})"

    # Gráfico 1: Receita diária
    fig_fat = go.Figure()
    fig_fat.add_trace(go.Scatter(
        x=fat_a["data"], y=fat_a["faturamento"],
        name=label_a, mode="lines+markers", line=dict(color="#1f77b4", width=2),
    ))
    fig_fat.add_trace(go.Scatter(
        x=fat_b["data"], y=fat_b["faturamento"],
        name=label_b, mode="lines+markers", line=dict(color="#ff7f0e", width=2, dash="dash"),
    ))
    fig_fat.update_layout(
        title="Receita Diária",
        xaxis_title="Data", yaxis_title="R$",
        legend=dict(orientation="h", y=-0.2),
        height=350,
    )
    st.plotly_chart(fig_fat, use_container_width=True)

    # Gráfico 2: Pedidos pagos por dia
    fig_ped = go.Figure()
    fig_ped.add_trace(go.Bar(
        x=ped_a["data"], y=ped_a["pedidos"],
        name=label_a, marker_color="#1f77b4", opacity=0.8,
    ))
    fig_ped.add_trace(go.Bar(
        x=ped_b["data"], y=ped_b["pedidos"],
        name=label_b, marker_color="#ff7f0e", opacity=0.8,
    ))
    fig_ped.update_layout(
        title="Pedidos Pagos por Dia",
        xaxis_title="Data", yaxis_title="Pedidos",
        barmode="group",
        legend=dict(orientation="h", y=-0.2),
        height=350,
    )
    st.plotly_chart(fig_ped, use_container_width=True)

    # Métricas resumidas da comparação
    c1, c2, c3, c4 = st.columns(4)
    fat_a_total = fat_a["faturamento"].sum()
    fat_b_total = fat_b["faturamento"].sum()
    delta_fat = fat_a_total - fat_b_total
    delta_fat_pct = (delta_fat / fat_b_total * 100) if fat_b_total else 0

    ped_a_total = ped_a["pedidos"].sum() if not ped_a.empty else 0
    ped_b_total = ped_b["pedidos"].sum() if not ped_b.empty else 0
    delta_ped = ped_a_total - ped_b_total
    delta_ped_pct = (delta_ped / ped_b_total * 100) if ped_b_total else 0

    _kpi(c1, f"Faturamento — {label_a}", _fmt_brl(fat_a_total))
    _kpi(c2, f"Faturamento — {label_b}", _fmt_brl(fat_b_total),
         delta=f"{delta_fat_pct:+.1f}% vs B")
    _kpi(c3, f"Pedidos Pagos — {label_a}", f"{ped_a_total:,}")
    _kpi(c4, f"Pedidos Pagos — {label_b}", f"{ped_b_total:,}",
         delta=f"{delta_ped_pct:+.1f}% vs B")


# ------------------------------------------------------------------
# Seção: Faturamento e Ticket por Canal
# ------------------------------------------------------------------

def _render_canais(df: pd.DataFrame):
    st.subheader("Por Canal de Venda")

    canal_agg = (
        df.groupby("canal")
        .agg(faturamento=("total", "sum"), pedidos=("id", "count"), ticket_medio=("total", "mean"))
        .reset_index()
        .sort_values("faturamento", ascending=False)
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            canal_agg, x="faturamento", y="canal",
            orientation="h", title="Faturamento por Canal",
            labels={"faturamento": "R$", "canal": ""},
            color="canal", color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_layout(showlegend=False, height=350)
        fig.update_traces(
            text=canal_agg["faturamento"].apply(lambda v: _fmt_brl(v)),
            textposition="outside",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = px.bar(
            canal_agg, x="ticket_medio", y="canal",
            orientation="h", title="Ticket Médio por Canal",
            labels={"ticket_medio": "R$", "canal": ""},
            color="canal", color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig2.update_layout(showlegend=False, height=350)
        fig2.update_traces(
            text=canal_agg["ticket_medio"].apply(lambda v: _fmt_brl(v)),
            textposition="outside",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Qtd de pedidos por canal
    fig3 = px.bar(
        canal_agg, x="canal", y="pedidos",
        title="Quantidade de Pedidos por Canal",
        labels={"pedidos": "Pedidos", "canal": ""},
        color="canal", color_discrete_sequence=px.colors.qualitative.Set2,
        text="pedidos",
    )
    fig3.update_layout(showlegend=False, height=350)
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)


# ------------------------------------------------------------------
# Seção: Produtos mais vendidos
# ------------------------------------------------------------------

def _render_produtos(df_pedidos: pd.DataFrame, df_itens: pd.DataFrame, top_n: int = 15):
    st.subheader("Produtos Mais Vendidos")

    # Unir itens com canal do pedido
    canais_pedido = df_pedidos[["id", "canal"]].rename(columns={"id": "pedido_id"})
    itens = df_itens.merge(canais_pedido, on="pedido_id", how="inner")

    tab_total, tab_canal = st.tabs(["Total", "Por Canal"])

    with tab_total:
        top = (
            itens.groupby("descricao")
            .agg(quantidade=("quantidade", "sum"), faturamento=("valor_total", "sum"))
            .reset_index()
            .sort_values("faturamento", ascending=False)
            .head(top_n)
        )
        fig = px.bar(
            top, x="faturamento", y="descricao",
            orientation="h",
            labels={"faturamento": "Faturamento (R$)", "descricao": ""},
            color_discrete_sequence=["#2196F3"],
            text=top["faturamento"].apply(lambda v: _fmt_brl(v)),
        )
        fig.update_layout(height=500, yaxis=dict(autorange="reversed"))
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with tab_canal:
        canal_sel = st.selectbox(
            "Selecione o canal",
            options=sorted(itens["canal"].unique()),
            key="canal_produtos",
        )
        top_canal = (
            itens[itens["canal"] == canal_sel]
            .groupby("descricao")
            .agg(quantidade=("quantidade", "sum"), faturamento=("valor_total", "sum"))
            .reset_index()
            .sort_values("faturamento", ascending=False)
            .head(top_n)
        )
        fig2 = px.bar(
            top_canal, x="faturamento", y="descricao",
            orientation="h",
            labels={"faturamento": "Faturamento (R$)", "descricao": ""},
            color_discrete_sequence=["#4CAF50"],
            text=top_canal["faturamento"].apply(lambda v: _fmt_brl(v)),
        )
        fig2.update_layout(height=500, yaxis=dict(autorange="reversed"))
        fig2.update_traces(textposition="outside")
        st.plotly_chart(fig2, use_container_width=True)


# ------------------------------------------------------------------
# Entrada principal da aba
# ------------------------------------------------------------------

def render_receita(df_pedidos: pd.DataFrame, df_itens: pd.DataFrame):
    st.header("Receita")

    _render_kpis(df_pedidos)
    st.divider()
    _render_comparacao(df_pedidos)
    st.divider()
    _render_canais(df_pedidos)
    st.divider()
    _render_produtos(df_pedidos, df_itens)
