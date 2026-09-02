from pathlib import Path

import pytest

from src.parte_02_rag import upload_to_s3


def test_upload_requires_explicit_bucket(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(upload_to_s3, "BUCKET_NAME", "")

    with pytest.raises(RuntimeError, match="S3_BUCKET_NAME"):
        upload_to_s3.upload_file(object(), tmp_path / "artifact.json", "key.json")
