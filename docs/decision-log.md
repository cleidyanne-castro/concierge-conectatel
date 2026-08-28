# Registro de decisões técnicas

Este arquivo registra decisões pontuais que precisam de contexto, alternativas,
evidência e responsável. Ele não substitui o comparativo planejado versus
executado, que está em [`arquitetura/planejado_vs_executado.md`](arquitetura/planejado_vs_executado.md), nem repete o registro de contribuições.

| Data | Parte | Decisão | Alternativas consideradas | Evidência | Responsável |
|---|---|---|---|---|---|
| Ago/2026 | Parte 0 | Criar e organizar o repositório GitHub com pastas por etapa do desafio | Manter código e documentação sem uma estrutura comum | [`CONTRIBUTING.md`](../CONTRIBUTING.md) e [`README.md`](../README.md) | Cleidyanne Castro Pereira |
| Ago/2026 | Arquitetura | Manter a arquitetura original como referência e registrar a arquitetura final separadamente | Substituir o desenho inicial e perder o histórico de evolução | [`docs/arquitetura/`](arquitetura/) e [`planejado_vs_executado.md`](arquitetura/planejado_vs_executado.md) | Cleidyanne Castro Pereira |
| Ago/2026 | Parte 1 | Usar uma arquitetura Medallion lógica com Python, Pandas, CSV, JSON e Markdown | Adotar PySpark, Delta Lake e processamento incremental sem exigência do desafio | [`docs/parte_01_dados/`](parte_01_dados/) | Cleidyanne Castro Pereira |
| Ago/2026 | Integração | Encadear Bronze, Silver e Gold em um Workflow Job do Databricks | Executar notebooks manualmente e deixar as dependências implícitas | [`infra/databricks_workflow_gold.json`](../infra/databricks_workflow_gold.json) | Cleidyanne Castro Pereira |
| Ago/2026 | Colaboração | Usar GitHub Projects, branches e Pull Requests para organizar a execução da squad | Centralizar o acompanhamento em conversas sem rastreabilidade | [GitHub Projects da Squad 4](https://github.com/users/cleidyanne-castro/projects/1) e [`CONTRIBUTING.md`](../CONTRIBUTING.md) | Cleidyanne Castro Pereira |
