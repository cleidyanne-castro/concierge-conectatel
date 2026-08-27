"""Parte 5 - trilha de auditoria consultável por trace_id."""
from datetime import datetime, timezone
import json
import uuid
from pathlib import Path

def create_trace_id() -> str:
    return uuid.uuid4().hex[:12]

def append_audit(path: str, *, trace_id: str, question: str, sources: list[str], decision: str, guardrail: str | None = None) -> None:
    record = {"trace_id": trace_id, "timestamp": datetime.now(timezone.utc).isoformat(), "question": question, "sources": sources, "decision": decision, "guardrail": guardrail}
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as stream: stream.write(json.dumps(record, ensure_ascii=False) + "\n")

def find_by_trace_id(path: str, trace_id: str) -> dict | None:
    target=Path(path)
    if not target.exists(): return None
    for line in target.read_text(encoding='utf-8').splitlines():
        record=json.loads(line)
        if record.get('trace_id') == trace_id: return record
    return None
