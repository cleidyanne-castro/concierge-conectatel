"""Configuração central. Segredos devem vir das credenciais AWS padrão ou do ambiente."""
from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    s3_bucket_name: str = os.getenv("S3_BUCKET_NAME", "")
    corpus_prefix: str = os.getenv("CORPUS_PREFIX", "knowledge-base/")
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "artifacts/index")
    retrieval_score_threshold: float = float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.70"))
    audit_log_path: str = os.getenv("AUDIT_LOG_PATH", "artifacts/audit/audit.jsonl")
    bedrock_model_id: str = os.getenv("BEDROCK_MODEL_ID", "")

