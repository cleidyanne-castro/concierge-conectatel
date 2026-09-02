# Deploy passo a passo — para quem nunca usou Docker nem AWS

Guia do zero para subir a **tool de busca (`retrieve_kb`) + API Gateway** na sua
conta AWS, usando o `infra/template.yaml`.

Tempo estimado na primeira vez: **40–60 min** (a maior parte é download de
ferramentas e da imagem Docker). Deploys seguintes: ~3 min.

Custo: praticamente tudo cai no Free Tour da AWS. Fora do Free Tier, o gasto
parado é só o armazenamento da imagem no ECR (~US$ 0,10/mês por GB) — por isso
o passo 7 (limpeza) importa.

---

## O que cada ferramenta faz

| Ferramenta | Para quê | Você digita comando dela? |
|---|---|---|
| **AWS CLI** | autentica e fala com a AWS pelo terminal | sim, poucos |
| **Docker Desktop** | "caixa" isolada onde a Lambda é montada. A `retrieve_kb` é grande demais (traz `torch` + modelo de embeddings) para o formato .zip normal da Lambda, então ela vira uma **imagem de container** | **não** — o SAM chama o Docker por você; basta o Docker estar aberto |
| **AWS SAM CLI** | lê o `template.yaml`, manda o Docker montar a imagem, publica na AWS e cria Lambda + API Gateway + permissões | sim, 3 comandos |

Fluxo mental: `sam build` (monta) → `sam deploy` (publica) → você recebe uma URL.

---

## Pré-requisitos

- Windows 10/11, terminal **PowerShell**.
- Acesso à conta AWS do Squad 4 via portal SSO (`https://...awsapps.com/start`),
  com a role `AlunoAdmin`. Confirme com a Cleidyanne/Kaique a SSO start URL e a
  SSO region.
- Os arquivos `artifacts/embeddings/embeddings.json` e
  `artifacts/chunks/chunks.json` presentes no repo (vieram no commit da Parte 2).

---

## Passo 1 — Instalar as ferramentas

Rode um de cada vez. Depois **feche e reabra o PowerShell** (para o PATH atualizar).

```powershell
winget install --id Amazon.AWSCLI -e
```
```powershell
winget install --id Amazon.SAM-CLI -e
```
```powershell
winget install --id Docker.DockerDesktop -e
```

Reabra o terminal e confira as versões (cada comando deve imprimir um número, não erro):

```powershell
aws --version
```
```powershell
sam --version
```
```powershell
docker --version
```

---

## Passo 2 — Ligar o Docker

1. Abra o **Docker Desktop** pelo menu Iniciar.
2. Na primeira vez ele pede para instalar o "WSL 2" — aceite, reinicie o PC se pedir.
3. Espere o ícone da baleia (canto inferior direito) ficar **verde / "running"**.
4. Confirme no terminal:

```powershell
docker info
```

Se aparecer um bloco de informações (Server Version, etc.) sem `ERROR`, está pronto.
Se der `error during connect`, o Docker Desktop ainda não terminou de subir — espere 1 min.

> Você **não** vai rodar mais nenhum comando `docker` neste guia. Ele só precisa
> estar aberto enquanto você roda o `sam build`.

---

## Passo 3 — Conectar na sua conta AWS

A squad usa **AWS IAM Identity Center (SSO)** — você acessa por um portal
`https://...awsapps.com/start`. É este o caminho abaixo. (Se em vez disso você
tiver Access Key + Secret Key de um usuário IAM, pule para "Alternativa" no fim
deste passo.)

### 3.1 Pegue duas informações antes

1. **SSO start URL**: a URL do portal de acesso da empresa (abra no navegador e
   copie da barra de endereço). Tem a cara `https://algo.awsapps.com/start`.
2. **SSO region**: a região onde o Identity Center roda — quase sempre
   `us-east-1`, mas precisa ser a correta. Se não souber, pergunte no grupo do
   Squad 4 (quem já configurou sabe o valor).

### 3.2 Configure o perfil SSO

```powershell
aws configure sso
```

| Pergunta | O que responder |
|---|---|
| `SSO session name` | `conectatel-squad4` |
| `SSO start URL` | a URL do portal (3.1 item 1) |
| `SSO region` | `us-east-1` (ou a confirmada em 3.1 item 2) |
| `SSO registration scopes` | ENTER (aceita `sso:account:access`) |

