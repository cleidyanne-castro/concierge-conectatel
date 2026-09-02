import os
import json

import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLE_NAME", "concierge-conectatel-escalonamentos")

REQUIRED_FIELDS = (
    "trace_id",
    "protocolo_atendimento",
    "data_hora_abertura",
    "canal_origem",
    "categoria_motivo",
    "resumo_caso",
    "historico_ja_levantado",
    "produto_servico_envolvido",
    "documento_fonte_consultado",
    "urgencia",
    "dados_contato_retorno",
)
VALID_URGENCIES = {"baixa", "media", "alta"}


def _table():
    """Resolve a tabela sob demanda para facilitar teste e evitar efeito no import."""
    return boto3.resource("dynamodb").Table(TABLE_NAME)


def _response(*, stored: bool, protocolo: str | None = None, **extra) -> dict:
    payload = {"stored": stored, **extra}
    if protocolo:
        payload["protocolo"] = protocolo
    return payload


def _build_item(event: dict) -> tuple[dict | None, list[str]]:
    item = {
        "trace_id": event.get("trace_id"),
        "protocolo_atendimento": event.get("protocolo_atendimento"),
        "data_hora_abertura": event.get("data_hora_abertura"),
        "canal_origem": event.get("canal_origem", "chat"),
        "categoria_motivo": event.get("categoria_motivo"),
        "resumo_caso": event.get("resumo_caso"),
        "historico_ja_levantado": event.get("historico_ja_levantado"),
        "produto_servico_envolvido": event.get("produto_servico_envolvido"),
        "documento_fonte_consultado": event.get("documento_fonte_consultado"),
        "urgencia": event.get("urgencia", "media"),
        "dados_contato_retorno": event.get("dados_contato_retorno"),
    }
    missing = [field for field in REQUIRED_FIELDS if not str(item.get(field) or "").strip()]
    if item["urgencia"] not in VALID_URGENCIES:
        missing.append("urgencia_invalida")
    return item, missing


def handler(event, context):
    """
    Recebe os dados do HandoffRecord e persiste no DynamoDB.
    Chave primária: trace_id
    """
    event = event or {}
    item, missing = _build_item(event)
    if missing:
        print(json.dumps({
            "trace_id": item.get("trace_id"),
            "level": "ERROR",
            "event": "handoff_rejected",
            "missing_fields": missing,
        }))
        return _response(stored=False, reason="campos_obrigatorios_ausentes", fields=missing)

    try:
        _table().put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(trace_id)",
        )
        print(json.dumps({
            "trace_id": item["trace_id"],
            "event": "handoff_stored",
            "protocolo": item["protocolo_atendimento"],
        }))
        return _response(stored=True, protocolo=item["protocolo_atendimento"])
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code")
        if code == "ConditionalCheckFailedException":
            print(json.dumps({
                "trace_id": item["trace_id"],
                "event": "handoff_duplicate",
            }))
            return _response(
                stored=False,
                duplicate=True,
                reason="trace_id_duplicado",
            )
        print(json.dumps({
            "trace_id": item["trace_id"],
            "level": "ERROR",
            "event": "handoff_persistence_failed",
            "message": str(error),
        }))
        raise
