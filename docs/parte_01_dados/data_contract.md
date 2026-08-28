# Contrato de dados do ConectaTel

## Escopo

Este contrato define o formato comum entre Bronze, Silver e Gold. A Bronze
preserva o CSV original; a Silver trata os dados; a Gold publica agregações
para análise e decisões do Concierge.

## Colunas do log

| Coluna | Tipo Silver | Regra | Consumidor |
|---|---|---|---|
| `chamado_id` | string | identificador do chamado | todas as camadas |
| `data_abertura` | datetime | inválida vira nula e é contabilizada | Gold |
| `canal` | string | lowercase, sem acentos, sem espaços externos | Gold/Agente |
| `categoria` | string | lowercase, sem acentos, sem espaços externos | Gold/RAG |
| `subcategoria` | string | lowercase, sem acentos, sem espaços externos | Gold/RAG |
| `estado` | string | categoria normalizada | Gold |
| `cidade` | string | categoria normalizada | Gold |
| `duracao_minutos` | numeric | número não negativo | Gold |
| `resolvido_primeiro_contato` | boolean | `sim/não`, `1/0`, `true/false` | Gold |
| `encaminhado_humano` | boolean | `sim/não`, `1/0`, `true/false` | Gold/Agente |
| `satisfacao_1_a_5` | numeric | intervalo de 1 a 5 | Gold |
| `plano_atual` | string | categoria normalizada | Gold |
| `resumo_atendimento` | string | texto preservado; ausente vira `unknown` | RAG |

## Regras de qualidade

- Colunas ausentes interrompem a execução (`FAIL`).
- Saída sem linhas interrompe a execução (`FAIL`).
- Nulos, valores inválidos e duplicatas devem ser contabilizados.
- A Bronze não deduplica; a Silver remove duplicatas exatas mantendo a primeira
  ocorrência.
- A Gold só deve publicar métricas acompanhadas de denominador e volume.

## Artefatos por camada

- Bronze: snapshot, schema, inventário, qualidade e metadados do corpus.
- Silver: `silver_calls_cleaned.csv` e relatório de qualidade.
- Gold: KPIs, resumos por categoria/canal/geografia e decisões de design.
