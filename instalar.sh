#!/usr/bin/env bash
set -e

echo "========================================================"
echo " Instalador del Tutor de Sistemas de Ecuaciones (Unix)"
echo "========================================================"

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 no está instalado o no se encuentra en el PATH."
    exit 1
fi

if [ ! -d ".venv" ]; then
    echo "[1/3] Creando entorno virtual .venv..."
    python3 -m venv .venv
else
    echo "[1/3] El entorno virtual .venv ya existe."
fi

echo "[2/3] Instalando dependencias..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[3/3] Configurando archivo .env..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Archivo .env creado desde .env.example."
fi

echo "========================================================"
echo " Instalación completada. Para ejecutar: ./ejecutar.sh"
echo "========================================================"
