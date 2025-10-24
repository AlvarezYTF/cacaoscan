# Guía de Ejecución de Tests E2E

## Requisitos Previos

### Software Necesario
- Node.js 18.x o superior
- Python 3.11 o superior
- PostgreSQL 13 o superior
- Navegadores: Chrome, Firefox, Edge

### Dependencias
```bash
# Frontend
cd frontend
npm install

# Backend
cd backend
pip install -r requirements.txt
```

## Configuración Inicial

### 1. Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:
```bash
# URLs de servicios
CYPRESS_baseUrl=http://localhost:4173
CYPRESS_apiUrl=http://localhost:8000

# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/cacaoscan_test
```

### 2. Base de Datos de Prueba
```bash
# Crear base de datos de prueba
createdb cacaoscan_test

# Ejecutar migraciones
cd backend
python manage.py migrate

# Cargar datos de prueba
python manage.py loaddata test_data.json
```

## Ejecución de Tests

### Modo Desarrollo (Interactivo)
```bash
# Iniciar servicios
cd backend
python manage.py runserver 0.0.0.0:8000 &

cd frontend
npm run build
npm run preview -- --port 4173 --host 0.0.0.0 &

# Ejecutar tests interactivos
npm run test:e2e:dev
```

### Modo Headless (Automático)
```bash
# Ejecutar todos los tests
npm run test:e2e

# Ejecutar tests específicos
npm run test:e2e:smoke
npm run test:e2e:performance
npm run test:e2e:security
```

### Tests por Navegador
```bash
# Chrome
npm run test:e2e:chrome

# Firefox
npm run test:e2e:firefox

# Edge
npm run test:e2e:edge
```

## Estructura de Tests

### Organización por Funcionalidad
```
cypress/e2e/
├── auth/                    # Autenticación
│   ├── login.cy.js
│   ├── register.cy.js
│   ├── password-recovery.cy.js
│   └── logout.cy.js
├── images/                  # Gestión de imágenes
│   ├── upload.cy.js
│   ├── analysis.cy.js
│   └── history.cy.js
├── fincas/                  # Gestión de fincas y lotes
│   ├── fincas-crud.cy.js
│   ├── lotes-crud.cy.js
│   └── fincas-lotes-relations.cy.js
├── reports/                 # Generación de reportes
│   ├── generation.cy.js
│   ├── visualization.cy.js
│   └── export-sharing.cy.js
├── navigation/              # Navegación y flujos
│   ├── complete-flows.cy.js
│   ├── routes-permissions.cy.js
│   └── ui-ux.cy.js
└── errors/                  # Manejo de errores
    ├── network-errors.cy.js
    ├── edge-cases.cy.js
    └── validation-forms.cy.js
```

## Comandos Personalizados

### Autenticación
```javascript
// Login con diferentes roles
cy.login('admin')      // Administrador
cy.login('analyst')    // Analista
cy.login('farmer')     // Agricultor

// Logout
cy.logout()
```

### Gestión de Datos
```javascript
// Llenar formularios
cy.fillFincaForm(fincaData)
cy.fillLoteForm(loteData)

// Cargar imágenes
cy.uploadTestImage('test-cacao.jpg')
```

### Verificaciones
```javascript
// Notificaciones
cy.checkNotification('Mensaje de éxito', 'success')

// Análisis
cy.waitForAnalysis(30000)

// Navegación
cy.checkNavigationForRole('admin')
```

## Datos de Prueba

### Usuarios Disponibles
```javascript
// Administrador
{
  email: 'admin@cacaoscan.com',
  password: 'Admin123!',
  role: 'admin'
}

// Analista
{
  email: 'analista@cacaoscan.com',
  password: 'Analyst123!',
  role: 'analyst'
}

// Agricultor
{
  email: 'agricultor@cacaoscan.com',
  password: 'Farmer123!',
  role: 'farmer'
}
```

