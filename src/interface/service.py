"""Cliente da Lambda de busca usado pela interface local.

Não contém credenciais: usa o profile AWS configurado no ambiente/.env.
"""

from __future__ import annotations

import json
from typing import Any

import boto3

from src.shared.config import get_settings


def invoke_retrieve_kb(
    question: str,
    trace_id: str | None = None,
    *,
    client: Any | None = None,
) -> dict[str, Any]:
    """Invoca a tool publicada e retorna seu JSON de domínio."""

    question = question.strip()
    if not question:
        raise ValueError("Informe uma pergunta para testar.")

    settings = get_settings()
    lambda_client = client
    if lambda_client is None:
        session = boto3.Session(
            profile_name=settings.aws_profile or None,
            region_name=settings.aws_region,
        )
        lambda_client = session.client("lambda")

    payload: dict[str, str] = {"question": question}
    if trace_id and trace_id.strip():
        payload["trace_id"] = trace_id.strip()

    response = lambda_client.invoke(
        FunctionName=settings.retrieve_kb_function,
        InvocationType="RequestResponse",
        Payload=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    )
    raw = response["Payload"].read() or b"{}"
    body = json.loads(raw)
    if response.get("FunctionError"):
        raise RuntimeError(body.get("errorMessage", "A Lambda retornou um erro."))
    if not isinstance(body, dict):
        raise RuntimeError("A Lambda retornou um payload inesperado.")
    return body
