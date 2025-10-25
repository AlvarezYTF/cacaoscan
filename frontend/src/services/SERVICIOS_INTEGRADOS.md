# 📚 Servicios Integrados - Frontend CacaoScan

Documentación completa de todos los servicios de API integrados entre frontend y backend.

## 📋 Índice

1. [Servicios Creados](#servicios-creados)
2. [Guía de Uso](#guía-de-uso)
3. [Ejemplos de Implementación](#ejemplos-de-implementación)
4. [Testing](#testing)

---

## 🆕 Servicios Creados

### 1. **notificationsApi.js** 🔔

Sistema completo de notificaciones en tiempo real.

**Endpoints integrados:**
- `GET /api/notifications/` - Lista de notificaciones
- `GET /api/notifications/{id}/` - Detalle de notificación
- `POST /api/notifications/{id}/read/` - Marcar como leída
- `POST /api/notifications/mark-all-read/` - Marcar todas como leídas
- `GET /api/notifications/unread-count/` - Contador de no leídas
- `GET /api/notifications/stats/` - Estadísticas
- `POST /api/notifications/create/` - Crear notificación (admin)

**Funciones principales:**
```javascript
import notificationsApi from '@/services/notificationsApi'

// Obtener notificaciones
const result = await notificationsApi.getNotifications({ page: 1, page_size: 20 })

// Contador de no leídas
const count = await notificationsApi.getUnreadNotificationsCount()

// Marcar como leída
await notificationsApi.markNotificationAsRead(notificationId)

// Marcar todas como leídas
await notificationsApi.markAllNotificationsAsRead()
```

---

### 2. **auditApi.js** 📊

Sistema de auditoría y logs de actividad.

**Endpoints integrados:**
- `GET /api/audit/activity-logs/` - Logs de actividad
- `GET /api/audit/login-history/` - Historial de logins
- `GET /api/audit/stats/` - Estadísticas de auditoría

**Funciones principales:**
```javascript
import auditApi from '@/services/auditApi'

// Obtener logs de actividad
const logs = await auditApi.getActivityLogs({
  page: 1,
  usuario: 'john@example.com',
  fecha_desde: '2025-01-01',
  fecha_hasta: '2025-12-31'
})

// Historial de logins
const logins = await auditApi.getLoginHistory({
  exitoso: true,
  fecha_desde: '2025-01-01'
})

// Estadísticas
const stats = await auditApi.getAuditStats()

// Generar reporte
const report = await auditApi.generateAuditReport({
  tipo: 'activity',
  formato: 'pdf',
  fecha_desde: '2025-01-01',
  fecha_hasta: '2025-12-31'
})
```

---

### 3. **calibrationApi.js** ⚖️

Sistema de calibración de modelos.

**Endpoints integrados:**
- `GET /api/calibration/status/` - Estado de calibración
- `POST /api/calibration/` - Realizar calibración
- `POST /api/scan/measure/calibrated/` - Análisis calibrado

**Funciones principales:**
```javascript
import calibrationApi from '@/services/calibrationApi'

// Obtener estado de calibración
const status = await calibrationApi.getCalibrationStatus()

// Verificar si la calibración es válida
const isValid = calibrationApi.isCalibrationValid(status.data)

// Realizar calibración
const calibrationData = {
  calibration_type: 'full',
  reference_weight: 1.5,
  reference_length: 20,
  reference_width: 10,
  reference_thickness: 8
}
const result = await calibrationApi.performCalibration(calibrationData)

// Análisis con calibración
const formData = new FormData()
formData.append('image', imageFile)
const scanResult = await calibrationApi.scanWithCalibration(formData)
```

---

### 4. **modelMetricsApi.js** 📈

Gestión de métricas y comparación de modelos.

**Endpoints integrados:**
- `GET /api/model-metrics/` - Lista de métricas
- `POST /api/model-metrics/create/` - Crear registro de métricas
- `GET /api/model-metrics/{id}/` - Detalle de métricas
- `PATCH /api/model-metrics/{id}/update/` - Actualizar métricas
- `DELETE /api/model-metrics/{id}/delete/` - Eliminar métricas
- `GET /api/model-metrics/stats/` - Estadísticas
- `GET /api/model-metrics/trend/` - Tendencias de rendimiento
- `POST /api/model-metrics/compare/` - Comparar modelos
- `GET /api/model-metrics/best/` - Mejores modelos
- `GET /api/model-metrics/production/` - Modelos en producción

**Funciones principales:**
```javascript
import modelMetricsApi from '@/services/modelMetricsApi'

// Obtener métricas
const metrics = await modelMetricsApi.getModelMetrics({
  model_type: 'regression',
  ordering: '-created_at'
})

// Crear registro de métricas
const metricsData = {
  model_type: 'regression',
  model_version: 'v1.2.0',
  metrics: {
    mse: 0.0123,
    mae: 0.089,
    r2_score: 0.95
  },
  hyperparameters: {
    epochs: 50,
    learning_rate: 0.001,
    batch_size: 32
  },
  training_data_size: 10000
}
await modelMetricsApi.createModelMetrics(metricsData)

// Comparar modelos
const comparison = await modelMetricsApi.compareModels([1, 2, 3])

// Obtener mejores modelos
const best = await modelMetricsApi.getBestModels({
  model_type: 'yolo',
  limit: 5,
  metric: 'map'
})

// Tendencias
const trend = await modelMetricsApi.getModelPerformanceTrend({
  model_type: 'regression',
  metric_name: 'mse',
  limit: 10
})
```

---

### 5. **incrementalTrainingApi.js** (Actualizado) 🔄

Sistema de entrenamiento incremental - endpoints corregidos.

**Endpoints integrados (actualizados):**
- `GET /api/incremental/status/` - Estado del sistema
- `POST /api/incremental/train/` - Entrenar incrementalmente
- `POST /api/incremental/upload/` - Subir datos
- `GET /api/incremental/models/` - Versiones de modelos
- `GET /api/incremental/data/` - Versiones de datos

**Funciones principales:**
```javascript
import incrementalTrainingApi from '@/services/incrementalTrainingApi'

// Estado del sistema
const status = await incrementalTrainingApi.getIncrementalTrainingStatus()

// Entrenar incrementalmente
const formData = new FormData()
formData.append('image', imageFile)
formData.append('data', JSON.stringify({
  id: 1,
  alto: 20.5,
  ancho: 10.2,
  grosor: 8.1,
  peso: 1.5
}))
const result = await incrementalTrainingApi.submitIncrementalTraining(formData)

// Subir datos
const uploadResult = await incrementalTrainingApi.uploadIncrementalData(formData)

// Ver versiones de modelos
const models = await incrementalTrainingApi.getIncrementalModels()

// Ver versiones de datos
const dataVersions = await incrementalTrainingApi.getIncrementalDataVersions()
```

---

### 6. **modelsApi.js** 🤖

Gestión de estado y carga de modelos ML.

**Endpoints integrados:**
- `GET /api/models/status/` - Estado de modelos
- `POST /api/models/load/` - Cargar modelos
- `POST /api/dataset/validation/` - Validar dataset
- `POST /api/auto-initialize/` - Inicialización automática

**Funciones principales:**
```javascript
import modelsApi from '@/services/modelsApi'

// Obtener estado de modelos
const status = await modelsApi.getModelsStatus()

// Verificar si un modelo está cargado
const isLoaded = modelsApi.isModelLoaded(status.data, 'regression')

// Verificar si todos los modelos están cargados
const allLoaded = modelsApi.areAllModelsLoaded(status.data)

// Cargar modelos
const loadResult = await modelsApi.loadModels({
  force_reload: false,
  model_types: ['regression', 'vision', 'yolo']
})

// Validar dataset
const validation = await modelsApi.validateDataset({
  check_integrity: true,
  check_balance: true
})

// Analizar validación
const analysis = modelsApi.analyzeDatasetValidation(validation)

// Inicialización automática
const initResult = await modelsApi.autoInitialize({
  load_models: true,
  validate_dataset: true,
  check_dependencies: true
})

// Formatear estado para UI
const formatted = modelsApi.formatModelsStatus(status.data)
```

---

## 🚀 Guía de Uso

### Importación Simple

```javascript
// Importar un servicio específico
import notificationsApi from '@/services/notificationsApi'

// Importar múltiples servicios
import { notificationsApi, auditApi, calibrationApi } from '@/services'
```

### Importación Dinámica

```javascript
import { getService, getServices, getServicesByCategory } from '@/services'

// Cargar un servicio dinámicamente
const notificationsApi = await getService('notifications')

// Cargar múltiples servicios
const services = await getServices(['notifications', 'audit', 'calibration'])

// Cargar servicios por categoría
const systemServices = await getServicesByCategory('SYSTEM')
```

---

## 💡 Ejemplos de Implementación

### Ejemplo 1: Panel de Notificaciones

```vue
<template>
  <div class="notifications-panel">
    <div class="notifications-header">
      <h3>Notificaciones</h3>
      <span class="badge">{{ unreadCount }}</span>
      <button @click="markAllAsRead">Marcar todas como leídas</button>
    </div>
    
    <div class="notifications-list">
      <div 
        v-for="notification in notifications" 
        :key="notification.id"
        :class="['notification-item', { unread: !notification.leida }]"
        @click="handleNotificationClick(notification)"
      >
        <div class="notification-icon" :class="notification.tipo">
          <i :class="getIcon(notification.tipo)"></i>
        </div>
        <div class="notification-content">
          <h4>{{ notification.titulo }}</h4>
          <p>{{ notification.mensaje }}</p>
          <span class="notification-date">{{ formatDate(notification.fecha_creacion) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import notificationsApi from '@/services/notificationsApi'

const notifications = ref([])
const unreadCount = ref(0)
let refreshInterval = null

const loadNotifications = async () => {
  const result = await notificationsApi.getNotifications({ 
    page: 1, 
    page_size: 20 
  })
  
  if (result.success) {
    notifications.value = result.data.results
  }
}

const loadUnreadCount = async () => {
  const result = await notificationsApi.getUnreadNotificationsCount()
  
  if (result.success) {
    unreadCount.value = result.data.unread_count
  }
}

const handleNotificationClick = async (notification) => {
  if (!notification.leida) {
    await notificationsApi.markNotificationAsRead(notification.id)
    notification.leida = true
    unreadCount.value--
  }
}

const markAllAsRead = async () => {
  const result = await notificationsApi.markAllNotificationsAsRead()
  
  if (result.success) {
    notifications.value.forEach(n => n.leida = true)
    unreadCount.value = 0
  }
}

onMounted(() => {
  loadNotifications()
  loadUnreadCount()
  
  // Refrescar cada 30 segundos
  refreshInterval = setInterval(() => {
    loadNotifications()
    loadUnreadCount()
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>
```

### Ejemplo 2: Vista de Auditoría

```vue
<template>
  <div class="audit-view">
    <div class="audit-filters">
      <input 
        v-model="filters.usuario" 
        placeholder="Filtrar por usuario"
      />
      <input 
        v-model="filters.fecha_desde" 
        type="date"
      />
      <input 
        v-model="filters.fecha_hasta" 
        type="date"
      />
      <select v-model="filters.accion">
        <option value="">Todas las acciones</option>
        <option value="login">Login</option>
        <option value="create">Crear</option>
        <option value="update">Actualizar</option>
        <option value="delete">Eliminar</option>
      </select>
      <button @click="loadLogs">Buscar</button>
      <button @click="exportReport">Exportar PDF</button>
    </div>
    
    <div class="audit-stats">
      <div class="stat-card">
        <h4>Total de Eventos</h4>
        <p>{{ stats.total_events || 0 }}</p>
      </div>
      <div class="stat-card">
        <h4>Usuarios Activos</h4>
        <p>{{ stats.active_users || 0 }}</p>
      </div>
      <div class="stat-card">
        <h4>Logins Exitosos</h4>
        <p>{{ stats.successful_logins || 0 }}</p>
      </div>
      <div class="stat-card">
        <h4>Logins Fallidos</h4>
        <p>{{ stats.failed_logins || 0 }}</p>
      </div>
    </div>
    
    <table class="audit-table">
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Usuario</th>
          <th>Acción</th>
          <th>Descripción</th>
          <th>IP</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="log in logs" :key="log.id">
          <td>{{ formatDate(log.fecha) }}</td>
          <td>{{ log.usuario_nombre }}</td>
          <td>
            <span :class="['badge', getActionColor(log.accion)]">
              {{ log.accion }}
            </span>
          </td>
          <td>{{ log.descripcion }}</td>
          <td>{{ log.direccion_ip }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import auditApi from '@/services/auditApi'

const logs = ref([])
const stats = ref({})
const filters = ref({
  usuario: '',
  fecha_desde: '',
  fecha_hasta: '',
  accion: ''
})

const loadLogs = async () => {
  const result = await auditApi.getActivityLogs({
    ...filters.value,
    page: 1,
    page_size: 50
  })
  
  if (result.success) {
    logs.value = result.data.results
  }
}

const loadStats = async () => {
  const result = await auditApi.getAuditStats()
  
  if (result.success) {
    stats.value = result.data
  }
}

const exportReport = async () => {
  const result = await auditApi.generateAuditReport({
    tipo: 'activity',
    formato: 'pdf',
    fecha_desde: filters.value.fecha_desde,
    fecha_hasta: filters.value.fecha_hasta
  })
  
  if (result.success) {
    // Descargar PDF
    const link = document.createElement('a')
    link.href = result.data.url
    link.download = result.data.filename
    link.click()
  }
}

onMounted(() => {
  loadLogs()
  loadStats()
})
</script>
```

---

## ✅ Testing

### Testing Manual

Para probar cada servicio:

1. **Notificaciones:**
```bash
# En el navegador, abrir consola de desarrollador
import notificationsApi from '@/services/notificationsApi'
const result = await notificationsApi.getNotifications()
console.log(result)
```

2. **Auditoría:**
```bash
import auditApi from '@/services/auditApi'
const logs = await auditApi.getActivityLogs({ page: 1 })
console.log(logs)
```

3. **Calibración:**
```bash
import calibrationApi from '@/services/calibrationApi'
const status = await calibrationApi.getCalibrationStatus()
console.log(status)
```

4. **Métricas de Modelos:**
```bash
import modelMetricsApi from '@/services/modelMetricsApi'
const metrics = await modelMetricsApi.getModelMetrics()
console.log(metrics)
```

5. **Modelos:**
```bash
import modelsApi from '@/services/modelsApi'
const status = await modelsApi.getModelsStatus()
console.log(status)
```

---

## 📊 Resumen de Integración

| Servicio | Endpoints | Estado | Prioridad |
|----------|-----------|--------|-----------|
| Notificaciones | 7 | ✅ Completado | Alta |
| Auditoría | 3 | ✅ Completado | Alta |
| Calibración | 3 | ✅ Completado | Media |
| Métricas de Modelos | 10 | ✅ Completado | Alta |
| Entrenamiento Incremental | 5 | ✅ Actualizado | Media |
| Gestión de Modelos | 4 | ✅ Completado | Alta |

**Total de endpoints integrados:** 32

---

## 🔗 Referencias

- Backend API Documentation: `/backend/API_IMPLEMENTATION_SUMMARY.md`
- Frontend Services: `/frontend/src/services/`
- Router Guards: `/frontend/src/router/guards.js`

---

## 📝 Notas Importantes

1. Todos los servicios incluyen manejo de errores consistente
2. Se emiten eventos de loading para mostrar indicadores de carga
3. Todos los servicios usan el cliente API base configurado en `api.js`
4. Las funciones incluyen validaciones y formateo de datos
5. Se siguen los principios SOLID, DRY, KISS y YAGNI

---

**Fecha de creación:** 25 de Octubre, 2025
**Última actualización:** 25 de Octubre, 2025
**Versión:** 1.0.0

