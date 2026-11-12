"""Pruebas del generador de explicaciones pedagógicas (6 secciones del tutor)."""
from tutor_ecuaciones.explicacion import generar_explicacion_tutor
from tutor_ecuaciones.herramientas import calcular


def _verificar_6_secciones(texto: str):
    assert "### 1. Planteamiento del Problema" in texto
    assert "### 2. Método Elegido y Justificación" in texto
    assert "### 3. Procedimiento Paso a Paso" in texto
    assert "### 4. Resultado e Interpretación Matemática" in texto
    assert "### 5. Verificación de la Solución" in texto
    assert "### 6. Idea Clave y Próximo Ejercicio" in texto


def test_explicacion_gauss_jordan_solucion_unica():
    A = [["2", "1"], ["1", "-1"]]
    b = ["5", "1"]
    res = calcular("resolver-sistema-lineal", A, b)
    texto = generar_explicacion_tutor("resolver-sistema-lineal", A, b, ["x", "y"], res)
    _verificar_6_secciones(texto)
    assert "Compatible Determinado" in texto
    assert "Comprobación exitosa" in texto


def test_explicacion_gauss_jordan_sin_solucion():
    A = [["1", "1"], ["1", "1"]]
    b = ["2", "5"]
    res = calcular("resolver-sistema-lineal", A, b)
    texto = generar_explicacion_tutor("resolver-sistema-lineal", A, b, ["x", "y"], res)
    _verificar_6_secciones(texto)
    assert "Sistema Incompatible" in texto


def test_explicacion_cramer():
    A = [["3", "2"], ["4", "-1"]]
    b = ["7", "2"]
    res = calcular("regla-de-cramer", A, b)
    texto = generar_explicacion_tutor("regla-de-cramer", A, b, ["x", "y"], res)
    _verificar_6_secciones(texto)
    assert "Regla de Cramer" in texto


def test_explicacion_matriz_inversa():
    A = [["2", "1"], ["5", "3"]]
    res = calcular("matriz-inversa", A)
    texto = generar_explicacion_tutor("matriz-inversa", A, None, ["x1", "x2"], res)
    _verificar_6_secciones(texto)
    assert "invertible" in texto.lower()
    assert "matriz identidad" in texto.lower()


def test_explicacion_metodos_iterativos():
    A = [["4", "1"], ["1", "5"]]
    b = ["5", "6"]
    opts = {"metodo": "gauss_seidel"}
    res = calcular("metodos-iterativos", A, b, **opts)
    texto = generar_explicacion_tutor("metodos-iterativos", A, b, ["x", "y"], res, opts)
    _verificar_6_secciones(texto)
    assert "Gauss-Seidel" in texto
