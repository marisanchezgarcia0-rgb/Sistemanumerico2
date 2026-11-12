"""Submódulo de motor matemático local y parseo algebraico determinista."""
from tutor_ecuaciones.motor_local.parser import (
    detectar_skill_solicitada,
    extraer_sistema_completo,
    matriz_a_latex,
    sistema_a_latex,
    vector_a_latex,
)

__all__ = [
    "detectar_skill_solicitada",
    "extraer_sistema_completo",
    "matriz_a_latex",
    "sistema_a_latex",
    "vector_a_latex",
]
