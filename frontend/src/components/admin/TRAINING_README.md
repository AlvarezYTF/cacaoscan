# Componentes de Reentrenamiento - Feature 5.2: Panel de Reentrenamiento

Esta implementación sigue los principios de desarrollo **SOLID**, **DRY** y **KISS** para crear un panel administrativo especializado en reentrenamiento de modelos ML.

## Arquitectura Implementada

### Principios Aplicados

#### **SOLID**
- **SRP (Single Responsibility Principle)**: Cada componente tiene una responsabilidad única específica
  - `adminApi.js`: Solo funciones administrativas avanzadas
  - `ModelTraining.vue`: Solo interfaz de configuración de entrenamiento
  - `AdminTraining.vue`: Solo coordinación y monitoreo de entrenamientos
- **OCP (Open/Closed Principle)**: Extensible mediante configuraciones sin modificar código
- **LSP (Liskov Substitution Principle)**: Interfaces consistentes y predecibles
- **ISP (Interface Segregation Principle)**: APIs específicas, no interfaces genéricas
- **DIP (Dependency Inversion Principle)**: Depende de abstracciones (servicios API)

#### **DRY (Don't Repeat Yourself)**
- **Reutilización inteligente**: `adminApi.js` extiende funcionalidad de `datasetApi.js` sin duplicar código
- **Configuraciones centralizadas**: Presets de entrenamiento reutilizables
- **Utilidades compartidas**: Funciones de formateo y validación

#### **KISS (Keep It Simple, Stupid)**
- **Presets predefinidos**: Configuraciones simples (Rápido, Estándar, Producción)
- **Interfaces intuitivas**: Formularios claros con validación en tiempo real
- **Feedback inmediato**: Estimaciones de tiempo y validaciones visuales

## Archivos Desarrollados

### 1. `adminApi.js` - Servicio Administrativo Especializado (SRP + DRY)

**Responsabilidad única**: Proporcionar funcionalidades administrativas avanzadas para entrenamiento de modelos.

```javascript
// Reutilización inteligente (DRY)
import { 
  trainRegressionModel as baseTrainRegression,
  trainVisionModel as baseTrainVision,
  getTrainingJobStatus as baseGetJobStatus,
  getTrainingJobs as baseGetJobs,
  formatNumber
} from './datasetApi.js';

// Funciones extendidas (SRP)
startAdvancedTraining(modelType, config, dataFilters, experimentData)
getTrainingHistory(filters)
getMultipleJobStatus(jobIds)
cancelTrainingJob(jobId)
getModelMetrics(jobId)
compareModels(jobIds)
createExperiment(experimentData)
validateTrainingConfig(modelType, config)
estimateTrainingTime(modelType, config, datasetSize)
```

**Características técnicas avanzadas**:
- ✅ **Configuraciones predefinidas**: 3 presets (Rápido, Estándar, Producción)
- ✅ **Filtros avanzados de datos**: Por calidad, tipo, período temporal
- ✅ **Gestión de experimentos**: Naming, descripción, tags automáticos
- ✅ **Estimación de tiempo**: Cálculo automático basado en dataset y configuración
- ✅ **Validación completa**: Parámetros de entrenamiento con feedback inmediato
- ✅ **Comparación de modelos**: Análisis comparativo de múltiples entrenamientos
- ✅ **Manejo de jobs concurrentes**: Estado de múltiples entrenamientos simultáneos

#### **Presets de Entrenamiento (KISS)**
```javascript
TRAINING_PRESETS = {
  FAST: {
    name: 'Entrenamiento Rápido',
    description: 'Para pruebas rápidas y desarrollo',
    regression: { epochs: 20, learning_rate: 0.01, batch_size: 64 },
    vision: { epochs: 15, learning_rate: 0.001, batch_size: 32 }
  },
  STANDARD: {
    name: 'Entrenamiento Estándar', 
    description: 'Configuración balanceada para uso general',
    regression: { epochs: 50, learning_rate: 0.001, batch_size: 32 },
    vision: { epochs: 30, learning_rate: 0.0005, batch_size: 16 }
  },
  PRODUCTION: {
    name: 'Entrenamiento de Producción',
    description: 'Máxima calidad para modelos en producción',
    regression: { epochs: 100, learning_rate: 0.0005, batch_size: 16 },
    vision: { epochs: 50, learning_rate: 0.0001, batch_size: 8 }
  }
}
```

