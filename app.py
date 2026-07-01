"""
app.py — Ponto de entrada do sistema.

Responsabilidades:
1. Inicializar o banco de dados (criar tabelas se não existirem).
2. Se o usuário não estiver logado, mostrar a tela de login e parar.
3. Se estiver logado, mostrar o conteúdo principal do sistema.
"""

import streamlit as st
from config import APP_NAME, APP_ICON
from database.db import init_db, criar_tenant_e_usuario_teste
from auth.login import esta_logado, tela_login, fazer_logout

st.set_page_config(page_title=APP_NAME, page_icon=APP_ICON, layout="centered")

# Roda apenas na primeira vez que o app é iniciado nesta sessão.
init_db()
criar_tenant_e_usuario_teste()

if not esta_logado():
    tela_login()
    st.stop()  # impede que o restante da página seja renderizado

# --- A partir daqui, o usuário já está autenticado ---

st.title(f"{APP_ICON} {APP_NAME}")
st.write(f"Bem-vindo(a), **{st.session_state['nome_completo']}**!")

with st.sidebar:
    st.write(f"Empresa: {st.session_state['tenant_nome']}")
    st.write(f"Logado como: {st.session_state['username']}")
    if st.button("Sair"):
        fazer_logout()
        st.rerun()