Abre o navegador → login com o e-mail da empresa → **Allow** → volta ao terminal.

| Pergunta | O que escolher |
|---|---|
| Conta AWS | **a sua** (seu nome / seu ID de conta) — não a de outra pessoa da squad |
| Role | `AlunoAdmin` (ou a role autorizada para a sua conta) |
| `Default client Region` | `us-east-1` |
| `Profile name` | `AlunoAdmin-<ID_DA_SUA_CONTA>` |

### 3.3 A cada sessão de trabalho

O SSO expira em algumas horas. Sempre que abrir um PowerShell novo para trabalhar:

```powershell
aws sso login --profile AlunoAdmin-SEU_ID
```
```powershell
$env:AWS_PROFILE = "AlunoAdmin-SEU_ID"
```

No `.env`, troque `AWS_PROFILE=default` por `AWS_PROFILE=AlunoAdmin-SEU_ID` — aí o
snippet do passo 4 que carrega o `.env` já seta isso sozinho.

### 3.4 Confirme

```powershell
aws sts get-caller-identity --profile AlunoAdmin-SEU_ID
```

Tem que retornar um JSON com `Account` (o ID da sua conta) e `Arn` (contendo a
role). Se der erro de credencial, rode o `aws sso login` de novo — provavelmente
expirou.


---

## Passo 4 — Configurar as variáveis do projeto

Na raiz do repositório:

```powershell
cp .env.example .env
```

Abra o `.env` e confira a linha `S3_BUCKET_NAME`. O nome de bucket é **único no
mundo inteiro**; se `concierge-conectatel-kb-squad4` já existir, troque por algo
como `concierge-conectatel-kb-SEUNOME`.

Carregue as variáveis do `.env` na sessão do PowerShell:

```powershell
Get-Content .env | Where-Object { $_ -and $_ -notmatch '^\s*#' } | ForEach-Object { $k,$v = $_ -split '=',2; Set-Item "env:$k" $v }
```

Confira:

```powershell
echo "$env:S3_BUCKET_NAME | $env:AWS_REGION"
```

---

## Passo 5 — Criar o bucket S3 e subir a base de conhecimento

O bucket é criado **à mão** (o template não cria, só lê dele):

```powershell
aws s3 mb "s3://$env:S3_BUCKET_NAME" --region $env:AWS_REGION
```

- `BucketAlreadyExists` → o nome está em uso por outra conta; volte ao passo 4 e escolha outro.
- `BucketAlreadyOwnedByYou` → você já criou; pode seguir.

Suba os dois arquivos da base:

```powershell
python src/parte_02_rag/upload_to_s3.py
```

Deve terminar com `UPLOAD CONCLUÍDO COM SUCESSO`. Verifique:

```powershell
aws s3 ls "s3://$env:S3_BUCKET_NAME" --recursive
```

Você deve ver `index/embeddings.json` e `processed/chunks.json`.

---

## Passo 6 — Montar e publicar (o deploy em si)

> **Antes deste passo**, o AgentCore Runtime já precisa existir na conta de
> demonstração. O parâmetro `AgentRuntimeArn` é obrigatório e deve apontar para
> esse Runtime. Ver [`agentcore/README.md`](agentcore/README.md). Nunca use ARN
> de runtime pertencente a outra conta.

> Se você usa SSO (passo 3), garanta que a sessão está ativa **nesta janela do
> PowerShell** antes de continuar:
> ```powershell
> aws sso login --profile AlunoAdmin-SEU_ID
> $env:AWS_PROFILE = "AlunoAdmin-SEU_ID"
> ```
> O `sam build`/`sam deploy` usam o `$env:AWS_PROFILE`.

### 6.1 Montar a imagem

Com o Docker Desktop aberto:

```powershell
sam build
```

- Primeira vez: baixa a imagem base e as bibliotecas (`torch`, `sentence-transformers`).
  Pode levar **10–20 min** e usar vários GB de disco. É normal.
- Sucesso termina com `Build Succeeded`.
- Se disser `Docker is unreachable` → o Docker Desktop não está "running" (passo 2).

### 6.2 Publicar

Primeira vez (modo guiado — ele grava suas respostas em `samconfig.toml`):

```powershell
sam deploy --guided
```