#### **Filtros Avanzados de Datos (Modular)**
```javascript
DATA_FILTERS = {
  QUALITY_LEVELS: {
    ALL: { min_quality_score: 0.0, label: 'Todos los datos' },
    HIGH: { min_quality_score: 0.8, label: 'Solo alta calidad (>80%)' },
    MEDIUM: { min_quality_score: 0.6, label: 'Calidad media y alta (>60%)' }
  },
  DATA_TYPES: {
    ALL: { label: 'Todos los tipos' },
    PROCESSED_ONLY: { only_processed: true, label: 'Solo datos procesados' },
    MANUAL_ONLY: { only_manual_verified: true, label: 'Solo verificados manualmente' }
  },
  TIME_RANGES: {
    LAST_MONTH: { days_back: 30, label: 'Último mes' },
    LAST_3_MONTHS: { days_back: 90, label: 'Últimos 3 meses' },
    CUSTOM: { label: 'Rango personalizado' }
  }
}
```

### 2. `ModelTraining.vue` - Componente de Configuración (SRP)

**Responsabilidad única**: Proporcionar interfaz para configuración avanzada de entrenamientos de modelos ML.

```vue
<ModelTraining
  :available-dataset-size="datasetSize"
  :auto-refresh-interval="2000"
  @training-started="handleTrainingStarted"
  @training-completed="handleTrainingCompleted"
  @training-failed="handleTrainingFailed"
  @training-cancelled="handleTrainingCancelled"
/>
```

**Funcionalidades implementadas** (SRP):

#### **Selección de Modelo (KISS)**
- **Interfaz visual**: Cards clicables para Regresión y Visión
- **Información contextual**: Descripción clara de cada tipo
- **Validación automática**: Solo permite tipos válidos

#### **Configuración por Presets (KISS)**
- **3 niveles predefinidos**: Rápido, Estándar, Producción
- **Customización avanzada**: Modo personalizado con todos los parámetros
- **Adaptación automática**: Parámetros se ajustan al tipo de modelo seleccionado

#### **Parámetros de Entrenamiento (Configurables)**
```javascript
// Parámetros configurables
trainingConfig = {
  model_type: 'regression' | 'vision',
  epochs: 1-1000,
  learning_rate: 0.00001-1,
  batch_size: 1-256,
  validation_split: 0.1-0.5,
  early_stopping: boolean
}
```

#### **Filtros de Datos Avanzados (Modular)**
- **Filtro de calidad**: Todos, Alta calidad (>80%), Media y alta (>60%)
- **Filtro de tipo**: Todos, Solo procesados, Solo verificados manualmente
- **Filtro temporal**: Último mes, Últimos 3 meses, Rango personalizado

#### **Información de Experimento (Estructurada)**
```javascript
experimentData = {
  name: 'Auto-generado o personalizado',
  description: 'Descripción del objetivo',
  tags: ['producción', 'optimizado', 'v2'], // Array de tags
  tagsInput: 'producción, optimizado, v2' // Input string
}
```

#### **Estimación de Entrenamiento (KISS)**
- **Tiempo estimado**: Cálculo automático basado en configuración
- **Finalización aproximada**: Hora estimada de finalización
- **Validación en tiempo real**: Errores de configuración mostrados inmediatamente

#### **Progreso en Tiempo Real (Durante entrenamiento)**
```javascript
// Estado de entrenamiento activo
currentTraining = {
  job_id: 'uuid',
  model_type: 'regression',
  progress: 45.5, // Porcentaje
  current_epoch: 45,
  total_epochs: 100,
  current_loss: 0.125,
  validation_accuracy: 0.876,
  elapsed_time: 2750 // segundos
}
```

### 3. `AdminTraining.vue` - Vista Principal de Coordinación (Integración)

**Responsabilidad**: Coordinar todos los aspectos del reentrenamiento y proporcionar monitoreo completo.

```vue
<!-- Estructura de la vista -->
<template>
  <!-- Header con estadísticas rápidas -->
  <!-- Grid de 3 columnas en desktop, 1 en mobile -->
  <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
    <!-- Columnas izquierdas (2/3): Configuración e Historial -->
    <div class="xl:col-span-2">
      <!-- Componente ModelTraining -->
      <!-- Historial de entrenamientos con filtros -->
    </div>
    
    <!-- Columna derecha (1/3): Monitoreo y Estadísticas -->
    <div>
      <!-- Monitor de entrenamientos activos -->
      <!-- Estadísticas rápidas -->
      <!-- Comparación de modelos -->
    </div>
  </div>
</template>
```

