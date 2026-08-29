from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 150


def calculate_sha256(file_path: Path) -> str:
    """
    Calcula o SHA-256 do arquivo original para rastreabilidade.
    """
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for block in iter(lambda: file.read(8192), b""):
            sha256.update(block)

    return sha256.hexdigest()


def load_metadata(metadata_path: Path) -> dict[str, dict[str, Any]]:
    """
    Lê o JSON de metadados e cria um índice usando source_path como chave.
    """
    with metadata_path.open("r", encoding="utf-8") as file:
        metadata_list = json.load(file)

    return {
        item["source_path"]: item
        for item in metadata_list
    }


def normalize_source_path(file_path: Path, corpus_root: Path) -> str:
    """
    Converte o caminho local para o formato usado no metadata JSON.

    Exemplo:
    data/corpus/faq/faq_geral.md
    """
    return file_path.as_posix()


def remove_frontmatter(content: str) -> str:
    pattern = r"\A---\s*\n.*?\n---\s*\n"
    return re.sub(
        pattern,
        "",
        content,
        count=1,
        flags=re.DOTALL,
    )


def parse_sections(content: str) -> list[dict[str, str]]:
    """
    Divide o documento em seções usando títulos Markdown.

    Cada seção mantém o título que contextualiza os parágrafos.
    """
    lines = content.splitlines()

    sections = []
    current_title = None
    current_lines = []

    for line in lines:
        stripped_line = line.strip()

        if re.match(r"^#{1,6}\s+", stripped_line):
            if current_lines:
                sections.append(
                    {
                        "section_title": current_title or "Conteúdo geral",
                        "text": "\n".join(current_lines).strip(),
                    }
                )

            current_title = re.sub(
                r"^#{1,6}\s+",
                "",
                stripped_line
            ).strip()

            current_lines = []

        else:
            current_lines.append(line)

    if current_lines:
        sections.append(
            {
                "section_title": current_title or "Conteúdo geral",
                "text": "\n".join(current_lines).strip(),
            }
        )

    return [
        section
        for section in sections
        if section["text"]
    ]

def build_overlap(text: str, overlap_size: int) -> str:
    """
    Retorna o final do texto para uso como overlap,
    preservando palavras completas.

    O corte nunca ocorre no meio de uma palavra.
    """
    if overlap_size <= 0:
        return ""

    if len(text) <= overlap_size:
        return text.strip()

    overlap = text[-overlap_size:]

    # Se começou no meio de uma palavra, descarta
    # a primeira palavra parcial.
    first_space = overlap.find(" ")

    if first_space == -1:
        return ""

    overlap = overlap[first_space + 1:]

    return overlap.strip()


