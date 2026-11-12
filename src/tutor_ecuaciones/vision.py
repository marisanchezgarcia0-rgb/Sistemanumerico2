"""Módulo de Visión Multimodal con Gemini para digitalización de ejercicios manuscritos o impresos."""
from __future__ import annotations

import io
import json
import re
from typing import Any

from PIL import Image

from tutor_ecuaciones.claves import obtener_api_key
from tutor_ecuaciones.config import MODELO_VISION, MODELOS_DISPONIBLES, TIMEOUT_VISION_SEGUNDOS

PROMPT_VISION = """Eres un asistente experto en visión computacional y álgebra lineal.
Analiza con máxima precisión la imagen adjunta, que contiene un ejercicio o sistema de ecuaciones matemáticas (manuscrito o impreso).

Instrucciones:
1. Identifica todas las ecuaciones lineales o matrices visibles.
2. Transcribe el sistema en formato LaTeX limpio (ejemplo: \\begin{cases} 2x + y = 5 \\\\ x - y = 1 \\end{cases}).
3. Extrae la matriz de coeficientes A (como lista de listas de números/fracciones en texto, ej. [["2", "1"], ["1", "-1"]]).
4. Extrae el vector de términos independientes b (como lista de números en texto, ej. ["5", "1"]). Si solo piden calcular la inversa de A, b debe ser null.
5. Identifica el método solicitado si el enunciado lo indica ("resolver-sistema-lineal", "regla-de-cramer", "matriz-inversa", "metodos-iterativos"). Por defecto usa "resolver-sistema-lineal".
6. Proporciona una breve descripción del ejercicio detectado.

Debes responder ÚNICAMENTE un objeto JSON válido con la siguiente estructura:
{
  "encontrado": true,
  "descripcion": "Sistema de 3 ecuaciones lineales con 3 variables (x, y, z)",
  "metodo_sugerido": "resolver-sistema-lineal",
  "transcripcion_latex": "\\\\begin{cases} ... \\\\end{cases}",
  "variables": ["x", "y", "z"],
  "A": [["2", "1", "-1"], ["-3", "-1", "2"], ["-2", "1", "2"]],
  "b": ["8", "-11", "-3"],
  "observaciones": "La escritura es manuscrita clara."
}

Si la imagen no contiene ecuaciones matemáticas o no es legible:
{
  "encontrado": false,
  "descripcion": "No se pudieron detectar ecuaciones legibles en la imagen.",
  "metodo_sugerido": "resolver-sistema-lineal",
  "transcripcion_latex": "",
  "variables": [],
  "A": null,
  "b": null,
  "observaciones": "Asegúrese de enfocar bien y contar con buena iluminación."
}
"""


def procesar_imagen_ejercicio(
    imagen_input: bytes | Image.Image,
    api_key: str | None = None,
    modelo: str = MODELO_VISION,
    texto_adicional: str = "",
) -> dict[str, Any]:
    """Lee una imagen mediante Gemini Vision y extrae el sistema estructurado para confirmación previa."""
    clave = api_key or obtener_api_key()
    if not clave:
        return {
            "ok": False,
            "error": "No hay clave GEMINI_API_KEY configurada. Ingrésela en la barra lateral para utilizar la digitalización por visión.",
            "encontrado": False,
        }

    # Procesar bytes de la imagen
    if isinstance(imagen_input, Image.Image):
        buf = io.BytesIO()
        if imagen_input.mode in ("RGBA", "P"):
            imagen_input = imagen_input.convert("RGB")
        imagen_input.save(buf, format="JPEG", quality=90)
        datos_bytes = buf.getvalue()
        mime_type = "image/jpeg"
    elif isinstance(imagen_input, bytes):
        datos_bytes = imagen_input
        mime_type = "image/jpeg"
    else:
        return {"ok": False, "error": "Formato de imagen no compatible.", "encontrado": False}

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(
            api_key=clave,
            http_options={"timeout": TIMEOUT_VISION_SEGUNDOS * 1000},
        )
        part_imagen = types.Part.from_bytes(data=datos_bytes, mime_type=mime_type)

        prompt_final = PROMPT_VISION
        if texto_adicional:
            prompt_final += f"\n\nInstrucción complementaria del estudiante: {texto_adicional}"

        modelos_candidatos = list(dict.fromkeys([modelo, *MODELOS_DISPONIBLES]))
        ultimo_err = None

        for mod in list(dict.fromkeys(modelos_candidatos)):
            try:
                resp = client.models.generate_content(
                    model=mod,
                    contents=[part_imagen, prompt_final],
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        response_mime_type="application/json",
                    ),
                )
                texto_resp = resp.text or ""
                texto_resp = re.sub(r"^```(?:json)?\s*", "", texto_resp.strip(), flags=re.IGNORECASE)
                texto_resp = re.sub(r"\s*```$", "", texto_resp.strip())
                datos = json.loads(texto_resp)
                datos["ok"] = True
                datos["modelo_usado"] = mod
                return datos
            except Exception as e:
                ultimo_err = e
                continue

        return {
            "ok": False,
            "error": f"Fallo al procesar con Gemini Vision: {ultimo_err}",
            "encontrado": False,
        }

    except Exception as exc:
        return {
            "ok": False,
            "error": f"Error al inicializar cliente de visión: {type(exc).__name__}: {exc}",
            "encontrado": False,
        }
