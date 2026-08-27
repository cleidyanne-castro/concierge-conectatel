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
