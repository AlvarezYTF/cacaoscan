# Componentes de Administración - Feature 5.1: Gestión de Dataset

Esta implementación sigue los principios de desarrollo **SOLID**, **DRY** y **KISS** para crear una interfaz administrativa modular y mantenible.

## Arquitectura Implementada

### Principios Aplicados

#### **SOLID**
- **SRP (Single Responsibility Principle)**: Cada componente tiene una responsabilidad única y bien definida
- **OCP (Open/Closed Principle)**: Componentes extensibles sin modificación del código existente
- **LSP (Liskov Substitution Principle)**: Interfaces consistentes y predecibles
- **ISP (Interface Segregation Principle)**: Props y eventos específicos, no interfaces genéricas
- **DIP (Dependency Inversion Principle)**: Componentes dependen de abstracciones (servicios API)

#### **DRY (Don't Repeat Yourself)**
- Funciones utilitarias centralizadas en `datasetApi.js`
- Componentes reutilizables con props configurables
- Lógica de formateo y validación compartida

#### **KISS (Keep It Simple, Stupid)**
- Interfaces simples e intuitivas
- Lógica clara y directa
- Configuración mínima necesaria

## Componentes Desarrollados

### 1. `datasetApi.js` - Servicio API (DRY + KISS)

**Responsabilidad**: Centralizar toda la comunicación con el backend para gestión de datasets.

```javascript
// Funciones principales
getDatasetImages(filters, page, pageSize)     // Obtener imágenes paginadas
uploadDatasetImages(files, metadata, onProgress) // Subir múltiples imágenes
updateDatasetImage(imageId, updateData)       // Actualizar imagen específica
bulkUpdateDatasetImages(imageIds, updateData) // Actualización masiva
exportDatasetCSV(filters)                     // Exportar datos a CSV
trainRegressionModel(trainingParams)          // Entrenar modelo regresión
trainVisionModel(trainingParams)              // Entrenar modelo visión
validateDataIntegrity()                       // Validar integridad de datos
```

**Principios aplicados**:
- **DRY**: Funciones `handleResponse()`, `buildQueryParams()`, `getCommonHeaders()` reutilizables
- **KISS**: Interfaces simples con parámetros opcionales inteligentes
- **SRP**: Una función por responsabilidad específica

**Características técnicas**:
- ✅ Manejo centralizado de errores HTTP
- ✅ Validación de archivos client-side
- ✅ Construcción automática de parámetros de consulta
- ✅ Formateo de datos consistente
- ✅ Configuración exportable (`DATASET_CONFIG`)

### 2. `DatasetUpload.vue` - Componente de Subida (SRP)

**Responsabilidad única**: Manejar la subida de múltiples imágenes al dataset con validación y progreso.

```vue
<DatasetUpload
  :max-files="50"
  :auto-upload="false"
  @upload-start="handleUploadStart"
  @upload-progress="handleUploadProgress"
  @upload-complete="handleUploadComplete"
  @upload-error="handleUploadError"
/>
```

**Principios aplicados**:
- **SRP**: Solo gestión de upload, sin lógica de listado o edición
- **OCP**: Extensible via props sin modificar código interno
- **DRY**: Utiliza funciones del servicio API compartido

**Funcionalidades**:
- ✅ **Drag & Drop**: Arrastrar y soltar múltiples archivos
- ✅ **Validación client-side**: Formato, tamaño, cantidad
- ✅ **Preview**: Lista de archivos seleccionados con detalles
- ✅ **Progreso**: Indicador de progreso por archivo y total
- ✅ **Metadatos**: Formulario para lote, origen y notas
- ✅ **Error handling**: Manejo granular de errores por archivo

### 3. `DatasetTable.vue` - Componente de Tabla (Modular)

**Responsabilidad**: Mostrar, filtrar, ordenar y gestionar imágenes del dataset de forma tabular.

```vue
<DatasetTable
  :auto-refresh="true"
  :refresh-interval="30000"
  @item-view="handleItemView"
  @item-edit="handleItemEdit"
  @item-delete="handleItemDelete"
  @bulk-edit="handleBulkEdit"
  @bulk-delete="handleBulkDelete"
  @data-refresh="handleDataRefresh"
/>
```

