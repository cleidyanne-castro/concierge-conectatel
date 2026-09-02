"""Painel Streamlit para testar o Concierge e a busca RAG publicada."""

from __future__ import annotations

import streamlit as st

from src.interface.service import invoke_concierge, invoke_retrieve_kb
from src.shared.config import get_settings


st.set_page_config(page_title="Concierge ConectaTel", page_icon="📡", layout="wide")

settings = get_settings()
st.title("📡 Concierge ConectaTel")
st.caption("Painel local para testes funcionais publicados na AWS.")

with st.sidebar:
    st.subheader("Ambiente")
    st.code(
        f"Região: {settings.aws_region}\n"
        f"Função RAG: {settings.retrieve_kb_function}\n"
        f"Limiar: {settings.retrieval_score_threshold}",
        language=None,
    )
    test_mode = st.radio(
        "Fluxo de teste",
        ("Concierge ponta a ponta", "Busca RAG direta"),
        help="Concierge valida AgentCore e handoff; RAG direta diagnostica a recuperação.",
    )
    concierge_api_url = st.text_input(
        "URL do Concierge",
        value=settings.concierge_api_url,
        placeholder="https://<api-id>.execute-api.us-east-1.amazonaws.com/concierge",
    )
    if test_mode == "Concierge ponta a ponta":
        st.info("Fluxo: Interface → API Gateway → AgentCore → ferramentas.")
    else:
        st.info("Diagnóstico: Interface → Lambda retrieve_kb.")

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

button_label = (
    "Enviar ao Concierge"
    if test_mode == "Concierge ponta a ponta"
    else "Consultar base de conhecimento"
)

if st.button(button_label, type="primary", use_container_width=True):
    try:
        with st.spinner("Processando o teste na AWS..."):
            if test_mode == "Concierge ponta a ponta":
                result = invoke_concierge(question, trace_id or None, api_url=concierge_api_url)
            else:
                result = invoke_retrieve_kb(question, trace_id or None)

        decision = result.get("decision", "nao_sei")
        if decision == "responder":
            st.success("Decisão: responder")
        elif decision == "escalar":
            st.warning("Decisão: escalar para atendimento humano")
        else:
            st.warning("Decisão: não sei")

        col1, col2, col3 = st.columns(3)
        col1.metric("Trace ID", result.get("trace_id", "-"))
        col2.metric("Decisão", decision.replace("_", " ").title())
        if test_mode == "Busca RAG direta":
            col3.metric("Latência", f"{result.get('latency_ms', '-')} ms")
        else:
            col3.metric("Fonte", result.get("source_path") or "-")

        if test_mode == "Concierge ponta a ponta":
            st.subheader("Resposta do Concierge")
            st.write(result.get("answer") or "Não houve resposta textual.")
            if result.get("reason"):
                st.caption(f"Motivo técnico: {result['reason']}")
            if result.get("source_path"):
                st.caption(f"Fonte informada: `{result['source_path']}`")
            if handoff := result.get("handoff"):
                st.subheader("Handoff registrado")
                st.json(handoff)
        else:
            results = result.get("results", [])
            if results:
                st.subheader("Fontes recuperadas")
                for index, item in enumerate(results, start=1):
                    label = (
                        f"{index}. {item.get('source_path', 'fonte sem caminho')} "
                        f"— score {item.get('score', 0):.4f}"
                    )
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
        st.caption("Verifique a sessão AWS SSO e as configurações do ambiente.")
