# Parte 1: Engenharia e análise de dados

Esta pasta reúne a implementação e a documentação da camada de dados do Concierge ConectaTel. Ela funciona como o ponto de entrada para entender o fluxo, reproduzir as etapas e localizar os contratos, testes e evidências da entrega.

## Visão geral

```text
Dados brutos
    ↓
Bronze — ingestão, inventário e diagnóstico
    ↓
Silver — limpeza, tipagem e regras de qualidade
    ↓
Gold — análises, indicadores e recomendações
    ↓
RAG, agente, triagem e governança
```

O desenho usa Python e Pandas, com CSV, JSON e Markdown como formatos de trabalho. A arquitetura Medallion organiza as responsabilidades sem introduzir tecnologias fora do escopo do hackathon.

## Mapa das camadas

| Camada | Entrada principal | Entrega | Responsabilidade | Notebook |
|---|---|---|---|---|
| Bronze | CSV de chamados e corpus documental | snapshots, inventários, qualidade e metadados | preservar a origem e tornar os insumos rastreáveis | [`01_bronze_ingestao.ipynb`](../../src/parte_01_dados/01_bronze_ingestao.ipynb) |
| Silver | saída tratada da Bronze | dataset limpo e validado | aplicar tipagem, normalização e regras de negócio | [`02_silver_limpeza.ipynb`](../../src/parte_01_dados/02_silver_limpeza.ipynb) |
| Gold | Silver | análises e síntese executiva | transformar dados tratados em evidências úteis para o produto | [`03_gold_analise.ipynb`](../../src/parte_01_dados/03_gold_analise.ipynb) |

## Conteúdo desta entrega

### Documentação

- [`engenharia_dados.md`](engenharia_dados.md) — visão técnica completa, decisões, execução, qualidade, workflow e integração entre as partes.
- [`data_contract.md`](data_contract.md) — contrato de dados, campos, tipos e expectativas de entrada e saída.
- [`regras_negocio.md`](regras_negocio.md) — regras de limpeza, validação e interpretação dos indicadores.
- [`../parte_02_rag/data_handoff.md`](../parte_02_rag/data_handoff.md) — contrato de entrega para Chunking e Embeddings.

### Implementação

- [`01_bronze_ingestao.ipynb`](../../src/parte_01_dados/01_bronze_ingestao.ipynb) — preservação da origem, diagnóstico e inventário.
- [`02_silver_limpeza.ipynb`](../../src/parte_01_dados/02_silver_limpeza.ipynb) — transformação do dataset para consumo analítico.
- [`03_gold_analise.ipynb`](../../src/parte_01_dados/03_gold_analise.ipynb) — indicadores, análises e recomendações.
- [`silver.py`](../../src/parte_01_dados/silver.py) — lógica reutilizável da Silver.
- [`gold.py`](../../src/parte_01_dados/gold.py) — lógica reutilizável da Gold.

### Papel dos módulos Python

- `silver.py` concentra as regras reutilizáveis de limpeza e validação da Silver.
- `gold.py` concentra as agregações, KPIs, síntese e saídas analíticas da Gold.
- `quality.py` concentra os status de qualidade e os manifestos de execução.
- Não há `bronze.py` porque a Bronze é executada pelo notebook de ingestão, que coordena leitura, snapshot, inventário e persistência dos artefatos.
- Os arquivos `__init__.py` podem permanecer vazios. Eles identificam a pasta como um pacote Python e não precisam conter lógica.

### Qualidade e operação

