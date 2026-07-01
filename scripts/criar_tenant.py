"""
scripts/criar_tenant.py — Cadastra uma nova empresa (tenant) e seu
usuário administrador.

Uso (rodando a partir da pasta do projeto):
    venv\\Scripts\\python.exe scripts\\criar_tenant.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import init_db, criar_tenant, criar_usuario


def main():
    init_db()

    print("=== Cadastro de nova empresa ===")
    nome = input("Nome da empresa: ").strip()
    slug = input("Slug da empresa (usado no login, ex: acme-seguros): ").strip()

    tenant_id = criar_tenant(nome, slug)
    if tenant_id is None:
        print(f"Já existe uma empresa com o slug '{slug}'. Escolha outro.")
        return

    print("\n=== Cadastro do usuário administrador ===")
    username = input("Usuário: ").strip()
    senha = input("Senha: ").strip()
    nome_completo = input("Nome completo: ").strip()

    usuario_id = criar_usuario(tenant_id, username, senha, nome_completo)
    if usuario_id is None:
        print(f"Já existe um usuário '{username}' nessa empresa.")
        return

    print(f"\nEmpresa '{nome}' (slug: {slug}) criada com sucesso!")
    print(f"Usuário administrador '{username}' pronto para login.")


if __name__ == "__main__":
    main()
