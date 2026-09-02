# Evidência - auditoria ponta a ponta

**Data:** 02/09/2026  
**Ambiente:** AWS `us-east-1`, conta de demonstração  
**Caso:** escalonamento por roubo de aparelho e suspeita de uso indevido  
**Trace ID:** `e2e-handoff-20260901`

## Consulta executada

```bash
AWS_PROFILE=AlunoAdmin-699038657189 AWS_REGION=us-east-1 \
python -m src.parte_05_governanca.audit \
  --trace-id e2e-handoff-20260901 \
  --log-group /aws/lambda/concierge-conectatel-gateway \
  --log-group /aws/lambda/concierge-conectatel-retrieve-kb \
  --log-group /aws/lambda/concierge-conectatel-store-handoff \
  --log-group /aws/bedrock-agentcore/runtimes/concierge_conectatel_agent-Sk4fyE6R6C-DEFAULT \
  --lookback-minutes 120
```

## Resultado

- Tempo total medido: **3,814 s** (meta do desafio: até 60 s).
- O gateway registrou o recebimento da interação e a decisão `escalar`.
- O AgentCore retornou o evento estruturado com a pergunta original, decisão
  `escalar`, `trace_id` e guardrail `titularidade/falecimento`.
- A resposta ao assinante incluiu o protocolo
  `CONCTL-20260901-6BFEA6`.
- O item com o mesmo `trace_id` foi confirmado na tabela DynamoDB
  `concierge-conectatel-escalonamentos`, com urgência `alta`.

## Controles confirmados

- Retenção de 14 dias nos log groups do gateway, `retrieve_kb`,
  `store_handoff` e AgentCore.
- Budget de custo ativo com limite de US$ 20 na conta de demonstração.
- Consulta preparada por script versionado, sem depender de pesquisa manual no
  console durante a demonstração.

## Cobertura complementar

Dois novos testes foram executados pelo endpoint público do Concierge e
consultados no log do AgentCore pelo mesmo procedimento:

| Trace ID | Decisão | Evidência no evento de auditoria |
|---|---|---|
| `e2e-grounded-20260902` | `responder` | Pergunta, fontes `faq_geral.md` e `procedimento_desbloqueio_aparelho.md`, score `0.9114` e guardrail nulo. |
| `e2e-no-source-20260902` | `nao_sei` | Pergunta, lista de fontes vazia, score nulo e guardrail nulo. |

Com o caso de handoff acima, a evidência cobre os três desfechos do
Concierge: resposta fundamentada, recusa segura por ausência de fonte e
escalonamento para atendimento humano.
