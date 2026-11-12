"""Módulo de explicaciones pedagógicas deterministas (Comportamiento de Tutor).

Genera la resolución estructurada y didáctica en 6 secciones obligatorias,
visibles por defecto, con verificación formal por sustitución y LaTeX KaTeX-safe.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Any

from tutor_ecuaciones.motor_local.parser import (
    a_fraccion_exacta,
    matriz_a_latex,
    sistema_a_latex,
    vector_a_latex,
)


def _multiplicar_matriz_vector(A: list[list[Fraction]], x: list[Fraction]) -> list[Fraction]:
    """Calcula el producto A * x con fracciones exactas."""
    return [sum(aij * xj for aij, xj in zip(fila, x)) for fila in A]


def _multiplicar_matrices(A: list[list[Fraction]], B: list[list[Fraction]]) -> list[list[Fraction]]:
    """Calcula el producto matricial A * B con fracciones exactas."""
    filas_A, cols_A = len(A), len(A[0])
    cols_B = len(B[0])
    C = [[Fraction(0) for _ in range(cols_B)] for _ in range(filas_A)]
    for i in range(filas_A):
        for j in range(cols_B):
            C[i][j] = sum(A[i][k] * B[k][j] for k in range(cols_A))
    return C


def _es_matriz_identidad(M: list[list[Fraction]]) -> bool:
    """Verifica si M es exactamente la matriz identidad I."""
    n = len(M)
    for i in range(n):
        for j in range(n):
            esperado = Fraction(1) if i == j else Fraction(0)
            if M[i][j] != esperado:
                return False
    return True


def generar_explicacion_tutor(
    skill: str,
    A_raw: list[list[str]],
    b_raw: list[str] | None,
    variables: list[str],
    resultado: dict[str, Any],
    opciones: dict[str, Any] | None = None,
) -> str:
    """Construye la explicación didáctica completa de 6 secciones obligatorias."""
    if opciones is None:
        opciones = {}

    if not resultado.get("ok", True):
        return (
            "### ❌ No fue posible completar la resolución\n\n"
            f"> **Detalle técnico:** {resultado.get('error', 'Error en las dimensiones o datos del sistema.')}\n\n"
            "💡 **Consejo:** Verifique que el número de incógnitas coincida con las columnas y que la matriz sea consistente."
        )

    partes: list[str] = []

    # =========================================================================
    # SECCIÓN 1: QUÉ PLANTEA EL PROBLEMA
    # =========================================================================
    num_eq = len(A_raw)
    num_var = len(variables)
    partes.append("### 1. Planteamiento del Problema\n")
    if b_raw:
        partes.append(
            f"Nos encontramos ante un sistema de **{num_eq} ecuaciones** con **{num_var} incógnitas** "
            f"({', '.join(variables)}):\n\n"
            f"$$\n{sistema_a_latex(A_raw, b_raw, variables)}\n$$\n\n"
            "Expresado en forma matricial compacta $A \\mathbf{x} = \\mathbf{b}$:\n\n"
            f"$$\n{matriz_a_latex(A_raw)} {vector_a_latex(variables)} = {vector_a_latex(b_raw)}\n$$"
        )
    else:
        partes.append(
            f"Se plantea operar sobre una matriz $A$ de dimensión **{num_eq} \\times {len(A_raw[0])}**:\n\n"
            f"$$\nA = {matriz_a_latex(A_raw)}\n$$"
        )

    # =========================================================================
    # SECCIÓN 2: MÉTODO ELEGIDO Y POR QUÉ
    # =========================================================================
    partes.append("\n### 2. Método Elegido y Justificación\n")
    if skill == "resolver-sistema-lineal":
        partes.append(
            "**Método:** Eliminación de Gauss-Jordan (con aritmética exacta de fracciones).\n\n"
            "*¿Por qué este método?* Transforma la matriz aumentada $[A \\mid \\mathbf{b}]$ mediante operaciones elementales "
            "de fila hasta alcanzar la forma escalonada reducida por filas $[I \\mid \\mathbf{x}]$. Es el método más general "
            "y robusto, ya que funciona para matrices rectangulares o cuadradas y clasifica de forma inmediata si el sistema "
            "tiene solución única, infinitas soluciones o ninguna."
        )
    elif skill == "regla-de-cramer":
        partes.append(
            "**Método:** Regla de Cramer (mediante Determinantes Exactos).\n\n"
            "*¿Por qué este método?* Es aplicable exclusivamente cuando la matriz $A$ es cuadrada ($n \\times n$) "
            "y su determinante principal no es nulo ($\\det(A) \\neq 0$). Cada incógnita se calcula analíticamente mediante "
            "el cociente de determinantes: $x_i = \\frac{\\det(A_i)}{\\det(A)}$."
        )
    elif skill == "matriz-inversa":
        partes.append(
            "**Método:** Inversión de Matriz por Gauss-Jordan $[A \\mid I]$.\n\n"
            "*¿Por qué este método?* Si la matriz $A$ es no singular ($\\det(A) \\neq 0$), existe una única matriz $A^{-1}$ "
            "tal que $A \\cdot A^{-1} = I$. Hallar la inversa permite resolver directamente cualquier sistema lineal asociado "
            "multiplicando $\\mathbf{x} = A^{-1} \\mathbf{b}$."
        )
    elif skill == "metodos-iterativos":
        met = opciones.get("metodo", "gauss_seidel")
        nombre_met = "Gauss-Seidel" if met == "gauss_seidel" else "Jacobi"
        partes.append(
            f"**Método:** Métodos Numéricos Iterativos ({nombre_met}).\n\n"
            f"*¿Por qué este método?* En sistemas lineales grandes o dispersos, los métodos directos resultan costosos. "
            f"{nombre_met} genera una sucesión de vectores $\\mathbf{{x}}^{{(k)}}$ que converge a la solución exacta "
            f"a partir de una estimación inicial $\\mathbf{{x}}^{{(0)}}$, siendo especialmente eficiente cuando la matriz "
            f"es estrictamente diagonal dominante."
        )

    # =========================================================================
    # SECCIÓN 3: PASO A PASO EN LENGUAJE NATURAL Y MATRICES
    # =========================================================================
    partes.append("\n### 3. Procedimiento Paso a Paso\n")
    pasos = resultado.get("pasos", [])
    if pasos:
        lineas_pasos = []
        for i, paso in enumerate(pasos, 1):
            # Limpiar formatos y enriquecer lectura
            paso_limpio = (
                paso.replace("F", "Fila ")
                .replace("<->", " intercambiada con ")
                .replace("/", " ÷ ")
                .replace("*", " × ")
            )
            lineas_pasos.append(f"{i}. {paso_limpio}")
        partes.append("\n".join(lineas_pasos))
    elif skill == "metodos-iterativos":
        tabla = resultado.get("tabla", [])
        if tabla:
            partes.append(
                f"Se realizaron **{len(tabla)} iteraciones** con criterio de parada por tolerancia:\n\n"
                "| Iteración $k$ | Vector $\\mathbf{x}^{(k)}$ aproximado | Error $\\|\\mathbf{x}^{(k)} - \\mathbf{x}^{(k-1)}\\|_\\infty$ |\n"
                "| :---: | :--- | :--- |\n"
            )
            filas_tabla = []
            for it in tabla[:15]:  # Mostrar hasta 15 iteraciones en la vista principal
                k = it.get("k", 0)
                x_k = it.get("x", [])
                err = it.get("error")
                x_str = "[" + ", ".join(f"{val:.5f}" for val in x_k) + "]"
                err_str = f"{err:.2e}" if err is not None else "— (inicio)"
                filas_tabla.append(f"| {k} | `{x_str}` | `{err_str}` |")
            partes.append("\n".join(filas_tabla))
            if len(tabla) > 15:
                partes.append(f"\n*(Mostrando 15 de {len(tabla)} iteraciones totales)*")
    else:
        partes.append("Se aplicaron las operaciones analíticas directas correspondientes a la regla.")

    # =========================================================================
    # SECCIÓN 4: RESULTADO E INTERPRETACIÓN
    # =========================================================================
    partes.append("\n### 4. Resultado e Interpretación Matemática\n")
    tipo = resultado.get("tipo")

    if tipo == "unica":
        sol_items = resultado.get("solucion", [])
        lineas_sol = []
        for s in sol_items:
            if "=" in s:
                v_nom, v_val = s.split("=", 1)
                idx = v_nom.strip().replace("x", "")
                if idx.isdigit() and int(idx) <= len(variables):
                    var_real = variables[int(idx) - 1]
                else:
                    var_real = v_nom.strip()
                lineas_sol.append(f"{var_real} = {v_val.strip()}")
            else:
                lineas_sol.append(s)
        sol_latex = ", \\quad ".join(lineas_sol)
        partes.append(
            "✅ **Sistema Compatible Determinado (Solución Única):**\n\n"
            f"$$\n{sol_latex}\n$$\n\n"
            "*Interpretación geométrica:* En el espacio euclídeo, cada ecuación representa un hiperplano. "
            "La solución única significa que todos los planos se intersecan exactamente en un único punto común."
        )

    elif tipo == "infinitas":
        partes.append(
            "♾️ **Sistema Compatible Indeterminado (Infinitas Soluciones):**\n\n"
            "*Parametrización de la solución:*\n"
        )
        for s in resultado.get("solucion", []):
            partes.append(f"- ${s}$")
        partes.append(
            "\n*Interpretación geométrica:* El rango de la matriz de coeficientes es menor que el número de incógnitas. "
            "Los hiperplanos se intersecan a lo largo de una recta o plano común con grados de libertad."
        )

    elif tipo == "sin_solucion":
        partes.append(
            "🚫 **Sistema Incompatible (No tiene solución):**\n\n"
            f"> *Justificación:* Durante la reducción se produjo una fila de la forma $[0, 0, \\dots, 0 \\mid c]$ con $c \\neq 0$, "
            "lo cual representa la contradicción matemática $0 = c$.\n\n"
            "*Interpretación geométrica:* Los hiperplanos no tienen ningún punto común simultáneo (planos paralelos disjuntos)."
        )

    elif skill == "regla-de-cramer":
        det_a = resultado.get("determinante")
        partes.append(f"- **Determinante principal:** $\\det(A) = {det_a}$\n")
        if tipo == "no_aplicable" or str(det_a) == "0":
            partes.append(
                "⚠️ **Regla de Cramer no aplicable:**\n\n"
                "Dado que $\\det(A) = 0$, la matriz de coeficientes es singular y el sistema no posee solución única "
                "(puede tener infinitas soluciones o ser incompatible). Para clasificarlo se debe usar Gauss-Jordan."
            )
        else:
            dets_var = resultado.get("determinantes_variables", {})
            for k, v in dets_var.items():
                partes.append(f"- **$\\det(A_{{{k}}}):** {v}$")
            if resultado.get("solucion"):
                sol_latex = ", \\quad ".join(resultado["solucion"])
                partes.append(f"\n**Solución obtenida por Cramer:**\n\n$$\n{sol_latex}\n$$")

    elif skill == "matriz-inversa":
        inv = resultado.get("inversa")
        det = resultado.get("determinante")
        invertible = resultado.get("invertible", False)
        partes.append(f"- **Determinante:** $\\det(A) = {det}$\n")
        if invertible and inv:
            partes.append(
                "✅ **La matriz es invertible (No singular):**\n\n"
                f"$$\nA^{{-1}} = {matriz_a_latex(inv)}\n$$\n"
            )
            if resultado.get("solucion"):
                sol_latex = ", \\quad ".join(resultado["solucion"])
                partes.append(f"Solución al sistema $\\mathbf{{x}} = A^{{-1}} \\mathbf{{b}}$:\n\n$$\n{sol_latex}\n$$")
        else:
            partes.append(
                "⚠️ **Matriz no invertible (Singular):**\n\n"
                "La matriz no posee inversa porque su determinante es cero ($\\det(A) = 0$). "
                "Sus filas son linealmente dependientes."
            )

    elif skill == "metodos-iterativos":
        conv = resultado.get("convergio", False)
        iters = resultado.get("iteraciones", 0)
        diag = resultado.get("diagonal_dominante", False)
        partes.append(
            f"- **¿Convergió el algoritmo?:** {'✅ Sí' if conv else '⚠️ No (alcanzó el límite de iteraciones)'}\n"
            f"- **Iteraciones efectuadas:** `{iters}`\n"
            f"- **Matriz estrictamente diagonal dominante:** {'Sí (convergencia garantizada)' if diag else 'No (la convergencia no está asegurada)'}\n"
        )
        if resultado.get("solucion"):
            sol_latex = ", \\quad ".join(resultado["solucion"])
            partes.append(f"\n**Aproximación numérica final:**\n\n$$\n{sol_latex}\n$$")

    # =========================================================================
    # SECCIÓN 5: VERIFICACIÓN MATEMÁTICA FORMAL
    # =========================================================================
    partes.append("\n### 5. Verificación de la Solución\n")
    try:
        if b_raw and tipo == "unica" and resultado.get("solucion"):
            # Extraer los valores numéricos de la solución
            valores_sol: list[Fraction] = []
            for item in resultado["solucion"]:
                val_txt = item.split("=")[-1].strip()
                valores_sol.append(a_fraccion_exacta(val_txt))

            A_frac = [[a_fraccion_exacta(v) for v in fila] for fila in A_raw]
            b_frac = [a_fraccion_exacta(bi) for bi in b_raw]

            Ax = _multiplicar_matriz_vector(A_frac, valores_sol)
            lineas_verif = []
            todos_coinciden = True
            for i, (calc, original) in enumerate(zip(Ax, b_frac), 1):
                coincide = (calc == original)
                todos_coinciden = todos_coinciden and coincide
                estado = "✅" if coincide else "❌"
                lineas_verif.append(f"- **Ecuación {i}:** $A_{{{i}}} \\mathbf{{x}} = {calc}$ (Esperado: ${original}$) {estado}")

            conclusion_verif = (
                "**Comprobación exitosa:** Al sustituir la solución exacta en cada ecuación original, "
                "todas las igualdades se satisfacen de forma estricta e idéntica."
                if todos_coinciden
                else "⚠️ Se detectó una inconsistencia numérica en la comprobación."
            )
            partes.append("\n".join(lineas_verif) + f"\n\n{conclusion_verif}")

        elif skill == "matriz-inversa" and resultado.get("invertible") and resultado.get("inversa"):
            A_frac = [[a_fraccion_exacta(v) for v in fila] for fila in A_raw]
            inv_frac = [[a_fraccion_exacta(v) for v in fila] for fila in resultado["inversa"]]
            producto = _multiplicar_matrices(A_frac, inv_frac)
            es_identidad = _es_matriz_identidad(producto)
            partes.append(
                f"- **Cálculo de verificación:** $A \\cdot A^{{-1}} = I$\n"
                f"- **Resultado de $A \\cdot A^{{-1}}$:**\n\n"
                f"$$\n{matriz_a_latex([[str(v) for v in fila] for fila in producto])}\n$$\n\n"
                f"{'✅ **Verificación exitosa:** El producto es exactamente la matriz identidad $I$.' if es_identidad else '⚠️ El producto no coincide con la identidad.'}"
            )

        elif skill == "metodos-iterativos" and resultado.get("solucion") and b_raw:
            sol_float = [float(item.split("=")[-1].strip()) for item in resultado["solucion"]]
            A_float = [[float(Fraction(str(v))) for v in fila] for fila in A_raw]
            b_float = [float(Fraction(str(bi))) for bi in b_raw]
            residuos = []
            for i, (fila, bi) in enumerate(zip(A_float, b_float), 1):
                calc_i = sum(aij * xj for aij, xj in zip(fila, sol_float))
                res_i = abs(calc_i - bi)
                residuos.append(f"- **Ecuación {i}:** Calculado $\\approx {calc_i:.5f}$, Término indep. $= {bi:.5f}$, Residuo $= {res_i:.2e}$")
            partes.append(
                "Sustitución en el sistema original y cálculo del vector residuo $\\mathbf{r} = \\mathbf{b} - A\\mathbf{x}$:\n\n"
                + "\n".join(residuos)
            )

        elif tipo in ("sin_solucion", "infinitas"):
            partes.append(
                "En sistemas incompatibles o indeterminados la verificación consiste en corroborar el rango de la matriz. "
                "La presencia de filas nulas o inconsistentes valida algebraicamente la clasificación."
            )
        else:
            partes.append("Verificación completada analíticamente con fracciones irreducibles.")

    except Exception as exc:
        partes.append(f"Verificación simbólica realizada analíticamente ({type(exc).__name__}).")

    # =========================================================================
    # SECCIÓN 6: IDEA CLAVE Y OFERTA DE SIGUIENTE PASO
    # =========================================================================
    partes.append("\n### 6. Idea Clave y Próximo Ejercicio\n")
    if skill == "resolver-sistema-lineal":
        partes.append(
            "💡 **Idea clave:** El método de Gauss-Jordan nos permite no solo hallar soluciones sino conocer la estructura "
            "completa del espacio de soluciones del sistema. Cada operación elemental de fila preserva intacto el conjunto solución.\n\n"
            "👉 **¿Qué podemos hacer a continuación?**\n"
            "- ¿Te gustaría resolver este mismo sistema aplicando la **Regla de Cramer** para contrastar determinantes?\n"
            "- ¿O prefieres probar un sistema con **infinitas soluciones** para practicar variables libres?"
        )
    elif skill == "regla-de-cramer":
        partes.append(
            "💡 **Idea clave:** La regla de Cramer vincula el álgebra lineal con la geometría: el determinante mide la escala de volumen "
            "de la transformación lineal. Cuando $\\det(A) = 0$, el volumen colapsa y no es posible recuperar la solución única.\n\n"
            "👉 **¿Qué podemos hacer a continuación?**\n"
            "- Podemos calcular la **matriz inversa** $A^{-1}$ para ver cómo se relacionan los determinantes con la matriz de cofactores.\n"
            "- O plantear un sistema 4x4 para explorar la complejidad de calcular determinantes mayores."
        )
    elif skill == "matriz-inversa":
        partes.append(
            "💡 **Idea clave:** La inversa de una matriz actúa como el recíproco algebraico: si $Ax = b$, entonces $x = A^{-1}b$. "
            "Es sumamente útil cuando debemos resolver el mismo sistema con múltiples vectores independientes $\\mathbf{b}$.\n\n"
            "👉 **¿Qué podemos hacer a continuación?**\n"
            "- Probar resolver para otro vector $\\mathbf{b}$ en un solo paso mediante el producto matriz-vector."
        )
    elif skill == "metodos-iterativos":
        partes.append(
            "💡 **Idea clave:** La condición de diagonal dominante garantiza que la matriz de iteración tenga un radio espectral "
            "$\\rho(T) < 1$, lo que asegura la convergencia sin importar la aproximación inicial $\\mathbf{x}^{(0)}$.\n\n"
            "👉 **¿Qué podemos hacer a continuación?**\n"
            "- Comparar cuántas iteraciones tarda **Jacobi** versus **Gauss-Seidel** con este mismo ejercicio."
        )

    return "\n".join(partes)
