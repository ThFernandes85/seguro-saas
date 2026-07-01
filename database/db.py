# database/db.py
#
# Funções de conexão e inicialização do banco de dados.
# Usamos SQLite: um banco simples que fica guardado em um único
# arquivo (.db), sem precisar instalar nenhum servidor separado.

import sqlite3
import os
import bcrypt
from config import DATABASE_PATH


def get_connection():
    """
    Abre uma conexão com o banco de dados.
    Toda função que precisar 'conversar' com o banco vai chamar
    essa função primeiro.
    """
    # Garante que a pasta do banco existe antes de tentar conectar
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # permite acessar colunas pelo nome
    return conn


def init_db():
    """
    Cria as tabelas do sistema, caso ainda não existam.
    Essa função é segura de rodar várias vezes (não duplica nada).
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Tabela de usuários.
    # Por enquanto, sem multi-tenant ainda -- isso vem na Etapa 3,
    # quando vamos adicionar a coluna "tenant_id".
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            nome_completo TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def criar_usuario_teste():
    """
    Cria um usuário padrão de teste, apenas se ainda não existir
    nenhum usuário no banco. Isso facilita testar o login sem
    precisar de uma tela de cadastro ainda.

    Usuário: admin
    Senha:   admin123
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM usuarios")
    total = cursor.fetchone()["total"]

    if total == 0:
        senha_hash = bcrypt.hashpw("admin123".encode("utf-8"), bcrypt.gensalt())
        cursor.execute(
            "INSERT INTO usuarios (username, senha_hash, nome_completo) VALUES (?, ?, ?)",
            ("admin", senha_hash.decode("utf-8"), "Administrador"),
        )
        conn.commit()

    conn.close()


def buscar_usuario(username):
    """
    Busca um usuário pelo username. Retorna None se não encontrar.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
    usuario = cursor.fetchone()
    conn.close()
    return usuario
