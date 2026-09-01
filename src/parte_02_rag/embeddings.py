import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CHUNKS_PATH = PROJECT_ROOT / "artifacts" / "chunks" / "chunks.json"

QUESTIONS_PATH = (
    PROJECT_ROOT
    / "data"
    / "evaluation"
    / "embedding_questions.json"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "embeddings"
    / "evaluation"
)

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


MODELS = {
    "multilingual_e5_small": {
        "name": "intfloat/multilingual-e5-small",
        "type": "e5",
    },
    "multilingual_minilm": {
        "name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "type": "standard",
    },
}


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

def load_json(path: Path):
    """Carrega um arquivo JSON."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_chunks():
    """Carrega os chunks do corpus."""
    chunks = load_json(CHUNKS_PATH)

    if not chunks:
        raise ValueError("Nenhum chunk foi encontrado.")

    print(f"Chunks carregados: {len(chunks)}")

    return chunks


def load_questions():
    """Carrega as perguntas de avaliação."""
    questions = load_json(QUESTIONS_PATH)

    if not questions:
        raise ValueError("Nenhuma pergunta foi encontrada.")

    print(f"Perguntas carregadas: {len(questions)}")

    return questions


# ============================================================
# EMBEDDINGS
# ============================================================

def create_model(model_name: str):
    """Carrega um modelo Sentence Transformers."""
    print()
    print("=" * 70)
    print(f"Carregando modelo: {model_name}")
    print("=" * 70)

    model = SentenceTransformer(model_name)

    print("Modelo carregado com sucesso.")

    return model


def encode_chunks(model, chunks, model_type):
    """
    Gera embeddings para os chunks.

    Para modelos E5, utiliza o prefixo 'passage:'.
    """
    texts = []

    for chunk in chunks:
        text = chunk["text"]

        if model_type == "e5":
            text = f"passage: {text}"

        texts.append(text)

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    return np.asarray(embeddings)


def encode_questions(model, questions, model_type):
    """
    Gera embeddings para as perguntas.

    Para modelos E5, utiliza o prefixo 'query:'.
    """
    texts = []

    for question in questions:
        text = question["question"]

        if model_type == "e5":
            text = f"query: {text}"

        texts.append(text)

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    return np.asarray(embeddings)


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve(query_embedding, chunk_embeddings, chunks, top_k=5):
    """
    Recupera os chunks mais semelhantes à pergunta.

    Como os embeddings estão normalizados, o produto escalar
    equivale à similaridade de cosseno.
    """

    scores = np.dot(chunk_embeddings, query_embedding)

    ranked_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in ranked_indices:
        chunk = chunks[index]

        results.append(
            {
                "chunk_id": chunk["chunk_id"],
                "score": float(scores[index]),
                "doc_family_id": chunk["doc_family_id"],
                "status": chunk["status"],
                "version_ordinal": chunk["version_ordinal"],
                "source_path": chunk["source_path"],
                "section_title": chunk["section_title"],
            }
        )

    return results


# ============================================================
# MÉTRICAS
# ============================================================

def calculate_metrics(question, retrieved_chunks):
    """
    Calcula Hit@1, Hit@3, Hit@5 e MRR para uma pergunta.
    """

    expected_ids = set(question["expected_chunk_ids"])

    ranked_ids = [
        result["chunk_id"]
        for result in retrieved_chunks
    ]

    # --------------------------------------------
    # Hit@1
    # --------------------------------------------

    hit_at_1 = int(
        any(
            chunk_id in expected_ids
            for chunk_id in ranked_ids[:1]
        )
    )

    # --------------------------------------------
    # Hit@3
    # --------------------------------------------

    hit_at_3 = int(
        any(
            chunk_id in expected_ids
            for chunk_id in ranked_ids[:3]
        )
    )

    # --------------------------------------------
    # Hit@5
    # --------------------------------------------

    hit_at_5 = int(
        any(
            chunk_id in expected_ids
            for chunk_id in ranked_ids[:5]
        )
    )

    # --------------------------------------------
    # MRR
    # --------------------------------------------

    reciprocal_rank = 0.0

    for rank, chunk_id in enumerate(ranked_ids, start=1):

        if chunk_id in expected_ids:
            reciprocal_rank = 1.0 / rank
            break

    return {
        "hit_at_1": hit_at_1,
        "hit_at_3": hit_at_3,
        "hit_at_5": hit_at_5,
        "mrr": reciprocal_rank,
    }


# ============================================================
# AVALIAÇÃO DE UM MODELO
# ============================================================

def evaluate_model(model_key, model_config, chunks, questions):
    """
    Executa a avaliação completa de um modelo.
    """

    model_name = model_config["name"]
    model_type = model_config["type"]

    model = create_model(model_name)

    print()
    print("Gerando embeddings dos chunks...")

    chunk_embeddings = encode_chunks(
        model,
        chunks,
        model_type,
    )

    print("Embeddings dos chunks gerados.")

    print()
    print("Gerando embeddings das perguntas...")

    question_embeddings = encode_questions(
        model,
        questions,
        model_type,
    )

    print("Embeddings das perguntas gerados.")

    detailed_results = []

    for index, question in enumerate(questions):

        query_embedding = question_embeddings[index]

        retrieved = retrieve(
            query_embedding,
            chunk_embeddings,
            chunks,
            top_k=5,
        )

        metrics = calculate_metrics(
            question,
            retrieved,
        )

        result = {
            "question_id": question["question_id"],
            "question": question["question"],
            "expected_doc_family_id": question[
                "expected_doc_family_id"
            ],
            "expected_chunk_ids": question[
                "expected_chunk_ids"
            ],
            "retrieved": retrieved,
            "metrics": metrics,
        }

        detailed_results.append(result)

    # ========================================================
    # MÉTRICAS GERAIS
    # ========================================================

    total = len(detailed_results)

    hit_at_1 = sum(
        result["metrics"]["hit_at_1"]
        for result in detailed_results
    ) / total

    hit_at_3 = sum(
        result["metrics"]["hit_at_3"]
        for result in detailed_results
    ) / total

    hit_at_5 = sum(
        result["metrics"]["hit_at_5"]
        for result in detailed_results
    ) / total

    mrr = sum(
        result["metrics"]["mrr"]
        for result in detailed_results
    ) / total

    summary = {
        "model_key": model_key,
        "model_name": model_name,
        "total_questions": total,
        "hit_at_1": round(hit_at_1, 4),
        "hit_at_3": round(hit_at_3, 4),
        "hit_at_5": round(hit_at_5, 4),
        "mrr": round(mrr, 4),
    }

    output = {
        "summary": summary,
        "questions": detailed_results,
    }

    output_path = RESULTS_DIR / f"{model_key}.json"

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print(f"RESULTADO — {model_name}")
    print("=" * 70)

    print(f"Hit@1: {hit_at_1:.4f}")
    print(f"Hit@3: {hit_at_3:.4f}")
    print(f"Hit@5: {hit_at_5:.4f}")
    print(f"MRR:    {mrr:.4f}")

    print()
    print(f"Resultado salvo em:")
    print(output_path)

    return summary


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("AVALIAÇÃO DE MODELOS DE EMBEDDINGS")
    print("Corpus ConectaTel")
    print("=" * 70)

    chunks = load_chunks()
    questions = load_questions()

    summaries = []

    for model_key, model_config in MODELS.items():

        summary = evaluate_model(
            model_key,
            model_config,
            chunks,
            questions,
        )

        summaries.append(summary)

    # ========================================================
    # COMPARAÇÃO FINAL
    # ========================================================

    comparison_path = RESULTS_DIR / "comparison.json"

    comparison = {
        "models": summaries,
    }

    with open(
        comparison_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            comparison,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("=" * 70)
    print("COMPARAÇÃO DOS MODELOS")
    print("=" * 70)

    print()

    for summary in summaries:

        print(summary["model_name"])

        print(
            f"  Hit@1: {summary['hit_at_1']:.4f}"
        )

        print(
            f"  Hit@3: {summary['hit_at_3']:.4f}"
        )

        print(
            f"  Hit@5: {summary['hit_at_5']:.4f}"
        )

        print(
            f"  MRR:    {summary['mrr']:.4f}"
        )

        print()

    print(f"Comparação salva em:")
    print(comparison_path)


if __name__ == "__main__":
    main()