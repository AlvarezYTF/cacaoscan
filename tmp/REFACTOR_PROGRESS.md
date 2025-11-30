# Progreso de Refactorización - Reducción de Duplicación de Código

**Fecha:** 2025-01-27  
**Estado:** FASE 1 Completada ✅ | FASE 2 Muy Avanzada (Casi Completa) 🔄

**Última Actualización:** Todos los stores principales refactorizados para usar `apiErrorHandler` de forma consistente.

## Resumen Ejecutivo

Se ha completado la FASE 1 (bajo riesgo) y se está avanzando en la FASE 2 (riesgo medio) del plan de refactorización para reducir la duplicación de código en el frontend Vue 3.

## FASE 1: COMPLETADA ✅

### Composables Creados

1. **`usePagination.js`** ✅
   - Estado de paginación reactivo
   - Métodos para navegación (next, previous, goToPage)
   - Sincronización con respuestas API
   - Computed properties para UI

2. **`useTable.js`** ✅
   - Lógica de sorting (key, order)
   - Selección de filas (opcional)
   - Filtrado básico
   - Procesamiento de datos

3. **`useForm.js`** ✅
   - Gestión completa de formularios
   - Validación integrada
   - Manejo de errores del servidor
   - Integración con catalogos
   - Helpers para campos comunes

### Utilidades Creadas

1. **`formFieldConfigs.js`** ✅
   - Configuraciones centralizadas de campos comunes
   - Definiciones de validación
   - Grupos de campos predefinidos

2. **`apiClient.js`** ✅
   - Cliente API unificado
   - Wrappers para axios y fetch
   - Manejo consistente de errores
   - Helpers para requests paginados

### Servicios Migrados a apiClient

1. **`dashboardStatsService.js`** ✅
   - Migrado de axios directo a `apiGet` y `apiPost`
   - Eliminada configuración duplicada de interceptores
   - Reducción de ~40 líneas de código

2. **`reportsService.js`** ✅
   - Migrado de fetch directo a `fetchGet`, `fetchPost`, `fetchDelete`
   - Eliminada lógica duplicada de headers y manejo de errores
   - Reducción de ~80 líneas de código

3. **`fincasApi.js`** ✅
   - Migrado de api.get/post/put/delete a `apiGet`, `apiPost`, `apiPut`, `apiDelete`
   - Eliminados try-catch duplicados
   - Reducción de ~60 líneas de código

4. **`lotesApi.js`** ✅
   - Migrado de api.get/post/put/delete a `apiGet`, `apiPost`, `apiPut`, `apiDelete`
   - Eliminados try-catch duplicados
   - Reducción de ~40 líneas de código

5. **`personasApi.js`** ✅
   - Migrado de api.get/post/patch a `apiGet`, `apiPost`, `apiPatch`
   - Eliminados try-catch duplicados
   - Reducción de ~30 líneas de código

6. **`configApi.js`** ✅
   - Migrado de api.get/put a `apiGet`, `apiPut`
   - Mantiene lógica especial de manejo de errores (403/500)
   - Reducción de ~40 líneas de código

7. **`datasetApi.js`** ✅
   - Migrado parcialmente a `apiClient` (funciones que no requieren FormData)
   - Funciones con FormData mantienen fetch directo
   - Reducción de ~100 líneas de código

8. **`adminApi.js`** ✅
   - Migrado parcialmente a `apiClient` (funciones simples)
   - Eliminada función `makeRequest` duplicada
   - Funciones complejas mantienen su lógica especial
   - Reducción de ~80 líneas de código

9. **`catalogosApi.js`** ✅
   - Migrado de `api.get` a `apiGet` de `apiClient`
   - Mantiene lógica de fallback para compatibilidad
   - Reducción de ~30 líneas de código

10. **`auditApi.js`** ✅
   - Migrado de `api.get` a `apiGet` de `apiClient`
   - Mantiene manejo de errores personalizado
   - Reducción de ~40 líneas de código

### Componentes Base Creados

1. **`BaseFormField.vue`** ✅
   - Componente reutilizable para campos de formulario
   - Maneja labels, errores, help text
   - Soporta múltiples tipos de input

2. **`BaseTable.vue`** ✅
   - Tabla genérica reutilizable
   - Integra useTable y usePagination
   - Soporta sorting, selection, pagination

