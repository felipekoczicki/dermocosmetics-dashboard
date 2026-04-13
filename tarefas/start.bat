@echo off
cd /d "%~dp0"

if not exist "venv" (
    echo Criando ambiente virtual...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt -q

echo.
echo ================================
echo  Minhas Tarefas
echo  Acesse: http://localhost:7000
echo ================================
echo.

uvicorn main:app --host 0.0.0.0 --port 7000

pause
