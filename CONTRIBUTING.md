# Contribuições

## Contribuições realizadas

### Cleidyanne Castro Pereira

Responsável pela Parte 0 e pela coordenação técnica inicial. O registro
consolidado das contribuições está em
 [`docs/registros_cleidyanne.md`](docs/registros_cleidyanne.md).

Na Parte 1, a contribuição concluída inclui:

- ingestão e validação do log de chamados com Pandas;
- organização da arquitetura Medallion em Bronze, Silver e Gold;
- tratamento de tipos, textos, estados, valores ausentes e duplicatas;
- controles de qualidade e testes automatizados;
- três análises descritivas, síntese dos achados e decisões de design;
- metadados de vigência para consumo pelo RAG;
- dashboard executivo com métricas e pain points do atendimento;
- Workflow Job no Databricks com dependências entre as três camadas;
- documentação técnica, contrato de dados, regras de negócio e evidências;
- handoff versionado para Chunking e Embeddings.

As implementações estão em [`src/parte_01_dados/`](src/parte_01_dados/), a
documentação em [`docs/parte_01_dados/`](docs/parte_01_dados/) e as evidências
em [`artifacts/audit/`](artifacts/audit/).

### João Vitor Althaus Godoi

Responsável pela Parte 3 (Agente Concierge) e pela integração ponta a ponta na AWS.

Agente — src/parte_03_04_agente_triagem/agent_concierge.py: agente Strands com duas ferramentas (retrieve_kb, store_handoff) rodando no Amazon Bedrock AgentCore Runtime. Grounding com citação de source_path, resposta "não sei" sem inferência, escalonamento com handoff, e classificação da decisão (responder / nao_sei / escalar) derivada em código.

Borda — lambda_gateway.py: Lambda que traduz o API Gateway (HTTP API) em InvokeAgentRuntime, com origem canônica do trace_id e falha segura.

Contratos compartilhados — src/shared/: get_settings() (configuração única) e os tipos usados pelas Partes 3, 4 e 5.

Infraestrutura — evolução do template.yaml (gateway e wiring das tools), infra/agentcore/ (container do agente e criação do Runtime) e os guias infra/DEPLOY.md e infra/README.md.

Deploy e validação ponta a ponta na AWS, cobrindo os três caminhos de decisão (o de escalonamento persistindo em DynamoDB) e a consulta por trace_id.

Registro consolidado em docs/registros_joao.md.

### Kaique Silva Sousa

Responsável por implementar a ferramenta de busca em uma função lambda e calibrar o treshold, alem de criar o dockerfile para gerar a imagem da lambda, criar o template de IaC, usando o AWS SAM. As implementações da ferramenta e o código de calibração do limiar estão em [`src/tools`](src/tools) o dockerfile em [`infra/retrieve_kb.Dockerfile`](infra/retrieve_kb.Dockerfile) e o template em [`infra/template.yaml`](infra/template.yaml). A documentação da implementação está em [`docs/parte_02_rag/rag_implementation.md`](docs/parte_02_rag/rag_implementation.md) e a documentação da calibração do limiar em [`artifacts/retrieval/calibration_report.json`](artifacts/retrieval/calibration_report.json)

### Bruno Jordão das Neves Moura

Responsável pela construção e disponibilização da base de conhecimento para o RAG, abrangendo a preparação dos documentos, definição e validação da estratégia de chunking, geração e avaliação dos embeddings e construção do índice vetorial.

Na Parte 2A, a contribuição concluída inclui:

- preparação e organização dos documentos do corpus para utilização na base de conhecimento;
- definição e aplicação de uma estratégia de chunking, considerando a estrutura e o conteúdo dos documentos;
- realização de experimentos com diferentes configurações de chunking, avaliando tamanho dos chunks, sobreposição e comportamento dos resultados, até a definição da configuração adotada;
- preservação dos metadados necessários à rastreabilidade e controle de vigência, incluindo chunk_id, doc_family_id, status,version_ordinal, effective_from, effective_to, source_path e section_title;
- avaliação comparativa de modelos de embeddings, considerando a adequação ao corpus e às consultas em português;
- seleção do modelo intfloat/multilingual-e5-small para a geração dos embeddings definitivos;
- geração dos embeddings definitivos de todo o corpus, utilizando normalização dos vetores para permitir a utilização de similaridade de cosseno por meio de Inner Product;
- construção do índice vetorial FAISS utilizando IndexFlatIP, mantendo o mapeamento entre cada vetor e seus respectivos metadados;
- implementação das rotinas de persistência e carregamento do índice e dos metadados;
- implementação da função de busca vetorial para consultas, retornando scores de similaridade e informações dos chunks recuperados;
- criação e execução de testes automatizados para validar a existência, estrutura, dimensionalidade, quantidade de vetores, correspondência entre índice e metadados e funcionamento da busca;
- adaptação dos testes para considerar que os artefatos vetoriais são regeneráveis e não versionados no Git, evitando que a ausência local de arquivos .faiss e .pkl seja tratada como falha de código;
- organização dos artefatos gerados de forma compatível com a execução posterior do pipeline de recuperação;
- publicação dos artefatos da base de conhecimento no Amazon S3, permitindo seu consumo pelas etapas posteriores da solução;
- documentação dos experimentos, decisões técnicas, validações e evidências relacionadas à construção da base.

