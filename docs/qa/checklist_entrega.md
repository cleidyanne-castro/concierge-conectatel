# Checklist de entrega do desafio

Este checklist distingue implementação registrada de evidência ainda não
publicada. Um item só deve ser marcado como concluído quando houver código,
documentação e evidência compatíveis.

| Item | Estado | Evidência ou ação necessária |
|---|---|---|
| Parte 0: líder, papéis e integração/auditoria definidos | Concluído | [`CONTRIBUTING.md`](../../CONTRIBUTING.md), [`docs/arquitetura/`](../arquitetura/) e Kanban |
| Parte 1: limpeza, três análises e achado ligado a decisão de design | Concluído | [`docs/parte_01_dados/`](../parte_01_dados/) e [`artifacts/audit/`](../../artifacts/audit/) |
| Parte 2: chunking, embeddings, índice e filtro `status=vigente` antes do score | Implementado | Código, experimentos e artefatos em [`docs/parte_02_rag/`](../parte_02_rag/) e [`artifacts/`](../../artifacts/) |
| Parte 3: fonte, grounding, “não sei” por limiar e calibração | Implementado | Código e testes disponíveis. Registrar transcrições finais |
| Parte 4: escalonamento e handoff com problema, verificações e urgência | Implementado | Código e testes disponíveis. Registrar os casos finais de handoff |
| Parte 5: pergunta, fonte, decisão, guardrail e `trace_id` consultável em até 60 s | Implementado | [`docs/parte_05_governanca/`](../parte_05_governanca/) e [`consulta_trace_id_evidence.md`](../../artifacts/audit/consulta_trace_id_evidence.md) |
| 10 a 15 transcrições cobrindo todos os casos obrigatórios | Pendente | Inserir os registros finais em [`docs/transcricoes/`](../transcricoes/) |
| README executado do zero por um membro diferente do autor da configuração | Pendente | Registrar executor, data, ambiente e resultado |
| Slides para 15 minutos, vídeo plano B de até 3 minutos e transcrições impressas | Pendente | Inserir ou referenciar os materiais finais da banca |
| Tag `v1.0-entrega` criada antes do prazo e usada na demonstração | Pendente | Criar a tag a partir da `main` validada |
| AWS Budgets ativos e recursos contínuos desligados ou revisados | A validar | Anexar registro operacional da conta AWS |
