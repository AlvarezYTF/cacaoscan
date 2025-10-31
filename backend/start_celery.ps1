# Script PowerShell para iniciar el worker de Celery
Set-Location $PSScriptRoot
.\venv\Scripts\Activate.ps1
python -m celery -A cacaoscan worker --loglevel=info --pool=solo

