"""Parser algebraico y extractor de sistemas matemáticos sin IA."""
from __future__ import annotations

import json
import re
from fractions import Fraction
from typing import Any


def a_fraccion_exacta(x: Any) -> Fraction:
    """Convierte cualquier número, decimal o cadena a Fraction exacta."""
    try:
        return Fraction(str(x).strip())
    except Exception:
        raise ValueError(f"Valor numérico no válido: {x!r}")


def parse_ecuacion_lineal(eq_str: str) -> tuple[dict[str, Fraction], Fraction] | None:
    """Parsea una ecuación lineal individual como '2x + y - z = 8' o '-3x_1 + 1/2x_2 = 4'.

    Retorna: (diccionario_coeficientes, termino_independiente_b) o None si no es válida.
    """
    if "=" not in eq_str:
        return None
    partes = eq_str.split("=")
    if len(partes) != 2:
        return None

    lhs, rhs = partes[0].strip(), partes[1].strip()
    lhs = re.sub(r"^[a-zA-ZáéíóúÁÉÍÓÚ\s0-9_]+:\s*", "", lhs).strip()

    patron = r"([+-]?\s*\d*(?:/\d+|\.\d+)?)\s*([a-zA-Z](?:_?\d+)?)"
    tokens = re.findall(patron, lhs)
    if not tokens:
        return None

    coefs: dict[str, Fraction] = {}
    for c_str, var in tokens:
        if not var:
            continue
        c_clean = c_str.replace(" ", "")
        if c_clean in ("", "+"):
            val = Fraction(1)
        elif c_clean == "-":
            val = Fraction(-1)
        else:
            val = a_fraccion_exacta(c_clean)
        coefs[var] = coefs.get(var, Fraction(0)) + val

    try:
        rhs_clean = re.sub(r"[^\d/.-]", "", rhs)
        b_val = a_fraccion_exacta(rhs_clean) if rhs_clean else Fraction(0)
    except Exception:
        b_val = Fraction(0)

    return coefs, b_val


def parse_matriz_en_texto(texto: str) -> tuple[list[list[str]] | None, list[str] | None]:
    """Detecta matrices y vectores b escritos en formato lista [[2,1],[5,3]]."""
    match_mat = re.search(r"\[\s*\[.*?\]\s*\]", texto, re.DOTALL)
    if match_mat:
        try:
            mat_raw = json.loads(match_mat.group(0))
            if isinstance(mat_raw, list) and all(isinstance(r, list) for r in mat_raw):
                A = [[str(elem) for elem in fila] for fila in mat_raw]
                match_b = re.search(r"[bB]\s*[:=]\s*\[(.*?)\]", texto)
                b = None
                if match_b:
                    b = [e.strip() for e in match_b.group(1).replace(",", " ").split() if e.strip()]
                return A, b
        except Exception:
            pass

        filas_str = re.findall(r"\[([^\[\]]+)\]", match_mat.group(0))
        A = []
        for f in filas_str:
            elementos = [e.strip() for e in f.replace(",", " ").split() if e.strip()]
            if elementos:
                A.append(elementos)
        if A:
            match_b = re.search(r"[bB]\s*[:=]\s*\[(.*?)\]", texto)
            b = None
            if match_b:
                b = [e.strip() for e in match_b.group(1).replace(",", " ").split() if e.strip()]
            return A, b
    return None, None


def extraer_sistema_completo(texto: str) -> tuple[list[list[str]] | None, list[str] | None, list[str] | None]:
    """Extrae la matriz A, vector b y nombres de variables de cualquier texto de usuario."""
    # 1. Intentar matrices en formato lista
    A_mat, b_mat = parse_matriz_en_texto(texto)
    if A_mat:
        n = len(A_mat[0])
        vars_default = [f"x{i+1}" for i in range(n)]
        return A_mat, b_mat, vars_default

    # 2. Separar ecuaciones por ';', saltos de línea o comas
    lineas = re.split(r"[;\n\r]+", texto)
    candidatos = []
    for l in lineas:
        l = l.strip()
        if "," in l and "=" in l and not re.search(r"\[.*?\]", l):
            sub = l.split(",")
            for s in sub:
                if "=" in s:
                    candidatos.append(s.strip())
        elif "=" in l:
            candidatos.append(l)

    parsed = []
    todas_vars = set()
    for eq in candidatos:
        res = parse_ecuacion_lineal(eq)
        if res:
            coefs, b_val = res
            parsed.append((coefs, b_val))
            todas_vars.update(coefs.keys())

    if not parsed or not todas_vars:
        return None, None, None

    vars_ordenadas = sorted(list(todas_vars), key=lambda v: (len(v), v))
    A: list[list[str]] = []
    b: list[str] = []
    for coefs, b_val in parsed:
        fila = [str(coefs.get(v, Fraction(0))) for v in vars_ordenadas]
        A.append(fila)
        b.append(str(b_val))

    return A, b, vars_ordenadas


def detectar_skill_solicitada(texto: str, A: list[list[str]] | None = None) -> tuple[str, dict[str, Any]]:
    """Identifica el método numérico o algebraico solicitado según el texto del usuario."""
    t = texto.lower()
    opciones: dict[str, Any] = {}

    if "cramer" in t:
        return "regla-de-cramer", opciones
    if "inversa" in t or "invertir" in t or "inversa de" in t:
        return "matriz-inversa", opciones
    if "jacobi" in t:
        opciones["metodo"] = "jacobi"
        return "metodos-iterativos", opciones
    if "seidel" in t or "gauss-seidel" in t or "iterativo" in t or "iterativos" in t:
        opciones["metodo"] = "gauss_seidel"
        return "metodos-iterativos", opciones

    return "resolver-sistema-lineal", opciones


# ----------------------------------------------------------------------------
# Generadores de LaTeX compatibles con KaTeX de Streamlit
# ----------------------------------------------------------------------------

def matriz_a_latex(M: list[list[Any]]) -> str:
    """Convierte una matriz 2D a sintaxis LaTeX pmatrix KaTeX-safe."""
    filas = [" & ".join(str(v) for v in fila) for fila in M]
    return "\\begin{pmatrix}\n" + " \\\\\n".join(filas) + "\n\\end{pmatrix}"


def vector_a_latex(v: list[Any]) -> str:
    """Convierte un vector 1D a sintaxis LaTeX pmatrix columna."""
    return "\\begin{pmatrix}\n" + " \\\\\n".join(str(x) for x in v) + "\n\\end{pmatrix}"


def sistema_a_latex(A: list[list[str]], b: list[str], variables: list[str]) -> str:
    """Genera representación del sistema con llave \\begin{cases} sin syntax bugs de KaTeX."""
    lineas_eq = []
    for fila, bi in zip(A, b):
        terminos = []
        for c_str, var in zip(fila, variables):
            c = a_fraccion_exacta(c_str)
            if c == 0:
                continue
            if not terminos:
                if c == 1:
                    terminos.append(f"{var}")
                elif c == -1:
                    terminos.append(f"-{var}")
                else:
                    terminos.append(f"{c}{var}")
            else:
                signo = "+" if c > 0 else "-"
                abs_c = abs(c)
                if abs_c == 1:
                    terminos.append(f"{signo} {var}")
                else:
                    terminos.append(f"{signo} {abs_c}{var}")
        lado_izq = " ".join(terminos) if terminos else "0"
        lineas_eq.append(f"{lado_izq} = {bi}")
    return "\\begin{cases}\n" + " \\\\\n".join(lineas_eq) + "\n\\end{cases}"
