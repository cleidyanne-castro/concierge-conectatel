import pandas as pd
import pytest

from src.parte_01_dados.gold import build_kpis, save_gold_outputs, validate_silver


@pytest.fixture
def silver_calls():
    return pd.DataFrame(
        [
            {"chamado_id": "1", "canal": "chat", "categoria": "conexao", "subcategoria": "wifi", "estado": "ce", "cidade": "fortaleza", "duracao_minutos": 10, "resolvido_primeiro_contato": True, "encaminhado_humano": False, "satisfacao_1_a_5": 5, "plano_atual": "fibra", "data_abertura": "2026-01-01", "resumo_atendimento": "sem sinal"},
            {"chamado_id": "2", "canal": "telefone", "categoria": "fatura", "subcategoria": "segunda via", "estado": "ce", "cidade": "sobral", "duracao_minutos": 20, "resolvido_primeiro_contato": False, "encaminhado_humano": True, "satisfacao_1_a_5": 3, "plano_atual": "fibra", "data_abertura": "2026-01-02", "resumo_atendimento": "boleto"},
        ]
    )


def test_kpis_have_denominators(silver_calls):
    kpis = build_kpis(silver_calls)
    assert kpis["denominador"].gt(0).all()
    assert set(kpis["kpi"]) >= {"total_chamados", "taxa_primeiro_contato"}


def test_gold_persists_outputs(tmp_path, silver_calls):
    manifest = save_gold_outputs(silver_calls, tmp_path)
    assert manifest["input_rows"] == 2
    assert (tmp_path / "gold_decisoes_design.md").exists()
    assert (tmp_path / "gold_categoria_resumo.csv").exists()
    assert (tmp_path / "gold_quality_report.json").exists()
    assert (tmp_path / "gold_manifest.json").exists()


def test_gold_grouped_metrics_publish_denominators(tmp_path, silver_calls):
    manifest = save_gold_outputs(silver_calls, tmp_path)
    assert manifest["analysis_count"] == 3
    category = pd.read_csv(tmp_path / "gold_categoria_resumo.csv")
    assert {"satisfacao_n", "primeiro_contato_n", "duracao_n"}.issubset(category.columns)


def test_gold_rejects_empty_input(silver_calls):
    with pytest.raises(ValueError, match="não possui linhas"):
        validate_silver(silver_calls.iloc[0:0])
