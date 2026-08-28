# Contribuições

## Contribuições realizadas

### Cleidyanne Castro Pereira

Responsável pela Parte 0 e pela coordenação técnica inicial. O registro
consolidado das contribuições está em
 [`docs/registros_cleidyanne.md`](docs/registros_cleidyanne.md).

## Responsabilidades planejadas por etapa

### Parte 1. Pipeline de dados

Responsável: Cleidyanne Castro Pereira

Escopo: limpeza do CSV, análises descritivas e registro do achado utilizado para orientar uma decisão de design.

### Parte 2. RAG e base vetorial

Responsável pela estratégia de RAG: Kaique Silva

Responsável por chunking, embeddings e índice vetorial: Bruno Jordão das Neves Moura

Escopo: chunking, metadados de vigência, embeddings, índice vetorial, filtro de documentos vigentes e avaliação da recuperação.

### Parte 3. Agente Concierge

Responsável: João Vitor Althaus Godoi

Escopo: agente, integração com Bedrock, grounding, citação de fonte, limiar de resposta e integração ponta a ponta.

### Parte 4. Triagem e escalonamento

Responsável: José Ivanildo

Escopo: política de suporte, critérios de escalonamento, urgência e geração do handoff para atendimento humano.

### Parte 5. Governança e auditoria

Responsável: Natan Alencar Maia

Escopo: audit trail, `trace_id`, guardrails, IAM, riscos conhecidos, consulta do registro e controles de custo.

## Metodologia de trabalho

A squad adotará um fluxo Kanban para acompanhar as atividades. Essa é uma escolha de organização interna e complementa a divisão de responsabilidades definida na Parte 0 do desafio.

### Fluxo das atividades

1. Backlog: tarefa identificada e descrita, ainda não iniciada.
2. Em andamento: responsável trabalhando na implementação ou documentação.
3. Em revisão: contribuição pronta, com testes e evidências anexados.
4. Concluído: revisão realizada, testes aprovados e integração feita na branch principal.

### Regras de acompanhamento

- Cada tarefa deve ter um responsável, uma etapa do desafio e um critério de conclusão.
- O responsável deve atualizar código, documentação e testes relacionados à sua etapa.
- Toda contribuição deve ser revisada por pelo menos uma pessoa de outra frente.
- A squad deve manter um fluxo mínimo funcionando de ponta a ponta desde os primeiros dias.
- Alterações que afetem mais de uma etapa devem ser alinhadas com a pessoa responsável pela integração.
- O quadro deve ser revisado nos encontros da squad para identificar bloqueios e dependências.

## Regra de colaboração

Cada responsável deve atualizar o código, a documentação e os testes da própria etapa. Toda contribuição deve ser revisada por pelo menos uma pessoa de outra frente.

O responsável pela integração deve testar continuamente o fluxo completo entre dados, recuperação, agente, escalonamento e auditoria. A integração não deve ser executada somente na noite anterior à entrega.

## Fluxo de trabalho

1. Criar uma branch com o padrão `feat/parte-XX-descricao` ou `docs/descricao`.
2. Implementar a mudança e atualizar os testes correspondentes.
3. Executar `python -m pytest -q`.
4. Abrir um Pull Request para `main` com a descrição da mudança e a evidência do teste.
5. Solicitar revisão de pelo menos uma pessoa de outra frente.
6. Fazer merge somente após a revisão e a aprovação dos testes.

## Regras do repositório

Não versionar chaves AWS, dados reais, arquivos `.env`, índices gerados ou logs com informações sensíveis.

A versão demonstrada à banca deve corresponder à tag `v1.0-entrega`.
