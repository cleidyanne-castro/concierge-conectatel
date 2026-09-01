"""Configuração compartilhada do Concierge.

Fonte única de verdade para as variáveis de ambiente descritas em `.env.example`.
Nenhum módulo deve ler `os.environ` diretamente para esses valores — importe
`get_settings()` e use o objeto tipado. Sem lógica de negócio, sem chamada a
serviço externo: só carregamento e validação.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache

try:  # python-dotenv é dependência do projeto, mas o carregamento é opcional
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - ambiente sem .env (ex.: Lambda/Runtime)
    pass


def _get(name: str, default: str | None = None, *, required: bool = False) -> str:
    value = os.environ.get(name, default)
    if required and not value:
        raise RuntimeError(
            f"Variável de ambiente obrigatória ausente: {name}. "
            "Copie .env.example para .env e preencha, ou injete via IaC."
        )
    return value or ""


@dataclass(frozen=True)
class Settings:
    """Configuração efetiva da execução atual."""

    # AWS
    aws_region: str
    aws_profile: str

    # Base de conhecimento (Parte 2 / tool retrieve_kb)
    s3_bucket_name: str
    corpus_prefix: str
    vector_store_path: str
    embeddings_key: str
    chunks_key: str

    # Recuperação
    retrieval_score_threshold: float
    retrieval_top_k: int

    # Agente (Parte 3)
    bedrock_model_id: str
    retrieve_kb_function: str
    store_handoff_function: str

    # Escalonamento (Parte 4) — tool store_handoff
    handoff_table_name: str

    # Governança (Parte 5) — auditoria vive no CloudWatch
    audit_log_group: str

    @property
    def bedrock_stub_mode(self) -> bool:
        """Sem modelo configurado → adaptador Bedrock roda em modo stub local."""
        return not self.bedrock_model_id or self.bedrock_model_id.startswith("replace-")

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            aws_region=_get("AWS_REGION", "us-east-1"),
            aws_profile=_get("AWS_PROFILE", "default"),
            s3_bucket_name=_get("S3_BUCKET_NAME"),
            corpus_prefix=_get("CORPUS_PREFIX", "knowledge-base/"),
            vector_store_path=_get("VECTOR_STORE_PATH", "artifacts/index"),
            embeddings_key=_get("EMBEDDINGS_KEY", "index/embeddings.json"),
            chunks_key=_get("CHUNKS_KEY", "processed/chunks.json"),
            retrieval_score_threshold=float(_get("RETRIEVAL_SCORE_THRESHOLD", "0.85")),
            retrieval_top_k=int(_get("RETRIEVAL_TOP_K", "3")),
            bedrock_model_id=_get("BEDROCK_MODEL_ID", ""),
            retrieve_kb_function=_get(
                "RETRIEVE_KB_FUNCTION", "concierge-conectatel-retrieve-kb"
            ),
            store_handoff_function=_get(
                "STORE_HANDOFF_FUNCTION", "concierge-conectatel-store-handoff"
            ),
            handoff_table_name=_get("HANDOFF_TABLE_NAME", "concierge-handoff"),
            audit_log_group=_get("AUDIT_LOG_GROUP", "/concierge/agent"),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Configuração memoizada — carregada uma vez por processo."""
    return Settings.from_env()
