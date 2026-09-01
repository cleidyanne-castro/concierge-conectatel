# Arquitetura do Sistema - Concierge ConectaTel

## 1. Visão Geral
O **Concierge ConectaTel** é uma solução de triagem e atendimento baseada em Inteligência Artificial Generativa construída na AWS. O sistema combina agentes do **Amazon Bedrock** com arquitetura Serverless para responder dúvidas de clientes e, quando necessário, realizar o transbordo (escalonamento) para atendimento humano.

---

## 2. Diagrama de Fluxo de Atendimento

```text
[ Cliente ] 
    │
    ▼
[ Agente de Triagem (agent_concierge.py / Bedrock) ]
    │
    ├─── (Consulta de Informações) ───► [ Lambda Retrieve KB ] ───► Base de Conhecimento
    │
    └─── (Escalonamento de Caso)  ───► [ Lambda Store Handoff ] ───► [ Tabela DynamoDB ]
```
---
## 3. Componentes do Sistema

  Amazon Bedrock: Processa os prompts em linguagem natural, executa guardrails e orquestra a chamada de ferramentas (Tool Use).

  Agente de Triagem (agent_concierge.py): Ponto de entrada das mensagens. Avalia se a dúvida pode ser resolvida via Knowledge Base ou se atinge critérios de escalonamento.

  Lambda Store Handoff (store_handoff_lambda.py): Função acionada pela IA para gerar um protocolo de atendimento único e gravar os dados do caso no banco de dados.

  Tabela DynamoDB (concierge-conectatel-escalonamentos): Banco NoSQL responsável pela persistência dos tickets de escalonamento.


## 4. Decisões Arquiteturais (ADRs)

  Serverless First: Utilização de AWS Lambda e DynamoDB para garantir alta disponibilidade e pagamento por uso.

  Orquestração por IA: A decisão de invocar o escalonamento é tomada de forma autônoma pelo modelo generativo com base nas políticas de suporte configuradas no sistema.
