"""
Página: Relatórios

Mostra um panorama do negócio da empresa (tenant) logada: quantidade
de clientes, apólices por status e a receita mensal recorrente (MRR)
vinda das apólices com assinatura ativa no Mercado Pago.
"""

import pandas as pd
import streamlit as st

from auth.login import esta_logado
from database.db import init_db, listar_clientes, listar_apolices, obter_resumo_apolices

STATUS_LABELS = {
    "pending": "Pendente",
    "authorized": "Ativa",
    "paused": "Pausada",
    "cancelled": "Cancelada",
}

init_db()

if not esta_logado():
    st.warning("Faça login para acessar esta página.")
    st.stop()

tenant_id = st.session_state["tenant_id"]

st.title("Relatórios")

clientes = listar_clientes(tenant_id)
apolices = listar_apolices(tenant_id)
resumo = obter_resumo_apolices(tenant_id)

col_clientes, col_apolices, col_receita = st.columns(3)
col_clientes.metric("Clientes cadastrados", len(clientes))
col_apolices.metric("Apólices", len(apolices))
col_receita.metric(
    "Receita mensal recorrente", f"R$ {resumo['receita_mensal_recorrente']:.2f}"
)

st.subheader("Apólices por status")

if not resumo["por_status"]:
    st.info("Nenhuma apólice cadastrada ainda.")
else:
    df_status = pd.DataFrame(
        {"Quantidade": list(resumo["por_status"].values())},
        index=[STATUS_LABELS.get(s, s) for s in resumo["por_status"].keys()],
    )
    st.bar_chart(df_status)

st.subheader("Clientes sem apólice ativa")

clientes_com_apolice_ativa = {
    a["cliente_id"] for a in apolices if a["status"] == "authorized"
}
clientes_sem_apolice_ativa = [c for c in clientes if c["id"] not in clientes_com_apolice_ativa]

if not clientes:
    st.info("Nenhum cliente cadastrado ainda.")
elif not clientes_sem_apolice_ativa:
    st.success("Todos os clientes têm uma apólice ativa!")
else:
    st.dataframe(
        [
            {"Nome": c["nome"], "E-mail": c["email"]}
            for c in clientes_sem_apolice_ativa
        ],
        use_container_width=True,
        hide_index=True,
    )
