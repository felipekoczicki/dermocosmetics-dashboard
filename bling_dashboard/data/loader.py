# =============================================================
# data/loader.py — Carregamento e preparação dos dados
# =============================================================

from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PARQUET_DIR, CANAL_MAP, CANAL_DIRETO, SITUACOES_EXCLUIDAS


@st.cache_data(ttl=3600, show_spinner="Carregando dados...")
def carregar_pedidos() -> pd.DataFrame:
    path = Path(PARQUET_DIR) / "pedidos.parquet"
    df = pd.read_parquet(path)
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["canal"] = df["intermediador_cnpj"].map(CANAL_MAP).fillna(CANAL_DIRETO)
    df = df[~df["situacao_valor"].isin(SITUACOES_EXCLUIDAS)]
    df = df.dropna(subset=["data"])
    return df


@st.cache_data(ttl=3600, show_spinner="Carregando itens...")
def carregar_itens() -> pd.DataFrame:
    path = Path(PARQUET_DIR) / "itens.parquet"
    df = pd.read_parquet(path)
    df["pedido_data"] = pd.to_datetime(df["pedido_data"], errors="coerce")
    return df


def filtrar_periodo(df: pd.DataFrame, inicio: pd.Timestamp, fim: pd.Timestamp) -> pd.DataFrame:
    return df[(df["data"] >= inicio) & (df["data"] <= fim)]


def filtrar_periodo_itens(
    df_itens: pd.DataFrame,
    df_pedidos_filtrado: pd.DataFrame,
) -> pd.DataFrame:
    ids_validos = set(df_pedidos_filtrado["id"])
    return df_itens[df_itens["pedido_id"].isin(ids_validos)]
