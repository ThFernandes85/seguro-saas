# config.py
# Configurações gerais do sistema.
# Centralizar aqui evita "números mágicos" e textos espalhados pelo código.

APP_NAME = "Sistema de Seguros de Vida"
APP_ICON = "🛡️"

# Caminho do banco de dados (vamos usar SQLite no início, por ser simples
# e não exigir instalação de servidor. Trocar para PostgreSQL no futuro
# será só mudar esse caminho de conexão dentro de database/db.py).
DATABASE_PATH = "database/seguro_saas.db"
