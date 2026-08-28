# Handoff de dados para Chunking e Embeddings

## Objetivo

Este documento define como a Engenharia de Dados entrega os insumos para a
Parte 2 do projeto: chunking, embeddings e índice de busca do Concierge
ConectaTel.

## Fontes oficiais

No Databricks, a origem oficial do corpus é:

```text
/Volumes/workspace/conectatel/raw_files/conectatel-dados/corpus/
```

Como o Bruno não possui acesso ao Databricks, a Engenharia de Dados deve
entregar a ele uma cópia local dos arquivos `.md` e do JSON de metadados. O
fluxo local recomendado é:

```text
data/corpus/
data/bronze/bronze_corpus_metadata.json
```

O corpus e os dados gerados no Volume não são baixados automaticamente pelo
clone do GitHub. Eles devem ser compartilhados pela squad como um pacote de
entrada ou por outro canal combinado, sem incluir credenciais.

O caminho do Databricks para referência da Silver é:

```text
/Volumes/workspace/conectatel/raw_files/silver/silver_corpus_metadata.json
```

## Contrato documental

Cada documento deve ser associado, quando disponível, aos seguintes campos:

| Campo | Uso |
|---|---|
| `source_path` | localização do documento original |
| `doc_family_id` | agrupamento de versões do mesmo documento |
| `version_ordinal` | ordem da versão |
| `effective_from` | início da vigência |
| `effective_to` | fim da vigência, quando houver |
| `status` | `vigente` ou `revogado` |
| `sha256` | rastreabilidade do arquivo |

Quando o documento não possuir um metadado explícito, a Parte 1 deve manter a
heurística registrada no inventário da Bronze. O campo não deve ser inventado
sem indicação no conteúdo.

## Regra de vigência

Antes de calcular similaridade ou selecionar um resultado, a Parte 2 deve
filtrar somente documentos com:

```text
status = vigente
```

Documentos revogados podem permanecer armazenados para auditoria, mas não devem
ser usados como fonte de resposta do Concierge.

## Como executar localmente

1. Clone o repositório e entre na pasta do projeto.

   ```bash
   git clone https://github.com/cleidyanne-castro/concierge-conectatel.git
   cd concierge-conectatel
   ```

2. Crie um ambiente virtual e instale as dependências.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Crie as pastas de entrada e receba da Engenharia de Dados o pacote do
   corpus. Copie os arquivos `.md` para `data/corpus/` e o
   `bronze_corpus_metadata.json` para `data/bronze/`.

   ```bash
   mkdir -p data/corpus data/bronze
   # copie ou extraia os arquivos recebidos nessas pastas
   ```

4. Confirme que cada documento possui `doc_family_id`, `version_ordinal`,
   `effective_from`, `effective_to` e `status` no JSON. Confirme também a
   presença de pelo menos uma família com versão `vigente` e `revogado`.

5. Execute o código de chunking e embeddings desenvolvido pela Parte 2 usando
   `data/corpus/` como entrada. Os resultados devem ser gravados fora de
   `data/`, por exemplo em `artifacts/` ou em um diretório local ignorado pelo
   Git.

Este fluxo não depende de Databricks. O tamanho dos chunks, a estratégia de
divisão, o modelo de embedding e o formato do índice são decisões da Parte 2
e devem ser registrados junto com a justificativa.

## Insumos para chunking

O processo de chunking deve usar o conteúdo integral dos arquivos `.md` e
preservar os metadados em cada chunk. Recomenda-se incluir:

- identificador do documento;
- título ou cabeçalho da seção;
- texto do chunk;
- caminho da fonte;
- família e versão documental;
- período de vigência;
- status de vigência;
- hash do arquivo;
- identificador estável do chunk.

O texto deve ser dividido por seções ou parágrafos, evitando separar uma regra
de negócio do seu contexto. O tamanho e a sobreposição dos chunks ficam sob
responsabilidade da Parte 2, desde que a fonte seja preservada.

## Insumos para embeddings

A equipe de Embeddings deve gerar vetores apenas para chunks documentais
válidos. Cada vetor deve manter uma referência ao chunk e ao documento de
origem, permitindo recuperar:

- o texto utilizado;
- a fonte original;
- a versão documental;
- o status de vigência;
- o hash do arquivo.

O índice vetorial deve permitir filtrar `status = vigente` antes ou durante a
busca, conforme a implementação escolhida.

## Chamados tratados

O arquivo `silver_calls_cleaned.csv` pode apoiar análises de linguagem,
categorias e decisões do Concierge. Os campos mais úteis são:

- `categoria`;
- `subcategoria`;
- `resumo_atendimento`;
- `canal`;
- `encaminhado_humano`;
- `resolvido_primeiro_contato`.

Esses dados não substituem o corpus oficial como fonte de resposta. Eles servem
para orientar prioridades, avaliar padrões de atendimento e apoiar decisões de
design.

## Responsabilidades

### Engenharia de Dados

- preservar o corpus original;
- mapear vigência e versões;
- normalizar o log de chamados;
- entregar caminhos e contratos estáveis;
- registrar alterações e evidências no GitHub.

### Chunking e Embeddings

- ler somente as fontes documentadas;
- preservar os metadados em cada chunk e vetor;
- filtrar documentos revogados;
- manter rastreabilidade até o arquivo original;
- registrar métricas de cobertura e recuperação.

## Exemplo de registro de chunk

```json
{
  "chunk_id": "politica_fatura_v2_001",
  "source_path": "corpus/politica_fatura__vigente.md",
  "doc_family_id": "politica_fatura",
  "version_ordinal": 2,
  "effective_from": "2026-01-01",
  "effective_to": null,
  "status": "vigente",
  "text": "Conteúdo da seção do documento..."
}
```

## Limites do handoff

A Engenharia de Dados não cria embeddings, respostas, prompts ou regras de
roteamento. A Parte 2 é responsável pelo chunking e pela indexação; as partes
seguintes são responsáveis pela geração da resposta, triagem, escalonamento e
auditoria da interação.

## Checklist de recebimento

- [ ] O corpus local foi recebido e contém somente documentos da ConectaTel.
- [ ] O JSON de metadados acompanha os arquivos do corpus.
- [ ] Existe ao menos um par vigente e revogado da mesma família.
- [ ] O filtro `status = vigente` será aplicado antes da similaridade.
- [ ] Cada chunk preservará a fonte, a família, a versão, o status e o hash.
- [ ] O processo local foi executado sem depender do Databricks.
