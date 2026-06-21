@echo off
setlocal
set "ROOT=%~dp0"
set "ROOT_PY=%ROOT%backend-python\.venv\Scripts\python.exe"
cd /d "%ROOT%backend-python"
if exist "%ROOT_PY%" (
    "%ROOT_PY%" server.py
) else (
    echo [WARN] Using system Python because backend-python virtualenv python was not found.
    python server.py
)
