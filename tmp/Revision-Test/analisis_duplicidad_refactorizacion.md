# 📋 ANÁLISIS DE DUPLICIDAD Y PLAN DE REFACTORIZACIÓN

## 🟦 cypress/e2e/admin/admin-training.cy.js

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~15-20%

**Tipos de duplicidad:**
- beforeEach repetido (cy.login, cy.visit)
- Patrones de espera duplicados (cy.wait)
- Selectores repetidos en múltiples tests
- Flujos de confirmación duplicados

**Causas principales:**
- Falta de custom commands para acciones comunes
- No hay helpers centralizados para interacciones repetitivas

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **beforeEach duplicado:**
  ```javascript
  beforeEach(() => {
    cy.login('admin')
    cy.visit('/admin/training')
  })
  ```

- **Patrones de espera:**
  - `cy.wait(1000)`, `cy.wait(500)` repetidos
  - Falta de esperas inteligentes

- **Flujos de confirmación:**
  - `cy.get('[data-cy="confirm-cancel"]').click()` repetido

- **Selectores duplicados:**
  - `[data-cy="training-jobs"]` usado múltiples veces sin abstracción

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Cypress:**
- Crear custom command `cy.navigateToTraining()` que combine login + visit
- Crear helper `waitForTrainingJobs()` para esperas inteligentes
- Crear custom command `cy.confirmAction()` para confirmaciones genéricas
- Centralizar selectores en `cypress/support/selectors.js`
- Crear fixture para datos de training jobs

**Tests:**
- Unificar beforeEach usando setup helpers
- Extraer flujos comunes a funciones reutilizables

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <5%
- Mantener cobertura actual
- Código más legible y mantenible

---

## 🟦 cypress/e2e/images/analysis.cy.js

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~40-50%

**Tipos de duplicidad:**
- Flujo completo de upload + análisis repetido en cada test
- Helpers locales duplicados (`verifySelectorsExist`)
- Patrones de verificación de resultados idénticos
- Intercepts duplicados con misma estructura

**Causas principales:**
- Falta de abstracción del flujo de análisis completo
- Helpers no centralizados
- No hay fixtures para datos de análisis

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Flujo de upload repetido (11 veces):**
  ```javascript
  cy.get('body').then(($body) => {
    if ($body.find('input[type="file"]').length > 0) {
      cy.uploadTestImage('test-cacao.jpg')
      cy.get('body', { timeout: 5000 }).then(($afterUpload) => {
        if ($afterUpload.find('[data-cy="upload-button"]').length > 0) {
          cy.get('[data-cy="upload-button"]').first().click()
          // ... más código
        }
      })
    }
  })
  ```

- **Helper `verifySelectorsExist` duplicado:**
  - Existe en este archivo pero también en otros archivos

- **Patrones de verificación de resultados:**
  - Misma lógica para verificar `[data-cy="analysis-results"]` repetida

- **Intercepts duplicados:**
  - Misma estructura de intercept para errores repetida

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Cypress:**
- Crear custom command `cy.performImageAnalysis(imageName, options)` que encapsule todo el flujo
- Mover `verifySelectorsExist` a `cypress/support/helpers.js`
- Crear custom command `cy.waitForAnalysisResults(timeout)`
- Crear helper `setupAnalysisIntercepts()` para intercepts comunes
- Crear fixture `analysisResults.json` para datos de prueba

**Tests:**
- Refactorizar tests para usar `cy.performImageAnalysis()`
- Extraer verificaciones comunes a helpers
- Unificar manejo de errores

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <10%
- Tests más cortos y legibles
- Mantener cobertura completa

---

## 🟦 cypress/e2e/admin/admin-usuarios.cy.js

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~25-30%

**Tipos de duplicidad:**
- beforeEach duplicado
- Patrones de filtrado/búsqueda repetidos
- Flujos CRUD básicos sin abstracción
- Selectores repetidos

**Causas principales:**
- Falta de helpers para operaciones CRUD genéricas
- No hay abstracción de filtros y búsqueda

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **beforeEach duplicado:**
  ```javascript
  beforeEach(() => {
    cy.login('admin')
    cy.visit('/admin/usuarios')
  })
  ```

- **Patrones de filtrado:**
  - `cy.get('[data-cy="role-filter"]').select('farmer')` + `cy.wait(500)` repetido

- **Flujos CRUD:**
  - Ver, editar, eliminar con confirmación - patrón repetido

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Cypress:**
- Crear custom command `cy.navigateToAdminUsers()`
- Crear helper `filterUsersByRole(role)`
- Crear helper `searchUsers(query)`
- Crear custom commands genéricos: `cy.viewUser()`, `cy.editUser()`, `cy.deleteUserWithConfirmation()`
- Centralizar selectores de usuarios

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <10%
- Tests más expresivos
- Mantener funcionalidad actual

---

## 🟦 cypress/e2e/fincas/lotes-crud.cy.js

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~35-45%

**Tipos de duplicidad:**
- Helpers locales duplicados (`verifySelectorsExist`, `clickIfExists`, `selectIfExists`, `typeIfExists`, `fillLoteForm`)
- Flujos CRUD completos repetidos
- Patrones de validación duplicados
- Intercepts con misma estructura

**Causas principales:**
- Helpers definidos localmente en lugar de centralizados
- Falta de abstracción de flujos CRUD
- No hay fixtures para datos de lotes

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Helpers duplicados (también en fincas-crud.cy.js):**
  ```javascript
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => { ... }
  const clickIfExists = (selector, options = {}) => { ... }
  const selectIfExists = (selector, value, options = {}) => { ... }
  const typeIfExists = (selector, text, options = {}) => { ... }
  const fillLoteForm = (data) => { ... }
  ```

