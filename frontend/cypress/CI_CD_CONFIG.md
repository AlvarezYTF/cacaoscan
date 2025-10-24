# Configuración de Cypress para CI/CD

## Variables de Entorno

```bash
# URLs de los servicios
CYPRESS_baseUrl=http://localhost:4173
CYPRESS_apiUrl=http://localhost:8000

# Configuración de base de datos
CYPRESS_dbHost=localhost
CYPRESS_dbPort=5432
CYPRESS_dbName=cacaoscan_test
CYPRESS_dbUser=test_user
CYPRESS_dbPassword=test_password

# Configuración de archivos
CYPRESS_downloadsFolder=cypress/downloads
CYPRESS_screenshotsFolder=cypress/screenshots
CYPRESS_videosFolder=cypress/videos

# Configuración de timeouts
CYPRESS_defaultCommandTimeout=10000
CYPRESS_requestTimeout=10000
CYPRESS_responseTimeout=10000
CYPRESS_pageLoadTimeout=30000

# Configuración de retry
CYPRESS_retries=2
CYPRESS_retryDelay=1000

# Configuración de video
CYPRESS_video=true
CYPRESS_videoCompression=32

# Configuración de screenshots
CYPRESS_screenshotOnRunFailure=true
CYPRESS_screenshotOnHeadlessFailure=true

# Configuración de reportes
CYPRESS_reporter=spec
CYPRESS_reporterOptions=reportDir=cypress/reports
```

## Scripts de NPM

```json
{
  "scripts": {
    "test:e2e": "start-server-and-test preview http://localhost:4173 'cypress run --e2e'",
    "test:e2e:dev": "start-server-and-test 'vite dev --port 4173' http://localhost:4173 'cypress open --e2e'",
    "test:e2e:headless": "cypress run --e2e --headless",
    "test:e2e:chrome": "cypress run --e2e --browser chrome",
    "test:e2e:firefox": "cypress run --e2e --browser firefox",
    "test:e2e:edge": "cypress run --e2e --browser edge",
    "test:e2e:smoke": "cypress run --e2e --spec 'cypress/e2e/smoke/*.cy.js'",
    "test:e2e:performance": "cypress run --e2e --spec 'cypress/e2e/performance/*.cy.js'",
    "test:e2e:security": "cypress run --e2e --spec 'cypress/e2e/security/*.cy.js'",
    "test:e2e:parallel": "cypress run --e2e --parallel",
    "test:e2e:record": "cypress run --e2e --record --key $CYPRESS_RECORD_KEY",
    "test:e2e:ci": "cypress run --e2e --ci --browser chrome --headless",
    "test:e2e:debug": "cypress run --e2e --headed --no-exit"
  }
}
```

## Configuración de Docker

```dockerfile
# Dockerfile para tests E2E
FROM cypress/included:14.5.3

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos del proyecto
COPY frontend/package*.json ./frontend/
COPY backend/requirements.txt ./backend/

# Instalar dependencias
WORKDIR /app/frontend
RUN npm ci

WORKDIR /app/backend
RUN pip3 install -r requirements.txt

# Copiar código fuente
COPY . .

# Script de inicio
COPY scripts/start-e2e-tests.sh /start-e2e-tests.sh
RUN chmod +x /start-e2e-tests.sh

CMD ["/start-e2e-tests.sh"]
```

## Script de Inicio para Docker

