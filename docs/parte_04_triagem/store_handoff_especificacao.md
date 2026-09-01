# Especificação da Lambda e Escalonamento (Store Handoff)

## 1. Objetivo
O componente *Store Handoff* é responsável por registrar solicitações que exigem intervenção de um atendente humano, gerando um protocolo rastreável e salvando o contexto completo da conversa no DynamoDB.

---

## 2. Regras de Disparo do Escalonamento
A IA deve acionar a ferramenta de escalonamento quando identificar:
* **Contestação de Fatura:** Faturas com valor igual ou superior a R$ 500.
* **Suporte Técnico Avançado:** Problemas de conectividade recorrentes ou falhas físicas na infraestrutura.
* **Demandas Jurídicas ou Órgãos de Defesa:** Menções a PROCON, Anatel ou processos judiciais.
* **Solicitação Direta:** Pedido explícito do cliente para falar com um atendente humano (com dados de contato fornecidos).

---

## 3. Schema da Tabela DynamoDB

* **Nome da Tabela:** `concierge-conectatel-escalonamentos`
* **Chave Primária (Partition Key):** `trace_id` (String)

### Campos do Registro (Contrato JSON)

| Campo | Tipo | Descrição | Exemplo |
| :--- | :--- | :--- | :--- |
| `trace_id` | String | Identificador único da sessão/chamada (PK) | `146ce41d-5569-48a7-91f7-d8ed9af92f13` |
| `protocolo_atendimento` | String | Código gerado no formato `CONCTL-YYYYMMDD-XXXXXX` | `CONCTL-20260901-901272` |
| `data_hora_abertura` | String | Data/hora em formato ISO 8601 | `2026-09-01T20:07:35.178962+00:00` |
| `categoria_motivo` | String | Categoria do problema | `contestacao_fatura` |
| `urgencia` | String | Nível de urgência (`baixa`, `media`, `alta`) | `alta` |
| `resumo_caso` | String | Resumo sintetizado pelo Bedrock | `Cliente contesta fatura de R$ 750` |
| `dados_contato_retorno` | String | Telefone ou e-mail de contato do cliente | `83 99999-8888` |
| `canal_origem` | String | Canal de atendimento | `chat` |
| `produto_servico_envolvido`| String | Serviço associado à reclamação | `Fatura` |
| `historico_ja_levantado` | String | Informações prévias coletadas | `Não informado` |
| `documento_fonte_consultado`| String | Documentos de referência consultados na KB