from planos import pode_adicionar_cliente, pode_adicionar_usuario


def test_pode_adicionar_cliente_abaixo_do_limite():
    assert pode_adicionar_cliente("starter", 19) is True


def test_pode_adicionar_cliente_no_limite():
    assert pode_adicionar_cliente("starter", 20) is False


def test_pode_adicionar_cliente_plano_ilimitado():
    assert pode_adicionar_cliente("business", 10_000) is True


def test_pode_adicionar_usuario_abaixo_do_limite():
    assert pode_adicionar_usuario("pro", 4) is True


def test_pode_adicionar_usuario_no_limite():
    assert pode_adicionar_usuario("starter", 1) is False


def test_pode_adicionar_usuario_plano_ilimitado():
    assert pode_adicionar_usuario("business", 500) is True
