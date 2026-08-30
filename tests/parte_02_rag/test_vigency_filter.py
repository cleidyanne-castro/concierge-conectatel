from pathlib import Path

import numpy as np
import pytest

from src.tools.retrieve_kb import retrieval
from src.tools.retrieve_kb.retrieval import load_kb, retrieve

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EMBEDDINGS_PATH = PROJECT_ROOT / "artifacts" / "embeddings" / "embeddings.json"
CHUNKS_PATH = PROJECT_ROOT / "artifacts" / "chunks" / "chunks.json"

CALIBRATED_THRESHOLD = 0.85

def _make_item(chunk_id, status, embedding, doc_family_id="pol-teste"):
    return {
        "chunk_id": chunk_id,
        "status": status,
        "embedding": embedding,
        "doc_family_id": doc_family_id,
        "source_path": f"data/corpus/{doc_family_id}.md",
        "section_title": "Seção de teste",
    }

def test_structural_filter_excludes_revoked_even_with_higher_similarity(monkeypatch):
    """Garante que o filtro de vigência exclui documentos revogados antes do cálculo de similaridade."""
    embeddings_data = {
        "embeddings": [
            _make_item("chunk_v1_revogado", "revogado", [1.0, 0.0, 0.0]),
            _make_item("chunk_v2_vigente", "vigente", [0.1, 0.0, 0.0]),
        ]
    }
    chunks_by_id = {
        "chunk_v1_revogado": {"text": "texto da versão revogada"},
        "chunk_v2_vigente": {"text": "texto da versão vigente"},
    }

    monkeypatch.setattr(retrieval, "embed_query", lambda question: np.array([1.0, 0.0, 0.0]))

    result = retrieve(
        "pergunta qualquer",
        embeddings_data,
        chunks_by_id,
        threshold=0.05,
        top_k=5,
    )

    returned_ids = {item["chunk_id"] for item in result["results"]}
    assert "chunk_v1_revogado" not in returned_ids
    assert returned_ids == {"chunk_v2_vigente"}
    assert all(item["status"] == "vigente" for item in result["results"])

def test_returns_dont_know_without_valid_document_no_model_call(monkeypatch):
    """Retorna 'nao_sei' imediatamente se houver apenas documentos revogados, sem chamar o modelo."""
    embeddings_data = {
        "embeddings": [
            _make_item("chunk_v1_revogado", "revogado", [1.0, 0.0, 0.0]),
        ]
    }
    chunks_by_id = {"chunk_v1_revogado": {"text": "texto da versão revogada"}}

    def _fail_if_called(question):
        raise AssertionError("embed_query não deveria ser chamado sem vigentes no índice")

    monkeypatch.setattr(retrieval, "embed_query", _fail_if_called)

    result = retrieve("qualquer pergunta", embeddings_data, chunks_by_id, threshold=0.85)

    assert result["decision"] == "nao_sei"
    assert result["results"] == []
    assert result["reason"] == "sem_documentos_vigentes"

@pytest.fixture(scope="module")
def real_kb():
    if not EMBEDDINGS_PATH.exists():
        pytest.skip(
            f"{EMBEDDINGS_PATH} não encontrado — rode a indexação antes de rodar os testes de integração."
        )
    return load_kb(EMBEDDINGS_PATH, CHUNKS_PATH)

@pytest.fixture(scope="module")
def revoked_chunk_ids(real_kb):
    """Retorna um set com os IDs dos chunks revogados obtidos do índice real."""
    embeddings_data, _ = real_kb
    return {
        item["chunk_id"]
        for item in embeddings_data["embeddings"]
        if item["status"] == "revogado"
    }

def test_policy_version_question_never_returns_revoked(real_kb, revoked_chunk_ids):
    """Verifica se uma pergunta direta sobre a versão da política não retorna chunks revogados."""
    embeddings_data, chunks_by_id = real_kb

    result = retrieve(
        "Qual versão da política de reembolso deve ser usada atualmente?",
        embeddings_data,
        chunks_by_id,
        threshold=CALIBRATED_THRESHOLD,
        top_k=5,
    )

    returned_ids = {item["chunk_id"] for item in result["results"]}
    assert returned_ids.isdisjoint(revoked_chunk_ids), (
        "Um chunk da versão revogada da política de reembolso vazou na resposta"
    )
    assert result["decision"] == "responder"
    assert result["results"][0]["status"] == "vigente"
    assert result["results"][0]["doc_family_id"] == "pol-reembolso"
    assert result["results"][0]["score"] >= CALIBRATED_THRESHOLD

def test_generic_refund_question_does_not_retrieve_revoked_version(real_kb, revoked_chunk_ids):
    """Garante que perguntas genéricas sobre tópicos em comum não retornem versões revogadas."""
    embeddings_data, chunks_by_id = real_kb

    result = retrieve(
        "Qual é o prazo atual para contestar uma cobrança da fatura?",
        embeddings_data,
        chunks_by_id,
        threshold=CALIBRATED_THRESHOLD,
        top_k=5,
    )

    returned_ids = {item["chunk_id"] for item in result["results"]}
    assert returned_ids.isdisjoint(revoked_chunk_ids)
    assert result["decision"] == "responder"
    assert result["results"][0]["doc_family_id"] == "pol-reembolso"
    assert result["results"][0]["status"] == "vigente"

@pytest.mark.parametrize(
    "question",
    [
        "Em quais casos uma contestação de fatura precisa passar por verificação antifraude?",
        "Como funciona o reembolso quando a contestação é aceita?",
    ],
)
def test_answerable_questions_cite_valid_source_above_threshold(real_kb, question):
    """Valida se perguntas respondíveis encontram documentos vigentes com score acima do limiar."""
    embeddings_data, chunks_by_id = real_kb

    result = retrieve(
        question,
        embeddings_data,
        chunks_by_id,
        threshold=CALIBRATED_THRESHOLD,
        top_k=3,
    )

    assert result["decision"] == "responder"
    top = result["results"][0]
    assert top["status"] == "vigente"
    assert top["score"] >= CALIBRATED_THRESHOLD
    assert top["text"], "resultado sem texto do chunk — o agente não teria o que citar"