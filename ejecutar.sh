#!/usr/bin/env bash
set -e

if [ ! -f ".venv/bin/activate" ]; then
    echo "[AVISO] No se encontró el entorno virtual .venv. Ejecutando instalación..."
    bash ./instalar.sh
fi

source .venv/bin/activate
echo "Iniciando Streamlit..."
streamlit run app.py
