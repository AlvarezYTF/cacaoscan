@echo off
echo ============================
echo 1) Generando coverage BACKEND (Python)
echo ============================

cd backend
pytest --cov=. --cov-report=xml:coverage.xml

if NOT exist coverage.xml (
    echo ERROR: coverage.xml NO SE GENERO
    exit /b 1
)

REM Fix coverage.xml paths for SonarQube (in case it was generated on a different machine)
python fix_coverage_paths.py coverage.xml

cd ..

echo ============================
echo 2) Generando coverage FRONTEND (Vue)
echo ============================

cd frontend
npm install
npm run test -- --coverage

if NOT exist coverage\lcov.info (
    echo ERROR: lcov.info NO SE GENERO
    exit /b 1
)
cd ..

echo ============================
echo 3) Ejecutando SONAR-SCANNER
echo ============================

sonar-scanner.bat ^
  -D"sonar.projectKey=cacao-scan" ^
  -D"sonar.sources=." ^
  -D"sonar.tests=backend/tests" ^
  -D"sonar.python.version=3.12" ^
  -D"sonar.python.coverage.reportPaths=backend/coverage.xml" ^
  -D"sonar.javascript.lcov.reportPaths=frontend/coverage/lcov.info" ^
  -D"sonar.host.url=https://sonarqube.dataguaviare.com.co" ^
  -D"sonar.token=sqa_xxxxxxxxxxxxxxxxxxxxxxxxxxxx"

echo ============================
echo  ANALISIS COMPLETO
echo ============================
pause
