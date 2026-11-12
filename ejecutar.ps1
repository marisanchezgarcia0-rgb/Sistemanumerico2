# Script de ejecución para PowerShell
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Iniciando Tutor de Sistemas de Ecuaciones..." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "[AVISO] No se encontró .venv. Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv .venv
    & .\.venv\Scripts\python.exe -m pip install -r requirements.txt
}

Write-Host "Activando entorno virtual e iniciando Streamlit..." -ForegroundColor Green
& .\.venv\Scripts\python.exe -m streamlit run app.py
