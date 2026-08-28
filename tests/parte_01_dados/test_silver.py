import pandas as pd
import pytest

from datetime import datetime, timezone

from src.parte_01_dados.silver import (
    EXPECTED_COLUMNS,
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
    assert cleaned.columns.tolist() == EXPECTED_COLUMNS
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


def test_validate_columns_rejects_incomplete_input(raw_calls):
    with pytest.raises(ValueError, match="Colunas obrigatórias ausentes"):
        validate_columns(raw_calls.drop(columns="cidade"))


def test_clean_calls_keeps_invalid_dates_as_null(raw_calls):
    raw_calls.loc[0, "data_abertura"] = "data inválida"
    cleaned = clean_calls(raw_calls)
    assert pd.isna(cleaned.loc[0, "data_abertura"])


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
