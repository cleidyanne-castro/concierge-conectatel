import json
from pathlib import Path

import faiss
import numpy as np


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

EMBEDDINGS_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "embeddings"
    / "embeddings.json"
)

FAISS_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "embeddings"
    / "faiss"
)

INDEX_PATH = FAISS_DIR / "index.faiss"
METADATA_PATH = FAISS_DIR / "metadata.json"


# ============================================================
# CARREGAMENTO
# ============================================================

def load_embeddings():
    """Carrega o artefato de embeddings."""

    with open(
        EMBEDDINGS_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if "metadata" not in data:
        raise ValueError(
            "Metadados dos embeddings não encontrados."
        )

    if "embeddings" not in data:
        raise ValueError(
            "Embeddings não encontrados."
        )

    print(
        f"Embeddings carregados: "
        f"{len(data['embeddings'])}"
    )

    return data


# ============================================================
# CONSTRUÇÃO DO ÍNDICE
# ============================================================

def build_faiss_index(embeddings_data):
    """
    Cria um índice FAISS usando os embeddings normalizados.

    Como os embeddings foram normalizados na Fase 6,
    Inner Product equivale à similaridade de cosseno.
    """

    items = embeddings_data["embeddings"]

    if not items:
        raise ValueError(
            "Nenhum embedding disponível para indexação."
        )

    vectors = np.array(
        [
            item["embedding"]
            for item in items
        ],
        dtype=np.float32,
    )

    dimension = vectors.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(vectors)

    print()
    print("Índice FAISS criado.")
    print(f"Dimensão: {dimension}")
    print(f"Vetores adicionados: {index.ntotal}")

    return index


# ============================================================
# METADADOS
# ============================================================

def build_metadata(embeddings_data):
    """
    Cria o mapeamento entre a posição do vetor no FAISS
    e os metadados do chunk correspondente.
    """

    items = embeddings_data["embeddings"]

    metadata_items = []

    for faiss_index, item in enumerate(items):

        metadata_items.append(
            {
                "faiss_index": faiss_index,
                "chunk_id": item["chunk_id"],
                "doc_family_id": item["doc_family_id"],
                "status": item["status"],
                "version_ordinal": item["version_ordinal"],
                "source_path": item["source_path"],
                "section_title": item["section_title"],
                "effective_from": item.get("effective_from"),
                "effective_to": item.get("effective_to"),
            }
        )

    return {
        "metadata": embeddings_data["metadata"],
        "items": metadata_items,
    }


# ============================================================
# PERSISTÊNCIA
# ============================================================

def save_index(index):
    """Salva o índice FAISS em disco."""

    FAISS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    faiss.write_index(
        index,
        str(INDEX_PATH),
    )

    print()
    print("Índice FAISS salvo em:")
    print(INDEX_PATH)


def save_metadata(metadata):
    """Salva o mapeamento dos vetores."""

    FAISS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("Metadados do índice salvos em:")
    print(METADATA_PATH)


# ============================================================
# CARREGAMENTO EM RUNTIME
# ============================================================

def load_vector_store():
    """
    Carrega o índice FAISS e seus metadados.

    Esta função será utilizada posteriormente
    pelo componente de recuperação.
    """

    if not INDEX_PATH.exists():
        raise FileNotFoundError(
            f"Índice FAISS não encontrado: {INDEX_PATH}"
        )

    if not METADATA_PATH.exists():
        raise FileNotFoundError(
            f"Metadados não encontrados: {METADATA_PATH}"
        )

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        metadata = json.load(file)

    return index, metadata


# ============================================================
# CONSULTA LOCAL
# ============================================================

def search(index, metadata, query_vector, top_k=5):
    """
    Executa uma busca simples no índice FAISS.

    A função apenas demonstra a recuperação vetorial.
    Filtros de vigência e limiar de 'não sei' pertencem
    à implementação da ferramenta retrieve_kb.
    """

    query_vector = np.asarray(
        query_vector,
        dtype=np.float32,
    )

    if query_vector.ndim == 1:
        query_vector = query_vector.reshape(1, -1)

    scores, indices = index.search(
        query_vector,
        top_k,
    )

    results = []

    for score, faiss_index in zip(
        scores[0],
        indices[0],
    ):

        if faiss_index == -1:
            continue

        item = metadata["items"][faiss_index]

        results.append(
            {
                "score": float(score),
                "faiss_index": int(faiss_index),
                "chunk_id": item["chunk_id"],
                "doc_family_id": item["doc_family_id"],
                "status": item["status"],
                "version_ordinal": item["version_ordinal"],
                "source_path": item["source_path"],
                "section_title": item["section_title"],
                "effective_from": item.get(
                    "effective_from"
                ),
                "effective_to": item.get(
                    "effective_to"
                ),
            }
        )

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("CRIAÇÃO DO ÍNDICE VETORIAL")
    print("Corpus ConectaTel")
    print("=" * 70)

    embeddings_data = load_embeddings()

    index = build_faiss_index(
        embeddings_data
    )

    metadata = build_metadata(
        embeddings_data
    )

    save_index(index)
    save_metadata(metadata)

    print()
    print("=" * 70)
    print("VECTOR STORE CRIADO COM SUCESSO")
    print("=" * 70)

    print(
        f"Modelo: "
        f"{embeddings_data['metadata']['model_name']}"
    )

    print(
        f"Dimensão: "
        f"{embeddings_data['metadata']['embedding_dimension']}"
    )

    print(
        f"Vetores: "
        f"{index.ntotal}"
    )

    print(f"Índice: {INDEX_PATH}")
    print(f"Metadados: {METADATA_PATH}")


if __name__ == "__main__":
    main()