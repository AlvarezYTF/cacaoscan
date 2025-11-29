@echo off
REM Script para ejecutar tests en Windows
REM Prioriza Python 3.12
cd /d %~dp0

REM Intentar Python 3.12 específicamente
py -3.12 run_tests.py %* 2>nul
if %ERRORLEVEL% EQU 0 goto :end

REM Si falla, intentar con py sin versión específica
py run_tests.py %* 2>nul
if %ERRORLEVEL% EQU 0 goto :end

REM Último recurso: python genérico
python run_tests.py %*

:end

