# Comandos para Ejecutar Tests - CacaoScan

## 🐍 Backend (Python/pytest)

### Ejecutar todos los tests
```bash
cd backend
pytest
```

### Ejecutar tests con coverage (para SonarQube)
```bash
cd backend
pytest --cov=. --cov-report=xml:coverage.xml --cov-report=term-missing
```

### Ejecutar tests específicos
```bash
cd backend
pytest tests/test_prediction_scalers.py
pytest tests/test_api.py -v
pytest tests/ -k "test_prediction"  # Tests que contengan "test_prediction"
```

### Ejecutar tests excluyendo los lentos
```bash
cd backend
pytest -m "not slow"
```

### Ejecutar solo tests de integración
```bash
cd backend
pytest -m integration
```

### Usar script de Windows
```bash
cd backend
run_tests.bat
```

---

## 🎨 Frontend (Vue/Vitest/Cypress)

### Tests Unitarios (Vitest)

#### Ejecutar todos los tests unitarios
```bash
cd frontend
pnpm test:unit
```

#### Ejecutar tests unitarios con coverage
```bash
cd frontend
pnpm test:unit:coverage
```

#### Ejecutar tests en modo watch (desarrollo)
```bash
cd frontend
pnpm test:unit:watch
```

#### Ejecutar tests con coverage para SonarQube
```bash
cd frontend
pnpm test:coverage:sonar
```

### Tests E2E (Cypress)

#### Modo interactivo (abre interfaz gráfica)
```bash
cd frontend
pnpm cypress:open
```

#### Modo headless (ejecuta todos los tests)
```bash
cd frontend
pnpm cypress:run
```

#### Tests E2E específicos por categoría
```bash
cd frontend
pnpm test:auth        # Tests de autenticación
pnpm test:fincas      # Tests de fincas y lotes
pnpm test:reports     # Tests de reportes
pnpm test:navigation  # Tests de navegación y rutas
pnpm test:images      # Tests de imágenes
pnpm test:admin       # Tests de administración
pnpm test:ui          # Tests de UI/UX
```

### Ejecutar todos los tests (unitarios + E2E)
```bash
cd frontend
pnpm test:all
```

### Ejecutar todos los tests con coverage
```bash
cd frontend
pnpm test:all:coverage
```

---

## 📊 Generar Coverage para SonarQube

### Backend
```bash
cd backend
pytest --cov=. --cov-report=xml:coverage.xml
# El archivo coverage.xml se genera en backend/coverage.xml
```

### Frontend
```bash
cd frontend
pnpm test:unit:coverage
# El archivo lcov.info se genera en frontend/coverage/lcov.info
```

---

## 🔍 Verificar que los tests pasan

### Backend
```bash
cd backend
pytest -v
# Debe terminar con: "passed", "failed", "skipped"
# Meta: 0 errores, 0 fails, solo skips permitidos
```

### Frontend - Unitarios
```bash
cd frontend
pnpm test:unit
# Debe mostrar todos los tests pasando
```

### Frontend - E2E
```bash
cd frontend
pnpm cypress:run
# Debe ejecutar todos los tests Cypress
```

---

## ⚠️ Notas Importantes

1. **Backend**: Asegúrate de tener el entorno virtual activado
   ```bash
   cd backend
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Frontend**: Asegúrate de tener las dependencias instaladas
   ```bash
   cd frontend
   pnpm install
   ```

3. **Coverage**: Los archivos de coverage se generan automáticamente:
   - Backend: `backend/coverage.xml`
   - Frontend: `frontend/coverage/lcov.info`

4. **Tests lentos**: Algunos tests están marcados como `@pytest.mark.slow` y pueden tardar más tiempo.

