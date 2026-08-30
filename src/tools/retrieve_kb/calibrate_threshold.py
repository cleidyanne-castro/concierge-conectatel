"""
Calibra o limiar de "não sei" da retrieve_kb.

Executa localmente (não faz parte do runtime da Lambda):
    python -m src.tools.retrieve_kb.calibrate_threshold
"""

import json
from pathlib import Path

from src.tools.retrieve_kb.retrieval import load_kb, retrieve

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EMBEDDINGS_PATH = PROJECT_ROOT / "artifacts" / "embeddings" / "embeddings.json"
CHUNKS_PATH = PROJECT_ROOT / "artifacts" / "chunks" / "chunks.json"
QUESTIONS_PATH = PROJECT_ROOT / "data" / "evaluation" / "embedding_questions.json"

OUTPUT_PATH = PROJECT_ROOT / "artifacts" / "retrieval" / "calibration_report.json"

THRESHOLDS = [0.80, 0.82, 0.84, 0.85, 0.86, 0.88, 0.90]

# perguntas deliberadamente fora do corpus — conjunto negativo
# recomendação: use pelo menos 15-20 perguntas aqui para uma margem confiável
# (o corte real fica bem perto do teto do cosseno em modelos e5 — ver "Como
# interpretar os resultados" logo abaixo)
NEGATIVE_QUESTIONS = [
    "Qual é a previsão do tempo em Salvador hoje?",
    "Vocês vendem plano internacional para os EUA?",
    "Qual o horário de funcionamento do banco mais próximo?",
    "Como faço para trocar o óleo do meu carro?",
    "Qual é a capital da Argentina?",
]


def evaluate_threshold(threshold, positives, negatives, embeddings_data, chunks_by_id):
    tp = fp = tn = fn = 0

    for q in positives:
        result = retrieve(
            q["question"], embeddings_data, chunks_by_id, threshold=threshold
        )
        acertou = (
            result["results"]
            and result["results"][0]["chunk_id"] in q["expected_chunk_ids"]
        )
        if result["decision"] == "responder" and acertou:
            tp += 1
        else:
            fn += 1

    for question in negatives:
        result = retrieve(question, embeddings_data, chunks_by_id, threshold=threshold)
        if result["decision"] == "nao_sei":
            tn += 1
        else:
            fp += 1

    return {"threshold": threshold, "tp": tp, "fp": fp, "tn": tn, "fn": fn}


def debug_scores(positives, negatives, embeddings_data, chunks_by_id):
    """
    Roda cada pergunta com threshold=0.0 (sempre traz o top-1, independente
    de decisão) e mostra o score real e se o chunk_id bateu com o esperado.
    Use isto ANTES de confiar na tabela de thresholds — se os números da
    varredura não mudam entre valores muito diferentes de threshold, o
    problema normalmente está aqui: scores fora da faixa testada, ou
    chunk_id não batendo por formato/prefixo diferente entre
    embeddings.json e embedding_questions.json.
    """

    rows = []

    print("=== POSITIVAS (esperado vs. obtido) ===")
    for q in positives:
        result = retrieve(
            q["question"], embeddings_data, chunks_by_id, threshold=0.0, top_k=1
        )
        top = result["results"][0] if result["results"] else None
        row = {
            "question_id": q["question_id"],
            "question": q["question"],
            "score": top["score"] if top else None,
            "expected_chunk_ids": q["expected_chunk_ids"],
            "obtained_chunk_id": top["chunk_id"] if top else None,
            "chunk_id_match": bool(top and top["chunk_id"] in q["expected_chunk_ids"]),
        }
        rows.append({"type": "positive", **row})
        print(
            f"{row['question_id']:5} score={row['score']!s:>10}  "
            f"match={row['chunk_id_match']!s:5}  "
            f"esperado={row['expected_chunk_ids']}  obtido={row['obtained_chunk_id']}"
        )

    print("\n=== NEGATIVAS (deveriam ter score baixo) ===")
    for question in negatives:
        result = retrieve(question, embeddings_data, chunks_by_id, threshold=0.0, top_k=1)
        top = result["results"][0] if result["results"] else None
        row = {
            "question": question,
            "score": top["score"] if top else None,
            "top_chunk_id": top["chunk_id"] if top else None,
        }
        rows.append({"type": "negative", **row})
        print(f"score={row['score']!s:>10}  chunk={row['top_chunk_id']}  pergunta={question!r}")

    return rows


def main():
    import sys

    debug_mode = "--debug" in sys.argv

    embeddings_data, chunks_by_id = load_kb(EMBEDDINGS_PATH, CHUNKS_PATH)
    positives = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))

    debug_rows = None
    if debug_mode:
        debug_rows = debug_scores(positives, NEGATIVE_QUESTIONS, embeddings_data, chunks_by_id)
        print()

    report = [
        evaluate_threshold(t, positives, NEGATIVE_QUESTIONS, embeddings_data, chunks_by_id)
        for t in THRESHOLDS
    ]

    # escolhe o menor limiar sem falso positivo, mantendo o máximo de acertos
    candidatos = [r for r in report if r["fp"] == 0]
    melhor = max(candidatos, key=lambda r: r["tp"]) if candidatos else None

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(
            {
                "model": "intfloat/multilingual-e5-small",
                "positive_questions_source": str(QUESTIONS_PATH),
                "negative_questions": NEGATIVE_QUESTIONS,
                "results": report,
                "recommended_threshold": melhor["threshold"] if melhor else None,
                "debug_scores": debug_rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"Relatório salvo em: {OUTPUT_PATH}")
    for r in report:
        print(r)
    print(f"Limiar recomendado: {melhor['threshold'] if melhor else 'nenhum threshold zerou FP'}")


if __name__ == "__main__":
    main()