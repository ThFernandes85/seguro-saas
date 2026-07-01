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

    # Tabela de empresas (tenants). Cada corretora que usa o sistema
    # é uma linha aqui, identificada por um "slug" (ex: "acme-seguros").
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Tabela de usuários. Cada usuário pertence a uma única empresa
    # (tenant_id), e o username só precisa ser único dentro da empresa
    # -- duas empresas diferentes podem ter cada uma o seu "admin".
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            username TEXT NOT NULL,
            senha_hash TEXT NOT NULL,
            nome_completo TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(tenant_id, username)
        )
    """)

    conn.commit()
    conn.close()


def criar_tenant(nome, slug):
    """
    Cria uma nova empresa (tenant). Retorna o id do tenant criado,
    ou None se o slug já estiver em uso.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tenants WHERE slug = ?", (slug,))
    if cursor.fetchone() is not None:
        conn.close()
        return None

    cursor.execute("INSERT INTO tenants (nome, slug) VALUES (?, ?)", (nome, slug))
    conn.commit()
    tenant_id = cursor.lastrowid
    conn.close()
    return tenant_id


def buscar_tenant_por_slug(slug):
    """
    Busca uma empresa pelo slug. Retorna None se não encontrar.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tenants WHERE slug = ?", (slug,))
    tenant = cursor.fetchone()
    conn.close()
    return tenant


def criar_usuario(tenant_id, username, senha, nome_completo):
    """
    Cria um usuário vinculado a uma empresa (tenant_id). Retorna o id
    do usuário criado, ou None se o username já existir nessa empresa.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM usuarios WHERE tenant_id = ? AND username = ?",
        (tenant_id, username),
    )
    if cursor.fetchone() is not None:
        conn.close()
        return None

    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO usuarios (tenant_id, username, senha_hash, nome_completo) "
        "VALUES (?, ?, ?, ?)",
        (tenant_id, username, senha_hash.decode("utf-8"), nome_completo),
    )
    conn.commit()
    usuario_id = cursor.lastrowid
    conn.close()
    return usuario_id


def criar_tenant_e_usuario_teste():
    """
    Cria uma empresa de demonstração e um usuário admin padrão,
    apenas se ainda não existir nenhuma empresa no banco. Isso facilita
    testar o login sem precisar de uma tela de cadastro ainda.

    Empresa: demo
    Usuário: admin
    Senha:   admin123
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM tenants")
    total = cursor.fetchone()["total"]
    conn.close()

    if total == 0:
        tenant_id = criar_tenant("Empresa Demo", "demo")
        criar_usuario(tenant_id, "admin", "admin123", "Administrador")


def buscar_usuario(tenant_slug, username):
    """
    Busca um usuário pelo slug da empresa e pelo username.
    Retorna None se a empresa ou o usuário não existirem.
    """
    tenant = buscar_tenant_por_slug(tenant_slug)
    if tenant is None:
        return None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE tenant_id = ? AND username = ?",
        (tenant["id"], username),
    )
    usuario = cursor.fetchone()
    conn.close()
    return usuario
