"""
Publica os artefatos da base de conhecimento no Amazon S3.

Fluxo pretendido: um programador cria o bucket S3 manualmente, exporta o nome
em ``S3_BUCKET_NAME`` (ou coloca no ``.env``) e roda este script UMA vez para
semear os artefatos. Depois disso, ``sam deploy`` sobe o resto da infra — o
template SAM apenas lê deste bucket, não o cria.

Credenciais: cadeia padrão do boto3 (variáveis de ambiente, ``AWS_PROFILE``,
SSO, role de instância). Nada é fixado neste arquivo.
"""

import os
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError

try:  
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  
    pass


BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "").strip()
REGION = os.environ.get("AWS_REGION", "us-east-1")


PROJECT_ROOT = Path(__file__).resolve().parents[2]

ARTIFACTS = {
    PROJECT_ROOT / "artifacts" / "chunks" / "chunks.json":
        "processed/chunks.json",

    PROJECT_ROOT / "artifacts" / "embeddings" / "embeddings.json":
        "index/embeddings.json",
}


def upload_file(s3_client, local_path: Path, s3_key: str) -> None:
    """Envia um arquivo local para o S3."""

    if not BUCKET_NAME:
        raise RuntimeError(
            "Defina S3_BUCKET_NAME explicitamente antes de publicar os artefatos."
        )
    if not local_path.exists():
        raise FileNotFoundError(
            f"Artefato não encontrado: {local_path}"
        )

    print(f"Enviando: {local_path}")
    print(f"      S3: s3://{BUCKET_NAME}/{s3_key}")

    s3_client.upload_file(
        str(local_path),
        BUCKET_NAME,
        s3_key,
    )

    print("      OK")


def main() -> None:
    print("=" * 60)
    print("UPLOAD DA BASE DE CONHECIMENTO — CONECTATEL")
    print("=" * 60)
    print(f"Bucket: {BUCKET_NAME}")
    print(f"Região: {REGION}")
    profile = os.environ.get("AWS_PROFILE") or os.environ.get("AWS_DEFAULT_PROFILE")
    print(f"Perfil: {profile or '(cadeia padrão de credenciais)'}")
    print()

    if not BUCKET_NAME:
        raise RuntimeError(
            "Defina S3_BUCKET_NAME (o bucket precisa já existir na conta AWS)."
        )

    # region_name explícito; o profile vem do ambiente automaticamente.
    session = boto3.Session(region_name=REGION)
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
