import io
import json
from urllib.error import HTTPError

import pytest

from src.interface import service
from src.interface.service import ConciergeApiError, invoke_concierge, invoke_retrieve_kb


class FakeLambdaClient:
    def __init__(self, body, *, function_error=None):
        self.body = body
        self.function_error = function_error
        self.kwargs = None

    def invoke(self, **kwargs):
        self.kwargs = kwargs
        response = {"Payload": io.BytesIO(json.dumps(self.body).encode("utf-8"))}
        if self.function_error:
            response["FunctionError"] = self.function_error
        return response


def test_invoke_retrieve_kb_sends_question_and_trace_id():
    client = FakeLambdaClient({"decision": "responder", "trace_id": "ui-001"})

    result = invoke_retrieve_kb("Como consulto meu consumo?", "ui-001", client=client)

    assert result["decision"] == "responder"
    assert client.kwargs["FunctionName"] == "concierge-conectatel-retrieve-kb"
    assert json.loads(client.kwargs["Payload"]) == {
        "question": "Como consulto meu consumo?",
        "trace_id": "ui-001",
    }


def test_invoke_retrieve_kb_requires_question():
    with pytest.raises(ValueError, match="pergunta"):
        invoke_retrieve_kb("   ", client=FakeLambdaClient({}))


def test_invoke_retrieve_kb_exposes_lambda_error_safely():
    client = FakeLambdaClient({"errorMessage": "erro interno"}, function_error="Unhandled")

    with pytest.raises(RuntimeError, match="erro interno"):
        invoke_retrieve_kb("pergunta", client=client)


def test_invoke_concierge_sends_question_and_trace_id():
    calls = []

    def fake_post(url, payload):
        calls.append((url, payload))
        return {"decision": "responder", "trace_id": "ui-agent-001"}

    result = invoke_concierge(
        "Como consulto meu consumo?",
        "ui-agent-001",
        api_url="https://example.execute-api.amazonaws.com/concierge",
        post_json=fake_post,
    )

    assert result["decision"] == "responder"
    assert calls == [
        (
            "https://example.execute-api.amazonaws.com/concierge",
            {"question": "Como consulto meu consumo?", "trace_id": "ui-agent-001"},
        )
    ]


def test_invoke_concierge_requires_api_url():
    with pytest.raises(ValueError, match="URL do Concierge"):
        invoke_concierge("pergunta", api_url="", post_json=lambda *_: {})


def test_invoke_concierge_preserves_structured_api_error():
    expected = ConciergeApiError(
        502,
        {"trace_id": "ui-falha-001", "reason": "erro_runtime"},
        "A API do Concierge retornou erro: tente novamente.",
    )

    def failing_post(*_):
        raise expected

    with pytest.raises(ConciergeApiError) as captured:
        invoke_concierge("pergunta", "ui-falha-001", api_url="https://example.com", post_json=failing_post)

    assert captured.value.status_code == 502
    assert captured.value.payload["trace_id"] == "ui-falha-001"


def test_post_json_preserves_payload_from_http_error(monkeypatch):
    payload = {"trace_id": "ui-http-502", "reason": "erro_runtime"}
    http_error = HTTPError(
        "https://example.com/concierge",
        502,
        "Bad Gateway",
        {},
        io.BytesIO(json.dumps(payload).encode("utf-8")),
    )

    def raise_http_error(*_args, **_kwargs):
        raise http_error

    monkeypatch.setattr(service, "urlopen", raise_http_error)

    with pytest.raises(ConciergeApiError) as captured:
        service._post_json("https://example.com/concierge", {"question": "teste"})

    assert captured.value.status_code == 502
    assert captured.value.payload == payload


def test_post_json_rejects_non_http_url():
    with pytest.raises(ValueError, match="HTTP ou HTTPS"):
        service._post_json("file:///tmp/resposta.json", {"question": "teste"})


def test_post_json_normalizes_invalid_unicode_response(monkeypatch):
    class InvalidResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return b"\xff"

    monkeypatch.setattr(service, "urlopen", lambda *_args, **_kwargs: InvalidResponse())

    with pytest.raises(RuntimeError, match="JSON inválido"):
        service._post_json("https://example.com/concierge", {"question": "teste"})


def test_post_json_normalizes_timeout(monkeypatch):
    monkeypatch.setattr(
        service,
        "urlopen",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(TimeoutError()),
    )

    with pytest.raises(RuntimeError, match="conectar"):
        service._post_json("https://example.com/concierge", {"question": "teste"})
