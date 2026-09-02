# Concierge ConectaTel

Assistente GenAI de atendimento para a operadora fictícia ConectaTel: pipeline de
dados, RAG sobre o corpus oficial com filtro determinístico de vigência, agente
que responde com fonte citada / "não sei" / escalonamento com handoff, e trilha
de auditoria por `trace_id`.

Este README é um guia de execução completo. Uma pessoa fora da squad consegue,
seguindo apenas este documento: instalar o projeto, rodar os testes, rodar o
agente localmente, subir toda a infraestrutura na sua própria conta AWS e validar
o fluxo ponta a ponta. Os guias [`infra/DEPLOY.md`](infra/DEPLOY.md) (passo a
passo para quem nunca usou Docker/AWS) e
[`infra/agentcore/README.md`](infra/agentcore/README.md) (detalhe do Runtime) são
complementares.

---

## 1. Arquitetura

![Arquitetura final do Concierge ConectaTel](docs/arquitetura/arquitetura_conectatel_final.jpg)

Arquivos: [arquitetura planejada](docs/arquitetura/arquitetura_conectatel_planejada.jpg),
[arquitetura final](docs/arquitetura/arquitetura_conectatel_final.jpg),
[planejado × executado](docs/arquitetura/planejado_vs_executado.md).

**Fluxo de uma pergunta:**

```
Interface / cliente HTTP
      │  POST /concierge  {question, trace_id?}
      ▼
API Gateway (HTTP API)
      ▼
Lambda gateway ──► bedrock-agentcore:InvokeAgentRuntime
      ▼
AgentCore Runtime (container do agente Strands)
      ├─ tool retrieve_kb  ─► Lambda retrieve_kb ─► S3 (índice vetorial); filtro status=vigente + limiar
      └─ tool store_handoff ─► Lambda store_handoff ─► DynamoDB (escalonamentos)
      ▼
Resposta {decision: responder | nao_sei | escalar, answer, source_path, handoff?}
      +  AuditEvent (JSON) ─► CloudWatch  ─►  consulta por trace_id < 60s
```

O pipeline Bronze/Silver/Gold (Databricks) e a geração de embeddings alimentam o
índice no S3 e são pré-requisito da busca.

---

## 2. Estrutura do repositório

| Caminho | Conteúdo |
|---|---|
| `src/parte_01_dados/` | pipeline Medallion (notebooks + módulos) |
| `src/parte_02_rag/` | chunking, embeddings, índice vetorial, `upload_to_s3.py` |
| `src/tools/retrieve_kb/` | Lambda da tool de busca (imagem Docker) |
| `src/parte_03_04_agente_triagem/` | `agent_concierge.py` (agente no Runtime), `lambda_gateway.py` (borda), `store_handoff_lambda.py` (persistência) |
| `src/parte_05_governanca/` | `audit.py` (`find_by_trace_id`), `log_retention.py` |
| `src/shared/` | `config.py` (`get_settings()`), `types.py` (contratos entre partes), `security.py` |
| `src/interface/` | painel Streamlit de testes |
| `src/cli.py` | entrada local do agente |
| `infra/` | `template.yaml` (SAM), `retrieve_kb.Dockerfile`, `agentcore/` (Runtime), `DEPLOY.md` |
| `tests/` | testes espelhados por parte |
| `docs/` | contratos, decisões, arquitetura, QA, transcrições |
| `artifacts/` | evidências versionadas de execução |

---

## 3. Pré-requisitos

**Rodar localmente (testes, CLI, interface):**

- Python 3.11+.
- Sessão AWS ativa com acesso a Amazon Bedrock (`bedrock:InvokeModel*`) e
  `lambda:InvokeFunction` na Lambda `concierge-conectatel-retrieve-kb`.
  A CLI do agente e a interface **chamam recursos na AWS** — não há modo 100%
  offline: a tool de busca sempre invoca a Lambda e o modelo sempre é o Bedrock.

**Subir a infraestrutura, além do acima:**

