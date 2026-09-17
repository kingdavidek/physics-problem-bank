@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (set PY=.venv\Scripts\python.exe) else (set PY=python)
start "" /b cmd /c "timeout /t 3 >nul && start http://127.0.0.1:5001"
"%PY%" app.py
pause
