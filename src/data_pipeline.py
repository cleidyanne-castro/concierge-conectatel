"""Parte 1 - pipeline de dados. Implementar limpeza e as três análises do desafio."""
from pathlib import Path
import pandas as pd
import argparse

def load_and_clean(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df.drop_duplicates().dropna(how="all")

def run_analyses(df: pd.DataFrame) -> dict:
    """Retornar no mínimo três análises descritivas e registrar o achado usado no design."""
    analyses = {
        "shape": {"rows": int(df.shape[0]), "columns": int(df.shape[1])},
        "missing_values": df.isna().sum().to_dict(),
        "columns": list(df.columns),
    }
    for column in df.select_dtypes(include='object').columns[:3]:
        analyses[f"frequency_{column}"] = df[column].value_counts(dropna=False).head(10).to_dict()
    return analyses

def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument('--input',required=True); parser.add_argument('--output',required=True)
    args=parser.parse_args(); output=Path(args.output); output.mkdir(parents=True,exist_ok=True)
    df=load_and_clean(args.input); df.to_csv(output/'cleaned_calls.csv',index=False); (output/'analyses.json').write_text(__import__('json').dumps(run_analyses(df),ensure_ascii=False,indent=2),encoding='utf-8')

if __name__ == '__main__': main()
