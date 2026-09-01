# Registro de contribuições — João Vitor Althaus Godoi

Parte 3 (Agente Concierge) e integração ponta a ponta com a AWS.

## Agente

- `src/parte_03_04_agente_triagem/agent_concierge.py` — agente **Strands** com
  duas ferramentas (`retrieve_kb`, `store_handoff`), rodando dentro do
  **Amazon Bedrock AgentCore Runtime**. Compõe respostas fundamentadas citando
  `source_path`, responde "não sei" quando a base não cobre, e escala nos casos
  da política. `ContextVar` por requisição deriva a decisão (`responder` /
  `nao_sei` / `escalar`) a partir dos efeitos das tools.
- `src/parte_03_04_agente_triagem/lambda_gateway.py` — Lambda de borda:
  API Gateway (HTTP API) → `bedrock-agentcore:InvokeAgentRuntime`. Gera o
  `trace_id` quando a interface não manda, devolve `X-Trace-Id` no header,
  falha segura para `nao_sei`.
- `src/cli.py` — entrada local (`python -m src.cli --question "..."`), mesmo
  `run()` do Runtime, para gerar transcrições sem depender do deploy.
- Validado local nos 3 caminhos: `responder` (com citação), `nao_sei`
  (sem inventar), `escalar` (handoff com os 10 campos).

## Contratos compartilhados

- `src/shared/config.py` — `get_settings()`: fonte única das variáveis de
  ambiente, um default por chave (resolve o threshold divergente em 3 lugares).
- `src/shared/types.py` — `Decision`, `RetrieveResult`, `HandoffRecord` (nomes
  idênticos à Política de Suporte), `ConciergeResponse`, `AuditEvent`,
  `Escalation`.

## Infraestrutura AWS

- `infra/template.yaml` (SAM, evoluído a partir do do Kaique) — cria o bucket S3
  como parâmetro (não recurso), Lambda `retrieve_kb` (imagem, 10240 MB por causa
  do cold start), Lambda `gateway` (zip), HTTP API com rotas `/retrieve` e
  `/concierge`.
- `infra/agentcore/` — `Dockerfile` do agente (ARM64, `/invocations` + `/ping`),
  `runtime.json` (`create-agent-runtime`), `lambda-invoke-policy.json`,
  `README.md` com o passo a passo do Runtime.
- `infra/DEPLOY.md` — deploy do zero para quem nunca usou Docker/AWS (SSO,
  bucket, `sam build`/`deploy`, troubleshooting).
- `infra/README.md` — visão dos componentes e ordem de deploy.
- `src/parte_02_rag/upload_to_s3.py` — ajustado para ler bucket/região do
  ambiente, sem `AWS_PROFILE` fixo; `Makefile` com `seed-kb` / `deploy`.

## Deploy executado 

- Stack SAM `concierge-conectatel`: `retrieve_kb` + HTTP API no ar.
- AgentCore Runtime `concierge_agent-OGCvl4G9Yj` (status READY), imagem em
  `bedrock-agentcore-concierge_agent`, execution role com invoke das tools.
- Teste `invoke-agent-runtime`: `statusCode 200`, `decision "responder"` com
  fonte citada.
- Modelo: `amazon.nova-lite-v1:0` 

## Handoff para as Partes 4 e 5

- `docs/proximas_etapas_04_05.md` — contrato do `store_handoff`, esquema
  DynamoDB, snippet do `template.yaml`, guardrail determinístico, e como a
  Parte 5 consulta por `trace_id` (Logs Insights, < 60 s).
