# Parte 2: RAG e base de conhecimento

Esta pasta documenta a entrega da base de conhecimento e o contrato para
Chunking e Embeddings.

## Responsabilidades

### Bruno: base de conhecimento

- preparar o corpus oficial.
- extrair e preservar metadados de vigência.
- dividir documentos em chunks rastreáveis.
- gerar embeddings e alimentar o índice vetorial.

### Kaique: recuperação

- implementar a tool `retrieve_kb`.
- filtrar documentos com `status = vigente` antes da similaridade.
- calibrar o limiar de "não sei".
- avaliar a recuperação com perguntas de teste.

## Integração

O contrato de entrada e saída está em [`data_handoff.md`](data_handoff.md).
Os módulos de implementação estão em `src/parte_02_rag/`.
