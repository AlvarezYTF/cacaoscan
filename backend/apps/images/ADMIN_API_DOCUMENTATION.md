# Feature 3.2: APIs para Administrador - Gestión de Datos en CacaoScan

## Resumen de Implementación

Se ha implementado exitosamente la **Feature 3.2: APIs para administrador - gestión de datos** en CacaoScan. Esta feature proporciona endpoints REST administrativos con permisos especiales para CRUD completo, operaciones masivas, reentrenamiento de modelos ML y gestión avanzada de datos.

## Archivos Implementados

### 1. `backend/apps/images/admin_serializers.py`
**Propósito**: Serialización y validación para endpoints administrativos

**Serializers principales**:

#### **`AdminCacaoImageSerializer`**
- **CRUD completo** del modelo `CacaoImage`
- **Campos editables** para administradores:
  - Características físicas: `width`, `height`, `thickness`, `weight`
  - Calidad: `quality_score`, `predicted_quality`, `defect_type`
  - Estados: `is_processed`, `processing_time`
  - Metadatos: `batch_number`, `origin`, `notes`, `uploaded_by`

- **Validaciones administrativas**:
  - Rangos realistas para dimensiones (0.001-100.000 mm)
  - Peso válido (0.0001-50.0000 g)
  - Puntuación de calidad (0.000-1.000)
  - Consistencia entre dimensiones y peso (densidad 0.3-2.0 g/cm³)
  - Alineación entre `quality_score` y `predicted_quality`

- **Logging de cambios**: Registra automáticamente modificaciones importantes

#### **`AdminImageBulkUpdateSerializer`**
- **Actualización masiva** de hasta 100 imágenes simultáneamente
- **Campos soportados**: `batch_number`, `origin`, `predicted_quality`, `defect_type`, `notes`
- **Validación de IDs**: Verifica que todas las imágenes existen

#### **`TrainingJobSerializer`**
- **Parámetros de entrenamiento**: `epochs`, `learning_rate`, `batch_size`, `validation_split`
- **Filtros de datos**: `min_quality_score`, `exclude_defective`, `only_processed`
- **Validaciones específicas** por tipo de modelo (vision vs regression)

#### **Serializers adicionales**:
- `TrainingJobStatusSerializer`: Estado de trabajos de entrenamiento
- `AdminStatsSerializer`: Estadísticas administrativas detalladas

### 2. `backend/apps/images/admin_views.py`
**Propósito**: Vistas REST administrativas con permisos especiales

#### **`AdminImageViewSet`**
**Funcionalidades principales**:
- **CRUD administrativo completo** con `IsAdminUser` permission
- **Filtros avanzados**:
  ```python
  # Calidad de datos
  ?data_quality=complete          # Solo registros completos
  ?data_quality=incomplete        # Registros con campos faltantes
  
  # Filtros específicos
  ?quality=excellent&defect=none&batch=LOTE001
  ?min_quality=0.8&max_quality=1.0
  ?date_from=2024-01-01&date_to=2024-12-31
  ```

- **Operaciones especiales**:
  - `bulk-update/`: Actualización masiva de múltiples imágenes
  - `admin-stats/`: Estadísticas administrativas detalladas
  - `export-csv/`: Exportación de datos en formato CSV

- **Logging completo**: Registra todas las operaciones administrativas

#### **`MLTrainingView`**
**Funcionalidades de entrenamiento**:
- **POST**: Inicia entrenamiento de modelos (regression/vision)
- **GET**: Obtiene estado de trabajos de entrenamiento
- **Gestión de trabajos** en memoria con thread safety
- **Simulación de progreso** en tiempo real

#### **`AdminDataManagementView`**
**Operaciones de mantenimiento**:
- **Validación de integridad**: Verifica archivos y consistencia de datos
- **Detección de anomalías**: Identifica densidades inusuales
- **Preparado para expansión**: Estructura para más operaciones

### 3. `backend/apps/images/urls.py` (Actualizado)
**Estructura de URLs administrativas**:

