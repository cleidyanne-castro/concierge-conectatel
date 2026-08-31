"""Entrada local do Concierge — valida o fluxo do agente sem API Gateway.

    python -m src.cli --question "Qual o valor do plano Conecta Basico?"

Requer credenciais AWS ativas (ex.: `aws sso login` + AWS_PROFILE) e as
dependencias do agente instaladas (`pip install -r requirements.txt`).
Chama o mesmo `run()` que o AgentCore Runtime usa em producao.
"""

from __future__ import annotations

import argparse
import json

from src.parte_03_04_agente_triagem.agent_concierge import run


def main() -> None:
    parser = argparse.ArgumentParser(description="Concierge ConectaTel (local)")
    parser.add_argument("--question", required=True, help="pergunta do assinante")
    parser.add_argument("--trace-id", default=None, help="trace_id opcional")
    args = parser.parse_args()

    resp = run({"question": args.question, "trace_id": args.trace_id})
    print(json.dumps(resp, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