def split_text_by_paragraphs(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """
    Divide o texto priorizando blocos semânticos.

    Cada bloco separado por linha em branco é tratado como uma
    unidade. Quando possível, mantém perguntas e respectivas
    respostas no mesmo chunk.

    Parágrafos maiores que chunk_size são delegados para
    split_large_paragraph().
    """

    paragraphs = [
        paragraph.strip()
        for paragraph in re.split(r"\n\s*\n", text)
        if paragraph.strip()
    ]

    chunks = []
    current_parts = []
    current_length = 0

    for paragraph in paragraphs:
        paragraph_length = len(paragraph)

        # Parágrafo/bloco maior que o limite.
        if paragraph_length > chunk_size:
            if current_parts:
                chunks.append("\n\n".join(current_parts))

            large_chunks = split_large_paragraph(
                paragraph,
                chunk_size,
                chunk_overlap,
            )

            chunks.extend(large_chunks)

            current_parts = []
            current_length = 0
            continue

        additional_length = (
            paragraph_length
            if not current_parts
            else paragraph_length + 2
        )

        # Se ultrapassar o tamanho do chunk, fecha o atual.
        if (
            current_parts
            and current_length + additional_length > chunk_size
        ):
            previous_text = "\n\n".join(current_parts)
            chunks.append(previous_text)

            overlap_text = build_overlap(
                previous_text,
                chunk_overlap,
            )

            current_parts = (
                [overlap_text]
                if overlap_text
                else []
            )

            current_length = len(overlap_text)

        current_parts.append(paragraph)

        if len(current_parts) == 1:
            current_length = paragraph_length
        else:
            current_length += paragraph_length + 2

    if current_parts:
        chunks.append("\n\n".join(current_parts))

    return chunks


def split_large_paragraph(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """
    Divide um parágrafo grande sem cortar palavras.

    A divisão procura preferencialmente:
    1. fim de frase;
    2. espaço entre palavras.

    O overlap também utiliza somente palavras completas.
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        if end < text_length:
            # Primeiro tenta encontrar uma quebra natural
            # próxima do limite.
            sentence_positions = [
                text.rfind(". ", start, end),
                text.rfind("? ", start, end),
                text.rfind("! ", start, end),
                text.rfind("; ", start, end),
            ]

            sentence_position = max(sentence_positions)

            if sentence_position > start:
                end = sentence_position + 1
            else:
                # Caso não exista fim de frase próximo,
                # procura um espaço.
                split_position = text.rfind(" ", start, end)

                if split_position > start:
                    end = split_position

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        overlap_text = build_overlap(
            chunk,
            chunk_overlap,
        )

        if overlap_text:
            overlap_start = text.rfind(
                overlap_text,
                start,
                end,
            )

            if overlap_start >= start:
                start = overlap_start
            else:
                start = max(end - chunk_overlap, start + 1)
        else:
            start = max(end - chunk_overlap, start + 1)

    return chunks


def build_chunk_id(
    source_path: str,
    section_title: str,
    chunk_index: int,
    text: str,
) -> str:
    """
    Gera um identificador determinístico.

    O mesmo documento, com o mesmo conteúdo e configuração,
    gera o mesmo identificador.
    """
    raw_id = (
        f"{source_path}|"
        f"{section_title}|"
        f"{chunk_index}|"
        f"{text}"
    )

    digest = hashlib.sha256(
        raw_id.encode("utf-8")
    ).hexdigest()[:16]

    return f"chunk_{digest}"


def chunk_document(
    file_path: Path,
    metadata: dict[str, Any],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    """
    Gera chunks de um único documento.

    Cada chunk preserva:
    - origem;
    - família documental;
    - versão;
    - período de vigência;
    - status;
    - hash do arquivo;
    - seção de origem;
    - texto.
    """
    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap deve ser menor que chunk_size."
        )

    content = file_path.read_text(encoding="utf-8")
    content = remove_frontmatter(content)

    file_sha256 = calculate_sha256(file_path)

    sections = parse_sections(content)

    chunks = []
    chunk_index = 0

    for section in sections:
        section_title = section["section_title"]
        section_text = section["text"]

        text_chunks = split_text_by_paragraphs(
            text=section_text,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        for text_chunk in text_chunks:
            chunk_id = build_chunk_id(
                source_path=metadata["source_path"],
                section_title=section_title,
                chunk_index=chunk_index,
                text=text_chunk,
            )

            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "source_path": metadata["source_path"],
                    "doc_family_id": metadata.get(
                        "doc_family_id"
                    ),
                    "version_ordinal": metadata.get(
                        "version_ordinal"
                    ),
                    "effective_from": metadata.get(
                        "effective_from"
                    ),
                    "effective_to": metadata.get(
                        "effective_to"
                    ),
                    "status": metadata.get("status"),
                    "sha256": file_sha256,
                    "section_title": section_title,
                    "text": text_chunk,
                }
            )

            chunk_index += 1

    return chunks


def chunk_corpus(
    corpus_root: Path,
    metadata_path: Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    """
    Processa todos os documentos Markdown do corpus.
    """
    metadata_index = load_metadata(metadata_path)

    all_chunks = []

    for file_path in sorted(corpus_root.rglob("*.md")):
        source_path = normalize_source_path(
            file_path,
            corpus_root,
        )

        metadata = metadata_index.get(source_path)

        if metadata is None:
            raise ValueError(
                f"Metadados não encontrados para: {source_path}"
            )

        document_chunks = chunk_document(
            file_path=file_path,
            metadata=metadata,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        all_chunks.extend(document_chunks)

    return all_chunks


def save_chunks(
    chunks: list[dict[str, Any]],
    output_path: Path,
) -> None:
    """
    Salva os chunks em JSON para inspeção e para as próximas
    etapas de embeddings e indexação.
    """
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2,
        )


if __name__ == "__main__":
    corpus_root = Path("data/corpus")
    metadata_path = Path(
        "data/bronze/bronze_corpus_metadata.json"
    )

    output_path = Path(
        "artifacts/chunks/chunks.json"
    )

    chunks = chunk_corpus(
        corpus_root=corpus_root,
        metadata_path=metadata_path,
        chunk_size=800,
        chunk_overlap=150,
    )

    save_chunks(
        chunks=chunks,
        output_path=output_path,
    )

    print(f"Documentos processados: {len(list(corpus_root.rglob('*.md')))}")
    print(f"Chunks gerados: {len(chunks)}")
    print(f"Arquivo gerado: {output_path}")