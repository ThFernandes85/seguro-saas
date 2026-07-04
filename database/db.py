# database/db.py
#
# Funções de conexão e inicialização do banco de dados.
# Usamos SQLite: um banco simples que fica guardado em um único
# arquivo (.db), sem precisar instalar nenhum servidor separado.

import sqlite3
import os
import bcrypt
from config import DATABASE_PATH
from planos import PLANO_PADRAO, pode_adicionar_cliente, pode_adicionar_usuario


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
    # plano/limite: ver planos.py. mp_preapproval_id e assinatura_status
    # são da assinatura do PRÓPRIO SaaS que a corretora paga (não tem
    # relação com as apólices dos clientes dela).
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            plano TEXT NOT NULL DEFAULT 'starter',
            email_contato TEXT,
            mp_preapproval_id TEXT,
            assinatura_status TEXT NOT NULL DEFAULT 'sem_assinatura'
        )
    """)

    # Migração para bancos criados antes dessas colunas existirem.
    colunas_tenants = {linha["name"] for linha in cursor.execute("PRAGMA table_info(tenants)")}
    if "plano" not in colunas_tenants:
        cursor.execute("ALTER TABLE tenants ADD COLUMN plano TEXT NOT NULL DEFAULT 'starter'")
    if "email_contato" not in colunas_tenants:
        cursor.execute("ALTER TABLE tenants ADD COLUMN email_contato TEXT")
    if "mp_preapproval_id" not in colunas_tenants:
        cursor.execute("ALTER TABLE tenants ADD COLUMN mp_preapproval_id TEXT")
    if "assinatura_status" not in colunas_tenants:
        cursor.execute("ALTER TABLE tenants ADD COLUMN assinatura_status TEXT NOT NULL DEFAULT 'sem_assinatura'")

    # Tabela de usuários. Cada usuário pertence a uma única empresa
    # (tenant_id), e o username só precisa ser único dentro da empresa
    # -- duas empresas diferentes podem ter cada uma o seu "admin".
    # tentativas_falhas e bloqueado_ate implementam a proteção contra
    # força bruta no login (ver auth/login.py).
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL REFERENCES tenants(id),
            username TEXT NOT NULL,
            senha_hash TEXT NOT NULL,
            nome_completo TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tentativas_falhas INTEGER NOT NULL DEFAULT 0,
            bloqueado_ate TEXT,
            UNIQUE(tenant_id, username)
        )
    """)

    # Migração para bancos criados antes de tentativas_falhas/bloqueado_ate
    # existirem (CREATE TABLE IF NOT EXISTS não altera tabelas já criadas).
    colunas_usuarios = {linha["name"] for linha in cursor.execute("PRAGMA table_info(usuarios)")}
    if "tentativas_falhas" not in colunas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN tentativas_falhas INTEGER NOT NULL DEFAULT 0")
    if "bloqueado_ate" not in colunas_usuarios:
        cursor.execute("ALTER TABLE usuarios ADD COLUMN bloqueado_ate TEXT")

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


def criar_tenant(nome, slug, email_contato=None, plano=PLANO_PADRAO):
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

    cursor.execute(
        "INSERT INTO tenants (nome, slug, email_contato, plano) VALUES (?, ?, ?, ?)",
        (nome, slug, email_contato, plano),
    )
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


def buscar_tenant_por_id(tenant_id):
    """
    Busca uma empresa pelo id. Retorna None se não encontrar.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,))
    tenant = cursor.fetchone()
    conn.close()
    return tenant


def listar_tenants():
    """
    Lista todas as empresas (tenants) cadastradas, da mais recente
    para a mais antiga. Usado no painel de administração do SaaS.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tenants ORDER BY id DESC")
    tenants = cursor.fetchall()
    conn.close()
    return tenants


def atualizar_plano_tenant(tenant_id, plano):
    """
    Atualiza o plano de assinatura de uma empresa.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tenants SET plano = ? WHERE id = ?", (plano, tenant_id))
    conn.commit()
    conn.close()


def atualizar_email_contato_tenant(tenant_id, email_contato):
    """
    Atualiza o e-mail de contato/cobrança de uma empresa.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tenants SET email_contato = ? WHERE id = ?", (email_contato, tenant_id)
    )
    conn.commit()
    conn.close()


def atualizar_assinatura_tenant(tenant_id, mp_preapproval_id, status):
    """
    Atualiza os dados da assinatura do próprio SaaS de uma empresa
    (a mensalidade que a corretora paga para usar o sistema).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tenants SET mp_preapproval_id = ?, assinatura_status = ? WHERE id = ?",
        (mp_preapproval_id, status, tenant_id),
    )
    conn.commit()
    conn.close()


def contar_clientes(tenant_id):
    """
    Conta quantos clientes uma empresa já tem cadastrados.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM clientes WHERE tenant_id = ?", (tenant_id,))
    total = cursor.fetchone()["total"]
    conn.close()
    return total


