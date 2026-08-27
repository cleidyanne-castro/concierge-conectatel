"""Parte 4 - triagem e escalonamento conforme a política do corpus."""
def should_escalate(question: str, policy: dict) -> bool:
    from .policy import should_escalate as evaluate
    return evaluate(question, (policy or {}).get('terms'))

def build_handoff(question: str, checks: list[str], urgency: str, reason: str) -> dict:
    return {"problem_reported": question, "checks_already_done": checks, "urgency": urgency, "escalation_reason": reason}