- **AWS CLI v2** — `winget install Amazon.AWSCLI` ou [instalador oficial](https://aws.amazon.com/cli/).
- **AWS SAM CLI** — `winget install Amazon.SAM-CLI`.
- **Docker Desktop** — necessário para `sam build` (a Lambda de busca é imagem,
  traz `torch` + modelo de embeddings) e para o build ARM64 do container do agente.
- Conta AWS com permissão de criar S3, Lambda, API Gateway, ECR, IAM roles,
  DynamoDB, CloudWatch e recursos do Bedrock AgentCore.
- **Acesso a um modelo Bedrock.** `amazon.nova-lite-v1:0` funciona sob demanda
  sem formulário. Modelos Claude exigem antes o "Anthropic use case details"
  no console Bedrock → Model access.

Nunca grave chaves AWS no repositório. Use `aws configure sso` ou `aws configure`.

---

## 4. Configuração inicial

```bash
git clone https://github.com/cleidyanne-castro/concierge-conectatel.git
cd concierge-conectatel
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` (arquivo local, fora do git):

| Variável | O que é |
|---|---|
| `AWS_REGION` | região dos recursos (o projeto usa `us-east-1`) |
| `AWS_PROFILE` | nome do seu profile da AWS CLI |
| `S3_BUCKET_NAME` | bucket da base de conhecimento — **nome único global**; você cria no passo 6.2 |
| `EMBEDDINGS_KEY` / `CHUNKS_KEY` | chaves no S3 (`index/embeddings.json`, `processed/chunks.json`) |
| `RETRIEVAL_SCORE_THRESHOLD` | limiar responder/não-sei (`0.85`, calibrado) |
| `RETRIEVAL_TOP_K` | nº de trechos retornados (`3`) |
| `BEDROCK_MODEL_ID` | modelo do agente (`amazon.nova-lite-v1:0`) |
| `RETRIEVE_KB_FUNCTION` / `STORE_HANDOFF_FUNCTION` | nomes das Lambdas-tool |
| `HANDOFF_TABLE_NAME` | tabela DynamoDB (`concierge-conectatel-escalonamentos`) |
| `CONCIERGE_API_URL` | endpoint `POST /concierge`; preencha após o passo 6.4 |
| `AUDIT_LOG_GROUP` | log group base da auditoria |

Ative a sessão AWS:

```powershell
aws sso login --profile <seu-profile>
$env:AWS_PROFILE = "<seu-profile>"
aws sts get-caller-identity   # confirma conta e role
```

---

## 5. Rodar localmente

### 5.1 Testes automatizados

```bash
python -m pytest -q     # ou: make test
```

### 5.2 Agente pela CLI

Requer dependências instaladas, sessão AWS ativa e a Lambda `retrieve_kb` já
publicada (passo 6). Chama o mesmo `run()` que o Runtime usa em produção.

```bash
python -m src.cli --question "Qual o prazo para contestar uma cobranca da fatura?"
```

Saída: JSON com `decision` (`responder` / `nao_sei` / `escalar`), `trace_id`,
`answer` e `source_path`. Use para gerar as transcrições.

### 5.3 Interface de testes (Streamlit)

```bash
python -m streamlit run src/interface/app.py     # ou: make ui
```

Testa dois fluxos: **Concierge ponta a ponta** (usa `CONCIERGE_API_URL`) e
**Busca RAG direta** (invoca `retrieve_kb`). Preencha `CONCIERGE_API_URL` no
`.env` com o output do passo 6.4.

---

## 6. Deploy completo na AWS

Ordem obrigatória: **bucket S3 → AgentCore Runtime → stack SAM**. O Runtime não é
criado pelo SAM; o SAM recebe o ARN dele como parâmetro.

### 6.1 Sessão AWS

```powershell
aws sso login --profile <seu-profile>
$env:AWS_PROFILE = "<seu-profile>"
```

### 6.2 Bucket S3 + base de conhecimento

O `template.yaml` **não cria** o bucket; ele só lê. Crie e semeie:

```powershell
$b = "<S3_BUCKET_NAME do seu .env>"
aws s3 mb "s3://$b" --region us-east-1
aws s3 cp artifacts/chunks/chunks.json          "s3://$b/processed/chunks.json"
aws s3 cp artifacts/embeddings/embeddings.json  "s3://$b/index/embeddings.json"
aws s3 ls "s3://$b" --recursive        # deve listar os 2 arquivos
```

(Alternativa: `make seed-kb`, que roda `upload_to_s3.py` lendo `S3_BUCKET_NAME` do ambiente.)

### 6.3 AgentCore Runtime

Detalhe completo em [`infra/agentcore/README.md`](infra/agentcore/README.md).
Resumo, da raiz do repo, com o Docker aberto:

1. **Ajuste os JSON para a SUA conta** — em `infra/agentcore/runtime.json` e
   `infra/agentcore/lambda-invoke-policy.json`, troque o account id, o
   `containerUri` (seu repo ECR) e o `roleArn`.
2. **ECR + build + push:**
   ```powershell
   $ACC = "<seu-account-id>"
   $ECR = "$ACC.dkr.ecr.us-east-1.amazonaws.com/bedrock-agentcore-concierge-agent"
   aws ecr create-repository --repository-name bedrock-agentcore-concierge-agent --region us-east-1
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin "$ACC.dkr.ecr.us-east-1.amazonaws.com"
   docker build --platform linux/arm64 -f infra/agentcore/Dockerfile -t "${ECR}:latest" .
   docker push "${ECR}:latest"
   ```
3. **Execution role** — role com trust em `bedrock-agentcore.amazonaws.com` e
   permissões de `bedrock:InvokeModel*`, `logs:*`, `xray:PutTraceSegments`,
   `cloudwatch:PutMetricData`, pull do ECR, mais o conteúdo de
   `lambda-invoke-policy.json`. Coloque o ARN dela em `runtime.json`.
4. **Criar o Runtime:**
   ```powershell
   aws bedrock-agentcore-control create-agent-runtime --region us-east-1 --cli-input-json file://infra/agentcore/runtime.json
   ```
   Anote o `agentRuntimeArn`; confirme `status: READY` com `get-agent-runtime`.

### 6.4 Stack SAM

```powershell
sam build
sam deploy --guided        # 1ª vez: grava samconfig.toml
```

No `--guided`: Stack `concierge-conectatel`; região `us-east-1`;
`KnowledgeBaseBucketName` = seu bucket; `AgentRuntimeArn` = ARN do passo 6.3;
`CorsAllowOrigin` = `*`; permitir criação de roles IAM = Y; criar repositórios
ECR gerenciados = Y. Deploys seguintes: só `sam deploy`.

Cria: Lambda `retrieve_kb` (imagem), Lambda `store_handoff`, tabela DynamoDB
`concierge-conectatel-escalonamentos`, Lambda `gateway`, HTTP API com rotas
`/concierge` e `/retrieve`.

### 6.5 Validação ponta a ponta

```powershell
aws cloudformation describe-stacks --stack-name concierge-conectatel --region us-east-1 --query "Stacks[0].Outputs" --output table
```

Pegue `ConciergeApiUrl` e teste os três caminhos:

```powershell
$u = "<ConciergeApiUrl>"
Invoke-RestMethod -Method Post -Uri $u -ContentType "application/json" -Body '{"question":"Qual o prazo para contestar uma cobranca da fatura?","trace_id":"t-responder"}'
Invoke-RestMethod -Method Post -Uri $u -ContentType "application/json" -Body '{"question":"Qual a previsao do tempo para amanha?","trace_id":"t-naosei"}'
Invoke-RestMethod -Method Post -Uri $u -ContentType "application/json" -Body '{"question":"Recebi uma cobranca de R$ 900 que nao reconheco, acho que foi golpe","trace_id":"t-escalar"}'
```

Esperado: `responder` com `source_path`; `nao_sei` sem fonte; `escalar` com
`handoff` e protocolo. Confirme o escalonamento na tabela:

```powershell
aws dynamodb get-item --table-name concierge-conectatel-escalonamentos --region us-east-1 --key '{\"trace_id\":{\"S\":\"t-escalar\"}}'
```

A primeira chamada tem cold start; a segunda responde em poucos segundos.

---

## 7. Partes 1 e 2 — dados e RAG

- **Parte 1 (pipeline):** notebooks
  [`01_bronze_ingestao.ipynb`](src/parte_01_dados/01_bronze_ingestao.ipynb),
  [`02_silver_limpeza.ipynb`](src/parte_01_dados/02_silver_limpeza.ipynb),
  [`03_gold_analise.ipynb`](src/parte_01_dados/03_gold_analise.ipynb), executados
  no Databricks; encadeamento versionado em
  [`infra/databricks_workflow_gold.json`](infra/databricks_workflow_gold.json).
  Documentação e evidências em [`docs/parte_01_dados/`](docs/parte_01_dados/) e
  [`artifacts/audit/`](artifacts/audit/).
- **Parte 2 (RAG):** chunking, embeddings e índice em
  [`src/parte_02_rag/`](src/parte_02_rag/). O filtro `status=vigente` ocorre
  **antes** da similaridade. Os artefatos prontos (`embeddings.json`,
  `chunks.json`) já estão em `artifacts/` e são o que o passo 6.2 sobe para o S3;
  regenerá-los é opcional. Stretch de acerto de versão:
  [`docs/parte_02_rag/version_accuracy.md`](docs/parte_02_rag/version_accuracy.md).

---

## 8. Governança e auditoria

Cada interação emite um `AuditEvent` JSON (pergunta, fontes, decisão, guardrail,
`trace_id`) para o CloudWatch. Para localizar uma interação inteira:

```bash
python -m src.parte_05_governanca.audit --trace-id <trace_id>
```

`find_by_trace_id()` consulta os log groups do gateway, do Runtime e das Lambdas
via Logs Insights, com SLA de 60 segundos. Retenção de logs: `make retention`.
IAM mínimo, guardrails, riscos e AWS Budgets em
[`docs/parte_05_governanca/`](docs/parte_05_governanca/).

---

## 9. Limpeza de recursos

```powershell
sam delete --stack-name concierge-conectatel
aws bedrock-agentcore-control delete-agent-runtime --agent-runtime-id <ID> --region us-east-1
aws ecr delete-repository --repository-name bedrock-agentcore-concierge-agent --force --region us-east-1
aws s3 rb "s3://<S3_BUCKET_NAME>" --force
```

---

## 10. Erros comuns

| Sintoma | Causa provável |
|---|---|
| `Unable to locate credentials` | faltou `$env:AWS_PROFILE` na janela, ou o SSO expirou (`aws sso login`) |
| `sam build` → `Docker is unreachable` | Docker Desktop não está rodando |
| `sam deploy` → parâmetro sem valor | passe `AgentRuntimeArn` e `KnowledgeBaseBucketName` (ou use `--guided`) |
| gateway responde `reason: erro_runtime` | `AGENT_RUNTIME_ARN` inválido (ARN incompleto ou com `<>`), ou Runtime não `READY` — ver `/aws/lambda/concierge-conectatel-gateway` |
| tudo retorna `nao_sei` | índice ausente no S3, limiar alto demais, ou nenhum documento `vigente` |
| `AccessDenied` no Bedrock | região, role/profile ou acesso ao modelo |
| `ResourceNotFoundException ... use case details` | modelo Claude sem o formulário Anthropic; use `amazon.nova-lite-v1:0` |
| 1ª chamada à API expira | cold start; repita |

---

## 11. Entrega

Código, documentação, testes, evidências e contratos das cinco partes. As
transcrições obrigatórias (10 a 15, cobrindo respostas com fonte, versão
revogada, "não sei", escalonamentos e consulta de `trace_id` em até 60 s) ficam
em [`docs/transcricoes/`](docs/transcricoes/). 
