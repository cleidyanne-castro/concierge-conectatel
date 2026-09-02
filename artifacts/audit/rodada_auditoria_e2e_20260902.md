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

## Revalidação após correção do Runtime

Em 02/09/2026, após a correção na versão 3 e a publicação da imagem definitiva
na versão 4 do AgentCore Runtime, foram reexecutados os desfechos pelo endpoint
público:

| Trace ID | Decisão | Resultado |
|---|---|---|
| `review-green-answer-20260902` | `responder` | HTTP 200, resposta fundamentada e fonte `data/corpus/faq/faq_geral.md`. |
| `review-green-unknown-20260902` | `nao_sei` | HTTP 200, resposta segura e `source_path` nulo. |
| `review-green-handoff-20260902` | `escalar` | HTTP 200, protocolo emitido e registro confirmado no DynamoDB. |

O erro 502 causado por sequência inválida de `ToolUse` do modelo Nova deixou de
ocorrer após a simplificação do contrato exposto pela tool de handoff. A
telemetria GenAI também passou a operar em modo `NO_CONTENT`: um teste com o
marcador inválido `00 00000-0000` não encontrou o valor bruto nos spans, enquanto
o evento funcional do trace `review-green-private-20260902` preservou a trilha
com `[TELEFONE_MASCARADO]`. Os quatro grupos de logs foram novamente confirmados
com retenção de 14 dias e não houve erro recente no gateway após o deploy.
