"""Agente con Google Antigravity SDK y respaldo automático al Motor Local Resiliente."""
from __future__ import annotations

import asyncio
import concurrent.futures
import inspect
import logging
import time
from typing import Any

from tutor_ecuaciones.claves import obtener_api_key
from tutor_ecuaciones.config import (
    INSTRUCCIONES_TUTOR,
    MAX_CARACTERES_ENTRADA,
    MAX_REINTENTOS_503,
    MODELO_DEFAULT,
    MODELOS_DISPONIBLES,
    SKILLS_DIR,
    TIEMPO_BASE_ESPERA,
    TIMEOUT_GEMINI_SEGUNDOS,
)
from tutor_ecuaciones.explicacion import generar_explicacion_tutor
from tutor_ecuaciones.herramientas import HERRAMIENTAS, calcular
from tutor_ecuaciones.motor_local.parser import (
    detectar_skill_solicitada,
    extraer_sistema_completo,
)

logger = logging.getLogger("tutor_ecuaciones.agente")


def _resumir_error(exc: Exception, clave: str | None = None) -> str:
    """Reduce un error técnico a una línea y evita mostrar una clave API."""
    detalle = " ".join(str(exc).split())
    if clave:
        detalle = detalle.replace(clave, "[clave redactada]")
    return detalle[:497] + "..." if len(detalle) > 500 else detalle


def _normalizar_latex_streamlit(texto: str) -> str:
    """Convierte delimitadores \\[ \\] y \\( \\) a $$ $$ y $ $ compatibles con Streamlit KaTeX."""
    import re
    texto = re.sub(r"\\\[(.*?)\\\]", lambda m: f"\n$$\n{m.group(1).strip()}\n$$\n", texto, flags=re.DOTALL)
    texto = re.sub(r"\\\((.*?)\\\)", lambda m: f"${m.group(1).strip()}$", texto, flags=re.DOTALL)
    return texto


def _armar_prompt_con_historial(mensaje: str, historial: list[dict] | None) -> str:
    """Incluye los últimos turnos de la conversación para mantener contexto en preguntas de seguimiento."""
    if not historial:
        return mensaje
    turnos = []
    for m in historial[-6:]:
        rol = "Estudiante" if m.get("role") == "user" else "Tutor"
        contenido = str(m.get("content", ""))[:600]
        if contenido:
            turnos.append(f"{rol}: {contenido}")
    if not turnos:
        return mensaje
    return "Historial reciente de la conversación:\n" + "\n".join(turnos) + "\n\nNueva consulta del estudiante:\n" + mensaje


def crear_config_antigravity(api_key: str | None = None, modelo: str = MODELO_DEFAULT):
    """Crea la configuración estricta de seguridad requerida para Google Antigravity SDK."""
    from google.antigravity import CapabilitiesConfig, LocalAgentConfig
    from google.antigravity.hooks.policy import allow, deny
    from google.antigravity.types import BuiltinTools

    clave = api_key or obtener_api_key()
    return LocalAgentConfig(
        model=modelo,
        api_key=clave,
        system_instructions=INSTRUCCIONES_TUTOR,
        skills_paths=[str(SKILLS_DIR)],
        tools=HERRAMIENTAS,
        capabilities=CapabilitiesConfig(enabled_tools=BuiltinTools.read_only()),
        policies=[deny("*"), allow("view_file"), *[allow(f.__name__) for f in HERRAMIENTAS]],
    )


