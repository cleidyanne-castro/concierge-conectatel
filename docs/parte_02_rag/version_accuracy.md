# Stretch: métrica de acerto de versão

## Objetivo

O Stretch mede se a recuperação entrega a versão vigente esperada para cada
pergunta de avaliação. A métrica complementa o filtro estrutural já usado pela
tool `retrieve_kb` e torna observável um risco importante do RAG: responder
com uma versão revogada quando existe uma versão atual da mesma família.

## Regra de avaliação

Para cada pergunta, o resultado é considerado correto quando:

1. o chunk vigente esperado aparece entre os `top_k` resultados
2. nenhum chunk `revogado` da mesma família aparece nesse conjunto

Assim, a presença de uma versão revogada é tratada como erro mesmo quando o
chunk vigente também aparece. A taxa é:

```text
acerto de versão = perguntas corretas / perguntas avaliadas
```

O conjunto inicial usa as 12 perguntas de
[`data/evaluation/embedding_questions.json`](../../data/evaluation/embedding_questions.json).
O valor padrão é `top_k = 5`, alinhado à avaliação de recuperação existente.

## Implementação e reprodução

A lógica reutilizável está em
[`src/parte_02_rag/version_accuracy.py`](../../src/parte_02_rag/version_accuracy.py).
Ela recebe uma função de recuperação, por isso pode ser testada sem modelo ou
rede. A execução de produção usa o mesmo filtro `status = vigente` aplicado
antes da similaridade na tool `retrieve_kb`.

Com as dependências locais instaladas, executar na raiz do repositório:

```bash
python -m src.parte_02_rag.version_accuracy
```

O relatório é salvo em
[`artifacts/retrieval/version_accuracy_report.json`](../../artifacts/retrieval/version_accuracy_report.json).
Os testes unitários estão em
[`tests/parte_02_rag/test_version_accuracy.py`](../../tests/parte_02_rag/test_version_accuracy.py).

As evidências visuais da execução estão em [`stretch2.png`](../../artifacts/audit/stretch2.png)
e do resultado detalhado em [`stretch1.png`](../../artifacts/audit/stretch1.png).

## Interpretação

O indicador mede a segurança da versão retornada, não a qualidade completa da
resposta textual do agente. Ele deve ser analisado junto de Hit@k, MRR,
calibração do limiar de “não sei” e testes de citação. Perguntas, corpus e
modelo devem ser mantidos versionados para que comparações futuras sejam
reproduzíveis.
