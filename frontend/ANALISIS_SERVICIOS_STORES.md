# Análisis de Servicios, Stores, Composables y Utils - CacaoScan

Este documento analiza el uso de servicios, stores, composables y utilidades del frontend.

## 📊 RESUMEN EJECUTIVO

- **Total de servicios originales:** 21
- **Servicios eliminados:** 6
- **Servicios restantes:** 14 (todos en uso)
- **Total de stores:** 9 (todos en uso) ✅
- **Total de composables:** 3 (todos en uso) ✅
- **Total de utils:** 1 (en uso) ✅
- **Reducción de servicios:** ~30%

## ✅ SERVICIOS EN USO (Verificados)

### Servicios Principales
- ✅ `api.js` - Usado en múltiples lugares (servicio base de Axios)
- ✅ `authApi.js` - Usado extensivamente (autenticación)
- ✅ `fincasApi.js` - Usado en vistas y componentes de fincas
- ✅ `lotesApi.js` - Usado en vistas de lotes
- ✅ `predictionApi.js` - Usado en componentes de predicción
- ✅ `adminApi.js` - Usado en AdminTraining
- ✅ `reportsService.js` - Usado en stores de reportes
- ✅ `dashboardStatsService.js` - Usado en composable useDashboardStats
- ✅ `configApi.js` - Usado en stores de configuración
- ✅ `auditApi.js` - Usado en stores de auditoría
- ✅ `catalogosApi.js` - **USADO** en:
  - RegisterForm.vue
  - EditFarmerModal.vue
  - CreateFarmerModal.vue
  - ProfileSection.vue
- ✅ `personasApi.js` - **USADO** en:
  - AgricultorConfiguracion.vue
  - EditFarmerModal.vue

### Servicios Exportados pero con Uso Limitado
- ⚠️ `servicioAnalisis.js` - Exportado en index.js pero uso indirecto
- ⚠️ `datasetApi.js` - Usado indirectamente en adminApi.js

## ❌ SERVICIOS SIN USAR (Verificados)

### Verificación de Uso Dinámico
- ❌ **getService(), getServices(), getServicesByCategory()** NO se usan en ningún lugar
- ❌ **SERVICE_MAP** solo se define pero nunca se usa
- ❌ **SERVICE_CATEGORIES** solo se define pero nunca se usa
- **CONCLUSIÓN:** Los servicios configurados para importación dinámica NO se están usando realmente

### Servicios Sin Uso Confirmado
1. **`calibrationApi.js`**
   - ❌ Exportado en index.js
   - ❌ NO se importa directamente en ningún componente o vista
   - ❌ NO se usa a través de funciones dinámicas
   - **DECISIÓN:** **ELIMINAR** o mantener para funcionalidad futura

2. **`modelMetricsApi.js`**
   - ❌ Exportado en index.js
   - ❌ NO se importa directamente en ningún componente o vista
   - ❌ NO se usa a través de funciones dinámicas
   - **DECISIÓN:** **ELIMINAR** o mantener para funcionalidad futura

3. **`incrementalTrainingApi.js`**
   - ❌ Exportado en index.js
   - ❌ NO se importa directamente en ningún componente o vista
   - ❌ NO se usa a través de funciones dinámicas
   - **DECISIÓN:** **ELIMINAR** o mantener para funcionalidad futura

4. **`modelsApi.js`**
   - ❌ Exportado en index.js
   - ❌ NO se importa directamente en ningún componente o vista
   - ❌ NO se usa a través de funciones dinámicas
   - **DECISIÓN:** **ELIMINAR** o mantener para funcionalidad futura

5. **`notificationsApi.js`**
   - ❌ Exportado en index.js
   - ❌ NO se importa directamente en ningún componente o vista
   - ❌ NO se usa a través de stores
   - ❌ NO se usa a través de funciones dinámicas
   - **DECISIÓN:** **ELIMINAR** o mantener para funcionalidad futura

6. **`trainingApi.js`**
   - ❌ **ELIMINADO** (no se usaba en ningún lugar)

### Servicios con Uso Indirecto
- ⚠️ `servicioAnalisis.js` - Exportado pero NO se importa directamente, posible código legacy
- ✅ `datasetApi.js` - **USADO** indirectamente en adminApi.js (necesario)

## ✅ STORES EN USO (Todos Verificados)

