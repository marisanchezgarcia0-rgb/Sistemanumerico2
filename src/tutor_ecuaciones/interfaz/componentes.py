"""Componentes visuales reutilizables para Streamlit."""
from __future__ import annotations

import json
import os
from typing import Any

import streamlit as st

from tutor_ecuaciones.claves import obtener_api_key

CLAVE_ADMIN_DEFAULT = "admin123"


def render_header():
    """Muestra el banner superior estilizado."""
    st.markdown(
        """
        <div class="tutor-header">
            <h1>🧮 Tutor de Sistemas de Ecuaciones</h1>
            <p>Aprende Álgebra Lineal y Métodos Numéricos paso a paso con explicaciones didácticas,
               aritmética exacta con fracciones y soporte de visión para fotos de ejercicios.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge_motor(motor: str):
    """Muestra la insignia transparente que indica qué motor respondió."""
    if motor == "gemini":
        st.markdown(
            '<div class="badge-motor-ia">🤖 Respondió Gemini (Google AI)</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="badge-motor-local">⚙️ Respondió Motor Matemático Local (Exacto, Sin IA)</div>',
            unsafe_allow_html=True,
        )


def mostrar_detalle_tecnico(detalles: list[dict[str, Any]]):
    """Presenta el resultado técnico de las skills en un desplegable secundario."""
    if not detalles:
        return
    with st.expander("🔍 Detalle Técnico de los Cálculos (JSON de Skills)", expanded=False):
        for idx, item in enumerate(detalles, 1):
            skill = item.get("skill", "Cálculo")
            st.markdown(f"**Operación {idx}:** `{skill}`")
            res = item.get("resultado", {})
            st.code(json.dumps(res, indent=2, ensure_ascii=False), language="json")


def sidebar_control() -> dict[str, Any]:
    """Barra lateral con controles de navegación y panel de administración seguro."""
    with st.sidebar:
        st.markdown("### 🧭 Modo de Trabajo")
        modo = st.radio(
            "Seleccione una sección:",
            ["💬 Chat Tutor & Visión", "🧮 Calculadora Directa"],
            index=0,
        )

        st.divider()

        # Selector de motor preferido
        clave_detectada = bool(obtener_api_key())
        st.markdown("### ⚙️ Motor de Resolución")
        modo_preferido = st.toggle(
            "Preferir IA (Gemini)",
            value=clave_detectada,
            help="Si se desactiva o si falla la red, el sistema usará automáticamente el motor matemático exacto local.",
        )

        if clave_detectada:
            st.caption("🟢 Clave de Gemini activa.")
        else:
            st.caption("🟡 Sin clave configurada: operando 100% en Modo Local.")

        st.divider()

        # Panel de Administrador con contraseña para diagnósticos técnicos
        with st.expander("🔐 Configuración de Administrador", expanded=False):
            st.caption("Protegido para evitar cambios accidentales de los estudiantes.")
            clave_admin = st.text_input("Contraseña de Administrador", type="password", key="admin_pwd_input")
            password_esperada = os.environ.get("ADMIN_PASSWORD", CLAVE_ADMIN_DEFAULT)

            if clave_admin == password_esperada:
                st.success("Acceso concedido.")
                nueva_clave = st.text_input(
                    "Ingresar o cambiar GEMINI_API_KEY temporal:",
                    type="password",
                    value=st.session_state.get("admin_gemini_key", ""),
                    key="admin_gemini_input",
                )
                if st.button("Guardar clave temporal para esta sesión"):
                    if nueva_clave.strip():
                        st.session_state["admin_gemini_key"] = nueva_clave.strip()
                        st.success("Clave guardada en la sesión actual.")
                        st.rerun()

                st.markdown("---")
                st.caption("💡 Para configurar la clave permanentemente:")
                st.caption("- En local: defina `GEMINI_API_KEY` en su archivo `.env`")
                st.caption("- En Streamlit Cloud: agregue `GEMINI_API_KEY` en Settings -> Secrets")
            elif clave_admin:
                st.error("Contraseña incorrecta.")

        st.markdown("---")
        st.caption("© 2026 Tutor de Sistemas de Ecuaciones • Versión 2.0")

    return {
        "modo": modo,
        "preferir_ia": modo_preferido,
        "api_key_admin": st.session_state.get("admin_gemini_key"),
    }
