# Evidência — consulta de auditoria por `trace_id`

## Execução

- Data da evidência: 31/08/2026.
- `trace_id`: `smoke-test-local`.
- Log group: `/aws/lambda/concierge-conectatel-retrieve-kb`.
- Janela consultada: últimas 4 horas.
- Tempo medido com `time.perf_counter()`: **2,780 s**.
- Critério da entrega: consulta disponível em menos de 60 s — **atendido**.

## Comando reproduzível

```bash
python -m src.parte_05_governanca.audit \
  --trace-id "smoke-test-local" \
  --log-group /aws/lambda/concierge-conectatel-retrieve-kb \
  --lookback-minutes 240
```

## Evento retornado

```json
{
  "trace_id": "smoke-test-local",
  "question": "Como consulto meu consumo de dados?",
  "decision": "responder",
  "top_score": 0.9114037752151489,
  "log_group": "/aws/lambda/concierge-conectatel-retrieve-kb",
  "timestamp": "2026-08-31 17:28:22.094"
}
```

## Conclusão

O mesmo `trace_id` usado na invocação da Lambda permitiu recuperar a pergunta,
a decisão e o score diretamente do CloudWatch Logs Insights. A evidência cobre
a tool `retrieve_kb`; quando AgentCore e `store_handoff` estiverem implantados,
a consulta deverá incluir também seus log groups para fechar a trilha ponta a
ponta.
