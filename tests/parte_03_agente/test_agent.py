from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from src.parte_03_04_agente_triagem import agent_concierge, lambda_gateway
from src.shared.security import normalize_trace_id, redact_pii


def test_handoff_tool_exposes_nova_compatible_contract():
    schema = agent_concierge.store_handoff.tool_spec["inputSchema"]["json"]

    assert set(schema["properties"]) == {
        "categoria_motivo",
        "resumo_caso",
        "urgencia",
        "dados_contato_retorno",
    }
    assert set(schema["required"]) == set(schema["properties"])
    assert all("default" not in field for field in schema["properties"].values())


def test_handoff_contract_still_persists_complete_record(monkeypatch):
    captured = {}

    def fake_invoke(function_name, payload):
        captured.update(payload)
        return {"stored": True}

    monkeypatch.setattr(agent_concierge, "_invoke_lambda", fake_invoke)
    agent_concierge._ctx.set(
        {"trace_id": "handoff-completo", "last_retrieve": None, "handoff": None}
    )

    result = agent_concierge.store_handoff(
        categoria_motivo="Suspeita de fraude",
        resumo_caso="Linha móvel; cliente não reconhece a troca de chip.",
        urgencia="alta",
        dados_contato_retorno="Retorno pelo chat cadastrado",
    )

    assert result["stored"] is True
    assert captured["trace_id"] == "handoff-completo"
    assert captured["canal_origem"] == "chat"
    assert captured["historico_ja_levantado"] == captured["resumo_caso"]
    assert captured["produto_servico_envolvido"]
    assert captured["documento_fonte_consultado"]
    assert agent_concierge._ctx_get()["handoff"] is not None


def test_handoff_retry_reuses_protocol_persisted_in_same_request(monkeypatch):
    calls = []

    def fake_invoke(_function_name, payload):
        calls.append(payload)
        return {"stored": True}

    monkeypatch.setattr(agent_concierge, "_invoke_lambda", fake_invoke)
    agent_concierge._ctx.set(
        {"trace_id": "handoff-retry", "last_retrieve": None, "handoff": None}
    )

    first = agent_concierge.store_handoff(
        categoria_motivo="Suspeita de fraude",
        resumo_caso="Cliente não reconhece a troca de chip.",
        urgencia="alta",
        dados_contato_retorno="Retorno pelo chat",
    )
    second = agent_concierge.store_handoff(
        categoria_motivo="Suspeita de fraude",
        resumo_caso="Cliente não reconhece a troca de chip.",
        urgencia="alta",
        dados_contato_retorno="Retorno pelo chat",
    )

    assert second == first
    assert len(calls) == 1


def test_handoff_without_contact_is_not_published(monkeypatch):
    invoked = False

    def fake_invoke(*_args, **_kwargs):
        nonlocal invoked
        invoked = True
        return {"stored": True}

    monkeypatch.setattr(agent_concierge, "_invoke_lambda", fake_invoke)
    agent_concierge._ctx.set(
        {"trace_id": "handoff-sem-contato", "last_retrieve": None, "handoff": None}
    )

    result = agent_concierge.store_handoff(
        categoria_motivo="Contestação de fatura",
        resumo_caso="Cliente contesta cobrança de R$ 750.",
        urgencia="alta",
        dados_contato_retorno="   ",
    )

    ctx = agent_concierge._ctx_get()
    assert result == {
        "stored": False,
        "reason": "dados_contato_retorno_ausente",
    }
    assert invoked is False
    assert ctx["handoff"] is None
    assert ctx["handoff_failure"] == "dados_contato_retorno_ausente"


