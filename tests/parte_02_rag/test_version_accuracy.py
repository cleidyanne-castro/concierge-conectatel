from src.parte_02_rag.version_accuracy import (
    assess_version_result,
    evaluate_version_accuracy,
)


METADATA = {
    "current": {
        "chunk_id": "current",
        "doc_family_id": "policy",
        "status": "vigente",
    },
    "revoked": {
        "chunk_id": "revoked",
        "doc_family_id": "policy",
        "status": "revogado",
    },
    "other": {
        "chunk_id": "other",
        "doc_family_id": "other-family",
        "status": "vigente",
    },
}

CASE = {
    "question_id": "q-version",
    "question": "Qual versão está vigente?",
    "expected_doc_family_id": "policy",
    "expected_chunk_ids": ["current"],
}


def test_current_version_in_top_k_is_accurate():
    result = assess_version_result(
        CASE,
        [METADATA["other"], METADATA["current"]],
        METADATA,
        top_k=5,
    )

    assert result["current_chunk_hit"] is True
    assert result["revoked_same_family_error"] is False
    assert result["version_accurate"] is True


def test_revoked_same_family_is_an_error_even_when_current_also_appears():
    result = assess_version_result(
        CASE,
        [METADATA["revoked"], METADATA["current"]],
        METADATA,
        top_k=5,
    )

    assert result["current_chunk_hit"] is True
    assert result["revoked_same_family_error"] is True
    assert result["version_accurate"] is False


def test_evaluation_returns_rates_and_details():
    cases = [CASE, {**CASE, "question_id": "q-miss", "question": "outra"}]

    def retrieve_fn(question, top_k):
        return [METADATA["current"]] if question == CASE["question"] else [METADATA["other"]]

    report = evaluate_version_accuracy(cases, retrieve_fn, METADATA, top_k=5)

    assert report["total_questions"] == 2
    assert report["version_accurate_questions"] == 1
    assert report["version_accuracy"] == 0.5
    assert len(report["questions"]) == 2
