"""Parte 2 - chunking, metadados de vigência, embeddings e índice vetorial."""
from dataclasses import dataclass

@dataclass(frozen=True)
class DocumentChunk:
    text: str
    source: str
    doc_family_id: str
    version_ordinal: int
    status: str
    effective_from: str | None = None
    effective_to: str | None = None

def filter_current(chunks: list[DocumentChunk]) -> list[DocumentChunk]:
    """Filtro determinístico obrigatório antes do score de similaridade."""
    return [chunk for chunk in chunks if chunk.status.lower() == "vigente"]

def main() -> None:
    import argparse
    from .chunking import load_corpus
    from .vector_store import build_index
    parser=argparse.ArgumentParser(); parser.add_argument('--corpus',required=True); parser.add_argument('--output',required=True)
    args=parser.parse_args(); build_index(load_corpus(args.corpus), args.output)

if __name__ == '__main__': main()
