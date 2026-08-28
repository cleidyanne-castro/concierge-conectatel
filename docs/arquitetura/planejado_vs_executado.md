# Planejado versus executado

Este registro conecta os dois documentos de planejamento do GitHub ao desenho
final anexado pela squad. A comparação evita confundir intenção arquitetural
com componente já executado.

## Planejado

- pipeline para o log de chamados e o corpus documental.
- RAG com chunking, embeddings e busca vetorial.
- agente com resposta fundamentada e filtro de vigência.
- escalonamento com handoff.
- observabilidade e auditoria por `trace_id`.

## Executado na Engenharia de Dados

- Bronze com preservação, inventário, schema, qualidade e vigência.
- Silver com normalização, tipagem, regras de negócio, deduplicação e testes.
- Gold com KPIs, três análises, síntese e decisões de design.
- Workflow Job com dependências entre as três camadas.
- handoff documentado para Chunking e Embeddings.
- evidências de execução registradas no GitHub.

## Arquitetura final

Os arquivos visuais devem ser lidos em conjunto:

- [`arquitetura_conectatel_planejada.jpg`](arquitetura_conectatel_planejada.jpg): desenho original de referência.
- [`arquitetura_conectatel_final.jpg`](arquitetura_conectatel_final.jpg): desenho final anexado pela squad.

A comparação mostra a evolução entre o escopo planejado e a arquitetura
consolidada. O desenho final mantém a integração entre pipeline de dados,
componentes agentes e governança.

## Critério de leitura

Quando um componente aparece no diagrama, mas não possui notebook, teste ou
evidência de execução no repositório, ele deve ser tratado como integração
planejada ou responsabilidade de outra parte do projeto.
