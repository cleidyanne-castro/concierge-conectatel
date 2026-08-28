# Testes

Os testes seguem a mesma decomposição funcional de `src/`. Isso permite
localizar rapidamente a cobertura de cada contrato sem duplicar a estrutura de
produção em outra nomenclatura.

| Área | Cobertura |
|---|---|
| `parte_01_dados/` | pipeline e transformação Silver |
| `parte_02_rag/` | filtro determinístico de vigência |
| `parte_03_agente/` | decisão e integração do agente |
| `parte_04_triagem/` | handoff e escalonamento |
| `parte_05_governanca/` | registro e consulta da auditoria |

Execute tudo com `python -m pytest -q` ou apenas uma área com
`python -m pytest tests/parte_01_dados -q`.
