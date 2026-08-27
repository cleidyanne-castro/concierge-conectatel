from src.shared.types import DocumentChunk
from src.parte_02_rag.rag_index import filter_current

def test_only_current_versions_are_retrievable():
    chunks = [
        DocumentChunk("old", "policy-v1", "policy", 1, "revogado"),
        DocumentChunk("current", "policy-v2", "policy", 2, "vigente"),
    ]
    assert [c.source for c in filter_current(chunks)] == ["policy-v2"]
