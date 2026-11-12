"""Herramientas matemáticas exactas basadas en las skills del sistema.

Cada herramienta envuelve un script independiente en skills/ que utiliza aritmética
exacta con fractions.Fraction de la librería estándar de Python.
"""
from __future__ import annotations

import importlib.util
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from tutor_ecuaciones.config import SKILLS_DIR


def _cargar_modulo(ruta_relativa: str, nombre_modulo: str):
    ruta_script = SKILLS_DIR / ruta_relativa
    if not ruta_script.exists():
        raise FileNotFoundError(f"No se encontró el script de skill: {ruta_script}")
    spec = importlib.util.spec_from_file_location(nombre_modulo, ruta_script)
    if spec is None or spec.loader is None:
        raise ImportError(f"No se pudo cargar el módulo desde: {ruta_script}")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


_skill_lineal = _cargar_modulo("resolver-sistema-lineal/scripts/resolver_lineal.py", "skill_lineal")
_skill_iterativos = _cargar_modulo("metodos-iterativos/scripts/iterativos.py", "skill_iterativos")
_skill_cramer = _cargar_modulo("regla-de-cramer/scripts/cramer.py", "skill_cramer")
_skill_inversa = _cargar_modulo("matriz-inversa/scripts/inversa.py", "skill_inversa")


def _a_float(valor: Any) -> float:
    try:
        return float(Fraction(str(valor).strip()))
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"Valor numérico no válido: {valor!r}")


def calcular(skill: str, A: list[list[Any]], b: list[Any] | None = None, **opciones) -> dict[str, Any]:
    """Ejecuta una skill de cálculo exacto de forma pura y sin estado global compartido.

    Devuelve un diccionario con el resultado del script o un diccionario de error amigable.
    """
    try:
        if skill == "resolver-sistema-lineal":
            if b is None:
                raise ValueError("El método de Gauss-Jordan requiere el vector b de términos independientes.")
            return _skill_lineal.resolver(A, b)

        elif skill == "regla-de-cramer":
            if b is None:
                raise ValueError("La regla de Cramer requiere el vector b de términos independientes.")
            return _skill_cramer.resolver(A, b)

        elif skill == "matriz-inversa":
            return _skill_inversa.resolver(A, b if b else None)

        elif skill == "metodos-iterativos":
            if b is None:
                raise ValueError("Los métodos iterativos requieren el vector b de términos independientes.")
            x0 = opciones.get("x0")
            return _skill_iterativos.resolver(
                [[_a_float(v) for v in fila] for fila in A],
                [_a_float(v) for v in b],
                opciones.get("metodo", "gauss_seidel"),
                [_a_float(v) for v in x0] if x0 else None,
                float(opciones.get("tolerancia", 1e-6)),
                int(opciones.get("max_iter", 100)),
            )
        else:
            raise ValueError(f"Skill no reconocida: {skill}")

    except (ValueError, TypeError, ZeroDivisionError) as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def _serializar_json(resultado: dict[str, Any]) -> str:
    return json.dumps(resultado, ensure_ascii=False)


# ----------------------------------------------------------------------------
# Herramientas expuestas al agente (Antigravity SDK y Gemini)
# ----------------------------------------------------------------------------

def resolver_lineal(A: list[list[str]], b: list[str]) -> str:
    """Resuelve un sistema de ecuaciones lineales Ax = b mediante el método de Gauss-Jordan.

    Parámetros:
        A: Matriz de coeficientes, donde cada elemento es una cadena numérica exacta ('2', '-1/3', '0.5').
        b: Vector de términos independientes como lista de cadenas ('8', '-11', '3').
    Retorna:
        JSON con 'tipo' ('unica', 'infinitas' o 'sin_solucion'), 'solucion', 'pasos' y 'explicacion'.
    """
    return _serializar_json(calcular("resolver-sistema-lineal", A, b))


def resolver_iterativo(
    A: list[list[str]],
    b: list[str],
    metodo: str = "gauss_seidel",
    x0: list[str] | None = None,
    tolerancia: float = 1e-6,
    max_iter: int = 100,
) -> str:
    """Resuelve un sistema cuadrado Ax = b mediante métodos numéricos iterativos (Jacobi o Gauss-Seidel).

    Parámetros:
        A: Matriz cuadrada de coeficientes como cadenas numéricas.
        b: Vector de términos independientes.
        metodo: 'gauss_seidel' o 'jacobi'.
        x0: Vector inicial opcional (por defecto ceros).
        tolerancia: Criterio de parada por error relativo/absoluto (ej. 1e-6).
        max_iter: Límite máximo de iteraciones.
    Retorna:
        JSON con 'convergio', 'iteraciones', 'solucion', 'tabla' y 'diagonal_dominante'.
    """
    return _serializar_json(
        calcular(
            "metodos-iterativos",
            A,
            b,
            metodo=metodo,
            x0=x0,
            tolerancia=tolerancia,
            max_iter=max_iter,
        )
    )


def resolver_cramer(A: list[list[str]], b: list[str]) -> str:
    """Resuelve un sistema cuadrado Ax = b mediante la Regla de Cramer con determinantes exactos.

    Parámetros:
        A: Matriz cuadrada de coeficientes.
        b: Vector de términos independientes.
    Retorna:
        JSON con 'determinante', 'determinantes_variables' y 'solucion'. Si det(A)=0, indica tipo 'no_aplicable'.
    """
    return _serializar_json(calcular("regla-de-cramer", A, b))


def calcular_inversa(A: list[list[str]], b: list[str] | None = None) -> str:
    """Calcula la matriz inversa A^-1 por Gauss-Jordan y opcionalmente resuelve Ax = b con x = A^-1 * b.

    Parámetros:
        A: Matriz cuadrada a invertir.
        b: Vector opcional de términos independientes.
    Retorna:
        JSON con 'invertible', 'determinante', 'inversa', 'solucion' y 'pasos'.
    """
    return _serializar_json(calcular("matriz-inversa", A, b))


HERRAMIENTAS = [resolver_lineal, resolver_iterativo, resolver_cramer, calcular_inversa]


# ----------------------------------------------------------------------------
# Parseadores auxiliares para la calculadora directa interactiva
# ----------------------------------------------------------------------------

def parsear_matriz(texto: str) -> list[list[str]]:
    """Convierte texto de matriz ('2 1 -1\\n-3 -1 2') en lista 2D de cadenas."""
    filas = [[t for t in linea.replace(",", " ").split()] for linea in texto.strip().splitlines() if linea.strip()]
    if not filas:
        raise ValueError("Debe ingresar al menos una fila en la matriz de coeficientes.")
    cols = len(filas[0])
    for idx, f in enumerate(filas, 1):
        if len(f) != cols:
            raise ValueError(f"Fila {idx} tiene {len(f)} elementos, pero la fila 1 tiene {cols}.")
    return filas


def parsear_vector(texto: str) -> list[str]:
    """Convierte texto de vector ('8 -11 -3' o '8, -11, -3') en lista de cadenas."""
    elems = [t for t in texto.replace(",", " ").split() if t.strip()]
    if not elems:
        raise ValueError("El vector de términos independientes no puede estar vacío.")
    return elems
