# Contribuição

## Responsabilidades por etapa

- `src/parte_01_dados/`: Cleidyanne — Parte 1.
- `src/parte_02_rag/`: Kaique — RAG; Bruno — chunking, embeddings e índice.
- `src/parte_03_agente/`: João Vitor — agente e integração Bedrock.
- `src/parte_04_triagem/`: José Ivanildo — política e escalonamento.
- `src/parte_05_governanca/`: Natan — auditoria e controles.
- `docs/`, README, arquitetura e slides: Cleidyanne, com conteúdo técnico fornecido por cada responsável.

## Fluxo de trabalho

1. Criar branch `feat/parte-XX-descricao` ou `docs/descricao`.
2. Implementar a mudança e atualizar testes/documentação da etapa.
3. Executar `python -m pytest -q`.
4. Abrir Pull Request para `main` com evidência do teste.
5. Solicitar revisão de pelo menos uma pessoa de outra frente.
6. Fazer merge somente após os testes passarem.

Não versionar chaves AWS, dados reais, `.env`, índices gerados ou logs com informações sensíveis. A versão demonstrada deve ser congelada na tag `v1.0-entrega`.
