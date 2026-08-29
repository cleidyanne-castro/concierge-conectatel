# Experimentos de Chunking

## Objetivo

Avaliar diferentes configurações de chunking para o corpus da
ConectaTel, considerando tamanho dos chunks, overlap, preservação
de contexto e quantidade de chunks gerados.

O objetivo é selecionar uma configuração adequada para as etapas
posteriores de embeddings, indexação e retrieval.

## Estratégia utilizada

O algoritmo de chunking:

- remove o frontmatter YAML;
- divide os documentos por seções Markdown;
- prioriza a divisão por parágrafos;
- divide parágrafos maiores que o limite configurado;
- procura preservar finais de frases;
- evita cortar palavras;
- utiliza overlap entre chunks;
- preserva metadados documentais em cada chunk.

## Experimento 1 — Baseline

### Configuração

- chunk_size: 800
- chunk_overlap: 150

### Resultado

- Documentos processados: 12
- Chunks gerados: 59

### Observações

A configuração produziu 59 chunks.

A inspeção inicial mostrou que o algoritmo preserva as seções
documentais, porém alguns conteúdos maiores que o limite são
divididos em mais de um chunk.

A utilização de overlap mantém parte do contexto entre chunks
consecutivos, reduzindo o risco de perda de informação nas divisões.

Essa configuração será utilizada como baseline para comparação
com outras configurações.

## FASE 4 — Validação da qualidade do chunking

Após a geração dos chunks, foi realizada uma validação das regras
definidas para a etapa de chunking.

### 1. Chunks vazios ou excessivamente pequenos

Os chunks gerados foram inspecionados quanto à existência de conteúdo
vazio.

Não foram identificados chunks vazios.

Também foram observados chunks menores que o tamanho máximo
configurado. Esses casos são esperados, principalmente quando uma
seção ou conteúdo documental é menor que o limite definido.

Portanto, não foi necessário remover ou juntar chunks artificialmente.

### 2. Limites de tamanho

A configuração utilizada foi:

- chunk_size: 800
- chunk_overlap: 150

Os chunks respeitam a estratégia de divisão definida pelo algoritmo,
utilizando o tamanho configurado como limite para a segmentação.

Conteúdos maiores são divididos em múltiplos chunks, com sobreposição
entre partes consecutivas.

### 3. Preservação de títulos e contexto

Os chunks preservam o campo `section_title`, permitindo identificar
a seção documental de origem.

O texto também mantém o conteúdo da seção correspondente e utiliza
overlap entre chunks consecutivos.

Durante a inspeção foram observados alguns chunks iniciando ou
terminando no meio de uma frase. Isso ocorre nas divisões de conteúdos
maiores e é compensado parcialmente pelo overlap, que mantém contexto
entre os chunks consecutivos.

Não foram identificados cortes que eliminassem informações relevantes
do corpus.

### 4. Preservação dos metadados

Cada chunk mantém os principais metadados documentais:

- `chunk_id`
- `source_path`
- `doc_family_id`
- `version_ordinal`
- `effective_from`
- `effective_to`
- `status`
- `sha256`
- `section_title`

A validação confirmou que os metadados permitem relacionar cada chunk
ao documento e à versão documental correspondente.

Isso é especialmente importante para o controle de versões do corpus,
como no caso das políticas de reembolso, que possuem versões revogada
e vigente.

### 5. Testes das regras de chunking

Foram verificadas as seguintes regras:

- geração de chunks para os documentos do corpus;
- ausência de chunks vazios;
- preservação dos metadados;
- identificação da seção de origem;
- aplicação de overlap;
- manutenção do vínculo com a versão documental;
- geração de arquivo `chunks.json` válido para as etapas seguintes.

O resultado da validação foi considerado satisfatório para prosseguir
para as etapas de embeddings, indexação e retrieval.

## Configuração final

Com base na inspeção realizada, a configuração definida para seguir
nas próximas etapas é:

- chunk_size: 800
- chunk_overlap: 150

Resultado:

- Documentos processados: 12
- Chunks gerados: 59

A configuração foi mantida por apresentar equilíbrio adequado entre
granularidade e preservação de contexto para o corpus utilizado.

## Alternativas avaliadas

| Experimento | chunk_size | chunk_overlap | Documentos | Chunks | Observações |
|---|---:|---:|---:|---:|---|
| E1 - Baseline / Final | 800 | 150 | 12 | 59 | Configuração selecionada |
| E2 | 600 | 100 | 12 | 63 | Alternativa registrada |
| E3 | 1000 | 200 | - | - | Não utilizada |

A configuração final poderá ser reavaliada posteriormente caso os
testes de retrieval indiquem perda de contexto ou recuperação
insatisfatória.

## Critério de decisão

A configuração final não foi escolhida somente pela quantidade
de chunks.

Foram considerados:

1. preservação de contexto;
2. ausência de chunks vazios;
3. respeito aos limites de tamanho;
4. preservação de títulos e metadados;
5. capacidade de recuperar informações relevantes;
6. equilíbrio entre granularidade e contexto.

A configuração `chunk_size=800` e `chunk_overlap=150` foi selecionada
como configuração final da etapa de chunking e será utilizada como
entrada para as próximas etapas do pipeline.