@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" configurar_telegram.py
) else (
  "D:\escritorio\Syslog\NETGUARD-NOC\.venv\Scripts\python.exe" configurar_telegram.py
)
pause
