# Infraestrutura AWS

Configuração reproduzível e sem segredos. Credenciais AWS vêm sempre do
ambiente (`aws sso login` / `AWS_PROFILE`) — nunca deste diretório.

## Componentes

| Componente | Como sobe | Arquivo |
|---|---|---|
| Bucket S3 da base de conhecimento | criado **à mão** (`aws s3 mb`); o stack só lê | — |
| Lambda `retrieve_kb` (imagem) + HTTP API | SAM | [`template.yaml`](template.yaml), [`retrieve_kb.Dockerfile`](retrieve_kb.Dockerfile) |
| Lambda `gateway` (zip) — API Gateway → AgentCore | SAM | [`template.yaml`](template.yaml) |
| **AgentCore Runtime** (container do agente) | CLI `bedrock-agentcore-control` | [`agentcore/`](agentcore/) |
| Lambda `store_handoff` + DynamoDB | SAM (Parte 4) | ver [`../docs/proximas_etapas_04_05.md`](../docs/proximas_etapas_04_05.md) |
| Workflow Databricks Bronze→Silver→Gold | Job no workspace | [`databricks_workflow_gold.json`](databricks_workflow_gold.json) |

O Job foi publicado e executado no workspace Databricks com as três tarefas
dependentes. O JSON é a referência versionada de configuração, enquanto os
resultados da execução estão registrados em
[`gold_execution_evidence.md`](../artifacts/audit/gold_execution_evidence.md).
O screenshot do grafo está em
[`gold_workflow_execution_evidence.png`](../artifacts/audit/gold_workflow_execution_evidence.png).
## Ordem de deploy (do zero)

Ferramentas e credenciais: [`DEPLOY.md`](DEPLOY.md) passos 1–3.

1. **Criar o bucket S3** e semear os artefatos — [`DEPLOY.md`](DEPLOY.md) passos 4–5
   (`aws s3 mb` + `aws s3 cp` de `index/embeddings.json` e `processed/chunks.json`).
2. **AgentCore Runtime** — [`agentcore/README.md`](agentcore/README.md) passos 1–5.
   Guardar o `agentRuntimeArn`.
3. **Stack SAM** — `sam build` + `sam deploy`, passando os parâmetros:
   ```
   sam deploy --parameter-overrides \
     AgentRuntimeArn=<ARN do passo 2> \
     KnowledgeBaseBucketName=<bucket do passo 1>
   ```
   Sobe `retrieve_kb`, `gateway` e o HTTP API. Output `ConciergeApiUrl` é o endpoint.
4. **Parte 4** — adicionar `store_handoff` + DynamoDB ao `template.yaml` e
   `sam deploy` de novo (o agente já invoca pelo nome).

## Parâmetros do `template.yaml`

| Parâmetro | Default | Observação |
|---|---|---|
| `KnowledgeBaseBucketName` | `concierge-conectatel-kb-squad4` | bucket já existente; o stack só lê |
| `AgentRuntimeArn` | ARN do runtime da squad (conta `582766763753`) | **trocar para outra conta** |
| `CorsAllowOrigin` | `*` | restringir à origem da interface em produção |

## Valores específicos da conta da squad

Trocar ao reproduzir em outra conta AWS:

- `infra/agentcore/runtime.json` — `containerUri`, `roleArn`, account id
- `infra/agentcore/lambda-invoke-policy.json` — ARNs das Lambdas (account id)
- `template.yaml` parâmetro `AgentRuntimeArn`
- `samconfig.toml` — `parameter_overrides` (bucket)

## Limpeza de recursos

```powershell
sam delete --stack-name concierge-conectatel
aws bedrock-agentcore-control delete-agent-runtime --agent-runtime-id <ID> --region us-east-1
aws ecr delete-repository --repository-name bedrock-agentcore-concierge_agent --force --region us-east-1
aws s3 rb s3://<bucket> --force
```

IAM de menor privilégio, guardrails, AWS Budgets e riscos: responsabilidade da
Parte 5 — ver [`../docs/proximas_etapas_04_05.md`](../docs/proximas_etapas_04_05.md).
