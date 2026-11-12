"""Vista de Calculadora Directa Determinista (Sin IA)."""
from __future__ import annotations

from typing import Any

import streamlit as st

from tutor_ecuaciones.explicacion import generar_explicacion_tutor
from tutor_ecuaciones.herramientas import calcular, parsear_matriz, parsear_vector
from tutor_ecuaciones.interfaz.componentes import mostrar_detalle_tecnico, render_header


def render_calculadora():
    """Renderiza la calculadora directa de álgebra lineal con explicación paso a paso."""
    render_header()
    st.markdown("### 🧮 Calculadora Directa de Álgebra Lineal")
    st.caption("Cálculos exactos con fracciones de la biblioteca estándar (soporta enteros, decimales y fracciones como `1/3`, `-5/2`).")

    col_skill, col_dim = st.columns([2, 1])
    with col_skill:
        skill = st.selectbox(
            "Método de resolución:",
            ["resolver-sistema-lineal", "regla-de-cramer", "matriz-inversa", "metodos-iterativos"],
            format_func=lambda s: {
                "resolver-sistema-lineal": "Gauss-Jordan (Solución Exacta)",
                "regla-de-cramer": "Regla de Cramer (Determinantes)",
                "matriz-inversa": "Matriz Inversa (A^-1)",
                "metodos-iterativos": "Métodos Iterativos (Jacobi / Gauss-Seidel)",
            }.get(s, s),
        )

    with col_dim:
        tamano = st.selectbox("Dimensiones predefinidas:", ["3x3", "2x2", "4x4", "Personalizado"], index=0)

    valores_def_A = {
        "2x2": "2 1\n1 -1",
        "3x3": "2 1 -1\n-3 -1 2\n-2 1 2",
        "4x4": "1 2 0 1\n0 1 1 0\n2 0 1 1\n1 1 0 2",
        "Personalizado": "2 1 -1\n-3 -1 2\n-2 1 2",
    }[tamano]

    valores_def_b = {
        "2x2": "3 1",
        "3x3": "8 -11 -3",
        "4x4": "4 2 5 3",
        "Personalizado": "8 -11 -3",
    }[tamano]

    col_A, col_b = st.columns([2, 1])
    with col_A:
        texto_A = st.text_area(
            "Matriz de Coeficientes A (una fila por línea, valores separados por espacio o coma):",
            valores_def_A,
            height=130,
        )
    with col_b:
        texto_b = st.text_input("Vector b (términos independientes):", valores_def_b)
        if skill == "matriz-inversa":
            st.caption("ℹ️ En matriz inversa, si deja b vacío solo se calculará $A^{-1}$.")

    opciones_iter: dict[str, Any] = {}
    if skill == "metodos-iterativos":
        c1, c2, c3 = st.columns(3)
        opciones_iter["metodo"] = c1.selectbox("Algoritmo:", ["gauss_seidel", "jacobi"], format_func=lambda m: "Gauss-Seidel" if m == "gauss_seidel" else "Jacobi")
        opciones_iter["tolerancia"] = c2.number_input("Tolerancia de error:", value=1e-6, format="%.1e")
        opciones_iter["max_iter"] = c3.number_input("Máximo de iteraciones:", value=100, min_value=1, step=10)

    if st.button("🚀 Calcular con Explicación de Tutor", type="primary"):
        try:
            A_mat = parsear_matriz(texto_A)
            b_vec = parsear_vector(texto_b) if (texto_b.strip() or skill != "matriz-inversa") else None
            num_cols = len(A_mat[0])
            variables = [f"x_{i+1}" for i in range(num_cols)]

            res = calcular(skill, A_mat, b_vec, **opciones_iter)
            explicacion = generar_explicacion_tutor(
                skill=skill,
                A_raw=A_mat,
                b_raw=b_vec,
                variables=variables,
                resultado=res,
                opciones=opciones_iter,
            )

            st.markdown("---")
            st.markdown(explicacion)
            mostrar_detalle_tecnico([{"skill": skill, "resultado": res}])

        except Exception as exc:
            st.error(f"❌ Error al procesar los datos de entrada: {exc}")
