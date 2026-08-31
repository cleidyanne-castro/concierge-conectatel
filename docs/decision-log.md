# Registro de decisões técnicas

Este arquivo registra decisões pontuais que precisam de contexto, alternativas,
evidência e responsável. Ele não substitui o comparativo planejado versus
executado, que está em [`arquitetura/planejado_vs_executado.md`](arquitetura/planejado_vs_executado.md), nem repete o registro de contribuições.

| Data | Parte | Decisão | Alternativas consideradas | Evidência | Responsável |
|---|---|---|---|---|---|
| Ago/2026 | Parte 0 | Criar e organizar o repositório GitHub com pastas por etapa do desafio | Manter código e documentação sem uma estrutura comum | [`CONTRIBUTING.md`](../CONTRIBUTING.md) e [`README.md`](../README.md) | Cleidyanne Castro Pereira |
| Ago/2026 | Arquitetura | Manter a arquitetura original como referência e registrar a arquitetura final separadamente | Substituir o desenho inicial e perder o histórico de evolução | [`docs/arquitetura/`](arquitetura/) e [`planejado_vs_executado.md`](arquitetura/planejado_vs_executado.md) | Cleidyanne Castro Pereira |
| Ago/2026 | Parte 1 | Usar uma arquitetura Medallion lógica com Python, Pandas, CSV, JSON e Markdown | Adotar PySpark, Delta Lake e processamento incremental sem exigência do desafio | [`docs/parte_01_dados/`](parte_01_dados/) | Cleidyanne Castro Pereira |
| Ago/2026 | Integração | Encadear Bronze, Silver e Gold em um Workflow Job do Databricks | Executar notebooks manualmente e deixar as dependências implícitas | [`docs/parte_01_dados/engenharia_dados.md`](parte_01_dados/engenharia_dados.md) | Cleidyanne Castro Pereira |
| Ago/2026 | Colaboração | Usar GitHub Projects, branches e Pull Requests para organizar a execução da squad | Centralizar o acompanhamento em conversas sem rastreabilidade | [GitHub Projects da Squad 4](https://github.com/users/cleidyanne-castro/projects/1) e [`CONTRIBUTING.md`](../CONTRIBUTING.md) | Cleidyanne Castro Pereira |
| Ago/2026 | Parte 3 | Um agente único com 2 tools em vez do orquestrador + 2 sub-agentes do diagrama | Multi-agente fiel ao diagrama | Com 2 ferramentas não há ambiguidade de seleção; menos custo/latência/pontos de falha. [`src/parte_03_04_agente_triagem/`](../src/parte_03_04_agente_triagem/) | João Vitor Althaus Godoi |
| Ago/2026 | Parte 3 | Agente em Amazon Bedrock AgentCore Runtime (container Strands) | Lambda simples com tool-use; Strands sem AgentCore | Fiel ao "Agentcore Runtime" do diagrama; sessão isolada e observabilidade nativa. [`infra/agentcore/`](../infra/agentcore/) | João Vitor Althaus Godoi |
| Ago/2026 | Parte 3 | Modelo `amazon.nova-lite-v1:0` | Claude Haiku/Sonnet 4.5 | Nova roda on-demand sem o formulário "Anthropic use case details" exigido para Claude; troca é 1 variável de ambiente | João Vitor Althaus Godoi |
| Ago/2026 | Infra | Manter AWS SAM (do Kaique) e estender; Dockerfiles em `infra/` | Migrar tudo para CDK | Evita refazer o deploy já validado; Docker é exigido nos dois casos (imagem da `retrieve_kb`). [`infra/template.yaml`](../infra/template.yaml) | João Vitor Althaus Godoi |
| Ago/2026 | Parte 5 | Auditoria por `trace_id` em logs estruturados no CloudWatch (Logs Insights), não `audit.jsonl` local | Arquivo `audit.jsonl` do scaffold original | Alinha com o diagrama final (CloudWatch); `trace_id` nasce na `lambda_gateway` e propaga por toda a cadeia. [`docs/proximas_etapas_04_05.md`](proximas_etapas_04_05.md) | João Vitor Althaus Godoi |
