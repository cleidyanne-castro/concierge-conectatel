"""Índice vetorial simples e persistível em JSON para o MVP local."""
import json
from pathlib import Path
from .embeddings import embed, cosine
from .rag_index import DocumentChunk, filter_current

def build_index(chunks: list[DocumentChunk], path: str | Path) -> None:
    target=Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    payload={'chunks':[c.__dict__ | {'embedding': embed(c.text)} for c in chunks]}
    target.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')

def search(question: str, path: str | Path, top_k: int = 5, current_only: bool = True):
    payload=json.loads(Path(path).read_text(encoding='utf-8'))
    chunks=[DocumentChunk(**{k:v for k,v in item.items() if k!='embedding'}) for item in payload['chunks']]
    vectors=[item['embedding'] for item in payload['chunks']]
    # Requisito do desafio: vigência é filtrada antes do score.
    allowed=filter_current(chunks) if current_only else chunks
    allowed_sources={id(c): c.source for c in allowed}
    q=embed(question); scored=[]
    for c,v in zip(chunks,vectors):
        if c.source not in {x.source for x in allowed}: continue
        scored.append((cosine(q,v),c))
    return sorted(scored,key=lambda x:x[0],reverse=True)[:top_k]

