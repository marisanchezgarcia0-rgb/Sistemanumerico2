"""Punto de entrada principal de la aplicación en Streamlit.

Para iniciar la aplicación:
    streamlit run app.py
o use los scripts de ayuda:
    ejecutar.bat  (Windows)
    ./ejecutar.sh (Linux/macOS)
"""
from __future__ import annotations

import sys
from pathlib import Path

# Añadir src/ al path de módulos de forma relativa a este archivo
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st

# Verificación inicial de versión de Python recomendada
version_info = sys.version_info
if version_info.major == 3 and version_info.minor > 12:
    pass  # Continuar normalmente permitiendo ejecución en Python 3.13 / 3.14

from tutor_ecuaciones.interfaz import (
    inyectar_estilos,
    render_calculadora,
    render_chat,
    sidebar_control,
)

# Configuración de página de Streamlit
st.set_page_config(
    page_title="Tutor de Sistemas de Ecuaciones",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inyectar estilos modernos
inyectar_estilos()

# Barra lateral de control y navegación
control = sidebar_control()
modo_actual = control["modo"]
preferir_ia = control["preferir_ia"]
api_key_admin = control["api_key_admin"]

# Renderizado de la vista seleccionada
if modo_actual == "💬 Chat Tutor & Visión":
    render_chat(preferir_ia=preferir_ia, api_key_personal=api_key_admin)
elif modo_actual == "🧮 Calculadora Directa":
    render_calculadora()
