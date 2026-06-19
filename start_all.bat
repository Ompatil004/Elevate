@echo off
setlocal
echo =======================================================
echo Starting Elevate Platform Services...
echo =======================================================

:: Use absolute path derived from this bat file location.
set "ROOT=%~dp0"

echo [1/3] Starting Node.js Backend (port 5000)...
start "Elevate - Node.js Backend" cmd /k call "%ROOT%start_node.bat"

echo Waiting 2 seconds before starting Python backend...
timeout /t 2 /nobreak >nul

echo [2/3] Starting Python Backend (port 8000)...
start "Elevate - Python Backend" cmd /k call "%ROOT%start_python.bat"

echo Waiting 2 seconds before starting Frontend...
timeout /t 2 /nobreak >nul

echo [3/3] Starting React Frontend (port 5173)...
start "Elevate - React Frontend" cmd /k call "%ROOT%start_frontend.bat"

echo.
echo =======================================================
echo All services launched in separate windows!
echo.
echo   Node.js  -^> http://localhost:5000
echo   Python   -^> http://localhost:8000
echo   Frontend -^> http://localhost:5173
echo.
echo Launcher exiting. Check each service window for errors.
echo =======================================================
endlocal
exit /b 0
