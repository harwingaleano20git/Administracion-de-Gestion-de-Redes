@echo off
cd /d "%~dp0"
set "NOC_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%NOC_PYTHON%" set "NOC_PYTHON=D:\escritorio\Syslog\NETGUARD-NOC\.venv\Scripts\python.exe"
if not exist "%NOC_PYTHON%" (
  echo Instala las dependencias siguiendo README.md.
  pause
  exit /b 1
)
echo Abre http://127.0.0.1:8002 en tu navegador.
echo Si el puerto esta ocupado, ya hay otra instancia activa.
"%NOC_PYTHON%" -m uvicorn app.main:app --host 127.0.0.1 --port 8002
pause
