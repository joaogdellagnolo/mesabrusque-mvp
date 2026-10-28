@echo off
chcp 65001 >nul
echo ===================================================
echo   Iniciando MesaBrusque (Backend API + Frontend)
echo ===================================================

set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
set "PATH=%PATH%;C:\Program Files\nodejs;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"

echo [1/2] Subindo Backend FastAPI em http://localhost:8000 ...
start "MesaBrusque - Backend FastAPI" cmd /k "cd /d "%~dp0backend" && "%PYTHON_EXE%" -m uvicorn main:app --reload --port 8000"

echo [2/2] Subindo Frontend React/Vite em http://localhost:5173 ...
start "MesaBrusque - Frontend React" cmd /k "cd /d "%~dp0frontend" && "C:\Program Files\nodejs\npm.cmd" run dev"

echo.
echo Tudo pronto! Aguarde alguns segundos e acesse:
echo - App React: http://localhost:5173
echo - Docs da API: http://localhost:8000/docs
pause

