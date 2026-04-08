# =============================================================
# data/loader.py — Carregamento e preparação dos dados
# =============================================================

from __future__ import annotations
from pathlib import Path
import pandas as pd
import streamlit as st

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PARQUET_DIR, CANAIS_CSV, SITUACOES_EXCLUIDAS


def _carregar_mapa_canais() -> dict[int, str]:
    df = pd.read_csv(CANAIS_CSV, sep=";", dtype={"loja_id": "Int64", "canal_nome": str}, encoding="utf-8-sig")
    return dict(zip(df["loja_id"], df["canal_nome"].fillna("Sem Nome")))


@st.cache_data(ttl=3600, show_spinner="Carregando dados...")
def carregar_pedidos() -> pd.DataFrame:
    path = Path(PARQUET_DIR) / "pedidos.parquet"
    df = pd.read_parquet(path)
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    mapa_canais = _carregar_mapa_canais()
    df["loja_id"] = pd.to_numeric(df["loja_id"], errors="coerce").astype("Int64")
    df["canal"] = df["loja_id"].map(mapa_canais).fillna("Sem Nome")
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
