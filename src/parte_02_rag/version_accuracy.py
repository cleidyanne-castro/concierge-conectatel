"""Métrica de acerto de versão do Stretch do hackathon.

O módulo é independente do runtime da Lambda. Ele recebe uma função de
recuperação e verifica se a versão vigente esperada apareceu no top-k. Um
chunk revogado da mesma família no resultado é contado como vazamento de
versão, mesmo que o chunk vigente também apareça.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
QUESTIONS_PATH = PROJECT_ROOT / "data" / "evaluation" / "embedding_questions.json"
EMBEDDINGS_PATH = PROJECT_ROOT / "artifacts" / "embeddings" / "embeddings.json"
CHUNKS_PATH = PROJECT_ROOT / "artifacts" / "chunks" / "chunks.json"
OUTPUT_PATH = PROJECT_ROOT / "artifacts" / "retrieval" / "version_accuracy_report.json"


def _expected_current_items(
    case: Mapping[str, Any],
    metadata_by_id: Mapping[str, Mapping[str, Any]],
) -> list[Mapping[str, Any]]:
    """Resolve os chunks esperados e garante que são versões vigentes."""
    expected_ids = set(case.get("expected_chunk_ids", []))
    expected = [metadata_by_id[item_id] for item_id in expected_ids if item_id in metadata_by_id]
    return [item for item in expected if item.get("status") == "vigente"]


def assess_version_result(
    case: Mapping[str, Any],
    results: Sequence[Mapping[str, Any]],
    metadata_by_id: Mapping[str, Mapping[str, Any]],
    *,
    top_k: int = 5,
) -> dict[str, Any]:
    """Avalia uma pergunta sem depender de modelo ou de infraestrutura.

    O acerto exige a presença do chunk vigente esperado no top-k e a ausência
    de qualquer chunk revogado da mesma família entre os retornados.
    """
    ranked = list(results[:top_k])
    expected_items = _expected_current_items(case, metadata_by_id)
    expected_ids = {item["chunk_id"] for item in expected_items}
    expected_families = {item.get("doc_family_id") for item in expected_items}

    returned_ids = [item.get("chunk_id") for item in ranked]
    current_hit = bool(expected_ids.intersection(returned_ids))
    revoked_same_family = [
        item.get("chunk_id")
        for item in ranked
        if item.get("status") == "revogado"
        and item.get("doc_family_id") in expected_families
    ]

    return {
        "question_id": case.get("question_id"),
        "question": case.get("question"),
        "expected_chunk_ids": sorted(expected_ids),
        "expected_doc_family_id": case.get("expected_doc_family_id"),
        "top_k": top_k,
        "returned_chunk_ids": returned_ids,
        "current_chunk_hit": current_hit,
        "revoked_same_family_error": bool(revoked_same_family),
        "revoked_same_family_chunk_ids": revoked_same_family,
        "version_accurate": current_hit and not revoked_same_family,
    }


def evaluate_version_accuracy(
    cases: Iterable[Mapping[str, Any]],
    retrieve_fn: Callable[[str, int], Sequence[Mapping[str, Any]]],
    metadata_by_id: Mapping[str, Mapping[str, Any]],
    *,
    top_k: int = 5,
) -> dict[str, Any]:
    """Calcula a métrica para o conjunto de perguntas de avaliação."""
    details = []
    for case in cases:
        details.append(
            assess_version_result(
                case,
                retrieve_fn(str(case["question"]), top_k),
                metadata_by_id,
                top_k=top_k,
            )
        )

    total = len(details)
    accurate = sum(item["version_accurate"] for item in details)
    current_hits = sum(item["current_chunk_hit"] for item in details)
    revoked_errors = sum(item["revoked_same_family_error"] for item in details)

    return {
        "metric": "version_accuracy",
        "definition": "proporção de perguntas em que o chunk vigente esperado aparece no top-k sem chunk revogado da mesma família",
        "top_k": top_k,
        "total_questions": total,
        "version_accurate_questions": accurate,
        "current_chunk_hits": current_hits,
        "revoked_same_family_errors": revoked_errors,
        "version_accuracy": round(accurate / total, 4) if total else None,
        "current_chunk_hit_rate": round(current_hits / total, 4) if total else None,
        "revoked_same_family_error_rate": round(revoked_errors / total, 4) if total else None,
        "questions": details,
    }


def load_metadata() -> dict[str, dict[str, Any]]:
    """Carrega metadados do índice de embeddings por ``chunk_id``."""
    data = json.loads(EMBEDDINGS_PATH.read_text(encoding="utf-8"))
    return {item["chunk_id"]: item for item in data["embeddings"]}


def run_production_evaluation() -> dict[str, Any]:
    """Executa a métrica usando o mesmo filtro de vigência da tool de busca."""
    from src.tools.retrieve_kb.retrieval import load_kb, retrieve

    cases = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    embeddings_data, chunks_by_id = load_kb(EMBEDDINGS_PATH, CHUNKS_PATH)

    def retrieve_for_metric(question: str, top_k: int) -> Sequence[Mapping[str, Any]]:
        result = retrieve(question, embeddings_data, chunks_by_id, threshold=0.0, top_k=top_k)
        return result["results"]

    report = evaluate_version_accuracy(cases, retrieve_for_metric, load_metadata(), top_k=5)
    report.update(
        {
            "model": "intfloat/multilingual-e5-small",
            "questions_source": str(QUESTIONS_PATH.relative_to(PROJECT_ROOT)),
            "retrieval_rule": "status = vigente antes da similaridade",
        }
    )
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    result = run_production_evaluation()
    print(f"Version accuracy@{result['top_k']}: {result['version_accuracy']:.4f}")
    print(f"Relatório salvo em: {OUTPUT_PATH.relative_to(PROJECT_ROOT)}")