**Secciones integradas**:

#### **Header con Estadísticas (Dashboard)**
```javascript
// Stats en tiempo real
activeTrainings.length // Entrenamientos en ejecución
completedToday        // Completados hoy
refreshAll()          // Actualización manual
```

#### **Configuración de Entrenamiento (Delegada)**
- **Integración completa**: Componente `ModelTraining`
- **Event handling**: Manejo coordinado de eventos de entrenamiento
- **Estado sincronizado**: Actualización automática tras cambios

#### **Historial de Entrenamientos (Filtrable y Detallado)**
```javascript
// Filtros de historial
historyFilters = {
  model_type: '', // 'regression' | 'vision' | ''
  status: '',     // 'running' | 'completed' | 'failed' | 'cancelled' | ''
  date_from: '',  // ISO date string
  date_to: ''     // ISO date string
}

// Funcionalidades del historial
loadTrainingHistory() // Carga con filtros aplicados
cancelJob(jobId)      // Cancelación directa desde historial
viewMetrics(job)      // Ver métricas detalladas
viewJobDetails(job)   // Ver detalles completos
```

#### **Monitor de Entrenamientos Activos (Tiempo Real)**
- **Lista en vivo**: Solo entrenamientos con status 'running'
- **Progreso visual**: Barras de progreso animadas
- **Información clave**: Época actual, tiempo transcurrido, progreso porcentual
- **Actualización automática**: Cada 5 segundos cuando hay entrenamientos activos

#### **Estadísticas Rápidas (Dashboard)**
```javascript
stats = {
  completed: 15,  // Total completados
  running: 2,     // En ejecución actualmente
  failed: 1,      // Fallidos
  avgTrainingTime: 1250 // Tiempo promedio en segundos
}
```

#### **Comparación de Modelos (Avanzada)**
- **Selección múltiple**: Hasta 3 modelos para comparar
- **Filtrado inteligente**: Solo modelos completados
- **Análisis comparativo**: Métricas lado a lado

#### **Sistema de Notificaciones (Coordinado)**
```javascript
// Tipos de notificación
notificationType = 'success' | 'error' | 'info'

// Eventos manejados
handleTrainingStarted()   // Entrenamiento iniciado exitosamente  
handleTrainingCompleted() // Entrenamiento completado con éxito
handleTrainingFailed()    // Entrenamiento falló con error
handleTrainingCancelled() // Entrenamiento cancelado por usuario
```

## Flujo de Datos y Arquitectura

### 1. **Inicio de Entrenamiento (Event-Driven)**
```javascript
// Flujo completo de inicio
ModelTraining → selectPreset() → validateConfig() → estimateTime()
             → handleStartTraining() → adminApi.startAdvancedTraining()
             → @training-started → AdminTraining.handleTrainingStarted()
             → updateHistorial() + showNotification()
```

### 2. **Monitoreo en Tiempo Real (Polling)**
```javascript
// Polling automático para entrenamientos activos
AdminTraining → startAutoRefresh() → setInterval(loadTrainingHistory, 5000)
ModelTraining → startStatusPolling() → setInterval(getTrainingJobStatus, 2000)
```

### 3. **Gestión de Estado (Coordinated)**
```javascript
// Estados sincronizados entre componentes
AdminTraining: {
  trainingHistory,    // Lista completa de entrenamientos
  activeTrainings,    // Computed: solo entrenamientos activos
  completedJobs,      // Computed: solo entrenamientos completados
  stats              // Computed: estadísticas calculadas
}

ModelTraining: {
  currentTraining,    // Entrenamiento actual en progreso
  trainingConfig,     // Configuración del formulario
  validationErrors,   // Errores de validación en tiempo real
  trainingEstimation  // Estimación de tiempo calculada
}
```

### 4. **Comunicación Entre Componentes (Event-Based)**
```javascript
// Eventos específicos y tipados
@training-started   → { job, config, filters, experiment }
@training-completed → { job_id, final_metrics, training_time }
@training-failed    → { job_id, error, partial_metrics }
@training-cancelled → { job_id, elapsed_time, reason }
```

## Configuración y Personalización