3. **`BaseModal.vue`** ✅
   - Modal reutilizable con slots
   - Maneja transiciones y overlay
   - Consistente en toda la aplicación

4. **`BaseTimeline.vue`** ✅
   - Componente timeline genérico
   - Estructura común para cronologías
   - Soporta slots para personalización

### Ejemplos Creados

1. **`BaseFormField.example.vue`** ✅
   - Ejemplo completo de uso de BaseFormField
   - Demuestra reducción de código duplicado
   - Incluye múltiples tipos de campos (text, email, tel, select, textarea)

### Mejoras Realizadas

1. **`useFormValidation.js`** ✅
   - Agregados helpers para campos comunes
   - Métodos mejorados de validación
   - Mejor integración con formularios

### Componentes Migrados

1. **`AuditoriaView.vue`** ✅
   - Ahora usa `usePagination`
   - Sincronización con store mantenida

2. **`Reportes.vue`** ✅
   - Ahora usa `usePagination`
   - Sincronización con store mantenida

3. **`AuditTable.vue`** ✅
   - Ahora usa `useTable` para sorting
   - Usa `useAuditHelpers` consistentemente
   - Usa `useDateFormatting` para formateo

4. **`ReportsTable.vue`** ✅
   - Ahora usa `useTable` para sorting
   - Migrado a Composition API

## FASE 1: COMPLETADA ✅ (Actualización)

### Nuevos Composables Creados

1. **`useAuthForm.js`** ✅
   - Lógica centralizada para formularios de autenticación
   - Validación de email/username y password
   - Manejo de estado de formulario
   - Reducción de ~300 líneas en LoginForm.vue

2. **`useFileUpload.js`** ✅
   - Lógica de upload de archivos con drag-drop
   - Preview de imágenes
   - Validación de archivos
   - Reducción de ~150 líneas en ImageUpload.vue

3. **`useChartConfig.js`** ✅
   - Configuración centralizada de Chart.js
   - Manejo de temas (light/dark)
   - Procesamiento de datasets y colores
   - Reducción de ~150 líneas en AdvancedChart.vue

### Nuevos Componentes Base Creados

1. **`BaseCard.vue`** ✅
   - Componente base genérico para cards
   - Slots para header, body, footer, actions
   - Variantes de estilo (success, error, warning, info)
   - Reducción de ~200 líneas en AuditCard.vue

2. **`BaseHistoryCard.vue`** ✅
   - Componente base para cards de historial
   - Paginación integrada
   - Filtros opcionales
   - Reducción de ~150 líneas en ImageHistoryCard.vue

### Componentes Migrados (FASE 1 - Nueva)

1. **`LoginForm.vue`** ✅
   - Migrado a usar `useAuthForm.js`
   - Eliminada lógica duplicada de validación
   - Reducción de ~300 líneas

2. **`ImageUpload.vue`** ✅
   - Migrado a usar `useFileUpload.js`
   - Eliminada lógica duplicada de drag-drop y preview
   - Reducción de ~150 líneas

3. **`AdvancedChart.vue`** ✅
   - Migrado a usar `useChartConfig.js`
   - Eliminada lógica duplicada de configuración de gráficos
   - Reducción de ~150 líneas

4. **`AuditCard.vue`** ✅
   - Migrado a usar `BaseCard.vue`
   - Estructura simplificada
   - Reducción de ~200 líneas

5. **`ImageHistoryCard.vue`** ✅
   - Migrado a usar `BaseHistoryCard.vue`
   - Lógica de paginación centralizada
   - Reducción de ~150 líneas

## FASE 1 EXTENDED: EN PROGRESO 🔄

### Nuevos Componentes Base Creados

1. **`BaseToggleSwitch.vue`** ✅
   - Toggle switch reutilizable
   - Soporta múltiples colores y tamaños
   - Accesible con ARIA labels
   - Maneja estados disabled y error

2. **`BaseSpinner.vue`** ✅
   - Spinner de carga reutilizable
   - Múltiples tamaños (xs, sm, md, lg, xl)
   - Múltiples colores
   - Soporte para fullScreen overlay
   - Texto opcional

3. **`BaseHero.vue`** ✅
   - Sección hero reutilizable
   - Badge, título, subtítulo configurables
   - CTA buttons con slots
   - Trust indicators
   - Decoraciones opcionales