```python
# Endpoints administrativos bajo /api/images/admin/
path('admin/', include([
    # CRUD administrativo
    path('', include(admin_router.urls)),
    
    # Entrenamiento ML
    path('train/regression/', MLTrainingView.as_view()),
    path('train/vision/', MLTrainingView.as_view()),
    path('train/status/<str:job_id>/', MLTrainingView.as_view()),
    path('train/jobs/', MLTrainingView.as_view()),
    
    # Gestión de datos
    path('data/validate-integrity/', AdminDataManagementView.as_view()),
]))
```

## APIs Administrativas Implementadas

### Gestión Avanzada de Imágenes

#### **`GET /api/images/admin/images/`**
**Descripción**: Lista TODAS las imágenes del sistema con filtros avanzados

**Filtros administrativos**:
```http
GET /api/images/admin/images/?data_quality=complete&min_quality=0.8&defect=none
GET /api/images/admin/images/?batch=LOTE001&origin=Colombia&date_from=2024-01-01
```

**Respuesta**:
```json
{
  "count": 1250,
  "next": "...",
  "previous": "...",
  "results": [
    {
      "id": 1,
      "image_url": "...",
      "width": 12.5,
      "height": 8.3,
      "thickness": 4.2,
      "weight": 1.25,
      "quality_score": 0.85,
      "predicted_quality": "excellent",
      "is_processed": true,
      "batch_number": "LOTE001",
      "origin": "Colombia",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### **`PUT /api/images/admin/images/{id}/`**
**Descripción**: Actualiza CUALQUIER campo de una imagen

**Request**:
```json
{
  "width": 12.8,
  "height": 8.5,
  "thickness": 4.3,
  "weight": 1.28,
  "quality_score": 0.90,
  "predicted_quality": "excellent",
  "batch_number": "LOTE001_CORREGIDO",
  "notes": "Valores corregidos manualmente"
}
```

**Validaciones automáticas**:
- ✅ Rangos realistas para cada campo
- ✅ Consistencia dimensional (densidad)
- ✅ Alineación calidad-puntuación
- ✅ Logging de cambios

#### **`POST /api/images/admin/images/bulk-update/`**
**Descripción**: Actualización masiva de múltiples imágenes

**Request**:
```json
{
  "image_ids": [1, 2, 3, 4, 5],
  "predicted_quality": "excellent",
  "batch_number": "LOTE_RECLASIFICADO_001",
  "notes": "Reclasificación masiva por calidad"
}
```

**Respuesta**:
```json
{
  "success": true,
  "updated_count": 5,
  "updated_ids": [1, 2, 3, 4, 5],
  "applied_changes": {
    "predicted_quality": "excellent",
    "batch_number": "LOTE_RECLASIFICADO_001",
    "notes": "Reclasificación masiva por calidad"
  }
}
```

#### **`GET /api/images/admin/images/admin-stats/`**
**Descripción**: Estadísticas administrativas detalladas

**Respuesta**:
```json
{
  "total_images": 1250,
  "processed_images": 1180,
  "unprocessed_images": 70,
  "quality_distribution": {
    "excellent": 450,
    "good": 520,
    "fair": 180,
    "poor": 30
  },
  "defect_distribution": {
    "none": 1050,
    "mold": 120,
    "broken": 50,
    "other": 30
  },
  "dimension_statistics": {
    "width": {"avg": 12.8, "min": 8.2, "max": 16.5},
    "height": {"avg": 8.1, "min": 5.8, "max": 11.2},
    "thickness": {"avg": 4.3, "min": 2.1, "max": 7.8},
    "weight": {"avg": 1.18, "min": 0.65, "max": 2.45}
  },
  "images_by_month": {
    "2024-01": 120,
    "2024-02": 145,
    "2024-03": 180
  },
  "processing_times": {
    "avg_seconds": 0.156,
    "min_seconds": 0.045,
    "max_seconds": 2.340
  },
  "model_performance": {
    "vision_model": {
      "accuracy": 0.89,
      "last_trained": "2024-01-15T10:30:00Z",
      "samples_used": 1180
    },
    "regression_model": {
      "r2_score": 0.82,
      "rmse": 0.12,
      "last_trained": "2024-01-15T10:30:00Z",
      "samples_used": 1180
    }
  },
  "storage_usage": {
    "total_size_bytes": 2147483648,
    "total_size_mb": 2048.0,
    "avg_file_size_kb": 1638.4,
    "storage_efficiency": "good"
  }
}
```

#### **`GET /api/images/admin/images/export-csv/`**
**Descripción**: Exporta datos completos en formato CSV

**Respuesta**: Archivo CSV con headers:
```csv
ID,Imagen,Ancho (mm),Alto (mm),Grosor (mm),Peso (g),Calidad Predicha,Puntuación Calidad,Tipo Defecto,Lote,Origen,Procesado,Tiempo Procesamiento (s),Fecha Creación,Notas
1,grain_001.jpg,12.5,8.3,4.2,1.25,Excelente,0.85,Sin defecto,LOTE001,Colombia,Sí,0.125,2024-01-15 10:30:00,Muestra de referencia
```

### Entrenamiento de Modelos ML

#### **`POST /api/images/admin/train/regression/`**
**Descripción**: Inicia entrenamiento del modelo de regresión

**Request**:
```json
{
  "epochs": 100,
  "learning_rate": 0.001,
  "batch_size": 32,
  "validation_split": 0.2,
  "min_quality_score": 0.7,
  "exclude_defective": true,
  "only_processed": true,
  "save_intermediate": true,
  "notify_completion": true
}
```

**Respuesta (202 Accepted)**:
```json
{
  "job_id": "uuid-4f3b2a1e-8c7d-4b5a-9e2f-1a3b4c5d6e7f",
  "model_type": "regression",
  "status": "pending",
  "progress": 0.0,
  "current_epoch": 0,
  "total_epochs": 100,
  "started_at": "2024-01-15T10:30:00Z",
  "dataset_size": 0,
  "validation_size": 0,
  "parameters": {
    "epochs": 100,
    "learning_rate": 0.001,
    "batch_size": 32,
    "validation_split": 0.2
  }
}
```

#### **`POST /api/images/admin/train/vision/`**
**Descripción**: Inicia entrenamiento del modelo de visión CNN

**Request**:
```json
{
  "epochs": 50,
  "learning_rate": 0.0001,
  "batch_size": 16,
  "validation_split": 0.25,
  "min_quality_score": 0.8,
  "exclude_defective": true
}
```

**Validaciones específicas para visión**:
- ✅ `batch_size` máximo 64
- ✅ `learning_rate` máximo 0.01
- ✅ Parámetros optimizados para CNN

#### **`GET /api/images/admin/train/status/{job_id}/`**
**Descripción**: Estado detallado de un trabajo de entrenamiento

**Respuesta**:
```json
{
  "job_id": "uuid-4f3b2a1e-8c7d-4b5a-9e2f-1a3b4c5d6e7f",
  "model_type": "regression",
  "status": "running",
  "progress": 45.50,
  "current_epoch": 45,
  "total_epochs": 100,
  "current_loss": 0.125,
  "current_accuracy": 0.876,
  "validation_loss": 0.142,
  "validation_accuracy": 0.851,
  "started_at": "2024-01-15T10:30:00Z",
  "estimated_completion": "2024-01-15T11:15:00Z",
  "dataset_size": 944,
  "validation_size": 236,
  "log_url": "/api/admin/train/logs/uuid-4f3b2a1e/"
}
```

#### **`GET /api/images/admin/train/jobs/`**
**Descripción**: Lista todos los trabajos de entrenamiento

**Respuesta**:
```json
{
  "jobs": [
    {
      "job_id": "uuid-123",
      "model_type": "regression",
      "status": "completed",
      "progress": 100.0,
      "completed_at": "2024-01-15T11:15:00Z"
    },
    {
      "job_id": "uuid-456",
      "model_type": "vision",
      "status": "running",
      "progress": 67.5,
      "current_epoch": 34
    }
  ],
  "total_jobs": 2
}
```

### Gestión Avanzada de Datos

#### **`POST /api/images/admin/data/validate-integrity/`**
**Descripción**: Valida integridad de todos los datos

**Respuesta**:
```json
{
  "total_images": 1250,
  "issues_found": 3,
  "issues": [
    {
      "type": "missing_file",
      "image_id": 145,
      "details": "Archivo no encontrado: /media/cacao_images/grain_145.jpg"
    },
    {
      "type": "unrealistic_density",
      "image_id": 267,
      "details": "Densidad inusual: 2.45 g/cm³"
    },
    {
      "type": "unrealistic_density",
      "image_id": 389,
      "details": "Densidad inusual: 0.25 g/cm³"
    }
  ]
}
```

## Seguridad y Permisos

### Esquema de Permisos

#### **Usuarios Normales**:
- ✅ `POST /api/images/predict/` - Subir y predecir
- ✅ `GET /api/images/` - Ver sus propias imágenes
- ✅ `GET /api/images/{id}/` - Solo si es propietario
- ✅ `PUT /api/images/{id}/` - Solo metadatos básicos
- ✅ `DELETE /api/images/{id}/` - Solo si es propietario
- ❌ **NO acceso** a endpoints `/admin/`

#### **Administradores (`IsAdminUser`)**:
- ✅ **Acceso completo** a todos los endpoints de usuario
- ✅ **Acceso completo** a endpoints administrativos
- ✅ **CRUD total** sobre cualquier imagen
- ✅ **Operaciones masivas** y de mantenimiento
- ✅ **Entrenamiento de modelos** ML
- ✅ **Exportación de datos** y estadísticas

### Validación de Permisos

```python
# En admin_views.py
class AdminImageViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]  # Solo administradores

