import base64
import json
import os
import time
from pathlib import Path

import boto3

try:  # imagem Lambda copia ``src/shared`` como pacote de topo
    from shared.security import normalize_trace_id
except ModuleNotFoundError:  # checkout local mantém o pacote sob ``src``
    from src.shared.security import normalize_trace_id

from .retrieval import load_kb, retrieve

# ============================================================
# CONFIGURAÇÃO (via variáveis de ambiente da Lambda)
# ============================================================

S3_BUCKET_NAME = os.environ["S3_BUCKET_NAME"]
EMBEDDINGS_KEY = os.environ.get("EMBEDDINGS_KEY", "index/embeddings.json")
CHUNKS_KEY = os.environ.get("CHUNKS_KEY", "processed/chunks.json")
RETRIEVAL_SCORE_THRESHOLD = float(os.environ.get("RETRIEVAL_SCORE_THRESHOLD", "0.85"))
TOP_K = int(os.environ.get("RETRIEVAL_TOP_K", "3"))
MAX_QUESTION_LENGTH = 4_000

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

    Instrumentado com checkpoints de tempo — em caso de timeout,
    esses logs (via CloudWatch) mostram qual etapa é o gargalo real,
    em vez de ficar adivinhando.
    """
    global _embeddings_data, _chunks_by_id

    if _embeddings_data is not None and _chunks_by_id is not None:
        return _embeddings_data, _chunks_by_id

    t0 = time.time()
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    s3 = _get_s3_client()

    if not EMBEDDINGS_PATH.exists():
        s3.download_file(S3_BUCKET_NAME, EMBEDDINGS_KEY, str(EMBEDDINGS_PATH))
    t1 = time.time()
    print(json.dumps({"checkpoint": "download_embeddings", "elapsed_s": round(t1 - t0, 2)}))

    if not CHUNKS_PATH.exists():
        s3.download_file(S3_BUCKET_NAME, CHUNKS_KEY, str(CHUNKS_PATH))
    t2 = time.time()
    print(json.dumps({"checkpoint": "download_chunks", "elapsed_s": round(t2 - t1, 2)}))

    _embeddings_data, _chunks_by_id = load_kb(EMBEDDINGS_PATH, CHUNKS_PATH)
    t3 = time.time()
    print(json.dumps({"checkpoint": "load_kb_json", "elapsed_s": round(t3 - t2, 2)}))

    # carrega o modelo de embedding já no cold start, não na 1ª pergunta
    from .retrieval import get_model
    get_model()
    t4 = time.time()
    print(json.dumps({"checkpoint": "load_sentence_transformer_model", "elapsed_s": round(t4 - t3, 2)}))
    print(json.dumps({"checkpoint": "TOTAL_cold_start", "elapsed_s": round(t4 - t0, 2)}))

    return _embeddings_data, _chunks_by_id


def _request_payload(event):
    """Normaliza invocações diretas da Lambda e eventos HTTP API v2.

    O AgentCore invoca a tool diretamente, com ``question`` no nível raiz.
    Já a rota de depuração ``POST /retrieve`` recebe o JSON serializado em
    ``event["body"]`` pelo API Gateway. Manter os dois formatos evita que a
    rota HTTP pareça saudável, mas descarte a pergunta do usuário.
    """
    event = event or {}
    if not isinstance(event, dict):
        return {}

    body = event.get("body")
    if body is None:
        return event

    if event.get("isBase64Encoded") and isinstance(body, str):
        try:
            body = base64.b64decode(body).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return {}

    if isinstance(body, str):
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            return {}

    return body if isinstance(body, dict) else {}


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

    payload = _request_payload(event)
    raw_question = payload.get("question")
    question = raw_question.strip() if isinstance(raw_question, str) else ""
    trace_id = normalize_trace_id(payload.get("trace_id"))

    if not question:
        return {
            "decision": "nao_sei",
            "trace_id": trace_id,
            "results": [],
            "reason": (
                "pergunta_invalida"
                if raw_question is not None and not isinstance(raw_question, str)
                else "pergunta_vazia"
            ),
        }
    if len(question) > MAX_QUESTION_LENGTH:
        return {
            "decision": "nao_sei",
            "trace_id": trace_id,
            "results": [],
            "reason": "pergunta_muito_longa",
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
        "decision": response["decision"],
        "top_score": response["results"][0]["score"] if response["results"] else None,
    }))

    return response
