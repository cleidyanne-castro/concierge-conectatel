from src.escalation import build_handoff
from src.policy import should_escalate

def test_handoff_contains_continuation_context():
    handoff = build_handoff("sem sinal", ["reinício do modem"], "alta", "incidente técnico")
    assert set(["problem_reported", "checks_already_done", "urgency"]).issubset(handoff)
    assert should_escalate('Suspeito de golpe')
