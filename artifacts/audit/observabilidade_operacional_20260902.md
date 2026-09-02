# Evidência - observabilidade operacional

**Data:** 02/09/2026
**Região:** `us-east-1`
**Stack:** `conectatel`

## Recursos publicados

| Recurso | Nome | Finalidade |
|---|---|---|
| Dashboard CloudWatch | `concierge-conectatel-operacao` | Visualizar invocações, erros, duração p95, decisões e handoffs. |
| Alarme padrão | `concierge-conectatel-gateway-errors` | Sinalizar erro da Lambda de borda em janela de 5 min. |
| Alarme padrão | `concierge-conectatel-retrieve-kb-errors` | Sinalizar erro da tool RAG em janela de 5 min. |
| Filtros de métrica | `RespondDecisions`, `NoAnswerDecisions`, `EscalateDecisions` | Contabilizar decisões a partir dos eventos JSON da gateway. |

## Verificação pós-deploy

O CloudFormation confirmou o dashboard e os três filtros de métrica com estado
`CREATE_COMPLETE`; os dois alarmes também foram publicados na mesma stack.
Na checagem inicial, o alarme da gateway estava em `OK`. O alarme RAG estava em
`INSUFFICIENT_DATA`, comportamento esperado até a primeira métrica após sua
criação; a propriedade `TreatMissingData: notBreaching` impede que ausência de
tráfego seja interpretada como incidente.

## Uso durante a banca

1. Abrir o dashboard no CloudWatch.
2. Executar um caso grounded, um `nao_sei` e um handoff pela interface.
3. Mostrar a mudança nas invocações e na tabela de decisões.
4. Se houver erro, abrir a consulta de auditoria pelo `trace_id` exibido pela
   interface.

O dashboard usa métricas nativas e três métricas customizadas de decisão,
alimentadas por filtros no log do gateway. Isso permanece dentro da cota
gratuita de dez métricas customizadas. Não foram criados alarmes de alta
resolução ou ações automáticas.

## Limite da evidência funcional

Uma chamada de alimentação posterior ao deploy retornou `502` no gateway. A
consulta do log pelo `trace_id` mostrou que a origem foi o AgentCore: o modelo
retornou `modelStreamErrorException` por sequência inválida de `ToolUse`. O
alarme de erros do gateway passa a sinalizar esse tipo de ocorrência; a correção
da orquestração do agente deve ser tratada pela frente responsável, sem alterar
os controles de observabilidade desta entrega.
