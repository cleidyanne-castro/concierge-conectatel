"""Agregações analíticas da camada Gold do ConectaTel."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import pandas as pd


SILVER_COLUMNS = [
    "chamado_id", "data_abertura", "canal", "categoria", "subcategoria",
    "estado", "cidade", "duracao_minutos", "resolvido_primeiro_contato",
    "encaminhado_humano", "satisfacao_1_a_5", "plano_atual",
    "resumo_atendimento",
]


def validate_silver(df: pd.DataFrame) -> None:
    """Valida o contrato mínimo recebido da Silver."""
    missing = sorted(set(SILVER_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")
    if df.empty:
        raise ValueError("A Silver não possui linhas para análise")


def _rate(series: pd.Series) -> float:
    """Calcula uma taxa percentual com denominador explícito."""
    valid = series.dropna()
    return round(float(valid.mean() * 100), 2) if len(valid) else 0.0


def _mean(series: pd.Series) -> float:
    """Calcula média sem transformar ausência em zero."""
    valid = series.dropna()
    return round(float(valid.mean()), 2) if len(valid) else 0.0


def build_category_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Resume volume, satisfação e resolução por categoria."""
    result = (
        df.groupby(["categoria", "subcategoria"], dropna=False)
        .agg(
            chamados=("chamado_id", "size"),
            satisfacao_media=("satisfacao_1_a_5", _mean),
            satisfacao_n=("satisfacao_1_a_5", "count"),
            taxa_primeiro_contato=("resolvido_primeiro_contato", _rate),
            primeiro_contato_n=("resolvido_primeiro_contato", "count"),
            taxa_encaminhamento=("encaminhado_humano", _rate),
            encaminhamento_n=("encaminhado_humano", "count"),
            duracao_media_minutos=("duracao_minutos", _mean),
            duracao_n=("duracao_minutos", "count"),
        )
        .reset_index()
        .sort_values("chamados", ascending=False)
    )
    result["percentual_chamados"] = (result["chamados"] / len(df) * 100).round(2)
    return result


def build_channel_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Resume desempenho por canal de atendimento."""
    return (
        df.groupby("canal", dropna=False)
        .agg(
            chamados=("chamado_id", "size"),
            satisfacao_media=("satisfacao_1_a_5", _mean),
            satisfacao_n=("satisfacao_1_a_5", "count"),
            taxa_primeiro_contato=("resolvido_primeiro_contato", _rate),
            primeiro_contato_n=("resolvido_primeiro_contato", "count"),
            taxa_encaminhamento=("encaminhado_humano", _rate),
            encaminhamento_n=("encaminhado_humano", "count"),
            duracao_media_minutos=("duracao_minutos", _mean),
            duracao_n=("duracao_minutos", "count"),
        )
        .reset_index()
        .sort_values("chamados", ascending=False)
    )


def build_geography_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Resume volume e duração por estado e cidade."""
    return (
        df.groupby(["estado", "cidade"], dropna=False)
        .agg(
            chamados=("chamado_id", "size"),
            duracao_media_minutos=("duracao_minutos", _mean),
            duracao_n=("duracao_minutos", "count"),
            satisfacao_media=("satisfacao_1_a_5", _mean),
            satisfacao_n=("satisfacao_1_a_5", "count"),
        )
        .reset_index()
        .sort_values("chamados", ascending=False)
        .round({"satisfacao_media": 2, "duracao_media_minutos": 2})
    )


def build_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Publica KPIs sempre acompanhados de volume ou denominador."""
    return pd.DataFrame(
        [
            {"kpi": "total_chamados", "valor": len(df), "denominador": len(df)},
            {"kpi": "satisfacao_media", "valor": _mean(df["satisfacao_1_a_5"]), "denominador": int(df["satisfacao_1_a_5"].notna().sum())},
            {"kpi": "taxa_primeiro_contato", "valor": _rate(df["resolvido_primeiro_contato"]), "denominador": int(df["resolvido_primeiro_contato"].notna().sum())},
            {"kpi": "taxa_encaminhamento_humano", "valor": _rate(df["encaminhado_humano"]), "denominador": int(df["encaminhado_humano"].notna().sum())},
            {"kpi": "duracao_media_minutos", "valor": round(float(df["duracao_minutos"].mean()), 2), "denominador": int(df["duracao_minutos"].notna().sum())},
        ]
    )


def build_design_decisions(category: pd.DataFrame, channel: pd.DataFrame) -> str:
    """Gera decisões de design rastreáveis aos achados da Gold."""
    top = category.iloc[0]
    best_channel = channel.sort_values("taxa_primeiro_contato", ascending=False).iloc[0]
    return (
        "# Síntese e decisões de design\n\n"
        f"A categoria **{top['categoria']} / {top['subcategoria']}** concentra "
        f"{top['percentual_chamados']:.2f}% dos chamados ({int(top['chamados'])} registros). "
        "O Concierge deve priorizar uma intenção e respostas guiadas para esse tema.\n\n"
        f"O canal **{best_channel['canal']}** apresenta a maior taxa de resolução "
        f"no primeiro contato entre os canais observados ({best_channel['taxa_primeiro_contato']:.2f}%). "
        "A experiência deve favorecer esse canal e encaminhar ao humano quando os sinais de baixa resolução aparecerem.\n\n"
        "## Rastreabilidade\n\n"
        "As decisões usam diretamente `gold_categoria_resumo.csv` e `gold_canal_resumo.csv`, "
        "com volume e denominador publicados para auditoria.\n"
    )


def save_gold_outputs(df: pd.DataFrame, output_root: str | Path) -> dict[str, Any]:
    """Gera e persiste os produtos analíticos da Gold."""
    validate_silver(df)
    root = Path(output_root)
    root.mkdir(parents=True, exist_ok=True)
    category = build_category_analysis(df)
    channel = build_channel_analysis(df)
    geography = build_geography_analysis(df)
    outputs = {
        "gold_kpis.csv": build_kpis(df),
        "gold_categoria_resumo.csv": category,
        "gold_canal_resumo.csv": channel,
        "gold_geografia_resumo.csv": geography,
    }
    for name, frame in outputs.items():
        frame.to_csv(root / name, index=False)
    decision_path = root / "gold_decisoes_design.md"
    decision_path.write_text(build_design_decisions(category, channel), encoding="utf-8")

    quality = {
        "layer": "gold",
        "input_rows": int(len(df)),
        "output_rows": {name: int(len(frame)) for name, frame in outputs.items()},
        "nulls_in_input": {column: int(df[column].isna().sum()) for column in SILVER_COLUMNS},
        "denominator_policy": "taxas e medias usam somente valores validos; o denominador e publicado",
        "status": "PASS",
    }
    (root / "gold_quality_report.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    output_files = [*outputs, decision_path.name, "gold_quality_report.json"]
    manifest = {
        "layer": "gold",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_rows": int(len(df)),
        "output_files": output_files,
        "analysis_count": 3,
        "status": "PASS",
    }
    (root / "gold_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifest
