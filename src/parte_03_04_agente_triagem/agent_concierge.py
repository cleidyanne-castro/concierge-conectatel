"""Agente Concierge — roda dentro do Amazon Bedrock AgentCore Runtime.

Um agente Strands com duas ferramentas:
  - retrieve_kb    : busca na base vetorial (Lambda do Kaique)
  - store_handoff  : registra escalonamento no DynamoDB (Lambda do José)

Este arquivo E o entrypoint do container: rodar `app.run()` sobe o servidor
/invocations + /ping na porta 8080 (BedrockAgentCoreApp).
"""

from __future__ import annotations

import contextvars
import json
import os
import re
import sys
import uuid
from datetime import datetime, timezone

import boto3
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent, tool
from strands.models import BedrockModel

from src.shared.config import get_settings
from src.shared.security import normalize_trace_id, redact_pii
from src.shared.types import AuditEvent, ConciergeResponse, HandoffRecord

# ------------------------------------------------------------------
# Etapa 1 — Configuracao (injetada como variavel de ambiente pelo Runtime)
# ------------------------------------------------------------------
settings = get_settings()

MODEL_ID = settings.bedrock_model_id or os.environ.get("MODEL_ID", "")
AWS_REGION = settings.aws_region
RETRIEVE_KB_FUNCTION = settings.retrieve_kb_function
STORE_HANDOFF_FUNCTION = settings.store_handoff_function
MAX_QUESTION_LENGTH = 4_000

app = BedrockAgentCoreApp()
bedrock_model = BedrockModel(
    model_id=MODEL_ID,
    region_name=AWS_REGION,
    # Parâmetros recomendados pela AWS para estabilizar ToolUse no Nova.
    temperature=0,
    max_tokens=3000,
    additional_request_fields={"inferenceConfig": {"topK": 1}},
)

# Client Lambda reaproveitado entre invocacoes quentes do container.
_lambda_client = None


def _lambda():
    global _lambda_client
    if _lambda_client is None:
        _lambda_client = boto3.client("lambda", region_name=AWS_REGION)
    return _lambda_client


# Contexto por requisicao: as tools escrevem aqui os efeitos colaterais
# (ultimo retrieve, handoff gerado) e o entrypoint monta a ConciergeResponse
# a partir disso — o texto do LLM sozinho nao carrega decision/source_path.
_ctx: contextvars.ContextVar[dict] = contextvars.ContextVar("concierge_ctx")


def _ctx_get() -> dict:
    try:
        return _ctx.get()
    except LookupError:
        return {
            "trace_id": "",
            "last_retrieve": None,
            "handoff": None,
            "handoff_failure": None,
            "handoff_guardrail": None,
        }


def _ultimo_source_path(ctx: dict) -> str | None:
    results = (ctx.get("last_retrieve") or {}).get("results") or []
    return results[0].get("source_path") if results else None


def _invoke_lambda(function_name: str, payload: dict) -> dict:
    resp = _lambda().invoke(
        FunctionName=function_name,
        Payload=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
    )
    raw = resp["Payload"].read() or b"{}"
    data = json.loads(raw)
    return data if isinstance(data, dict) else {"raw": data}


# ------------------------------------------------------------------
# Etapa 2 — tool retrieve_kb (Lambda do Kaique)
# ------------------------------------------------------------------
@tool
def retrieve_kb(question: str) -> dict:
    """Busca na base de conhecimento oficial e VIGENTE da ConectaTel.

    Chame SEMPRE antes de responder qualquer pergunta factual do assinante
    (planos, prazos, politicas, procedimentos).

    Retorna um dict no formato RetrieveResult:
      - decision: "responder" ou "nao_sei" (ja decidido pela ferramenta)
      - results: lista de trechos com source_path, text, score
    Se decision == "nao_sei" ou results vazio, NAO invente: diga que nao sabe.
    """
    ctx = _ctx_get()
    try:
        result = _invoke_lambda(
            RETRIEVE_KB_FUNCTION,
            {"question": question, "trace_id": ctx.get("trace_id", "")},
        )
    except Exception as error:  # falha segura — o agente trata como "nao sei"
        print(json.dumps({"trace_id": ctx.get("trace_id"), "level": "ERROR",
                          "tool": "retrieve_kb", "message": str(error)}))
        result = {"decision": "nao_sei", "results": [], "reason": "erro_tool_retrieve"}

    ctx["last_retrieve"] = result
    return result


