import streamlit as st
import plotly.express as px


def render_evolucao_chart(df):
    st.subheader("Evolução Mensal de Faturamento")

    ordem_meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                   "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

    evolucao = df.groupby(["mes", "mes_nome", "marca"])["faturamento"].sum().reset_index()
    evolucao["mes_nome"] = pd.Categorical(evolucao["mes_nome"], categories=ordem_meses, ordered=True)
    evolucao = evolucao.sort_values("mes")

    fig = px.line(
        evolucao,
        x="mes_nome",
        y="faturamento",
        color="marca",
        markers=True,
        color_discrete_sequence=px.colors.qualitative.Set2,
        labels={"mes_nome": "Mês", "faturamento": "Faturamento (R$)", "marca": "Marca"},
    )
    fig.update_layout(
        hovermode="x unified",
        height=420,
        margin=dict(t=30, b=30),
        yaxis_tickformat=",.0f",
    )
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b>: R$ %{y:,.0f}<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)


import pandas as pd
