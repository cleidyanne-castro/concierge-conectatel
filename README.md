# Concierge ConectaTel — Squad 4

> README temporário para o Hackathon final. Atualizar após a integração e executar do zero com um membro que não tenha escrito a configuração original.

Assistente GenAI de atendimento para a operadora fictícia ConectaTel, com RAG sobre corpus oficial, filtro determinístico de vigência, triagem, escalonamento com handoff e trilha de auditoria.

## Escopo do desafio

- Parte 1: tratar o log CSV com Pandas, produzir 3 análises e usar um achado em uma decisão de design.
- Parte 2: chunking, embeddings, índice vetorial e filtro `status=vigente` antes do score.
- Parte 3: responder apenas pelo corpus, citar fonte e retornar “não sei” quando não houver fonte suficiente.
- Parte 4: escalar conforme a política e gerar handoff completo.
- Parte 5: registrar pergunta, fonte, decisão, guardrail e `trace_id`, localizável em até 60 segundos.

## Estrutura planejada

```text
.
├── README.md
├── architecture_concierge_conectatel.jpg
├── data/                 # insumos fornecidos pelo desafio (não versionar segredos)
├── src/
│   ├── data_pipeline.py
│   ├── rag_index.py
│   ├── concierge.py
│   ├── escalation.py
│   └── audit.py
├── tests/
├── docs/
│   ├── relatorio/
│   ├── transcricoes/
│   └── arquitetura/
└── infra/                # IAM, Lambda, S3 e configuração AWS
```

## Pré-requisitos

1. Python 3.11+ e ambiente virtual.
2. AWS CLI configurado na região usada pela squad anteriormente.
3. Permissões mínimas para S3 e `bedrock:InvokeModel` na conta de consolidação.
4. Acesso ao Amazon Bedrock; cada integrante deve registrar uma chamada Anthropic bem-sucedida conforme o desafio.
5. AWS Budget de baixo valor ativo em cada conta individual.

## Configuração do zero

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Preencher apenas variáveis não secretas no `.env`; usar credenciais AWS padrão, role Lambda ou profile local. Nunca commitar chaves.

## Ordem de execução

```bash
python -m src.data_pipeline --input data/call_log.csv --output artifacts/data
python -m src.rag_index --corpus data/corpus --output artifacts/index.json
python -m src.cli --question "<pergunta de teste>"
python -m pytest -q
```

Após a configuração, a sequência é: dados → índice → `VECTOR_STORE_PATH=artifacts/index.json` → handler do agente → triagem/escalonamento → auditoria → testes. O handler pode ser invocado localmente ou adaptado para AWS Lambda.

## Critérios de teste

O conjunto final deve conter 10–15 transcrições: pelo menos 2 respostas com fonte vigente, 2 perguntas sobre versão revogada, 2 perguntas sem fonte e 2 escalonamentos distintos com handoff completo. Também testar perguntas não preparadas e medir a recuperação do `trace_id` em até 60 segundos.

## Arquitetura

Ver [`docs/arquitetura/architecture.mmd`](docs/arquitetura/architecture.mmd) e [`docs/arquitetura/architecture_concierge_conectatel.jpg`](docs/arquitetura/architecture_concierge_conectatel.jpg). A decisão crítica é filtrar metadados `status=vigente` antes da similaridade; prompt sozinho não atende ao requisito.

## Entrega e congelamento

Antes de 02/09 às 23h59: revisar documento, README, slides, código, vídeo plano B e transcrições; criar a tag `v1.0-entrega`; demonstrar na banca exatamente essa versão.

## Limites e segurança

O corpus é a única fonte de resposta. Não usar dados reais nem informações externas sobre operadoras. Registrar riscos, guardrails, permissões IAM de menor privilégio e desligar recursos gerenciados de custo contínuo ao fim das sessões.
