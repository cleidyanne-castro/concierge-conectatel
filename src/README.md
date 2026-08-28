# Código da aplicação

O diretório `src/` contém somente código executável e notebooks de trabalho.
A organização acompanha o fluxo funcional do Concierge:

| Pacote | Responsabilidade | Ponto de entrada |
|---|---|---|
| `parte_01_dados/` | ingestão, limpeza e qualidade dos dados | `pipeline.py` |
| `parte_02_rag/` | chunking, embeddings, índice e busca | `rag_index.py` |
| `parte_03_agente/` | agente, handler e integração Bedrock | `handler.py` |
| `parte_04_triagem/` | política de decisão e escalonamento | `policy.py` |
| `parte_05_governanca/` | auditoria e rastreabilidade | `audit.py` |
| `shared/` | configuração e tipos compartilhados | `config.py`, `types.py` |

## Convenções

- Notebooks documentam e reproduzem etapas; lógica reutilizável deve permanecer
  nos módulos `.py` correspondentes.
- A comunicação entre partes deve usar os tipos e contratos documentados em
  `docs/`, sem duplicar regras em cada pacote.
- `src/cli.py` é a entrada local para validar o fluxo do agente.
- Caminhos de dados e artefatos devem ser configuráveis; nenhum segredo deve
  ser codificado no código.

Veja o mapa completo em [`docs/README.md`](../docs/README.md) e os testes
correspondentes em [`tests/`](../tests/).
