# Engenharia de Dados do Concierge ConectaTel

## Objetivo

Esta documentação registra a construção da Parte 1 do projeto: ingestão,
tratamento, análise e disponibilização dos dados para as etapas seguintes do
Concierge ConectaTel.

O GitHub é a fonte oficial das decisões, contratos, código e evidências. Os
notebooks executam o processamento. Os arquivos Markdown explicam o contexto,
as regras e como reproduzir os resultados.

## Escopo adotado

O desafio solicita uma pipeline com Python, Pandas e arquivos CSV, JSON e
Markdown. Por isso, a implementação mantém esse padrão e não introduz
PySpark, Delta Lake ou processamento incremental como requisito artificial.

O desenho segue três camadas lógicas:

```text
Bronze → Silver → Gold
```

As camadas são separadas por responsabilidade, mas permanecem compatíveis com
o ambiente Databricks e com execução em Workflow Job.

## Bronze: preservação e descoberta

A Bronze preserva o insumo bruto e cria os primeiros artefatos de
rastreabilidade:

- snapshot do CSV original.
- validação das 13 colunas esperadas.
- relatório de qualidade antes da limpeza.
- relatório de schema.
- inventário de arquivos com SHA256.
- metadados de vigência do corpus documental.
- três análises descritivas iniciais.
- síntese das dúvidas mais frequentes.
- decisão de design relacionada aos achados.

A Bronze não remove duplicatas. Essa decisão preserva a fidelidade do insumo e
permite que a Silver registre o efeito da limpeza.

## Silver: qualidade e contrato comum

A Silver prepara os dados para consumo analítico e operacional:

- lê o snapshot da Bronze.
- valida o contrato de colunas.
- normaliza textos, espaços e acentos.
- converte datas, números e booleanos.
- trata valores ausentes com regras explícitas.
- invalida durações negativas.
- mantém satisfação no intervalo de 1 a 5.
- remove duplicatas exatas mantendo a primeira ocorrência.
- gera schema e relatório de qualidade.
- registra métricas de processamento.
- mantém uma cópia dos metadados do corpus.

O contrato e as regras estão documentados em:

- `docs/parte_01_dados/data_contract.md`.
- `docs/parte_01_dados/regras_negocio.md`.

A lógica reutilizável está em `src/parte_01_dados/silver.py` e é consumida pelo
notebook `02_silver_limpeza`.

## Gold: consumo analítico e decisões

A Gold transforma a Silver em produtos analíticos para a banca e para as
decisões do Concierge:

- KPIs gerais com volume e denominador.
- resumo por categoria e subcategoria.
- resumo de desempenho por canal.
- resumo por estado e cidade.
- síntese de decisões de design rastreáveis aos achados.
- artefatos prontos para um dashboard.

O notebook `03_gold_analise` centraliza a execução e o módulo `gold.py` mantém
as agregações reutilizáveis e testáveis.

## Planejado x concretizado

| Frente | Planejado | Concretizado | Estado |
|---|---|---|---|
| Bronze | preservar insumos, diagnosticar qualidade e mapear vigência | snapshots, análises, inventário, schema, qualidade e metadados do corpus | Concluído |
| Silver | preparar um dataset confiável | normalização sem acentos, conversões, ausências, duplicatas, métricas e testes | Concluído |
| Gold | transformar a Silver em evidência para decisões | três agregações, KPIs com denominadores, decisões, qualidade e manifesto | Executado com sucesso |
| Automação | encadear Bronze → Silver → Gold | Workflow Job publicado, com três tarefas dependentes e Serverless | Executado com sucesso |
| Dashboard | comunicar os indicadores | especificação de fontes, visuais, filtros e critérios de leitura | Especificado. Falta criação no workspace |
| Integração | entregar insumos claros às próximas partes | handoff de vigência, campos de chunk e rastreabilidade | Documentado |

Esse comparativo separa código versionado de execução operacional, deixando
claro para a banca o que já foi implementado e o que ainda depende do ambiente.

## Decisões técnicas

### Pandas e arquivos abertos

Mantivemos Pandas e CSV/JSON porque são tecnologias compatíveis com o escopo
oficial e facilitam a inspeção pela banca e pelas equipes sem acesso ao
Databricks.

### Separação entre notebook e módulo

