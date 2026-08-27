"""Handler ponta a ponta para Lambda ou execução local."""
from .audit import append_audit, create_trace_id
from .config import Settings
from .escalation import build_handoff
from .policy import should_escalate
from .vector_store import search

def handle(question: str, settings: Settings, *, bedrock=None) -> dict:
    trace_id=create_trace_id(); matches=search(question, settings.vector_store_path)
    best_score=matches[0][0] if matches else 0.0
    sources=[chunk.source for score,chunk in matches]
    if should_escalate(question):
        decision='escalar'; result={'trace_id':trace_id,'decision':decision,'handoff':build_handoff(question,[], 'alta' if 'urg' in question.lower() else 'média','política de suporte'),'sources':sources}
    elif best_score < settings.retrieval_score_threshold:
        decision='nao_sei'; result={'trace_id':trace_id,'decision':decision,'answer':'Não sei com base no corpus fornecido.','sources':[]}
    else:
        context='\n'.join(chunk.text for score,chunk in matches[:3])
        answer=bedrock.generate(question,context) if bedrock else '[resposta grounded pendente de Bedrock]'
        decision='responder'; result={'trace_id':trace_id,'decision':decision,'answer':answer,'sources':sources[:3]}
    append_audit(settings.audit_log_path, trace_id=trace_id, question=question, sources=result.get('sources',[]), decision=decision)
    return result

