import json

import faiss
import numpy as np

from src.parte_02_rag.vector_store import (
    INDEX_PATH,
    METADATA_PATH,
    load_vector_store,
)


def test_faiss_index_exists():
    """Verifica se o índice FAISS existe."""

    assert INDEX_PATH.exists()


def test_metadata_exists():
    """Verifica se os metadados existem."""

    assert METADATA_PATH.exists()


def test_faiss_index_structure():
    """Verifica a estrutura básica do índice."""

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    assert index.ntotal == 59
    assert index.d == 384


def test_metadata_matches_index():
    """Verifica se cada vetor possui metadata correspondente."""

    index, metadata = load_vector_store()

    assert len(metadata["items"]) == index.ntotal

    for position, item in enumerate(
        metadata["items"]
    ):
        assert item["faiss_index"] == position
        assert item["chunk_id"]
        assert item["doc_family_id"]
        assert item["source_path"]
        assert item["status"] in {
            "vigente",
            "revogado",
        }


def test_search_returns_results():
    """
    Verifica se o FAISS consegue executar
    uma consulta vetorial.
    """

    index, metadata = load_vector_store()

    query_vector = np.zeros(
        384,
        dtype=np.float32,
    )

    results = index.search(
        query_vector.reshape(1, -1),
        5,
    )

    scores, indices = results

    assert scores.shape == (1, 5)
    assert indices.shape == (1, 5)

    for faiss_index in indices[0]:
        assert 0 <= faiss_index < index.ntotal