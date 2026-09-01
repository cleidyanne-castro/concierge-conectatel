# Reflexão da squad

## O que faríamos diferente

Se recomeçássemos o projeto, priorizaríamos ainda mais cedo a integração ponta a ponta entre dados, base de conhecimento, agente, escalonamento e auditoria. O desafio mostrou que as partes não funcionam de forma isolada. Uma alteração no tratamento dos dados pode afetar o RAG, o comportamento do agente e a qualidade das evidências apresentadas.

Também anteciparíamos os testes com perguntas de fronteira. Além das perguntas respondíveis, testaríamos desde o início casos sem fonte suficiente, documentos revogados e situações que exigem atendimento humano. Isso ajudaria a calibrar melhor as decisões do agente antes da etapa final de integração.

Outro ponto seria definir mais cedo um padrão único de documentação, nomes de arquivos, evidências e instruções de execução. Essa organização reduziria retrabalho e facilitaria o handoff entre os integrantes.

## A decisão técnica mais difícil

A decisão mais difícil foi equilibrar simplicidade, rastreabilidade e confiabilidade dentro do escopo de um MVP. O desafio não era apenas fazer o agente responder, mas garantir que ele soubesse quando responder, quando dizer que não tinha informação suficiente e quando encaminhar o caso para uma pessoa.

Na base de conhecimento, foi necessário tratar a vigência dos documentos de forma determinística, usando os metadados para priorizar apenas documentos vigentes antes da recuperação por similaridade. Essa decisão foi importante porque depender apenas do prompt poderia permitir que uma versão revogada fosse utilizada.

Na parte de dados, optamos por manter o processamento com Pandas e arquivos CSV, conforme previsto no hackathon. Embora tecnologias distribuídas pudessem parecer mais sofisticadas, elas não seriam necessárias para o volume sintético fornecido. A escolha preservou a compatibilidade com o escopo, facilitou a reprodução e permitiu concentrar esforço na qualidade das análises e na integração com o produto.

## O que cada membro aprendeu e aplicou

Cleidyanne aprofundou a importância de transformar dados tratados em decisões de produto. A limpeza, as análises descritivas, o dashboard e o storytelling foram usados para identificar oportunidades de melhoria na resolução inicial e apoiar a comunicação dos resultados.

Bruno desenvolveu conhecimentos sobre preparação de uma base de conhecimento, incluindo leitura de metadados de vigência, chunking, embeddings e indexação. O trabalho mostrou que a qualidade da recuperação depende tanto da divisão dos documentos quanto da preservação dos metadados.

Kaique aplicou conhecimentos de recuperação com filtro determinístico de vigência e calibração do comportamento de “não sei”. A principal aprendizagem foi que precisão não significa retornar sempre um resultado, mas retornar uma fonte adequada ou reconhecer os limites da base.

João trabalhou na construção e na orquestração do Concierge Agent, conectando o agente às ferramentas e ao fluxo de atendimento. A experiência reforçou a importância de grounding, composição clara das respostas e integração entre as etapas.

José desenvolveu a lógica de triagem, escalonamento e handoff. O aprendizado central foi que um bom escalonamento precisa preservar o contexto necessário para que outra pessoa continue o atendimento sem pedir que o cliente repita sua situação.

Natan trabalhou com governança, observabilidade, auditoria e organização da entrega. Essa etapa mostrou que uma solução confiável precisa permitir a reconstrução de uma resposta, identificar o `trace_id` correspondente e explicar seus guardrails e riscos.

## Aprendizado coletivo

O principal aprendizado da squad foi que uma solução de GenAI confiável depende menos de uma única tecnologia e mais da qualidade das decisões entre as etapas. Dados tratados, fontes vigentes, respostas fundamentadas, escalonamento contextualizado e trilhas de auditoria precisam funcionar como um conjunto.

A construção colaborativa também mostrou a importância de contratos claros entre as partes. O handoff da engenharia de dados para RAG, chunking e embeddings, por exemplo, só funciona quando os arquivos, metadados, formatos e responsabilidades estão documentados.

Ao final, a squad passou a enxergar o Concierge ConectaTel não apenas como um agente capaz de responder perguntas, mas como um sistema que precisa demonstrar limites, justificar suas decisões e permitir sua verificação. Esse foi o principal ganho técnico e profissional obtido durante o desafio.

## Pontos fortes da squad

- Integração entre dados, RAG, agente, escalonamento e governança.
- Divisão clara de responsabilidades entre os integrantes.
- Comunicação contínua durante as etapas de desenvolvimento.
- Uso de evidências para validar decisões técnicas e de produto.
- Preocupação com vigência, citações, limites do agente e prevenção de respostas inventadas.
- Documentação organizada para facilitar o handoff e a reprodução da solução.
- Capacidade de adaptar decisões técnicas ao escopo real do hackathon.
- Colaboração para transformar componentes individuais em uma solução ponta a ponta.

## Oportunidades de melhoria

- Integrar todas as partes desde o início, reduzindo dependências descobertas apenas na etapa final.
- Antecipar os testes de integração e os testes com perguntas não planejadas.
- Definir previamente padrões únicos para arquivos, documentação, evidências e nomenclaturas.
- Reservar mais tempo para ensaios da apresentação, teste cego e pergunta de auditoria.
- Formalizar os contratos entre as etapas, principalmente entre dados, base de conhecimento e agente.
- Planejar a consolidação final com mais antecedência para reduzir retrabalho antes da entrega.
