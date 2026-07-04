# landing.py
#
# Landing page (institucional) do sistema, mostrada para quem ainda não
# está logado. Diferente da tela de login pura, aqui o público-alvo é o
# dono/gestor de uma corretora ou seguradora de vida que ainda não é
# cliente do SaaS -- a página vende o sistema de gestão, não seguros.

import os

import streamlit as st

from config import (
    APP_NAME,
    LOGO_PATH,
    COR_PRIMARIA,
    COR_DOURADO,
    COR_ACCENT,
    COR_FUNDO_CLARO,
    COR_CREME,
    HERO_IMAGE_PATH,
    HERO_IMAGE_URL_PLACEHOLDER,
    CONTATO_WHATSAPP,
    CONTATO_EMAIL,
)
from planos import PLANOS

_LINK_WHATSAPP = (
    f"https://wa.me/{CONTATO_WHATSAPP}"
    "?text=Ol%C3%A1!%20Quero%20conhecer%20o%20sistema%20de%20gest%C3%A3o%20de%20seguros%20de%20vida."
)
_LINK_EMAIL = f"mailto:{CONTATO_EMAIL}"

_HERO_BG_URL = HERO_IMAGE_URL_PLACEHOLDER if not os.path.exists(HERO_IMAGE_PATH) else None

_NAV_ITENS = [
    ("Home", "inicio"),
    ("Como Funciona", "como-funciona"),
    ("Planos", "planos"),
    ("Simulador", "simulador"),
    ("Novidades", "novidades"),
    ("Sobre Nós", "sobre"),
    ("Contato", "contato"),
]

_CARDS_DESTAQUE = [
    ("🗂️", "Organização", "Chega de planilhas soltas: clientes e apólices centralizados e sempre à mão."),
    ("⏱️", "Tempo de Volta", "Automatize cobranças e relatórios para focar em vender, não em burocracia."),
    ("📈", "Crescimento Sustentável", "Planos que acompanham sua corretora, do primeiro cliente à carteira grande."),
]

_RECURSOS = [
    ("👥", "Cadastro de Clientes", "CRUD completo com validação de CPF para organizar toda a sua carteira em um só lugar."),
    ("💳", "Cobrança Recorrente", "Assinaturas mensais das apólices via Mercado Pago, com status atualizado por você."),
    ("📊", "Relatórios do Negócio", "Receita recorrente, apólices por status e oportunidades de venda em tempo real."),
    ("🔒", "Multiempresa e Segurança", "Cada corretora tem seus dados isolados, com proteção contra força bruta no login."),
]

_PASSOS = [
    ("1", "Fale com a gente", "Conte um pouco da sua corretora e o tamanho atual da sua carteira de clientes."),
    ("2", "Configuramos seu acesso", "Criamos a conta da sua empresa no sistema e o primeiro usuário administrador."),
    ("3", "Comece a usar", "Cadastre clientes, crie cobranças recorrentes e acompanhe tudo pelo painel."),
]

_NOVIDADES = [
    "Dashboard inicial com KPIs e acesso rápido às principais telas.",
    "Modelo de planos (Starter, Pro, Business) com limites de uso por empresa.",
    "Proteção contra força bruta e troca de senha pelo próprio usuário.",
    "Cobrança recorrente das apólices integrada ao Mercado Pago.",
    "Página de relatórios com panorama completo do negócio.",
    "Cadastro de clientes (CRUD) com validação de CPF.",
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


def _iniciais(nome):
    partes = nome.split()
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[-1][0]).upper()


def _recomendar_plano(clientes, usuarios):
    for chave in ("starter", "pro", "business"):
        plano = PLANOS[chave]
        cabe_clientes = plano["limite_clientes"] is None or clientes <= plano["limite_clientes"]
        cabe_usuarios = plano["limite_usuarios"] is None or usuarios <= plano["limite_usuarios"]
        if cabe_clientes and cabe_usuarios:
            return plano["nome"]
    return PLANOS["business"]["nome"]


