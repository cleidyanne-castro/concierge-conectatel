# Dashboard da Gold

## Objetivo

Oferecer uma visão executiva das dúvidas mais frequentes, do esforço de
atendimento e dos pontos em que o Concierge pode reduzir encaminhamentos.

## Fontes

O dashboard foi criado no Databricks com base no dataset tratado da Silver. Os
arquivos Gold continuam sendo os produtos analíticos oficiais para consumo e
auditoria:

- `gold_kpis.csv` para os cartões principais.
- `gold_categoria_resumo.csv` para concentração de temas.
- `gold_canal_resumo.csv` para comparação operacional.
- `gold_geografia_resumo.csv` para distribuição territorial.

## Visuais

- total de chamados e satisfação média.
- taxa de resolução no primeiro contato.
- taxa de encaminhamento humano.
- categorias e subcategorias mais frequentes.
- comparação de desempenho por canal.
- volume e duração média por estado e cidade.

Cada visualização deve exibir o volume ou denominador correspondente. Médias e
taxas não devem ser interpretadas sem observar a quantidade de registros
válidos.

Filtros disponíveis: canal, categoria, estado e plano atual. A Gold e suas
fontes estão implementadas no repositório. O dashboard publicado e sua
validação estão registrados em
`artifacts/audit/gold_dashboard_execution_evidence.md`.

## Storytelling para o produto

### Problema

A base tratada reúne 320 chamados, com satisfação média de 3,46. Apenas 151
foram resolvidos no primeiro contato e 63 foram encaminhados para atendimento
humano. O cenário indica oportunidade de melhorar a resolução inicial e reduzir
o esforço operacional.

### Conflito

Somados, os canais virtuais concentraram 94 resoluções no primeiro contato,
contra 57 na loja física. Esse resultado indica maior volume absoluto de
resoluções virtuais, mas não comprova maior rapidez ou eficiência, pois a
comparação não usa o total de chamados recebidos por canal. Na dimensão
regional, o Paraná apresentou duração mediana de 15 minutos em 52 chamados,
enquanto São Paulo apresentou 20,5 minutos em 33 chamados. A diferença pode
estar relacionada ao canal, à categoria ou à complexidade dos atendimentos.

### Resolução

Os achados orientam decisões de produto e operação: priorizar respostas guiadas
e conteúdos digitais para as categorias mais frequentes, melhorar a orientação
inicial e investigar canal e categoria antes de criar regras específicas por
estado. O dashboard registra evidências para essas decisões, mas não alimenta
diretamente o RAG ou o agente.

**Decisão de design:** o Concierge deve priorizar respostas guiadas e melhorar
a orientação inicial para aumentar a resolução no primeiro contato e reduzir
encaminhamentos desnecessários.

## Pain points observados

- **Concentração de demandas:** categorias recorrentes indicam onde respostas
  guiadas e artigos mais acessíveis podem reduzir esforço operacional.
- **Resolução abaixo da metade:** 151 de 320 chamados foram resolvidos no
  primeiro contato. Existe oportunidade de melhorar a orientação inicial e a
  recuperação de conteúdo.
- **Encaminhamento humano:** 63 de 320 chamados foram encaminhados. Esse grupo
  merece análise por categoria e canal para separar complexidade real de falha
  na jornada digital.
- **Comparações regionais sensíveis ao volume:** Paraná e São Paulo têm volumes
  diferentes. A mediana ajuda a reduzir o efeito de outliers, mas não permite
  atribuir causalidade ao estado sem controlar categoria e canal.

Na duração mediana, o Paraná apresenta 15 minutos em 52 chamados, enquanto São
Paulo apresenta 20,5 minutos em 33 chamados. A diferença é de 5,5 minutos, ou
aproximadamente 36,7% em relação à mediana do Paraná. Isso significa que o
atendimento típico em São Paulo dura mais, mas não prova que o Paraná seja mais
eficiente. A causa pode estar relacionada à complexidade dos chamados, ao canal
utilizado ou ao perfil das categorias. A recomendação de produto é investigar
esses fatores antes de criar uma regra específica por estado.

### Decisões de produto

- Priorizar jornadas digitais para as categorias mais frequentes.
- Comparar taxas por canal usando o total de chamados como denominador.
- Usar a loja física como referência para casos de maior complexidade.
- Investigar Paraná e São Paulo por categoria, canal, satisfação e
  encaminhamento antes de propor mudanças regionais.

## Referências visuais

- [Evidência da visão geral](../../artifacts/audit/gold_dashboard_evidence.png)
- [Evidência dos indicadores operacionais](../../artifacts/audit/gold_dashboard_operacao_evidence.png)
