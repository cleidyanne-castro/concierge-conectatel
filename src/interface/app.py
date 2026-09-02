"""Painel Streamlit para testar o Concierge e a busca RAG publicada."""

from __future__ import annotations

import streamlit as st

from src.interface.service import ConciergeApiError, invoke_concierge, invoke_retrieve_kb
from src.shared.config import get_settings


st.set_page_config(
    page_title="Concierge ConectaTel",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)

settings = get_settings()
dashboard_url = (
    f"https://{settings.aws_region}.console.aws.amazon.com/cloudwatch/home"
    f"?region={settings.aws_region}#dashboards:name=concierge-conectatel-operacao"
)

st.markdown(
    """
    <style>
      /* Paleta escura com contraste AA (>= 4.5:1) sobre o fundo #0d0e14.
         Texto de apoio: #c9cdda (~9:1). Detalhe/realce: #c2b9ff. */
      .stApp { background: radial-gradient(circle at 82% -10%, #2f2769 0, #11121a 38%, #0d0e14 78%); }
      .block-container { max-width: 1180px; padding-top: 2.4rem; padding-bottom: 3rem; }
      [data-testid="stSidebar"] { background: #141520; border-right: 1px solid #2f3142; }
      [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
      .brand-kicker, .eyebrow { color: #c2b9ff; font-size: .78rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; }
      .brand-name { color: #ffffff; font-size: 1.35rem; font-weight: 750; margin: .15rem 0 .25rem; }
      .brand-copy, .muted { color: #c9cdda; font-size: .9rem; line-height: 1.55; }
      .hero { background: linear-gradient(120deg, rgba(120,104,255,.28), rgba(20,21,31,.85) 58%); border: 1px solid rgba(170,160,255,.4); border-radius: 20px; padding: 2rem 2.1rem; margin-bottom: 1.5rem; }
      .hero h1 { color: #ffffff; font-size: clamp(2rem, 4vw, 3.3rem); letter-spacing: -.045em; margin: .35rem 0 .55rem; }
      .hero p { color: #dfe1ec; font-size: 1.04rem; line-height: 1.55; margin: 0; max-width: 680px; }
      .section-title { color: #ffffff; font-size: 1.06rem; font-weight: 700; margin: .2rem 0 .25rem; }
      .section-copy { color: #c9cdda; font-size: .9rem; margin-bottom: 1rem; }
      .result-card { background: #16171f; border: 1px solid #3a3c50; border-radius: 16px; padding: 1.25rem; margin-top: 1rem; }
      .status-dot { color: #7ff0c2; font-size: .74rem; font-weight: 700; letter-spacing: .05em; }
      .stButton > button, .stLinkButton > a { border-radius: 10px !important; font-weight: 650 !important; min-height: 2.75rem; }
      [data-testid="stMetric"] { background: rgba(255,255,255,.05); border: 1px solid #3a3c50; border-radius: 12px; padding: .75rem; }
      [data-testid="stMetricLabel"] p { color: #c9cdda !important; }
      [data-testid="stMetricValue"] { color: #ffffff; }
      /* caption nativo do Streamlit: sobe de ~2.8:1 para ~7:1 */
      [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: #b9bdcc !important; }
      .stExpander summary, .stExpander summary p { color: #e7e9f2 !important; }
      .flow-note { border-left: 3px solid #8b80ff; color: #cdd0dd; font-size: .88rem; line-height: 1.5; margin: .5rem 0 1rem; padding: .2rem 0 .2rem .8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="brand-kicker">AWS · Agentic RAG</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-name">ConectaTel</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="brand-copy">Painel de validação do Concierge, com decisões rastreáveis e operação observável.</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("**Ambiente de demonstração**")
    st.markdown('<span class="status-dot">● CONECTADO À AWS</span>', unsafe_allow_html=True)
    st.code(
        f"Região: {settings.aws_region}\n"
        f"RAG: {settings.retrieve_kb_function}\n"
        f"Limiar: {settings.retrieval_score_threshold}",
        language=None,
    )
    st.link_button("Dashboard operacional ↗", dashboard_url, use_container_width=True)
    st.divider()
    st.markdown("**O que cada fluxo valida**")
    st.markdown(
        "<div class='brand-copy'><b>Concierge</b><br>API Gateway, AgentCore e ferramentas.<br><br>"
        "<b>RAG direto</b><br>Recuperação, fontes e limiar.</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <section class="hero">
      <div class="eyebrow">Central de testes</div>
      <h1>Teste o Concierge com confiança.</h1>
      <p>Envie uma pergunta, acompanhe a decisão e use o mesmo trace para investigar cada etapa no CloudWatch.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

form_column, guide_column = st.columns([1.65, 0.85], gap="large")

with form_column:
    st.markdown('<div class="section-title">Nova validação</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Escolha o fluxo e informe uma pergunta como um assinante faria.</div>',
        unsafe_allow_html=True,
    )
    with st.container(border=True):
        test_mode = st.radio(
            "Fluxo de teste",
            ("Concierge ponta a ponta", "Busca RAG direta"),
            horizontal=True,
        )
        concierge_api_url = st.text_input(
            "URL do Concierge",
            value=settings.concierge_api_url,
            placeholder="https://<api-id>.execute-api.us-east-1.amazonaws.com/concierge",
            disabled=test_mode != "Concierge ponta a ponta",
        )
        flow_text = (
            "Interface → API Gateway → AgentCore → ferramentas"
            if test_mode == "Concierge ponta a ponta"
            else "Interface → Lambda retrieve_kb → base de conhecimento"
        )
        st.markdown(f'<div class="flow-note">{flow_text}</div>', unsafe_allow_html=True)
        question = st.text_area(
            "Pergunta do assinante",
            placeholder="Ex.: Como consulto meu consumo de dados?",
            height=118,
        )
        trace_id = st.text_input(
            "Trace ID (recomendado)",
            placeholder="teste-consumo-001",
            help="Use um identificador único para localizar a interação no CloudWatch.",
        )
        button_label = "Enviar ao Concierge" if test_mode == "Concierge ponta a ponta" else "Consultar a base"
        submitted = st.button(button_label, type="primary", use_container_width=True)

with guide_column:
    st.markdown('<div class="section-title">Roteiro rápido</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Uma boa rodada de demo leva menos de dois minutos.</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("**1 · Pergunta com fonte**")
        st.caption("“Como consulto meu consumo de dados?”")
        st.markdown("**2 · Pergunta fora da base**")
        st.caption("“Qual é a previsão do tempo?”")
        st.markdown("**3 · Caso sensível**")
        st.caption("Use um trace exclusivo e confira a auditoria.")
    st.info("Em falhas HTTP, o painel preserva o trace e o motivo técnico para investigação.")

if submitted:
    try:
        with st.spinner("Processando na AWS..."):
            if test_mode == "Concierge ponta a ponta":
                result = invoke_concierge(question, trace_id or None, api_url=concierge_api_url)
            else:
                result = invoke_retrieve_kb(question, trace_id or None)

        decision = result.get("decision", "nao_sei")
        if decision == "responder":
            st.success("Resposta encontrada na base oficial")
        elif decision == "escalar":
            st.warning("Caso encaminhado para atendimento humano")
        else:
            st.warning("A base não forneceu uma resposta segura")

        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Trace ID", result.get("trace_id", "-"))
        col2.metric("Decisão", decision.replace("_", " ").title())
        if test_mode == "Busca RAG direta":
            col3.metric("Latência", f"{result.get('latency_ms', '-')} ms")
        else:
            col3.metric("Fonte", result.get("source_path") or "-")

        if test_mode == "Concierge ponta a ponta":
            st.markdown("#### Resposta ao assinante")
            st.write(result.get("answer") or "Não houve resposta textual.")
            if result.get("reason"):
                st.caption(f"Motivo técnico: {result['reason']}")
            if result.get("source_path"):
                st.caption(f"Fonte: `{result['source_path']}`")
            if handoff := result.get("handoff"):
                st.markdown("#### Handoff registrado")
                st.json(handoff)
        else:
            results = result.get("results", [])
            if results:
                st.markdown("#### Fontes recuperadas")
                for index, item in enumerate(results, start=1):
                    label = f"{index}. {item.get('source_path', 'fonte sem caminho')} · score {item.get('score', 0):.4f}"
                    with st.expander(label, expanded=index == 1):
                        st.caption(f"Status: {item.get('status', '-')} · Seção: {item.get('section_title', '-')}")
                        st.markdown(item.get("text") or "Trecho indisponível.")
            else:
                st.info("Nenhuma fonte passou pelo limiar de recuperação.")

        with st.expander("Resposta técnica (JSON)"):
            st.json(result)
        st.markdown("</div>", unsafe_allow_html=True)
    except ConciergeApiError as error:
        result = error.payload
        result_trace_id = result.get("trace_id") or trace_id or "-"
        st.error(f"A API retornou HTTP {error.status_code}")
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("Trace ID para auditoria", result_trace_id)
        col2.metric("Motivo técnico", result.get("reason", "não informado"))
        st.write("A API não concluiu a solicitação. Use o trace para correlacionar logs e métricas antes de repetir o teste.")
        st.link_button("Abrir dashboard operacional", dashboard_url)
        with st.expander("Resposta técnica (JSON)", expanded=True):
            st.json(result)
        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as error:
        st.error(f"Não foi possível concluir o teste: {error}")
        st.caption("Verifique a sessão AWS SSO e as configurações do ambiente.")
