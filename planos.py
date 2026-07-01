# planos.py
#
# Planos de assinatura do SaaS: o que a própria corretora (tenant)
# paga para usar o sistema, e os limites de uso de cada plano.
# `None` em um limite significa "ilimitado".

PLANOS = {
    "starter": {
        "nome": "Starter",
        "preco_mensal": 49.90,
        "limite_clientes": 20,
        "limite_usuarios": 1,
    },
    "pro": {
        "nome": "Pro",
        "preco_mensal": 149.90,
        "limite_clientes": 100,
        "limite_usuarios": 5,
    },
    "business": {
        "nome": "Business",
        "preco_mensal": 399.90,
        "limite_clientes": None,
        "limite_usuarios": None,
    },
}

PLANO_PADRAO = "starter"


def pode_adicionar_cliente(plano, total_atual):
    """
    Verifica se a empresa ainda pode cadastrar mais um cliente, de
    acordo com o limite do seu plano.
    """
    limite = PLANOS[plano]["limite_clientes"]
    return limite is None or total_atual < limite


def pode_adicionar_usuario(plano, total_atual):
    """
    Verifica se a empresa ainda pode cadastrar mais um usuário, de
    acordo com o limite do seu plano.
    """
    limite = PLANOS[plano]["limite_usuarios"]
    return limite is None or total_atual < limite
