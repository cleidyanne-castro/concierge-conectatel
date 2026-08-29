# Experimentos de Embeddings

## Objetivo

Avaliar modelos de embeddings adequados ao idioma português e ao
ambiente de execução local, utilizando um conjunto controlado de
perguntas derivadas do corpus ConectaTel.

A avaliação considera a capacidade dos modelos de recuperar os chunks
esperados por meio de similaridade semântica.

## Conjunto de avaliação

Foram utilizadas 12 perguntas associadas previamente aos chunks
esperados.

O conjunto contempla diferentes tipos de informação presentes no
corpus, incluindo perguntas sobre políticas, procedimentos, planos,
FAQ e controle de versões documentais.

Também foi incluído caso envolvendo documento com versão vigente e
revogada, permitindo avaliar se o retrieval prioriza a informação
atualmente válida.

## Modelos avaliados

### Modelo 1

`intfloat/multilingual-e5-small`

Modelo multilíngue utilizado para geração dos embeddings dos chunks
e das perguntas.

### Modelo 2

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

Modelo multilíngue utilizado como alternativa para comparação.

## Resultados

| Modelo | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---:|---:|---:|---:|
| intfloat/multilingual-e5-small | 33,33% | 75,00% | 83,33% | 0,5444 |
| paraphrase-multilingual-MiniLM-L12-v2 | 25,00% | 66,67% | 75,00% | 0,4514 |

## Análise

O modelo `intfloat/multilingual-e5-small` apresentou desempenho
superior em todas as métricas avaliadas.

Em relação ao segundo modelo, apresentou:

- maior Hit@1;
- maior Hit@3;
- maior Hit@5;
- maior MRR.

O resultado indica maior capacidade de posicionar os chunks relevantes
nas primeiras posições do ranking de recuperação.

O Hit@5 de 83,33% indica que o chunk esperado foi recuperado entre os
cinco primeiros resultados em 10 das 12 perguntas avaliadas.

## Decisão

O modelo selecionado para a geração dos embeddings definitivos é:

`intfloat/multilingual-e5-small`

A escolha foi baseada nos resultados quantitativos obtidos no conjunto
de avaliação, considerando também a adequação ao idioma do corpus e a
possibilidade de execução local.

A validação de documentos com versões vigente e revogada foi considerada
na análise para evitar que uma informação documentalmente inválida fosse
priorizada pelo retrieval.

## Artefatos

Os resultados individuais de cada modelo foram armazenados em:

- `artifacts/embeddings/evaluation/multilingual_e5_small.json`
- `artifacts/embeddings/evaluation/multilingual_minilm.json`

A comparação consolidada foi armazenada em:

- `artifacts/embeddings/evaluation/comparison.json`