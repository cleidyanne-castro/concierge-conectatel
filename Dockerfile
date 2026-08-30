FROM public.ecr.aws/lambda/python:3.11

# WORKDIR já vem definido como ${LAMBDA_TASK_ROOT} (/var/task) na imagem base,
# mas deixamos explícito por clareza
WORKDIR ${LAMBDA_TASK_ROOT}

# 1) dependências primeiro (aproveita cache de camada do Docker
#    enquanto o código muda com mais frequência que as libs)
COPY src/tools/retrieve_kb/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) código da tool + módulos compartilhados
COPY src/tools ./tools
COPY src/shared ./shared

# 3) baixa o modelo em build-time, não no cold start da Lambda
#    (evita chamada de rede no runtime, o que também é mais seguro se a
#    Lambda ficar numa VPC sem NAT/saída pra internet)
ENV HF_HOME=/opt/hf_cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-small')"

# 4) runtime não deve tentar bater no Hugging Face Hub de novo
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1

# module.function relativo ao WORKDIR — igual ao CMD que copiamos em ./tools
CMD ["tools.retrieve_kb.lambda_handler.handler"]