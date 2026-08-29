from sentence_transformers import SentenceTransformer

from src.parte_02_rag.vector_store import (
    build_faiss_index,
    build_metadata,
    load_embeddings,
    search,
)


MODEL_NAME = "intfloat/multilingual-e5-small"


def create_test_vector_store():
    """
    Cria o índice FAISS em memória a partir dos embeddings.
    """

    embeddings_data = load_embeddings()

    index = build_faiss_index(
        embeddings_data
    )

    metadata = build_metadata(
        embeddings_data
    )

    return index, metadata


def test_real_query_retrieval():

    model = SentenceTransformer(
        MODEL_NAME
    )

    index, metadata = create_test_vector_store()

    query = (
        "Como consultar meu consumo de dados?"
    )

    query_embedding = model.encode(
        f"query: {query}",
        normalize_embeddings=True,
    )

    results = search(
        index,
        metadata,
        query_embedding,
        top_k=5,
    )

    assert len(results) == 5

    print()
    print("=" * 70)
    print("RESULTADOS DA CONSULTA")
    print("=" * 70)

    for result in results:
        print(
            f"\nScore: {result['score']:.4f}"
        )
        print(
            f"Chunk: {result['chunk_id']}"
        )
        print(
            f"Documento: "
            f"{result['doc_family_id']}"
        )
        print(
            f"Seção: "
            f"{result['section_title']}"
        )
        print(
            f"Status: "
            f"{result['status']}"
        )
        print(
            f"Fonte: "
            f"{result['source_path']}"
        )

    assert any(
        result["doc_family_id"] == "faq-geral"
        for result in results
    )