def _injetar_estilo():
    hero_bg = (
        f"url('{_HERO_BG_URL}')" if _HERO_BG_URL
        else f"linear-gradient(135deg, {COR_PRIMARIA}, {COR_ACCENT})"
    )
    st.markdown(
        f"""
        <style>
        .ls-nav {{
            display: flex;
            justify-content: center;
            gap: 1.6rem;
            flex-wrap: wrap;
            font-size: 0.92rem;
            font-weight: 500;
        }}
        .ls-nav a {{
            color: #4B5563;
            text-decoration: none;
        }}
        .ls-nav a:hover {{
            color: {COR_PRIMARIA};
        }}
        .ls-hero {{
            background-image: linear-gradient(rgba(11, 37, 69, 0.82), rgba(11, 37, 69, 0.82)), {hero_bg};
            background-size: cover;
            background-position: center;
            border-radius: 20px;
            padding: 4rem 2.5rem 5.5rem 2.5rem;
            margin-top: 0.5rem;
            text-align: center;
        }}
        .ls-hero h1 {{
            color: #FFFFFF;
            font-size: 2.6rem;
            line-height: 1.15;
            margin-bottom: 0.8rem;
        }}
        .ls-hero p {{
            color: #E5E9F0;
            font-size: 1.1rem;
            max-width: 42rem;
            margin: 0 auto 1.6rem auto;
        }}
        .ls-cta-dourado {{
            display: inline-block;
            background-color: {COR_DOURADO};
            color: #FFFFFF !important;
            font-weight: 700;
            text-decoration: none;
            padding: 0.9rem 2rem;
            border-radius: 10px;
            margin: 0 0.5rem 0.5rem 0.5rem;
            box-shadow: 0 8px 20px rgba(238, 155, 0, 0.35);
        }}
        .ls-cta-outline {{
            display: inline-block;
            border: 2px solid #FFFFFF;
            color: #FFFFFF !important;
            font-weight: 600;
            text-decoration: none;
            padding: 0.85rem 1.9rem;
            border-radius: 10px;
            margin: 0 0.5rem 0.5rem 0.5rem;
        }}
        .ls-cards-flutuantes {{
            margin-top: -3.2rem;
            margin-bottom: 1.5rem;
        }}
        .ls-card-destaque {{
            background-color: {COR_ACCENT};
            color: #FFFFFF;
            border-radius: 16px;
            padding: 1.3rem 1.5rem;
            height: 100%;
            box-shadow: 0 12px 24px rgba(11, 37, 69, 0.18);
        }}
        .ls-card-destaque h4 {{
            margin: 0.4rem 0 0.3rem 0;
        }}
        .ls-card-destaque p {{
            color: #D7DEE9;
            font-size: 0.88rem;
            margin: 0;
        }}
        .ls-icone-circulo {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 52px;
            height: 52px;
            border-radius: 50%;
            background-color: {COR_FUNDO_CLARO};
            font-size: 1.5rem;
            margin-bottom: 0.6rem;
        }}
        .ls-secao-titulo {{
            text-align: center;
            color: {COR_PRIMARIA};
            margin-bottom: 0.4rem;
        }}
        .ls-secao-subtitulo {{
            text-align: center;
            color: #6B7280;
            margin-bottom: 2rem;
        }}
        .ls-passo-numero {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: {COR_DOURADO};
            color: #FFFFFF;
            font-weight: 700;
            margin-bottom: 0.6rem;
        }}
        .ls-avatar-iniciais {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background-color: {COR_ACCENT};
            color: #FFFFFF;
            font-weight: 700;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}
        .ls-depoimento {{
            font-style: italic;
            color: #2B2F38;
        }}
        details.ls-faq-item {{
            background-color: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            padding: 0.9rem 1.2rem;
            margin-bottom: 0.7rem;
        }}
        details.ls-faq-item summary {{
            font-weight: 600;
            color: {COR_PRIMARIA};
            cursor: pointer;
            list-style: none;
        }}
        details.ls-faq-item summary::-webkit-details-marker {{
            display: none;
        }}
        details.ls-faq-item summary::after {{
            content: "▾";
            float: right;
            color: {COR_DOURADO};
        }}
        details.ls-faq-item[open] summary::after {{
            content: "▴";
        }}
        details.ls-faq-item p {{
            color: #4B5563;
            margin: 0.7rem 0 0 0;
            font-size: 0.94rem;
        }}
        .ls-simulador {{
            background-color: {COR_FUNDO_CLARO};
            border: 1px solid #DCE3EC;
            border-radius: 20px;
            padding: 1.8rem 2rem;
        }}
        .ls-rodape {{
            background-color: {COR_PRIMARIA};
            color: #B9C2D0;
            border-radius: 16px;
            padding: 2.2rem 2.2rem 1.2rem 2.2rem;
            margin-top: 2rem;
            font-size: 0.88rem;
        }}
        .ls-rodape h4 {{
            color: #FFFFFF;
            font-size: 0.95rem;
            margin-bottom: 0.7rem;
        }}
        .ls-rodape a {{
            color: #B9C2D0;
            text-decoration: none;
            display: block;
            margin-bottom: 0.4rem;
        }}
        .ls-rodape a:hover {{
            color: #FFFFFF;
        }}
        .ls-rodape-copyright {{
            border-top: 1px solid #2A3F5E;
            margin-top: 1.4rem;
            padding-top: 1rem;
            text-align: center;
            font-size: 0.8rem;
            color: #8695AB;
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
        div[data-testid="stButton"] button {{
            background-color: {COR_DOURADO};
            color: #FFFFFF;
            font-weight: 700;
            border: none;
            border-radius: 10px;
        }}
        div[data-testid="stButton"] button:hover {{
            background-color: {COR_DOURADO};
            opacity: 0.9;
            color: #FFFFFF;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _ancora(id_secao):
    st.markdown(f'<div id="{id_secao}"></div>', unsafe_allow_html=True)


def _secao_nav():
    _ancora("inicio")
    col_logo, col_nav, col_entrar = st.columns([1.6, 5, 1.1], vertical_alignment="center")
    with col_logo:
        col_img, col_txt = st.columns([1, 3], vertical_alignment="center")
        with col_img:
            st.image(LOGO_PATH, width=40)
        with col_txt:
            st.markdown(f"**{APP_NAME}**")
    with col_nav:
        links = " &nbsp;·&nbsp; ".join(f'<a href="#{id_}">{label}</a>' for label, id_ in _NAV_ITENS)
        st.markdown(f'<div class="ls-nav">{links}</div>', unsafe_allow_html=True)
    with col_entrar:
        if st.button("Área do Cliente", use_container_width=True):
            st.session_state["mostrar_login"] = True
            st.rerun()
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)


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
            <a class="ls-cta-dourado" href="{_LINK_WHATSAPP}" target="_blank">💬 Falar com a gente</a>
            <a class="ls-cta-outline" href="#como-funciona">Saiba mais</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _secao_cards_flutuantes():
    st.markdown('<div class="ls-cards-flutuantes">', unsafe_allow_html=True)
    cols = st.columns(3)
    for col, (icone, titulo, texto) in zip(cols, _CARDS_DESTAQUE):
        with col:
            st.markdown(
                f"""
                <div class="ls-card-destaque">
                    <div style="font-size:1.6rem;">{icone}</div>
                    <h4>{titulo}</h4>
                    <p>{texto}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)


