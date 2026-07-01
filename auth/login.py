# auth/login.py
#
# Lógica de autenticação: verificar se usuário/senha estão corretos
# e controlar o estado de "logado" usando o session_state do Streamlit.

import bcrypt
import streamlit as st
from database.db import buscar_usuario, buscar_tenant_por_slug


def verificar_senha(senha_digitada, senha_hash):
    """
    Compara a senha digitada com o hash guardado no banco.
    Retorna True se bater, False caso contrário.
    """
    return bcrypt.checkpw(senha_digitada.encode("utf-8"), senha_hash.encode("utf-8"))


def autenticar(tenant_slug, username, senha):
    """
    Tenta autenticar o usuário dentro de uma empresa (tenant_slug).
    Retorna o registro do usuário se as credenciais estiverem
    corretas, ou None caso contrário.
    """
    usuario = buscar_usuario(tenant_slug, username)

    if usuario is None:
        return None

    if verificar_senha(senha, usuario["senha_hash"]):
        return usuario

    return None


def esta_logado():
    """
    Verifica se já existe um usuário logado na sessão atual.
    """
    return st.session_state.get("logado", False)


def fazer_login(usuario, tenant):
    """
    Marca o usuário como logado, guardando seus dados e os da
    empresa (tenant) na sessão.
    """
    st.session_state["logado"] = True
    st.session_state["usuario_id"] = usuario["id"]
    st.session_state["username"] = usuario["username"]
    st.session_state["nome_completo"] = usuario["nome_completo"]
    st.session_state["tenant_id"] = tenant["id"]
    st.session_state["tenant_nome"] = tenant["nome"]
    st.session_state["tenant_slug"] = tenant["slug"]


def fazer_logout():
    """
    Remove os dados de login da sessão.
    """
    chaves = [
        "logado",
        "usuario_id",
        "username",
        "nome_completo",
        "tenant_id",
        "tenant_nome",
        "tenant_slug",
    ]
    for chave in chaves:
        if chave in st.session_state:
            del st.session_state[chave]


def tela_login():
    """
    Renderiza o formulário de login. Se as credenciais estiverem
    corretas, marca o usuário como logado e recarrega a página.
    """
    st.title("🛡️ Login")

    with st.form("form_login"):
        empresa_slug = st.text_input("Empresa")
        username = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        enviado = st.form_submit_button("Entrar")

    if enviado:
        usuario = autenticar(empresa_slug, username, senha)
        if usuario is not None:
            tenant = buscar_tenant_por_slug(empresa_slug)
            fazer_login(usuario, tenant)
            st.rerun()
        else:
            st.error("Empresa, usuário ou senha inválidos.")
