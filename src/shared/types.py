"""Tipos compartilhados entre as partes do Concierge.

Vocabulário único para as estruturas que cruzam a fronteira Parte 2 → 3 → 4 → 5.
Espelha os contratos já documentados em `docs/` e o retorno real de
`src/tools/retrieve_kb/retrieval.py`. Sem lógica: apenas forma de dados.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict

# Decisão final exposta na saída (README seção 5).
Decision = Literal["responder", "nao_sei", "escalar"]


class RetrievedChunk(TypedDict, total=False):
    """Um resultado de `retrieve_kb`."""

    chunk_id: str
    score: float
    doc_family_id: str
    section_title: str | None
    source_path: str
    status: str
    text: str | None


class RetrieveResult(TypedDict, total=False):
    """Retorno da tool `retrieve_kb` (a decisão responder/nao_sei já vem pronta)."""

    decision: Literal["responder", "nao_sei"]
    trace_id: str
    results: list[RetrievedChunk]
    threshold_used: float
    latency_ms: int
    reason: str


Urgencia = Literal["baixa", "media", "alta"]


@dataclass
class Escalation:
    """Resultado do guardrail de triagem (Parte 4).

    `criterio` é 1..8 conforme a Política de Suporte e Escalonamento.
    """

    criterio: int
    categoria_motivo: str
    urgencia: Urgencia
    motivo_detectado: str = ""


@dataclass
class HandoffRecord:
    """Os 10 campos mínimos de um escalonamento (Política de Suporte).

    Nomes idênticos aos da tabela em
    `data/corpus/politicas/politica_suporte_escalonamento.md`. Critério de
    qualidade: o atendente humano continua sem pedir ao cliente para repetir
    nada. Gravado pela tool `store_handoff` no DynamoDB.
    """

    protocolo_atendimento: str
    data_hora_abertura: str
    canal_origem: str
    categoria_motivo: str
    resumo_caso: str
    historico_ja_levantado: str
    produto_servico_envolvido: str
    documento_fonte_consultado: str
    urgencia: Urgencia
    dados_contato_retorno: str
    trace_id: str = ""

    def to_item(self) -> dict[str, Any]:
        """Formato serializável para persistência/log."""
        return {k: v for k, v in self.__dict__.items()}


@dataclass
class ConciergeResponse:
    """Resposta final do orquestrador para o API Gateway / CLI."""

    decision: Decision
    trace_id: str
    answer: str
    source_path: str | None = None
    handoff: HandoffRecord | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "decision": self.decision,
            "trace_id": self.trace_id,
            "answer": self.answer,
            "source_path": self.source_path,
        }
        if self.handoff is not None:
            data["handoff"] = self.handoff.to_item()
        return data


@dataclass
class AuditEvent:
    """Registro estruturado emitido para o CloudWatch a cada interação."""

    trace_id: str
    question: str
    decision: Decision
    sources: list[str] = field(default_factory=list)
    top_score: float | None = None
    guardrail: str | None = None

    def to_log(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "question": self.question,
            "decision": self.decision,
            "sources": self.sources,
            "top_score": self.top_score,
            "guardrail": self.guardrail,
        }
