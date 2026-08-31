# Evidência — retenção de logs CloudWatch

## Configuração aplicada

- Data: 31/08/2026.
- Conta: `699038657189`.
- Região: `us-east-1`.
- Log group: `/aws/lambda/concierge-conectatel-retrieve-kb`.
- Retenção configurada: **14 dias**.

## Comando aplicado

```bash
aws logs put-retention-policy \
  --log-group-name /aws/lambda/concierge-conectatel-retrieve-kb \
  --retention-in-days 14 \
  --region us-east-1 \
  --profile AlunoAdmin-699038657189
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

Os futuros log groups do gateway, AgentCore e `store_handoff` devem receber a
mesma retenção no respectivo deploy.