- [`test_silver.py`](../../tests/parte_01_dados/test_silver.py) — testes automatizados da Silver.
- [`test_gold.py`](../../tests/parte_01_dados/test_gold.py) — testes automatizados da Gold.
- [`silver_execution_evidence.md`](../../artifacts/audit/silver_execution_evidence.md) — evidência da execução real da Silver no Databricks.
- [`silver_read_validation.png`](../../artifacts/audit/silver_read_validation.png), [`silver_cleaning_result.png`](../../artifacts/audit/silver_cleaning_result.png) e [`silver_persistence_metadata.png`](../../artifacts/audit/silver_persistence_metadata.png) — evidências visuais da execução da Silver.
- [`gold_execution_evidence.md`](../../artifacts/audit/gold_execution_evidence.md) — evidência da execução ponta a ponta e dos resultados da Gold.
- [`bronze_execution_evidence.md`](../../artifacts/audit/bronze_execution_evidence.md) — evidência da leitura, validação e persistência da Bronze.
- [`gold_workflow_execution_evidence.png`](../../artifacts/audit/gold_workflow_execution_evidence.png) — evidência visual das dependências entre as camadas.
- [`databricks_workflow_gold.json`](../../infra/databricks_workflow_gold.json) — definição do Workflow Job com dependências entre as camadas.

## Como reproduzir

1. Disponibilize o CSV de chamados e o corpus no Volume definido pelo projeto.
2. Execute a Bronze para gerar os snapshots, relatórios de qualidade, inventário e metadados de vigência.
3. Execute a Silver usando as saídas da Bronze.
4. Execute a Gold usando o dataset tratado da Silver.
5. Rode os testes automatizados:

   ```bash
   pytest tests/parte_01_dados -q
   ```

6. Registre no GitHub os resultados relevantes, limitações e evidências de execução.

O fluxo operacional sugerido está descrito em [`engenharia_dados.md`](engenharia_dados.md), e a automação planejada está representada em [`databricks_workflow_gold.json`](../../infra/databricks_workflow_gold.json).

## Contratos de saída

### Bronze

Preserva o dado de origem e produz artefatos de inspeção, incluindo snapshot bruto, dados limpos, análises iniciais, síntese, inventário de arquivos, schema, relatório de qualidade e metadados de vigência do corpus.

### Silver

Entrega chamados com colunas conhecidas, tipos coerentes, textos normalizados, valores ausentes tratados, duplicatas removidas conforme a regra definida e qualidade mensurada.

### Gold

Entrega três análises agregadas, KPIs com denominadores, síntese orientada à decisão, relatório de qualidade e manifesto de execução. Esses artefatos conectam os achados dos chamados a decisões do Concierge.

## Integração com as próximas partes

Os chamados tratados apoiam a análise do atendimento, mas não substituem o corpus oficial como fonte de resposta do assistente.

Para Chunking e Embeddings, a entrega principal é o corpus com metadados de vigência. O consumo deve priorizar documentos com `status = vigente`, preservar `doc_family_id`, versão, datas, categoria, subcategoria e fonte, e manter a rastreabilidade até o arquivo original. Os detalhes do formato e das responsabilidades estão no [`data_handoff.md`](../parte_02_rag/data_handoff.md).

As equipes seguintes consomem contratos e artefatos versionados no GitHub. Elas não precisam acessar o Databricks para entender a estrutura ou reproduzir a lógica localmente, desde que recebam os arquivos de dados previstos pelo projeto.

## Critério de pronto

- [x] Insumos identificados e preservados na Bronze.
- [x] Schema e qualidade registrados antes e depois da limpeza.
- [x] Silver reproduzível e coberta por testes.
- [x] Gold com indicadores, denominadores e interpretação.
- [x] Decisões de produto rastreadas a achados específicos.
- [x] Metadados de vigência disponíveis para RAG.
- [x] Handoff documentado para Chunking e Embeddings.
- [x] Workflow com dependência Bronze → Silver → Gold descrito.
- [x] Workflow publicado e executado no workspace.
- [x] Dashboard criado e validado no workspace.
- [x] Evidências de execução e limitações registradas.

## Limites da solução

Esta parte não cria embeddings, chunks, respostas do agente, roteamento de ferramentas ou infraestrutura de produção. Também não migra o projeto para PySpark, Delta Lake ou streaming sem uma exigência explícita do desafio.

O objetivo é entregar dados confiáveis, análises explicáveis e contratos claros para que as próximas equipes construam sobre uma base estável.

## Diferenciais da entrega

O fator de maturidade está na combinação entre implementação e rastreabilidade: separação explícita das camadas, regras documentadas, testes automatizados, evidências reais, metadados de vigência, decisões de design baseadas em dados e integração formal com as etapas de RAG e agente.
