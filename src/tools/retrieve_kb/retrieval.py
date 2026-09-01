import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer


MODEL_NAME = "intfloat/multilingual-e5-small"
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model

def embed_query(question: str) -> np.ndarray:
    return get_model().encode(f"query: {question}", normalize_embeddings=True)

def load_kb(embeddings_path: Path, chunks_path: Path):
    embeddings_data = json.loads(embeddings_path.read_text(encoding="utf-8"))
    chunks_by_id = {
        c["chunk_id"]: c for c in json.loads(chunks_path.read_text(encoding="utf-8"))
    }
    return embeddings_data, chunks_by_id

def retrieve(question: str, embeddings_data: dict, chunks_by_id: dict,
             threshold: float, top_k: int = 3):
    items = embeddings_data["embeddings"]

    # 1) FILTRO ESTRUTURAL — vigência
    vigentes = [it for it in items if it["status"] == "vigente"]
    if not vigentes:
        return {"decision": "nao_sei", "results": [], "reason": "sem_documentos_vigentes"}

    matrix = np.array([it["embedding"] for it in vigentes], dtype=np.float32)
    query_vec = embed_query(question).astype(np.float32)

    # embeddings já normalizados -> produto interno = similaridade de cosseno
    scores = matrix @ query_vec

    order = np.argsort(-scores)[:top_k]
    results = []
    for idx in order:
        item = vigentes[idx]
        chunk = chunks_by_id.get(item["chunk_id"], {})
        results.append({
            "chunk_id": item["chunk_id"],
            "score": float(scores[idx]),
            "doc_family_id": item["doc_family_id"],
            "section_title": item.get("section_title"),
            "source_path": item["source_path"],
            "status": item["status"],
            "text": chunk.get("text"),
        })

    top_score = results[0]["score"] if results else 0.0
    decision = "responder" if top_score >= threshold else "nao_sei"

    return {"decision": decision, "results": results if decision == "responder" else []}