As implementações relacionadas à Parte 2A estão organizadas em src/parte_02_rag/, os testes em tests/parte_02_rag/ e as documentações e evidências correspondentes estão distribuídas em docs/ e artifacts/.

## Responsabilidades planejadas por etapa

### Parte 1. Pipeline de dados

Responsável: Cleidyanne Castro Pereira

Escopo: limpeza do CSV, análises descritivas e registro do achado utilizado para orientar uma decisão de design.

### Parte 2. RAG e base vetorial

Responsável pela estratégia de recuperação e pela tool `retrieve_kb`: Kaique Silva

Responsável por chunking, embeddings e índice vetorial: Bruno Jordão das Neves Moura

Escopo do Bruno: definição e experimentação da estratégia de chunking, metadados de vigência e rastreabilidade, avaliação e seleção do modelo de embeddings, geração dos embeddings definitivos, construção e validação do índice vetorial FAISS, testes automatizados e publicação dos artefatos no S3.
Escopo do Kaique: filtro determinístico de documentos vigentes na busca,
calibração do limiar de "não sei" e avaliação da recuperação.

### Parte 3. Agente Concierge

Responsável: João Vitor Althaus Godoi

Escopo: agente, integração com Bedrock, grounding, citação de fonte, limiar de resposta e integração ponta a ponta.

### Parte 4. Triagem e escalonamento

Responsável: José Ivanildo

Escopo: política de suporte, critérios de escalonamento, urgência e geração do handoff para atendimento humano.

# Contribuição — Observabilidade e Auditoria

**Autor:** Natan Alencar

## Resumo

Atuei na frente de rastreabilidade e auditoria do Concierge ConectaTel, cobrindo desde a instrumentação inicial (dashboard, alarmes, filtros de métrica) até a evolução do projeto para um modelo sem dashboard agregado, mantendo integralmente a capacidade de auditoria por `trace_id`, retenção de logs e proteção de dados sensíveis.

## Trabalho realizado

### Observabilidade operacional

- Publicação inicial via CloudFormation do dashboard `concierge-conectatel-operacao`, dos alarmes `concierge-conectatel-gateway-errors` e `concierge-conectatel-retrieve-kb-errors`, e dos filtros de métrica `RespondDecisions`, `NoAnswerDecisions`, `EscalateDecisions` e `GatewayRuntimeErrors`, todos confirmados em `CREATE_COMPLETE`.
- Validação do comportamento esperado do alarme RAG em `INSUFFICIENT_DATA` logo após a criação, com `TreatMissingData: notBreaching` configurado para não tratar ausência de tráfego como incidente.
- Evolução da stack para remover o dashboard agregado, preservando log group, filtros de métrica, alarmes, retenção (14 dias) e a consulta por `trace_id` como mecanismo primário de verificação — o log group hoje é criado declarativamente antes da Lambda em instalações do zero.
- Diagnóstico e correção de uma regressão (HTTP 502 por sequência inválida de `ToolUse` no AgentCore/modelo Nova), localizada via consulta por `trace_id` e resolvida com simplificação do contrato da tool e atualização do Runtime (v3 → v4), restaurando HTTP 200 nos três desfechos (`responder`, `nao_sei`, `escalar`).

### Auditoria ponta a ponta

- Execução e validação da consulta de auditoria por `trace_id` (`e2e-handoff-20260901`) cobrindo gateway, `retrieve_kb`, `store_handoff` e AgentCore, com tempo total de 3,814 s (dentro da meta de 60 s).
- Confirmação do fluxo completo de escalonamento: decisão `escalar`, guardrail `titularidade/falecimento`, protocolo `CONCTL-20260901-6BFEA6` emitido e item correspondente localizado na tabela DynamoDB `concierge-conectatel-escalonamentos` com urgência `alta`.
- Cobertura complementar dos três desfechos do Concierge com evidência de evento estruturado:
  - `e2e-grounded-20260902` → `responder`, fontes `faq_geral.md` e `procedimento_desbloqueio_aparelho.md`, score `0,9114`.
  - `e2e-no-source-20260902` → `nao_sei`, fontes vazias, score nulo.
  - Handoff (`e2e-handoff-20260901`) → `escalar`, conforme acima.
