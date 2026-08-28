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

A base contém 320 chamados, satisfação média de 3,46 e 151 resoluções no
primeiro contato, equivalentes a 47,2% dos registros. A dashboard deve ser
apresentada como uma leitura de oportunidade para o produto, e não apenas como
um painel operacional.

O gráfico de resolução por canal mostra contagens de chamados resolvidos no
primeiro contato. Na leitura atual, os canais virtuais somam 94 resoluções e a
loja física representa 57. Assim, a maior parte das resoluções ocorreu fora do
atendimento presencial. Esse achado sustenta o fortalecimento das jornadas
digitais para as categorias mais frequentes, mantendo a loja física como apoio
para casos que exigem orientação ou intervenção especializada.

Essa comparação representa volume de resoluções, não eficiência percentual por
canal. Para afirmar que um canal é mais eficiente, é necessário dividir as
resoluções pelo total de chamados recebidos naquele canal. A dashboard mantém o
volume total como contexto para evitar uma conclusão indevida.

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

- [Evidência do recorte de loja física](../../artifacts/audit/gold_dashboard_loja_fisica_evidence.jpg)
