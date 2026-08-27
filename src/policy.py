"""Política mínima de escalonamento; ajustar ao corpus oficial."""
DEFAULT_ESCALATION_TERMS=('fraude','golpe','não reconheço','sem sinal','não funciona','cancelar contrato','urgente')

def should_escalate(question: str, terms=DEFAULT_ESCALATION_TERMS) -> bool:
    if terms is None: terms=DEFAULT_ESCALATION_TERMS
    q=question.lower()
    return any(term in q for term in terms)
