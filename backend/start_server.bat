@echo off
REM Script para iniciar el servidor Django en Windows
echo ========================================
echo Iniciando servidor Django CacaoScan
echo ========================================
echo.

REM Verificar si el entorno virtual existe
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Entorno virtual no encontrado.
    echo Por favor, crea el entorno virtual primero:
    echo   py -3.12 -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Verificar que Django esté instalado
python -c "import django" 2>nul
if errorlevel 1 (
    echo ERROR: Django no está instalado.
    echo Por favor, instala las dependencias:
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM Verificar que el archivo .env existe
if not exist ".env" (
    echo ADVERTENCIA: Archivo .env no encontrado.
    echo Asegúrate de haber creado el archivo .env con la configuración necesaria.
    echo.
)

echo Iniciando servidor en http://127.0.0.1:8000
echo Presiona Ctrl+C para detener el servidor
echo.

REM Iniciar el servidor
python manage.py runserver

pause

