# Plano de testes para banca

Este plano separa os testes que já podem ser executados dos testes que
dependem da integração final. Ele serve como roteiro da demonstração, do teste
cego e das transcrições da entrega; não substitui os testes automatizados.

## Pré-requisitos da rodada

- ambiente virtual instalado e dependências atualizadas;
- credenciais AWS válidas para o perfil da equipe;
- bucket da base de conhecimento com índice e metadados carregados;
- stack SAM e, na rodada integrada, AgentCore/API Gateway publicados;
- uma pessoa que não acompanhou o desenvolvimento para executar o teste
  independente.

## Casos de aceitação

| ID | Cenário | Resultado esperado | Situação atual | Responsável pela evidência |
| --- | --- | --- | --- | --- |
| T01 | Pergunta coberta por documento vigente | Resposta fundamentada e fonte identificável | Executável na `retrieve_kb` | Kaique / Natan |
| T02 | Pergunta sem cobertura no corpus | O sistema declara que não sabe; não inventa resposta | Executável na `retrieve_kb` | Kaique / Natan |
| T03 | Documento revogado que conflita com vigente | Documento revogado é descartado antes da similaridade | Validar na integração | Bruno / Kaique |
| T04 | Duas perguntas sem fonte | Duas transcrições distintas com decisão de não responder | Executável quando a resposta do agente estiver integrada | João |
| T05 | Caso que exige escalonamento | Handoff contém problema, verificações realizadas e urgência | Pendente da tool e DynamoDB | José |
| T06 | Auditoria por `trace_id` | Em até 60 s, recupera pergunta, fonte, decisão e guardrail | Parcial: Lambda já registra decisão; integração deve registrar fonte e guardrail | Natan / João |
| T07 | Teste cego | Pessoa externa usa o README e obtém um handoff utilizável | Pendente da integração de escalonamento | José / Natan |
| T08 | Execução reproduzível | `pytest` e validação SAM passam no commit congelado | Executável | Natan |

## Roteiro da demonstração ponta a ponta

1. Mostrar uma pergunta de T01 e a resposta com a fonte citada.
2. Mostrar uma pergunta de T02 e a recusa segura (“não sei”), sem completar
   com conhecimento externo.
3. Mostrar T03, deixando explícito que o item revogado não entrou na busca.
4. Mostrar T05 e o registro de handoff no DynamoDB.
5. Copiar o `trace_id` da mesma interação e executar T06 na consulta de
   auditoria.
6. Registrar cada execução em
   [`docs/transcricoes/`](../transcricoes/) usando o
   [template](../transcricoes/template_interacao.md).

## Procedimento de auditoria (T06)

Inicie a medição antes da consulta e pare-a quando o evento aparecer. A meta é
no máximo 60 segundos.

```bash
python -m src.parte_05_governanca.audit \
  --trace-id "<trace_id>" \
  --log-group /aws/lambda/concierge-conectatel-retrieve-kb \
  --lookback-minutes 60
```

Na integração final, inclua também o grupo de logs do gateway/runtime do
agente. A evidência deve conter, em texto, pergunta, fontes usadas, decisão e
guardrail aplicado. Se qualquer campo não aparecer, o caso falha e deve gerar
ação corretiva antes da entrega.

## Teste cego de handoff (T07)

1. Escolher uma pessoa que não participou da implementação.
2. Entregar apenas o README e o cenário de atendimento, sem explicar o fluxo.
3. Solicitar que ela execute o projeto e provoque um caso de escalonamento.
4. Entregar o handoff a outra pessoa que não acompanhou a conversa.
5. Registrar se ela consegue agir usando somente problema, contexto,
   verificações e urgência.
6. Salvar a transcrição, o `trace_id`, o identificador do registro e a ação
   corretiva, caso exista.

## Critério de congelamento

Antes da apresentação, executar T01--T08 aplicáveis, preencher as
transcrições obrigatórias (10 a 15 no total), revisar o checklist de entrega e
criar a tag `v1.0-entrega`. A demonstração e o vídeo plano B devem usar esse
mesmo commit.
