"""Regras Pandas reutilizáveis da camada Silver."""

from __future__ import annotations

import re
import unicodedata
from typing import Any

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
    normalized = normalized.astype("boolean")
    return normalized.fillna(False).astype(bool)


def build_processing_metrics(
    *,
    input_rows: int,
    output_rows: int,
    started_at: Any,
    finished_at: Any,
) -> dict[str, Any]:
    """Registra volume e duração da execução da Silver."""
    duration_seconds = (finished_at - started_at).total_seconds()
    return {
        "input_rows": int(input_rows),
        "output_rows": int(output_rows),
        "rows_removed": int(input_rows - output_rows),
        "duration_seconds": float(duration_seconds),
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat(),
    }


def clean_calls(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica as transformações oficiais da camada Silver."""
    validate_columns(df)
    cleaned = df.loc[:, EXPECTED_COLUMNS].copy()
    cleaned = cleaned.drop_duplicates(keep="first").reset_index(drop=True)

    for column in CATEGORY_COLUMNS:
        cleaned[column] = cleaned[column].map(normalize_text).fillna("unknown")

    cleaned["data_abertura"] = pd.to_datetime(
        cleaned["data_abertura"], errors="coerce", format="mixed"
    )
    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
    cleaned["duracao_minutos"] = cleaned["duracao_minutos"].where(
        cleaned["duracao_minutos"].ge(0)
    )
    cleaned["satisfacao_1_a_5"] = cleaned["satisfacao_1_a_5"].clip(1, 5)
    for column in BOOLEAN_COLUMNS:
        cleaned[column] = _to_boolean(cleaned[column])

    cleaned["chamado_id"] = cleaned["chamado_id"].astype("string").fillna("unknown")
    cleaned["resumo_atendimento"] = (
        cleaned["resumo_atendimento"].astype("string").fillna("unknown").str.strip()
    )
    return cleaned
