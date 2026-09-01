# Container do Agente Concierge para o Amazon Bedrock AgentCore Runtime.
# Contrato do Runtime: ARM64, escuta na porta 8080, expõe POST /invocations e
# GET /ping — o BedrockAgentCoreApp.run() cuida disso.
#
# Build SEMPRE a partir da RAIZ do repo (o contexto precisa enxergar src/):
#   docker build --platform linux/arm64 -f infra/agentcore/Dockerfile -t <tag> .

FROM public.ecr.aws/docker/library/python:3.12-slim

WORKDIR /app

COPY src/parte_03_04_agente_triagem/agent-requirements.txt .
RUN pip install --no-cache-dir -r agent-requirements.txt

# Só o que o agente importa: o pacote src/, shared/ e a propria parte.
COPY src/__init__.py ./src/__init__.py
COPY src/shared ./src/shared
COPY src/parte_03_04_agente_triagem ./src/parte_03_04_agente_triagem

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

# opentelemetry-instrument: emite os spans do agente pro collector do Runtime.
CMD ["opentelemetry-instrument", "python", "-m", "src.parte_03_04_agente_triagem.agent_concierge"]
