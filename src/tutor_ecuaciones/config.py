"""Configuración global, constantes y rutas del sistema."""
from __future__ import annotations

from pathlib import Path

# Rutas del proyecto basadas en Path(__file__) sin sys.path.insert
PAQUETE_DIR = Path(__file__).resolve().parent
RAIZ_PROYECTO = PAQUETE_DIR.parents[1]
SKILLS_DIR = RAIZ_PROYECTO / "skills"
EJEMPLOS_DIR = RAIZ_PROYECTO / "ejemplos"
DOCS_DIR = RAIZ_PROYECTO / "docs"

# Modelos oficiales vigentes de Google Gemini
MODELO_DEFAULT = "gemini-3.5-flash-lite"
MODELO_LITE = "gemini-3.5-flash-lite"
MODELO_VISION = "gemini-3.5-flash"

MODELOS_DISPONIBLES = [
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-flash-lite-latest",
]

# Límites de sesión y timeouts
MAX_CARACTERES_ENTRADA = 3000
MAX_MENSAJES_SESION = 60
TIMEOUT_GEMINI_SEGUNDOS = 25
TIMEOUT_VISION_SEGUNDOS = 25
MAX_REINTENTOS_503 = 2
TIEMPO_BASE_ESPERA = 1.5

# Instrucción de sistema para el tutor en Antigravity y Gemini
INSTRUCCIONES_TUTOR = (
    "Eres un tutor universitario de Álgebra Lineal y Métodos Numéricos. Responde siempre en español, con calidez, rigor y claridad pedagógica.\n"
    "Dispones de cuatro herramientas de cálculo exacto: resolver_lineal, resolver_iterativo, resolver_cramer y calcular_inversa.\n"
    "REGLA CRÍTICA: NUNCA hagas operaciones aritméticas ni resuelvas ecuaciones por tu cuenta. Delega SIEMPRE el cálculo en la herramienta "
    "correspondiente pasando coeficientes como cadenas ('2', '-1.5', '1/3').\n"
    "Toda explicación debe estructurarse enseñando el porqué, mostrando matrices y fórmulas en LaTeX ($...$ para fórmulas y $$...$$ para bloques), "
    "interpretando el significado geométrico y ofreciendo comparar métodos."
)
