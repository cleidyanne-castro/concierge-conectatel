# Infraestrutura AWS

Registrar aqui somente configuração reproduzível e sem segredos: S3 privado com versionamento/SSE-S3, IAM de menor privilégio, Lambda/handler, permissões mínimas do Bedrock, região adotada e procedimento de limpeza de recursos.

## Workflow Databricks

[`databricks_workflow_gold.json`](databricks_workflow_gold.json) versiona o
encadeamento `Bronze → Silver → Gold`. Os placeholders `workspace_path` e
`compute_id` evitam registrar caminhos privados e identificadores do workspace.

O Job foi publicado e executado no workspace Databricks com as três tarefas
dependentes. O JSON é a referência versionada de configuração, enquanto os
resultados da execução estão registrados em
[`gold_execution_evidence.md`](../artifacts/audit/gold_execution_evidence.md).
O screenshot do grafo está em
[`gold_workflow_execution_evidence.png`](../artifacts/audit/gold_workflow_execution_evidence.png).
