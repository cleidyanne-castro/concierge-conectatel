import pandas as pd
import pytest

from datetime import datetime, timezone

from src.parte_01_dados.silver import (
    EXPECTED_COLUMNS,
    QUALITY_COLUMNS,
    build_processing_metrics,
    clean_calls,
    validate_columns,
)


@pytest.fixture
def raw_calls():
    return pd.DataFrame(
        [
            {
                "chamado_id": "1",
                "data_abertura": "2026-01-01",
                "canal": " Chat ",
                "categoria": "Conexão",
                "subcategoria": " Wi-Fi ",
                "estado": "CE",
                "cidade": "Fortaleza",
                "duracao_minutos": "12",
                "resolvido_primeiro_contato": "sim",
                "encaminhado_humano": "não",
                "satisfacao_1_a_5": "5",
                "plano_atual": " Fibra ",
                "resumo_atendimento": "Sem sinal",
            },
            {
                "chamado_id": "1",
                "data_abertura": "2026-01-01",
                "canal": " Chat ",
                "categoria": "Conexão",
                "subcategoria": " Wi-Fi ",
                "estado": "CE",
                "cidade": "Fortaleza",
                "duracao_minutos": "12",
                "resolvido_primeiro_contato": "sim",
                "encaminhado_humano": "não",
                "satisfacao_1_a_5": "5",
                "plano_atual": " Fibra ",
                "resumo_atendimento": "Sem sinal",
            },
        ]
    )


def test_clean_calls_preserves_contract(raw_calls):
    cleaned = clean_calls(raw_calls)
    assert cleaned.columns[: len(EXPECTED_COLUMNS)].tolist() == EXPECTED_COLUMNS
    assert set(QUALITY_COLUMNS).issubset(cleaned.columns)
    assert len(cleaned) == 1


def test_clean_calls_normalizes_text_and_types(raw_calls):
    cleaned = clean_calls(raw_calls)
    row = cleaned.iloc[0]
    assert row["categoria"] == "conexao"
    assert row["canal"] == "chat"
    assert pd.api.types.is_datetime64_any_dtype(cleaned["data_abertura"])
    assert cleaned["duracao_minutos"].dtype.kind in "fi"
    assert bool(row["resolvido_primeiro_contato"]) is True
    assert bool(row["encaminhado_humano"]) is False


def test_clean_calls_canonicalizes_state_aliases(raw_calls):
    raw_calls.loc[0, "estado"] = "Ceará"
    raw_calls.loc[1, "estado"] = "ce"
    cleaned = clean_calls(raw_calls)
    assert cleaned["estado"].tolist() == ["ce", "ce"]


def test_clean_calls_preserves_unknown_boolean_as_missing(raw_calls):
    raw_calls.loc[0, "resolvido_primeiro_contato"] = "indisponivel"
    cleaned = clean_calls(raw_calls)
    assert pd.isna(cleaned.loc[0, "resolvido_primeiro_contato"])
    assert bool(cleaned.loc[0, "has_unknown_boolean"]) is True


def test_clean_calls_flags_future_date_and_negative_duration(raw_calls):
    raw_calls.loc[0, "data_abertura"] = "2099-01-01"
    raw_calls.loc[0, "duracao_minutos"] = "-4"
    cleaned = clean_calls(raw_calls)
    assert bool(cleaned.loc[0, "is_valid_date"]) is False
    assert bool(cleaned.loc[0, "is_valid_duration"]) is False


def test_clean_calls_flags_duration_outlier(raw_calls):
    rows = pd.concat([raw_calls.iloc[[0]]] * 5, ignore_index=True)
    rows["chamado_id"] = ["1", "2", "3", "4", "5"]
    rows["duracao_minutos"] = [10, 11, 12, 13, 1000]
    cleaned = clean_calls(rows)
    assert bool(cleaned.loc[4, "is_outlier_duration"]) is True


def test_validate_columns_rejects_incomplete_input(raw_calls):
    with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
        validate_columns(raw_calls.drop(columns="cidade"))


def test_clean_calls_keeps_invalid_dates_as_null(raw_calls):
    raw_calls.loc[0, "data_abertura"] = "data inválida"
    cleaned = clean_calls(raw_calls)
    assert pd.isna(cleaned.loc[0, "data_abertura"])


def test_clean_calls_keeps_out_of_range_satisfaction_as_missing(raw_calls):
    raw_calls.loc[0, "satisfacao_1_a_5"] = "6"

    cleaned = clean_calls(raw_calls)

    assert pd.isna(cleaned.loc[0, "satisfacao_1_a_5"])
    assert bool(cleaned.loc[0, "is_valid_satisfaction"]) is False


def test_build_processing_metrics_reports_volume_and_duration():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2026, 1, 1, 0, 0, 2, tzinfo=timezone.utc)
    metrics = build_processing_metrics(
        input_rows=10,
        output_rows=8,
        started_at=start,
        finished_at=end,
    )
    assert metrics["rows_removed"] == 2
    assert metrics["duration_seconds"] == 2.0
