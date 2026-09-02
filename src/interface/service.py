"""Cliente da Lambda de busca usado pela interface local.

Não contém credenciais: usa o profile AWS configurado no ambiente/.env.
"""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import boto3

from src.shared.config import get_settings


def _post_json(url: str, payload: dict[str, str]) -> dict[str, Any]:
    """Envia um JSON à API HTTP do Concierge e normaliza erros de transporte."""

    request = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:  # nosec B310 - URL configurada localmente
            raw = response.read() or b"{}"
    except HTTPError as error:
        raw = error.read() or b"{}"
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = {}
        message = detail.get("answer") or detail.get("message") or f"HTTP {error.code}"
        raise RuntimeError(f"A API do Concierge retornou erro: {message}") from error
    except URLError as error:
        raise RuntimeError("Não foi possível conectar à API do Concierge.") from error

    try:
        body = json.loads(raw)
    except json.JSONDecodeError as error:
        raise RuntimeError("A API do Concierge retornou um JSON inválido.") from error
    if not isinstance(body, dict):
        raise RuntimeError("A API do Concierge retornou um payload inesperado.")
    return body


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


def invoke_concierge(
    question: str,
    trace_id: str | None = None,
    *,
    api_url: str | None = None,
    post_json: Any | None = None,
) -> dict[str, Any]:
    """Invoca o endpoint público do Concierge (API GW → AgentCore)."""

    question = question.strip()
    if not question:
        raise ValueError("Informe uma pergunta para testar.")

    url = (api_url if api_url is not None else get_settings().concierge_api_url).strip()
    if not url:
        raise ValueError("Informe a URL do Concierge no campo de ambiente da interface.")

    payload: dict[str, str] = {"question": question}
    if trace_id and trace_id.strip():
        payload["trace_id"] = trace_id.strip()

    return (post_json or _post_json)(url, payload)
