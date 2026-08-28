# Dados

Este diretório contém entradas do projeto, nunca lógica de negócio ou saídas de execução.

- `examples/`: conjunto pequeno e seguro para smoke tests e demonstrações.
- `corpus/`: corpus fictício oficial, versionado para o handoff de Chunking e Embeddings.
- `bronze/`: metadados de vigência produzidos a partir do corpus.
- `processed/`: ponto reservado para dados tratados quando a execução local
  precisar persistir essa etapa.
- `raw/`: dados brutos locais; ignorados pelo Git.

O corpus oficial é a única fonte autorizada para respostas. Saídas produzidas
por notebooks e pipelines devem ir para `artifacts/`, não voltar para `data/`.
O log de chamados completo e os dados gerados no Volume permanecem fora do GitHub.
