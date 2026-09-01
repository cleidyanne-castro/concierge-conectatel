# Documentação do projeto

Esta é a entrada oficial para a documentação. A regra de organização é simples:
`src/` explica como o sistema executa, `docs/` explica contratos e decisões,
`tests/` comprova comportamento e `artifacts/` registra evidências de execução.

## Rota de leitura recomendada

1. [`../README.md`](../README.md): visão geral e execução local.
2. [`arquitetura/`](arquitetura/): desenho final e evolução da solução.
3. A documentação da parte que será alterada.
4. O teste correspondente em [`../tests/`](../tests/).
5. As evidências em [`../artifacts/`](../artifacts/), quando houver execução.

Cada pasta de parte é a fonte oficial da documentação daquele domínio. Não
duplicar regras entre partes: referenciar o contrato original.

- `arquitetura/`: arquitetura original planejada, arquitetura final e comparação entre planejado e executado.
- `arquitetura/README.md`: arquitetura final e comparação entre planejado e executado.
- `arquitetura/planejado_vs_executado.md`: registro do escopo previsto e entregue.
- `registros_cleidyanne.md`: registro exclusivo das contribuições de Cleidyanne Castro Pereira.
- `registros_joao.md`: registro das contribuições de João Vitor Althaus Godoi (Parte 3 + infra).
- `proximas_etapas_04_05.md`: instruções e contratos para as Partes 4 e 5.
- `parte_01_dados/`: pipeline Bronze, Silver e Gold.
- `parte_02_rag/`: handoff, chunking, embeddings e índice vetorial.
- `parte_03_agente/`: agente Concierge e integração com Bedrock.
- `parte_04_triagem/`: política de triagem e escalonamento.
- `parte_05_governanca/`: auditoria, rastreabilidade e controles.
- `relatorio/`: template do documento principal e versão final a preencher.
- `transcricoes/`: registros textuais dos testes obrigatórios.
- `apresentacao/`: slides usados na banca.
- `qa/`: evidências de execução, teste cego, auditoria e plano B.
