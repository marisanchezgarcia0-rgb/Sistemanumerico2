@echo off
setlocal
cd /d "%~dp0"
title Instalador Tutor de Sistemas de Ecuaciones

echo ========================================================
echo  Instalador del Tutor de Sistemas de Ecuaciones
echo ========================================================

REM 1. Verificar si ya existe .venv
if exist ".venv\Scripts\python.exe" (
    echo [OK] El entorno virtual .venv ya esta creado.
    echo Actualizando dependencias...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    goto :env_check
)

REM 2. Buscar ejecutable de Python
set "PY_CMD="

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=py"
    goto :crear_venv
)

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :crear_venv
)

if exist "%APPDATA%\uv\python\cpython-3.14-windows-x86_64-none\python.exe" (
    set "PY_CMD=%APPDATA%\uv\python\cpython-3.14-windows-x86_64-none\python.exe"
    goto :crear_venv
)

echo [ERROR] No se encontro Python en el sistema.
echo Por favor instale Python desde https://www.python.org/downloads/
echo Asegurese de marcar la casilla 'Add python.exe to PATH' durante la instalacion.
pause
exit /b 1

:crear_venv
echo [1/3] Creando entorno virtual .venv con %PY_CMD%...
%PY_CMD% -m venv .venv
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo crear el entorno virtual.
    pause
    exit /b 1
)

echo [2/3] Instalando dependencias desde requirements.txt...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt

:env_check
echo [3/3] Configurando archivo .env...
if not exist ".env" (
    copy .env.example .env >nul
    echo Archivo .env creado.
)

echo.
echo ========================================================
echo  Instalacion completada con exito.
echo  Para iniciar la aplicacion haga doble clic en ejecutar.bat
echo ========================================================
pause