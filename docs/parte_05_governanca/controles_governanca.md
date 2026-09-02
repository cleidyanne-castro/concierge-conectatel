# Controles de governança, segurança e custo

Este documento consolida os controles operacionais do Concierge ConectaTel.
Ele complementa a [operação de auditoria](operacao_auditoria.md) e deve ser
revisado antes de cada deploy de demonstração.

## Matriz de menor privilégio

| Componente | Permissões necessárias | Limites deliberados |
|---|---|---|
| Pessoa operadora (SSO) | deploy SAM, leitura de logs, invocação de teste | Usar profile da conta da demo; não salvar access keys no repositório. |
| Lambda `retrieve_kb` | `s3:GetObject` somente no bucket da base; logs de execução | Não escreve no bucket e não possui permissões Bedrock ou DynamoDB. |
| Lambda `gateway` | `bedrock-agentcore:InvokeAgentRuntime` somente no ARN do Runtime | Não acessa S3, DynamoDB ou o modelo Bedrock diretamente. |
| AgentCore Runtime | `bedrock:InvokeModel` e `bedrock:InvokeModelWithResponseStream` somente para o modelo aprovado; `lambda:InvokeFunction` apenas para `retrieve_kb` e `store_handoff`; logs/traces | Não recebe permissões administrativas e não lista/invoca Lambdas arbitrárias. |
| Lambda `store_handoff` | `dynamodb:PutItem` na tabela `concierge-conectatel-escalonamentos`; logs | Não lê/escreve outras tabelas; a chave de idempotência é o `trace_id`. |
| Consulta de auditoria | `logs:StartQuery` e `logs:GetQueryResults` nos log groups do Concierge | A consulta é somente leitura e usa `trace_id` como chave de busca. |

Os ARNs, IDs de conta e nomes de repositório em `infra/agentcore/` são
específicos de ambiente. Antes de implantar em outra conta, substituí-los pelos
recursos da conta de demonstração; nunca reutilizar o ARN de outra squad.

## Guardrails aplicados

| Risco de resposta | Controle | Evidência |
|---|---|---|
| Documento revogado aparecer na resposta | Filtro estrutural `status = vigente` antes da similaridade | Testes de vigência e resultado da Lambda. |
| Pergunta fora do corpus gerar alucinação | Limiar calibrado `0.85`; decisão `nao_sei` abaixo do corte | `calibration_report.json` e transcrições sem fonte. |
| Modelo responder sem fonte | Prompt exige chamar `retrieve_kb` antes de resposta factual e citar `source_path` | Código do agente e transcrições grounded. |
| Caso sensível ser resolvido indevidamente | Tool `store_handoff` e critérios de escalonamento determinísticos | Testes de handoff quando a Parte 4 estiver integrada. |
| Falha técnica vazar detalhe ao assinante | Gateway devolve resposta segura e grava o erro no log | Teste de erro do gateway e CloudWatch. |
| Raciocínio interno ser mostrado | Remoção de blocos `<thinking>` antes da resposta final | `_clean_answer()` do agente. |

## Auditoria e dados

O `trace_id` nasce no gateway (ou é recebido da interface) e acompanha cada
chamada. O evento de auditoria registra pergunta, decisão, fontes, score e
guardrail. A consulta consolidada é feita com:

```bash
python -m src.parte_05_governanca.audit \
  --trace-id "<trace_id>" \
  --log-group /aws/lambda/concierge-conectatel-retrieve-kb
```

Na configuração implantada, a consulta inclui os log groups do gateway,
AgentCore, `retrieve_kb` e `store_handoff`. A meta demonstrável é recuperar a
trilha em menos de 60 segundos; uma execução real está registrada em
[`rodada_auditoria_e2e_20260902.md`](../../artifacts/audit/rodada_auditoria_e2e_20260902.md).

Não registrar em logs access keys, tokens, CPF, cartão, anexos ou conteúdo
sensível fora do necessário para o desafio. CPF, cartão, telefone e e-mail são
mascarados antes de a pergunta ser emitida no evento de auditoria. A telemetria
automática mantém métricas e traces, mas não captura prompts, respostas ou
argumentos de tools (`NO_CONTENT`), evitando duplicar dados pessoais nos spans.

## Observabilidade operacional

