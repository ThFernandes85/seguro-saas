"""
Página: Admin - Cadastro de Corretoras

Uso exclusivo do dono do SaaS (você) para cadastrar novas empresas
(corretoras/seguradoras) e seus usuários administradores direto pelo
navegador, sem precisar rodar scripts/criar_tenant.py no terminal.

Protegida por uma senha própria (ADMIN_PANEL_SENHA em
.streamlit/secrets.toml), sem relação com o login das corretoras --
qualquer usuário de qualquer empresa NÃO tem acesso a esta página.
"""

import hmac

import streamlit as st

from config import ADMIN_PANEL_SENHA_KEY, obter_segredo
from database.db import init_db, criar_tenant, criar_usuario, listar_tenants
from planos import PLANOS, PLANO_PADRAO

st.set_page_config(layout="wide")
init_db()

st.title("Admin: Cadastro de Corretoras")


def _senha_correta(digitada, configurada):
    return hmac.compare_digest(digitada, configurada)


if not st.session_state.get("admin_autenticado"):
    senha_configurada = obter_segredo(ADMIN_PANEL_SENHA_KEY)
    if not senha_configurada:
        st.error(
            "Página desativada: defina `ADMIN_PANEL_SENHA` em "
            "`.streamlit/secrets.toml` para habilitar o painel de administração."
        )
        st.stop()

    st.info("Área restrita ao administrador do sistema.")
    with st.form("form_senha_admin"):
        senha_digitada = st.text_input("Senha de administrador", type="password")
        entrar = st.form_submit_button("Entrar")
    if entrar:
        if _senha_correta(senha_digitada, senha_configurada):
            st.session_state["admin_autenticado"] = True
            st.rerun()
        else:
            st.error("Senha incorreta.")
    st.stop()

with st.sidebar:
    if st.button("Sair do modo admin"):
        del st.session_state["admin_autenticado"]
        st.rerun()

st.warning(
    "Lembrete: enquanto o banco de dados for SQLite local, os cadastros "
    "feitos aqui são perdidos sempre que o app reinicia no Streamlit "
    "Community Cloud (veja o README, seção 'Deploy online'). Para uso "
    "com clientes reais, migre para um banco externo antes."
)

st.subheader("Cadastrar nova corretora")

with st.form("form_nova_corretora"):
    nome = st.text_input("Nome da empresa")
    slug = st.text_input("Slug (usado no login, ex: acme-seguros)")
    email_contato = st.text_input("E-mail de contato")
    plano = st.selectbox(
        "Plano",
        options=list(PLANOS.keys()),
        format_func=lambda chave: PLANOS[chave]["nome"],
        index=list(PLANOS.keys()).index(PLANO_PADRAO),
    )

    st.markdown("**Usuário administrador da empresa**")
    username = st.text_input("Usuário")
    nome_completo = st.text_input("Nome completo")
    senha = st.text_input("Senha", type="password")

    cadastrar = st.form_submit_button("Cadastrar corretora")

if cadastrar:
    if not all([nome, slug, username, nome_completo, senha]):
        st.error("Preencha nome da empresa, slug, usuário, nome completo e senha.")
    elif len(senha) < 8:
        st.error("A senha do administrador precisa ter pelo menos 8 caracteres.")
    else:
        tenant_id = criar_tenant(nome, slug, email_contato=email_contato or None, plano=plano)
        if tenant_id is None:
            st.error(f"Já existe uma empresa com o slug '{slug}'. Escolha outro.")
        else:
            usuario_id, erro = criar_usuario(tenant_id, username, senha, nome_completo)
            if erro:
                st.error(erro)
            else:
                st.success(
                    f"Empresa '{nome}' cadastrada! Login: empresa=**{slug}**, "
                    f"usuário=**{username}**."
                )

st.divider()
st.subheader("Corretoras cadastradas")

tenants = listar_tenants()
if not tenants:
    st.caption("Nenhuma corretora cadastrada ainda.")
else:
    st.dataframe(
        [
            {
                "Empresa": t["nome"],
                "Slug": t["slug"],
                "Plano": PLANOS[t["plano"]]["nome"],
                "E-mail de contato": t["email_contato"],
                "Criado em": t["criado_em"],
            }
            for t in tenants
        ],
        use_container_width=True,
        hide_index=True,
    )
