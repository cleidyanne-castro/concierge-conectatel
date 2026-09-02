"""Sanitização compartilhada de identificadores e dados sensíveis."""

from __future__ import annotations

import re
import uuid


_CPF_RE = re.compile(r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)")
_CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
_EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
_PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?55[ -]?)?(?:\(?\d{2}\)?[ -]?)?\d{4,5}[ -]?\d{4}(?!\d)"
)
_UNSAFE_TRACE_CHARS_RE = re.compile(r"[^A-Za-z0-9]+")


def redact_pii(text: str) -> str:
    """Mascara identificadores pessoais comuns antes de emitir logs."""

    value = str(text or "")
    value = _CPF_RE.sub("[CPF_MASCARADO]", value)
    value = _CARD_RE.sub("[CARTAO_MASCARADO]", value)
    value = _EMAIL_RE.sub("[EMAIL_MASCARADO]", value)
    return _PHONE_RE.sub("[TELEFONE_MASCARADO]", value)


def normalize_trace_id(value: str | None, *, max_length: int = 95) -> str:
    """Produz um identificador seguro para logs, headers e sessões AgentCore.

    O limite padrão deixa espaço para ``-`` e um UUID de 32 caracteres no
    ``runtimeSessionId``, cujo máximo no AgentCore é 128 caracteres.
    """

    normalized = _UNSAFE_TRACE_CHARS_RE.sub("-", str(value or "")).strip("-")
    if not normalized:
        normalized = str(uuid.uuid4())
    return normalized[:max_length].rstrip("-") or str(uuid.uuid4())
