import streamlit as st
import plotly.express as px


def render_ranking_chart(df):
    st.subheader("Ranking de Marcas")

    metrica = st.radio(
        "Ordenar por:",
        ["Faturamento", "Pedidos", "Ticket Médio"],
        horizontal=True,
        key="ranking_metrica"
    )

    col_map = {
        "Faturamento": "faturamento",
        "Pedidos": "pedidos",
        "Ticket Médio": "ticket_medio"
    }
    col = col_map[metrica]

    if metrica == "Ticket Médio":
        ranking = df.groupby("marca")[col].mean().reset_index()
    else:
        ranking = df.groupby("marca")[col].sum().reset_index()

    ranking = ranking.sort_values(col, ascending=True)

    label_map = {
        "faturamento": "Faturamento (R$)",
        "pedidos": "Pedidos",
        "ticket_medio": "Ticket Médio (R$)"
    }

    fig = px.bar(
        ranking,
        x=col,
        y="marca",
        orientation="h",
        color=col,
        color_continuous_scale="teal",
        labels={col: label_map[col], "marca": "Marca"},
        text=col,
    )

    if metrica in ["Faturamento", "Ticket Médio"]:
        fig.update_traces(texttemplate="R$ %{x:,.0f}", textposition="outside")
    else:
        fig.update_traces(texttemplate="%{x:,.0f}", textposition="outside")

    fig.update_layout(
        coloraxis_showscale=False,
        height=400,
        margin=dict(t=20, b=20, l=10, r=80),
        xaxis_tickformat=",.0f",
    )
    st.plotly_chart(fig, use_container_width=True)
