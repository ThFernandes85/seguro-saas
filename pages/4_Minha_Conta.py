"""
Página: Minha Conta

Permite ao usuário logado trocar a própria senha.
"""

import streamlit as st

from auth.login import esta_logado, alterar_senha
from database.db import init_db

init_db()

if not esta_logado():
    st.warning("Faça login para acessar esta página.")
    st.stop()

st.title("Minha Conta")

st.write(f"Usuário: **{st.session_state['username']}**")
st.write(f"Empresa: **{st.session_state['tenant_nome']}**")

st.divider()
st.subheader("Trocar senha")

with st.form("form_trocar_senha", clear_on_submit=True):
    senha_atual = st.text_input("Senha atual", type="password")
    nova_senha = st.text_input("Nova senha", type="password", help="Mínimo de 8 caracteres.")
    confirmar_nova_senha = st.text_input("Confirmar nova senha", type="password")
    enviado = st.form_submit_button("Salvar nova senha")

if enviado:
    if nova_senha != confirmar_nova_senha:
        st.error("A confirmação não bate com a nova senha.")
    else:
        sucesso, erro = alterar_senha(
            st.session_state["usuario_id"],
            st.session_state["tenant_id"],
            senha_atual,
            nova_senha,
        )
        if sucesso:
            st.success("Senha alterada com sucesso!")
        else:
            st.error(erro)