### Datos de Fincas y Lotes
```javascript
// Finca de prueba
{
  nombre: 'Finca El Paraíso',
  ubicacion: 'Provincia de Los Ríos',
  area_total: 15.5,
  propietario: 'Carlos Campo'
}

// Lote de prueba
{
  nombre: 'Lote A - Norte',
  area: 3.2,
  variedad: 'CCN-51',
  edad_plantas: 5
}
```

## Debugging y Troubleshooting

### Problemas Comunes

#### 1. Tests Fallan por Timeout
```bash
# Aumentar timeout
CYPRESS_defaultCommandTimeout=20000 npm run test:e2e
```

#### 2. Servicios No Inician
```bash
# Verificar puertos
lsof -i :8000
lsof -i :4173

# Reiniciar servicios
pkill -f "python manage.py runserver"
pkill -f "npm run preview"
```

#### 3. Base de Datos Bloqueada
```bash
# Limpiar conexiones
psql -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'cacaoscan_test';"
```

### Modo Debug
```bash
# Ejecutar con interfaz gráfica
npm run test:e2e:dev

# Ejecutar test específico
npx cypress run --spec "cypress/e2e/auth/login.cy.js" --headed
```

### Logs y Reportes
```bash
# Ver logs detallados
DEBUG=cypress:* npm run test:e2e

# Generar reporte HTML
npx cypress run --reporter html
```

## Integración con CI/CD

### GitHub Actions
```yaml
# Ejecutar tests en CI
- name: Run E2E Tests
  run: npm run test:e2e:ci
  env:
    CYPRESS_baseUrl: http://localhost:4173
    CYPRESS_apiUrl: http://localhost:8000
```

### Variables de Entorno para CI
```bash
# Configuración mínima para CI
CYPRESS_baseUrl=http://localhost:4173
CYPRESS_apiUrl=http://localhost:8000
CYPRESS_video=false
CYPRESS_screenshotOnRunFailure=true
```

## Mantenimiento

### Actualización de Tests
1. **Revisar selectores**: Verificar que los selectores sigan siendo válidos
2. **Actualizar datos**: Modificar fixtures cuando cambien los datos de prueba
3. **Optimizar performance**: Identificar y optimizar tests lentos
4. **Agregar cobertura**: Incluir nuevos casos de prueba cuando sea necesario

### Monitoreo Continuo
1. **Revisar reportes**: Analizar resultados de CI/CD regularmente
2. **Screenshots de fallos**: Revisar capturas de pantalla de tests fallidos
3. **Métricas de rendimiento**: Monitorear tiempo de ejecución de tests
4. **Tasa de éxito**: Mantener > 95% de tests exitosos

### Mejores Prácticas
1. **Tests independientes**: Cada test debe poder ejecutarse por separado
2. **Datos limpios**: Limpiar datos de prueba después de cada test
3. **Selectores estables**: Usar `data-cy` attributes para selectores
4. **Timeouts apropiados**: Configurar timeouts según la complejidad de la operación
5. **Documentación**: Mantener documentación actualizada

## Recursos Adicionales

### Documentación Oficial
- [Cypress Documentation](https://docs.cypress.io/)
- [Cypress Best Practices](https://docs.cypress.io/guides/references/best-practices)
- [Cypress CI/CD](https://docs.cypress.io/guides/continuous-integration/introduction)

### Herramientas Útiles
- [Cypress Dashboard](https://dashboard.cypress.io/): Para monitoreo de tests
- [Cypress Real Events](https://github.com/dmtrKovalenko/cypress-real-events): Para eventos reales
- [Cypress Axe](https://github.com/component-driven/cypress-axe): Para tests de accesibilidad

### Comunidad
- [Cypress Discord](https://discord.gg/cypress)
- [Cypress GitHub](https://github.com/cypress-io/cypress)
- [Cypress Blog](https://www.cypress.io/blog/)