# ------------------------------------------------------------------
# Etapa 3 — tool store_handoff (Lambda do José / DynamoDB)
# ------------------------------------------------------------------
@tool
def store_handoff(
    categoria_motivo: str,
    resumo_caso: str,
    urgencia: str,
    dados_contato_retorno: str,
) -> dict:
    """Registra o caso para atendimento humano (escalonamento).

    Chame quando o caso se enquadrar em QUALQUER um dos 8 criterios da Politica
    de Suporte e Escalonamento (fraude; contestacao de fatura >= R$500;
    contestacao de multa de fidelidade; titularidade/falecimento; reclamacao em
    Anatel/Procon ou acao judicial; assedio/discriminacao; problema tecnico com
    visita presencial; ou pergunta sem fonte suficiente com cliente insistindo).

    Em `resumo_caso`, consolide também produto/serviço e verificações já feitas,
    para o atendente não pedir que o cliente repita o relato. `urgencia` deve ser
    "baixa", "media" ou "alta". Se faltar contato, pergunte antes de chamar.

    O contrato é intencionalmente enxuto: esquemas extensos fazem o Amazon Nova
    Lite produzir sequências ToolUse inválidas. Os demais campos auditáveis são
    derivados de forma determinística pela aplicação.
    """
    ctx = _ctx_get()
    ctx["handoff_guardrail"] = categoria_motivo

    # Uma tentativa anterior do mesmo ciclo do agente pode ter persistido o
    # handoff antes de o modelo encerrar o stream com uma sequência ToolUse
    # inválida. Nesse caso, o retry deve reutilizar o protocolo confirmado em
    # memória, nunca criar outro registro para o mesmo trace.
    existing_handoff = ctx.get("handoff")
    if isinstance(existing_handoff, HandoffRecord):
        return {
            "stored": True,
            "protocolo": existing_handoff.protocolo_atendimento,
        }

    contact = dados_contato_retorno.strip()
    if not contact:
        reason = "dados_contato_retorno_ausente"
        ctx["handoff_failure"] = reason
        print(json.dumps({"trace_id": ctx.get("trace_id"), "level": "ERROR",
                          "tool": "store_handoff", "message": reason}))
        return {"stored": False, "reason": reason}

    record = HandoffRecord(
        protocolo_atendimento=(
            f"CONCTL-{datetime.now(timezone.utc):%Y%m%d}-{uuid.uuid4().hex[:6].upper()}"
        ),
        data_hora_abertura=datetime.now(timezone.utc).isoformat(),
        canal_origem="chat",
        categoria_motivo=categoria_motivo,
        resumo_caso=resumo_caso,
        historico_ja_levantado=resumo_caso,
        produto_servico_envolvido="Conforme relato consolidado no resumo do caso",
        documento_fonte_consultado=(
            _ultimo_source_path(ctx) or "Nenhum documento vigente aplicavel"
        ),
        urgencia=urgencia if urgencia in ("baixa", "media", "alta") else "media",
        dados_contato_retorno=contact,
        trace_id=ctx.get("trace_id", ""),
    )

    try:
        result = _invoke_lambda(STORE_HANDOFF_FUNCTION, record.to_item())
        if result.get("duplicate") is True:
            raise RuntimeError("trace_id_duplicado")
        if result.get("stored") is not True:
            reason = result.get("reason", "handoff_nao_persistido")
            raise RuntimeError(reason)
    except Exception as error:
        reason = str(error) or "handoff_nao_persistido"
        ctx["handoff_failure"] = reason
        print(json.dumps({"trace_id": ctx.get("trace_id"), "level": "ERROR",
                          "tool": "store_handoff", "message": reason}))
        return {"stored": False, "reason": reason}

    ctx["handoff"] = record
    ctx["handoff_failure"] = None
    return {"stored": True, "protocolo": record.protocolo_atendimento}


