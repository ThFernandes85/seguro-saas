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
from planos import PLANOS, PLANO_PADRAO


def main():
    init_db()

    print("=== Cadastro de nova empresa ===")
    nome = input("Nome da empresa: ").strip()
    slug = input("Slug da empresa (usado no login, ex: acme-seguros): ").strip()
    email_contato = input("E-mail de contato (para cobrança do plano): ").strip()

    print(f"\nPlanos disponíveis: {', '.join(PLANOS.keys())} (padrão: {PLANO_PADRAO})")
    plano = input(f"Plano [{PLANO_PADRAO}]: ").strip() or PLANO_PADRAO
    if plano not in PLANOS:
        print(f"Plano '{plano}' não existe. Escolha um de: {', '.join(PLANOS.keys())}.")
        return

    tenant_id = criar_tenant(nome, slug, email_contato=email_contato, plano=plano)
    if tenant_id is None:
        print(f"Já existe uma empresa com o slug '{slug}'. Escolha outro.")
        return

    print("\n=== Cadastro do usuário administrador ===")
    username = input("Usuário: ").strip()
    senha = input("Senha: ").strip()
    nome_completo = input("Nome completo: ").strip()

    usuario_id, erro = criar_usuario(tenant_id, username, senha, nome_completo)
    if erro:
        print(erro)
        return

    print(f"\nEmpresa '{nome}' (slug: {slug}, plano: {plano}) criada com sucesso!")
    print(f"Usuário administrador '{username}' pronto para login.")


if __name__ == "__main__":
    main()