def resolver_con_motor_local(mensaje: str) -> dict[str, Any]:
    """Resuelve el sistema algebraico de forma 100% determinista sin llamadas a la IA."""
    A, b, variables = extraer_sistema_completo(mensaje)

    if not A:
        # Pregunta conceptual o saludo
        bienvenida = (
            "👋 **¡Hola! Soy tu Tutor de Álgebra Lineal y Métodos Numéricos.**\n\n"
            "Puedo ayudarte a resolver sistemas de ecuaciones paso a paso, calcular matrices inversas, "
            "aplicar la regla de Cramer o métodos iterativos como Jacobi y Gauss-Seidel.\n\n"
            "💡 **Ejemplos de cómo puedes escribirme:**\n"
            "- *Resuelve: 2x + y - z = 8; -3x - y + 2z = -11; -2x + y + 2z = -3*\n"
            "- *Resuelve por Cramer: x + y = 3; x - y = 1*\n"
            "- *Calcula la inversa de [[2,1],[5,3]]*\n"
            "- *Resuelve por Gauss-Seidel: 4x + y + z = 6; x + 5y + 2z = 8; x + 2y + 6z = 9*\n\n"
            "📸 También puedes **subir una foto o captura** de tu ejercicio con el botón superior."
        )
        return {
            "texto": bienvenida,
            "detalles": [],
            "motor": "local",
            "ok": True,
        }

    skill, opciones = detectar_skill_solicitada(mensaje, A)
    res = calcular(skill, A, b, **opciones)
    vars_usadas = variables or [f"x{i+1}" for i in range(len(A[0]))]

    explicacion_didactica = generar_explicacion_tutor(
        skill=skill,
        A_raw=A,
        b_raw=b,
        variables=vars_usadas,
        resultado=res,
        opciones=opciones,
    )

    return {
        "texto": explicacion_didactica,
        "detalles": [{"skill": skill, "resultado": res, "A": A, "b": b}],
        "motor": "local",
        "ok": res.get("ok", True),
    }


async def _ejecutar_con_antigravity(
    mensaje: str,
    clave: str,
    historial: list[dict] | None = None,
) -> dict[str, Any]:
    """Ejecuta el agente usando el SDK oficial de Google Antigravity."""
    from google.antigravity import Agent

    prompt = _armar_prompt_con_historial(mensaje, historial)
    ultimo_error = None

    for mod in MODELOS_DISPONIBLES[:2]:
        try:
            config = crear_config_antigravity(api_key=clave, modelo=mod)
            async with Agent(config) as agente:
                respuesta = await asyncio.wait_for(
                    agente.chat(prompt),
                    timeout=TIMEOUT_GEMINI_SEGUNDOS,
                )
                texto_raw = await respuesta.text() if respuesta else ""
                texto = _normalizar_latex_streamlit(texto_raw)

                # Enriquecer con las 6 secciones pedagógicas deterministas si hay sistema numérico
                A, b, v = extraer_sistema_completo(mensaje)
                detalles = []
                if A:
                    skill, opts = detectar_skill_solicitada(mensaje, A)
                    res = calcular(skill, A, b, **opts)
                    detalles.append({"skill": skill, "resultado": res, "A": A, "b": b})
                    vars_u = v or [f"x{i+1}" for i in range(len(A[0]))]
                    explicacion = generar_explicacion_tutor(skill, A, b, vars_u, res, opts)
                    texto_completo = f"{texto}\n\n---\n\n{explicacion}" if texto.strip() else explicacion
                else:
                    texto_completo = texto

                return {
                    "texto": texto_completo,
                    "detalles": detalles,
                    "motor": "gemini",
                    "ok": True,
                }
        except Exception as exc:
            ultimo_error = exc
            continue

    raise RuntimeError(f"Fallo en Antigravity: {ultimo_error}")


