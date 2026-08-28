"""Controles de qualidade e rastreabilidade das camadas de dados."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def quality_status(
    *,
    missing_columns: int = 0,
    output_rows: int = 0,
    invalid_values: int = 0,
    duplicate_rows: int = 0,
) -> str:
    """Classifica a execução sem esconder problemas encontrados."""
    if missing_columns > 0 or output_rows == 0:
        return "FAIL"
    if invalid_values > 0 or duplicate_rows > 0:
        return "WARNING"
    return "PASS"


def build_run_manifest(
    *,
    layer: str,
    source_path: str | Path,
    output_paths: list[str | Path],
    input_rows: int,
    output_rows: int,
    status: str,
    started_at: datetime,
    finished_at: datetime,
    code_version: str = "local",
) -> dict[str, Any]:
    """Monta um registro serializável da execução da camada."""
    duration_seconds = (finished_at - started_at).total_seconds()
    if duration_seconds < 0:
        raise ValueError("finished_at não pode ser anterior a started_at")
    return {
        "layer": layer,
        "source_path": str(source_path),
        "output_paths": [str(path) for path in output_paths],
        "input_rows": int(input_rows),
        "output_rows": int(output_rows),
        "rows_removed": int(input_rows - output_rows),
        "status": status,
        "started_at_utc": started_at.astimezone(timezone.utc).isoformat(),
        "finished_at_utc": finished_at.astimezone(timezone.utc).isoformat(),
        "duration_seconds": duration_seconds,
        "code_version": code_version,
    }
