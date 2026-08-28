# Parte 2: RAG e base de conhecimento

Esta pasta documenta a entrega da base de conhecimento e o contrato para
Chunking e Embeddings.

## Responsabilidades

- preparar o corpus oficial.
- extrair e preservar metadados de vigência.
- dividir documentos em chunks rastreáveis.
- gerar embeddings e alimentar o índice vetorial.
- avaliar a recuperação com filtro obrigatório de documentos vigentes.

## Integração

O contrato de entrada e saída está em [`data_handoff.md`](data_handoff.md).
Os módulos de implementação estão em `src/parte_02_rag/`.
