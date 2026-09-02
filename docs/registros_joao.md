# Registro de contribuições — João Vitor Althaus Godoi

Parte 3 (Agente Concierge) e integração ponta a ponta com a AWS.

## Agente

- `src/parte_03_04_agente_triagem/agent_concierge.py` — agente **Strands** com
  duas ferramentas (`retrieve_kb`, `store_handoff`), rodando dentro do
  **Amazon Bedrock AgentCore Runtime**. Compõe respostas fundamentadas citando
  `source_path`, responde "não sei" quando a base não cobre, e escala nos casos
  da política. Um `ContextVar` por requisição registra os efeitos das ferramentas
  e o entrypoint deriva a decisão (`responder` / `nao_sei` / `escalar`) em código
  — o texto do modelo sozinho não carrega essa classificação.
- `src/parte_03_04_agente_triagem/lambda_gateway.py` — Lambda de borda:
  API Gateway (HTTP API) → `bedrock-agentcore:InvokeAgentRuntime`. Origem canônica
  do `trace_id` (gera quando a requisição não traz), devolve `X-Trace-Id` no
  cabeçalho e falha segura para `nao_sei`.
- `src/cli.py` — entrada local (`python -m src.cli --question "..."`), mesmo
  `run()` do Runtime, para gerar transcrições.
- `system_prompt` com seis regras (busca antes de responder, citar fonte, "não
  sei" sem inferência, escalonamento, não prometer o que não está na fonte, não
  vazar raciocínio interno) e guardrails determinísticos (limiar na ferramenta de
  busca, remoção de blocos de raciocínio, classificação em código).

## Contratos compartilhados

- `src/shared/config.py` — `get_settings()`: fonte única das variáveis de
  ambiente, um default por chave (resolve o limiar que estava divergente em três
  lugares do repositório).
- `src/shared/types.py` — `Decision`, `RetrieveResult`, `HandoffRecord` (nomes
  idênticos à Política de Suporte e Escalonamento), `ConciergeResponse`,
  `AuditEvent`, `Escalation` — o vocabulário usado pelas Partes 3, 4 e 5.

## Modelo

Escolha inicial: **Claude Haiku 4.5** (robustez em uso de ferramentas). Ao
integrar via Strands, a conta retornou `ResourceNotFoundException: Model use case
details have not been submitted` — o Bedrock exige o formulário de caso de uso da
Anthropic antes de liberar Claude por streaming. Para não bloquear a entrega, o
agente passou a usar **`amazon.nova-lite-v1:0`** (on-demand, sem formulário). O
modelo é uma variável de ambiente (`BEDROCK_MODEL_ID`), então voltar ao Claude é
troca de configuração, sem alterar código.

## Infraestrutura AWS

- `infra/template.yaml` (SAM) — evolução do template do Kaique: adição da Lambda
  `gateway` e do wiring das ferramentas; o bucket S3 passou a ser parâmetro (o
  stack só lê dele); parâmetro `AgentRuntimeArn` para o gateway alcançar o
  Runtime; Dockerfile da `retrieve_kb` movido para `infra/`.
- `infra/agentcore/` — `Dockerfile` do agente (ARM64, `/invocations` + `/ping`),
  `runtime.json` (`create-agent-runtime`), `lambda-invoke-policy.json` e `README.md`
  com o passo a passo do Runtime.
- `infra/DEPLOY.md` — deploy do zero para quem nunca usou Docker/AWS (instalação,
  sessão SSO, bucket, `sam build`/`deploy`, troubleshooting).
- `infra/README.md` — componentes e ordem de deploy (bucket → Runtime → SAM).
- `README.md` (raiz) — seção de deploy completa, account-agnostic, para
  reprodução por pessoa externa.
- `src/parte_02_rag/upload_to_s3.py` — ajustado para ler bucket e região do
  ambiente, sem `AWS_PROFILE` fixo.

## Deploy e validação

- Stack SAM `concierge-conectatel` publicada: Lambdas `retrieve_kb`, `gateway`,
  API Gateway HTTP com as rotas `/concierge` e `/retrieve`.
- AgentCore Runtime publicado (status `READY`), imagem no ECR, execution role com
  permissão de invocar as Lambdas-ferramenta e o modelo Bedrock.
- Validação ponta a ponta pelo endpoint `/concierge` (API Gateway → gateway →
  Runtime → ferramentas), cobrindo os três caminhos: `responder` com fonte
  citada, `nao_sei` sem inferência e `escalar` com o registro persistido em
  DynamoDB. `trace_id` propagado por toda a cadeia.

## Contratos documentados para as Partes 4 e 5

- `docs/proximas_etapas_04_05.md` — contrato de entrada/saída do `store_handoff`,
  esquema da tabela DynamoDB, snippet do `template.yaml`, guardrail determinístico
  dos oito critérios e como a Parte 5 consulta a auditoria por `trace_id`
  (CloudWatch Logs Insights, SLA de 60 s).