4. **`BaseLandingSection.vue`** ✅
   - Sección de landing page reutilizable
   - Título y subtítulo configurables
   - Slots para contenido personalizado
   - Diseño responsive

5. **`BaseStatsCard.vue`** ✅
   - Tarjeta de estadísticas reutilizable
   - Icono, valor, label, trend
   - Múltiples esquemas de color
   - Slots para personalización

### Composables Mejorados

1. **`usePasswordValidation.js`** ✅
   - Funciones de validación mejoradas
   - Soporte para reglas adicionales (specialChar)
   - Función `getPasswordRequirements` para checklist
   - Función `validatePassword` unificada
   - Mensajes de error configurables

### Cypress Support Mejorado

1. **`commands.js`** ✅
   - Helpers genéricos CRUD agregados
   - `createEntity`, `updateEntity`, `deleteEntity`
   - `logoutWithConfirmation` helper
   - `validateFormErrors` helper
   - `interactWithTableRow` helper
   - `navigateTablePage` helper
   - `applyTableFilter` y `clearTableFilters` helpers

2. **`selectors.js`** ✅
   - Ya existe y está bien estructurado

3. **`test-data.js`** ✅
   - Ya existe con factory functions

## FASE 2 EXTENDED: COMPLETADA ✅

### Nuevos Componentes Base Creados

1. **`BaseFincaCard.vue`** ✅
   - Tarjeta reutilizable para fincas
   - Slots para header, body, stats, actions
   - Soporte para status badges
   - Clickable y eventos personalizables

2. **`BaseFincaList.vue`** ✅
   - Lista genérica con estados de carga/error/vacío
   - Integración con componentes de item
   - Slots para personalización
   - Grid layout configurable

3. **`BaseFincaFilters.vue`** ✅
   - Componente de filtros reutilizable
   - Búsqueda con debounce
   - Slots para filtros personalizados
   - Botón de limpiar filtros

4. **`BaseChart.vue`** ✅
   - Wrapper genérico para Chart.js
   - Soporta múltiples tipos (line, bar, pie, doughnut, radar)
   - Opciones configurables
   - Auto-destrucción y actualización

5. **`BaseScanPreferences.vue`** ✅
   - Componente reutilizable para preferencias de escaneo
   - Slots para campos personalizados
   - Botones de acción configurables

6. **`BaseVisualSettings.vue`** ✅
   - Componente reutilizable para ajustes visuales
   - Slots para campos personalizados
   - Botones de acción configurables

7. **`BaseAuthForm.vue`** ✅
   - Formulario de autenticación reutilizable
   - Soporta login/register/reset modes
   - Slots para campos y botones
   - Manejo de estados y errores

8. **`BaseDashboardWidget.vue`** ✅
   - Widget de dashboard reutilizable
   - Header, body, footer con slots
   - Variantes de color
   - Iconos configurables

### Composables Mejorados

1. **`useDashboardStats.js`** ✅
   - Funciones de transformación de datos agregadas
   - `transformToChartData` - Convierte datos raw a formato chart
   - `aggregateByPeriod` - Agrega datos por período de tiempo
   - `filterByDateRange` - Filtra datos por rango de fechas
   - `getCacheKey` - Generador de claves de caché

### Utilidades Mejoradas

1. **`imageValidationUtils.js`** ✅
   - `validateImageDimensions` - Validación de dimensiones de imagen
   - `validateMultipleImages` - Validación de múltiples imágenes
   - `formatFileSize` - Formateo de tamaño de archivo
   - `isImageFile` - Verificación de extensión de imagen

### Migraciones Completadas

1. **`SummaryCard.vue`** ✅
   - Migrado a usar `BaseStatsCard`
   - Reducción de ~70 líneas

2. **`FarmersStatsCards.vue`** ✅
   - Migrado a usar `BaseStatsCard`
   - Reducción de ~100 líneas

3. **`ToggleSwitch.vue` (AdminConfigComponents)** ✅
   - Migrado a usar `BaseToggleSwitch`
   - Reducción de ~120 líneas

4. **`LoadingSpinner.vue` (AdminGeneralComponents)** ✅
   - Migrado a usar `BaseSpinner`
   - Reducción de ~100 líneas

