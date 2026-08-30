"""
Publica os artefatos da base de conhecimento no Amazon S3.

As credenciais AWS NÃO são armazenadas neste arquivo.
O boto3 utiliza o perfil AWS configurado no ambiente.
"""

from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError


# Configuração do bucket
BUCKET_NAME = "concierge-conectatel-kb-squad04"
REGION = "us-east-1"

# Perfil AWS SSO configurado pelo AWS CLI
AWS_PROFILE = "AlunoAdmin-668723997013"

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Artefatos que serão publicados
ARTIFACTS = {
    PROJECT_ROOT / "artifacts" / "chunks" / "chunks.json":
        "processed/chunks.json",

    PROJECT_ROOT / "artifacts" / "embeddings" / "embeddings.json":
        "index/embeddings.json",

    PROJECT_ROOT / "artifacts" / "embeddings" / "faiss" / "index.faiss":
        "index/index.faiss",

    PROJECT_ROOT / "artifacts" / "embeddings" / "faiss" / "metadata.json":
        "index/metadata.json",
}


def upload_file(s3_client, local_path: Path, s3_key: str) -> None:
    """Envia um arquivo local para o S3."""

    if not local_path.exists():
        raise FileNotFoundError(
            f"Artefato não encontrado: {local_path}"
        )

    print(f"Enviando: {local_path}")
    print(f"       S3: s3://{BUCKET_NAME}/{s3_key}")

    s3_client.upload_file(
        str(local_path),
        BUCKET_NAME,
        s3_key,
    )

    print("       OK")


def main() -> None:
    print("=" * 60)
    print("UPLOAD DA BASE DE CONHECIMENTO — CONECTATEL")
    print("=" * 60)
    print(f"Bucket: {BUCKET_NAME}")
    print(f"Região: {REGION}")
    print(f"Perfil: {AWS_PROFILE}")
    print()

    # Usa as credenciais temporárias obtidas pelo AWS SSO.
    session = boto3.Session(
        profile_name=AWS_PROFILE,
        region_name=REGION,
    )

    s3_client = session.client("s3")

    try:
        for local_path, s3_key in ARTIFACTS.items():
            upload_file(s3_client, local_path, s3_key)

    except (FileNotFoundError, BotoCoreError, ClientError) as error:
        print()
        print(f"ERRO durante o upload: {error}")
        raise

    print()
    print("=" * 60)
    print("UPLOAD CONCLUÍDO COM SUCESSO")
    print("=" * 60)


if __name__ == "__main__":
    main()