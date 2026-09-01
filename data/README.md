# Dados

Este diretório contém entradas do projeto, nunca lógica de negócio ou saídas de execução.

- `examples/`: conjunto pequeno e seguro para smoke tests e demonstrações.
- `corpus/`: corpus fictício oficial, versionado para o handoff de Chunking e Embeddings.
- `bronze/`: metadados de vigência produzidos a partir do corpus.
- `raw/`: dados brutos locais; ignorados pelo Git.

O corpus oficial é a única fonte autorizada para respostas. Saídas produzidas
por notebooks e pipelines devem ir para `artifacts/`, não voltar para `data/`.
O log de chamados completo e os dados gerados no Volume permanecem fora do GitHub.

## Navegação da Parte 1

`data/` contém os insumos. A implementação, as regras e os resultados da
engenharia de dados estão organizados em [`docs/parte_01_dados/`](../docs/parte_01_dados/).

- [`README da Parte 1`](../docs/parte_01_dados/README.md): mapa de Bronze, Silver e Gold.
- [`Regras de negócio`](../docs/parte_01_dados/regras_negocio.md): limpeza e validações.
- [`Storytelling e pain points`](../docs/parte_01_dados/gold_dashboard.md): achados e impacto no produto.
- [`Evidências do dashboard`](../artifacts/audit/gold_dashboard_execution_evidence.md): execução e screenshots.
- [`Evidência da Gold`](../artifacts/audit/gold_execution_evidence.md): resultados e rastreabilidade.
