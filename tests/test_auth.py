import bcrypt

from auth.login import verificar_senha


def test_verificar_senha_correta():
    senha = "minhaSenha123"
    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    assert verificar_senha(senha, senha_hash) is True


def test_verificar_senha_incorreta():
    senha = "minhaSenha123"
    senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    assert verificar_senha("senhaErrada", senha_hash) is False
