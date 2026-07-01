from utils.helpers import apenas_digitos, validar_cpf, formatar_cpf


def test_validar_cpf_valido():
    assert validar_cpf("529.982.247-25") is True
    assert validar_cpf("52998224725") is True


def test_validar_cpf_digitos_verificadores_invalidos():
    assert validar_cpf("529.982.247-24") is False


def test_validar_cpf_todos_digitos_iguais():
    assert validar_cpf("111.111.111-11") is False


def test_validar_cpf_tamanho_invalido():
    assert validar_cpf("123") is False


def test_apenas_digitos():
    assert apenas_digitos("529.982.247-25") == "52998224725"


def test_formatar_cpf():
    assert formatar_cpf("52998224725") == "529.982.247-25"