**Principios aplicados**:
- **SRP**: Solo visualización y gestión de tabla
- **OCP**: Configurable via props, extensible via slots
- **DRY**: Reutiliza componente `Pagination` existente y funciones de API

**Funcionalidades modulares**:
- ✅ **Filtros avanzados**: Por calidad, estado, lote, origen
- ✅ **Ordenamiento**: Por cualquier columna con indicadores visuales
- ✅ **Selección múltiple**: Checkbox para operaciones masivas
- ✅ **Paginación**: Integrada con componente reutilizable
- ✅ **Acciones por fila**: Ver, editar, eliminar
- ✅ **Operaciones masivas**: Editar/eliminar múltiples elementos
- ✅ **Exportación**: CSV con filtros aplicados
- ✅ **Auto-refresh**: Actualización automática configurable

### 4. `AdminDataset.vue` - Vista Principal (Integración)

**Responsabilidad**: Coordinar todos los componentes y proporcionar funcionalidades administrativas completas.

**Principios aplicados**:
- **SRP**: Solo coordinación, delegando responsabilidades específicas
- **DIP**: Depende de abstracciones (servicios API) no implementaciones
- **ISP**: Interfaces específicas para cada componente

**Secciones integradas**:

#### **Header con Estadísticas**
```javascript
// Stats en tiempo real
total_images: 1250
processed_images: 1180
avg_quality_score: 85%
```

#### **Sección de Upload (Colapsable)**
- Integración completa del componente `DatasetUpload`
- Refresh automático tras subida exitosa
- Notificaciones de estado

#### **Tabla de Dataset**
- Integración del componente `DatasetTable`
- Manejo coordinado de eventos
- Confirmaciones para operaciones críticas

#### **Entrenamiento de Modelos**
```javascript
// Funcionalidades implementadas
initiateTraining('regression' | 'vision')
startTrainingStatusPolling(jobId)
stopTrainingStatusPolling()
```

#### **Validación de Datos**
```javascript
// Verificación de integridad
validateDataIntegrity()
// Genera reporte detallado de problemas
```

#### **Resumen Estadístico**
- Dashboard con métricas del dataset
- Distribución de calidad visualizada
- Uso de almacenamiento
- Dimensiones promedio

## Estructura de Archivos

```
frontend/src/
├── services/
│   └── datasetApi.js              # Servicio API centralizado (DRY)
├── components/
│   └── admin/
│       ├── DatasetUpload.vue      # Componente upload (SRP)
│       ├── DatasetTable.vue       # Componente tabla (Modular)
│       └── README.md              # Esta documentación
└── views/
    └── AdminDataset.vue           # Vista principal (Integración)
```

## Flujo de Datos

### 1. Carga Inicial
```javascript
AdminDataset.vue → loadStats() → datasetApi.getDatasetStats()
                → DatasetTable → loadData() → datasetApi.getDatasetImages()
```

### 2. Subida de Archivos
```javascript
DatasetUpload → processFiles() → datasetApi.uploadDatasetImages()
             → @upload-complete → AdminDataset.refreshData()
             → DatasetTable.refreshData() + loadStats()
```

### 3. Operaciones de Tabla
```javascript
DatasetTable → handleSort() → datasetApi.getDatasetImages(sortedFilters)
            → handleFilter() → datasetApi.getDatasetImages(filteredParams)
            → exportData() → datasetApi.exportDatasetCSV()
```

### 4. Entrenamiento de Modelos
```javascript
AdminDataset → initiateTraining() → datasetApi.trainRegressionModel()
            → startPolling() → datasetApi.getTrainingJobStatus()
            → Auto-update UI con progreso en tiempo real
```

## Configuración y Personalización

### Variables de Configuración (DATASET_CONFIG)
```javascript
{
  MAX_FILE_SIZE: 20MB,
  MAX_BULK_OPERATIONS: 100,
  SUPPORTED_FORMATS: ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff'],
  DEFAULT_PAGE_SIZE: 20,
  STATS_REFRESH_INTERVAL: 30000ms,
  JOB_STATUS_REFRESH_INTERVAL: 2000ms
}
```

### Props Configurables

#### DatasetUpload
- `maxFiles`: Máximo archivos permitidos
- `autoUpload`: Subida automática al seleccionar

#### DatasetTable  
- `autoRefresh`: Actualización automática
- `refreshInterval`: Intervalo de actualización