def test_handoff_persistence_failure_overrides_false_confirmation(
    monkeypatch, capsys
):
    monkeypatch.setattr(
        agent_concierge,
        "_invoke_lambda",
        lambda *_args, **_kwargs: {"stored": False, "reason": "falha_dynamodb"},
    )
    agent_concierge._ctx.set(
        {"trace_id": "handoff-falhou", "last_retrieve": None, "handoff": None}
    )

    tool_result = agent_concierge.store_handoff(
        categoria_motivo="Suspeita de fraude",
        resumo_caso="Cliente não reconhece a troca de chip.",
        urgencia="alta",
        dados_contato_retorno="Retorno pelo chat",
    )
    ctx = agent_concierge._ctx_get()
    response = agent_concierge._build_response(
        "handoff-falhou",
        "Seu caso foi registrado com sucesso.",
        ctx,
    )

    assert tool_result == {"stored": False, "reason": "falha_dynamodb"}
    assert response.decision == "nao_sei"
    assert response.handoff is None
    assert "nenhum protocolo foi confirmado" in response.answer
    assert ctx["handoff_guardrail"] == "Suspeita de fraude"

    agent_concierge._emit_audit(
        "Não reconheço a troca de chip.",
        response,
        ctx,
    )
    audit_event = json.loads(capsys.readouterr().err)
    assert audit_event["decision"] == "nao_sei"
    assert audit_event["guardrail"] == "Suspeita de fraude"


def test_duplicate_trace_does_not_confirm_a_new_protocol(monkeypatch):
    monkeypatch.setattr(
        agent_concierge,
        "_invoke_lambda",
        lambda *_args, **_kwargs: {
            "stored": True,
            "protocolo": "CONCTL-JA-PERSISTIDO",
            "duplicate": True,
        },
    )
    agent_concierge._ctx.set(
        {"trace_id": "trace-repetido", "last_retrieve": None, "handoff": None}
    )

    result = agent_concierge.store_handoff(
        categoria_motivo="Contestação de fatura",
        resumo_caso="Cliente contesta cobrança de R$ 750.",
        urgencia="alta",
        dados_contato_retorno="Retorno pelo chat",
    )
    ctx = agent_concierge._ctx_get()

    assert result == {"stored": False, "reason": "trace_id_duplicado"}
    assert ctx["handoff"] is None
    assert ctx["handoff_failure"] == "trace_id_duplicado"


def test_bedrock_model_uses_stable_nova_tool_parameters():
    config = agent_concierge.bedrock_model.config

    assert config["temperature"] == 0
    assert config["max_tokens"] == 3000
    assert config["additional_request_fields"] == {"inferenceConfig": {"topK": 1}}


def test_run_creates_an_isolated_agent_for_each_request(monkeypatch):
    created = []

    class FakeAgent:
        def __call__(self, question):
            return f"Sem fonte para: {question}"

    def fake_new_agent():
        instance = FakeAgent()
        created.append(instance)
        return instance

    monkeypatch.setattr(agent_concierge, "_new_agent", fake_new_agent)

    first = agent_concierge.run({"question": "pergunta um", "trace_id": "isolado-1"})
    second = agent_concierge.run({"question": "pergunta dois", "trace_id": "isolado-2"})

    assert len(created) == 2
    assert created[0] is not created[1]
    assert first["trace_id"] == "isolado-1"
    assert second["trace_id"] == "isolado-2"


def test_invalid_tool_use_sequence_retries_with_fresh_agents(monkeypatch):
    outcomes = [
        RuntimeError("modelStreamErrorException: invalid sequence as part of ToolUse"),
        RuntimeError("invalid sequence as part of ToolUse"),
        "resposta recuperada",
    ]
    created = []

    class FakeAgent:
        def __init__(self, outcome):
            self.outcome = outcome

        def __call__(self, _question):
            if isinstance(self.outcome, Exception):
                raise self.outcome
            return self.outcome

    def fake_new_agent():
        instance = FakeAgent(outcomes[len(created)])
        created.append(instance)
        return instance

    monkeypatch.setattr(agent_concierge, "_new_agent", fake_new_agent)
    agent_concierge._ctx.set({"trace_id": "retry-tool-use"})

    assert agent_concierge._invoke_agent("pergunta") == "resposta recuperada"
    assert len(created) == 3


