"""
Página: Cadastro de Clientes

O Streamlit transforma automaticamente cada arquivo dentro da pasta
"pages/" em um item de menu lateral. O número no início do nome do
arquivo ("1_") define a ordem de exibição no menu.

Permite cadastrar, listar, editar e excluir os clientes da empresa
(tenant) do usuário logado.
"""

import datetime

import streamlit as st

from auth.login import esta_logado
from database.db import (
    init_db,
    buscar_tenant_por_id,
    contar_clientes,
    criar_cliente,
    listar_clientes,
    atualizar_cliente,
    excluir_cliente,
)
from planos import PLANOS
from utils.helpers import apenas_digitos, validar_cpf, formatar_cpf

init_db()

if not esta_logado():
    st.warning("Faça login para acessar esta página.")
    st.stop()

tenant_id = st.session_state["tenant_id"]
tenant = buscar_tenant_por_id(tenant_id)
limite_clientes = PLANOS[tenant["plano"]]["limite_clientes"]

st.title("Cadastro de Clientes")

if limite_clientes is not None:
    st.caption(f"Plano {PLANOS[tenant['plano']]['nome']}: {contar_clientes(tenant_id)}/{limite_clientes} clientes usados.")

with st.expander("➕ Novo cliente", expanded=True):
    with st.form("form_novo_cliente", clear_on_submit=True):
        nome = st.text_input("Nome completo")
        cpf = st.text_input("CPF", placeholder="000.000.000-00")
        data_nascimento = st.date_input(
            "Data de nascimento",
            value=None,
            min_value=datetime.date(1900, 1, 1),
            max_value=datetime.date.today(),
        )
        telefone = st.text_input("Telefone")
        email = st.text_input("E-mail")
        enviado = st.form_submit_button("Cadastrar")

    if enviado:
        cpf_digitos = apenas_digitos(cpf)

        if not nome.strip():
            st.error("Informe o nome do cliente.")
        elif not validar_cpf(cpf_digitos):
            st.error("CPF inválido.")
        elif data_nascimento is None:
            st.error("Informe a data de nascimento.")
        else:
            cliente_id, erro = criar_cliente(
                tenant_id,
                nome.strip(),
                cpf_digitos,
                data_nascimento.isoformat(),
                telefone.strip(),
                email.strip(),
            )
            if erro:
                st.error(erro)
            else:
                st.success(f"Cliente '{nome}' cadastrado com sucesso!")
                st.rerun()

st.divider()
st.subheader("Clientes cadastrados")

clientes = listar_clientes(tenant_id)

if not clientes:
    st.info("Nenhum cliente cadastrado ainda.")
else:
    st.dataframe(
        [
            {
                "Nome": c["nome"],
                "CPF": formatar_cpf(c["cpf"]),
                "Nascimento": c["data_nascimento"],
                "Telefone": c["telefone"],
                "E-mail": c["email"],
            }
            for c in clientes
        ],
        use_container_width=True,
        hide_index=True,
    )

    opcoes = {c["id"]: f"{c['nome']} — {formatar_cpf(c['cpf'])}" for c in clientes}
    cliente_id_selecionado = st.selectbox(
        "Selecione um cliente para editar ou excluir",
        options=list(opcoes.keys()),
        format_func=lambda cid: opcoes[cid],
    )
    cliente_selecionado = next(c for c in clientes if c["id"] == cliente_id_selecionado)

    with st.expander("✏️ Editar / excluir cliente"):
        with st.form("form_editar_cliente"):
            nome_edit = st.text_input("Nome completo", value=cliente_selecionado["nome"])
            cpf_edit = st.text_input(
                "CPF", value=formatar_cpf(cliente_selecionado["cpf"])
            )
            data_nascimento_edit = st.date_input(
                "Data de nascimento",
                value=datetime.date.fromisoformat(cliente_selecionado["data_nascimento"]),
                min_value=datetime.date(1900, 1, 1),
                max_value=datetime.date.today(),
            )
            telefone_edit = st.text_input(
                "Telefone", value=cliente_selecionado["telefone"] or ""
            )
            email_edit = st.text_input("E-mail", value=cliente_selecionado["email"] or "")

            col_salvar, col_excluir = st.columns(2)
            salvar = col_salvar.form_submit_button("Salvar alterações")
            excluir = col_excluir.form_submit_button("Excluir cliente")

        if salvar:
            cpf_edit_digitos = apenas_digitos(cpf_edit)

            if not nome_edit.strip():
                st.error("Informe o nome do cliente.")
            elif not validar_cpf(cpf_edit_digitos):
                st.error("CPF inválido.")
            else:
                atualizado = atualizar_cliente(
                    cliente_id_selecionado,
                    tenant_id,
                    nome_edit.strip(),
                    cpf_edit_digitos,
                    data_nascimento_edit.isoformat(),
                    telefone_edit.strip(),
                    email_edit.strip(),
                )
                if not atualizado:
                    st.error("Já existe outro cliente com esse CPF nesta empresa.")
                else:
                    st.success("Cliente atualizado com sucesso!")
                    st.rerun()

        if excluir:
            excluir_cliente(cliente_id_selecionado, tenant_id)
            st.success("Cliente excluído.")
            st.rerun()
