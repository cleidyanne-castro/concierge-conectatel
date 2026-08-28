# Infraestrutura AWS

Registrar aqui somente configuração reproduzível e sem segredos: S3 privado com versionamento/SSE-S3, IAM de menor privilégio, Lambda/handler, permissões mínimas do Bedrock, região adotada e procedimento de limpeza de recursos.

## Workflow Databricks

O encadeamento esperado é `Bronze → Silver → Gold`, conforme descrito em
[`docs/parte_01_dados/engenharia_dados.md`](../docs/parte_01_dados/engenharia_dados.md).
Quando a definição do Workflow Job for exportada do ambiente, ela deve ser
versionada nesta pasta com placeholders para `workspace_path` e `compute_id`,
sem caminhos privados ou identificadores do workspace.

Antes da publicação, substitua os parâmetros pelo ambiente correto, confirme o
acesso aos três notebooks e execute uma rodada completa. Registre horário,
status de cada tarefa, linhas processadas e links das evidências. O JSON é uma
referência de configuração. A criação efetiva do Job continua sendo feita no
 workspace Databricks.
