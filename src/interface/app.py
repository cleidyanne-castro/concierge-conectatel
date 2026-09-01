"""Painel Streamlit para testar a Lambda retrieve_kb localmente."""

from __future__ import annotations

import streamlit as st

from src.interface.service import invoke_retrieve_kb
from src.shared.config import get_settings


st.set_page_config(page_title="Concierge ConectaTel", page_icon="📡", layout="wide")

settings = get_settings()
st.title("📡 Concierge ConectaTel")
st.caption("Painel local de teste da ferramenta RAG publicada na AWS.")

with st.sidebar:
    st.subheader("Ambiente")
    st.code(
        f"Região: {settings.aws_region}\n"
        f"Função: {settings.retrieve_kb_function}\n"
        f"Limiar: {settings.retrieval_score_threshold}",
        language=None,
    )
    st.info(
        "Esta versão consulta diretamente a Lambda retrieve_kb. "
        "O agente Bedrock/AgentCore será conectado depois do deploy completo."
    )

question = st.text_area(
    "Pergunta do assinante",
    placeholder="Ex.: Como consulto meu consumo de dados?",
    height=110,
)
trace_id = st.text_input(
    "Trace ID (opcional)",
    placeholder="teste-interface-001",
    help="Use um ID para localizar esta interação no CloudWatch após o teste.",
)

if st.button("Consultar base de conhecimento", type="primary", use_container_width=True):
    try:
        with st.spinner("Consultando a Lambda na AWS..."):
            result = invoke_retrieve_kb(question, trace_id or None)

        decision = result.get("decision", "nao_sei")
        if decision == "responder":
            st.success("Decisão: responder")
        else:
            st.warning("Decisão: não sei")

        col1, col2, col3 = st.columns(3)
        col1.metric("Trace ID", result.get("trace_id", "-"))
        col2.metric("Latência", f"{result.get('latency_ms', '-')} ms")
        col3.metric("Limiar", result.get("threshold_used", "-"))

        results = result.get("results", [])
        if results:
            st.subheader("Fontes recuperadas")
            for index, item in enumerate(results, start=1):
                label = f"{index}. {item.get('source_path', 'fonte sem caminho')} — score {item.get('score', 0):.4f}"
                with st.expander(label, expanded=index == 1):
                    st.caption(
                        f"Status: {item.get('status', '-')} | "
                        f"Seção: {item.get('section_title', '-')}"
                    )
                    st.markdown(item.get("text") or "Trecho indisponível.")
        else:
            st.info("Nenhuma fonte passou pelo limiar de recuperação.")

        with st.expander("Resposta técnica (JSON)"):
            st.json(result)
    except Exception as error:
        st.error(f"Não foi possível concluir o teste: {error}")
        st.caption("Verifique a sessão AWS SSO, o profile e o nome da Lambda no .env.")