- Revalidação pós-correção do Runtime com os três desfechos reexecutados pelo endpoint público (`review-green-answer`, `review-green-unknown`, `review-green-handoff`), todos retornando HTTP 200 com evidência consistente.

### Evidência formal de banca (T01, T02, T08)

- **T01** — pergunta fundamentada ("Como consulto meu consumo de dados?"), decisão `responder`, score `0,9114037752151489`, fonte `data/corpus/faq/faq_geral.md` com status `vigente`; confirmado tanto na chamada direta quanto na consulta posterior ao CloudWatch pelo mesmo `trace_id`.
- **T02** — pergunta fora do corpus ("Qual será a previsão do tempo amanhã?"), decisão `nao_sei`, sem resultados acima do limiar `0,85`; confirmado da mesma forma via CloudWatch.
- **T08** — suíte local de testes (`27 passed`) e validação do template SAM (`sam validate`), garantindo consistência da infraestrutura antes do deploy.
- Registro do limite conhecido: na Lambda `retrieve_kb` isolada, o evento de auditoria ainda não consolida fonte e guardrail junto com `trace_id`/decisão/score — isso depende da integração completa com o AgentCore/gateway (item pendente do caso T06, à época).

### Proteção de dados sensíveis na telemetria

- Validação de que a telemetria GenAI opera em modo `NO_CONTENT`: um teste com marcador inválido de telefone (`00 00000-0000`) não expôs o valor bruto nos spans.
- Confirmação, no trace funcional `review-green-private-20260902`, de que a trilha preserva o dado mascarado (`[TELEFONE_MASCARADO]`) em vez do valor original.
- Reconfirmação da retenção de 14 dias nos quatro grupos de logs (gateway, `retrieve_kb`, `store_handoff`, AgentCore) e ausência de erros recentes no gateway após o deploy mais recente.

## Pontos em aberto / próximos passos

- Consolidação definitiva do evento único de auditoria (pergunta + fontes + decisão + score + guardrail + handoff) diretamente no AgentCore, eliminando a limitação registrada em T08.
- Formalizar, na documentação final, a transição do modelo "com dashboard" para "sem dashboard operacional", já refletida no nome da branch e no roteiro de demonstração atualizado.

## Metodologia de trabalho

A squad adotará um fluxo Kanban para acompanhar as atividades. Essa é uma escolha de organização interna e complementa a divisão de responsabilidades definida na Parte 0 do desafio.

### Fluxo das atividades

1. Backlog: tarefa identificada e descrita, ainda não iniciada.
2. Em andamento: responsável trabalhando na implementação ou documentação.
3. Em revisão: contribuição pronta, com testes e evidências anexados.
4. Concluído: revisão realizada, testes aprovados e integração feita na branch principal.

### Regras de acompanhamento

- Cada tarefa deve ter um responsável, uma etapa do desafio e um critério de conclusão.
- O responsável deve atualizar código, documentação e testes relacionados à sua etapa.
- Toda contribuição deve ser revisada por pelo menos uma pessoa de outra frente.
- A squad deve manter um fluxo mínimo funcionando de ponta a ponta desde os primeiros dias.
- Alterações que afetem mais de uma etapa devem ser alinhadas com a pessoa responsável pela integração.
- O quadro deve ser revisado nos encontros da squad para identificar bloqueios e dependências.

## Regra de colaboração

Cada responsável deve atualizar o código, a documentação e os testes da própria etapa. Toda contribuição deve ser revisada por pelo menos uma pessoa de outra frente.

O responsável pela integração deve testar continuamente o fluxo completo entre dados, recuperação, agente, escalonamento e auditoria. A integração não deve ser executada somente na noite anterior à entrega.

## Fluxo de trabalho

1. Criar uma branch com o padrão `feat/parte-XX-descricao` ou `docs/descricao`.
2. Implementar a mudança e atualizar os testes correspondentes.
3. Executar `python -m pytest -q`.
4. Abrir um Pull Request para `main` com a descrição da mudança e a evidência do teste.
5. Solicitar revisão de pelo menos uma pessoa de outra frente.
6. Fazer merge somente após a revisão e a aprovação dos testes.

## Regras do repositório

Não versionar chaves AWS, dados reais, arquivos `.env`, índices gerados ou logs com informações sensíveis.

A versão demonstrada à banca deve corresponder à tag `v1.0-entrega`.