- **Flujo de creación repetido:**
  - Mismo patrón de click → select → fill → submit en múltiples tests

- **Patrones de validación:**
  - Verificación de errores con misma estructura repetida

- **Intercepts duplicados:**
  - Misma estructura para errores de creación

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Cypress:**
- **MOVER helpers a `cypress/support/helpers.js`:**
  - `verifySelectorsExist`
  - `clickIfExists`
  - `selectIfExists`
  - `typeIfExists`
  - `fillLoteForm` → generalizar a `fillForm(formData, formType)`

- **Crear custom commands:**
  - `cy.createLote(loteData)`
  - `cy.editLote(loteId, updates)`
  - `cy.deleteLote(loteId)`
  - `cy.validateLoteForm(expectedErrors)`

- **Centralizar:**
  - Selectores en `cypress/support/selectors.js`
  - Fixtures para datos de lotes
  - Intercepts comunes en `cypress/support/intercepts.js`

**Tests:**
- Refactorizar tests para usar helpers centralizados
- Simplificar tests usando custom commands

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <10%
- Eliminar helpers locales duplicados
- Tests más cortos y mantenibles

---

## 🟦 cypress/e2e/images/upload.cy.js

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~50-60%

**Tipos de duplicidad:**
- Flujo completo de carga de archivo repetido 8+ veces
- Creación de File/Blob/DataTransfer duplicada
- Manejo de fixtures duplicado
- Patrones de validación de archivos repetidos

**Causas principales:**
- No hay abstracción del flujo de upload
- Creación de archivos de prueba repetida
- Falta de helpers para validaciones de archivos

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Flujo de upload completo (8+ veces):**
  ```javascript
  cy.fixture('test-cacao.jpg', { encoding: null }).then((fileContent) => {
    const blob = new Blob([fileContent], { type: 'image/jpeg' })
    const file = new File([blob], 'test-cacao.jpg', { type: 'image/jpeg' })
    cy.get('[data-cy="file-input"]').then(($input) => {
      const dataTransfer = new DataTransfer()
      dataTransfer.items.add(file)
      $input[0].files = dataTransfer.files
      cy.wrap($input).trigger('change', { force: true })
    })
  }).catch(() => {
    // fallback duplicado
  })
  ```

- **Creación de archivos de prueba:**
  - Misma lógica para crear File/Blob repetida

- **Validaciones de tipo/tamaño:**
  - Misma estructura para validar tipos permitidos/no permitidos

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Cypress:**
- **Crear custom command `cy.uploadFile(fileName, options)`:**
  - Encapsular toda la lógica de File/Blob/DataTransfer
  - Manejar fallbacks automáticamente

- **Crear helpers:**
  - `createTestFile(name, type, size)` para crear archivos de prueba
  - `validateFileType(file, allowedTypes)`
  - `validateFileSize(file, maxSize)`

- **Centralizar:**
  - Fixtures de imágenes
  - Constantes de tipos/tamaños permitidos

**Tests:**
- Refactorizar todos los tests para usar `cy.uploadFile()`
- Simplificar validaciones usando helpers

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <15%
- Eliminar código repetido de creación de archivos
- Tests más claros y mantenibles

---

## 🟦 cypress/e2e/errors/validation-forms.cy.js

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~30-40%

**Tipos de duplicidad:**
- Helpers locales duplicados (`verifySelectorsExist`, `openModal`, `fillFieldAndSubmit`, `verifyErrorMessage`)
- Patrones de validación repetidos
- Flujos de apertura de modales duplicados
- Estructura de verificación de errores idéntica

**Causas principales:**
- Helpers no centralizados
- Falta de abstracción de validaciones comunes
- No hay helpers genéricos para formularios

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Helpers duplicados:**
  ```javascript
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => { ... }
  const openModal = (buttonSelector, callback) => { ... }
  const fillFieldAndSubmit = (fieldSelector, value, submitSelector, errorCallback) => { ... }
  const verifyErrorMessage = ($error, errorSelector, expectedTexts) => { ... }
  ```

- **Patrones de validación:**
  - Misma estructura para validar campos requeridos
  - Misma estructura para validar formatos (email, teléfono, etc.)

- **Flujos de modal:**
  - Apertura de modal → llenar campo → submit → verificar error repetido

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Cypress:**
- **MOVER helpers a `cypress/support/helpers.js`:**
  - Todos los helpers locales

- **Crear custom commands:**
  - `cy.openFormModal(modalSelector)`
  - `cy.validateRequiredField(fieldSelector, errorSelector)`
  - `cy.validateFieldFormat(fieldSelector, invalidValue, expectedError)`
  - `cy.submitFormAndVerifyError(formSelector, expectedErrors)`

- **Crear helpers genéricos:**
  - `validateEmailFormat()`
  - `validatePhoneFormat()`
  - `validatePasswordStrength()`

**Tests:**
- Refactorizar para usar helpers centralizados
- Simplificar tests de validación

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <15%
- Eliminar helpers locales
- Tests más expresivos

---

## 🟦 cypress/e2e/errors/network-errors.cy.js

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~35-45%

**Tipos de duplicidad:**
- Helpers locales duplicados (`setupErrorIntercept`, `verifyErrorDisplay`, `clickRetryIfExists`)
- Estructura de intercepts repetida
- Patrones de verificación de errores idénticos
- Manejo de diferentes códigos de error con misma estructura

