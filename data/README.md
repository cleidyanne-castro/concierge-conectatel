# Dados

Este diretório contém entradas, nunca lógica de negócio ou saídas de execução.

- `examples/`: conjunto pequeno e seguro para smoke tests e demonstrações.
- `corpus/`: corpus local de entrada; documentos reais permanecem fora do Git.
- `processed/`: ponto reservado para dados tratados quando a execução local
  precisar persistir essa etapa.
- `raw/`: dados brutos locais; ignorados pelo Git.

O corpus oficial é a única fonte autorizada para respostas. Saídas produzidas
por notebooks e pipelines devem ir para `artifacts/`, não voltar para `data/`.
