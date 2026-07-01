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

    # Tabela de clientes. Cada cliente pertence a uma única empresa
    # (tenant_id), e o CPF só precisa ser único dentro da empresa.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            nome TEXT NOT NULL,
            cpf TEXT NOT NULL,
            data_nascimento TEXT NOT NULL,
            telefone TEXT,
            email TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(tenant_id, cpf)
        )
    """)

    # Tabela de apólices: o prêmio (cobrança recorrente mensal) de um
    # cliente. mp_preapproval_id é o id da assinatura no Mercado Pago;
    # status reflete o status retornado por lá (pending, authorized,
    # paused, cancelled).
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apolices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            cliente_id INTEGER NOT NULL REFERENCES clientes(id),
            valor_mensal REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            mp_preapproval_id TEXT,
            mp_checkout_url TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


def criar_cliente(tenant_id, nome, cpf, data_nascimento, telefone, email):
    """
    Cadastra um cliente vinculado a uma empresa (tenant_id). Retorna o
    id do cliente criado, ou None se o CPF já estiver cadastrado
    nessa empresa.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM clientes WHERE tenant_id = ? AND cpf = ?", (tenant_id, cpf)
    )
    if cursor.fetchone() is not None:
        conn.close()
        return None

    cursor.execute(
        """
        INSERT INTO clientes (tenant_id, nome, cpf, data_nascimento, telefone, email)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (tenant_id, nome, cpf, data_nascimento, telefone, email),
    )
    conn.commit()
    cliente_id = cursor.lastrowid
    conn.close()
    return cliente_id


def listar_clientes(tenant_id):
    """
    Lista todos os clientes de uma empresa, do mais recente para o
    mais antigo.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM clientes WHERE tenant_id = ? ORDER BY id DESC", (tenant_id,)
    )
    clientes = cursor.fetchall()
    conn.close()
    return clientes


def atualizar_cliente(cliente_id, tenant_id, nome, cpf, data_nascimento, telefone, email):
    """
    Atualiza os dados de um cliente, restrito à empresa (tenant_id)
    para impedir que uma empresa altere clientes de outra. Retorna
    False se o CPF já pertencer a outro cliente dessa empresa.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM clientes WHERE tenant_id = ? AND cpf = ? AND id != ?",
        (tenant_id, cpf, cliente_id),
    )
    if cursor.fetchone() is not None:
        conn.close()
        return False

    cursor.execute(
        """
        UPDATE clientes
        SET nome = ?, cpf = ?, data_nascimento = ?, telefone = ?, email = ?
        WHERE id = ? AND tenant_id = ?
        """,
        (nome, cpf, data_nascimento, telefone, email, cliente_id, tenant_id),
    )
    conn.commit()
    conn.close()
    return True


def excluir_cliente(cliente_id, tenant_id):
    """
    Remove um cliente, restrito à empresa (tenant_id) para impedir
    que uma empresa exclua clientes de outra.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM clientes WHERE id = ? AND tenant_id = ?", (cliente_id, tenant_id)
    )
    conn.commit()
    conn.close()


def criar_apolice(tenant_id, cliente_id, valor_mensal, mp_preapproval_id, mp_checkout_url, status="pending"):
    """
    Cria uma apólice (prêmio mensal) vinculada a um cliente de uma
    empresa. Retorna o id da apólice criada.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO apolices
            (tenant_id, cliente_id, valor_mensal, status, mp_preapproval_id, mp_checkout_url)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (tenant_id, cliente_id, valor_mensal, status, mp_preapproval_id, mp_checkout_url),
    )
    conn.commit()
    apolice_id = cursor.lastrowid
    conn.close()
    return apolice_id


def listar_apolices(tenant_id):
    """
    Lista as apólices de uma empresa, junto com o nome e e-mail do
    cliente de cada uma, da mais recente para a mais antiga.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT apolices.*, clientes.nome AS cliente_nome, clientes.email AS cliente_email
        FROM apolices
        JOIN clientes ON clientes.id = apolices.cliente_id
        WHERE apolices.tenant_id = ?
        ORDER BY apolices.id DESC
        """,
        (tenant_id,),
    )
    apolices = cursor.fetchall()
    conn.close()
    return apolices


def atualizar_status_apolice(apolice_id, tenant_id, status):
    """
    Atualiza o status de uma apólice, restrito à empresa (tenant_id).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE apolices SET status = ? WHERE id = ? AND tenant_id = ?",
        (status, apolice_id, tenant_id),
    )
    conn.commit()
    conn.close()


def obter_resumo_apolices(tenant_id):
    """
    Retorna métricas agregadas das apólices de uma empresa: quantidade
    por status (`por_status`) e a receita mensal recorrente
    (`receita_mensal_recorrente`), que é a soma do valor_mensal
    apenas das apólices com status "authorized" (assinatura ativa).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT status, COUNT(*) AS total, SUM(valor_mensal) AS soma
        FROM apolices
        WHERE tenant_id = ?
        GROUP BY status
        """,
        (tenant_id,),
    )
    linhas = cursor.fetchall()
    conn.close()

    por_status = {linha["status"]: linha["total"] for linha in linhas}
    receita_mensal_recorrente = sum(
        linha["soma"] for linha in linhas if linha["status"] == "authorized"
    )

    return {
        "por_status": por_status,
        "receita_mensal_recorrente": receita_mensal_recorrente,
    }