Além da auditoria individual por `trace_id`, filtros de logs e métricas nativas
mantêm indicadores agregados de saúde disponíveis no CloudWatch:

| Indicador | Fonte | Uso operacional |
|---|---|---|
| Invocações, erros e duração p95 | Métricas nativas das Lambdas gateway e `retrieve_kb`, mais filtro de erro tratado no gateway | Identificar indisponibilidade ou degradação de latência, inclusive quando a API devolve 502 sem encerrar a Lambda com erro. |
| Decisões `responder`, `nao_sei` e `escalar` | Três filtros de métrica no log do gateway | Verificar o comportamento seguro do agente em lote. |
| Handoffs persistidos | `SuccessfulRequestLatency` / `PutItem` da tabela DynamoDB | Confirmar que os escalonamentos chegaram à fila humana. |

Os alarmes de erro da gateway e da tool RAG avaliam janelas de cinco minutos,
tratam ausência de dados como saudável e não executam ação automática. O alarme
da gateway usa o evento estruturado de erro, pois uma resposta HTTP 502 tratada
não incrementa necessariamente a métrica nativa `AWS/Lambda Errors`. Isso
evita custo e ruído operacional durante a demonstração, mantendo uma sinalização
visível para investigação pelo `trace_id`.

## Riscos e respostas operacionais

| Risco | Sinal | Mitigação | Responsável |
|---|---|---|---|
| Cold start do modelo exceder o timeout | `Sandbox.Timedout` / 5xx | Pré-carregar o modelo na imagem, medir latência e dimensionar memória/timeout. | Infra |
| Sessão SSO expirar | `TokenRetrievalError` | Rodar `aws sso login --profile <perfil>` e confirmar com STS. | Operador |
| ARN do AgentCore pertencer a outra conta | Gateway retorna `erro_runtime` | Criar Runtime, ECR e role na conta da demo; atualizar parâmetros de deploy. | Infra/Agente |
| Custo inesperado | Uso de Lambda/AgentCore/Bedrock acima do previsto | Criar Budget com alerta, revisar memória e remover recursos após testes. | Infra |
| Falha do handoff | Log `store_handoff` com erro | Exibir escalonamento seguro, investigar pelo `trace_id` e repetir teste após DynamoDB estar disponível. | Triagem |
| Mudança de corpus sem reindexação | Score ou fonte inesperados | Executar chunking, embeddings, índice e upload antes do deploy. | Base de conhecimento |

## Custos e limpeza

Antes da demonstração, criar um AWS Budget de valor baixo com alerta por e-mail
para a pessoa responsável pela conta. O endereço de notificação é específico da
conta e, por isso, não deve ser fixado no repositório.

Após testes ou ao encerrar o projeto, remover recursos contínuos nesta ordem:

```bash
sam delete --stack-name <stack>
aws bedrock-agentcore-control delete-agent-runtime --agent-runtime-id <id> --region us-east-1
aws ecr delete-repository --repository-name <repo-do-agente> --force --region us-east-1
aws s3 rb s3://<bucket-da-base> --force
```

O bucket deve ser removido apenas depois de preservar as evidências que precisam
ser entregues. A retenção dos log groups é reaplicada de forma idempotente após
o deploy com:

```bash
make retention
```

O comando descobre o grupo do AgentCore e configura 14 dias nele e nos três
grupos Lambda, salvo exigência institucional diferente.

Na conta de demonstração, a retenção de **14 dias** está aplicada aos quatro
grupos operacionais: `retrieve_kb`, gateway, `store_handoff` e AgentCore. O
Budget de custo **Consumo AWS - Natan Alencar Maia**, com limite de **US$ 20**,
também estava ativo na verificação de 02/09/2026.

## Checklist pré-demo

- [ ] Conta, região, bucket e ARNs correspondem ao ambiente da demo.
- [ ] SSO válido e `aws sts get-caller-identity` confirmado.
- [x] Budget de US$ 20 ativo e plano de limpeza revisado.
- [x] Consulta por `trace_id` cronometrada em menos de 60 segundos.
- [x] Captura de conteúdo sensível desabilitada na telemetria; evento funcional mascara PII.
- [ ] Duas transcrições grounded, duas `nao_sei` e dois handoffs disponíveis.
- [ ] Rollback do CloudFormation habilitado no deploy final.