class MLTrainingView(APIView):
    permission_classes = [IsAdminUser]  # Solo administradores

class AdminDataManagementView(APIView):
    permission_classes = [IsAdminUser]  # Solo administradores
```

### Logging de Seguridad

```python
# Logging automático de operaciones administrativas
logger.info(f"Admin {self.request.user.username} actualizó imagen {instance.id}")
logger.info(f"Admin {request.user.username} actualizó masivamente {updated_count} imágenes")
logger.info(f"Admin {request.user.username} inició entrenamiento {model_type}")
logger.info(f"Admin {request.user.username} eliminó imagen {image_id}")
logger.info(f"Admin {request.user.username} exportó {queryset.count()} registros a CSV")
```

## Características Técnicas

### Validaciones Administrativas

#### **Validaciones de Dimensiones**:
```python
# Rangos realistas
width: 0.001 - 100.000 mm
height: 0.001 - 100.000 mm  
thickness: 0.001 - 100.000 mm
weight: 0.0001 - 50.0000 g

# Proporciones realistas
width/height: 0.5 - 3.0
thickness <= min(width, height)

# Densidad razonable
density: 0.3 - 2.0 g/cm³
```

#### **Validaciones de Calidad**:
```python
# Rangos por calidad predicha
excellent: quality_score 0.8 - 1.0
good: quality_score 0.6 - 0.8
fair: quality_score 0.4 - 0.6
poor: quality_score 0.0 - 0.4
```

### Gestión de Trabajos ML

#### **Thread Safety**:
```python
# Storage thread-safe para trabajos
training_jobs = {}
training_jobs_lock = threading.Lock()

