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
DATABASE_PATH = os.path.join(BASE_DIR, "database", "seguro_saas.db")