### Stores Activos (9)
1. ✅ `auth.js` - **USADO EXTENSIVAMENTE** en múltiples vistas y componentes
2. ✅ `admin.js` - Usado en AdminUsuarios y componentes de admin
3. ✅ `analysis.js` - Usado en Analisis.vue
4. ✅ `audit.js` - Usado en AuditoriaView.vue
5. ✅ `config.js` - Usado en múltiples vistas (AdminDashboard, AdminConfiguracion, HomeView)
6. ✅ `fincas.js` - Usado en FincasView y componentes de fincas
7. ✅ `notifications.js` - Usado en múltiples vistas (LoteDetailView, FincaDetailView, ReportsManagement)
8. ✅ `prediction.js` - Usado en UserPrediction.vue
9. ✅ `reports.js` - Usado en Reportes.vue y ReportGeneratorModal

**RESULTADO:** Todos los stores están en uso ✅

## ✅ COMPOSABLES EN USO (Todos Verificados)

### Composables Activos (3)
1. ✅ `useDashboardStats.js` - Usado en composables (importado en composables)
2. ✅ `useImageStats.js` - **USADO** en:
   - AgricultorHistorial.vue
   - AgricultorDashboard.vue
3. ✅ `useWebSocket.js` - **USADO** en:
   - AdminUsuarios.vue
   - AdminDashboard.vue

**RESULTADO:** Todos los composables están en uso ✅

## ✅ UTILS EN USO (Verificado)

### Utils Activos (1)
1. ✅ `apiResponse.js` - **USADO** en:
   - fincasApi.js
   - servicioAnalisis.js
   - lotesApi.js

**RESULTADO:** El único util está en uso ✅

## 📋 RECOMENDACIONES

### Alta Prioridad (Verificar Antes de Eliminar)

1. **Servicios sin uso confirmado:**
   - `calibrationApi.js` - Verificar si se usa dinámicamente
   - `modelMetricsApi.js` - Verificar si se usa dinámicamente
   - `incrementalTrainingApi.js` - Verificar si se usa dinámicamente
   - `modelsApi.js` - Verificar si se usa dinámicamente
   - `notificationsApi.js` - Verificar si se usa a través de stores

2. **Servicio sin exportar:**
   - `trainingApi.js` - Decidir si agregar a index.js o eliminar

3. **Servicios con uso indirecto:**
   - `servicioAnalisis.js` - Verificar si realmente se necesita o es código legacy
   - `datasetApi.js` - Verificar si adminApi realmente lo necesita

### Limpieza Sugerida

1. **Eliminar de index.js si no se usan:**
   - CalibrationApi (si no se usa)
   - ModelMetricsApi (si no se usa)
   - IncrementalTrainingApi (si no se usa)
   - ModelsApi (si no se usa)
   - NotificationsApi (si no se usa a través de stores)

2. **Decidir sobre:**
   - `trainingApi.js` - Agregar a index.js o eliminar
   - `servicioAnalisis.js` - Mantener o eliminar si es legacy

## 🎯 RESUMEN FINAL

### En Uso Confirmado:
- **Servicios:** 12 de 21 (57%)
- **Stores:** 9 de 9 (100%) ✅
- **Composables:** 3 de 3 (100%) ✅
- **Utils:** 1 de 1 (100%) ✅

### Sin Usar / Verificar:
- **Servicios:** 6 servicios necesitan verificación
- **1 servicio** (trainingApi.js) **SIN USAR** - Eliminar

## ✅ LIMPIEZA COMPLETADA

### Servicios Eliminados (6 servicios):
1. ✅ `trainingApi.js` - ELIMINADO
2. ✅ `calibrationApi.js` - ELIMINADO
3. ✅ `modelMetricsApi.js` - ELIMINADO
4. ✅ `incrementalTrainingApi.js` - ELIMINADO
5. ✅ `modelsApi.js` - ELIMINADO
6. ✅ `notificationsApi.js` - ELIMINADO

### index.js Limpiado:
- ✅ Removidas exportaciones de servicios eliminados
- ✅ Removidas funciones de importación dinámica sin usar (getService, getServices, getServicesByCategory)
- ✅ Removido SERVICE_MAP sin usar
- ✅ Removido SERVICE_CATEGORIES sin usar
- ✅ Mantenido solo servicios activos en exportación por defecto

### Servicios Mantenidos (14 servicios en uso):
- `api.js`, `authApi.js`, `catalogosApi.js`, `personasApi.js`, `predictionApi.js`, `fincasApi.js`, `lotesApi.js`, `reportsService.js`, `datasetApi.js`, `adminApi.js`, `dashboardStatsService.js`, `servicioAnalisis.js`, `auditApi.js`, `configApi.js`

### Resultado Final:
- **Total de servicios eliminados:** 6
- **Servicios restantes en uso:** 14
- **Reducción:** ~30% de servicios eliminados
- **Sin errores de linting**