def _secao_recursos():
    st.markdown("<h2 class='ls-secao-titulo'>Feito para o dia a dia da sua corretora</h2>", unsafe_allow_html=True)
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (icone, titulo, texto) in zip(cols, _RECURSOS):
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="ls-icone-circulo">{icone}</div>', unsafe_allow_html=True)
                st.markdown(f"**{titulo}**")
                st.caption(texto)
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)


def _secao_como_funciona():
    _ancora("como-funciona")
    st.markdown("<h2 class='ls-secao-titulo'>Como funciona</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p class='ls-secao-subtitulo'>Do primeiro contato ao seu painel funcionando, em 3 passos.</p>",
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    for col, (numero, titulo, texto) in zip(cols, _PASSOS):
        with col:
            st.markdown(f'<div class="ls-passo-numero">{numero}</div>', unsafe_allow_html=True)
            st.markdown(f"**{titulo}**")
            st.caption(texto)
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)


def _secao_planos():
    _ancora("planos")
    st.markdown("<h2 class='ls-secao-titulo'>Planos</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p class='ls-secao-subtitulo'>Cada plano acompanha o tamanho da sua carteira. "
        "Fale com a gente para saber os valores.</p>",
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    for col, chave in zip(cols, ("starter", "pro", "business")):
        plano = PLANOS[chave]
        clientes = "Ilimitados" if plano["limite_clientes"] is None else f"até {plano['limite_clientes']}"
        usuarios = "Ilimitados" if plano["limite_usuarios"] is None else f"até {plano['limite_usuarios']}"
        with col:
            with st.container(border=True):
                st.markdown(f"**{plano['nome']}**")
                st.caption(f"Clientes: {clientes}")
                st.caption(f"Usuários: {usuarios}")
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)


