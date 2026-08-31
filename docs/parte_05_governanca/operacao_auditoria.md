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

Quando o AgentCore e a Parte 4 estiverem implantados, consulte todos os grupos
da mesma trilha:

```bash
python -m src.parte_05_governanca.audit \
  --trace-id "teste-final-001" \
  --log-group /aws/bedrock-agentcore/runtimes/<runtime> \
  --log-group /aws/lambda/concierge-conectatel-gateway \
  --log-group /aws/lambda/concierge-conectatel-retrieve-kb \
  --log-group /aws/lambda/concierge-conectatel-store-handoff
```

A consulta usa CloudWatch Logs Insights, ordena os eventos por tempo e encerra
em até 55 segundos. Salve a saída junto às evidências da entrega.

## Controles

- **Menor privilégio:** a identidade que executa a consulta precisa apenas de
  `logs:StartQuery` e `logs:GetQueryResults` nos log groups do Concierge.
- **Dados pessoais:** não registrar credenciais, tokens, CPF, cartão ou anexos.
  A pergunta é registrada somente para rastreabilidade do desafio; em produção,
  deve passar por mascaramento de PII antes da emissão do evento.
- **Retenção:** configurar uma retenção explícita para os log groups no deploy;
  a duração deve ser aprovada pela política de dados da operação.
- **Escalonamento:** a Parte 4 adicionará o registro DynamoDB ao mesmo
  `trace_id`; a consulta deve incluir o resultado de `store_handoff`.

## Evidência esperada

Para a demonstração, cronometre uma consulta real por `trace_id` e registre:

- comando executado e horário UTC;
- tempo até o retorno;
- pergunta, decisão, fonte, guardrail e `trace_id`;
- para um handoff, o protocolo retornado e o item associado na DynamoDB.
