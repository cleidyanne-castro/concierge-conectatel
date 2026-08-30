FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

RUN pip install --upgrade pip

# torch CPU-only: o Lambda não tem GPU, mas por padrão o pip instala a build
# com toda a stack CUDA da NVIDIA (cudnn, cublas, nccl, cusolver, triton...) —
# mais de 2GB de peso morto que nunca seria executado. Instalar a build "cpu"
# primeiro faz o pip reaproveitar essa instalação quando sentence-transformers
# pedir torch>=1.11.0 logo depois, em vez de baixar a versão GPU por engano.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY src/tools/retrieve_kb/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/tools ./tools
COPY src/shared ./shared

ENV HF_HOME=/opt/hf_cache
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-small')"

ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1

CMD ["tools.retrieve_kb.lambda_handler.handler"]