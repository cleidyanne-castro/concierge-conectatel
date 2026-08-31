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
