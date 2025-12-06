# Comandos para Ejecutar Tests - CacaoScan

## 🐍 Backend (Python/pytest) | 🎨 Frontend (Vue/Vitest)

<table>
<tr>
<td width="50%">

### Backend

#### Ejecutar todos los tests
```bash
cd backend
pytest
```

#### Ejecutar tests con coverage (para SonarQube)
```bash
cd backend
pytest --cov=. --cov-report=xml:coverage.xml --cov-report=term-missing -v --tb=short
```

#### Ejecutar tests con errores completos (debugging)
```bash
cd backend
pytest --cov=. --cov-report=xml:coverage.xml --cov-report=term-missing -v --tb=long --showlocals
```

#### Ejecutar tests específicos
```bash
cd backend
pytest tests/test_prediction_scalers.py
pytest tests/test_api.py -v
pytest tests/ -k "test_prediction"
```

#### Ejecutar tests excluyendo los lentos
```bash
cd backend
pytest -m "not slow"
```

#### Ejecutar solo tests de integración
```bash
cd backend
pytest -m integration
```

#### Usar script de Windows
```bash
cd backend
run_tests.bat
```

#### Generar Coverage para SonarQube
```bash
cd backend
pytest --cov=. --cov-report=xml:coverage.xml
# Archivo: backend/coverage.xml
```

#### Verificar que los tests pasan
```bash
cd backend
pytest -v
# Meta: 0 errores, 0 fails, solo skips permitidos
```

</td>
<td width="50%">

### Frontend

#### Ejecutar todos los tests unitarios
```bash
cd frontend
pnpm test:unit
```

#### Ejecutar tests unitarios con coverage
```bash
cd frontend
pnpm test:coverage
```

#### Ejecutar tests en modo watch (desarrollo)
```bash
cd frontend
pnpm test:unit:watch
```

#### Ejecutar tests con coverage para SonarQube
```bash
cd frontend
pnpm test:coverage
```

#### Ejecutar todos los tests
```bash
cd frontend
pnpm test:all
```

#### Generar Coverage para SonarQube
```bash
cd frontend
pnpm test:unit:coverage
# Archivo: frontend/coverage/lcov.info
```

#### Verificar que los tests pasan
```bash
cd frontend
pnpm test:unit
# Debe mostrar todos los tests pasando
```

</td>
</tr>
</table>

---

## ⚠️ Notas Importantes

<table>
<tr>
<td width="50%">

### Backend

**Activar entorno virtual:**
```bash
cd backend
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

**Coverage:**
- Archivo generado: `backend/coverage.xml`

**Tests lentos:**
- Algunos tests están marcados como `@pytest.mark.slow`

</td>
<td width="50%">

### Frontend

**Instalar dependencias:**
```bash
cd frontend
pnpm install
```

**Coverage:**
- Archivo generado: `frontend/coverage/lcov.info`

**Comandos disponibles:**
- `pnpm test:unit` - Tests unitarios
- `pnpm test:coverage` - Tests con coverage
- `pnpm test:unit:watch` - Modo watch

</td>
</tr>
</table>
