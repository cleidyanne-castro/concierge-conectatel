# Dashboard da Gold

## Objetivo

Oferecer uma visão executiva das dúvidas mais frequentes, do esforço de
atendimento e dos pontos em que o Concierge pode reduzir encaminhamentos.

## Fontes

O dashboard deve consumir os arquivos Gold no Volume:

- `gold_kpis.csv` para os cartões principais;
- `gold_categoria_resumo.csv` para concentração de temas;
- `gold_canal_resumo.csv` para comparação operacional;
- `gold_geografia_resumo.csv` para distribuição territorial.

## Visuais

- total de chamados e satisfação média;
- taxa de resolução no primeiro contato;
- taxa de encaminhamento humano;
- categorias e subcategorias mais frequentes;
- comparação de desempenho por canal;
- volume e duração média por estado/cidade.

Cada visualização deve exibir o volume ou denominador correspondente. Médias e
taxas não devem ser interpretadas sem observar a quantidade de registros
válidos.

Filtros recomendados: período, canal, categoria, estado e plano. A Gold e suas
fontes estão implementadas no repositório; a criação efetiva no workspace deve
ser registrada com URL, data de atualização e evidência de carga.