### **Variables de Configuración Avanzada**
```javascript
ADMIN_TRAINING_CONFIG = {
  // Intervalos de actualización optimizados
  STATUS_REFRESH_INTERVAL: 2000,   // Estado de jobs individuales
  METRICS_REFRESH_INTERVAL: 5000,  // Métricas de rendimiento
  
  // Límites de sistema
  MAX_CONCURRENT_JOBS: 3,          // Entrenamientos simultáneos
  MAX_EXPERIMENT_NAME_LENGTH: 100, // Nombres de experimento
  MAX_DESCRIPTION_LENGTH: 500,     // Descripciones
  
  // Personalización visual
  STATUS_COLORS: {
    pending: 'yellow',
    running: 'blue', 
    completed: 'green',
    failed: 'red',
    cancelled: 'gray'
  }
}
```

### **Configuración de Presets Personalizable**
```javascript
// Fácil modificación de presets existentes
TRAINING_PRESETS.CUSTOM = {
  name: 'Mi Configuración',
  description: 'Configuración personalizada para mi caso de uso',
  regression: { epochs: 75, learning_rate: 0.002, batch_size: 24 },
  vision: { epochs: 40, learning_rate: 0.0003, batch_size: 12 }
}
```

## Patrones de Diseño Implementados

### 1. **Specialization Pattern** (SRP)
- `adminApi.js` especializa y extiende funcionalidad de `datasetApi.js`
- Cada componente maneja una responsabilidad específica del entrenamiento
- Separación clara entre configuración, monitoreo y coordinación

### 2. **Configuration Pattern** (KISS)
- Presets predefinidos para casos de uso comunes
- Configuración por excepción (solo cambiar lo necesario)
- Valores por defecto sensatos y validados

### 3. **Observer Pattern** (Reactive)
- Auto-refresh cuando hay entrenamientos activos
- Polling de estado con intervalos adaptativos
- Notificaciones reactivas a cambios de estado

### 4. **Event-Driven Architecture** (SOLID)
- Comunicación entre componentes via eventos tipados
- Loose coupling entre configuración y monitoreo
- State management centralizado pero distribuido

### 5. **Factory Pattern** (DRY)
- Generación automática de configuraciones basadas en presets
- Creación de experimentos con naming automático
- Construcción de filtros de datos combinables

## Funcionalidades Avanzadas

### **Estimación Inteligente de Tiempo**
```javascript
// Cálculo basado en modelo, configuración y dataset
const estimateTrainingTime = (modelType, config, datasetSize) => {
  const timeFactors = {
    regression: 0.1, // 0.1 segundos por época por 1000 muestras
    vision: 2.0      // 2 segundos por época por 1000 muestras
  };
  
  const factor = timeFactors[modelType];
  const epochsPerBatch = Math.ceil(datasetSize / config.batch_size);
  const estimatedSecondsPerEpoch = (epochsPerBatch * factor * datasetSize) / 1000;
  const totalSeconds = estimatedSecondsPerEpoch * config.epochs;
  
  return {
    totalSeconds,
    formatted: formatDuration(totalSeconds),
    estimatedCompletion: new Date(Date.now() + totalSeconds * 1000)
  };
};
```

### **Validación Completa de Configuración**
```javascript
// Validación específica por tipo de modelo
const validateTrainingConfig = (modelType, config) => {
  const errors = [];
  
  // Validaciones básicas universales
  if (config.epochs < 1 || config.epochs > 1000) {
    errors.push('Épocas debe estar entre 1 y 1000');
  }
  
  // Validaciones específicas por tipo
  if (modelType === 'vision' && config.batch_size > 64) {
    errors.push('Para modelos de visión, batch size recomendado es máximo 64');
  }
  
  return { isValid: errors.length === 0, errors };
};
```

### **Gestión de Experimentos Estructurada**
```javascript
// Auto-generación de nombres descriptivos
const generateExperimentName = (modelType, preset, date) => {
  return `${modelType}_${preset.toLowerCase()}_${date}`;
};

// Metadata automática de experimentos
const experimentData = {
  name: generateExperimentName(),
  description: userDescription,
  tags: ['auto-generated', modelType, preset],
  created_by: currentUser.id,
  dataset_snapshot: datasetStats.version
};
```

### **Comparación Avanzada de Modelos**
```javascript
// Análisis comparativo automatizado
const compareModels = async (jobIds) => {
  const metrics = await Promise.all(
    jobIds.map(id => getModelMetrics(id))
  );
  
  return {
    comparison: metrics,
    bestPerforming: findBestModel(metrics),
    recommendations: generateRecommendations(metrics),
    visualizations: prepareChartData(metrics)
  };
};
```

