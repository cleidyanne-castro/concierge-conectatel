# **Estratégia de Recuperação e Tool de Busca (retrieve\_kb)**

## **Objetivo**

Detalhar a implementação da ferramenta de busca vetorial do Concierge ConectaTel (retrieve\_kb), responsável por recuperar chunks relevantes do índice vetorial e garantir a aplicação rigorosa dos *guardrails* de segurança e vigência antes de passar o contexto para o Agente.

## **Estratégia utilizada**

O algoritmo de recuperação da Lambda (retrieve\_kb):

> * carrega os artefatos vetoriais e metadados estruturados;  
> * aplica o filtro determinístico de vigência antes do cálculo matemático;  
> * vetoriza a pergunta utilizando obrigatoriamente o prefixo exigido pelo modelo de linguagem;  
> * executa o cálculo de similaridade por produto escalar em matrizes filtradas;  
> * valida o limiar de confiança calibrado para evitar respostas fora de escopo;  
> * retorna os resultados estruturados ou a decisão segura de "não sei".

## **Arquitetura e Decisões de Implementação**

### **1\. Filtro Determinístico de Vigência (Guardrail)**

A regra mais estrita da arquitetura estabelece que o assistente **nunca** pode basear sua resposta em políticas ou documentos revogados. Depender exclusivamente de instruções em prompt para que o LLM entenda status provou-se vulnerável em sistemas agênticos.  
Para resolver isso de forma definitiva, implementamos um **filtro estrutural antes do cálculo de similaridade**:

> 1. A ferramenta recupera os metadados do índice gerado.  
> 2. Uma list comprehension filtra **apenas** os chunks que possuem o metadado status \== "vigente".  
> 3. Somente os embeddings correspondentes a esses chunks vigentes são convertidos em uma matriz Numpy.  
> 4. O produto escalar (equivalente à similaridade de cosseno para vetores normalizados) é executado **apenas** sobre os chunks da matriz filtrada.

Com isso, torna-se matematicamente impossível que um documento revogado receba um *score* de similaridade, garantindo que as respostas da inteligência artificial sejam embasadas exclusivamente nas regras de negócio atuais da ConectaTel.

### **2\. Seleção do Modelo de Embeddings**

Para a vetorização e cálculo de similaridade semântica, adotamos o modelo multilíngue intfloat/multilingual-e5-small.  
Na implementação da ferramenta de busca em Numpy puro, adaptamos o código para atender às especificações do modelo, que exige a inserção obrigatória do prefixo "query: " antes da pergunta enviada pelo usuário, garantindo o alinhamento semântico adequado durante a inferência.

### **3\. Calibração do Limiar de Confiança (Threshold)**

Para impedir que o assistente invente respostas (alucine) quando o usuário fizer perguntas fora do escopo do negócio, implementamos um corte de pontuação (limiar).  
A calibração foi validada confrontando perguntas positivas do projeto com questionamentos negativos ou fora de escopo.  
**Parâmetros definidos:**

> * **Modelo Utilizado:** intfloat/multilingual-e5-small  
> * **Limiar (Threshold) Selecionado:** 0.85

Se a melhor similaridade obtida na busca ficar abaixo de 0.85, a função aborta o retorno dos chunks e devolve diretamente a decisão estruturada "nao\_sei".

## **Contrato de Integração da Lambda**

A interface de I/O foi projetada para conversar nativamente com o Orquestrador e emitir telemetria padronizada.

### **Payload de Entrada**

> {  
>  "question": "texto da pergunta do cliente",  
>  "trace\_id": "uuid-propagado-pelo-agente"  
> }
