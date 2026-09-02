# Interface local de testes

O painel Streamlit permite testar dois fluxos publicados na AWS:

- **Concierge ponta a ponta:** Interface → API Gateway → AgentCore → ferramentas;
- **Busca RAG direta:** Interface → Lambda `retrieve_kb`, útil para diagnóstico.

## Executar

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run src/interface/app.py
```

Ou, após instalar as dependências:

```bash
make ui
```

Abra o endereço exibido pelo Streamlit, normalmente `http://localhost:8501`.
Antes de testar, valide a sessão AWS:

```bash
aws sso login --profile AlunoAdmin-699038657189
```

Para o fluxo ponta a ponta, informe a URL `ConciergeApiUrl` exibida pelo deploy
no campo lateral da interface ou defina-a localmente em `.env`:

```dotenv
CONCIERGE_API_URL=https://<api-id>.execute-api.us-east-1.amazonaws.com/concierge
```

## Escopo atual

O painel mostra decisão, `trace_id`, resposta final e fonte do Concierge, além
do objeto de handoff quando houver escalonamento. No modo RAG direto, também
exibe latência, limiar, fontes recuperadas e scores. Em erros HTTP do Concierge,
o painel preserva o `trace_id` e o motivo técnico devolvidos pela API, e oferece
um atalho para o dashboard operacional do CloudWatch.
