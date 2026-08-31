"""Configuração e tipos compartilhados entre as partes do Concierge."""

from __future__ import annotations

from .config import Settings, get_settings
from .types import (
    AuditEvent,
    ConciergeResponse,
    Decision,
    Escalation,
    HandoffRecord,
    RetrievedChunk,
    RetrieveResult,
    Urgencia,
)

__all__ = [
    "Settings",
    "get_settings",
    "AuditEvent",
    "ConciergeResponse",
    "Decision",
    "Escalation",
    "HandoffRecord",
    "RetrievedChunk",
    "RetrieveResult",
    "Urgencia",
]