# Acceso seguro
with training_jobs_lock:
    training_jobs[job_id] = job_data
```

#### **Simulación de Progreso**:
```python
# Progreso en tiempo real (simulado)
for epoch in range(1, parameters['epochs'] + 1):
    progress = (epoch / parameters['epochs']) * 100
    
    with training_jobs_lock:
        training_jobs[job_id]['current_epoch'] = epoch
        training_jobs[job_id]['progress'] = progress
        training_jobs[job_id]['current_loss'] = 0.5 - (epoch * 0.01)
```

### Operaciones Masivas

#### **Actualización Masiva**:
```python
# Límite de seguridad
max_length=100  # Máximo 100 imágenes por operación

# Validación de existencia
existing_ids = set(CacaoImage.objects.filter(id__in=value).values_list('id', flat=True))
missing_ids = set(value) - existing_ids

# Operación atómica
updated_count = CacaoImage.objects.filter(id__in=image_ids).update(**update_data)
```

#### **Exportación CSV**:
```python
# Headers descriptivos
headers = [
    'ID', 'Imagen', 'Ancho (mm)', 'Alto (mm)', 'Grosor (mm)', 'Peso (g)',
    'Calidad Predicha', 'Puntuación Calidad', 'Tipo Defecto',
    'Lote', 'Origen', 'Procesado', 'Tiempo Procesamiento (s)',
    'Fecha Creación', 'Notas'
]

