"""Gestión segura y de solo lectura de credenciales de la API de Gemini."""
from __future__ import annotations

import os
from pathlib import Path
from tutor_ecuaciones.config import RAIZ_PROYECTO


def _leer_archivo_env(ruta: Path) -> str | None:
    """Lee una variable de un archivo .env sin escribir ni modificar nada en disco."""
    if not ruta.is_file():
        return None
    try:
        contenido = ruta.read_text(encoding="utf-8")
        for linea in contenido.splitlines():
            linea = linea.strip()
            if linea and not linea.startswith("#") and "=" in linea:
                clave, valor = linea.split("=", 1)
                if clave.strip() == "GEMINI_API_KEY":
                    val_limpio = valor.strip().strip('"').strip("'")
                    if val_limpio:
                        return val_limpio
    except Exception:
        pass
    return None


def obtener_api_key(clave_usuario: str | None = None) -> str | None:
    """Obtiene la clave API de Gemini siguiendo el orden de precedencia estricto:

    1. Clave pasada explícitamente como argumento (por ejemplo desde la UI).
    2. Variable de entorno del sistema operativo (os.environ["GEMINI_API_KEY"]).
    3. st.secrets de Streamlit Cloud (Settings -> Secrets).
    4. Archivo .env en la raíz del proyecto (solo lectura con codificación UTF-8).

    NUNCA escribe archivos ni expone claves en logs.
    """
    if clave_usuario and clave_usuario.strip():
        return clave_usuario.strip()

    # 1. Variable de entorno
    env_val = os.environ.get("GEMINI_API_KEY")
    if env_val and env_val.strip():
        return env_val.strip()

    # 2. st.secrets (solo si Streamlit está activo con Runtime/ScriptRunContext)
    try:
        import sys
        if "streamlit" in sys.modules:
            import streamlit as st
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            if get_script_run_ctx() is not None and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                sec_val = st.secrets["GEMINI_API_KEY"]
                if sec_val and str(sec_val).strip():
                    return str(sec_val).strip()
    except Exception:
        pass

    # 3. Archivo .env en la raíz
    env_archivo = RAIZ_PROYECTO / ".env"
    val_archivo = _leer_archivo_env(env_archivo)
    if val_archivo:
        return val_archivo

    return None
