# auth/login.py
#
# Lógica de autenticação: verificar se usuário/senha estão corretos
# e controlar o estado de "logado" usando o session_state do Streamlit.

import datetime
import math

import bcrypt
import streamlit as st
from config import APP_NAME, APP_TAGLINE, LOGO_PATH
from database.db import (
    buscar_usuario,
    buscar_usuario_por_id,
    buscar_tenant_por_slug,
    incrementar_tentativas_falhas,
    bloquear_usuario_ate,
    resetar_tentativas_falhas,
    salvar_nova_senha,
)

# Proteção contra força bruta: depois de LIMITE_TENTATIVAS senhas
# erradas seguidas, a conta fica bloqueada por DURACAO_BLOQUEIO_MINUTOS.
LIMITE_TENTATIVAS = 5
DURACAO_BLOQUEIO_MINUTOS = 15


def verificar_senha(senha_digitada, senha_hash):
    """
    Compara a senha digitada com o hash guardado no banco.
    Retorna True se bater, False caso contrário.
    """
    return bcrypt.checkpw(senha_digitada.encode("utf-8"), senha_hash.encode("utf-8"))


def calcular_bloqueio(tentativas_falhas):
    """
    Decide se a conta deve ser bloqueada, dado o número total de
    tentativas de login falhas acumuladas. Retorna o horário (UTC,
    datetime) até quando a conta deve ficar bloqueada, ou None se
    ainda não atingiu o limite.
    """
    if tentativas_falhas < LIMITE_TENTATIVAS:
        return None
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=DURACAO_BLOQUEIO_MINUTOS)


def esta_bloqueado(bloqueado_ate, agora=None):
    """
    Verifica se um horário de bloqueio (string ISO 8601 em UTC, ou
    None/vazio) ainda está em vigor.
    """
    if not bloqueado_ate:
        return False
    agora = agora or datetime.datetime.now(datetime.timezone.utc)
    return datetime.datetime.fromisoformat(bloqueado_ate) > agora


def _minutos_restantes(bloqueado_ate):
    delta = datetime.datetime.fromisoformat(bloqueado_ate) - datetime.datetime.now(datetime.timezone.utc)
    return max(1, math.ceil(delta.total_seconds() / 60))


def autenticar(tenant_slug, username, senha):
    """
    Tenta autenticar o usuário dentro de uma empresa (tenant_slug),
    aplicando a proteção contra força bruta.

    Retorna uma tupla (usuario, erro):
    - Em caso de sucesso: (registro do usuário, None).
    - Em caso de falha: (None, mensagem de erro para mostrar na tela).
    """
    usuario = buscar_usuario(tenant_slug, username)

    if usuario is None:
        return None, "Empresa, usuário ou senha inválidos."

    if esta_bloqueado(usuario["bloqueado_ate"]):
        minutos = _minutos_restantes(usuario["bloqueado_ate"])
        return None, f"Conta bloqueada temporariamente. Tente novamente em {minutos} min."

    if not verificar_senha(senha, usuario["senha_hash"]):
        tentativas = incrementar_tentativas_falhas(usuario["id"])
        bloqueio_ate = calcular_bloqueio(tentativas)
        if bloqueio_ate is not None:
            bloquear_usuario_ate(usuario["id"], bloqueio_ate.isoformat())
            return None, (
                f"Muitas tentativas erradas. Conta bloqueada por "
                f"{DURACAO_BLOQUEIO_MINUTOS} minutos."
            )
        return None, "Empresa, usuário ou senha inválidos."

    resetar_tentativas_falhas(usuario["id"])
    return usuario, None


def alterar_senha(usuario_id, tenant_id, senha_atual, nova_senha):
    """
    Troca a senha do usuário logado, após confirmar a senha atual.
    Retorna uma tupla (sucesso, erro): (True, None) ou (False, mensagem).
    """
    usuario = buscar_usuario_por_id(usuario_id, tenant_id)
    if usuario is None:
        return False, "Usuário não encontrado."

    if not verificar_senha(senha_atual, usuario["senha_hash"]):
        return False, "Senha atual incorreta."

    if len(nova_senha) < 8:
        return False, "A nova senha precisa ter pelo menos 8 caracteres."

    nova_senha_hash = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    salvar_nova_senha(usuario_id, nova_senha_hash)
    return True, None


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
    col_esq, col_centro, col_dir = st.columns([1, 2, 1])
    with col_centro:
        st.image(LOGO_PATH, width=120)
        st.markdown(f"<h2 style='text-align: center;'>{APP_NAME}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: gray;'>{APP_TAGLINE}</p>", unsafe_allow_html=True)

    with st.form("form_login"):
        empresa_slug = st.text_input("Empresa")
        username = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        enviado = st.form_submit_button("Entrar")

    if enviado:
        usuario, erro = autenticar(empresa_slug, username, senha)
        if usuario is not None:
            tenant = buscar_tenant_por_slug(empresa_slug)
            fazer_login(usuario, tenant)
            st.rerun()
        else:
            st.error(erro)
