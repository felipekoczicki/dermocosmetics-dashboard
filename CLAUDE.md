# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Streamlit-based analytics dashboard for dermocosmetics (skincare/cosmetics) market data. Visualizes synthetic 2025 market data with year-over-year comparisons across brands, product categories, and sales channels. All UI text and data labels are in Portuguese (Brazilian).

## Commands

```bash
# Install dependencies
python -m pip install -r requirements.txt

# Run the dashboard (from dermocosmetics-dashboard/)
streamlit run app.py
```

## Architecture

```
dermocosmetics-dashboard/
├── app.py                     # Entry point: layout, sidebar filters, data flow orchestration
├── data/
│   └── dados_2025.py          # Synthetic data generator with seasonality simulation
└── components/
    ├── kpi_cards.py            # 4 KPI cards with YoY growth deltas
    ├── share_chart.py          # Donut chart + table for market share by brand
    ├── ranking_chart.py        # Horizontal bar chart ranking brands by selectable metric
    └── evolucao_chart.py       # Multi-line chart for monthly revenue evolution
```

**Data flow:** `app.py` calls `gerar_dados()` (cached via `@st.cache_data`) to produce 2025 and 2024 DataFrames → `aplicar_filtros()` filters by sidebar selections → filtered DataFrames pass into each `render_*()` component function → components run `groupby()` aggregations and render Plotly figures.

**Data model:** Each row has `marca`, `mês`, `categoria`, `canal`, `faturamento`, `pedidos`, `ticket_medio`. Seasonality and ±15% random variance are seeded for reproducibility. 2024 data is a scaled baseline for YoY comparisons.

**Filter behavior:** All sidebar filters (month, category, channel, brand) default to all options selected. Changing filters triggers full re-render of all components.

## Key Details

- Currency formatting uses Brazilian locale: `R$ 1.234,56`
- The donut chart `hole` parameter creates the visual donut effect
- `ranking_chart.py` switches between `sum()` and `mean()` aggregation depending on the selected metric (revenue/orders use sum; average ticket uses mean)
- Data is entirely synthetic — no external data sources or database connections
