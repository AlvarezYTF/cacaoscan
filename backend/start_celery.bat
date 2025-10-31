@echo off
REM Script para iniciar el worker de Celery en Windows
cd /d %~dp0
call venv\Scripts\activate.bat
python -m celery -A cacaoscan worker --loglevel=info --pool=solo
pause