O notebook representa a execução. Os módulos Python concentram regras
reutilizáveis. Isso reduz duplicação, facilita testes e permite que outras
etapas consumam as mesmas funções.

### Tratamento de duplicatas

A Bronze preserva duplicatas para auditoria. A Silver remove somente
duplicatas exatas, mantendo a primeira ocorrência e registrando o volume
removido.

### Metadados de vigência

O corpus mantém família documental, versão, período de vigência, status e hash
quando disponíveis. A Parte 2 deve usar somente documentos vigentes para
responder às perguntas.

### Métricas com denominador

Taxas e médias da Gold são publicadas com volume ou denominador. Assim, uma
taxa não é apresentada isoladamente e pode ser interpretada e auditada.

## Qualidade e testes

Os controles implementados incluem:

- falha quando faltam colunas obrigatórias.
- falha quando a saída fica vazia.
- contagem de nulos e valores inválidos.
- controle de duplicatas removidas.
- validação de tipos e intervalos.
- testes unitários das transformações da Silver.
- testes unitários das agregações da Gold.
- execução automatizada pelo workflow do GitHub.

Execução local registrada durante a evolução da Silver:

```text
Silver: 5 passed
Gold: 8 passed
```

## Execução no Databricks

A Silver foi executada no Databricks com:

- branch: `feat/silver-dados`.
- compute: Serverless.
- células concluídas: `5/5`.
- linhas lidas: `324`.
- linhas gravadas: `320`.
- duplicatas removidas: `4`.
- metadados copiados com sucesso.
- status: `WARNING` esperado pela presença de duplicatas no insumo.

A evidência está em:

`artifacts/audit/silver_execution_evidence.md`

## Workflow Job

O Workflow Job proposto executa as tarefas na seguinte ordem:

```text
Bronze → Silver → Gold
```

Cada tarefa depende da conclusão bem-sucedida da anterior. A configuração
mantém os notebooks independentes e torna a execução ponta a ponta reproduzível.

O arquivo de referência está em:

`infra/databricks_workflow_gold.json`

A execução realizada está registrada em:

`artifacts/audit/gold_execution_evidence.md`

Antes da demonstração, devem ser preenchidos os parâmetros do workspace e do
compute e realizada uma execução completa para gerar a evidência do fluxo.

## Dashboard

A Gold entrega `gold_kpis.csv`, três resumos analíticos,
`gold_quality_report.json`, `gold_manifest.json` e `gold_decisoes_design.md`.
O dashboard deve apresentar volume, satisfação, resolução no primeiro contato,
encaminhamento humano, desempenho por canal e concentração geográfica.

Cada visualização deve indicar sua fonte e exibir o volume ou denominador
correspondente. A especificação está em:

`docs/parte_01_dados/gold_dashboard.md`

## Integração com as partes seguintes

A Engenharia de Dados entrega:

- log de chamados limpo para análises e priorização.
- corpus preservado e inventariado.
- metadados de vigência e versão.
- caminhos estáveis no Volume.
- contratos de dados.
- regras de qualidade.
- decisões de design baseadas nos chamados.
- evidências reproduzíveis.

O handoff detalhado para Chunking e Embeddings está separado em:

`docs/parte_02_rag/data_handoff.md`

A Engenharia de Dados não cria embeddings, respostas, prompts ou regras de
roteamento. Ela fornece os dados e o contexto necessários para que essas
responsabilidades sejam executadas pelas partes seguintes.

## Limitações conhecidas

- Os dados processados permanecem no Volume e não são versionados no GitHub.
- O dashboard precisa ser criado e validado após a execução da Gold.
- O status `WARNING` da Silver é esperado quando duplicatas são encontradas.
- A execução local não substitui a evidência do Databricks.

## Próximos passos

1. Executar a Gold no Databricks.
2. Validar os arquivos analíticos e o manifesto gerado.
3. Publicar o Workflow Job com as dependências Bronze → Silver → Gold.
4. Criar o dashboard a partir dos arquivos da Gold.
5. Registrar evidências do fluxo completo.
6. Atualizar o relatório e a apresentação com os achados e decisões.

## Critério de entrega

Uma entrega completa combina atendimento ao escopo obrigatório com evidências
de execução, documentação clara, testes, automação e integração explícita com
as equipes de Chunking, Embeddings, Agente, Triagem e Governança.