Responda:
- **Stack Name**: `concierge-conectatel`
- **AWS Region**: `us-east-1`
- **Parameter KnowledgeBaseBucketName**: o mesmo valor de `$env:S3_BUCKET_NAME`
- **Parameter AgentRuntimeArn**: o ARN do AgentCore Runtime da conta de demonstração
- **Parameter CorsAllowOrigin**: `*` (ou a origem da interface)
- **Confirm changes before deploy**: `Y`
- **Allow SAM CLI IAM role creation**: `Y`
- **Disable rollback**: `N`
- **Create managed ECR repositories for all functions?**: **`Y`**  ← importante
- **Save arguments to configuration file**: `Y` (aceite o nome `samconfig.toml`)

Ele mostra a lista de recursos que vai criar, pede confirmação (`y`), sobe a
imagem para o ECR e cria a stack. Ao final imprime a seção **Outputs**.

**Copie os valores de `RetrieveKbApiUrl` e `ConciergeApiUrl`.**

Se `sam deploy` falhar com `AccessDenied` em `iam:CreateRole` ou
`ecr:CreateRepository`: a role `AlunoAdmin` da sua conta não permite. Fale com a
Cleidyanne sobre qual conta/role a squad vai usar na banca.

---

## Passo 7 — Testar

Para validar a tool de recuperação, troque a URL abaixo por `RetrieveKbApiUrl`:

```powershell
Invoke-RestMethod -Method Post -Uri "https://XXXX.execute-api.us-east-1.amazonaws.com/retrieve" -ContentType "application/json" -Body '{"question":"Qual o prazo para contestar uma cobranca da fatura?","trace_id":"teste-001"}'
```

- A **primeira** chamada demora ~20–40 s (a Lambda "acorda" e carrega o modelo).
  As seguintes respondem em ~1 s.
- Resposta esperada: um JSON com `decision`, `trace_id`, `results` e `threshold_used`.

Para validar o fluxo completo, use `ConciergeApiUrl` depois de publicar o
AgentCore Runtime:

```powershell
Invoke-RestMethod -Method Post -Uri "https://XXXX.execute-api.us-east-1.amazonaws.com/concierge" -ContentType "application/json" -Body '{"question":"Como consulto meu consumo de dados?","trace_id":"teste-concierge-001"}'
```

O resultado deve incluir `trace_id`, decisão, resposta e a fonte utilizada.

Para ver os logs da Lambda:

```powershell
sam logs --stack-name concierge-conectatel --name RetrieveKbFunction --tail
```

---

## Passo 8 — Deploys seguintes (depois de mexer no código)

```powershell
sam build
```
```powershell
sam deploy
```

(sem `--guided` — ele reusa o `samconfig.toml`).

---

## Passo 9 — Limpar tudo (fazer ao terminar / trocar de conta)

```powershell
sam delete --stack-name concierge-conectatel
```

Isso apaga Lambda, API Gateway, roles e o repositório ECR. O **bucket S3 não é
apagado** (foi criado à mão). Para remover também:

```powershell
aws s3 rb "s3://$env:S3_BUCKET_NAME" --force
```

---

## Problemas comuns

| Sintoma | Causa / solução |
|---|---|
| `aws: command not found` após instalar | não reabriu o PowerShell |
| `docker info` → `error during connect` | Docker Desktop não terminou de subir |
| `sam build` → `Docker is unreachable` | idem — abra o Docker Desktop e espere ficar verde |
| `sam build` muito lento / trava | primeira vez baixa GB de libs; deixe rodar |
| `CREATE_FAILED` + `BucketAlreadyOwnedByYou` | você já tinha criado o bucket antes; siga o deploy normalmente, o template não cria bucket |
| `AccessDenied` em `iam:` ou `ecr:` no deploy | a role não tem permissão; fale com a Cleidyanne sobre a conta/role |
| `Unable to locate credentials` / `sts get-caller-identity` falha | faltou `$env:AWS_PROFILE` nesta janela, ou o SSO expirou — rode `aws sso login --profile ...` e reexporte o `$env:AWS_PROFILE` |
| `Error loading SSO Token` / `token has expired` no `sam deploy` | `aws sso login --profile ...` de novo (sessão SSO expira em horas) |
| selecionou a conta errada no `aws configure sso` | rode `aws configure sso` de novo com outro `Profile name`, ou edite `~/.aws/config` |
| primeira chamada à API dá timeout | cold start; tente de novo, a 2ª responde |
| deploy trava em `UPDATE_ROLLBACK_FAILED` | `sam delete` e refaça do zero |
