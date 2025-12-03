@echo off
REM Script para generar reporte de cobertura en formato texto
REM Uso: generate_coverage.bat [nombre_archivo_salida.txt]

cd /d "%~dp0"

if "%1"=="" (
    set "OUTPUT_FILE=coverage_report.txt"
) else (
    set "OUTPUT_FILE=%1"
)

REM Detectar y usar el entorno virtual si existe
set "PYTHON_CMD="
if exist "venv\Scripts\python.exe" (
    set "PYTHON_CMD=venv\Scripts\python.exe"
    echo Usando Python del entorno virtual...
    goto :run
)

if exist "env\Scripts\python.exe" (
    set "PYTHON_CMD=env\Scripts\python.exe"
    echo Usando Python del entorno virtual (env)...
    goto :run
)

REM Intentar py -3.12
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py"
    set "PYTHON_ARGS=-3.12"
    echo Usando py -3.12...
    goto :run
)

REM Último recurso: python del sistema
set "PYTHON_CMD=python"
set "PYTHON_ARGS="
echo Usando python del sistema...

:run
echo ========================================
echo Generando reporte de cobertura...
echo ========================================
echo.

if defined PYTHON_ARGS (
    "%PYTHON_CMD%" %PYTHON_ARGS% generate_coverage_report.py "%OUTPUT_FILE%"
) else (
    "%PYTHON_CMD%" generate_coverage_report.py "%OUTPUT_FILE%"
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Reporte generado exitosamente!
    echo ========================================
    echo.
    echo Archivo: %OUTPUT_FILE%
    echo.
) else (
    echo.
    echo ========================================
    echo Error al generar el reporte
    echo ========================================
    exit /b 1
)

pause
