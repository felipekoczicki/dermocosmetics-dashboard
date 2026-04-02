import streamlit as st
import plotly.express as px


def render_share_chart(df):
    st.subheader("Share de Mercado por Marca")

    share = df.groupby("marca")["faturamento"].sum().reset_index()
    share["share_%"] = (share["faturamento"] / share["faturamento"].sum() * 100).round(2)
    share = share.sort_values("share_%", ascending=False)

    fig = px.pie(
        share,
        names="marca",
        values="faturamento",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(
        textposition="outside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Faturamento: R$ %{value:,.0f}<br>Share: %{percent}<extra></extra>"
    )
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", x=1.05),
        margin=dict(t=30, b=30, l=30, r=30),
        height=420,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabela de share
    share_display = share[["marca", "share_%", "faturamento"]].copy()
    share_display.columns = ["Marca", "Share (%)", "Faturamento (R$)"]
    share_display["Faturamento (R$)"] = share_display["Faturamento (R$)"].apply(lambda x: f"R$ {x:,.0f}".replace(",", "."))
    share_display["Share (%)"] = share_display["Share (%)"].apply(lambda x: f"{x:.2f}%")
    st.dataframe(share_display, use_container_width=True, hide_index=True)
