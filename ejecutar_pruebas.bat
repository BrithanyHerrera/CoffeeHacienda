@echo off
chcp 65001 > nul
title Pruebas Unitarias - Sistema POS Cafeteria La Hacienda

echo.
echo =====================================================================
echo   SISTEMA POS - CAFETERIA LA HACIENDA
echo   Laboratorio Abierto, Pruebas 2026 B2
echo =====================================================================
echo.

:: ---------- Verificar que .venv exista ----------
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] No se encontro el entorno virtual .venv
    echo         Crealo con: python -m venv .venv
    pause
    exit /b 1
)

echo [1/4] Instalando dependencias de produccion...
.venv\Scripts\pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la instalacion de requirements.txt
    pause
    exit /b 1
)
echo        OK - requirements.txt instalado.
echo.

echo [2/4] Instalando dependencias de desarrollo y pruebas...
.venv\Scripts\pip install -r requirements-dev.txt --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la instalacion de requirements-dev.txt
    pause
    exit /b 1
)
echo        OK - requirements-dev.txt instalado.
echo.

echo [3/4] Ejecutando suite de pruebas unitarias...
echo -----------------------------------------------
.venv\Scripts\python.exe -m pytest tests\ --tb=short -v
set TEST_EXIT=%errorlevel%
echo -----------------------------------------------
echo.

echo [4/4] Generando documento Word de evidencias...
.venv\Scripts\python.exe "%~dp0scripts\gen_docx.py"
echo.

echo =====================================================================
if %TEST_EXIT% equ 0 (
    echo   RESULTADO: Todas las pruebas PASARON exitosamente.
) else (
    echo   RESULTADO: Algunas pruebas FALLARON. Revisa la salida de arriba.
)
echo =====================================================================
echo.
pause
