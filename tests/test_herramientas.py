"""Pruebas de wrappers de herramientas y parseo auxiliar."""
import json
import pytest
from tutor_ecuaciones.herramientas import (
    HERRAMIENTAS,
    calcular_inversa,
    parsear_matriz,
    parsear_vector,
    resolver_cramer,
    resolver_iterativo,
    resolver_lineal,
)


def test_lista_de_herramientas_tiene_exactamente_4():
    assert len(HERRAMIENTAS) == 4
    nombres = [f.__name__ for f in HERRAMIENTAS]
    assert "resolver_lineal" in nombres
    assert "resolver_iterativo" in nombres
    assert "resolver_cramer" in nombres
    assert "calcular_inversa" in nombres


def test_herramientas_devuelven_json_valido():
    res_str = resolver_lineal([["1", "1"], ["1", "-1"]], ["2", "0"])
    res = json.loads(res_str)
    assert res["ok"] is True
    assert res["tipo"] == "unica"


def test_parsear_matriz_y_vector():
    M = parsear_matriz("2 1 -1\n-3 -1 2\n-2 1 2")
    assert len(M) == 3
    assert len(M[0]) == 3

    b = parsear_vector("8, -11, -3")
    assert b == ["8", "-11", "-3"]


def test_parsear_matriz_invalida_lanza_error():
    with pytest.raises(ValueError):
        parsear_matriz("1 2\n3")
