"""
Página: Meu Plano

Mostra o plano de assinatura da empresa (tenant) logada, o uso atual
em relação aos limites do plano, permite trocar de plano e assinar a
mensalidade do SaaS via Mercado Pago.
"""

import streamlit as st

from auth.login import esta_logado
from database.db import (
    init_db,
    buscar_tenant_por_id,
    contar_clientes,
    contar_usuarios,
    atualizar_plano_tenant,
    atualizar_email_contato_tenant,
    atualizar_assinatura_tenant,
)
from pagamentos.mercado_pago import criar_assinatura, consultar_assinatura
from planos import PLANOS

st.set_page_config(layout="wide")

init_db()

if not esta_logado():
    st.warning("Faça login para acessar esta página.")
    st.stop()

tenant_id = st.session_state["tenant_id"]
tenant = buscar_tenant_por_id(tenant_id)

st.title("Meu Plano")

plano_atual = PLANOS[tenant["plano"]]
total_clientes = contar_clientes(tenant_id)
total_usuarios = contar_usuarios(tenant_id)

col_plano, col_clientes, col_usuarios = st.columns(3)
col_plano.metric("Plano atual", plano_atual["nome"])
col_clientes.metric(
    "Clientes",
    f"{total_clientes}/{plano_atual['limite_clientes'] or '∞'}",
)
col_usuarios.metric(
    "Usuários",
    f"{total_usuarios}/{plano_atual['limite_usuarios'] or '∞'}",
)

st.divider()
st.subheader("Planos disponíveis")

st.table(
    [
        {
            "Plano": info["nome"],
            "Preço mensal": f"R$ {info['preco_mensal']:.2f}",
            "Limite de clientes": info["limite_clientes"] or "Ilimitado",
            "Limite de usuários": info["limite_usuarios"] or "Ilimitado",
        }
        for info in PLANOS.values()
    ]
)

chaves_planos = list(PLANOS.keys())
plano_escolhido = st.selectbox(
    "Trocar de plano",
    options=chaves_planos,
    index=chaves_planos.index(tenant["plano"]),
    format_func=lambda p: PLANOS[p]["nome"],
)

novo_limite_clientes = PLANOS[plano_escolhido]["limite_clientes"]
novo_limite_usuarios = PLANOS[plano_escolhido]["limite_usuarios"]

if st.button("Confirmar mudança de plano"):
    if plano_escolhido == tenant["plano"]:
        st.info("Esse já é o plano atual.")
    elif novo_limite_clientes is not None and total_clientes > novo_limite_clientes:
        st.error(
            f"Esse plano permite até {novo_limite_clientes} clientes, e a empresa "
            f"já tem {total_clientes}. Remova clientes antes de fazer o downgrade."
        )
    elif novo_limite_usuarios is not None and total_usuarios > novo_limite_usuarios:
        st.error(
            f"Esse plano permite até {novo_limite_usuarios} usuários, e a empresa "
            f"já tem {total_usuarios}. Remova usuários antes de fazer o downgrade."
        )
    else:
        atualizar_plano_tenant(tenant_id, plano_escolhido)
        st.success(f"Plano alterado para {PLANOS[plano_escolhido]['nome']}!")
        st.rerun()

st.divider()
st.subheader("Assinatura do plano (cobrança da empresa)")

st.write(f"Status da assinatura: **{tenant['assinatura_status']}**")

email_contato = st.text_input(
    "E-mail de contato para cobrança", value=tenant["email_contato"] or ""
)
if email_contato != (tenant["email_contato"] or ""):
    atualizar_email_contato_tenant(tenant_id, email_contato)
    st.rerun()

if st.button("Assinar / renovar plano via Mercado Pago"):
    if not email_contato:
        st.error("Informe um e-mail de contato antes de assinar.")
    else:
        resposta, erro = criar_assinatura(
            email_cliente=email_contato,
            valor_mensal=plano_atual["preco_mensal"],
            motivo=f"Assinatura plano {plano_atual['nome']} - Seguro SaaS",
            back_url="https://seguro-saas.exemplo.com/obrigado",
        )
        if erro:
            st.error(erro)
        else:
            atualizar_assinatura_tenant(tenant_id, resposta["id"], resposta.get("status", "pending"))
            st.success("Assinatura criada! Complete o pagamento pelo link abaixo.")
            st.markdown(f"[Link de pagamento]({resposta.get('init_point')})")
            st.rerun()

if tenant["mp_preapproval_id"] and st.button("🔄 Atualizar status da assinatura"):
    resposta, erro = consultar_assinatura(tenant["mp_preapproval_id"])
    if erro:
        st.error(erro)
    else:
        atualizar_assinatura_tenant(tenant_id, tenant["mp_preapproval_id"], resposta["status"])
        st.success(f"Status atualizado: {resposta['status']}")
        st.rerun()
