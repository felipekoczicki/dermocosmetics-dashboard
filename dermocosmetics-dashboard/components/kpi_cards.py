import streamlit as st


def render_kpi_cards(df, df_2024):
    fat_2025 = df["faturamento"].sum()
    fat_2024 = df_2024["faturamento"].sum()
    pedidos_2025 = df["pedidos"].sum()
    pedidos_2024 = df_2024["pedidos"].sum()
    ticket_medio = df["faturamento"].sum() / df["pedidos"].sum()
    crescimento_fat = ((fat_2025 - fat_2024) / fat_2024) * 100
    crescimento_ped = ((pedidos_2025 - pedidos_2024) / pedidos_2024) * 100

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Faturamento Total 2025",
            value=f"R$ {fat_2025/1_000_000:.1f}M",
            delta=f"{crescimento_fat:+.1f}% vs 2024"
        )

    with col2:
        st.metric(
            label="Total de Pedidos",
            value=f"{pedidos_2025:,.0f}".replace(",", "."),
            delta=f"{crescimento_ped:+.1f}% vs 2024"
        )

    with col3:
        st.metric(
            label="Ticket Médio",
            value=f"R$ {ticket_medio:.2f}"
        )

    with col4:
        marcas_ativas = df["marca"].nunique()
        st.metric(
            label="Marcas Analisadas",
            value=str(marcas_ativas)
        )
