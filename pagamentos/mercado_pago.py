# pagamentos/mercado_pago.py
#
# Integração com o Mercado Pago para cobrança recorrente (assinatura)
# do prêmio mensal do seguro, usando a API de "preapproval".
#
# Documentação: https://www.mercadopago.com.br/developers/pt/docs/subscriptions

import mercadopago

from config import MERCADOPAGO_ACCESS_TOKEN_KEY, obter_segredo


def get_sdk():
    """
    Retorna o cliente do Mercado Pago, ou None se o Access Token
    ainda não tiver sido configurado em .streamlit/secrets.toml.
    """
    access_token = obter_segredo(MERCADOPAGO_ACCESS_TOKEN_KEY)
    if not access_token:
        return None
    return mercadopago.SDK(access_token)


def criar_assinatura(email_cliente, valor_mensal, motivo, back_url):
    """
    Cria uma assinatura (cobrança recorrente mensal) no Mercado Pago.

    Retorna uma tupla (resposta, erro):
    - Em caso de sucesso: (dict com "id" e "init_point", None).
    - Em caso de falha: (None, mensagem de erro).
    """
    sdk = get_sdk()
    if sdk is None:
        return None, "Access Token do Mercado Pago não configurado."

    dados = {
        "reason": motivo,
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "transaction_amount": valor_mensal,
            "currency_id": "BRL",
        },
        "back_url": back_url,
        "payer_email": email_cliente,
        "status": "pending",
    }

    resultado = sdk.preapproval().create(dados)
    resposta = resultado.get("response", {})

    if resultado.get("status") not in (200, 201):
        return None, resposta.get("message", "Erro ao criar assinatura no Mercado Pago.")

    return resposta, None


def consultar_assinatura(preapproval_id):
    """
    Consulta o status atual de uma assinatura no Mercado Pago
    (ex: "pending", "authorized", "paused", "cancelled").

    Retorna uma tupla (resposta, erro), no mesmo formato de
    `criar_assinatura`.
    """
    sdk = get_sdk()
    if sdk is None:
        return None, "Access Token do Mercado Pago não configurado."

    resultado = sdk.preapproval().get(preapproval_id)
    resposta = resultado.get("response", {})

    if resultado.get("status") != 200:
        return None, resposta.get("message", "Erro ao consultar assinatura.")

    return resposta, None
