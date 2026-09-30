@echo off
title DepthWizard Launcher
echo ===================================================
echo             STARTING DEPTHWIZARD
echo ===================================================
echo.

set "PATH=C:\Program Files\nodejs;%PATH%"

echo Starting AI Backend Server on http://localhost:8000 ...
start "DepthWizard Backend" cmd /k "cd /d "%~dp0" && py server.py"

timeout /t 3 /nobreak >nul

echo Starting Frontend on http://localhost:5173 ...
start "DepthWizard Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo DepthWizard is starting!
echo - Backend:  http://localhost:8000
echo - Frontend: http://localhost:5173
echo.
pause