#### AdminDataset
- Sin props - Vista de nivel superior

## Patrones de Diseño Utilizados

### 1. **Service Layer Pattern** (DRY)
- `datasetApi.js` actúa como capa de servicio
- Centraliza lógica de comunicación con backend
- Funciones reutilizables en múltiples componentes

### 2. **Event-Driven Architecture** (SRP)
- Comunicación entre componentes via eventos
- Cada componente emite eventos específicos de su responsabilidad
- Vista principal coordina mediante event handlers

### 3. **Configuration Object Pattern** (KISS)
- `DATASET_CONFIG` centraliza configuración
- Fácil modificación sin cambiar código
- Valores por defecto sensatos

### 4. **Observer Pattern** (Responsivo)
- Auto-refresh en DatasetTable
- Polling de estado de entrenamiento
- Actualizaciones reactivas de estadísticas

## Manejo de Errores

### Nivel de Servicio (datasetApi.js)
```javascript
// Error handling centralizado
handleResponse(response) {
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
}
```

### Nivel de Componente
```javascript
// Error handling específico por componente
try {
  const result = await uploadDatasetImages(files, metadata);
  emit('upload-complete', result);
} catch (error) {
  emit('upload-error', error);
}
```

### Nivel de Vista
```javascript
// Error handling coordinado
const showError = (message) => {
  errorMessage.value = message;
  showErrorMessage.value = true;
  setTimeout(() => showErrorMessage.value = false, 5000);
};
```

## Testing y Debugging

### Logging Estructurado
```javascript
// En desarrollo
if (import.meta.env.DEV) {
  console.log('Dataset operation:', { operation, params, result });
}
```

### Validaciones Client-Side
```javascript
// Validación antes de envío
const validation = validateImageFile(file);
if (!validation.isValid) {
  return { success: false, error: validation.error };
}
```

### Estado de Debugging
```javascript
// Acceso al estado desde consola del navegador
window.datasetStore = { stats, trainingJobs, validationReports };
```

## Mejores Prácticas Implementadas

### 1. **Separación de Responsabilidades** (SOLID)
- Servicio API: Solo comunicación backend
- DatasetUpload: Solo subida de archivos  
- DatasetTable: Solo visualización de datos
- AdminDataset: Solo coordinación

### 2. **Reutilización de Código** (DRY)
- Funciones utilitarias compartidas
- Componentes configurables y extensibles
- Servicios centralizados

### 3. **Simplicidad de Interfaz** (KISS)
- Props mínimas necesarias
- Eventos descriptivos y específicos
- Configuración por defecto sensata

### 4. **Mantenibilidad**
- Código autodocumentado
- Estructura clara y consistente
- Fácil localización de funcionalidades

## Próximos Pasos

### Funcionalidades Futuras
- **Batch processing avanzado**: Operaciones masivas optimizadas
- **Filtros inteligentes**: Búsqueda por similitud visual
- **Análisis de calidad**: Detección automática de defectos
- **Versionado de dataset**: Control de versiones de datos
- **Colaboración**: Múltiples administradores concurrentes

### Optimizaciones
- **Virtual scrolling**: Para tablas con miles de registros
- **Lazy loading**: Carga diferida de imágenes
- **Caching inteligente**: Cache de consultas frecuentes
- **Compresión**: Optimización de transferencia de datos

---

## Uso Rápido

### Acceso a la Vista
```
URL: /admin/dataset
Permisos: requiresAuth: true, requiresAdmin: true
```

### Importación de Componentes
```javascript
// En otro componente
import DatasetUpload from '@/components/admin/DatasetUpload.vue';
import DatasetTable from '@/components/admin/DatasetTable.vue';

// Uso del servicio
import { getDatasetImages, uploadDatasetImages } from '@/services/datasetApi.js';
```

### Ejemplo de Integración
```vue
<template>
  <div>
    <DatasetUpload @upload-complete="refreshTable" />
    <DatasetTable ref="table" @data-refresh="updateStats" />
  </div>
</template>

<script>
export default {
  methods: {
    refreshTable() {
      this.$refs.table.refreshData();
    },
    updateStats(info) {
      console.log('Datos actualizados:', info);
    }
  }
};
</script>
```

La implementación está **100% completa** y lista para uso en producción, siguiendo estrictamente los principios de desarrollo solicitados.
