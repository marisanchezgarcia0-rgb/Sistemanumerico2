"""Estilos visuales modernos y limpios para la interfaz de Streamlit."""
from __future__ import annotations

import streamlit as st

CSS_GLOBAL = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Banner de encabezado principal */
.tutor-header {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 45%, #0f766e 100%);
    border-radius: 16px;
    padding: 24px 30px;
    color: #ffffff;
    margin-bottom: 22px;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.12);
}
.tutor-header h1 {
    font-size: 2.1rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.02em;
    display: flex;
    align-items: center;
    gap: 12px;
    color: #ffffff;
}
.tutor-header p {
    font-size: 0.96rem;
    opacity: 0.9;
    margin-top: 8px;
    margin-bottom: 0;
    line-height: 1.5;
}

/* Badges indicadoras del motor */
.badge-motor-ia {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    background: rgba(99, 102, 241, 0.18);
    color: #a5b4fc;
    border: 1px solid rgba(99, 102, 241, 0.35);
    margin-bottom: 8px;
}
.badge-motor-local {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 600;
    background: rgba(16, 185, 129, 0.18);
    color: #6ee7b7;
    border: 1px solid rgba(16, 185, 129, 0.35);
    margin-bottom: 8px;
}

/* Tarjeta interactiva de confirmación de visión */
.card-confirmacion-vision {
    background: #1e293b;
    border: 2px solid #6366f1;
    border-radius: 14px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.2);
}
</style>
"""


def inyectar_estilos():
    """Inyecta los estilos CSS en la página de Streamlit."""
    st.markdown(CSS_GLOBAL, unsafe_allow_html=True)
