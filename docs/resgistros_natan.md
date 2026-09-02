# Registros de Natan Alencar

## Observabilidade operacional

- criação inicial do dashboard `concierge-conectatel-operacao`, dos alarmes de erro do gateway e da tool `retrieve_kb` e dos filtros de métrica de decisão (`RespondDecisions`, `NoAnswerDecisions`, `EscalateDecisions`, `GatewayRuntimeErrors`).
- verificação pós-deploy dos recursos publicados via CloudFormation, incluindo o comportamento esperado do alarme RAG em `INSUFFICIENT_DATA` antes da primeira métrica.
- evolução da stack para remover o dashboard agregado, preservando log group, filtros de métrica, alarmes, retenção e auditoria por `trace_id`.
- diagnóstico e correção de uma regressão de HTTP 502 no gateway, causada por sequência inválida de `ToolUse` no AgentCore, com simplificação do contrato da tool e atualização do Runtime.

O detalhamento e a evidência histórica estão em [`docs/parte_05_governanca/evidencia_observabilidade_operacional.md`](parte_05_governanca/evidencia_observabilidade_operacional.md).

## Auditoria ponta a ponta

- execução da consulta de auditoria por `trace_id` cobrindo gateway, `retrieve_kb`, `store_handoff` e AgentCore, validando o tempo de resposta dentro da meta do desafio.
- confirmação do fluxo completo de escalonamento, com decisão, guardrail, protocolo emitido e registro correspondente localizado no DynamoDB.
- cobertura complementar dos três desfechos do Concierge (`responder`, `nao_sei`, `escalar`) com evidência de evento estruturado para cada caso.
- revalidação dos três desfechos pelo endpoint público após a correção do Runtime, confirmando HTTP 200 e consistência da trilha de auditoria.

A evidência completa está em [`docs/parte_05_governanca/evidencia_auditoria_ponta_a_ponta.md`](parte_05_governanca/evidencia_auditoria_ponta_a_ponta.md).

## Evidência formal de banca

- validação do caso T01, com resposta fundamentada, score acima do limiar e fonte vigente confirmada tanto na chamada direta quanto na consulta ao CloudWatch.
- validação do caso T02, com decisão segura `nao_sei` para pergunta fora do corpus, também confirmada via CloudWatch.
- execução do caso T08, com a suíte local de testes e a validação do template SAM.
- registro do limite conhecido da integração parcial, em que fonte e guardrail ainda não constam no evento consolidado da Lambda isolada.

A evidência está em [`docs/parte_05_governanca/evidencia_t01_t02_t08.md`](parte_05_governanca/evidencia_t01_t02_t08.md).

## Proteção de dados sensíveis na telemetria

- validação do modo `NO_CONTENT` na telemetria GenAI, confirmando que um marcador inválido de telefone não aparece em texto puro nos spans.
- confirmação, em trace funcional, de que a trilha preserva o dado mascarado em vez do valor original.
- reconfirmação da retenção de 14 dias nos quatro grupos de logs envolvidos no fluxo do Concierge.

## Rastreabilidade

Os commits e Pull Requests associados às contribuições ficam registrados no
histórico do GitHub, na branch `fix/handoff-sem-dashboard-operacional`.