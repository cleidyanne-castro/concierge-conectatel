"""Leitura e chunking do corpus documental."""
from pathlib import Path
from ..shared.types import DocumentChunk

def load_corpus(corpus_dir: str | Path) -> list[DocumentChunk]:
    chunks = []
    for path in sorted(Path(corpus_dir).glob('**/*')):
        if path.suffix.lower() not in {'.txt', '.md'}:
            continue
        text = path.read_text(encoding='utf-8')
        family = path.stem.split('__')[0]
        status = 'revogado' if 'revog' in path.stem.lower() else 'vigente'
        for ordinal, start in enumerate(range(0, len(text), 800), start=1):
            chunks.append(DocumentChunk(text=text[start:start+800], source=path.name, doc_family_id=family, version_ordinal=ordinal, status=status))
    return chunks
