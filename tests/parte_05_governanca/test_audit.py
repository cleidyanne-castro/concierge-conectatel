import json
from src.parte_05_governanca.audit import append_audit, find_by_trace_id

def test_audit_record_is_locatable_by_trace_id(tmp_path):
    path = tmp_path / "audit.jsonl"
    append_audit(str(path), trace_id="abc123", question="q", sources=["faq"], decision="responder")
    record = json.loads(path.read_text(encoding="utf-8").strip())
    assert record["trace_id"] == "abc123"
    assert find_by_trace_id(str(path), "abc123")["decision"] == "responder"