def contar_usuarios(tenant_id):
    """
    Conta quantos usuários uma empresa já tem cadastrados.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM usuarios WHERE tenant_id = ?", (tenant_id,))
    total = cursor.fetchone()["total"]
    conn.close()
    return total


def criar_usuario(tenant_id, username, senha, nome_completo):
    """
    Cria um usuário vinculado a uma empresa (tenant_id).

    Retorna uma tupla (usuario_id, erro):
    - Em caso de sucesso: (id do usuário, None).
    - Em caso de falha: (None, mensagem de erro) -- username duplicado
      nessa empresa, ou limite de usuários do plano atingido.
    """
    tenant = buscar_tenant_por_id(tenant_id)
    if tenant is not None and not pode_adicionar_usuario(tenant["plano"], contar_usuarios(tenant_id)):
        return None, "Limite de usuários do plano atingido. Faça upgrade para adicionar mais."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM usuarios WHERE tenant_id = ? AND username = ?",
        (tenant_id, username),
    )
    if cursor.fetchone() is not None:
        conn.close()
        return None, "Já existe um usuário com esse nome nessa empresa."

    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt())
    cursor.execute(
        "INSERT INTO usuarios (tenant_id, username, senha_hash, nome_completo) "
        "VALUES (?, ?, ?, ?)",
        (tenant_id, username, senha_hash.decode("utf-8"), nome_completo),
    )
    conn.commit()
    usuario_id = cursor.lastrowid
    conn.close()
    return usuario_id, None


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
        tenant_id = criar_tenant("Empresa Demo", "demo", email_contato="demo@example.com")
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


def buscar_usuario_por_id(usuario_id, tenant_id):
    """
    Busca um usuário pelo id, restrito à empresa (tenant_id).
    Retorna None se não encontrar.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE id = ? AND tenant_id = ?", (usuario_id, tenant_id)
    )
    usuario = cursor.fetchone()
    conn.close()
    return usuario


def incrementar_tentativas_falhas(usuario_id):
    """
    Incrementa o contador de tentativas de login falhas de um
    usuário. Retorna o novo total de tentativas.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET tentativas_falhas = tentativas_falhas + 1 WHERE id = ?",
        (usuario_id,),
    )
    conn.commit()
    cursor.execute("SELECT tentativas_falhas FROM usuarios WHERE id = ?", (usuario_id,))
    total = cursor.fetchone()["tentativas_falhas"]
    conn.close()
    return total


def bloquear_usuario_ate(usuario_id, bloqueado_ate_iso):
    """
    Marca um usuário como bloqueado até o horário informado (string
    ISO 8601, em UTC).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET bloqueado_ate = ? WHERE id = ?", (bloqueado_ate_iso, usuario_id)
    )
    conn.commit()
    conn.close()


def resetar_tentativas_falhas(usuario_id):
    """
    Zera o contador de tentativas falhas e remove o bloqueio de um
    usuário. Chamado após um login bem-sucedido.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET tentativas_falhas = 0, bloqueado_ate = NULL WHERE id = ?",
        (usuario_id,),
    )
    conn.commit()
    conn.close()


def salvar_nova_senha(usuario_id, senha_hash):
    """
    Atualiza o hash de senha de um usuário (troca de senha).
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE usuarios SET senha_hash = ? WHERE id = ?", (senha_hash, usuario_id)
    )
    conn.commit()
    conn.close()


def criar_cliente(tenant_id, nome, cpf, data_nascimento, telefone, email):
    """
    Cadastra um cliente vinculado a uma empresa (tenant_id).

    Retorna uma tupla (cliente_id, erro):
    - Em caso de sucesso: (id do cliente, None).
    - Em caso de falha: (None, mensagem de erro) -- CPF duplicado
      nessa empresa, ou limite de clientes do plano atingido.
    """
    tenant = buscar_tenant_por_id(tenant_id)
    if tenant is not None and not pode_adicionar_cliente(tenant["plano"], contar_clientes(tenant_id)):
        return None, "Limite de clientes do plano atingido. Faça upgrade para cadastrar mais."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM clientes WHERE tenant_id = ? AND cpf = ?", (tenant_id, cpf)
    )
    if cursor.fetchone() is not None:
        conn.close()
        return None, "Já existe um cliente com esse CPF nesta empresa."

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
    return cliente_id, None


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