# ------------------------------------------------------------------
# Etapa 4 — system prompt
# ------------------------------------------------------------------
system_prompt = """\
Voce e o Concierge ConectaTel, assistente de atendimento da operadora ficticia
ConectaTel. Responde assinantes em portugues do Brasil, com tom cordial e objetivo.

REGRAS:
1. Antes de responder qualquer pergunta factual, chame a ferramenta retrieve_kb.
2. Responda SOMENTE com base no texto retornado por retrieve_kb. Cite a fonte
   usando o campo source_path do trecho utilizado.
3. Se retrieve_kb retornar decision "nao_sei" ou uma lista results vazia,
   responda que nao encontrou essa informacao na base oficial e NAO tente
   deduzir. Nao use conhecimento externo.
4. Escalonamento: se o caso se enquadrar em qualquer um dos 8 criterios da
   Politica de Suporte e Escalonamento, chame store_handoff com os campos
   preenchidos a partir do que o cliente informou, e explique ao cliente que o
   atendimento sera continuado por um humano. Confirme registro e protocolo
   somente se a ferramenta retornar stored=true. Se stored=false, diga que o
   encaminhamento nao foi registrado e solicite o dado faltante ou nova tentativa.
   Nao tente resolver esses casos.
5. Nunca prometa prazos, valores ou condicoes que nao estejam nas fontes.
6. Responda direto ao assinante. Nao inclua tags <thinking> nem raciocinio
   interno na resposta final.
"""


# ------------------------------------------------------------------
# Etapa 5 — agente + entrypoint do Runtime
# ------------------------------------------------------------------
def _new_agent() -> Agent:
    """Cria uma conversa isolada para cada invocação do Runtime.

    O Strands acumula mensagens no objeto ``Agent``. Reutilizar uma instância
    global mistura sessões de clientes e pode produzir sequências ToolUse
    inválidas quando uma chamada anterior termina com erro.
    """

    return Agent(
        model=bedrock_model,
        tools=[retrieve_kb, store_handoff],
        system_prompt=system_prompt,
        callback_handler=None,  # sem echo de streaming no stdout
    )


# Nova (e outros) as vezes emitem raciocinio em <thinking>...</thinking>;
# nunca deve vazar pra resposta do assinante.
_THINK_RE = re.compile(
    r"<thinking>.*?(?:</thinking>|$)",
    re.DOTALL | re.IGNORECASE,
)
_TOOL_USE_SEQUENCE_ERROR_MARKERS = (
    "modelStreamErrorException",
    "invalid sequence as part of ToolUse",
)
_MAX_TOOL_USE_ATTEMPTS = 4


def _clean_answer(text: str) -> str:
    return _THINK_RE.sub("", text).strip()


def _invoke_agent(question: str) -> str:
    """Invoca o Nova com retry somente para sequência ToolUse inválida."""

    for attempt in range(1, _MAX_TOOL_USE_ATTEMPTS + 1):
        if attempt > 1:
            # Resultados de busca pertencem à tentativa que os produziu. Se o
            # stream falhou depois da tool, uma nova resposta só pode ser
            # classificada como fundamentada se o agente repetir a consulta.
            _ctx_get()["last_retrieve"] = None
        try:
            return str(_new_agent()(question))
        except Exception as error:
            message = str(error)
            retryable = any(
                marker in message for marker in _TOOL_USE_SEQUENCE_ERROR_MARKERS
            )
            if not retryable or attempt == _MAX_TOOL_USE_ATTEMPTS:
                raise
            print(json.dumps({
                "trace_id": _ctx_get().get("trace_id"),
                "level": "WARNING",
                "event": "agent_tool_use_retry",
                "attempt": attempt,
            }))

    raise RuntimeError("agent_tool_use_retry_exhausted")  # pragma: no cover


