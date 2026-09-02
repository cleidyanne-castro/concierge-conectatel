from pathlib import Path

from src.parte_05_governanca.log_retention import configure_retention


class FakePaginator:
    def paginate(self, **kwargs):
        assert kwargs["logGroupNamePrefix"].startswith("/aws/bedrock-agentcore/")
        return [
            {
                "logGroups": [
                    {
                        "logGroupName": (
                            "/aws/bedrock-agentcore/runtimes/"
                            "concierge_conectatel_agent-test-DEFAULT"
                        )
                    }
                ]
            }
        ]


class FakeLogsClient:
    def __init__(self):
        self.calls = []

    def get_paginator(self, operation):
        assert operation == "describe_log_groups"
        return FakePaginator()

    def put_retention_policy(self, **kwargs):
        self.calls.append(kwargs)


def test_configure_retention_includes_lambdas_and_agentcore():
    client = FakeLogsClient()

    result = configure_retention(days=14, client=client)

    assert len(result) == 4
    assert all(item["retention_days"] == 14 for item in result)
    assert client.calls[-1]["logGroupName"].startswith("/aws/bedrock-agentcore/")


def test_configure_retention_deduplicates_explicit_groups():
    client = FakeLogsClient()

    configure_retention(
        days=7,
        log_groups=["/aws/lambda/example", "/aws/lambda/example"],
        client=client,
    )

    assert client.calls == [
        {"logGroupName": "/aws/lambda/example", "retentionInDays": 7}
    ]


def test_gateway_metric_filters_use_managed_log_group():
    project_root = Path(__file__).resolve().parents[2]
    template = (project_root / "infra/template.yaml").read_text(encoding="utf-8")

    assert "GatewayApplicationLogGroup:" in template
    assert "LogGroup: !Ref GatewayApplicationLogGroup" in template
    assert template.count("LogGroupName: !Ref GatewayApplicationLogGroup") == 4