5. **Imports actualizados** ✅
   - `DashboardCharts.vue` - Actualizado a `BaseSpinner`
   - `LoginForm.vue` - Actualizado a `BaseSpinner`
   - `UsersTable.vue` - Actualizado a `BaseSpinner`

6. **`BarChart.vue`** ✅
   - Migrado a usar `BaseChart`
   - Reducción de ~160 líneas

7. **`PieChart.vue`** ✅
   - Migrado a usar `BaseChart`
   - Reducción de ~80 líneas

6. **`LineChart.vue`** ✅
   - Migrado a usar `BaseChart`
   - Reducción de ~100 líneas

7. **`BarChart.vue`** ✅
   - Migrado a usar `BaseChart`
   - Reducción de ~160 líneas

8. **`PieChart.vue`** ✅
   - Migrado a usar `BaseChart`
   - Reducción de ~80 líneas

7. **`ScanPreferencesSection.vue`** ✅
   - Migrado a usar `BaseScanPreferences`
   - Reducción de ~50 líneas

8. **`VisualSettingsSection.vue`** ✅
   - Migrado a usar `BaseVisualSettings`
   - Reducción de ~50 líneas

9. **`FincaList.vue` (FincasViewComponents)** ✅
   - Migrado a usar `BaseFincaList`
   - Reducción de ~100 líneas

10. **`FincasFilters.vue`** ✅
    - Migrado a usar `BaseFincaFilters`
    - Reducción de ~80 líneas

11. **`FincaCardActions.vue`** ✅
    - Creado como componente auxiliar para acciones de fincas
    - Extraído de `FincaCard.vue`

## FASE 2: EN PROGRESO 🔄

### Servicios y Utilidades Creados (FASE 2 - Nueva)

1. **`apiErrorHandler.js`** ✅
   - Manejo centralizado de errores de API
   - Tipos de error específicos (network, timeout, validation, etc.)
   - Mensajes de error user-friendly
   - Extracción de errores de validación
   - Reducción de ~200 líneas de código duplicado

### Composables de Stores Creados (FASE 2 - Nueva)

1. **`useStoreBase.js`** ✅
   - Estado base para stores (loading, error)
   - Métodos comunes (setLoading, setError, clearError)
   - Helper executeAction para acciones async
   - Reducción de ~50 líneas por store

2. **`usePaginableStore.js`** ✅
   - Lógica de paginación para stores
   - Estado de paginación reactivo
   - Métodos para navegación de páginas
   - Sincronización con respuestas API
   - Reducción de ~40 líneas por store con paginación

3. **`useFilterableStore.js`** ✅
   - Lógica de filtrado para stores
   - Estado de filtros reactivo
   - Métodos para aplicar filtros
   - Computed para filtros activos
   - Reducción de ~30 líneas por store con filtros

### Composables de WebSocket Creados (FASE 2 - Nueva)

1. **`useWebSocketBase.js`** ✅
   - Composable base para conexiones WebSocket
   - Manejo de conexión/desconexión
   - Reconexión automática
   - Heartbeat
   - Reducción de ~100 líneas por implementación

2. **`useWebSocketManager.js`** ✅
   - Gestor de múltiples conexiones WebSocket
   - Usa useWebSocketBase para cada conexión
   - Métodos para conectar/desconectar todas
   - Reducción de ~50 líneas

3. **`useWebSocket.js`** ✅ (Refactorizado)
   - Migrado para usar `useWebSocketBase`
   - Conexiones creadas dinámicamente con URLs correctas
   - Lógica de mensajes específica mantenida
   - Reducción de ~200 líneas de código duplicado

### Composables de Dominio Creados (FASE 2 - Nueva)

1. **`usePrediction.js`** ✅
   - Composable para operaciones de predicción
   - Manejo centralizado de diferentes métodos (traditional, yolo, smart, cacaoscan)
   - Mapeo de respuestas API
   - Manejo de errores integrado
   - Reducción de ~150 líneas por componente que lo use

2. **`useDataset.js`** ✅
   - Composable para operaciones de datasets
   - Gestión de imágenes del dataset
   - Paginación y filtros integrados
   - Operaciones CRUD centralizadas
   - Reducción de ~100 líneas por componente que lo use

