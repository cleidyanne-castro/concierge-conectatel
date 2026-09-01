# Guia de Testes e Execução Local

## 1. Pré-requisitos
* Python 3.12 instalado.
* Ambiente virtual (`venv`) ativado com dependências instaladas (`bedrock-agentcore`, `strands`, `boto3`).
* Credenciais da AWS configuradas localmente (`aws configure`).

---

## 2. Variáveis de Ambiente no PowerShell

Antes de executar os testes locais, defina as variáveis no terminal:

```powershell
$env:STORE_HANDOFF_FUNCTION = "concierge-conectatel-store-handoff"
$env:MODEL_ID = "us.amazon.nova-lite-v1:0"   # Ou o modelo configurado na conta
$env:PYTHONPATH = "."
``` 

## 3. Execução de Teste Integrado (Bedrock + Lambda)

Simulação de interação em português diretamente no terminal:
```powershell
python -c "import json; from src.parte_03_04_agente_triagem.agent_concierge import run; res = run({'question': 'Minha fatura veio no valor de R$ 750 e nao concordo com essa cobranca. Meu telefone para retorno e 83 99999-8888.'}); print(json.dumps(res, indent=2, ensure_ascii=False))"
```

## 4. Consulta de Gravação no DynamoDB

Para verificar o registro criado via AWS CLI:

```powershell
# Escanear a tabela
aws dynamodb scan --table-name concierge-conectatel-escalonamentos --no-cli-pager

# Consultar item por arquivo de chave
'{"trace_id": {"S": "SEU_TRACE_ID_HERE"}}' | Set-Content -Encoding ASCII key.json
aws dynamodb get-item --table-name concierge-conectatel-escalonamentos --key file://key.json --no-cli-pager
```