# Evidência — retenção de logs CloudWatch

## Configuração aplicada

- Data: 02/09/2026.
- Conta: `699038657189`.
- Região: `us-east-1`.
- Retenção configurada: **14 dias**.

| Log group | Retenção |
|---|---:|
| `/aws/lambda/concierge-conectatel-retrieve-kb` | 14 dias |
| `/aws/lambda/concierge-conectatel-gateway` | 14 dias |
| `/aws/lambda/concierge-conectatel-store-handoff` | 14 dias |
| `/aws/bedrock-agentcore/runtimes/concierge_conectatel_agent-Sk4fyE6R6C-DEFAULT` | 14 dias |

## Comando aplicado

```bash
for group in \
  /aws/lambda/concierge-conectatel-retrieve-kb \
  /aws/lambda/concierge-conectatel-gateway \
  /aws/lambda/concierge-conectatel-store-handoff \
  /aws/bedrock-agentcore/runtimes/concierge_conectatel_agent-Sk4fyE6R6C-DEFAULT
do
  aws logs put-retention-policy \
    --log-group-name "$group" \
    --retention-in-days 14 \
    --region us-east-1 \
    --profile AlunoAdmin-699038657189
done
```

## Verificação

```json
[
  {
    "name": "/aws/lambda/concierge-conectatel-retrieve-kb",
    "retention": 14
  }
]
```

Os quatro grupos operacionais estão configurados com a mesma retenção, evitando
que o histórico de auditoria permaneça indefinidamente na conta de demonstração.
