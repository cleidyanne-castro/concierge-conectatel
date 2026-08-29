import json

import faiss
import numpy as np

from src.parte_02_rag.vector_store import (
    build_faiss_index,
    build_metadata,
    load_embeddings,
    search,
)


def create_test_vector_store():
    """
    Cria o índice FAISS em memória a partir dos embeddings
    versionados no repositório.
    """

    embeddings_data = load_embeddings()

    index = build_faiss_index(
        embeddings_data
    )

    metadata = build_metadata(
        embeddings_data
    )

    return index, metadata


def test_faiss_index_can_be_built():
    """Verifica se o índice FAISS pode ser construído."""

    index, _ = create_test_vector_store()

    assert index.ntotal == 59
    assert index.d == 384


def test_metadata_matches_index():
    """Verifica se cada vetor possui metadata correspondente."""

    index, metadata = create_test_vector_store()

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

    index, metadata = create_test_vector_store()

    query_vector = np.zeros(
        384,
        dtype=np.float32,
    )

    results = search(
        index,
        metadata,
        query_vector,
        top_k=5,
    )

    assert len(results) == 5

    for result in results:
        assert 0 <= result["faiss_index"] < index.ntotal