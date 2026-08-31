# Interface local de testes

O painel Streamlit permite demonstrar a base RAG publicada sem expor uma API
pública adicional. Ele usa o profile AWS da pessoa executora e invoca a Lambda
`retrieve_kb` diretamente.

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

## Escopo atual

O painel mostra decisão, latência, limiar, fontes, scores e o `trace_id` da
tool `retrieve_kb`. Com o AgentCore e API Gateway implantados, a interface deve
ser ajustada para chamar `/concierge` e exibir a resposta final do agente e o
handoff quando aplicável.