```bash
#!/bin/bash
# start-e2e-tests.sh

set -e

echo "Iniciando servicios para tests E2E..."

# Iniciar base de datos
echo "Iniciando base de datos..."
pg_ctlcluster 13 main start

# Configurar base de datos de prueba
echo "Configurando base de datos de prueba..."
createdb -U postgres cacaoscan_test
psql -U postgres -d cacaoscan_test -c "CREATE USER test_user WITH PASSWORD 'test_password';"
psql -U postgres -d cacaoscan_test -c "GRANT ALL PRIVILEGES ON DATABASE cacaoscan_test TO test_user;"

# Iniciar backend
echo "Iniciando backend..."
cd /app/backend
python manage.py migrate
python manage.py loaddata test_data.json
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!

# Esperar que el backend esté listo
echo "Esperando que el backend esté listo..."
npx wait-on http://localhost:8000/api/health/ --timeout 30000

# Construir frontend
echo "Construyendo frontend..."
cd /app/frontend
npm run build

# Iniciar frontend
echo "Iniciando frontend..."
npm run preview -- --port 4173 --host 0.0.0.0 &
FRONTEND_PID=$!

# Esperar que el frontend esté listo
echo "Esperando que el frontend esté listo..."
npx wait-on http://localhost:4173 --timeout 30000

# Ejecutar tests
echo "Ejecutando tests E2E..."
npx cypress run --e2e --browser chrome --headless

# Limpiar procesos
echo "Limpiando procesos..."
kill $BACKEND_PID $FRONTEND_PID

echo "Tests E2E completados"
```

## Configuración de Jenkins

```groovy
pipeline {
    agent any
    
    environment {
        CYPRESS_baseUrl = 'http://localhost:4173'
        CYPRESS_apiUrl = 'http://localhost:8000'
        CYPRESS_RECORD_KEY = credentials('cypress-record-key')
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup') {
            steps {
                sh '''
                    cd frontend
                    npm ci
                    npm run prepare
                    
                    cd ../backend
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Database Setup') {
            steps {
                sh '''
                    cd backend
                    python manage.py migrate
                    python manage.py loaddata test_data.json
                '''
            }
        }
        
        stage('Start Services') {
            steps {
                sh '''
                    cd backend
                    python manage.py runserver 0.0.0.0:8000 &
                    sleep 10
                    
                    cd ../frontend
                    npm run build
                    npm run preview -- --port 4173 --host 0.0.0.0 &
                    sleep 5
                '''
            }
        }
        
        stage('Run E2E Tests') {
            steps {
                sh '''
                    cd frontend
                    npx cypress run --e2e --browser chrome --headless
                '''
            }
        }
        
        stage('Publish Results') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'frontend/cypress/reports',
                    reportFiles: 'index.html',
                    reportName: 'Cypress E2E Test Report'
                ])
            }
        }
    }
    
    post {
        always {
            sh '''
                pkill -f "python manage.py runserver"
                pkill -f "npm run preview"
            '''
        }
    }
}
```

## Configuración de GitLab CI

```yaml
stages:
  - setup
  - test
  - report

variables:
  CYPRESS_baseUrl: "http://localhost:4173"
  CYPRESS_apiUrl: "http://localhost:8000"

setup:
  stage: setup
  image: node:20
  script:
    - cd frontend
    - npm ci
    - npm run prepare
    - cd ../backend
    - python -m pip install --upgrade pip
    - pip install -r requirements.txt
    - python manage.py migrate
    - python manage.py loaddata test_data.json
  artifacts:
    paths:
      - frontend/node_modules/
      - backend/

test:
  stage: test
  image: cypress/included:14.5.3
  dependencies:
    - setup
  services:
    - postgres:13
  variables:
    POSTGRES_DB: cacaoscan_test
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_password
  script:
    - cd backend
    - python manage.py runserver 0.0.0.0:8000 &
    - sleep 10
    - cd ../frontend
    - npm run build
    - npm run preview -- --port 4173 --host 0.0.0.0 &
    - sleep 5
    - npx cypress run --e2e --browser chrome --headless
  artifacts:
    when: always
    paths:
      - frontend/cypress/screenshots/
      - frontend/cypress/videos/
      - frontend/cypress/reports/
    expire_in: 1 week

report:
  stage: report
  image: alpine:latest
  dependencies:
    - test
  script:
    - echo "Test results available in artifacts"
  artifacts:
    reports:
      junit: frontend/cypress/reports/junit.xml
```

