# Parte 3 — Agente Concierge

## Arquivos

| Arquivo | O que é | Onde roda |
|---|---|---|
| `agent_concierge.py` | Agente Strands (modelo Bedrock + 2 tools) e entrypoint do container | **AgentCore Runtime** (`app.run()` serve `/invocations` + `/ping`) |
| `lambda_gateway.py` | Ponte HTTP: API Gateway → `InvokeAgentRuntime` | **Lambda** `.zip` atrás do HTTP API |
| `agent-requirements.txt` | Deps do container do agente (`strands-agents`, `bedrock-agentcore`, `boto3`) | build da imagem |
| `../../src/cli.py` | Entrada local: `python -m src.cli --question "..."` — chama `run()` direto | dev |

## Fluxo (`run(payload)`)

1. Extrai `question` + `trace_id`.
2. `agent(question)` — o LLM decide chamar `retrieve_kb` e/ou `store_handoff`.
3. Um `ContextVar` guarda os efeitos das tools (último retrieve, handoff gerado).
4. `_build_response` deriva a `ConciergeResponse` (`decision`, `source_path`, `handoff`).
5. `_emit_audit` → `AuditEvent` JSON no CloudWatch.

Tipos e config vêm de [`src/shared/`](../shared/). Decisão: `responder | nao_sei | escalar`.

## Deploy

- Container do agente: [`infra/agentcore/`](../../infra/agentcore/) (Dockerfile + `runtime.json`).
- Gateway + API: [`infra/template.yaml`](../../infra/template.yaml) (SAM).
- Passo a passo: [`infra/DEPLOY.md`](../../infra/DEPLOY.md).

## Modelo

`amazon.nova-lite-v1:0` (on-demand, sem formulário). Para Claude
(`us.anthropic.claude-haiku-4-5-20251001-v1:0`) é preciso preencher o
"Anthropic use case details" no console Bedrock antes.
