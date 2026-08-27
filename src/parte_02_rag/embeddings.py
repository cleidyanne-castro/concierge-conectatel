"""Embedding local determinístico para smoke tests; trocar por Bedrock na integração."""
import hashlib
import math
import re

def embed(text: str, dimensions: int = 256) -> list[float]:
    vector = [0.0] * dimensions
    for token in re.findall(r'[\wáéíóúãõç]+', text.lower()):
        idx = int(hashlib.sha256(token.encode()).hexdigest(), 16) % dimensions
        vector[idx] += 1.0
    norm = math.sqrt(sum(x*x for x in vector)) or 1.0
    return [x / norm for x in vector]

def cosine(a: list[float], b: list[float]) -> float:
    return sum(x*y for x,y in zip(a,b))

