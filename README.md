# Concierge ConectaTel

Assistente GenAI de atendimento para a operadora fictícia ConectaTel, com pipeline de dados, RAG sobre o corpus oficial, filtro determinístico de vigência, triagem, escalonamento com handoff e trilha de auditoria.

Este README é um guia técnico de execução para avaliadores e pessoas externas à squad.

## Mapa rápido

- [`src/`](src/): código executável, organizado pelas cinco partes da solução.
- [`tests/`](tests/): testes espelhados por domínio funcional.
- [`docs/`](docs/): contratos, decisões, arquitetura, QA e materiais de entrega.
- [`data/`](data/): entradas oficiais, corpus e exemplos pequenos.
- [`artifacts/`](artifacts/): evidências versionadas de execução e resultados selecionados.
- [`infra/`](infra/): configurações reproduzíveis de infraestrutura, sem segredos.

O conteúdo original dos notebooks, módulos, testes e imagens permanece nas
pastas correspondentes. Este mapa é a camada de navegação do repositório.

## 1. Arquitetura da solução

![Arquitetura final do Concierge ConectaTel](docs/arquitetura/arquitetura_conectatel_final.jpg)

Arquivos oficiais: [arquitetura original](docs/arquitetura/arquitetura_conectatel_planejada.jpg) e [arquitetura final](docs/arquitetura/arquitetura_conectatel_final.jpg). A comparação está em [planejado versus executado](docs/arquitetura/planejado_vs_executado.md).

Fluxo: log CSV → Pandas → achados de design. Corpus → S3 → chunking/metadados → embeddings/índice. Pergunta → Lambda → filtro `status=vigente` → busca → limiar → resposta grounded, “não sei” ou escalonamento → audit trail.

## 2. Pré-requisitos

- Python 3.11 ou superior.
- AWS CLI configurado na conta de consolidação.
- Região AWS usada pela squad nas sprints anteriores.
- Permissões mínimas para S3 e Amazon Bedrock. Para Lambda, role equivalente.
- Acesso ao modelo aprovado no Bedrock e AWS Budget de baixo valor ativo.
- Log CSV e corpus documental oficiais fornecidos no pacote do desafio.

O projeto não usa API key externa. Use credenciais AWS padrão, profile ou role. Nunca grave chaves no repositório.

## 3. Instalação

```bash
git clone https://github.com/cleidyanne-castro/concierge-conectatel.git
cd concierge-conectatel
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edite `.env` com região, bucket, caminho do índice, limiar de recuperação e modelo Bedrock.

## 4. Entrada de dados

Para execução local, use o exemplo em `data/examples/call_log.csv` e os
documentos em `data/corpus/`. No Databricks, disponibilize os mesmos insumos no
Volume configurado pela squad. Para versões diferentes da mesma política, use
nomes como `politica_fatura__vigente.txt` e `politica_fatura__revogado.txt`.

Os metadados devem conter `doc_family_id`, `version_ordinal`, `effective_from`, `effective_to` e `status`. O corpus oficial do desafio é a única fonte autorizada para as respostas.

## 5. Execução

### Parte 1: Pipeline de dados

Execute os notebooks [`01_bronze_ingestao.ipynb`](src/parte_01_dados/01_bronze_ingestao.ipynb),
[`02_silver_limpeza.ipynb`](src/parte_01_dados/02_silver_limpeza.ipynb) e
[`03_gold_analise.ipynb`](src/parte_01_dados/03_gold_analise.ipynb) no ambiente
Databricks configurado pela squad. A documentação, os contratos, as regras de
negócio, o dashboard e as evidências estão em
[`docs/parte_01_dados/`](docs/parte_01_dados/) e
[`artifacts/audit/`](artifacts/audit/).

O storytelling analítico está em
[`gold_dashboard.md`](docs/parte_01_dados/gold_dashboard.md), e os registros
visuais do dashboard estão em
[`gold_dashboard_evidence.png`](artifacts/audit/gold_dashboard_evidence.png)
e [`gold_dashboard_operacao_evidence.png`](artifacts/audit/gold_dashboard_operacao_evidence.png).

O Workflow Job versionado em
[`infra/databricks_workflow_gold.json`](infra/databricks_workflow_gold.json)
encadeia Bronze, Silver e Gold. A evidência visual da execução está em
[`gold_workflow_execution_evidence.png`](artifacts/audit/gold_workflow_execution_evidence.png).

### Parte 2: Base de conhecimento e RAG

Use os arquivos locais entregues no handoff em
[`docs/parte_02_rag/data_handoff.md`](docs/parte_02_rag/data_handoff.md). O
chunking, os embeddings e o índice vetorial estão organizados em
[`src/parte_02_rag/`](src/parte_02_rag/). O filtro `status=vigente` deve ocorrer
antes da similaridade. Prompt sozinho não atende ao requisito de vigência.

### Partes 3, 4 e 5: Agente, escalonamento e governança

```bash
python -m src.cli --question "<pergunta do assinante>"
```

O resultado contém `trace_id` e uma decisão: `responder`, `nao_sei` ou
`escalar`. O agente e a triagem estão em
[`src/parte_03_04_agente_triagem/`](src/parte_03_04_agente_triagem/) e a auditoria em
[`src/parte_05_governanca/`](src/parte_05_governanca/). O modo local permite
validar o fluxo sem credenciais.

## 6. Testes e evidências

```bash
python -m pytest -q
```

As evidências finais devem conter 10 a 15 transcrições textuais, incluindo duas
respostas com fonte vigente, duas perguntas sobre versão revogada, duas sem
fonte com “não sei” e dois escalonamentos distintos com handoff completo.
Também devem cobrir perguntas não preparadas, consulta do `trace_id` em até 60
segundos e execução do README por membro diferente do autor da configuração.

As evidências da Parte 1 estão em [`artifacts/audit/`](artifacts/audit/), com
registros visuais da Bronze, do Workflow, da Silver e do dashboard, além dos
respectivos registros de execução.

## 7. Auditoria e governança

Cada resposta registra pergunta, fontes, decisão, guardrail e `trace_id`. A
função `find_by_trace_id()` localiza uma interação. A documentação de
governança cobre IAM de menor privilégio, guardrails, riscos, AWS Budgets e
limpeza de recursos contínuos.

## 8. Estrutura do repositório

- `src/`: pipeline, RAG, agente, política e auditoria.
- `tests/`: testes automatizados.
- `data/`: entradas oficiais, corpus e exemplos de smoke test.
- `docs/arquitetura/`: arquitetura final aprovada pela squad.
- `docs/transcricoes/`: registros dos testes.
- `docs/qa/`: checklist e critérios de qualidade.
- `infra/`: configuração e documentação AWS.
- `artifacts/`: evidências selecionadas e registros de execução. Dados gerados
  em volume não são versionados no GitHub.

## 9. Troubleshooting

- `AccessDenied` no Bedrock: valide região, role/profile e acesso ao modelo.
- Índice ausente: execute a Parte 2 e confira `VECTOR_STORE_PATH`.
- Tudo retorna “não sei”: confirme índice, limiar e documentos `vigente`.
- Documento revogado aparece: corrija o filtro antes do score e repita os testes.
- `trace_id` ausente: confira os logs do CloudWatch, `AUDIT_LOG_GROUP` e a execução do handler.

## 10. Entrega final

O repositório reúne código, documentação, testes, evidências e contratos das
cinco partes. Antes da apresentação, a squad deve revisar as transcrições, os
slides, o código e o vídeo plano B. Se for necessário congelar uma versão,
crie a tag `v1.0-entrega` a partir da `main` validada.
