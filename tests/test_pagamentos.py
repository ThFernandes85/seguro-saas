from unittest.mock import MagicMock, patch

import pagamentos.mercado_pago as mp


def test_criar_assinatura_sem_token_configurado(monkeypatch):
    monkeypatch.setattr(mp, "obter_segredo", lambda chave, padrao=None: None)

    resposta, erro = mp.criar_assinatura(
        "cliente@teste.com", 100.0, "Prêmio mensal", "https://exemplo.com"
    )

    assert resposta is None
    assert "Access Token" in erro


def test_criar_assinatura_com_sucesso(monkeypatch):
    monkeypatch.setattr(mp, "obter_segredo", lambda chave, padrao=None: "TOKEN-FALSO")

    sdk_falso = MagicMock()
    sdk_falso.preapproval.return_value.create.return_value = {
        "status": 201,
        "response": {"id": "123", "init_point": "https://mp.example.com/checkout/123", "status": "pending"},
    }

    with patch.object(mp.mercadopago, "SDK", return_value=sdk_falso):
        resposta, erro = mp.criar_assinatura(
            "cliente@teste.com", 100.0, "Prêmio mensal", "https://exemplo.com"
        )

    assert erro is None
    assert resposta["id"] == "123"
    assert resposta["init_point"] == "https://mp.example.com/checkout/123"


def test_criar_assinatura_com_erro_da_api(monkeypatch):
    monkeypatch.setattr(mp, "obter_segredo", lambda chave, padrao=None: "TOKEN-FALSO")

    sdk_falso = MagicMock()
    sdk_falso.preapproval.return_value.create.return_value = {
        "status": 400,
        "response": {"message": "payer_email inválido"},
    }

    with patch.object(mp.mercadopago, "SDK", return_value=sdk_falso):
        resposta, erro = mp.criar_assinatura(
            "email-invalido", 100.0, "Prêmio mensal", "https://exemplo.com"
        )

    assert resposta is None
    assert erro == "payer_email inválido"


def test_consultar_assinatura_com_sucesso(monkeypatch):
    monkeypatch.setattr(mp, "obter_segredo", lambda chave, padrao=None: "TOKEN-FALSO")

    sdk_falso = MagicMock()
    sdk_falso.preapproval.return_value.get.return_value = {
        "status": 200,
        "response": {"id": "123", "status": "authorized"},
    }

    with patch.object(mp.mercadopago, "SDK", return_value=sdk_falso):
        resposta, erro = mp.consultar_assinatura("123")

    assert erro is None
    assert resposta["status"] == "authorized"


def test_consultar_assinatura_nao_encontrada(monkeypatch):
    monkeypatch.setattr(mp, "obter_segredo", lambda chave, padrao=None: "TOKEN-FALSO")

    sdk_falso = MagicMock()
    sdk_falso.preapproval.return_value.get.return_value = {
        "status": 404,
        "response": {"message": "Assinatura não encontrada"},
    }

    with patch.object(mp.mercadopago, "SDK", return_value=sdk_falso):
        resposta, erro = mp.consultar_assinatura("id-invalido")

    assert resposta is None
    assert erro == "Assinatura não encontrada"
