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

O deploy mantém o log group gerenciado da gateway, quatro filtros de métricas e
dois alarmes no CloudWatch. As decisões `responder`, `nao_sei` e `escalar`, além
dos erros tratados da gateway, são convertidas em métricas a partir dos eventos
JSON. A auditoria por `trace_id` continua baseada nos logs estruturados.

Dois alarmes padrão complementam a visualização:

- `concierge-conectatel-gateway-errors`;
- `concierge-conectatel-retrieve-kb-errors`.

O alarme do gateway entra em estado `ALARM` quando há erro tratado ou não
tratado registrado pela aplicação; o da RAG acompanha falhas não tratadas da
Lambda. Ambos avaliam janelas de cinco minutos e não possuem ação automática: na
demonstração, o operador investiga o `trace_id` no CloudWatch antes de qualquer
ação corretiva. A configuração usa métricas nativas e três métricas customizadas
de decisão, além de uma métrica de erro da gateway, dentro da cota gratuita de
dez métricas customizadas. Nenhum dashboard operacional é provisionado.
