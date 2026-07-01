import datetime

import bcrypt

import auth.login as auth_login
from auth.login import LIMITE_TENTATIVAS, calcular_bloqueio, esta_bloqueado, verificar_senha


def test_verificar_senha_correta():
    senha = "minhaSenha123"
    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    assert verificar_senha(senha, senha_hash) is True


def test_verificar_senha_incorreta():
    senha = "minhaSenha123"
    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    assert verificar_senha("senhaErrada", senha_hash) is False


def test_calcular_bloqueio_abaixo_do_limite():
    assert calcular_bloqueio(LIMITE_TENTATIVAS - 1) is None


def test_calcular_bloqueio_no_limite():
    resultado = calcular_bloqueio(LIMITE_TENTATIVAS)

    assert resultado is not None
    assert resultado > datetime.datetime.now(datetime.timezone.utc)


def test_esta_bloqueado_sem_bloqueio():
    assert esta_bloqueado(None) is False


def test_esta_bloqueado_no_passado():
    passado = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=1)).isoformat()

    assert esta_bloqueado(passado) is False


def test_esta_bloqueado_no_futuro():
    futuro = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)).isoformat()

    assert esta_bloqueado(futuro) is True


def _usuario_fake(senha="correta123"):
    return {
        "id": 1,
        "senha_hash": bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8"),
    }


def test_alterar_senha_senha_atual_incorreta(monkeypatch):
    monkeypatch.setattr(auth_login, "buscar_usuario_por_id", lambda uid, tid: _usuario_fake())

    sucesso, erro = auth_login.alterar_senha(1, 1, "senhaErrada", "novaSenha123")

    assert sucesso is False
    assert "incorreta" in erro


def test_alterar_senha_muito_curta(monkeypatch):
    monkeypatch.setattr(auth_login, "buscar_usuario_por_id", lambda uid, tid: _usuario_fake())

    sucesso, erro = auth_login.alterar_senha(1, 1, "correta123", "curta")

    assert sucesso is False
    assert "8 caracteres" in erro


def test_alterar_senha_com_sucesso(monkeypatch):
    monkeypatch.setattr(auth_login, "buscar_usuario_por_id", lambda uid, tid: _usuario_fake())

    chamadas = {}

    def salvar_fake(usuario_id, nova_hash):
        chamadas["usuario_id"] = usuario_id
        chamadas["nova_hash"] = nova_hash

    monkeypatch.setattr(auth_login, "salvar_nova_senha", salvar_fake)

    sucesso, erro = auth_login.alterar_senha(1, 1, "correta123", "novaSenha123")

    assert sucesso is True
    assert erro is None
    assert chamadas["usuario_id"] == 1
