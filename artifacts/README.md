# Artefatos de execução

Este diretório guarda somente saídas e evidências geradas durante a execução.
Ele não é fonte de código nem de documentação normativa.

- `audit/`: evidências revisáveis e trilha de auditoria versionada quando
  necessário para a entrega.
- `data/`: saídas locais do pipeline de dados.
- `index/`: índices gerados para busca; normalmente ignorados pelo Git.
- `logs/`: logs locais; normalmente ignorados pelo Git.

Arquivos gerados grandes, segredos e dados sensíveis não devem ser versionados.
Os contratos e procedimentos ficam em `docs/`; os dados de exemplo ficam em
`data/examples/`.