**Causas principales:**
- Helpers no centralizados
- Falta de abstracción de manejo de errores HTTP
- No hay helpers genéricos para intercepts de error

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Helpers duplicados:**
  ```javascript
  const setupErrorIntercept = (url, statusCode, body, alias) => { ... }
  const verifyErrorDisplay = (expectedTexts) => { ... }
  const clickRetryIfExists = () => { ... }
  ```

- **Estructura de intercepts repetida:**
  ```javascript
  const apiBaseUrl = Cypress.env('API_BASE_URL') || 'http://localhost:8000/api/v1'
  cy.intercept('GET', `${apiBaseUrl}/fincas/**`, {
    statusCode: 500,
    body: { error: '...' }
  }).as('...')
  ```

- **Verificación de errores:**
  - Misma estructura para verificar mensajes de error repetida

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Cypress:**
- **MOVER helpers a `cypress/support/helpers.js`**
- **Crear custom commands:**
  - `cy.interceptError(method, url, statusCode, errorBody, alias)`
  - `cy.verifyErrorMessage(expectedTexts)`
  - `cy.retryIfAvailable()`

- **Crear helpers para códigos HTTP comunes:**
  - `setupServerError()`
  - `setupNotFoundError()`
  - `setupUnauthorizedError()`
  - `setupForbiddenError()`

- **Centralizar:**
  - Constante `API_BASE_URL` en `cypress/support/config.js`
  - Mensajes de error esperados en fixtures

**Tests:**
- Refactorizar para usar helpers centralizados
- Simplificar tests de errores de red

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <15%
- Eliminar helpers locales
- Tests más claros y mantenibles

---

## 🟦 cypress/e2e/auth/register.cy.js

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~25-35%

**Tipos de duplicidad:**
- Helpers locales duplicados (`verifySelectorsExist`, `fillFormIfFieldsExist`, `fillOptionalField`, `fillRegisterForm`, `submitRegisterForm`, `verifySuccessMessage`, `verifyVerificationMessage`, `verifyErrorMessage`)
- Flujo de registro repetido
- Patrones de validación duplicados
- Generación de contraseñas (ya corregida)

**Causas principales:**
- Helpers no centralizados
- Falta de abstracción del flujo de registro
- No hay helpers genéricos para formularios de registro

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Helpers duplicados:**
  ```javascript
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => { ... }
  const fillFormIfFieldsExist = (callback) => { ... }
  const fillOptionalField = (selector, value) => { ... }
  const fillRegisterForm = (user) => { ... }
  const submitRegisterForm = () => { ... }
  const verifySuccessMessage = () => { ... }
  const verifyVerificationMessage = () => { ... }
  const verifyErrorMessage = (expectedTexts) => { ... }
  ```

- **Flujo de registro:**
  - Mismo patrón de llenar formulario → submit → verificar repetido

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Cypress:**
- **MOVER helpers a `cypress/support/helpers.js`**
- **Crear custom commands:**
  - `cy.fillRegisterForm(userData)`
  - `cy.submitRegisterForm()`
  - `cy.verifyRegistrationSuccess()`
  - `cy.verifyRegistrationError(expectedTexts)`

- **Crear helpers genéricos:**
  - `validatePasswordMatch()`
  - `validatePasswordStrength()`
  - `validateEmailFormat()`

**Tests:**
- Refactorizar para usar helpers centralizados
- Simplificar tests de registro

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <15%
- Eliminar helpers locales
- Tests más expresivos

---

## 🟦 cypress/e2e/fincas/fincas-crud.cy.js

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~35-45%

**Tipos de duplicidad:**
- **MISMO PROBLEMA que lotes-crud.cy.js:**
  - Helpers locales idénticos (`verifySelectorsExist`, `clickIfExists`, `selectIfExists`, `typeIfExists`, `fillFincaForm`)
  - Flujos CRUD completos repetidos
  - Patrones de validación duplicados

**Causas principales:**
- Helpers duplicados entre archivos
- Falta de abstracción de flujos CRUD
- No hay helpers genéricos reutilizables

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Helpers IDÉNTICOS a lotes-crud.cy.js:**
  - Mismo código copiado entre archivos

- **Flujos CRUD:**
  - Crear, editar, eliminar con misma estructura

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Cypress:**
- **MOVER helpers a `cypress/support/helpers.js` (COMPARTIDOS con lotes)**
- **Crear custom commands genéricos:**
  - `cy.createEntity(entityType, data)` - genérico para fincas/lotes
  - `cy.editEntity(entityType, id, updates)`
  - `cy.deleteEntity(entityType, id)`

- **Crear helpers específicos:**
  - `fillFincaForm(data)` - mantener pero en helpers compartidos
  - `fillLoteForm(data)` - mantener pero en helpers compartidos

**Tests:**
- Refactorizar para usar helpers centralizados
- Eliminar duplicación entre fincas y lotes

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <10%
- Eliminar helpers duplicados con lotes
- Tests más mantenibles

---

## 🟦 cypress/e2e/auth/password-recovery.cy.js

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~30-40%

**Tipos de duplicidad:**
- Helpers locales duplicados (`verifySelectorsExist`, `clickForgotPasswordLink`, `fillEmailAndSubmit`, `verifySuccessMessage`, `verifyErrorMessage`)
- Flujos de recuperación/reset repetidos
- Patrones de validación duplicados

**Causas principales:**
- Helpers no centralizados
- Falta de abstracción de flujos de recuperación

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Helpers duplicados:**
  ```javascript
  const verifySelectorsExist = (selectors, $context, timeout = 3000) => { ... }
  const clickForgotPasswordLink = (callback) => { ... }
  const fillEmailAndSubmit = (email, successCallback) => { ... }
  const verifySuccessMessage = ($result) => { ... }
  const verifyErrorMessage = ($result, expectedTexts) => { ... }
  ```

- **Flujos repetidos:**
  - Click link → fill email → submit → verify repetido

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Cypress:**
- **MOVER helpers a `cypress/support/helpers.js`**
- **Crear custom commands:**
  - `cy.requestPasswordRecovery(email)`
  - `cy.resetPassword(token, newPassword, confirmPassword)`
  - `cy.verifyPasswordResetSuccess()`

**Tests:**
- Refactorizar para usar helpers centralizados

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <15%
- Eliminar helpers locales
- Tests más claros

---

## 🟦 src/components/charts/AdvancedChart.vue

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~20-25%

**Tipos de duplicidad:**
- Props duplicados con BaseChart.vue
- Handlers de eventos similares
- Lógica de merge de opciones duplicada

**Causas principales:**
- Componente wrapper que duplica props del componente base
- Falta de composables para lógica compartida

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Props duplicados:**
  - Mismas props que BaseChart.vue (chartData, options, type, title, height, etc.)

- **Event handlers:**
  - `handleChartClick`, `handleChartHover`, `handleChartLoaded` - solo re-emiten eventos

- **Merged options:**
  - Lógica de merge similar a BaseChart

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Vue:**
- **Crear composable `useChartEvents()`:**
  - Centralizar handlers de eventos
  - Reutilizar en AdvancedChart y BaseChart

- **Simplificar AdvancedChart:**
  - Usar composable para eventos
  - Reducir código duplicado de props

**Tests:**
- Asegurar que composable tenga tests unitarios

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <10%
- Lógica de eventos centralizada
- Componente más simple

---

## 🟦 src/components/charts/BaseChart.vue

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~15-20%

**Tipos de duplicidad:**
- Lógica de procesamiento de datos duplicada
- Configuración de opciones repetida
- Manejo de gradientes similar en otros componentes

**Causas principales:**
- Falta de composables para lógica de charts
- Configuración no centralizada

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Procesamiento de datos:**
  - `processedChartData` - lógica que podría estar en composable

- **Configuración de opciones:**
  - `defaultOptions` - merge de opciones repetido

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Vue:**
- **Ya usa composables (`useChart`, `useChartConfig`) - VERIFICAR si hay duplicación:**
  - Revisar si la lógica está bien separada
  - Asegurar que no hay código duplicado entre composables

**Tests:**
- Verificar cobertura de composables

### 4️⃣ Objetivo final por archivo

- Mantener estructura actual si composables están bien
- Eliminar cualquier duplicación restante

---

## 🟦 src/components/common/BaseScanPreferences.vue

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~80-90% (con BaseVisualSettings.vue)

**Tipos de duplicidad:**
- **ESTRUCTURA CASI IDÉNTICA a BaseVisualSettings.vue:**
  - Mismo template structure
  - Mismas props (solo cambian defaults)
  - Mismos métodos (`updatePreference` vs `updateSetting` - misma lógica)
  - Mismos handlers (`handleSave`, `handleReset`)

**Causas principales:**
- Componente base duplicado en lugar de uno genérico
- Falta de abstracción para componentes de preferencias/ajustes

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Template idéntico:**
  - Misma estructura HTML
  - Mismos slots
  - Mismos estilos

- **Script casi idéntico:**
  ```javascript
  // BaseScanPreferences
  const updatePreference = (key, value) => {
    const updated = { ...props.modelValue, [key]: value }
    emit('update:modelValue', updated)
  }
  
  // BaseVisualSettings - IDÉNTICO
  const updateSetting = (key, value) => {
    const updated = { ...props.modelValue, [key]: value }
    emit('update:modelValue', updated)
  }
  ```

- **Props idénticas:**
  - Solo cambian defaults de `title`, `saveButtonText`

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Vue:**
- **CREAR componente base genérico `BasePreferences.vue`:**
  - Unificar BaseScanPreferences y BaseVisualSettings
  - Props configurables para personalización
  - Slots para contenido específico

- **Refactorizar componentes existentes:**
  - BaseScanPreferences → usar BasePreferences con props específicas
  - BaseVisualSettings → usar BasePreferences con props específicas
  - O eliminar y usar BasePreferences directamente

**Tests:**
- Actualizar tests para usar componente unificado
- Asegurar que props específicas funcionan

### 4️⃣ Objetivo final por archivo

- **ELIMINAR duplicación completamente (0%)**
- Un solo componente base reutilizable
- Mantener funcionalidad actual

---

## 🟦 src/components/common/BaseVisualSettings.vue

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~80-90% (con BaseScanPreferences.vue)

**Tipos de duplicidad:**
- **IDÉNTICO a BaseScanPreferences.vue** (ver análisis anterior)

### 2️⃣ Código repetido identificado

- **Mismo que BaseScanPreferences.vue**

### 3️⃣ Plan de refactorización (NO ejecutar aún)

- **Mismo plan que BaseScanPreferences.vue:**
  - Unificar en BasePreferences.vue

### 4️⃣ Objetivo final por archivo

- **ELIMINAR archivo** (unificar con BaseScanPreferences)
- O convertir en wrapper de BasePreferences

---

## 🟦 src/components/common/BaseFincaFilters.vue

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~10-15%

**Tipos de duplicidad:**
- Función `generateSecureId` duplicada (también en BaseSearchInput.vue)
- Lógica de debounce similar en otros componentes

**Causas principales:**
- Función de utilidad no centralizada
- Falta de composable para generación de IDs

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Función `generateSecureId` duplicada:**
  ```javascript
  const generateSecureId = (prefix = 'id') => {
    // ... misma implementación en BaseSearchInput.vue
  }
  ```

- **Lógica de debounce:**
  - Similar a otros componentes de búsqueda

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Vue:**
- **Crear utilidad `src/utils/idGenerator.js`:**
  - Mover `generateSecureId` aquí
  - Exportar como función reutilizable

- **Crear composable `useDebounce.js`:**
  - Centralizar lógica de debounce
  - Reutilizar en componentes de búsqueda

**Tests:**
- Tests unitarios para utilidades

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <5%
- Eliminar función duplicada
- Usar utilidades centralizadas

---

## 🟦 src/components/common/BaseSearchInput.vue

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~10-15%

**Tipos de duplicidad:**
- Función `generateSecureId` duplicada (también en BaseFincaFilters.vue)
- Lógica de clases computadas similar en otros inputs

**Causas principales:**
- Función de utilidad no centralizada

### 2️⃣ Código repetido identificado

- **Función `generateSecureId` duplicada** (mismo que BaseFincaFilters)

### 3️⃣ Plan de refactorización (NO ejecutar aún)

- **Mismo plan que BaseFincaFilters.vue:**
  - Mover `generateSecureId` a utilidad centralizada

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <5%
- Usar utilidad centralizada

---

## 🟦 src/components/common/FincasViewComponents/FincaForm.vue

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~85-95% (con src/components/FincaForm.vue)

**Tipos de duplicidad:**
- **ARCHIVO CASI IDÉNTICO a `src/components/FincaForm.vue`:**
  - Mismo template (solo diferencias menores en IDs)
  - Misma lógica de script
  - Mismos métodos
  - Misma validación

**Causas principales:**
- Archivo duplicado en diferentes ubicaciones
- Falta de componente único reutilizable

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Template casi idéntico:**
  - Misma estructura HTML
  - Solo diferencias en IDs de inputs (`finca-form-nombre` vs `finca-nombre`)

- **Script idéntico:**
  - Mismas imports
  - Misma lógica de validación
  - Mismos métodos
  - Misma estructura de formData

- **Diferencias menores:**
  - IDs de inputs
  - Algunos composables vs Swal directo

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Vue:**
- **DECIDIR cuál archivo mantener:**
  - Analizar uso en el proyecto
  - Verificar cuál es más completo/actualizado

- **Unificar en un solo componente:**
  - Mantener el más completo
  - Eliminar el duplicado
  - Actualizar imports en todo el proyecto

- **O crear componente base:**
  - Extraer lógica común
  - Crear wrapper específico si es necesario

**Tests:**
- Actualizar tests para usar componente unificado
- Asegurar que funcionalidad se mantiene

### 4️⃣ Objetivo final por archivo

- **ELIMINAR duplicación completamente (0%)**
- Un solo componente FincaForm
- Mantener funcionalidad actual

---

## 🟦 src/components/FincaForm.vue

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~85-95% (con FincasViewComponents/FincaForm.vue)

**Tipos de duplicidad:**
- **IDÉNTICO a FincasViewComponents/FincaForm.vue** (ver análisis anterior)

### 2️⃣ Código repetido identificado

- **Mismo que FincasViewComponents/FincaForm.vue**

### 3️⃣ Plan de refactorización (NO ejecutar aún)

- **Mismo plan que FincasViewComponents/FincaForm.vue:**
  - Unificar en un solo componente
  - Eliminar duplicado

### 4️⃣ Objetivo final por archivo

- **ELIMINAR archivo** (unificar con el otro)
- O mantener uno y eliminar el otro

---

## 🟦 src/components/admin/AdminAgricultorComponents/CreateFarmerModal.vue

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~30-40% (con EditFarmerModal.vue y RegisterForm.vue)

**Tipos de duplicidad:**
- Estructura de formulario similar a EditFarmerModal y RegisterForm
- Campos de información personal duplicados (nombre, apellido, documento, etc.)
- Lógica de validación similar
- Manejo de errores duplicado

**Causas principales:**
- Falta de componentes base para formularios de personas
- Validaciones no centralizadas
- Estructura de campos repetida

### 2️⃣ Código repetido identificado

**Lista de patrones detectados:**

- **Campos de información personal:**
  - Nombre, apellido, tipo documento, número documento - repetidos en múltiples formularios
  - Misma estructura HTML
  - Mismas clases CSS

- **Validaciones:**
  - Validación de email, teléfono, documento - lógica similar en múltiples componentes

- **Manejo de errores:**
  - Misma estructura de `errors` object
  - Mismo patrón de mostrar errores

### 3️⃣ Plan de refactorización (NO ejecutar aún)

**Vue:**
- **Crear componente base `BasePersonForm.vue`:**
  - Extraer campos comunes de información personal
  - Props configurables para campos opcionales/requeridos
  - Slots para campos adicionales

- **Crear composable `usePersonFormValidation()`:**
  - Centralizar validaciones de persona
  - Reutilizar en CreateFarmerModal, EditFarmerModal, RegisterForm

- **Refactorizar componentes:**
  - CreateFarmerModal → usar BasePersonForm + campos específicos
  - EditFarmerModal → usar BasePersonForm + campos específicos
  - RegisterForm → usar BasePersonForm + campos específicos

**Tests:**
- Actualizar tests para usar componentes base
- Tests unitarios para composable de validación

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <20%
- Usar componentes base compartidos
- Mantener funcionalidad actual

---

## 🟦 src/components/admin/AdminAgricultorComponents/EditFarmerModal.vue

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~30-40% (con CreateFarmerModal.vue)

**Tipos de duplicidad:**
- Campos de información personal similares a CreateFarmerModal
- Lógica de validación duplicada
- Estructura de formulario similar

### 2️⃣ Código repetido identificado

- **Similar a CreateFarmerModal.vue** (ver análisis anterior)

### 3️⃣ Plan de refactorización (NO ejecutar aún)

- **Mismo plan que CreateFarmerModal.vue:**
  - Usar BasePersonForm compartido

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <20%
- Compartir componentes base

---

## 🟦 src/components/auth/RegisterForm.vue

### 1️⃣ Resumen de duplicidad encontrada

**Porcentaje reportado:** ~25-35% (con CreateFarmerModal.vue)

**Tipos de duplicidad:**
- Campos de información personal similares
- Validaciones de email, teléfono, documento duplicadas
- Estructura de formulario similar

### 2️⃣ Código repetido identificado

- **Campos de información personal similares a CreateFarmerModal**

### 3️⃣ Plan de refactorización (NO ejecutar aún)

- **Usar BasePersonForm compartido** (ver CreateFarmerModal)

### 4️⃣ Objetivo final por archivo

- Reducir duplicidad a <20%
- Compartir componentes base

---

## RESUMEN GENERAL DE REFACTORIZACIÓN

### Archivos con mayor duplicidad (>50%):
1. **BaseScanPreferences.vue + BaseVisualSettings.vue** - 80-90% duplicados
2. **FincaForm.vue (ambas ubicaciones)** - 85-95% duplicados
3. **upload.cy.js** - 50-60% duplicado
4. **analysis.cy.js** - 40-50% duplicado

### Helpers a centralizar (ALTA PRIORIDAD):
1. `verifySelectorsExist` - usado en 10+ archivos
2. `clickIfExists` - usado en 5+ archivos
3. `selectIfExists` - usado en 5+ archivos
4. `typeIfExists` - usado en 5+ archivos
5. `fillForm` / `fillLoteForm` / `fillFincaForm` - lógica similar
6. `generateSecureId` - duplicado en 2 archivos
7. Helpers de validación - repetidos en múltiples archivos
8. `generatePassword` - usado en múltiples tests (ya corregido pero puede centralizarse)

### Custom Commands a crear:
1. `cy.performImageAnalysis()` - para analysis.cy.js
2. `cy.uploadFile()` - para upload.cy.js
3. `cy.createEntity()` / `cy.editEntity()` / `cy.deleteEntity()` - genéricos CRUD
4. `cy.fillRegisterForm()` - para register.cy.js
5. `cy.interceptError()` - para network-errors.cy.js
6. `cy.navigateTo*()` - para navegación común
7. `cy.fillPersonForm()` - para formularios de personas
8. `cy.waitForAnalysis()` - para esperas de análisis

### Componentes Vue a unificar:
1. **BaseScanPreferences + BaseVisualSettings** → `BasePreferences.vue`
2. **FincaForm (ambas ubicaciones)** → Un solo componente
3. **CreateFarmerModal + EditFarmerModal + RegisterForm** → Usar `BasePersonForm.vue`

### Utilidades a crear:
1. `src/utils/idGenerator.js` - para `generateSecureId`
2. `src/composables/useDebounce.js` - para debounce
3. `src/composables/usePersonFormValidation.js` - para validaciones de persona
4. `cypress/support/helpers.js` - centralizar todos los helpers
5. `cypress/support/selectors.js` - centralizar selectores
6. `cypress/support/intercepts.js` - centralizar intercepts comunes
7. `cypress/support/fixtures/` - organizar fixtures por dominio

### Prioridades de refactorización:

**ALTA PRIORIDAD (duplicación >50%):**
1. Unificar BaseScanPreferences + BaseVisualSettings
2. Unificar FincaForm (ambas ubicaciones)
3. Refactorizar upload.cy.js con custom commands
4. Refactorizar analysis.cy.js con custom commands

**MEDIA PRIORIDAD (duplicación 30-50%):**
5. Centralizar helpers de Cypress (verifySelectorsExist, clickIfExists, etc.)
6. Crear BasePersonForm para formularios de personas
7. Refactorizar network-errors.cy.js
8. Refactorizar validation-forms.cy.js

**BAJA PRIORIDAD (duplicación <30%):**
9. Centralizar generateSecureId
10. Crear composables para lógica compartida
11. Optimizar beforeEach repetidos
12. Centralizar selectores

---

## ANÁLISIS ADICIONALES - ARCHIVOS RESTANTES

### Archivos Cypress con patrones similares:

**Patrón común: beforeEach repetido (54 archivos):**
- `cy.login(role)` + `cy.visit(path)` + `cy.get('body').should('be.visible')`
- **Solución:** Crear custom commands `cy.loginAs(role, path)` que combine todo

**Patrón común: Helpers locales (15+ archivos):**
- `verifySelectorsExist` - duplicado en 10+ archivos
- `clickIfExists` - duplicado en 5+ archivos  
- `fillForm` variantes - duplicado en múltiples archivos
- **Solución:** Mover TODOS a `cypress/support/helpers.js`

**Patrón común: Intercepts (20+ archivos):**
- Misma estructura de `cy.intercept` con `API_BASE_URL`
- **Solución:** Crear helpers en `cypress/support/intercepts.js`

### Archivos Vue con duplicación:

**Componentes de formulario:**
- CreateFarmerModal, EditFarmerModal, RegisterForm - campos de persona duplicados
- **Solución:** BasePersonForm.vue

**Componentes base:**
- BaseScanPreferences ≈ BaseVisualSettings (90% idénticos)
- **Solución:** BasePreferences.vue unificado

**Formularios duplicados:**
- FincaForm.vue (2 ubicaciones) - 95% idénticos
- **Solución:** Un solo componente

### Archivos de servicios/tests:

**Tests con mocks duplicados:**
- Misma estructura de mocks en múltiples archivos de test
- **Solución:** Crear `src/test/mocks/` con mocks reutilizables

---

## PLAN DE EJECUCIÓN RECOMENDADO

### Fase 1: Infraestructura (Semana 1)
1. Crear `cypress/support/helpers.js` - mover todos los helpers
2. Crear `cypress/support/selectors.js` - centralizar selectores
3. Crear `cypress/support/intercepts.js` - centralizar intercepts
4. Crear `src/utils/idGenerator.js` - mover generateSecureId

### Fase 2: Custom Commands (Semana 2)
1. Crear `cy.performImageAnalysis()`
2. Crear `cy.uploadFile()`
3. Crear `cy.createEntity()` / `cy.editEntity()` / `cy.deleteEntity()`
4. Crear `cy.fillRegisterForm()` / `cy.fillPersonForm()`
5. Crear `cy.interceptError()`
6. Crear `cy.navigateTo*()` helpers

### Fase 3: Componentes Vue (Semana 3)
1. Crear `BasePreferences.vue` - unificar BaseScanPreferences + BaseVisualSettings
2. Unificar FincaForm (decidir cuál mantener)
3. Crear `BasePersonForm.vue` - para formularios de personas
4. Refactorizar CreateFarmerModal, EditFarmerModal, RegisterForm

### Fase 4: Refactorización de Tests (Semana 4)
1. Refactorizar upload.cy.js
2. Refactorizar analysis.cy.js
3. Refactorizar network-errors.cy.js
4. Refactorizar validation-forms.cy.js
5. Refactorizar fincas-crud.cy.js y lotes-crud.cy.js

### Fase 5: Optimización Final (Semana 5)
1. Optimizar beforeEach repetidos
2. Centralizar fixtures
3. Revisar y eliminar código muerto
4. Documentar nuevos helpers y commands

---

## MÉTRICAS ESPERADAS POST-REFACTORIZACIÓN

- **Reducción de duplicidad promedio:** 60-70%
- **Reducción de líneas de código:** ~2000-3000 líneas
- **Mejora en mantenibilidad:** Tests más cortos y legibles
- **Tiempo de ejecución de tests:** Potencial mejora por reutilización
- **Facilidad de agregar nuevos tests:** Significativamente mejorada

---

## 🟦 ANÁLISIS ADICIONALES - ARCHIVOS RESTANTES (RESUMEN)

### Archivos Cypress con duplicación media (20-30%):

**cypress/e2e/reports/generation.cy.js:**
- Helpers locales duplicados (`verifySelectorsExist`, `clickIfExists`, `fillFieldIfExists`, `selectOptionIfExists`, `checkCheckboxIfExists`)
- **Plan:** Mover helpers a `cypress/support/helpers.js`

**cypress/e2e/reports/export-sharing.cy.js:**
- Helpers locales duplicados
- Flujos de exportación repetidos
- **Plan:** Crear custom commands `cy.exportReport(format)`, `cy.shareReport(method)`

**cypress/e2e/admin/users_management.cy.js:**
- Helpers locales (`verifyRowFilter`, `filterAndVerifyRows`, `selectAndVerifyRows`, `clickIfExists`, `interactWithFirstRow`, `fillUserForm`)
- **Plan:** Mover helpers a centralizados, crear `cy.fillUserForm()`

**cypress/e2e/reports/filtering.cy.js, reports/reports-management.cy.js, reports/reportes-view.cy.js:**
- Patrones similares de filtrado
- Helpers locales duplicados
- **Plan:** Unificar en helpers compartidos

**cypress/e2e/navigation/complete-flows.cy.js:**
- Flujos completos que combinan múltiples acciones
- **Plan:** Crear custom commands para flujos completos

**cypress/e2e/navigation/ui-ux.cy.js:**
- Helpers locales duplicados
- **Plan:** Mover a helpers centralizados

**cypress/e2e/errors/edge-cases.cy.js:**
- Helpers locales duplicados
- Casos edge repetidos
- **Plan:** Centralizar helpers, crear fixtures para casos edge

**cypress/e2e/analysis/prediction_flow.cy.js:**
- Helper `uploadAndAnalyze` local
- **Plan:** Usar `cy.performImageAnalysis()` cuando esté disponible

**cypress/e2e/integration/full_user_journey.cy.js:**
- Flujo completo que combina múltiples acciones
- **Plan:** Crear custom commands para journey completo

**cypress/e2e/auth/login.cy.js:**
- Helpers locales (`verifySelectorsExist`, `performLoginAction`, `verifyErrorExists`, `verifyEmailError`)
- **Plan:** Mover a helpers centralizados, crear `cy.performLogin()`

**cypress/e2e/auth/logout.cy.js:**
- Flujo simple pero puede usar helpers compartidos
- **Plan:** Usar helpers centralizados

**cypress/e2e/settings/account_profile.cy.js:**
- Patrones de formulario similares
- **Plan:** Usar helpers de formularios compartidos

**cypress/e2e/agricultor/dashboard.cy.js, agricultor/configuracion.cy.js:**
- Helpers locales duplicados
- **Plan:** Mover a helpers centralizados

**cypress/e2e/admin/system_config.cy.js, admin/analytics_dashboard.cy.js:**
- Patrones similares
- **Plan:** Usar helpers compartidos

**cypress/e2e/images/history.cy.js:**
- Helpers locales duplicados
- **Plan:** Mover a helpers centralizados

**cypress/e2e/fincas/advanced_management.cy.js:**
- Helpers locales duplicados
- **Plan:** Mover a helpers centralizados

**cypress/e2e/ui/notifications.cy.js, ui/advanced_forms.cy.js, ui/map_interactions.cy.js:**
- Helpers locales duplicados
- **Plan:** Mover a helpers centralizados

**cypress/e2e/audit/auditoria-view.cy.js, audit/audit_logs.cy.js:**
- Patrones similares
- **Plan:** Usar helpers compartidos

**cypress/e2e/public/general_access.cy.js:**
- Tests simples pero pueden usar helpers
- **Plan:** Usar helpers centralizados

**cypress/e2e/lotes/lotes-view.cy.js:**
- Helpers locales duplicados
- **Plan:** Mover a helpers centralizados

### Archivos Vue con duplicación baja-media:

**src/components/agricultor/configuracion/PasswordSection.vue:**
- Validación de contraseña que puede usar composable
- **Plan:** Usar `usePasswordValidation` si existe

**src/components/common/BaseScanPreferences.vue + BaseVisualSettings.vue:**
- **YA ANALIZADO** - 80-90% duplicados

**src/components/common/FincasViewComponents/FincaForm.vue + FincaForm.vue:**
- **YA ANALIZADO** - 85-95% duplicados

**src/views/Agricultor/AgricultorReportes.vue, AgricultorHistorial.vue, AgricultorConfiguracion.vue:**
- Patrones similares de vistas
- **Plan:** Revisar si hay componentes base compartidos

**src/views/common/FincasView.vue, common/Analisis.vue:**
- Estructuras similares
- **Plan:** Revisar duplicación de lógica

**src/views/Reportes.vue, PredictionView.vue:**
- Patrones similares
- **Plan:** Revisar composables compartidos

**src/views/PasswordResetConfirm.vue:**
- Formulario simple
- **Plan:** Usar helpers de formularios si aplica

**src/components/layout/Common/Sidebar.vue:**
- Componente único, revisar si hay lógica duplicada
- **Plan:** Revisar si hay duplicación con otros componentes de navegación

### Archivos de servicios/composables:

**src/composables/useWebSocket.js:**
- Función `generateSecureId` no presente (ya corregido)
- Lógica de WebSocket bien estructurada
- **Plan:** Revisar si hay duplicación con otros composables de WebSocket

**src/composables/useDateFormatting.js:**
- **BIEN ESTRUCTURADO** - composable centralizado para formateo de fechas
- No hay duplicación significativa

**src/stores/prediction.js:**
- Store bien estructurado
- **Plan:** Revisar si hay lógica duplicada con otros stores

**src/router/index.js:**
- Configuración de rutas
- **Plan:** Revisar si hay guards duplicados o lógica repetida

**src/services/auditApi.js:**
- Servicio API
- **Plan:** Revisar si hay patrones duplicados con otros servicios API

### Archivos de tests unitarios:

**src/components/admin/AdminUserComponents/__tests__/UserFormModal.test.js:**
- Mocks duplicados con otros tests
- **Plan:** Crear `src/test/mocks/` con mocks reutilizables

**src/components/admin/AdminAgricultorComponents/__tests__/CreateFarmerModal.test.js:**
- Mocks similares a UserFormModal
- **Plan:** Centralizar mocks

**src/components/admin/AdminAgricultorComponents/__tests__/EditFarmerModal.test.js:**
- Mocks similares
- **Plan:** Centralizar mocks

**src/components/common/__tests__/GlobalLoader.test.js:**
- Tests simples
- **Plan:** Revisar si hay duplicación

**src/services/__tests__/servicioAnalisis.test.js:**
- Tests de servicio
- **Plan:** Revisar patrones de test duplicados

**src/views/__tests__/Admin/AdminDashboard.test.js:**
- Tests de vista
- **Plan:** Revisar mocks duplicados

**src/router/__tests__/index.test.js:**
- Tests de router
- **Plan:** Revisar si hay duplicación

**src/services/__tests__/lotesApi.test.js, predictionApi.test.js:**
- Tests de servicios
- **Plan:** Revisar patrones duplicados de test

**src/stores/__tests__/ (varios):**
- Tests de stores
- **Plan:** Revisar mocks y patrones duplicados

---

## NOTAS IMPORTANTES

⚠️ **NO EJECUTAR CAMBIOS TODAVÍA** - Este es solo el plan de análisis

✅ **Verificar antes de refactorizar:**
- Ejecutar todos los tests para baseline
- Hacer backup del código actual
- Refactorizar incrementalmente
- Ejecutar tests después de cada cambio

✅ **Orden recomendado:**
1. Primero: Infraestructura (helpers, selectors)
2. Segundo: Custom commands
3. Tercero: Componentes Vue
4. Cuarto: Refactorizar tests uno por uno

✅ **Estrategia de refactorización:**
- **Incremental:** Un archivo a la vez
- **Verificación continua:** Tests después de cada cambio
- **Documentación:** Actualizar documentación de helpers/commands
- **Comunicación:** Informar al equipo de cambios en helpers compartidos

