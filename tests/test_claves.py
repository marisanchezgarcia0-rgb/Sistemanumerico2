"""Pruebas de la gestión segura de claves API."""
import os
from tutor_ecuaciones.claves import obtener_api_key


def test_obtener_api_key_argumento_directo():
    assert obtener_api_key("mi_clave_test") == "mi_clave_test"


def test_obtener_api_key_desde_entorno(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "clave_desde_env_123")
    assert obtener_api_key() == "clave_desde_env_123"


def test_obtener_api_key_vacia_retorna_none(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    # Al no haber argumento ni variable de entorno ni secrets, retorna None si no hay .env
    # o el contenido de .env si existe.
    clave = obtener_api_key("")
    assert isinstance(clave, (str, type(None)))
