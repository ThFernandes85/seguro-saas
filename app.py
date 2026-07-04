"""
app.py — Ponto de entrada do sistema.

Responsabilidades:
1. Inicializar o banco de dados (criar tabelas se não existirem).
2. Se o usuário não estiver logado, mostrar a tela de login e parar.
3. Se estiver logado, mostrar o painel principal (dashboard).
"""

import streamlit as st
from config import APP_NAME, APP_TAGLINE, FAVICON_PATH, LOGO_PATH
from database.db import (
    init_db,
    criar_tenant_e_usuario_teste,
    buscar_tenant_por_id,
    contar_clientes,
    listar_apolices,
    obter_resumo_apolices,
)
from auth.login import esta_logado, tela_login, fazer_logout
from landing import tela_landing
from planos import PLANOS

st.set_page_config(page_title=APP_NAME, page_icon=FAVICON_PATH, layout="wide")
st.logo(LOGO_PATH)

# Roda apenas na primeira vez que o app é iniciado nesta sessão.
init_db()
criar_tenant_e_usuario_teste()

if not esta_logado():
    # Visitante: mostra a landing page institucional até que ele peça
    # para entrar (botão "Entrar"); só então aparece o formulário de login.
    if st.session_state.get("mostrar_login"):
        tela_login()
    else:
        tela_landing()
    st.stop()  # impede que o restante da página seja renderizado

# --- A partir daqui, o usuário já está autenticado ---

st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background-color: #F4F6F9;
        border: 1px solid #E3E8EF;
        border-radius: 10px;
        padding: 1rem 1rem 0.6rem 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

tenant_id = st.session_state["tenant_id"]
tenant = buscar_tenant_por_id(tenant_id)
plano_atual = PLANOS[tenant["plano"]]

col_logo, col_titulo = st.columns([1, 6], vertical_alignment="center")
with col_logo:
    st.image(LOGO_PATH, width=64)
with col_titulo:
    st.title(APP_NAME)
    st.caption(APP_TAGLINE)

st.write(
    f"Bem-vindo(a) de volta, **{st.session_state['nome_completo']}** "
    f"— {st.session_state['tenant_nome']} · plano **{plano_atual['nome']}**"
)

st.divider()

total_clientes = contar_clientes(tenant_id)
apolices = listar_apolices(tenant_id)
resumo = obter_resumo_apolices(tenant_id)
apolices_ativas = resumo["por_status"].get("authorized", 0)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Clientes cadastrados", total_clientes)
col2.metric("Apólices ativas", apolices_ativas)
col3.metric("Total de apólices", len(apolices))
col4.metric("Receita mensal recorrente", f"R$ {resumo['receita_mensal_recorrente']:.2f}")

st.divider()
st.subheader("Acesso rápido")

col_a, col_b, col_c, col_d = st.columns(4)
with col_a:
    with st.container(border=True):
        st.markdown("**👥 Clientes**")
        st.caption("Cadastre e gerencie os clientes da sua carteira.")
        st.page_link("pages/1_Cadastro_Clientes.py", label="Abrir", icon="➡️")
with col_b:
    with st.container(border=True):
        st.markdown("**💳 Apólices e Pagamentos**")
        st.caption("Crie cobranças recorrentes e acompanhe assinaturas.")
        st.page_link("pages/2_Apolices_Pagamentos.py", label="Abrir", icon="➡️")
with col_c:
    with st.container(border=True):
        st.markdown("**📊 Relatórios**")
        st.caption("Panorama do negócio: clientes, apólices e receita.")
        st.page_link("pages/3_Relatorios.py", label="Abrir", icon="➡️")
with col_d:
    with st.container(border=True):
        st.markdown("**🏷️ Meu Plano**")
        st.caption("Veja seu uso atual e faça upgrade quando precisar.")
        st.page_link("pages/5_Meu_Plano.py", label="Abrir", icon="➡️")

with st.sidebar:
    st.write(f"Empresa: {st.session_state['tenant_nome']}")
    st.write(f"Logado como: {st.session_state['username']}")
    if st.button("Sair"):
        fazer_logout()
        st.rerun()
