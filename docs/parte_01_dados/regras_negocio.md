# Regras de negócio da Silver

## Objetivo

A Silver prepara o log de chamados para as análises descritivas e para o
consumo pelas etapas seguintes do projeto, usando Pandas e arquivos CSV/JSON.

## Regras aplicadas

- `chamado_id` identifica o chamado e deve ser preservado no resultado.
- Duplicatas exatas são removidas, mantendo a primeira ocorrência.
- Textos categóricos são aparados, convertidos para minúsculas e normalizados
  sem acentos para evitar categorias artificialmente diferentes.
- Valores textuais ausentes recebem `unknown` quando a coluna é categórica.
- `data_abertura` é convertida para data; valores inválidos tornam-se nulos e
  são contabilizados no relatório de qualidade.
- `duracao_minutos` e `satisfacao_1_a_5` são convertidos para números.
- A satisfação deve permanecer entre 1 e 5; durações negativas são inválidas.
- Campos booleanos aceitam representações como `sim/não`, `true/false` e
  `1/0`; valores não reconhecidos são tratados como `False`.

## Relação com o projeto

Essas regras tornam as categorias comparáveis nas três análises descritivas e
mantêm a rastreabilidade das decisões usadas para entender as dúvidas mais
frequentes dos assinantes. A Silver não cria respostas, embeddings ou regras
de roteamento: essas responsabilidades pertencem às etapas seguintes.
