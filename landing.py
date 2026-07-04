# landing.py
#
# Landing page (institucional) do sistema, mostrada para quem ainda não
# está logado. Diferente da tela de login pura, aqui o público-alvo é o
# dono/gestor de uma corretora ou seguradora de vida que ainda não é
# cliente do SaaS -- a página vende o sistema de gestão, não seguros.

import streamlit as st

from config import (
    APP_NAME,
    LOGO_PATH,
    COR_DOURADO,
    CONTATO_WHATSAPP,
    CONTATO_EMAIL,
)

_LINK_WHATSAPP = (
    f"https://wa.me/{CONTATO_WHATSAPP}"
    "?text=Ol%C3%A1!%20Quero%20conhecer%20o%20sistema%20de%20gest%C3%A3o%20de%20seguros%20de%20vida."
)
_LINK_EMAIL = f"mailto:{CONTATO_EMAIL}"

_RECURSOS = [
    ("👥", "Cadastro de Clientes", "CRUD completo com validação de CPF para organizar toda a sua carteira em um só lugar."),
    ("💳", "Cobrança Recorrente", "Assinaturas mensais das apólices via Mercado Pago, com status atualizado por você."),
    ("📊", "Relatórios do Negócio", "Receita recorrente, apólices por status e oportunidades de venda em tempo real."),
    ("🔒", "Multiempresa e Segurança", "Cada corretora tem seus dados isolados, com proteção contra força bruta no login."),
]

_BENEFICIOS = [
    ("🗂️", "Organização", "Chega de planilhas soltas: clientes e apólices centralizados e sempre à mão."),
    ("⏱️", "Tempo de Volta", "Automatize cobranças e relatórios para focar em vender, não em burocracia."),
    ("📈", "Crescimento Sustentável", "Planos que acompanham sua corretora, do primeiro cliente à carteira grande."),
]

_DEPOIMENTOS = [
    (
        "Trocamos as planilhas por esse sistema e conseguimos ver, em segundos, "
        "quais clientes ainda não têm apólice ativa. Fez diferença nas vendas.",
        "Marina Alves",
        "Sócia, Alves Corretora de Seguros",
    ),
    (
        "A cobrança recorrente automática foi o que mais economizou tempo do "
        "nosso time. Antes cobrávamos cliente por cliente manualmente.",
        "Roberto Nascimento",
        "Diretor, RN Seguros de Vida",
    ),
    (
        "Como temos várias unidades, gostamos de saber que os dados de cada "
        "uma ficam separados e protegidos dentro do mesmo sistema.",
        "Camila Duarte",
        "Gerente Operacional, Duarte Seguradora",
    ),
]

_FAQ = [
    (
        "Preciso de conhecimento técnico para usar o sistema?",
        "Não. O sistema roda no navegador, com telas simples de cadastro, "
        "cobrança e relatórios -- não é necessário instalar nada nem saber programar.",
    ),
    (
        "Os dados da minha corretora ficam separados dos de outras empresas?",
        "Sim. O sistema é multiempresa (multi-tenant): cada corretora tem seu "
        "próprio espaço, com login por empresa + usuário, e não há acesso "
        "cruzado entre os dados de empresas diferentes.",
    ),
    (
        "Como funciona a cobrança do meu plano?",
        "Cada plano (Starter, Pro ou Business) tem um limite de clientes e "
        "usuários. Fale com a gente para saber qual plano combina com o "
        "tamanho atual da sua carteira.",
    ),
    (
        "Como faço para começar a usar?",
        "Ainda não temos cadastro automático: fale com a gente pelo WhatsApp "
        "ou e-mail e nós configuramos o acesso da sua empresa.",
    ),
]


