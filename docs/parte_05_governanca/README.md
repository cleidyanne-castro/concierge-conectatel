# Parte 5: Governança e auditoria

Esta pasta documenta a rastreabilidade das interações e os controles de
segurança, custo e observabilidade do projeto.

## Responsabilidades

- registrar `trace_id`, pergunta, fontes e decisão.
- permitir consulta do registro no prazo definido pelo desafio.
- documentar guardrails, IAM e riscos.
- acompanhar custos e limpeza de recursos.
- manter evidências reproduzíveis.

## Integração

Os módulos de implementação estão em `src/parte_05_governanca/`. As evidências
operacionais complementares ficam em `docs/qa/` e `artifacts/audit/`.

O procedimento de consulta por `trace_id`, as permissões envolvidas e os
controles operacionais estão em [`operacao_auditoria.md`](operacao_auditoria.md).

A matriz de IAM, guardrails, riscos, custos e checklist pré-demo está em
[`controles_governanca.md`](controles_governanca.md).

## Observabilidade operacional

O deploy cria o dashboard CloudWatch `concierge-conectatel-operacao`. Ele mostra
invocações, erros e latência p95 do gateway e da tool RAG, distribuição das
decisões do Concierge e as operações `PutItem` que representam handoffs. As
três decisões são convertidas em métricas pelo filtro de logs do gateway.

Dois alarmes padrão complementam a visualização:

- `concierge-conectatel-gateway-errors`;
- `concierge-conectatel-retrieve-kb-errors`.

O alarme do gateway entra em estado `ALARM` quando há erro tratado ou não
tratado registrado pela aplicação; o da RAG acompanha falhas não tratadas da
Lambda. Ambos avaliam janelas de cinco minutos e não possuem ação automática: na
demonstração, o operador investiga o `trace_id` no CloudWatch antes de qualquer
ação corretiva. A configuração usa métricas nativas e três métricas customizadas
de decisão, além de uma métrica de erro da gateway, dentro da cota gratuita de
dez métricas customizadas.
