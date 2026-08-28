import json
from pathlib import Path


ROOT = Path(__file__).parents[2]
NOTEBOOK_PATH = ROOT / "src" / "parte_01_dados" / "01_bronze_ingestao.ipynb"


def notebook_text():
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
    )


def test_bronze_notebook_exists_and_is_valid_json():
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    assert notebook["nbformat"] >= 4
    assert notebook["cells"]


def test_bronze_declares_expected_input_contract():
    source = notebook_text()
    expected = [
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
    assert all(column in source for column in expected)


def test_bronze_declares_required_paths_and_utilities():
    source = notebook_text()
    expected_markers = [
        "RAW_ROOT",
        "CALLS_PATH",
        "BRONZE_ROOT",
        "bronze_calls_snapshot.csv",
        "bronze_file_inventory.json",
        "bronze_quality_report.json",
        "bronze_schema.json",
        "bronze_corpus_metadata.json",
        "def sha256_file",
        "def write_json",
        "def inventory",
    ]
    assert all(marker in source for marker in expected_markers)


def test_bronze_keeps_deduplication_out_of_ingestion_contract():
    source = notebook_text()
    assert "drop_duplicates" not in source