3. **`useFincas.js`** ✅
   - Composable para operaciones de fincas
   - Gestión de fincas con paginación y filtros
   - Operaciones CRUD centralizadas
   - Manejo de errores integrado
   - Reducción de ~120 líneas por componente que lo use

### Componentes Migrados a useFincas (FASE 2 - Nueva)

1. **`FincaDetailModal.vue`** ✅
   - Migrado a usar `useFincas` para cargar detalles
   - Eliminada lógica duplicada de carga de finca
   - Reducción de ~50 líneas

2. **`FincaForm.vue`** ✅
   - Migrado a usar `useFincas` para crear/actualizar
   - Eliminada lógica duplicada de guardado
   - Reducción de ~70 líneas

3. **`ReportGenerator.vue`** ✅
   - Migrado a usar `useFincas` para cargar fincas
   - Eliminada lógica duplicada de carga
   - Reducción de ~30 líneas

4. **`EditFarmerModal.vue`** ✅
   - Migrado a usar `useFincas` para cargar y crear fincas
   - Eliminada lógica duplicada de carga y creación
   - Reducción de ~50 líneas

### Componentes Migrados a Servicios API (FASE 2 - Nueva)

1. **`ImageHistoryCard.vue`** ✅
   - Migrado a usar `predictionApi` en lugar de fetch directo
   - Eliminada lógica duplicada de carga y descarga de imágenes
   - Manejo de errores centralizado con `apiErrorHandler`
   - Reducción de ~60 líneas

### Router Guards Refactorizados (FASE 2 - Nueva)

1. **`guardFactories.js`** ✅
   - Factories para crear guards reutilizables
   - createAuthGuard, createRoleGuard, createVerifiedGuard, etc.
   - Helpers para rutas de redirección
   - Reducción de ~300 líneas en guards.js

2. **`guards.js`** ✅
   - Refactorizado para usar guardFactories
   - Guards simplificados usando factories
   - Reducción de ~200 líneas

### Servicios API Refactorizados (FASE 2 - Nueva)

1. **`predictionApi.js`** ✅
   - Refactorizado para usar `apiErrorHandler`
   - Manejo de errores centralizado
   - Reducción de ~100 líneas de código duplicado

### Stores Refactorizados (FASE 2 - Nueva)

1. **`prediction.js`** ✅
   - Refactorizado para usar `apiErrorHandler`
   - Manejo de errores consistente
   - Reducción de ~50 líneas

2. **`admin.js`** ✅
   - Refactorizado para usar `apiErrorHandler`
   - Todos los métodos con manejo de errores centralizado
   - Reducción de ~80 líneas

3. **`reports.js`** ✅
   - Refactorizado para usar `apiErrorHandler`
   - Todos los métodos con manejo de errores centralizado
   - Reducción de ~60 líneas

4. **`fincas.js`** ✅
   - Refactorizado para usar `apiErrorHandler`
   - Todos los métodos (fetchFincas, fetchById, create, update, remove, activate) ahora usan manejo de errores centralizado
   - Reducción de ~40 líneas

5. **`analysis.js`** ✅
   - Refactorizado para usar `apiErrorHandler`
   - Manejo de errores centralizado en submitBatch
   - Reducción de ~20 líneas

6. **`audit.js`** ✅
   - Refactorizado para usar `apiErrorHandler`
   - Todos los métodos ahora usan manejo de errores centralizado
   - Reducción de ~60 líneas

7. **`notifications.js`** ✅
   - Refactorizado para usar `apiErrorHandler`
   - Todos los métodos ahora usan manejo de errores centralizado
   - Reducción de ~50 líneas

### Componentes Base Creados (FASE 2 - Anterior)

1. **`BaseFormField.vue`** ✅
   - Campo de formulario reutilizable
   - Soporte para: text, email, tel, password, textarea, select, date
   - Validación visual integrada
   - Mensajes de error automáticos

2. **`BaseTable.vue`** ✅
   - Tabla genérica mejorada
   - Integración con `useTable` y `usePagination`
   - Sorting y selección integrados
   - Slots para personalización
   - Responsive por defecto

### Modales Migrados a BaseModal

1. **`UserActivityModal.vue`** ✅
   - Migrado a `BaseModal`
   - Usa `usePagination`
   - Reducción significativa de código

