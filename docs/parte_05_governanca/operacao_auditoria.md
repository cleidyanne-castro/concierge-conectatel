# Operação de auditoria por `trace_id`

## Objetivo

Toda interação deve poder ser localizada em menos de 60 segundos a partir do
seu `trace_id`. A fonte de verdade é o CloudWatch Logs; não mantemos uma cópia
paralela do histórico em arquivo local.

## Evento auditável

O AgentCore emite um JSON estruturado por interação:

```json
{
  "trace_id": "uuid",
  "question": "pergunta recebida",
  "decision": "responder | nao_sei | escalar",
  "sources": ["data/corpus/..."],
  "top_score": 0.91,
  "guardrail": "categoria de escalonamento ou null"
}
```

O mesmo `trace_id` é propagado pelo API Gateway, AgentCore, `retrieve_kb` e,
quando disponível, `store_handoff`.

## Consulta reproduzível

Com a sessão SSO ativa e a `.venv` ativada:

```bash
aws sso login --profile AlunoAdmin-699038657189

python -m src.parte_05_governanca.audit \
  --trace-id "teste-console-001" \
  --log-group /aws/lambda/concierge-conectatel-retrieve-kb
```

No ambiente implantado, consulte todos os grupos da mesma trilha:

```bash
python -m src.parte_05_governanca.audit \
  --trace-id "teste-final-001" \
  --log-group /aws/bedrock-agentcore/runtimes/concierge_conectatel_agent-Sk4fyE6R6C-DEFAULT \
  --log-group /concierge-conectatel/lambda/gateway \
  --log-group /aws/lambda/concierge-conectatel-retrieve-kb \
  --log-group /aws/lambda/concierge-conectatel-store-handoff
```

A consulta usa CloudWatch Logs Insights, ordena os eventos por tempo e encerra
em até 55 segundos. Salve a saída junto às evidências da entrega.

## Controles

- **Menor privilégio:** a identidade que executa a consulta precisa apenas de
  `logs:StartQuery` e `logs:GetQueryResults` nos log groups do Concierge.
- **Dados pessoais:** não registrar credenciais, tokens, CPF, cartão ou anexos.
  CPF, cartão, telefone e e-mail são mascarados antes da emissão do evento de
  auditoria. Apenas os dados necessários ao handoff são persistidos na tabela
  operacional, protegida por IAM de menor privilégio.
- **Retenção:** aplique 14 dias aos quatro log groups operacionais após cada
  criação/recriação de ambiente com `make retention`; revise a duração caso a
  política de dados mude.
- **Escalonamento:** o registro DynamoDB usa o mesmo `trace_id`; a consulta
  deve incluir o resultado de `store_handoff` quando houver handoff.

## Evidência esperada

Para a demonstração, cronometre uma consulta real por `trace_id` e registre:

- comando executado e horário UTC;
- tempo até o retorno;
- pergunta, decisão, fonte, guardrail e `trace_id`;
- para um handoff, o protocolo retornado e o item associado na DynamoDB.

## Evidência executada

Em 02/09/2026, a consulta do handoff `e2e-handoff-20260901` percorreu os
quatro grupos em **3,814 s** e retornou o evento estruturado do AgentCore com
pergunta, decisão `escalar`, guardrail e `trace_id`. O registro reproduzível
está em
[`artifacts/audit/rodada_auditoria_e2e_20260902.md`](../../artifacts/audit/rodada_auditoria_e2e_20260902.md).