def _ejecutar_con_gemini_chat(
    mensaje: str,
    clave: str,
    historial: list[dict] | None = None,
) -> dict[str, Any]:
    """Ejecuta el tutor IA mediante Gemini con ejecución automática de herramientas y formato didáctico."""
    from google import genai
    from google.genai import types

    client = genai.Client(
        api_key=clave,
        http_options={"timeout": TIMEOUT_GEMINI_SEGUNDOS * 1000},
    )
    prompt = _armar_prompt_con_historial(mensaje, historial)
    modelos_a_probar = MODELOS_DISPONIBLES
    ultimo_error = None
    ultimo_mod = None

    for mod in modelos_a_probar:
        ultimo_mod = mod
        try:
            config = types.GenerateContentConfig(
                temperature=0.2,
                system_instruction=INSTRUCCIONES_TUTOR,
                tools=HERRAMIENTAS,
            )
            chat = client.chats.create(model=mod, config=config)
            resp = chat.send_message(prompt)
            texto_resp = _normalizar_latex_streamlit(resp.text or "")

            A, b, v = extraer_sistema_completo(mensaje)
            detalles = []
            if A:
                skill, opts = detectar_skill_solicitada(mensaje, A)
                res = calcular(skill, A, b, **opts)
                detalles.append({"skill": skill, "resultado": res, "A": A, "b": b})
                vars_u = v or [f"x{i+1}" for i in range(len(A[0]))]
                explicacion = generar_explicacion_tutor(skill, A, b, vars_u, res, opts)
                texto_resp = f"{texto_resp}\n\n---\n\n{explicacion}" if texto_resp.strip() else explicacion

            return {
                "texto": texto_resp,
                "detalles": detalles,
                "motor": "gemini",
                "ok": True,
            }
        except Exception as exc:
            ultimo_error = exc
            continue

    raise RuntimeError(
        f"Falló el modelo {ultimo_mod}: {type(ultimo_error).__name__}: {ultimo_error}"
    ) from ultimo_error


def responder_tutor(
    mensaje: str,
    historial: list[dict] | None = None,
    api_key: str | None = None,
    preferir_ia: bool = True,
) -> dict[str, Any]:
    """Función de entrada principal consumida por la interfaz de Streamlit.

    Garantiza:
    1. Transparencia: retorna si respondió 'gemini' o 'local'.
    2. Resiliencia: si la red falla, hay 503 o falta la clave, conmuta sin errores al motor local.
    3. Nunca lanza excepciones no capturadas al usuario.
    """
    mensaje_limpio = mensaje.strip()[:MAX_CARACTERES_ENTRADA]
    if not mensaje_limpio:
        return {
            "texto": "Por favor ingrese un mensaje o sistema de ecuaciones para resolver.",
            "detalles": [],
            "motor": "local",
            "ok": False,
        }

    clave = api_key or obtener_api_key()

    motivo_fallback = None
    if preferir_ia and not clave:
        motivo_fallback = "No se encontró GEMINI_API_KEY; se utilizó el motor local."
    elif preferir_ia:
        # 1. Intentar con Antigravity SDK
        try:
            res_o_coro = _ejecutar_con_antigravity(mensaje_limpio, clave, historial)
            if inspect.iscoroutine(res_o_coro):
                try:
                    asyncio.get_running_loop()
                    # Si ya existe un loop activo (p. ej. Streamlit/Tornado), aislar en hilo
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                        return pool.submit(asyncio.run, res_o_coro).result()
                except RuntimeError:
                    return asyncio.run(res_o_coro)
            return res_o_coro
        except Exception as exc_antigravity:
            logger.info(
                "Antigravity SDK no disponible, usando Gemini Chat con tools: %s",
                _resumir_error(exc_antigravity, clave),
            )

        # 2. Respaldo directo con Gemini Chat + Function Calling (tools) con reintento ante 503
        for intento in range(MAX_REINTENTOS_503 + 1):
            try:
                return _ejecutar_con_gemini_chat(mensaje_limpio, clave, historial)
            except Exception as exc_gemini:
                detalle_error = _resumir_error(exc_gemini, clave)
                if ("503" in detalle_error or "unavailable" in detalle_error.lower()) and intento < MAX_REINTENTOS_503:
                    time.sleep(TIEMPO_BASE_ESPERA * (2 ** intento))
                    continue
                logger.warning("Fallo en Gemini API: %s", detalle_error)
                motivo_fallback = (
                    f"Gemini no pudo responder: {detalle_error or type(exc_gemini).__name__}. "
                    "Se utilizó el motor local."
                )
                break

    # 3. Respaldo resiliente automático e inmediato al motor local
    res_local = resolver_con_motor_local(mensaje_limpio)
    if motivo_fallback:
        res_local["aviso"] = motivo_fallback
    return res_local