2. **`ReportPreviewModal.vue`** ✅
   - Migrado a `BaseModal`
   - Usa `useAuditHelpers` para formatJson
   - Estilos simplificados

3. **`AuditDetailsModal.vue`** ✅
   - Migrado a `BaseModal`
   - Usa `useAuditHelpers` consistentemente
   - Usa `useDateFormatting` para fechas

4. **`AuditStatsModal.vue`** ✅
   - Migrado a `BaseModal`
   - Estructura simplificada

5. **`CreateFarmerModal.vue`** ✅
   - Migrado a `BaseModal`
   - Mantiene toda la funcionalidad del formulario
   - Footer con botones de acción

6. **`EditFarmerModal.vue`** ✅
   - Migrado a `BaseModal`
   - Mantiene funcionalidad de tabs (Información Personal / Fincas)
   - Footer con botones de acción

7. **`FarmerDetailModal.vue`** ✅
   - Migrado a `BaseModal`
   - Header personalizado con avatar del agricultor
   - Mantiene toda la funcionalidad de visualización

8. **`UserFormModal.vue`** ✅
   - Migrado a `BaseModal`
   - Mantiene toda la funcionalidad del formulario
   - Soporta modo create/edit

9. **`UserDetailsModal.vue`** ✅
   - Migrado a `BaseModal`
   - Mantiene toda la funcionalidad de visualización
   - Botón de edición condicional

10. **`FincaDetailModal.vue`** ✅
   - Migrado a `BaseModal`
   - Header personalizado con información de la finca
   - Mantiene toda la funcionalidad de visualización
   - Botones de acción en footer

### Componentes de Auditoría Mejorados

1. **`AuditTable.vue`** ✅
   - Usa `useTable` y `useAuditHelpers`

2. **`AuditCard.vue`** ✅
   - Ya usa `useAuditHelpers` correctamente

3. **`AuditTimeline.vue`** ✅
   - Ya usa `useAuditHelpers` correctamente

## Próximos Pasos

### Pendientes en FASE 2

1. ✅ Migrar más modales a BaseModal:
   - ✅ `EditFarmerModal.vue`
   - ✅ `CreateFarmerModal.vue`
   - ✅ `FincaDetailModal.vue`
   - ✅ `UserFormModal.vue`
   - ✅ `UserDetailsModal.vue`
   - `ReportGeneratorModal.vue` (complejo, wizard multi-paso - requiere más trabajo)

2. ✅ Demostrar uso de BaseFormField:
   - ✅ Ejemplo creado en `BaseFormField.example.vue`
   - ✅ Migración parcial en `UserFormModal.vue` (4 campos)
   - Documentar patrones de uso

3. Migrar más componentes a usar BaseTable:
   - Reemplazar DataTable donde sea apropiado

4. ✅ Unificar servicios API:
   - ✅ `dashboardStatsService.js` migrado a `apiClient`
   - ✅ `reportsService.js` migrado a `apiClient`

### FASE 3 (Futuro)

1. Unificar servicios API
2. Crear BaseForm component completo
3. Refactorizar stores de Pinia
4. Crear BaseTimeline component
5. Refactorizar routing patterns

## Métricas de Reducción

### Líneas de Código Reducidas (Estimado)

- **usePagination**: ~50-100 líneas por vista que lo use
- **useTable**: ~30-50 líneas por tabla
- **BaseModal**: ~100-200 líneas por modal migrado
- **useAuditHelpers**: ~20-30 líneas por componente de auditoría

### Vistas Migradas a usePagination

1. **`AdminAgricultores.vue`** ✅
   - Migrado de paginación local a `usePagination` composable
   - Reducción de ~15 líneas de código

2. **`AdminUsuarios.vue`** ✅
   - Migrado de paginación local a `usePagination` composable
   - Integrado con respuesta API del store
   - Reducción de ~20 líneas de código

3. **`FincaLotesView.vue`** ✅
   - Migrado de paginación local a `usePagination` composable
   - Reducción de ~15 líneas de código

### Total Estimado Reducido Hasta Ahora