def _secao_simulador():
    _ancora("simulador")
    st.markdown("<h2 class='ls-secao-titulo'>Simulador de Plano Ideal</h2>", unsafe_allow_html=True)
    col_esq, col_centro, col_dir = st.columns([1, 2, 1])
    with col_centro:
        st.markdown('<div class="ls-simulador">', unsafe_allow_html=True)
        st.caption("Rápido, sem compromisso. Descubra qual plano combina com sua corretora hoje.")
        clientes = st.number_input("Quantos clientes ativos você tem hoje?", min_value=0, step=1, value=0)
        usuarios = st.number_input("Quantas pessoas da equipe vão usar o sistema?", min_value=1, step=1, value=1)
        if st.button("Ver plano recomendado", use_container_width=True):
            recomendado = _recomendar_plano(int(clientes), int(usuarios))
            st.success(f"Plano recomendado: **{recomendado}**. Fale com a gente para confirmar valores.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)


def _secao_novidades():
    _ancora("novidades")
    st.markdown("<h2 class='ls-secao-titulo'>Novidades</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p class='ls-secao-subtitulo'>O sistema está em evolução constante. Últimas entregas:</p>",
        unsafe_allow_html=True,
    )
    for item in _NOVIDADES:
        st.markdown(f"- {item}")
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)


def _secao_depoimentos():
    st.markdown("<h2 class='ls-secao-titulo'>Quem usa, recomenda</h2>", unsafe_allow_html=True)
    st.markdown("<div style='height: 0.5rem'></div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for col, (frase, nome, cargo) in zip(cols, _DEPOIMENTOS):
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="ls-avatar-iniciais">{_iniciais(nome)}</div>', unsafe_allow_html=True)
                st.markdown(f'<p class="ls-depoimento">"{frase}"</p>', unsafe_allow_html=True)
                st.markdown(f"**{nome}**")
                st.caption(cargo)
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)


def _secao_sobre():
    _ancora("sobre")
    st.markdown("<h2 class='ls-secao-titulo'>Sobre Nós</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; max-width: 42rem; margin: 0 auto; color: #4B5563;'>"
        "Sistema criado para simplificar o dia a dia de corretoras e seguradoras de vida, "
        "reunindo cadastro de clientes, cobrança recorrente e relatórios em um só lugar -- "
        "sem depender de planilhas soltas."
        "</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height: 1.5rem'></div>", unsafe_allow_html=True)


def _secao_faq():
    _ancora("faq")
    st.markdown("<h2 class='ls-secao-titulo'>Perguntas Frequentes</h2>", unsafe_allow_html=True)
    html = "".join(
        f'<details class="ls-faq-item"><summary>{pergunta}</summary><p>{resposta}</p></details>'
        for pergunta, resposta in _FAQ
    )
    st.markdown(html, unsafe_allow_html=True)
    st.markdown("<div style='height: 1rem'></div>", unsafe_allow_html=True)


def _secao_rodape():
    _ancora("contato")
    st.markdown(
        f"""
        <div class="ls-rodape">
            <div style="display:flex; flex-wrap:wrap; gap:2rem; justify-content:space-between;">
                <div style="flex:1.3; min-width:220px;">
                    <div style="color:#FFFFFF; font-weight:700; font-size:1.1rem;">{APP_NAME}</div>
                    <p style="margin-top:0.6rem;">Sistema de gestão para corretoras e seguradoras de vida.</p>
                </div>
                <div style="flex:1; min-width:160px;">
                    <h4>Links rápidos</h4>
                    <a href="#planos">Planos</a>
                    <a href="#simulador">Simulador</a>
                    <a href="#sobre">Sobre Nós</a>
                </div>
                <div style="flex:1; min-width:160px;">
                    <h4>Contato</h4>
                    <a href="{_LINK_EMAIL}">{CONTATO_EMAIL}</a>
                    <a href="{_LINK_WHATSAPP}" target="_blank">💬 WhatsApp</a>
                </div>
            </div>
            <div class="ls-rodape-copyright">&copy; {APP_NAME} -- Todos os direitos reservados.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _botao_whatsapp_flutuante():
    st.markdown(
        f"""
        <a class="ls-whatsapp-float" href="{_LINK_WHATSAPP}" target="_blank" title="Falar no WhatsApp">💬</a>
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
    _secao_cards_flutuantes()
    _secao_recursos()
    _secao_como_funciona()
    _secao_planos()
    _secao_simulador()
    _secao_novidades()
    _secao_depoimentos()
    _secao_sobre()
    _secao_faq()
    _secao_rodape()
    _botao_whatsapp_flutuante()
