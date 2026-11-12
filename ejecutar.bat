@echo off
setlocal
cd /d "%~dp0"
title Tutor de Sistemas de Ecuaciones

echo ========================================================
echo  Iniciando Tutor de Sistemas de Ecuaciones...
echo ========================================================

if not exist ".venv\Scripts\python.exe" (
    echo [AVISO] No se encontro el entorno virtual .venv.
    echo Ejecutando instalador...
    call "%~dp0instalar.bat"
)

if exist ".venv\Scripts\python.exe" (
    echo [OK] Entorno virtual detectado.
    echo Abriendo Streamlit en tu navegador...
    ".venv\Scripts\python.exe" -m streamlit run app.py --server.headless false
) else (
    echo [ERROR] No se pudo preparar el entorno virtual .venv.
    pause
)