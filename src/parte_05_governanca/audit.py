"""Consulta da trilha de auditoria no CloudWatch Logs Insights.

O agente e as Lambdas escrevem eventos JSON que carregam o mesmo ``trace_id``.
Este módulo não persiste uma segunda cópia desses dados: ele reúne a trilha
existente para auditoria e demonstração, dentro do SLA de 60 segundos.
"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from src.shared.config import get_settings


DEFAULT_LOOKBACK = timedelta(hours=1)
DEFAULT_TIMEOUT_SECONDS = 55
DEFAULT_POLL_INTERVAL_SECONDS = 1.0


class AuditQueryError(RuntimeError):
    """Falha ao executar ou concluir uma consulta de auditoria."""


def _as_log_groups(value: str | Iterable[str] | None) -> list[str]:
    """Normaliza um ou mais log groups, rejeitando uma consulta sem destino."""

    if value is None:
        value = get_settings().audit_log_group

    groups = [value] if isinstance(value, str) else list(value)
    groups = [group.strip() for group in groups if group and group.strip()]
    if not groups:
        raise ValueError("Informe ao menos um log group para a auditoria.")
    return groups


def _query_for(trace_id: str) -> str:
    """Monta a consulta sem permitir que um trace_id altere a expressão regex."""

    if any(ord(character) < 32 or ord(character) == 127 for character in trace_id):
        raise ValueError("trace_id não pode conter caracteres de controle.")
    # ``re.escape`` não protege a barra, delimitador da regex no Logs Insights.
    safe_trace_id = re.escape(trace_id).replace("/", r"\/")
    return "\n".join(
        [
            "fields @timestamp, @log, @logStream, @message",
            f"| filter @message like /{safe_trace_id}/",
            "| sort @timestamp asc",
        ]
    )


def _rows_to_dicts(rows: list[list[dict[str, str]]]) -> list[dict[str, str]]:
    """Converte a representação ``field/value`` da API em dicionários simples."""

    return [
        {item["field"]: item.get("value", "") for item in row if "field" in item}
        for row in rows
    ]


def find_by_trace_id(
    trace_id: str,
    *,
    log_group_names: str | Iterable[str] | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    poll_interval_seconds: float = DEFAULT_POLL_INTERVAL_SECONDS,
    client: Any | None = None,
) -> list[dict[str, str]]:
    """Retorna eventos CloudWatch associados a ``trace_id`` em ordem cronológica.

    A consulta usa Logs Insights de forma assíncrona e encerra antes de 60
    segundos por padrão, atendendo ao requisito de auditoria da entrega.
    ``client`` existe para testes unitários; em produção usa o cliente boto3.
    """

    if not trace_id or not trace_id.strip():
        raise ValueError("trace_id é obrigatório para a consulta de auditoria.")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds deve ser maior que zero.")

    end = end_time or datetime.now(timezone.utc)
    start = start_time or end - DEFAULT_LOOKBACK
    if start > end:
        raise ValueError("start_time não pode ser posterior a end_time.")

    logs = client or boto3.client("logs")
    try:
        query = logs.start_query(
            logGroupNames=_as_log_groups(log_group_names),
            startTime=int(start.timestamp()),
            endTime=int(end.timestamp()),
            queryString=_query_for(trace_id.strip()),
        )
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code")
        if code == "ResourceNotFoundException":
            groups = ", ".join(_as_log_groups(log_group_names))
            raise AuditQueryError(
                "Um ou mais log groups não existem no CloudWatch: " + groups
            ) from error
        raise AuditQueryError(
            "Não foi possível iniciar a consulta no CloudWatch. Confirme as "
            "credenciais, permissões logs:StartQuery e os log groups informados."
        ) from error
    except BotoCoreError as error:
        raise AuditQueryError(
            "Não foi possível iniciar a consulta no CloudWatch. Confirme as "
            "credenciais (por exemplo, `aws sso login --profile <perfil>`) e "
            "as permissões logs:StartQuery/logs:GetQueryResults."
        ) from error
    query_id = query["queryId"]
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        try:
            result = logs.get_query_results(queryId=query_id)
        except (BotoCoreError, ClientError) as error:
            raise AuditQueryError(
                "Não foi possível ler o resultado da consulta no CloudWatch. "
                "Verifique a sessão AWS e as permissões de Logs Insights."
            ) from error
        status = result.get("status")
        if status == "Complete":
            return _rows_to_dicts(result.get("results", []))
        if status in {"Failed", "Cancelled", "Timeout", "Unknown"}:
            raise AuditQueryError(f"Consulta de auditoria terminou com status: {status}.")
        time.sleep(poll_interval_seconds)

    raise AuditQueryError(
        f"Consulta de auditoria excedeu {timeout_seconds:g}s para trace_id={trace_id!r}."
    )


def main() -> None:
    """Consulta manual usada na demonstração e na coleta de evidências."""

    parser = argparse.ArgumentParser(description="Consulta CloudWatch por trace_id")
    parser.add_argument("--trace-id", required=True, help="Identificador da interação")
    parser.add_argument(
        "--log-group",
        action="append",
        dest="log_groups",
        help="Log group a consultar; repita a opção para consultar vários grupos.",
    )
    parser.add_argument(
        "--lookback-minutes",
        type=int,
        default=60,
        help="Janela retrospectiva da consulta (padrão: 60).",
    )
    args = parser.parse_args()
    if args.lookback_minutes <= 0:
        parser.error("--lookback-minutes deve ser maior que zero")

    end = datetime.now(timezone.utc)
    rows = find_by_trace_id(
        args.trace_id,
        log_group_names=args.log_groups,
        start_time=end - timedelta(minutes=args.lookback_minutes),
        end_time=end,
    )
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