# Nombre de archivo con timestamp
filename = f"cacaoscan_data_{timezone.now().strftime('%Y%m%d_%H%M%S')}.csv"
```

## Integración con Sistema Existente

### Compatibilidad con Feature 3.1

- ✅ **Coexistencia** con endpoints de usuario
- ✅ **Separación clara** de permisos
- ✅ **Mismo modelo** `CacaoImage` subyacente
- ✅ **Consistencia** en respuestas JSON

### URLs Organizadas

```
/api/images/                     # Usuario - predicciones básicas
/api/images/admin/               # Administrador - gestión completa
/api/images/admin/train/         # Administrador - entrenamiento ML
/api/images/admin/data/          # Administrador - operaciones de datos
```

### Documentación Swagger

- ✅ **Tags organizados**: 'Administración', 'Entrenamiento ML', 'Gestión de Datos'
- ✅ **Esquemas detallados** para todos los serializers
- ✅ **Ejemplos de request/response**
- ✅ **Códigos de estado** específicos

## Ejemplos de Uso Completo

### Flujo Administrativo Típico

#### **1. Verificar Integridad de Datos**:
```bash
curl -X POST http://localhost:8000/api/images/admin/data/validate-integrity/ \
  -H "Authorization: Bearer admin_token"
```

#### **2. Obtener Estadísticas Detalladas**:
```bash
curl -X GET http://localhost:8000/api/images/admin/images/admin-stats/ \
  -H "Authorization: Bearer admin_token"
```

#### **3. Filtrar Imágenes con Problemas**:
```bash
curl "http://localhost:8000/api/images/admin/images/?data_quality=incomplete&min_quality=0.0&max_quality=0.5" \
  -H "Authorization: Bearer admin_token"
```

#### **4. Corregir Datos Masivamente**:
```bash
curl -X POST http://localhost:8000/api/images/admin/images/bulk-update/ \
  -H "Authorization: Bearer admin_token" \
  -H "Content-Type: application/json" \
  -d '{
    "image_ids": [1, 2, 3, 4, 5],
    "predicted_quality": "poor",
    "defect_type": "broken",
    "notes": "Reclasificación tras revisión manual"
  }'
```

#### **5. Entrenar Modelo con Datos Limpios**:
```bash
curl -X POST http://localhost:8000/api/images/admin/train/regression/ \
  -H "Authorization: Bearer admin_token" \
  -H "Content-Type: application/json" \
  -d '{
    "epochs": 200,
    "learning_rate": 0.001,
    "batch_size": 32,
    "validation_split": 0.2,
    "min_quality_score": 0.7,
    "exclude_defective": true
  }'
```

#### **6. Monitorear Progreso**:
```bash
curl -X GET http://localhost:8000/api/images/admin/train/status/uuid-job-id/ \
  -H "Authorization: Bearer admin_token"
```

#### **7. Exportar Datos Finales**:
```bash
curl -X GET "http://localhost:8000/api/images/admin/images/export-csv/?processed=true&quality=excellent" \
  -H "Authorization: Bearer admin_token" \
  -o cacaoscan_export.csv
