"""Parte 3 - agente Concierge: grounding, fonte e decisão segura de não sei."""
from ..shared.config import Settings
from ..shared.types import DocumentChunk
from ..parte_02_rag.rag_index import filter_current

def retrieve(question: str, chunks: list[DocumentChunk], threshold: float | None = None):
    """Implementar busca após filter_current; retornar evidência e score."""
    current = filter_current(chunks)
    return current, 0.0

def answer_or_decline(question: str, chunks: list[DocumentChunk], settings: Settings):
    """Não chamar o modelo quando o melhor score estiver abaixo do limiar calibrado."""
    evidence, score = retrieve(question, chunks, settings.retrieval_score_threshold)
    if score < settings.retrieval_score_threshold:
        return {"decision": "nao_sei", "answer": "Não sei com base no corpus fornecido.", "sources": []}
    return {"decision": "responder", "answer": "[gerar resposta grounded]", "sources": [x.source for x in evidence]}
