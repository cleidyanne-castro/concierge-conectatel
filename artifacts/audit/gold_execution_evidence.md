# Evidência de execução: Gold

## Identificação

- Data: 2026-08-28
- Branch do Git folder: `feat/gold-analises`
- Job: `conectatel-medallion-pipeline`
- Job ID: `974579039795300`
- Run ID: `1025750876614575`
- Compute: Serverless
- Status: `Succeeded`
- Duração: `1m 05s`

## Dependências observadas

| Tarefa | Notebook | Status | Duração |
|---|---|---|---|
| Bronze | `01_bronze_ingestao` | Succeeded | 23s |
| Silver | `02_silver_limpeza` | Succeeded | 8s |
| Gold | `03_gold_analise` | Succeeded | 32s |

O grafo confirmou a ordem `Bronze → Silver → Gold`. Silver aguardou a Bronze,
e Gold aguardou a Silver.

## Resultado da Gold

- Linhas consumidas da Silver: `320`.
- Análises agregadas: categoria/subcategoria, canal e geografia.
- Arquivos produzidos no Volume:
  - `gold_kpis.csv`.
  - `gold_categoria_resumo.csv`.
  - `gold_canal_resumo.csv`.
  - `gold_geografia_resumo.csv`.
  - `gold_decisoes_design.md`.
  - `gold_quality_report.json`.
  - `gold_manifest.json`.
- Principal categoria: `cancelamento / cancelamento de linha`, com `22`
  chamados e `6,88%` do volume.
- Canal com maior resolução no primeiro contato: `loja fisica`, com `48,96%`.

## Interpretação

Os resultados sustentam a priorização de uma intenção específica para
cancelamento e o uso dos indicadores por canal para orientar a experiência do
Concierge. Os denominadores permanecem publicados nos artefatos analíticos.

## Limite da evidência

Esta evidência confirma a execução do pipeline e a geração dos arquivos. A
criação e a validação visual do dashboard continuam sendo uma atividade
separada no workspace Databricks.
