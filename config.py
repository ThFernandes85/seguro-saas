# config.py
# Configurações gerais do sistema.
# Centralizar aqui evita "números mágicos" e textos espalhados pelo código.

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_NAME = "Sistema de Seguros de Vida"
APP_ICON = "🛡️"

# Caminho do banco de dados (vamos usar SQLite no início, por ser simples
# e não exigir instalação de servidor. Trocar para PostgreSQL no futuro
# será só mudar esse caminho de conexão dentro de database/db.py).
# Caminho absoluto (baseado neste arquivo) para não depender de qual
# diretório o Streamlit/script for iniciado.
DATABASE_PATH = os.path.join(BASE_DIR, "database", "seguro_saas.db")
