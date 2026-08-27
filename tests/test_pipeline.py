import pandas as pd
from src.data_pipeline import run_analyses

def test_pipeline_returns_three_descriptive_views():
    df=pd.DataFrame({'assunto':['fatura','fatura','sinal'],'urgencia':['baixa','alta','alta']})
    result=run_analyses(df)
    assert len([k for k in result if k.startswith('frequency_')]) >= 2

