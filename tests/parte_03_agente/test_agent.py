from __future__ import annotations

import json
from pathlib import Path

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


def test_bedrock_model_uses_stable_nova_tool_parameters():
    config = agent_concierge.bedrock_model.config

    assert config["temperature"] == 0
    assert config["max_tokens"] == 3000
    assert config["additional_request_fields"] == {"inferenceConfig": {"topK": 1}}


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
