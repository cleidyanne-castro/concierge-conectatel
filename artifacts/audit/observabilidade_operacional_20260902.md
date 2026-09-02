# Evidência histórica - observabilidade operacional

> Esta evidência registra o estado implantado em 02/09/2026. A configuração
> atual remove o dashboard agregado, mas preserva log group, filtros de métrica,
> alarmes, retenção e auditoria por `trace_id`.

**Data:** 02/09/2026
**Região:** `us-east-1`
**Stack:** `conectatel`

## Recursos publicados

| Recurso | Nome | Finalidade |
|---|---|---|
| Dashboard CloudWatch | `concierge-conectatel-operacao` | Visualizar invocações, erros, duração p95, decisões e handoffs. |
| Alarme padrão | `concierge-conectatel-gateway-errors` | Sinalizar erro da Lambda de borda em janela de 5 min. |
| Alarme padrão | `concierge-conectatel-retrieve-kb-errors` | Sinalizar erro da tool RAG em janela de 5 min. |
| Filtros de métrica | `RespondDecisions`, `NoAnswerDecisions`, `EscalateDecisions`, `GatewayRuntimeErrors` | Contabilizar decisões e erros tratados a partir dos eventos JSON da gateway. |

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

O dashboard usa métricas nativas e quatro métricas customizadas de decisão e
erro tratado,
alimentadas por filtros no log do gateway. Isso permanece dentro da cota
gratuita de dez métricas customizadas. Não foram criados alarmes de alta
resolução ou ações automáticas.

## Revalidação da evidência funcional

Uma chamada posterior ao primeiro deploy retornou `502` no gateway. A consulta
pelo `trace_id` localizou uma sequência inválida de `ToolUse` no AgentCore. O
contrato da tool foi simplificado, o Runtime foi atualizado e os três desfechos
(`responder`, `nao_sei` e `escalar`) voltaram a responder HTTP 200. O alarme do
gateway continua sinalizando uma eventual regressão pelo mesmo evento
estruturado. Para instalações do zero, o log group usado pelos filtros agora é
criado declarativamente antes da Lambda e mantém retenção de 14 dias.
