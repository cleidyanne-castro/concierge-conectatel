import hashlib
import json
from pathlib import Path

from sentence_transformers import SentenceTransformer


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CHUNKS_PATH = (
    PROJECT_ROOT
    / "artifacts"
    / "chunks"
    / "chunks.json"
)

EMBEDDINGS_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "embeddings"
)

EMBEDDINGS_PATH = (
    EMBEDDINGS_DIR
    / "embeddings.json"
)

# Modelo escolhido na Fase 5
MODEL_NAME = "intfloat/multilingual-e5-small"
MODEL_TYPE = "e5"

NORMALIZE_EMBEDDINGS = True

EMBEDDINGS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# CARREGAMENTO DOS DADOS
# ============================================================

def load_json(path: Path):
    """Carrega um arquivo JSON."""
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_chunks():
    """Carrega os chunks do corpus."""
    chunks = load_json(CHUNKS_PATH)

    if not chunks:
        raise ValueError("Nenhum chunk foi encontrado.")

    print(f"Chunks carregados: {len(chunks)}")

    return chunks


# ============================================================
# CONTROLE DE VERSÃO DO CORPUS
# ============================================================

def calculate_corpus_hash(chunks):
    """
    Gera um hash do conteúdo dos chunks.

    O hash permite verificar se o corpus mudou desde
    a última geração dos embeddings.
    """

    corpus_content = json.dumps(
        chunks,
        ensure_ascii=False,
        sort_keys=True,
    )

    return hashlib.sha256(
        corpus_content.encode("utf-8")
    ).hexdigest()


# ============================================================
# MODELO
# ============================================================

def load_model():
    """Carrega o modelo de embeddings configurado."""

    print()
    print("=" * 70)
    print(f"Carregando modelo: {MODEL_NAME}")
    print("=" * 70)

    model = SentenceTransformer(MODEL_NAME)

    print("Modelo carregado com sucesso.")

    return model


# ============================================================
# GERAÇÃO DOS EMBEDDINGS
# ============================================================

def prepare_text(chunk):
    """
    Prepara o texto do chunk para o modelo.

    O multilingual-e5-small utiliza o prefixo
    'passage:' para documentos.
    """

    text = chunk["text"]

    if MODEL_TYPE == "e5":
        text = f"passage: {text}"

    return text


def generate_embeddings(model, chunks):
    """
    Gera um embedding para cada chunk.

    Os embeddings são normalizados para que possam
    ser comparados posteriormente por produto escalar,
    equivalente à similaridade de cosseno.
    """

    texts = [
        prepare_text(chunk)
        for chunk in chunks
    ]

    print()
    print("Gerando embeddings dos chunks...")

    embeddings = model.encode(
        texts,
        normalize_embeddings=NORMALIZE_EMBEDDINGS,
        show_progress_bar=True,
    )

    print("Embeddings gerados com sucesso.")

    return embeddings


# ============================================================
# PERSISTÊNCIA
# ============================================================

def build_output(chunks, embeddings, corpus_hash):
    """
    Monta o artefato final preservando a associação:

    vetor ↔ chunk_id ↔ metadados
    """

    embedding_dimension = len(embeddings[0])

    items = []

    for chunk, embedding in zip(chunks, embeddings):

        
        item = {
            "chunk_id": chunk["chunk_id"],
            "embedding": embedding.tolist(),
            "doc_family_id": chunk["doc_family_id"],
            "status": chunk["status"],
            "version_ordinal": chunk["version_ordinal"],
            "effective_from": chunk["effective_from"],
            "effective_to": chunk["effective_to"],
            "source_path": chunk["source_path"],
            "section_title": chunk["section_title"],
        }

        items.append(item)

    return {
        "metadata": {
            "model_name": MODEL_NAME,
            "model_type": MODEL_TYPE,
            "normalized": NORMALIZE_EMBEDDINGS,
            "embedding_dimension": embedding_dimension,
            "total_chunks": len(chunks),
            "corpus_hash": corpus_hash,
        },
        "embeddings": items,
    }


def save_embeddings(output):
    """Salva os embeddings definitivos em JSON."""

    with open(
        EMBEDDINGS_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print("Embeddings salvos com sucesso em:")
    print(EMBEDDINGS_PATH)


# ============================================================
# VERIFICAÇÃO DE REGENERAÇÃO
# ============================================================

def should_regenerate(corpus_hash, chunks):
    """
    Verifica se os embeddings precisam ser regenerados.

    A regeneração ocorre quando:

    - o arquivo ainda não existe;
    - o modelo mudou;
    - o tipo do modelo mudou;
    - a normalização mudou;
    - a quantidade de chunks mudou;
    - o corpus mudou.
    """

    if not EMBEDDINGS_PATH.exists():
        print()
        print("Nenhum embedding definitivo encontrado.")
        print("Será necessário gerar os embeddings.")
        return True

    try:
        existing = load_json(EMBEDDINGS_PATH)
        metadata = existing["metadata"]

    except (json.JSONDecodeError, KeyError, TypeError):
        print()
        print("Artefato de embeddings inválido.")
        print("Será necessário regenerar.")
        return True

    if metadata.get("model_name") != MODEL_NAME:
        print("Modelo alterado. Regenerando embeddings.")
        return True

    if metadata.get("model_type") != MODEL_TYPE:
        print("Tipo de modelo alterado. Regenerando embeddings.")
        return True

    if metadata.get("normalized") != NORMALIZE_EMBEDDINGS:
        print("Configuração de normalização alterada.")
        print("Regenerando embeddings.")
        return True

    if metadata.get("total_chunks") != len(chunks):
        print("Quantidade de chunks alterada.")
        print("Regenerando embeddings.")
        return True

    if metadata.get("corpus_hash") != corpus_hash:
        print("Corpus alterado.")
        print("Regenerando embeddings.")
        return True

    print()
    print("Embeddings existentes são compatíveis.")
    print("Nenhuma regeneração necessária.")

    return False


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("GERAÇÃO DE EMBEDDINGS DEFINITIVOS")
    print("Corpus ConectaTel")
    print("=" * 70)

    chunks = load_chunks()

    corpus_hash = calculate_corpus_hash(chunks)

    # --------------------------------------------------------
    # Verifica se podemos reutilizar o artefato existente
    # --------------------------------------------------------

    if not should_regenerate(corpus_hash, chunks):
        return

    # --------------------------------------------------------
    # Carrega modelo
    # --------------------------------------------------------

    model = load_model()

    # --------------------------------------------------------
    # Gera embeddings
    # --------------------------------------------------------

    embeddings = generate_embeddings(
        model,
        chunks,
    )

    # --------------------------------------------------------
    # Monta artefato
    # --------------------------------------------------------

    output = build_output(
        chunks,
        embeddings,
        corpus_hash,
    )

    # --------------------------------------------------------
    # Salva
    # --------------------------------------------------------

    save_embeddings(output)

    print()
    print("=" * 70)
    print("GERAÇÃO CONCLUÍDA")
    print("=" * 70)
    print(f"Modelo: {MODEL_NAME}")
    print(f"Chunks: {len(chunks)}")
    print(
        f"Dimensão dos embeddings: "
        f"{output['metadata']['embedding_dimension']}"
    )
    print(f"Normalização: {NORMALIZE_EMBEDDINGS}")
    print(f"Arquivo: {EMBEDDINGS_PATH}")


if __name__ == "__main__":
    main()