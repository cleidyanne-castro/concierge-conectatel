# Dashboard da Gold

## Objetivo

Oferecer uma visão executiva das dúvidas mais frequentes, do esforço de
atendimento e dos pontos em que o Concierge pode reduzir encaminhamentos.

## Fontes

O dashboard foi criado no Databricks com base no dataset tratado da Silver. Os
arquivos Gold continuam sendo os produtos analíticos oficiais para consumo e
auditoria:

- `gold_kpis.csv` para os cartões principais.
- `gold_categoria_resumo.csv` para concentração de temas.
- `gold_canal_resumo.csv` para comparação operacional.
- `gold_geografia_resumo.csv` para distribuição territorial.

## Visuais

- total de chamados e satisfação média.
- taxa de resolução no primeiro contato.
- taxa de encaminhamento humano.
- categorias e subcategorias mais frequentes.
- comparação de desempenho por canal.
- volume e duração média por estado e cidade.

Cada visualização deve exibir o volume ou denominador correspondente. Médias e
taxas não devem ser interpretadas sem observar a quantidade de registros
válidos.

Filtros disponíveis: canal, categoria, estado e plano atual. A Gold e suas
fontes estão implementadas no repositório. O dashboard publicado e sua
validação estão registrados em
`artifacts/audit/gold_dashboard_execution_evidence.md`.