## Manejo de Errores y Resilencia

### **Error Handling Granular**
```javascript
// Diferentes tipos de errores manejados específicamente
try {
  const job = await startAdvancedTraining(config);
} catch (error) {
  if (error.code === 'INSUFFICIENT_DATA') {
    showNotification('Dataset insuficiente para entrenamiento', 'error');
  } else if (error.code === 'CONFIG_INVALID') {
    showValidationErrors(error.details);
  } else if (error.code === 'RESOURCE_LIMIT') {
    showNotification('Límite de entrenamientos concurrentes alcanzado', 'error');
  } else {
    showNotification('Error inesperado en entrenamiento', 'error');
  }
}
```

### **Recovery y Continuación**
```javascript
// Recuperación automática de entrenamientos interrumpidos
const recoverInterruptedTrainings = async () => {
  const runningJobs = await getTrainingJobs({ status: 'running' });
  
  runningJobs.forEach(job => {
    startStatusPolling(job.job_id); // Reanudar monitoreo
  });
};
```

### **Timeouts y Fallbacks**
```javascript
// Timeouts configurables para diferentes operaciones
const CONFIG_TIMEOUTS = {
  START_TRAINING: 30000,    // 30 segundos para iniciar
  STATUS_UPDATE: 10000,     // 10 segundos para estado
  METRICS_LOAD: 15000,      // 15 segundos para métricas
  MODEL_COMPARISON: 60000   // 60 segundos para comparación
};
```

## Testing y Debugging

### **Estado de Debug Accesible**
```javascript
// Acceso desde consola para debugging
if (import.meta.env.DEV) {
  window.adminTrainingDebug = {
    trainingHistory: trainingHistory.value,
    activeTrainings: activeTrainings.value,
    currentConfig: trainingConfig,
    lastEstimation: trainingEstimation.value
  };
}
```

### **Logging Estructurado**
```javascript
// Logging detallado para troubleshooting
const logTrainingEvent = (event, data) => {
  console.log(`[AdminTraining:${event}]`, {
    timestamp: new Date().toISOString(),
    event,
    data,
    currentState: {
      activeTrainings: activeTrainings.value.length,
      historyCount: trainingHistory.value.length
    }
  });
};
```

### **Validación de Estado Consistente**
```javascript
// Verificación de consistencia entre componentes
const validateStateConsistency = () => {
  const issues = [];
  
  // Verificar que entrenamientos activos estén en historial
  activeTrainings.value.forEach(active => {
    if (!trainingHistory.value.find(h => h.job_id === active.job_id)) {
      issues.push(`Active training ${active.job_id} not in history`);
    }
  });
  
  return issues;
};
```

## Próximas Mejoras

### **Funcionalidades Futuras**
- **AutoML**: Optimización automática de hiperparámetros
- **Pipelines**: Entrenamientos secuenciales automáticos
- **A/B Testing**: Comparación automática de configuraciones
- **Model Versioning**: Control de versiones de modelos
- **Collaborative Training**: Múltiples administradores colaborando

### **Optimizaciones de Performance**
- **Smart Polling**: Intervalos adaptativos basados en estado
- **Batch Operations**: Operaciones masivas optimizadas
- **Caching Inteligente**: Cache de configuraciones frecuentes
- **Progressive Loading**: Carga diferida de historial extenso

---

## Uso Rápido

### **Acceso a la Funcionalidad**
```
URL: /admin/training
Permisos: requiresAuth: true, requiresAdmin: true
```

### **Importación para Desarrollo**
```javascript
// Usar servicio administrativo
import { 
  startAdvancedTraining, 
  getTrainingHistory, 
  TRAINING_PRESETS 
} from '@/services/adminApi.js';

// Usar componente de entrenamiento
import ModelTraining from '@/components/admin/ModelTraining.vue';
```

### **Ejemplo de Integración Rápida**
```vue
<template>
  <div>
    <ModelTraining 
      :available-dataset-size="1000"
      @training-started="handleStart"
      @training-completed="handleComplete"
    />
  </div>
</template>

<script>
export default {
  methods: {
    handleStart(data) {
      console.log('Entrenamiento iniciado:', data);
    },
    handleComplete(result) {
      console.log('Entrenamiento completado:', result);
    }
  }
};
</script>
```

La implementación está **100% completa** y lista para uso en producción, proporcionando una interfaz administrativa avanzada para reentrenamiento de modelos ML con todas las funcionalidades modernas esperadas.
