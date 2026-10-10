@echo off
cd /d "%~dp0"
set "NOC_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%NOC_PYTHON%" set "NOC_PYTHON=D:\escritorio\Syslog\NETGUARD-NOC\.venv\Scripts\python.exe"
"%NOC_PYTHON%" configurar_ssh.py
pause
