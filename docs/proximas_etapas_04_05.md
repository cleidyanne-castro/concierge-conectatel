# Integração final - Partes 4 e 5

Este documento descreve o estado do código na `main`. A publicação na conta de
demonstração e as evidências ponta a ponta devem ser verificadas antes da
entrega; não confundir recurso declarado no template com recurso já publicado.

## Parte 4 - Triagem e escalonamento

O repositório já contém os recursos necessários para persistir um handoff:

| Componente | Implementação | Situação para a banca |
| --- | --- | --- |
| `store_handoff` | Lambda `concierge-conectatel-store-handoff` | requer deploy e teste real |
| Persistência | DynamoDB `concierge-conectatel-escalonamentos` | criada pelo SAM no deploy |
| Chave de auditoria | `trace_id` | usada como chave primária e na trilha de logs |
| Contrato de sucesso | `{"stored": true, "protocolo": "..."}` | validado por teste unitário |

A Lambda rejeita registros sem os campos mínimos definidos na Política de
Suporte e Escalonamento, valida a urgência e trata uma repetição do mesmo
`trace_id` de forma idempotente. Cada evento de persistência gera um log JSON
com `trace_id` e protocolo.

### Deploy e validação

1. Criar ou renovar a sessão SSO da conta de demonstração.
2. Criar/publicar o AgentCore Runtime dessa mesma conta e guardar seu ARN.
3. Executar `sam build` e `sam deploy`, passando explicitamente
   `AgentRuntimeArn` e `KnowledgeBaseBucketName`.
4. Enviar ao endpoint `/concierge` um caso de escalonamento obrigatório.
5. Conferir o item no DynamoDB e validar se um atendente humano entende
   problema, verificações já feitas e urgência sem consultar o histórico.

O escalonamento ainda depende da decisão do agente orientada pela política. Um
guardrail determinístico para os oito critérios permanece uma melhoria
recomendada para reduzir dependência do modelo.

## Parte 5 - Governança e auditoria

O agente propaga o `trace_id` para as tools e emite um evento estruturado com
pergunta, decisão, fontes, score e guardrail. A consulta em CloudWatch Logs
Insights é feita pelo módulo `src.parte_05_governanca.audit`.

Na rodada integrada, consulte todos os grupos de logs relevantes:

```bash
python -m src.parte_05_governanca.audit \
  --trace-id "teste-final-001" \
  --log-group /aws/bedrock-agentcore/runtimes/<runtime> \
  --log-group /aws/lambda/concierge-conectatel-gateway \
  --log-group /aws/lambda/concierge-conectatel-retrieve-kb \
  --log-group /aws/lambda/concierge-conectatel-store-handoff
```

A meta da banca é recuperar, em menos de 60 segundos, a pergunta, fonte,
decisão e guardrail. Para um escalonamento, apresentar também o protocolo e o
registro associado no DynamoDB.

## Evidências que ainda precisam ser produzidas

- dois handoffs distintos persistidos e avaliados em teste cego;
- duas perguntas sobre documento revogado, respondidas pela versão vigente;
- duas perguntas sem fonte, com decisão segura `nao_sei`;
- consulta integrada de auditoria cronometrada em menos de 60 segundos;
- transcrições textuais de 10 a 15 interações para o documento principal.
