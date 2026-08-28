# Parte 4: Triagem e escalonamento

Esta pasta documenta os critérios para decidir quando responder, informar falta
de evidência ou encaminhar a solicitação para atendimento humano.

## Responsabilidades

- definir política de suporte.
- classificar urgência e necessidade de encaminhamento.
- gerar o handoff com contexto suficiente.
- preservar a decisão para auditoria.

## Integração

Os módulos de implementação estão em `src/parte_04_triagem/`. A triagem
recebe a decisão do agente e entrega o handoff para a Governança.