- **FASE 1 (Original)**: ~200-300 líneas
- **FASE 1 (Nueva)**: ~950 líneas (useAuthForm, useFileUpload, useChartConfig, BaseCard, BaseHistoryCard, migraciones)
- **FASE 2 (Anterior)**: ~1900-2300 líneas
- **FASE 2 (Nueva)**: ~2550 líneas (apiErrorHandler, composables de stores, WebSocket, composables de dominio, componentes migrados a useFincas, componentes migrados a servicios API, guards, servicios, stores completamente refactorizados, ImageUpload)
- **Total**: ~5900-6500 líneas de código duplicado eliminadas

**Desglose detallado:**
- Modales migrados: ~1000-1150 líneas (10 modales × ~100-115 líneas cada uno)
- Servicios unificados: ~540-600 líneas (10 servicios migrados)
- Vistas migradas a usePagination: ~50 líneas (3 vistas)
- Componentes base creados (Fase 1-2 original): ~200-300 líneas (BaseModal, BaseTable, BaseFormField, BaseTimeline)
- Componentes base creados (Fase 1 extendida): ~400-500 líneas (BaseToggleSwitch, BaseSpinner, BaseHero, BaseLandingSection, BaseStatsCard)
- Componentes base creados (Fase 2 extendida): ~600-800 líneas (BaseFincaCard, BaseFincaList, BaseFincaFilters, BaseChart, BaseScanPreferences, BaseVisualSettings, BaseAuthForm, BaseDashboardWidget)
- Composables mejorados: ~100-150 líneas (usePasswordValidation, useDashboardStats)
- Utilidades mejoradas: ~50-100 líneas (imageValidationUtils)
- Cypress commands mejorados: ~100-150 líneas (helpers genéricos CRUD)
- Campos de formulario migrados a BaseFormField: ~30-40 líneas (4 campos en UserFormModal)
- Componentes de auditoría mejorados: ~50-100 líneas

**Desglose FASE 2 (Anterior):**
- Modales migrados: ~1000-1150 líneas (10 modales × ~100-115 líneas cada uno)
- Servicios unificados: ~150-200 líneas (2 servicios migrados a apiClient)
- Componentes de auditoría mejorados: ~50-100 líneas
- Composables y utilidades: ~50-100 líneas

**Desglose FASE 2 (Nueva):**
- apiErrorHandler: ~200 líneas
- Composables de stores: ~120 líneas (useStoreBase, usePaginableStore, useFilterableStore)
- Composables de WebSocket: ~350 líneas (useWebSocketBase, useWebSocketManager, useWebSocket refactorizado)
- Composables de dominio: ~370 líneas (usePrediction, useDataset, useFincas)
- Componentes migrados a useFincas: ~200 líneas (FincaDetailModal, FincaForm, ReportGenerator, EditFarmerModal)
- Componentes migrados a servicios API: ~60 líneas (ImageHistoryCard)
- Router guards: ~500 líneas (guardFactories, guards refactorizado)
- Servicios API: ~100 líneas (predictionApi refactorizado)
- Stores completamente refactorizados: ~350 líneas (prediction, admin, reports, fincas, analysis, audit, notifications - todos los métodos ahora usan apiErrorHandler)
- ImageUpload refactorizado: ~150 líneas adicionales (ahora usa usePrediction)

**Resumen de Stores Refactorizados:**
- ✅ `prediction.js` - Todos los métodos usan apiErrorHandler
- ✅ `admin.js` - Todos los métodos usan apiErrorHandler (14 métodos)
- ✅ `reports.js` - Todos los métodos usan apiErrorHandler
- ✅ `fincas.js` - Todos los métodos usan apiErrorHandler (6 métodos)
- ✅ `analysis.js` - submitBatch usa apiErrorHandler
- ✅ `audit.js` - Todos los métodos usan apiErrorHandler (10 métodos)
- ✅ `notifications.js` - Todos los métodos usan apiErrorHandler (12 métodos)

## Notas de Implementación

### Patrones Establecidos

1. **Paginación**: Usar `usePagination` y sincronizar con stores mediante `watch`
2. **Tablas**: Usar `useTable` para sorting, `BaseTable` para UI
3. **Modales**: Usar `BaseModal` con slots para header/footer
4. **Formularios**: Usar `useForm` para lógica, `BaseFormField` para campos
5. **Auditoría**: Usar `useAuditHelpers` para toda lógica de formateo

### Compatibilidad

- Todos los cambios mantienen compatibilidad hacia atrás
- Los stores existentes siguen funcionando
- Los componentes pueden migrarse gradualmente

