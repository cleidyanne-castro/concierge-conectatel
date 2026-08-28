# Infraestrutura AWS

Registrar aqui somente configuração reproduzível e sem segredos: S3 privado com versionamento/SSE-S3, IAM de menor privilégio, Lambda/handler, permissões mínimas do Bedrock, região adotada e procedimento de limpeza de recursos.

## Workflow Databricks

[`databricks_workflow_gold.json`](databricks_workflow_gold.json) versiona o
encadeamento `Bronze → Silver → Gold`. Os placeholders `workspace_path` e
`compute_id` evitam registrar caminhos privados e identificadores do workspace.

Antes da publicação, substitua os parâmetros pelo ambiente correto, confirme o
acesso aos três notebooks e execute uma rodada completa. Registre horário,
status de cada tarefa, linhas processadas e links das evidências. O JSON é uma
referência de configuração. A criação efetiva do Job continua sendo feita no
 workspace Databricks.
