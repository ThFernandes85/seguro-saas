# utils/helpers.py
# Funções auxiliares reutilizáveis (formatação, validação, etc).
# Vamos preencher conforme forem sendo necessárias.

import re


def apenas_digitos(texto):
    """
    Remove tudo que não for dígito de uma string.
    """
    return re.sub(r"\D", "", texto or "")


def validar_cpf(cpf):
    """
    Valida um CPF conferindo os dois dígitos verificadores.
    Aceita o CPF com ou sem formatação (pontos/traço).
    """
    cpf = apenas_digitos(cpf)

    if len(cpf) != 11:
        return False

    # CPFs com todos os dígitos iguais (ex: 111.111.111-11) passam no
    # cálculo abaixo mas não são válidos na prática.
    if cpf == cpf[0] * 11:
        return False

    for posicao in (9, 10):
        soma = sum(
            int(digito) * peso
            for digito, peso in zip(cpf[:posicao], range(posicao + 1, 1, -1))
        )
        digito_esperado = (soma * 10 % 11) % 10
        if digito_esperado != int(cpf[posicao]):
            return False

    return True


def formatar_cpf(cpf):
    """
    Formata um CPF (só dígitos) como "000.000.000-00".
    Retorna o valor original se não tiver 11 dígitos.
    """
    cpf = apenas_digitos(cpf)

    if len(cpf) != 11:
        return cpf

    return f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
