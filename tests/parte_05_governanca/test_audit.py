from datetime import datetime, timezone

import pytest
from botocore.exceptions import ClientError, NoCredentialsError

from src.parte_05_governanca.audit import AuditQueryError, find_by_trace_id


class FakeLogsClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.start_args = None

    def start_query(self, **kwargs):
        self.start_args = kwargs
        return {"queryId": "query-123"}

    def get_query_results(self, *, queryId):
        assert queryId == "query-123"
        return next(self.responses)


def test_find_by_trace_id_returns_structured_rows():
    client = FakeLogsClient(
        [
            {"status": "Running"},
            {
                "status": "Complete",
                "results": [
                    [
                        {"field": "@timestamp", "value": "2026-08-31T13:00:00Z"},
                        {"field": "trace_id", "value": "trace-001"},
                        {"field": "decision", "value": "responder"},
                    ]
                ],
            },
        ]
    )

    rows = find_by_trace_id(
        "trace-001",
        log_group_names=["/aws/lambda/concierge-conectatel-retrieve-kb"],
        start_time=datetime(2026, 8, 31, tzinfo=timezone.utc),
        end_time=datetime(2026, 8, 31, 1, tzinfo=timezone.utc),
        poll_interval_seconds=0,
        client=client,
    )

    assert rows == [
        {
            "@timestamp": "2026-08-31T13:00:00Z",
            "trace_id": "trace-001",
            "decision": "responder",
        }
    ]
    assert client.start_args["logGroupNames"] == [
        "/aws/lambda/concierge-conectatel-retrieve-kb"
    ]
    assert "trace\\-001" in client.start_args["queryString"]


def test_find_by_trace_id_rejects_empty_trace_id():
    with pytest.raises(ValueError, match="trace_id"):
        find_by_trace_id("", client=FakeLogsClient([]))


def test_find_by_trace_id_escapes_logs_insights_regex_delimiter():
    client = FakeLogsClient([{"status": "Complete", "results": []}])

    find_by_trace_id(
        "trace/.*",
        log_group_names="/aws/lambda/teste",
        poll_interval_seconds=0,
        client=client,
    )

    query = client.start_args["queryString"]
    assert r"trace\/\.\*" in query


def test_find_by_trace_id_rejects_control_characters():
    with pytest.raises(ValueError, match="controle"):
        find_by_trace_id("trace\n| limit 1", client=FakeLogsClient([]))


def test_find_by_trace_id_raises_when_logs_query_fails():
    client = FakeLogsClient([{"status": "Failed"}])

    with pytest.raises(AuditQueryError, match="Failed"):
        find_by_trace_id(
            "trace-001",
            log_group_names="/aws/lambda/concierge-conectatel-retrieve-kb",
            poll_interval_seconds=0,
            client=client,
        )


def test_find_by_trace_id_explains_credential_failure():
    class CredentialsExpiredClient:
        def start_query(self, **kwargs):
            raise NoCredentialsError()

    with pytest.raises(AuditQueryError, match="aws sso login"):
        find_by_trace_id(
            "trace-001",
            log_group_names="/aws/lambda/concierge-conectatel-retrieve-kb",
            client=CredentialsExpiredClient(),
        )


def test_find_by_trace_id_identifies_missing_log_group():
    class MissingLogGroupClient:
        def start_query(self, **kwargs):
            raise ClientError(
                {
                    "Error": {
                        "Code": "ResourceNotFoundException",
                        "Message": "missing",
                    }
                },
                "StartQuery",
            )

    with pytest.raises(AuditQueryError, match="não existem"):
        find_by_trace_id(
            "trace-001",
            log_group_names="/aws/log-group/inexistente",
            client=MissingLogGroupClient(),
        )
