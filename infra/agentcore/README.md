# AgentCore Runtime — deploy do agente Concierge

O agente (`src/parte_03_04_agente_triagem/agent_concierge.py`) roda no **Amazon
Bedrock AgentCore Runtime** como um container ARM64. O SAM (`infra/template.yaml`)
**não** cria o Runtime — ele é criado pelos passos abaixo, e o `sam deploy`
depois recebe o ARN resultante no parâmetro `AgentRuntimeArn`.

## Arquivos desta pasta

| Arquivo | Função |
|---|---|
| `Dockerfile` | imagem do agente (ARM64, porta 8080, `/invocations` + `/ping`) |
| `runtime.json` | input do `create-agent-runtime` (container URI, role, env vars) |
| `lambda-invoke-policy.json` | policy que dá ao Runtime permissão de invocar as Lambdas-tool |

> **Valores específicos da conta** nos JSON: account id `699038657189`, região
> `us-east-1`, nome de repo ECR e ARN do runtime. Outra conta/squad precisa
> editar `runtime.json` e `lambda-invoke-policy.json`.

## Pré-requisitos

- Docker Desktop rodando (build ARM64 roda via emulação no Windows/Mac Intel).
- Sessão AWS ativa: `aws sso login --profile <perfil>` + `$env:AWS_PROFILE`.
- Modelo Bedrock com acesso na conta. `amazon.nova-lite-v1:0` roda on-demand
  sem formulário. Para Claude, preencher antes o "Anthropic use case details"
  no console Bedrock > Model access.
- As Lambdas-tool devem existir (ou serão criadas depois): `concierge-conectatel-retrieve-kb`
  (Parte 2, já no ar) e `concierge-conectatel-store-handoff` (Parte 4).

## Passo a passo (primeira criação)

Da **raiz do repo**:

```powershell
$env:AWS_PROFILE = "AlunoAdmin-699038657189"
$ACCT = "699038657189"; $REGION = "us-east-1"
$ECR  = "$ACCT.dkr.ecr.$REGION.amazonaws.com/bedrock-agentcore-concierge-agent"
```

### 1. ECR + login

```powershell
aws ecr create-repository --repository-name bedrock-agentcore-concierge-agent --region $REGION
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin "$ACCT.dkr.ecr.$REGION.amazonaws.com"
```

### 2. Build ARM64 + push

```powershell
docker build --platform linux/arm64 -f infra/agentcore/Dockerfile -t "${ECR}:latest" .
docker push "${ECR}:latest"
```

### 3. Execution role

Criar uma role com trust em `bedrock-agentcore.amazonaws.com` e as permissões de
Bedrock/CloudWatch/X-Ray. O jeito mais rápido é deixar a AWS criar via
`bedrock-agentcore-starter-toolkit` (`agentcore configure` responde "auto-create"),
que gera `AmazonBedrockAgentCoreSDKRuntime-*` com a policy padrão. Depois,
adicionar a permissão de invocar as tools:

```powershell
aws iam put-role-policy `
  --role-name ConciergeConectaTelAgentCoreRuntimeRole `
  --policy-name concierge-tools-invoke `
  --policy-document file://infra/agentcore/lambda-invoke-policy.json
```

(Se criar a role manualmente: trust em `bedrock-agentcore.amazonaws.com`;
permissões `bedrock:InvokeModel*`, `logs:*`, `xray:PutTraceSegments/PutTelemetryRecords`,
`cloudwatch:PutMetricData`, `ecr:BatchGetImage/GetDownloadUrlForLayer/GetAuthorizationToken`,
mais o conteúdo de `lambda-invoke-policy.json`.)

### 4. Criar o Runtime

Confira `runtime.json` (containerUri, roleArn, env vars) e:

```powershell
aws bedrock-agentcore-control create-agent-runtime --region $REGION --cli-input-json file://infra/agentcore/runtime.json
```

Anote o `agentRuntimeArn` e o `agentRuntimeId` da saída.

### 5. Verificar e testar

```powershell
aws bedrock-agentcore-control get-agent-runtime --agent-runtime-id <ID> --region $REGION --query status

$sid = "smoke-" + [guid]::NewGuid().ToString("N")
[System.IO.File]::WriteAllText("$env:TEMP\p.json", '{"question":"Qual e o prazo para contestar uma cobranca da fatura?","trace_id":"smoke-1"}')
aws bedrock-agentcore invoke-agent-runtime --region $REGION `
  --agent-runtime-arn "<ARN>" --runtime-session-id $sid `
  --payload "fileb://$env:TEMP/p.json" --content-type application/json --accept application/json `
  "$env:TEMP\resp.json"
Get-Content "$env:TEMP\resp.json" -Raw
```

Esperado: `{"decision":"responder", "trace_id":"smoke-1", "answer":"...", "source_path":"..."}`.

### 6. Ligar no resto da infra

Rodar `sam deploy` passando o ARN:

```powershell
sam deploy --parameter-overrides AgentRuntimeArn=<ARN> KnowledgeBaseBucketName=$env:S3_BUCKET_NAME
```

(ou fixar o ARN no `samconfig.toml`).

## Atualizar o agente (novo código / observabilidade)

```powershell
docker build --platform linux/arm64 -f infra/agentcore/Dockerfile -t "${ECR}:latest" .
docker push "${ECR}:latest"
aws bedrock-agentcore-control update-agent-runtime --agent-runtime-id <ID> --region $REGION `
  --agent-runtime-artifact '{"containerConfiguration":{"containerUri":"'"${ECR}:latest"'"}}'
```

## Observabilidade (traces OTEL)

- Container já instrumentado: `aws-opentelemetry-distro` + `opentelemetry-instrument` no CMD.
- A captura de prompts, respostas e argumentos de tools está desabilitada por
  `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=NO_CONTENT`; métricas,
  traces e os eventos de auditoria sanitizados continuam disponíveis.
- Habilitar uma vez por conta: **CloudWatch → Settings → Transaction Search → Enable**.
- Ver traces: **CloudWatch → GenAI Observability → Bedrock AgentCore**.
- Independente disso, os logs `AuditEvent` (JSON com `trace_id`) já vão pro log
  group `/aws/bedrock-agentcore/runtimes/<ID>-*`.

## Limpeza

```powershell
aws bedrock-agentcore-control delete-agent-runtime --agent-runtime-id <ID> --region $REGION
aws ecr delete-repository --repository-name bedrock-agentcore-concierge-agent --force --region $REGION
```
