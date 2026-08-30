import json
import os
import time
import uuid
from pathlib import Path

import boto3

from tools.retrieve_kb.retrieval import load_kb, retrieve

# ============================================================
# CONFIGURAÇÃO (via variáveis de ambiente da Lambda)
# ============================================================

S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
EMBEDDINGS_KEY = os.environ.get("EMBEDDINGS_KEY", "index/embeddings.json")
CHUNKS_KEY = os.environ.get("CHUNKS_KEY", "processed/chunks.json")
RETRIEVAL_SCORE_THRESHOLD = float(os.environ.get("RETRIEVAL_SCORE_THRESHOLD", "0.65"))
TOP_K = int(os.environ.get("RETRIEVAL_TOP_K", "3"))

TMP_DIR = Path("/tmp/retrieve_kb")
EMBEDDINGS_PATH = TMP_DIR / "embeddings.json"
CHUNKS_PATH = TMP_DIR / "chunks.json"

# ============================================================
# CACHE ENTRE INVOCAÇÕES (mesmo container/Lambda quente)
# ============================================================

_s3_client = None
_embeddings_data = None
_chunks_by_id = None


def _get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client("s3")
    return _s3_client


def _ensure_kb_loaded():
    """Baixa os artefatos do S3 pra /tmp e carrega em memória,
    apenas na primeira invocação de um container (cold start).
    """
    global _embeddings_data, _chunks_by_id

    if _embeddings_data is not None and _chunks_by_id is not None:
        return _embeddings_data, _chunks_by_id

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    s3 = _get_s3_client()

    if not EMBEDDINGS_PATH.exists():
        s3.download_file(S3_BUCKET_NAME, EMBEDDINGS_KEY, str(EMBEDDINGS_PATH))

    if not CHUNKS_PATH.exists():
        s3.download_file(S3_BUCKET_NAME, CHUNKS_KEY, str(CHUNKS_PATH))

    _embeddings_data, _chunks_by_id = load_kb(EMBEDDINGS_PATH, CHUNKS_PATH)

    # carrega o modelo de embedding já no cold start, não na 1ª pergunta
    from tools.retrieve_kb.retrieval import get_model
    get_model()

    return _embeddings_data, _chunks_by_id


# ============================================================
# HANDLER
# ============================================================

def handler(event, context):
    """
    Payload de entrada esperado (invocado pelo SubAgente Buscador):
    {
        "question": "texto da pergunta do assinante",
        "trace_id": "opcional — propagado pelo Orquestrador"
    }
    """

    started_at = time.time()

    question = (event or {}).get("question", "").strip()
    trace_id = (event or {}).get("trace_id") or str(uuid.uuid4())

    if not question:
        return {
            "decision": "nao_sei",
            "trace_id": trace_id,
            "results": [],
            "reason": "pergunta_vazia",
        }

    try:
        embeddings_data, chunks_by_id = _ensure_kb_loaded()

        result = retrieve(
            question=question,
            embeddings_data=embeddings_data,
            chunks_by_id=chunks_by_id,
            threshold=RETRIEVAL_SCORE_THRESHOLD,
            top_k=TOP_K,
        )

        response = {
            "decision": result["decision"],
            "trace_id": trace_id,
            "results": result["results"],
            "threshold_used": RETRIEVAL_SCORE_THRESHOLD,
            "latency_ms": int((time.time() - started_at) * 1000),
        }

    except Exception as error:
        # nunca deixa a tool "inventar" resposta em caso de erro —
        # falha segura cai em não_sei, e o erro fica registrado pro CloudWatch
        print(json.dumps({
            "trace_id": trace_id,
            "level": "ERROR",
            "message": str(error),
        }))
        response = {
            "decision": "nao_sei",
            "trace_id": trace_id,
            "results": [],
            "reason": "erro_interno",
        }

    # log estruturado — é o que a Parte 5 (Natan) vai consultar por trace_id
    print(json.dumps({
        "trace_id": trace_id,
        "question": question,
        "decision": response["decision"],
        "top_score": response["results"][0]["score"] if response["results"] else None,
    }))

    return response