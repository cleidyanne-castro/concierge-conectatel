# Contribuições

## Status atual

Até o momento, a squad está na Parte 0 do desafio oficial, que corresponde à organização, definição de responsabilidades e preparação da estrutura de trabalho.

## Contribuições realizadas

### Cleidyanne Castro Pereira

Responsável pela Parte 0 e pela coordenação técnica inicial.

- Definição da estrutura inicial do repositório do Squad 4.
- Criação e organização do repositório público no GitHub.
- Organização das pastas por etapa do desafio.
- Criação da arquitetura visual final do Concierge ConectaTel.
- Inclusão da arquitetura final em `docs/arquitetura/arquitetura_conectatel_final.jpg`.
- Criação do README operacional para avaliadores e pessoas externas à squad.
- Inclusão das instruções de instalação, configuração, execução, testes, auditoria e troubleshooting.
- Criação da apresentação executiva inicial para stakeholders e banca técnica.
- Criação do template do relatório final do hackathon com base no relatório anterior da squad.
- Organização do template por Partes 0, 1, 2, 3, 4, 5 e Stretch.
- Inclusão de placeholders para decisões técnicas, evidências, transcrições, riscos e reflexão coletiva.
- Preparação do relatório final de contribuições em PDF.
- Definição do fluxo inicial de colaboração, revisão e integração.

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
