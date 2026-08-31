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
import uuid

import boto3

_AGENT_RUNTIME_ARN = os.environ.get("AGENT_RUNTIME_ARN", "")
_CORS_ORIGIN = os.environ.get("CORS_ALLOW_ORIGIN", "*")


_client = None


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
    """Le o corpo (streaming ou nao) e devolve dict; nunca levanta."""
    body = agent_response.get("response")
    try:
        raw = body.read() if hasattr(body, "read") else body
        if isinstance(raw, (bytes, bytearray)):
            raw = raw.decode("utf-8")
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {"answer": parsed}
    except Exception:  # pragma: no cover - resposta inesperada do Runtime
        return {"answer": "", "raw": str(body)}


def handler(event, context):
    # Preflight CORS
    method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
    )
    if method == "OPTIONS":
        return _resp(200, {"ok": True})

    body = _parse_body(event)
    question = (body.get("question") or "").strip()
    # Origem canonica do trace_id: se a interface nao mandou, o gateway gera.
    trace_id = (body.get("trace_id") or str(uuid.uuid4())).strip()
    client_trace = bool(body.get("trace_id"))
    print(json.dumps({"trace_id": trace_id, "event": "gateway_in",
                      "trace_origin": "client" if client_trace else "gateway"}))

    if not question:
        return _resp(400, {
            "decision": "nao_sei",
            "trace_id": trace_id,
            "answer": "Pergunta vazia.",
            "reason": "pergunta_vazia",
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
        result.setdefault("trace_id", trace_id)

        print(json.dumps({
            "trace_id": trace_id,
            "question": question,
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