def test_tool_use_retry_discards_retrieval_from_failed_attempt(monkeypatch):
    calls = 0

    class FakeAgent:
        def __call__(self, _question):
            nonlocal calls
            calls += 1
            if calls == 1:
                agent_concierge._ctx_get()["last_retrieve"] = {
                    "decision": "responder",
                    "results": [{"source_path": "fonte-da-tentativa-falha.md"}],
                }
                raise RuntimeError(
                    "modelStreamErrorException: invalid sequence as part of ToolUse"
                )
            return "resposta sem nova consulta"

    monkeypatch.setattr(agent_concierge, "_new_agent", FakeAgent)
    agent_concierge._ctx.set({"trace_id": "retry-sem-fonte", "last_retrieve": None})

    assert agent_concierge._invoke_agent("pergunta") == "resposta sem nova consulta"
    assert agent_concierge._ctx_get()["last_retrieve"] is None


def test_run_rejects_non_text_question_without_invoking_model(monkeypatch):
    monkeypatch.setattr(
        agent_concierge,
        "_invoke_agent",
        lambda _question: pytest.fail("o modelo não deveria ser invocado"),
    )

    result = agent_concierge.run({"question": 123, "trace_id": "tipo-invalido"})

    assert result["decision"] == "nao_sei"
    assert result["answer"] == "Pergunta inválida."


def test_run_rejects_oversized_question_without_invoking_model(monkeypatch):
    monkeypatch.setattr(
        agent_concierge,
        "_invoke_agent",
        lambda _question: pytest.fail("o modelo não deveria ser invocado"),
    )

    result = agent_concierge.run({
        "question": "x" * (agent_concierge.MAX_QUESTION_LENGTH + 1),
        "trace_id": "pergunta-grande",
    })

    assert result["decision"] == "nao_sei"
    assert "excede o limite" in result["answer"]


class _FakeAgentCoreClient:
    def __init__(self, payload: bytes):
        self.payload = payload
        self.calls = 0

    def invoke_agent_runtime(self, **_kwargs):
        self.calls += 1
        return {"response": io.BytesIO(self.payload)}


def test_gateway_rejects_non_text_question(monkeypatch):
    client = _FakeAgentCoreClient(b"{}")
    monkeypatch.setattr(lambda_gateway, "_client", client)
    monkeypatch.setattr(lambda_gateway, "_AGENT_RUNTIME_ARN", "arn:test")

    response = lambda_gateway.handler(
        {"body": json.dumps({"question": 123, "trace_id": "tipo-invalido"})},
        None,
    )

    assert response["statusCode"] == 400
    assert json.loads(response["body"])["reason"] == "pergunta_invalida"
    assert client.calls == 0


def test_gateway_rejects_oversized_question(monkeypatch):
    client = _FakeAgentCoreClient(b"{}")
    monkeypatch.setattr(lambda_gateway, "_client", client)
    monkeypatch.setattr(lambda_gateway, "_AGENT_RUNTIME_ARN", "arn:test")

    response = lambda_gateway.handler(
        {"body": json.dumps({
            "question": "x" * (lambda_gateway.MAX_QUESTION_LENGTH + 1),
            "trace_id": "pergunta-grande",
        })},
        None,
    )

    assert response["statusCode"] == 413
    assert json.loads(response["body"])["reason"] == "pergunta_muito_longa"
    assert client.calls == 0


def test_gateway_rejects_malformed_runtime_payload(monkeypatch):
    monkeypatch.setattr(lambda_gateway, "_client", _FakeAgentCoreClient(b"not-json"))
    monkeypatch.setattr(lambda_gateway, "_AGENT_RUNTIME_ARN", "arn:test")

    response = lambda_gateway.handler(
        {"body": json.dumps({"question": "teste", "trace_id": "runtime-invalido"})},
        None,
    )

    assert response["statusCode"] == 502
    assert json.loads(response["body"])["reason"] == "erro_runtime"


