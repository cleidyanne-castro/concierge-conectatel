"""Aplica retenção explícita aos log groups operacionais do Concierge."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from typing import Any

import boto3


DEFAULT_LOG_GROUPS = (
    "/concierge-conectatel/lambda/gateway",
    "/aws/lambda/concierge-conectatel-retrieve-kb",
    "/aws/lambda/concierge-conectatel-store-handoff",
)
AGENTCORE_PREFIX = "/aws/bedrock-agentcore/runtimes/concierge_conectatel_agent-"


def _agentcore_log_groups(client: Any) -> list[str]:
    groups: list[str] = []
    paginator = client.get_paginator("describe_log_groups")
    for page in paginator.paginate(logGroupNamePrefix=AGENTCORE_PREFIX):
        groups.extend(
            item["logGroupName"]
            for item in page.get("logGroups", [])
            if item.get("logGroupName")
        )
    return groups


def configure_retention(
    *,
    days: int = 14,
    log_groups: Iterable[str] | None = None,
    client: Any | None = None,
) -> list[dict[str, int | str]]:
    """Configura retenção idempotente e devolve os grupos processados."""

    if days <= 0:
        raise ValueError("days deve ser maior que zero.")
    logs = client or boto3.client("logs")
    groups = list(log_groups or (*DEFAULT_LOG_GROUPS, *_agentcore_log_groups(logs)))
    groups = list(dict.fromkeys(group.strip() for group in groups if group.strip()))
    if not groups:
        raise ValueError("Nenhum log group foi encontrado para configurar.")

    configured = []
    for group in groups:
        logs.put_retention_policy(logGroupName=group, retentionInDays=days)
        configured.append({"log_group": group, "retention_days": days})
    return configured


def main() -> None:
    parser = argparse.ArgumentParser(description="Configura retenção do CloudWatch")
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--log-group", action="append", dest="log_groups")
    args = parser.parse_args()
    result = configure_retention(days=args.days, log_groups=args.log_groups)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
