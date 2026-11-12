"""Pruebas de configuración y políticas de seguridad del agente Antigravity."""
from types import SimpleNamespace

from google import genai

import tutor_ecuaciones.agente as agente
from tutor_ecuaciones.config import MODELOS_DISPONIBLES, TIMEOUT_GEMINI_SEGUNDOS
from tutor_ecuaciones.agente import crear_config_antigravity, responder_tutor


def test_agente_politicas_de_seguridad_estrictas():
    config = crear_config_antigravity(api_key="test_dummy_key")
    # Verificar que el agente bloquea la terminal por defecto: deny("*")
    politicas_deny = [p for p in config.policies if p.tool == "*" and "DENY" in str(p.decision)]
    assert len(politicas_deny) > 0

    # Verificar que solo permite las 4 herramientas y view_file
    tools_esperadas = ["resolver_lineal", "resolver_iterativo", "resolver_cramer", "calcular_inversa", "view_file"]
    tools_permitidas = [p.tool for p in config.policies if "APPROVE" in str(p.decision)]
    for t in tools_esperadas:
        assert t in tools_permitidas


def test_responder_tutor_modo_local_resiliente():
    # Mensaje algebraico sin IA forzada o sin clave debe responder con motor local exitosamente
    resultado = responder_tutor("Resuelve: 2x + y = 5; x - y = 1", preferir_ia=False)
    assert resultado["ok"] is True
    assert resultado["motor"] == "local"
    assert "Planteamiento del Problema" in resultado["texto"]
    assert "x = 2" in resultado["texto"] or "x_1 = 2" in resultado["texto"]


def test_gemini_usa_modelo_y_timeout_en_milisegundos(monkeypatch):
    observados = {}

    class FakeChats:
        def create(self, model, config):
            observados["modelo"] = model
            return SimpleNamespace(send_message=lambda mensaje: SimpleNamespace(text="Respuesta Gemini"))

    class FakeClient:
        def __init__(self, api_key, http_options):
            observados["timeout"] = http_options["timeout"]
            self.chats = FakeChats()

    monkeypatch.setattr(genai, "Client", FakeClient)

    resultado = agente._ejecutar_con_gemini_chat("Hola", "clave-de-prueba")

    assert observados["modelo"] == MODELOS_DISPONIBLES[0]
    assert observados["timeout"] == TIMEOUT_GEMINI_SEGUNDOS * 1000
    assert resultado["motor"] == "gemini"


def test_fallback_ia_muestra_aviso_sin_ocultar_motor_local(monkeypatch):
    def fallar(*args):
        raise RuntimeError("HTTP 403: clave de prueba rechazada")

    monkeypatch.setattr(agente, "_ejecutar_con_antigravity", fallar)
    monkeypatch.setattr(agente, "_ejecutar_con_gemini_chat", fallar)

    resultado = responder_tutor("Hola", api_key="clave de prueba", preferir_ia=True)

    assert resultado["motor"] == "local"
    assert "HTTP 403" in resultado["aviso"]
    assert "[clave redactada]" in resultado["aviso"]
    assert "clave de prueba" not in resultado["aviso"]


def test_fallo_de_todos_los_modelos_conserva_detalle(monkeypatch):
    class FakeChats:
        def create(self, model, config):
            raise ValueError(f"modelo no disponible: {model}")

    class FakeClient:
        def __init__(self, api_key, http_options):
            self.chats = FakeChats()

    monkeypatch.setattr(genai, "Client", FakeClient)

    try:
        agente._ejecutar_con_gemini_chat("Hola", "clave-de-prueba")
    except RuntimeError as exc:
        assert MODELOS_DISPONIBLES[-1] in str(exc)
        assert "modelo no disponible" in str(exc)
        assert isinstance(exc.__cause__, ValueError)
    else:
        raise AssertionError("Se esperaba un error cuando todos los modelos fallan")