def _build_response(trace_id: str, answer: str, ctx: dict) -> ConciergeResponse:
    if ctx.get("handoff") is not None:
        handoff = ctx["handoff"]
        return ConciergeResponse(
            "escalar",
            trace_id,
            "Encaminhamento registrado para atendimento humano. "
            f"Protocolo: {handoff.protocolo_atendimento}.",
            handoff=handoff,
        )
    if ctx.get("handoff_failure"):
        return ConciergeResponse(
            "nao_sei",
            trace_id,
            "Não foi possível registrar o encaminhamento e nenhum protocolo foi "
            "confirmado. Informe um canal de contato para retorno, caso ainda não "
            "tenha informado, e tente novamente.",
        )

    last = ctx.get("last_retrieve") or {}
    results = last.get("results") or []
    answer = answer.strip()
    if last.get("decision") == "responder" and results and answer:
        source_path = results[0].get("source_path")
        if source_path and source_path not in answer:
            answer = f"{answer}\n\nFonte: {source_path}"
        return ConciergeResponse(
            "responder", trace_id, answer, source_path=source_path
        )
    return ConciergeResponse(
        "nao_sei",
        trace_id,
        "Não encontrei informação suficiente na base oficial para responder com "
        "segurança.",
    )


def _emit_audit(question: str, resp: ConciergeResponse, ctx: dict) -> None:
    results = (ctx.get("last_retrieve") or {}).get("results") or []
    fontes = list(dict.fromkeys(
        r["source_path"] for r in results if r.get("source_path")
    ))
    event = AuditEvent(
        trace_id=resp.trace_id,
        question=redact_pii(question),
        decision=resp.decision,
        sources=fontes,
        top_score=results[0].get("score") if results else None,
        guardrail=(
            resp.handoff.categoria_motivo
            if resp.handoff
            else ctx.get("handoff_guardrail")
        ),
    )
    # stderr: em Lambda/AgentCore vai pro CloudWatch igual; no CLI mantem o
    # stdout limpo (so a ConciergeResponse).
    print(json.dumps(event.to_log(), ensure_ascii=False), file=sys.stderr)


def run(payload: dict | None) -> dict:
    """Fluxo do agente. Entrada: {"question": "...", "trace_id": "opcional"}.

    Chamado pelo entrypoint do Runtime (`invoke`) e pela entrada local
    (`src/cli.py`) — sem depender do servidor HTTP do AgentCore.
    """
    payload = payload if isinstance(payload, dict) else {}
    raw_question = payload.get("question")
    question = raw_question.strip() if isinstance(raw_question, str) else ""
    trace_id = normalize_trace_id(payload.get("trace_id"))
    _ctx.set({
        "trace_id": trace_id,
        "last_retrieve": None,
        "handoff": None,
        "handoff_failure": None,
        "handoff_guardrail": None,
    })

    if not question:
        message = "Pergunta vazia." if raw_question in (None, "") else "Pergunta inválida."
        return ConciergeResponse("nao_sei", trace_id, message).to_dict()
    if len(question) > MAX_QUESTION_LENGTH:
        return ConciergeResponse(
            "nao_sei",
            trace_id,
            f"A pergunta excede o limite de {MAX_QUESTION_LENGTH} caracteres.",
        ).to_dict()

    answer = _clean_answer(_invoke_agent(question))
    ctx = _ctx_get()
    resp = _build_response(trace_id, answer, ctx)
    _emit_audit(question, resp, ctx)
    return resp.to_dict()


@app.entrypoint
def invoke(payload):
    return run(payload)


if __name__ == "__main__":
    app.run()
