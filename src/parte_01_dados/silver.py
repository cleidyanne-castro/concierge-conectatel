"""Regras Pandas reutilizáveis da camada Silver."""

from __future__ import annotations

import re
import unicodedata

import pandas as pd


EXPECTED_COLUMNS = [
    "chamado_id",
    "data_abertura",
    "canal",
    "categoria",
    "subcategoria",
    "estado",
    "cidade",
    "duracao_minutos",
    "resolvido_primeiro_contato",
    "encaminhado_humano",
    "satisfacao_1_a_5",
    "plano_atual",
    "resumo_atendimento",
]

CATEGORY_COLUMNS = [
    "canal",
    "categoria",
    "subcategoria",
    "estado",
    "cidade",
    "plano_atual",
]
BOOLEAN_COLUMNS = ["resolvido_primeiro_contato", "encaminhado_humano"]
NUMERIC_COLUMNS = ["duracao_minutos", "satisfacao_1_a_5"]


def normalize_text(value: object) -> object:
    """Padroniza texto sem alterar valores ausentes."""
    if pd.isna(value):
        return pd.NA
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"\s+", " ", text).strip().lower()
    return text or pd.NA


def validate_columns(df: pd.DataFrame) -> None:
    """Garante que o contrato mínimo da Silver foi preservado."""
    missing = sorted(set(EXPECTED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")


def _to_boolean(series: pd.Series) -> pd.Series:
    mapping = {
        "true": True,
        "false": False,
        "sim": True,
        "nao": False,
        "não": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False,
    }
    normalized = series.astype("string").str.strip().str.lower().map(mapping)
    return normalized.fillna(False).astype(bool)


def clean_calls(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica as transformações oficiais da camada Silver."""
    validate_columns(df)
    cleaned = df.loc[:, EXPECTED_COLUMNS].copy()
    cleaned = cleaned.drop_duplicates(keep="first").reset_index(drop=True)

    for column in CATEGORY_COLUMNS:
        cleaned[column] = cleaned[column].map(normalize_text).fillna("unknown")

    cleaned["data_abertura"] = pd.to_datetime(
        cleaned["data_abertura"], errors="coerce"
    )
    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    for column in BOOLEAN_COLUMNS:
        cleaned[column] = _to_boolean(cleaned[column])

    cleaned["chamado_id"] = cleaned["chamado_id"].astype("string").fillna("unknown")
    cleaned["resumo_atendimento"] = (
        cleaned["resumo_atendimento"].astype("string").fillna("unknown").str.strip()
    )
    return cleaned