## Configuración de Azure DevOps

```yaml
trigger:
- main
- develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  CYPRESS_baseUrl: 'http://localhost:4173'
  CYPRESS_apiUrl: 'http://localhost:8000'

stages:
- stage: E2ETests
  displayName: 'E2E Tests'
  jobs:
  - job: E2ETests
    displayName: 'Run E2E Tests'
    steps:
    - task: NodeTool@0
      inputs:
        versionSpec: '20.x'
      displayName: 'Install Node.js'
    
    - task: Npm@1
      inputs:
        command: 'ci'
        workingDir: 'frontend'
      displayName: 'Install Frontend Dependencies'
    
    - task: Npm@1
      inputs:
        command: 'custom'
        customCommand: 'run prepare'
        workingDir: 'frontend'
      displayName: 'Prepare Cypress'
    
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '3.11'
      displayName: 'Use Python 3.11'
    
    - task: PipAuthenticate@1
      inputs:
        pipServiceConnection: 'pip-service-connection'
      displayName: 'Pip Authenticate'
    
    - task: Pip@1
      inputs:
        command: 'install'
        requirementsSrc: 'backend/requirements.txt'
        workingDirectory: 'backend'
      displayName: 'Install Backend Dependencies'
    
    - script: |
        cd backend
        python manage.py migrate
        python manage.py loaddata test_data.json
        python manage.py runserver 0.0.0.0:8000 &
        sleep 10
      displayName: 'Setup Database and Start Backend'
    
    - script: |
        cd frontend
        npm run build
        npm run preview -- --port 4173 --host 0.0.0.0 &
        sleep 5
      displayName: 'Build and Start Frontend'
    
    - script: |
        cd frontend
        npx cypress run --e2e --browser chrome --headless
      displayName: 'Run E2E Tests'
    
    - task: PublishTestResults@2
      inputs:
        testResultsFiles: 'frontend/cypress/reports/junit.xml'
        testRunTitle: 'Cypress E2E Tests'
      condition: always()
      displayName: 'Publish Test Results'
    
    - task: PublishBuildArtifacts@1
      inputs:
        pathToPublish: 'frontend/cypress/screenshots'
        artifactName: 'cypress-screenshots'
      condition: always()
      displayName: 'Publish Screenshots'
    
    - task: PublishBuildArtifacts@1
      inputs:
        pathToPublish: 'frontend/cypress/videos'
        artifactName: 'cypress-videos'
      condition: always()
      displayName: 'Publish Videos'
```

## Configuración de CircleCI

```yaml
version: 2.1

orbs:
  cypress: cypress-io/cypress@2

jobs:
  e2e-tests:
    docker:
      - image: cypress/included:14.5.3
      - image: postgres:13
        environment:
          POSTGRES_DB: cacaoscan_test
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
    working_directory: ~/repo
    steps:
      - checkout
      - run:
          name: Install dependencies
          command: |
            cd frontend
            npm ci
            npm run prepare
            cd ../backend
            python -m pip install --upgrade pip
            pip install -r requirements.txt
      - run:
          name: Setup database
          command: |
            cd backend
            python manage.py migrate
            python manage.py loaddata test_data.json
      - run:
          name: Start backend
          command: |
            cd backend
            python manage.py runserver 0.0.0.0:8000 &
            sleep 10
      - run:
          name: Build and start frontend
          command: |
            cd frontend
            npm run build
            npm run preview -- --port 4173 --host 0.0.0.0 &
            sleep 5
      - cypress/run:
          browser: chrome
          headless: true
          working_directory: frontend
          env: CYPRESS_baseUrl=http://localhost:4173,CYPRESS_apiUrl=http://localhost:8000
      - store_artifacts:
          path: frontend/cypress/screenshots
      - store_artifacts:
          path: frontend/cypress/videos
      - store_test_results:
          path: frontend/cypress/reports

workflows:
  e2e-tests:
    jobs:
      - e2e-tests
