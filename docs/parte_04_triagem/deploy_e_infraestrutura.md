# Deploy e Infraestrutura AWS SAM

## 1. Estrutura do Template SAM (`infra/agentcore/template.yaml`)

O arquivo de infraestrutura gerencia:
* **`StoreHandoffFunction`:** AWS Lambda rodando Python 3.12.
* **`EscalonamentosTable`:** Tabela DynamoDB com chave primária `trace_id`.
* **`RetrieveKbFunction`:** Lambda de integração com a Knowledge Base.

---

## 2. Instruções de Deploy

### Build da Aplicação
```powershell
sam build --template-file infra/template.yaml
sam deploy --guided