@echo off
chcp 65001 > nul
title Cafeteria La Hacienda - Servidor POS

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo =====================================================================
    echo   [ERROR] No se encontro el entorno virtual .venv
    echo   Primero ejecuta: instalar_dependencias.bat
    echo =====================================================================
    echo.
    pause
    exit /b 1
)

echo.
echo =====================================================================
echo   Iniciando Servidor POS - Cafeteria La Hacienda...
echo   Presiona CTRL + C en esta ventana para detener el servidor.
echo =====================================================================
echo.

.venv\Scripts\python.exe app.py
pause
