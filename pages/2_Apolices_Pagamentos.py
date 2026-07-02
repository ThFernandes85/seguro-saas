"""
Página: Apólices e Pagamentos

Permite criar uma cobrança recorrente mensal (assinatura no Mercado
Pago) para o prêmio do seguro de um cliente, e acompanhar o status
de cada apólice.
"""

import streamlit as st

from auth.login import esta_logado
from config import MERCADOPAGO_ACCESS_TOKEN_KEY, obter_segredo
from database.db import (
    init_db,
    listar_clientes,
    criar_apolice,
    listar_apolices,
    atualizar_status_apolice,
)
from pagamentos.mercado_pago import criar_assinatura, consultar_assinatura

st.set_page_config(layout="wide")

init_db()

if not esta_logado():
    st.warning("Faça login para acessar esta página.")
    st.stop()

tenant_id = st.session_state["tenant_id"]

st.title("Apólices e Pagamentos")

if not obter_segredo(MERCADOPAGO_ACCESS_TOKEN_KEY):
    st.warning(
        "Access Token do Mercado Pago não configurado. Configure a chave "
        "`MERCADOPAGO_ACCESS_TOKEN` em `.streamlit/secrets.toml` para "
        "habilitar a criação de cobranças. Veja instruções no README."
    )

clientes = listar_clientes(tenant_id)

st.subheader("Nova apólice (cobrança recorrente)")

if not clientes:
    st.info("Cadastre um cliente primeiro, na página 'Cadastro Clientes'.")
else:
    opcoes_clientes = {c["id"]: f"{c['nome']} — {c['email'] or 'sem e-mail'}" for c in clientes}

    with st.form("form_nova_apolice"):
        cliente_id_selecionado = st.selectbox(
            "Cliente",
            options=list(opcoes_clientes.keys()),
            format_func=lambda cid: opcoes_clientes[cid],
        )
        valor_mensal = st.number_input(
            "Valor do prêmio mensal (R$)", min_value=0.01, step=10.0, format="%.2f"
        )
        motivo = st.text_input("Descrição da cobrança", value="Prêmio mensal - Seguro de Vida")
        criar = st.form_submit_button("Criar cobrança recorrente")

    if criar:
        cliente = next(c for c in clientes if c["id"] == cliente_id_selecionado)

        if not cliente["email"]:
            st.error("Este cliente não tem e-mail cadastrado. Edite o cadastro dele antes de criar a cobrança.")
        else:
            resposta, erro = criar_assinatura(
                email_cliente=cliente["email"],
                valor_mensal=valor_mensal,
                motivo=motivo,
                back_url="https://seguro-saas.exemplo.com/obrigado",
            )
            if erro:
                st.error(erro)
            else:
                criar_apolice(
                    tenant_id,
                    cliente_id_selecionado,
                    valor_mensal,
                    resposta["id"],
                    resposta.get("init_point"),
                    resposta.get("status", "pending"),
                )
                st.success("Apólice criada! Envie o link abaixo para o cliente autorizar a cobrança.")
                st.markdown(f"[Link de pagamento]({resposta.get('init_point')})")
                st.rerun()

st.divider()
st.subheader("Apólices cadastradas")

apolices = listar_apolices(tenant_id)

if not apolices:
    st.info("Nenhuma apólice cadastrada ainda.")
else:
    st.dataframe(
        [
            {
                "Cliente": a["cliente_nome"],
                "Valor mensal": f"R$ {a['valor_mensal']:.2f}",
                "Status": a["status"],
                "Criada em": a["criado_em"],
            }
            for a in apolices
        ],
        use_container_width=True,
        hide_index=True,
    )

    opcoes_apolices = {
        a["id"]: f"{a['cliente_nome']} — R$ {a['valor_mensal']:.2f} ({a['status']})"
        for a in apolices
    }
    apolice_id_selecionada = st.selectbox(
        "Selecione uma apólice para atualizar o status",
        options=list(opcoes_apolices.keys()),
        format_func=lambda aid: opcoes_apolices[aid],
    )
    apolice_selecionada = next(a for a in apolices if a["id"] == apolice_id_selecionada)

    col_link, col_status = st.columns(2)

    with col_link:
        if apolice_selecionada["mp_checkout_url"]:
            st.markdown(f"[Link de pagamento]({apolice_selecionada['mp_checkout_url']})")

    with col_status:
        if st.button("🔄 Atualizar status no Mercado Pago"):
            resposta, erro = consultar_assinatura(apolice_selecionada["mp_preapproval_id"])
            if erro:
                st.error(erro)
            else:
                atualizar_status_apolice(apolice_id_selecionada, tenant_id, resposta["status"])
                st.success(f"Status atualizado: {resposta['status']}")
                st.rerun()
