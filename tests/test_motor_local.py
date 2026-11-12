"""Pruebas del parser algebraico determinista y formato LaTeX KaTeX-safe."""
from fractions import Fraction
from tutor_ecuaciones.motor_local.parser import (
    detectar_skill_solicitada,
    extraer_sistema_completo,
    matriz_a_latex,
    parse_ecuacion_lineal,
    parse_matriz_en_texto,
    sistema_a_latex,
)


def test_parse_ecuacion_lineal():
    coefs, b = parse_ecuacion_lineal("2x - 3y + z = 8")
    assert coefs["x"] == Fraction(2)
    assert coefs["y"] == Fraction(-3)
    assert coefs["z"] == Fraction(1)
    assert b == Fraction(8)


def test_extraer_sistema_completo():
    texto = "Resuelve: 2x + y = 5; x - y = 1"
    A, b, vars_u = extraer_sistema_completo(texto)
    assert A == [["2", "1"], ["1", "-1"]]
    assert b == ["5", "1"]
    assert vars_u == ["x", "y"]


def test_parse_matriz_en_texto():
    texto = "Calcula la inversa de [[2, 1], [5, 3]]"
    A, b = parse_matriz_en_texto(texto)
    assert A == [["2", "1"], ["5", "3"]]
    assert b is None


def test_detectar_skill_solicitada():
    skill, _ = detectar_skill_solicitada("Resuelve por Cramer el sistema")
    assert skill == "regla-de-cramer"

    skill, opts = detectar_skill_solicitada("Aplica Gauss-Seidel")
    assert skill == "metodos-iterativos"
    assert opts["metodo"] == "gauss_seidel"


def test_latex_katex_safe_no_tiene_syntax_invalido():
    A = [["1", "2"], ["3", "4"]]
    b = ["5", "6"]
    vars_u = ["x", "y"]
    latex_sys = sistema_a_latex(A, b, vars_u)
    # KaTeX en Streamlit falla con '&=' en begin{cases}; debe ser solo '='
    assert "&=" not in latex_sys
    assert "\\begin{cases}" in latex_sys

    mat_latex = matriz_a_latex(A)
    assert "\\begin{pmatrix}" in mat_latex
