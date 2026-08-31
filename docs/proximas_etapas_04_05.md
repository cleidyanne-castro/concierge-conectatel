# Próximas etapas — Partes 4 e 5

Contexto: a Parte 3 (agente) está no ar. O agente roda no **Amazon Bedrock
AgentCore Runtime** (`concierge_agent-OGCvl4G9Yj`), é chamado pela Lambda
`concierge-conectatel-gateway` atrás do API Gateway, e usa duas tools:

| Tool | Lambda | Estado |
|---|---|---|
| `retrieve_kb` | `concierge-conectatel-retrieve-kb` | ✅ no ar (Parte 2) |
| `store_handoff` | `concierge-conectatel-store-handoff` | ❌ **não existe** — Parte 4 |

Enquanto `store_handoff` não existe, o agente ainda decide `escalar` e devolve o
`handoff` preenchido; só registra um ERROR no log porque a Lambda não responde.

---

## Parte 4 — Triagem e Escalonamento

### 4.1 Lambda `store_handoff` (obrigatório)

O agente já invoca `concierge-conectatel-store-handoff` com este payload
(exatamente `HandoffRecord.to_item()` de [`src/shared/types.py`](../src/shared/types.py)):

```json
{
  "protocolo_atendimento": "CONCTL-20260831-A07C90",
  "data_hora_abertura": "2026-08-31T13:24:42.791794+00:00",
  "canal_origem": "chat",
  "categoria_motivo": "Suspeita de fraude",
  "resumo_caso": "...",
  "historico_ja_levantado": "...",
  "produto_servico_envolvido": "...",
  "documento_fonte_consultado": "...",
  "urgencia": "alta",
  "dados_contato_retorno": "...",
  "trace_id": "..."
}
```

Nomes dos campos = tabela em
[`politica_suporte_escalonamento.md`](../data/corpus/politicas/politica_suporte_escalonamento.md).
O `protocolo_atendimento` **já vem gerado pelo agente** — a Lambda só persiste.

**Contrato de saída** (o agente espera):
```json
{"stored": true, "protocolo": "CONCTL-20260831-A07C90"}
```

**Implementação sugerida** (`src/parte_04_triagem/lambda_handler.py`):
- valida os 10 campos (nenhum vazio);
- `dynamodb.put_item` na tabela `HANDOFF_TABLE_NAME` (default `concierge-handoff`);
- idempotente por `protocolo_atendimento` (`ConditionExpression attribute_not_exists`);
- log estruturado JSON com `trace_id` (a Parte 5 consulta por ele).

### 4.2 Tabela DynamoDB

- PK: `protocolo_atendimento` (S)
- GSI `trace_id-index`: PK `trace_id` (S) — para a Parte 5 achar o handoff por trace.
- Billing `PAY_PER_REQUEST`.

### 4.3 Adicionar ao `infra/template.yaml`

```yaml
  HandoffTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: concierge-handoff
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - { AttributeName: protocolo_atendimento, AttributeType: S }
        - { AttributeName: trace_id, AttributeType: S }
      KeySchema:
        - { AttributeName: protocolo_atendimento, KeyType: HASH }
      GlobalSecondaryIndexes:
        - IndexName: trace_id-index
          KeySchema: [ { AttributeName: trace_id, KeyType: HASH } ]
          Projection: { ProjectionType: ALL }

  StoreHandoffFunction:
    Type: AWS::Serverless::Function
    Properties:
      FunctionName: concierge-conectatel-store-handoff
      Runtime: python3.12
      Handler: lambda_handler.handler
      CodeUri: ../src/parte_04_triagem/
      MemorySize: 256
      Timeout: 15
      Environment:
        Variables:
          HANDOFF_TABLE_NAME: !Ref HandoffTable
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref HandoffTable
```

Depois: `sam build && sam deploy`. Nada muda no agente — ele já chama pelo nome.

### 4.4 Guardrail determinístico dos 8 critérios (recomendado)

Hoje o escalonamento é 100% decisão do LLM (via `system_prompt` + a tool). Para
não depender só disso, criar `src/parte_04_triagem/policy.py` com
`evaluate(question, retrieve) -> Escalation | None` (os 8 critérios como
regex/keyword; o tipo `Escalation` já existe em `shared/types.py`) e chamá-lo
**dentro do agente**, em `agent_concierge.run()`, logo após o `agent()`:
se `evaluate` disparar e o LLM não escalou, força `decision = "escalar"`.
Isso exige rebuild + update do container do Runtime (ver `infra/agentcore/`).

---

## Parte 5 — Governança e Auditoria (Natan)

### 5.1 O que já existe

O agente emite um `AuditEvent` (JSON) por interação — ver `_emit_audit` em
[`agent_concierge.py`](../src/parte_03_04_agente_triagem/agent_concierge.py):
```json
{"trace_id": "...", "question": "...", "decision": "responder|nao_sei|escalar",
 "sources": ["..."], "top_score": 0.87, "guardrail": "Suspeita de fraude"}
```
Vai pro CloudWatch. AgentCore Observability está **ligado** (traces no console
"CloudWatch > GenAI Observability").

### 5.2 Log groups para consulta por `trace_id`

- AgentCore runtime: `/aws/bedrock-agentcore/runtimes/concierge_agent-OGCvl4G9Yj-*`
  (confirmar o nome exato no console AgentCore > Agent Runtime > Observability)
- `/aws/lambda/concierge-conectatel-gateway`
- `/aws/lambda/concierge-conectatel-retrieve-kb`
- `/aws/lambda/concierge-conectatel-store-handoff` (após a Parte 4)

### 5.3 `src/parte_05_governanca/audit.py`

Implementar `find_by_trace_id(trace_id: str) -> list[dict]`:
- `logs start-query` (CloudWatch Logs Insights) nos log groups acima com
  `filter @message like /<trace_id>/ | sort @timestamp asc`;
- `logs get-query-results` em loop até `Complete`;
- meta: retornar em **< 60 s** (requisito da rubrica).

### 5.4 Documento de entrega (seção de governança)

- Tabela IAM de menor privilégio (roles: execução do Runtime, gateway, tools).
- Guardrails: `system_prompt` + guardrail determinístico (4.4); opcional Bedrock
  Guardrails no `BedrockModel`.
- AWS Budgets: alerta de custo baixo (Bedrock + Lambda + AgentCore).
- Limpeza de recursos:
  ```
  sam delete --stack-name concierge-conectatel
  aws bedrock-agentcore-control delete-agent-runtime --agent-runtime-id concierge_agent-OGCvl4G9Yj --region us-east-1
  aws ecr delete-repository --repository-name bedrock-agentcore-concierge_agent --force --region us-east-1
  aws s3 rb s3://<bucket> --force
  ```

---

## Ordem sugerida

1. Parte 4: `store_handoff` + DynamoDB no template → `sam deploy` → testar `escalar` ponta a ponta.
2. Parte 5: `find_by_trace_id` + query salva no Logs Insights → cronometrar < 60 s.
3. Parte 4: guardrail `policy.py` no agente (se sobrar tempo) → rebuild do Runtime.
4. Transcrições finais (10–15) cobrindo `responder` / `nao_sei` / `escalar`.
