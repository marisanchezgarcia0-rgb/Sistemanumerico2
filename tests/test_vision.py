"""Pruebas de configuración de Gemini Vision sin llamadas de red."""
import json
from types import SimpleNamespace

from google import genai
from PIL import Image

from tutor_ecuaciones.config import MODELO_VISION, TIMEOUT_VISION_SEGUNDOS
from tutor_ecuaciones.vision import procesar_imagen_ejercicio


def test_vision_usa_modelo_actual_y_timeout_en_milisegundos(monkeypatch):
    observados = {}

    class FakeModels:
        def generate_content(self, model, contents, config):
            observados["modelo"] = model
            return SimpleNamespace(text=json.dumps({"encontrado": False}))

    class FakeClient:
        def __init__(self, api_key, http_options):
            observados["timeout"] = http_options["timeout"]
            self.models = FakeModels()

    monkeypatch.setattr(genai, "Client", FakeClient)

    resultado = procesar_imagen_ejercicio(
        Image.new("RGB", (2, 2)),
        api_key="clave-de-prueba",
    )

    assert observados["modelo"] == MODELO_VISION
    assert observados["timeout"] == TIMEOUT_VISION_SEGUNDOS * 1000
    assert resultado["ok"] is True
