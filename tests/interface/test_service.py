import io
import json

import pytest

from src.interface.service import invoke_retrieve_kb


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
