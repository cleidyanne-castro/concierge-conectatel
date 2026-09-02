"""Lambda de borda: API Gateway (HTTP API) -> AgentCore Runtime.

O HTTP API nao invoca o Runtime diretamente; esta Lambda faz a ponte:
le o corpo da requisicao, chama `bedrock-agentcore:InvokeAgentRuntime` e
devolve a resposta do agente com cabecalhos CORS.

So transporte: nenhuma regra de negocio, nenhum acesso a Bedrock/modelo aqui.

Variaveis de ambiente:
  AGENT_RUNTIME_ARN   ARN do Runtime publicado (obrigatoria).
  AWS_REGION          regiao (a Lambda ja injeta).
  CORS_ALLOW_ORIGIN   origem permitida no CORS (default "*").
"""

from __future__ import annotations

import json
import os
import re
import uuid

import boto3

_AGENT_RUNTIME_ARN = os.environ.get("AGENT_RUNTIME_ARN", "")
_CORS_ORIGIN = os.environ.get("CORS_ALLOW_ORIGIN", "*")


_client = None
_UNSAFE_TRACE_CHARS_RE = re.compile(r"[^A-Za-z0-9]+")
MAX_QUESTION_LENGTH = 4_000


def _normalize_trace_id(value: str | None) -> str:
    """Mantém o trace seguro para headers e para o runtimeSessionId."""

    normalized = _UNSAFE_TRACE_CHARS_RE.sub("-", str(value or "")).strip("-")
    if not normalized:
        normalized = str(uuid.uuid4())
    return normalized[:95].rstrip("-") or str(uuid.uuid4())


def _agentcore():
    global _client
    if _client is None:
        _client = boto3.client("bedrock-agentcore")
    return _client


def _resp(status: int, body: dict, trace_id: str = "") -> dict:
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": _CORS_ORIGIN,
        "Access-Control-Allow-Headers": "content-type",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
    }
    if trace_id:
        headers["X-Trace-Id"] = trace_id
    return {
        "statusCode": status,
        "headers": headers,
        "body": json.dumps(body, ensure_ascii=False),
    }


def _parse_body(event: dict) -> dict:
    raw = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        import base64

        raw = base64.b64decode(raw).decode("utf-8")
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except (ValueError, TypeError):
        return {}


def _session_id(trace_id: str) -> str:
    """AgentCore exige runtimeSessionId com 33-128 caracteres."""
    sid = f"{trace_id}-{uuid.uuid4().hex}"
    return sid if len(sid) >= 33 else sid.ljust(33, "0")


def _read_agent_payload(agent_response: dict) -> dict:
    """Lê e valida o envelope JSON básico devolvido pelo Runtime."""
    body = agent_response.get("response")
    try:
        raw = body.read() if hasattr(body, "read") else body
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")
        parsed = json.loads(raw)
    except (TypeError, ValueError, UnicodeDecodeError) as error:
        raise ValueError("Runtime retornou JSON inválido.") from error

    if not isinstance(parsed, dict):
        raise ValueError("Runtime retornou um payload que não é objeto JSON.")
    if parsed.get("decision") not in {"responder", "nao_sei", "escalar"}:
        raise ValueError("Runtime retornou uma decisão inválida.")
    if not isinstance(parsed.get("answer"), str):
        raise ValueError("Runtime retornou uma resposta textual inválida.")
    if parsed.get("source_path") is not None and not isinstance(
        parsed.get("source_path"), str
    ):
        raise ValueError("Runtime retornou uma fonte inválida.")
    if parsed.get("handoff") is not None and not isinstance(parsed.get("handoff"), dict):
        raise ValueError("Runtime retornou um handoff inválido.")
    return parsed


def handler(event, context):
    # Preflight CORS
    method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
    )
    if method == "OPTIONS":
        return _resp(200, {"ok": True})

    body = _parse_body(event)
    raw_question = body.get("question")
    question = raw_question.strip() if isinstance(raw_question, str) else ""
    # Origem canonica do trace_id: se a interface nao mandou, o gateway gera.
    trace_id = _normalize_trace_id(body.get("trace_id"))
    client_trace = bool(body.get("trace_id"))
    print(json.dumps({"trace_id": trace_id, "event": "gateway_in",
                      "trace_origin": "client" if client_trace else "gateway"}))

    if not question:
        invalid_type = raw_question is not None and not isinstance(raw_question, str)
        return _resp(400, {
            "decision": "nao_sei",
            "trace_id": trace_id,
            "answer": "Pergunta inválida." if invalid_type else "Pergunta vazia.",
            "reason": "pergunta_invalida" if invalid_type else "pergunta_vazia",
        }, trace_id)

    if len(question) > MAX_QUESTION_LENGTH:
        return _resp(413, {
            "decision": "nao_sei",
            "trace_id": trace_id,
            "answer": f"A pergunta excede o limite de {MAX_QUESTION_LENGTH} caracteres.",
            "reason": "pergunta_muito_longa",
        }, trace_id)

    if not _AGENT_RUNTIME_ARN:
        print(json.dumps({"trace_id": trace_id, "level": "ERROR",
                          "message": "AGENT_RUNTIME_ARN nao configurada"}))
        return _resp(500, {"decision": "nao_sei", "trace_id": trace_id,
                           "answer": "Configuracao incompleta.", "reason": "sem_runtime_arn"}, trace_id)

    try:
        agent_response = _agentcore().invoke_agent_runtime(
            agentRuntimeArn=_AGENT_RUNTIME_ARN,
            runtimeSessionId=_session_id(trace_id),
            payload=json.dumps({"question": question, "trace_id": trace_id}).encode("utf-8"),
            contentType="application/json",
            accept="application/json",
        )
        result = _read_agent_payload(agent_response)
        # O identificador da borda é canônico; o Runtime não pode substituí-lo.
        result["trace_id"] = trace_id

        print(json.dumps({
            "trace_id": trace_id,
            "decision": result.get("decision"),
        }))
        return _resp(200, result, trace_id)

    except Exception as error:  # falha segura — nunca vaza stack pro cliente
        print(json.dumps({
            "trace_id": trace_id,
            "level": "ERROR",
            "message": str(error),
        }))
        return _resp(502, {
            "decision": "nao_sei",
            "trace_id": trace_id,
            "answer": "Nao foi possivel processar agora. Tente novamente.",
            "reason": "erro_runtime",
        }, trace_id)