def _injetar_estilo():
    st.markdown(
        f"""
        <style>
        .ls-hero {{
            background-color: #13294B;
            border-radius: 16px;
            padding: 3rem 2.5rem;
            margin-bottom: 1.5rem;
        }}
        .ls-hero h1 {{
            color: #FFFFFF;
            font-size: 2.4rem;
            line-height: 1.15;
            margin-bottom: 0.8rem;
        }}
        .ls-hero p {{
            color: #D7DEE9;
            font-size: 1.05rem;
            max-width: 40rem;
        }}
        .ls-cta-dourado {{
            display: inline-block;
            background-color: {COR_DOURADO};
            color: #13294B !important;
            font-weight: 700;
            text-decoration: none;
            padding: 0.7rem 1.6rem;
            border-radius: 8px;
            margin-top: 0.8rem;
            margin-right: 0.8rem;
        }}
        .ls-cta-secundaria {{
            color: #FFFFFF !important;
            text-decoration: underline;
            font-weight: 500;
        }}
        .ls-beneficio {{
            background-color: #13294B;
            color: #FFFFFF;
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
            height: 100%;
        }}
        .ls-beneficio h4 {{
            margin: 0.3rem 0 0.3rem 0;
        }}
        .ls-beneficio p {{
            color: #D7DEE9;
            font-size: 0.9rem;
            margin: 0;
        }}
        .ls-depoimento {{
            font-style: italic;
            color: #2B2F38;
        }}
        .ls-whatsapp-float {{
            position: fixed;
            bottom: 24px;
            right: 24px;
            background-color: #25D366;
            color: white !important;
            border-radius: 50%;
            width: 56px;
            height: 56px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.6rem;
            text-decoration: none;
            box-shadow: 0 4px 10px rgba(0,0,0,0.25);
            z-index: 999;
        }}
        .ls-rodape {{
            background-color: #13294B;
            color: #D7DEE9;
            border-radius: 12px;
            padding: 1.8rem 2rem;
            margin-top: 2rem;
            font-size: 0.85rem;
        }}
        .ls-rodape a {{
            color: #D7DEE9;
            text-decoration: none;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _secao_nav():
    col_logo, col_titulo, col_espaco, col_entrar = st.columns([0.6, 2, 4, 1], vertical_alignment="center")
    with col_logo:
        st.image(LOGO_PATH, width=48)
    with col_titulo:
        st.markdown(f"**{APP_NAME}**")
    with col_entrar:
        if st.button("Entrar", use_container_width=True):
            st.session_state["mostrar_login"] = True
            st.rerun()
    st.divider()


def _secao_hero():
    st.markdown(
        f"""
        <div class="ls-hero">
            <h1>O sistema de gestão feito para corretoras e seguradoras de vida.</h1>
            <p>
                Cadastre seus clientes, controle apólices e cobranças recorrentes
                e acompanhe a saúde do seu negócio em um só lugar -- para que
                você foque em vender seguro de vida, não em planilhas.
            </p>
            <a class="ls-cta-dourado" href="{_LINK_WHATSAPP}" target="_blank">
                💬 Falar com a gente
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _secao_beneficios():
    cols = st.columns(3)
    for col, (icone, titulo, texto) in zip(cols, _BENEFICIOS):
        with col:
            st.markdown(
                f"""
                <div class="ls-beneficio">
                    <div style="font-size:1.6rem;">{icone}</div>
                    <h4>{titulo}</h4>
                    <p>{texto}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)


def _secao_recursos():
    st.subheader("Feito para o dia a dia da sua corretora")
    cols = st.columns(4)
    for col, (icone, titulo, texto) in zip(cols, _RECURSOS):
        with col:
            with st.container(border=True):
                st.markdown(f"### {icone}")
                st.markdown(f"**{titulo}**")
                st.caption(texto)
    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)


def _secao_depoimentos():
    st.subheader("Quem usa, recomenda")
    cols = st.columns(3)
    for col, (frase, nome, cargo) in zip(cols, _DEPOIMENTOS):
        with col:
            with st.container(border=True):
                st.markdown(f'<p class="ls-depoimento">"{frase}"</p>', unsafe_allow_html=True)
                st.markdown(f"**{nome}**")
                st.caption(cargo)
    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)


def _secao_faq():
    st.subheader("Perguntas frequentes")
    for pergunta, resposta in _FAQ:
        with st.expander(pergunta):
            st.write(resposta)


def _secao_rodape():
    st.markdown(
        f"""
        <div class="ls-rodape">
            <b>{APP_NAME}</b> -- sistema de gestão para corretoras e seguradoras de vida.<br>
            <a href="{_LINK_EMAIL}">{CONTATO_EMAIL}</a> ·
            <a href="{_LINK_WHATSAPP}" target="_blank">WhatsApp</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _botao_whatsapp_flutuante():
    st.markdown(
        f"""
        <a class="ls-whatsapp-float" href="{_LINK_WHATSAPP}" target="_blank" title="Falar no WhatsApp">
            💬
        </a>
        """,
        unsafe_allow_html=True,
    )


def tela_landing():
    """
    Renderiza a landing page institucional, mostrada para visitantes que
    ainda não estão logados e ainda não pediram para ver a tela de login.
    """
    _injetar_estilo()
    _secao_nav()
    _secao_hero()
    _secao_beneficios()
    _secao_recursos()
    _secao_depoimentos()
    _secao_faq()
    _secao_rodape()
    _botao_whatsapp_flutuante()
