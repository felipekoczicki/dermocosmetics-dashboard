@echo off
cd /d "%~dp0"

if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Instalando dependencias...
pip install -r requirements.txt -q

echo.
echo ============================================
echo  Monitor de Alteracoes Shopify
echo  Acesse: http://localhost:8000
echo ============================================
echo.

uvicorn main:app --host 0.0.0.0 --port 8000

pause
