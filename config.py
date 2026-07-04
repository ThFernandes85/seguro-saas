# config.py
# Configurações gerais do sistema.
# Centralizar aqui evita "números mágicos" e textos espalhados pelo código.

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_NAME = "Sistema de Seguros de Vida"
APP_TAGLINE = "Protegendo o que mais importa para você e sua família"
APP_ICON = "🛡️"

# Identidade visual: escudo com um coração no centro (proteção + cuidado).
# Caminhos absolutos (baseados neste arquivo) para funcionar independente
# de qual diretório o Streamlit for iniciado.
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo.png")
FAVICON_PATH = os.path.join(BASE_DIR, "assets", "favicon.png")

# Caminho do banco de dados (vamos usar SQLite no início, por ser simples
# e não exigir instalação de servidor. Trocar para PostgreSQL no futuro
# será só mudar esse caminho de conexão dentro de database/db.py).
# Caminho absoluto (baseado neste arquivo) para não depender de qual
# diretório o Streamlit/script for iniciado.
DATABASE_PATH = os.path.join(BASE_DIR, "database", "seguro_saas.db")


SECRETS_PATH = os.path.join(BASE_DIR, ".streamlit", "secrets.toml")


def obter_segredo(nome, padrao=None):
    """
    Lê uma configuração sensível (ex: chave de API) do arquivo
    .streamlit/secrets.toml. Retorna `padrao` se o arquivo não
    existir ou a chave não estiver definida -- assim scripts fora do
    Streamlit e o app sem o token configurado não quebram.

    Só chama st.secrets se o arquivo existir: o Streamlit mostra um
    banner de erro na tela (e não só uma exceção) quando st.secrets é
    acessado sem nenhum secrets.toml presente.

    É lida sob demanda (e não no import deste módulo) porque acessar
    st.secrets antes de st.set_page_config() quebra o Streamlit.
    """
    if not os.path.exists(SECRETS_PATH):
        return padrao

    try:
        import streamlit as st

        return st.secrets.get(nome, padrao)
    except Exception:
        return padrao


# Nome da chave do Access Token do Mercado Pago (modo sandbox/teste ou
# produção). Configure em .streamlit/secrets.toml (arquivo não
# versionado): MERCADOPAGO_ACCESS_TOKEN = "TEST-...". Veja instruções
# no README, seção "Pagamentos (Mercado Pago)". Use
# `obter_segredo(MERCADOPAGO_ACCESS_TOKEN_KEY)` para ler o valor.
MERCADOPAGO_ACCESS_TOKEN_KEY = "MERCADOPAGO_ACCESS_TOKEN"

# Senha do painel de administração do SaaS (pages/6_Admin_Corretoras.py),
# usado só por você (dono do sistema) para cadastrar novas corretoras
# pelo navegador. Configure em .streamlit/secrets.toml:
# ADMIN_PANEL_SENHA = "escolha-uma-senha-forte". Sem essa chave
# configurada, a página fica bloqueada (falha fechada, por segurança).
ADMIN_PANEL_SENHA_KEY = "ADMIN_PANEL_SENHA"

# Paleta de cores da landing page institucional (navy + dourado).
COR_PRIMARIA = "#0B2545"
COR_DOURADO = "#EE9B00"
COR_ACCENT = "#134074"
COR_FUNDO_CLARO = "#EEF4F8"
COR_CREME = "#FDFBF7"

# Foto de fundo do hero da landing page. Se existir um arquivo local em
# assets/hero.jpg, ele tem prioridade; caso contrário usamos a URL de
# placeholder abaixo (imagem gerada por IA, sem pessoas reais).
# TODO: trocar por uma foto própria salvando o arquivo em assets/hero.jpg.
HERO_IMAGE_PATH = os.path.join(BASE_DIR, "assets", "hero.jpg")
HERO_IMAGE_URL_PLACEHOLDER = (
    "https://images.unsplash.com/photo-1516627145497-ae6968895b74"
    "?auto=format&fit=crop&w=1200&q=80"
)

# Contato comercial exibido na landing page (botão do WhatsApp e link de
# e-mail). Como o cadastro de novas empresas ainda é manual (veja
# scripts/criar_tenant.py), o principal call-to-action da landing é
# "falar com a gente" em vez de um cadastro automático.
# TODO: atualizar com o WhatsApp/e-mail comercial reais antes de publicar.
CONTATO_WHATSAPP = "5511999999999"
CONTATO_EMAIL = "contato@segurosaas.com.br"
