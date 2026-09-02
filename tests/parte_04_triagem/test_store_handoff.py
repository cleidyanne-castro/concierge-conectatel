from __future__ import annotations

from botocore.exceptions import ClientError

from src.parte_03_04_agente_triagem import store_handoff_lambda


def valid_event() -> dict:
    return {
        "trace_id": "trace-handoff-001",
        "protocolo_atendimento": "CONCTL-20260901-ABC123",
        "data_hora_abertura": "2026-09-01T20:00:00+00:00",
        "canal_origem": "chat",
        "categoria_motivo": "Suspeita de fraude",
        "resumo_caso": "Cliente relata uso indevido da linha.",
        "historico_ja_levantado": "Cliente confirmou que nao reconhece a troca.",
        "produto_servico_envolvido": "Linha movel",
        "documento_fonte_consultado": "data/corpus/politicas/politica_suporte_escalonamento.md",
        "urgencia": "alta",
        "dados_contato_retorno": "Retorno pelo chat cadastrado",
    }


class FakeTable:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def put_item(self, **kwargs) -> None:
        self.items.append(kwargs)


def test_persists_complete_handoff(monkeypatch):
    table = FakeTable()
    monkeypatch.setattr(store_handoff_lambda, "_table", lambda: table)

    result = store_handoff_lambda.handler(valid_event(), None)

    assert result == {"stored": True, "protocolo": "CONCTL-20260901-ABC123"}
    assert table.items[0]["Item"]["trace_id"] == "trace-handoff-001"
    assert table.items[0]["ConditionExpression"] == "attribute_not_exists(trace_id)"


def test_rejects_handoff_with_required_data_missing(monkeypatch):
    monkeypatch.setattr(store_handoff_lambda, "_table", lambda: FakeTable())
    event = valid_event()
    event["resumo_caso"] = ""

    result = store_handoff_lambda.handler(event, None)

    assert result["stored"] is False
    assert result["reason"] == "campos_obrigatorios_ausentes"
    assert "resumo_caso" in result["fields"]


def test_duplicate_trace_does_not_claim_new_protocol(monkeypatch):
    class DuplicateTable:
        def put_item(self, **kwargs) -> None:
            raise ClientError(
                {"Error": {"Code": "ConditionalCheckFailedException", "Message": "duplicate"}},
                "PutItem",
            )

    monkeypatch.setattr(store_handoff_lambda, "_table", DuplicateTable)

    result = store_handoff_lambda.handler(valid_event(), None)

    assert result == {
        "stored": False,
        "duplicate": True,
        "reason": "trace_id_duplicado",
    }


def test_rejects_unknown_urgency(monkeypatch):
    monkeypatch.setattr(store_handoff_lambda, "_table", lambda: FakeTable())
    event = valid_event()
    event["urgencia"] = "imediata"

    result = store_handoff_lambda.handler(event, None)

    assert result["stored"] is False
    assert "urgencia_invalida" in result["fields"]
