@echo off
chcp 65001 > nul
title Instalador de Dependencias - Cafeteria La Hacienda

echo.
echo =====================================================================
echo   SISTEMA POS - CAFETERIA LA HACIENDA
echo   Instalacion automatica de librerias y entorno virtual
echo =====================================================================
echo.

:: 1. Verificar si Python esta instalado en el sistema
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no esta instalado o no se encuentra en el PATH de Windows.
    echo         Descargalo e instalalo desde: https://www.python.org/
    echo         *IMPORTANTE*: Marca la casilla "Add python.exe to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PY_VER=%%i
echo [*] Detectado: %PY_VER%
echo.

:: 2. Crear entorno virtual si no existe
if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Creando entorno virtual en .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual .venv
        pause
        exit /b 1
    )
    echo       OK - Entorno virtual creado.
) else (
    echo [1/3] El entorno virtual .venv ya existe. Continuamos...
)
echo.

:: 3. Activar entorno virtual
call .venv\Scripts\activate.bat

:: Actualizar pip
python -m pip install --upgrade pip --quiet

:: 4. Instalar requirements.txt
echo [2/3] Instalando dependencias base (requirements.txt)...
echo       (Flask, PyMySQL, python-dotenv, DBUtils, etc.)
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Ocurrio un fallo al instalar requirements.txt
    pause
    exit /b 1
)
echo       OK - Dependencias base instaladas.
echo.

:: 5. Instalar requirements-dev.txt
echo [3/3] Instalando herramientas de desarrollo y pruebas (requirements-dev.txt)...
echo       (pytest, pytest-cov, ruff, python-docx, etc.)
pip install -r requirements-dev.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Ocurrio un fallo al instalar requirements-dev.txt
    pause
    exit /b 1
)
echo       OK - Herramientas de desarrollo instaladas.
echo.

:: 6. Copiar archivo de entorno si no existe
if not exist "bd.env" (
    if exist "bd.env.example" (
        copy "bd.env.example" "bd.env" > nul
        echo [*] Se creo "bd.env" a partir de "bd.env.example".
        echo     Recuerda editarlo con las credenciales de tu base de datos local si es necesario.
        echo.
    )
)

echo =====================================================================
echo   INSTALACION COMPLETADA CON EXITO
echo   Todas las librerias estan listas en el entorno .venv
echo =====================================================================
echo.
pause