def test_gateway_keeps_canonical_trace_id(monkeypatch):
    runtime_payload = json.dumps({
        "decision": "nao_sei",
        "trace_id": "trace-trocado-pelo-runtime",
        "answer": "Não encontrei.",
        "source_path": None,
    }).encode("utf-8")
    monkeypatch.setattr(
        lambda_gateway, "_client", _FakeAgentCoreClient(runtime_payload)
    )
    monkeypatch.setattr(lambda_gateway, "_AGENT_RUNTIME_ARN", "arn:test")

    response = lambda_gateway.handler(
        {"body": json.dumps({"question": "teste", "trace_id": "trace-borda"})},
        None,
    )

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["trace_id"] == "trace-borda"


def test_non_tool_use_error_is_not_retried(monkeypatch):
    calls = 0

    class FailingAgent:
        def __call__(self, _question):
            raise RuntimeError("access denied")

    def fake_new_agent():
        nonlocal calls
        calls += 1
        return FailingAgent()

    monkeypatch.setattr(agent_concierge, "_new_agent", fake_new_agent)

    with pytest.raises(RuntimeError, match="access denied"):
        agent_concierge._invoke_agent("pergunta")

    assert calls == 1


def test_unclosed_thinking_block_is_not_exposed():
    assert agent_concierge._clean_answer(
        "<thinking>raciocínio interno que foi truncado"
    ) == ""


def test_ungrounded_model_text_is_replaced_by_safe_answer():
    response = agent_concierge._build_response(
        "sem-fonte",
        "A resposta inventada seria 42.",
        {"last_retrieve": {"decision": "nao_sei", "results": []}},
    )

    assert response.decision == "nao_sei"
    assert "42" not in response.answer
    assert "base oficial" in response.answer


def test_grounded_answer_includes_source_and_requires_text():
    context = {
        "last_retrieve": {
            "decision": "responder",
            "results": [{"source_path": "data/corpus/faq/faq_geral.md"}],
        }
    }

    grounded = agent_concierge._build_response(
        "com-fonte", "Resposta fundamentada.", context
    )
    empty = agent_concierge._build_response("sem-texto", "   ", context)

    assert grounded.decision == "responder"
    assert grounded.source_path == "data/corpus/faq/faq_geral.md"
    assert "data/corpus/faq/faq_geral.md" in grounded.answer
    assert empty.decision == "nao_sei"


def test_audit_event_masks_personal_data(capsys):
    response = agent_concierge.ConciergeResponse(
        "nao_sei", "trace-seguro", "Não encontrei a informação."
    )

    agent_concierge._emit_audit(
        "Meu CPF é 123.456.789-01 e meu e-mail é cliente@example.com",
        response,
        {"last_retrieve": None},
    )

    event = json.loads(capsys.readouterr().err)
    assert "123.456.789-01" not in event["question"]
    assert "cliente@example.com" not in event["question"]
    assert "[CPF_MASCARADO]" in event["question"]
    assert "[EMAIL_MASCARADO]" in event["question"]


def test_trace_id_is_safe_and_fits_agentcore_session():
    trace_id = normalize_trace_id(" cliente\r\nX-Injected: sim " + "x" * 200)
    session_id = lambda_gateway._session_id(trace_id)

    assert "\r" not in trace_id and "\n" not in trace_id
    assert len(trace_id) <= 95
    assert 33 <= len(session_id) <= 128


def test_redact_pii_masks_phone_and_card():
    redacted = redact_pii(
        "Retorne em (83) 99999-8888; cartão 4111 1111 1111 1111."
    )

    assert "99999-8888" not in redacted
    assert "4111 1111 1111 1111" not in redacted
    assert "[TELEFONE_MASCARADO]" in redacted
    assert "[CARTAO_MASCARADO]" in redacted


def test_agentcore_runtime_disables_genai_content_capture():
    project_root = Path(__file__).resolve().parents[2]
    runtime = json.loads(
        (project_root / "infra/agentcore/runtime.json").read_text(encoding="utf-8")
    )
    environment = runtime["environmentVariables"]

    assert environment["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] == (
        "NO_CONTENT"
    )
    assert environment["OTEL_INSTRUMENTATION_GENAI_EMIT_EVENT"] == "false"