```

### Integración con Frontend Administrativo

```javascript
// Cliente administrativo
class CacaoScanAdminAPI {
  constructor(baseUrl, token) {
    this.baseUrl = baseUrl;
    this.headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }
  
  // Obtener estadísticas administrativas
  async getAdminStats() {
    const response = await fetch(`${this.baseUrl}/api/images/admin/images/admin-stats/`, {
      headers: this.headers
    });
    return await response.json();
  }
  
  // Actualización masiva
  async bulkUpdate(imageIds, updates) {
    const response = await fetch(`${this.baseUrl}/api/images/admin/images/bulk-update/`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({
        image_ids: imageIds,
        ...updates
      })
    });
    return await response.json();
  }
  
  // Iniciar entrenamiento
  async startTraining(modelType, parameters) {
    const response = await fetch(`${this.baseUrl}/api/images/admin/train/${modelType}/`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(parameters)
    });
    return await response.json();
  }
  
  // Monitorear entrenamiento
  async getTrainingStatus(jobId) {
    const response = await fetch(`${this.baseUrl}/api/images/admin/train/status/${jobId}/`, {
      headers: this.headers
    });
    return await response.json();
  }
  
  // Exportar datos
  async exportData(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`${this.baseUrl}/api/images/admin/images/export-csv/?${params}`, {
      headers: this.headers
    });
    return await response.blob();
  }
}

// Ejemplo de uso
const adminAPI = new CacaoScanAdminAPI('http://localhost:8000', adminToken);

// Dashboard administrativo
async function updateAdminDashboard() {
  try {
    const stats = await adminAPI.getAdminStats();
    
    // Actualizar UI con estadísticas
    document.getElementById('total-images').textContent = stats.total_images;
    document.getElementById('processed-images').textContent = stats.processed_images;
    
    // Mostrar distribución de calidad
    updateQualityChart(stats.quality_distribution);
    
    // Mostrar rendimiento de modelos
    updatePerformanceMetrics(stats.model_performance);
    
  } catch (error) {
    console.error('Error obteniendo estadísticas:', error);
  }
}

// Entrenamiento con progreso en tiempo real
async function trainModel(modelType, parameters) {
  try {
    // Iniciar entrenamiento
    const job = await adminAPI.startTraining(modelType, parameters);
    console.log('Entrenamiento iniciado:', job.job_id);
    
    // Monitorear progreso
    const interval = setInterval(async () => {
      const status = await adminAPI.getTrainingStatus(job.job_id);
      
      // Actualizar barra de progreso
      updateProgressBar(status.progress);
      updateTrainingMetrics(status);
      
      // Si completado, detener monitoreo
      if (status.status === 'completed' || status.status === 'failed') {
        clearInterval(interval);
        handleTrainingComplete(status);
      }
    }, 5000); // Verificar cada 5 segundos
    
  } catch (error) {
    console.error('Error en entrenamiento:', error);
  }
}
```

## Próximos Pasos

### Mejoras Inmediatas

1. **Autenticación JWT**: Implementar tokens para APIs administrativas
2. **Rate Limiting**: Límites específicos para operaciones administrativas
3. **Async Tasks**: Integrar Celery para entrenamiento real
4. **Audit Log**: Base de datos para auditoría completa

### Funcionalidades Avanzadas

1. **Backup/Restore**: Operaciones de respaldo automático
2. **Data Migration**: Herramientas de migración de datos
3. **Model Versioning**: Versionado de modelos ML
4. **Performance Monitoring**: Métricas avanzadas de rendimiento

### Integración Empresarial

1. **LDAP/SSO**: Integración con sistemas corporativos
2. **API Gateway**: Rate limiting y cache distribuido
3. **Monitoring**: Prometheus/Grafana para métricas
4. **Alerting**: Notificaciones automáticas de eventos

Esta implementación proporciona una base sólida y escalable para la gestión administrativa completa del sistema CacaoScan, con capacidades avanzadas de CRUD, operaciones masivas, entrenamiento de modelos ML y gestión de datos.
