# Exposición de ML en CacaoScan API

## 📋 Resumen

El sistema ML de CacaoScan ya está **ampliamente expuesto** a través de múltiples endpoints REST. Este documento describe cómo está estructurada la exposición actual y qué funcionalidades están disponibles.

> 📖 **Documentación relacionada**: Para conocer las **herramientas, métodos y principios** utilizados para construir el sistema ML, consulta: [`HERRAMIENTAS_METODOS_PRINCIPIOS_ML.md`](./HERRAMIENTAS_METODOS_PRINCIPIOS_ML.md)

---

## 🎯 Endpoints ML Principales

### 1. **Predicción y Análisis**

#### `POST /api/v1/scan/measure/`
- **Descripción**: Endpoint principal para análisis de imágenes de granos de cacao
- **Funcionalidad**: 
  - Segmenta el grano de la imagen
  - Predice dimensiones (alto, ancho, grosor) y peso
  - Guarda resultados en base de datos
- **View**: `ScanMeasureView` (desde `images_app`)
- **Autenticación**: Requerida
- **Uso**: Frontend usa este endpoint para análisis individual

#### `POST /api/v1/scan/measure/calibrated/`
- **Descripción**: Versión calibrada del endpoint de predicción
- **Funcionalidad**: Aplica calibración de píxeles para mayor precisión
- **View**: `CalibratedScanMeasureView`
- **Autenticación**: Requerida

#### `POST /api/v1/analysis/batch/`
- **Descripción**: Análisis en lote de múltiples imágenes
- **Funcionalidad**: Procesa múltiples imágenes simultáneamente
- **View**: `BatchAnalysisView`
- **Autenticación**: Requerida

---

### 2. **Gestión de Modelos**

#### `GET /api/v1/models/status/` o `GET /api/v1/ml/models/status/`
- **Descripción**: Obtiene el estado de los modelos ML cargados
- **Respuesta**: Estado, dispositivo (CPU/GPU), detalles del modelo, escaladores
- **View**: `ModelsStatusView`
- **Cache**: 5 minutos
- **Autenticación**: Requerida

#### `POST /api/v1/models/load/` o `POST /api/v1/ml/models/load/`
- **Descripción**: Carga los modelos ML en memoria
- **Funcionalidad**: Carga artefactos (modelos y escaladores) usando `MLService`
- **View**: `LoadModelsView`
- **Autenticación**: Requerida
- **Nota**: Usa patrón singleton para evitar cargas múltiples

#### `POST /api/v1/ml/models/unload/`
- **Descripción**: Descarga modelos de memoria
- **View**: `UnloadModelsView`
- **Autenticación**: Requerida

---

### 3. **Entrenamiento de Modelos**

#### `POST /api/v1/train/jobs/create/` o `POST /api/v1/ml/train/`
- **Descripción**: Crea un trabajo de entrenamiento
- **Funcionalidad**: Inicia entrenamiento de modelos (puede ser síncrono o asíncrono)
- **View**: `TrainingJobCreateView`
- **Autenticación**: Requerida

#### `GET /api/v1/train/jobs/`
- **Descripción**: Lista todos los trabajos de entrenamiento
- **View**: `TrainingJobListView`
- **Autenticación**: Requerida

#### `GET /api/v1/train/jobs/<job_id>/status/`
- **Descripción**: Obtiene el estado de un trabajo de entrenamiento específico
- **View**: `TrainingJobStatusView`
- **Autenticación**: Requerida

#### `POST /api/v1/ml/auto-train/`
- **Descripción**: Entrenamiento automático síncrono (sin Celery)
- **Funcionalidad**: Ejecuta pipeline completo de entrenamiento
- **View**: `AutoTrainView`
- **Autenticación**: Requerida (solo admin)
- **Configuración**: Acepta parámetros como epochs, batch_size, learning_rate

---

### 4. **Validación de Dataset**

#### `GET /api/v1/dataset/validation/`
- **Descripción**: Valida el dataset y devuelve estadísticas
- **Funcionalidad**: Verifica integridad del dataset, cuenta imágenes, valida estructura
- **View**: `DatasetValidationView`
- **Autenticación**: Requerida
- **Nota**: Puede ejecutarse de forma asíncrona con Celery

---

### 5. **Inicialización Automática**

#### `POST /api/v1/auto-initialize/`
- **Descripción**: Inicialización automática completa del sistema ML
- **Pasos**:
  1. Validar dataset
  2. Generar crops (si no existen)
  3. Entrenar modelos (si no existen)
  4. Cargar modelos
- **View**: `AutoInitializeView`
- **Autenticación**: Requerida
- **Uso**: Útil para setup inicial del sistema

---

### 6. **Calibración**

#### `GET /api/v1/calibration/status/` o `GET /api/v1/ml/calibration/status/`
- **Descripción**: Obtiene el estado de la calibración
- **View**: `CalibrationStatusView`
- **Autenticación**: Requerida

#### `POST /api/v1/calibration/` o `POST /api/v1/ml/calibration/upload/`
- **Descripción**: Sube y procesa imagen de calibración
- **Funcionalidad**: Calibra el sistema usando imagen de referencia
- **View**: `CalibrationView`
- **Autenticación**: Requerida

---

### 7. **Entrenamiento Incremental**

#### `GET /api/v1/incremental/status/` o `GET /api/v1/ml/incremental/status/`
- **Descripción**: Estado del entrenamiento incremental
- **View**: `IncrementalTrainingStatusView`
- **Autenticación**: Requerida

#### `POST /api/v1/incremental/train/` o `POST /api/v1/ml/incremental/start/`
- **Descripción**: Inicia entrenamiento incremental
- **View**: `IncrementalTrainingView`
- **Autenticación**: Requerida

#### `POST /api/v1/incremental/upload/`
- **Descripción**: Sube datos para entrenamiento incremental
- **View**: `IncrementalDataUploadView`
- **Autenticación**: Requerida

#### `GET /api/v1/incremental/models/`
- **Descripción**: Lista versiones de modelos incrementales
- **View**: `IncrementalModelVersionsView`
- **Autenticación**: Requerida

#### `GET /api/v1/incremental/data/`
- **Descripción**: Lista versiones de datos incrementales
- **View**: `IncrementalDataVersionsView`
- **Autenticación**: Requerida

---

### 8. **Métricas de Modelos**

#### `GET /api/v1/ml/metrics/` o `GET /api/v1/model-metrics/`
- **Descripción**: Lista todas las métricas de modelos
- **View**: `ModelMetricsListView`
- **Autenticación**: Requerida

#### `POST /api/v1/ml/metrics/create/` o `POST /api/v1/model-metrics/create/`
- **Descripción**: Crea nueva métrica de modelo
- **View**: `ModelMetricsCreateView`
- **Autenticación**: Requerida

#### `GET /api/v1/ml/metrics/<pk>/`
- **Descripción**: Detalle de métrica específica
- **View**: `ModelMetricsDetailView`
- **Autenticación**: Requerida

#### `PATCH /api/v1/ml/metrics/<pk>/update/`
- **Descripción**: Actualiza métrica
- **View**: `ModelMetricsUpdateView`
- **Autenticación**: Requerida

#### `DELETE /api/v1/ml/metrics/<pk>/delete/`
- **Descripción**: Elimina métrica
- **View**: `ModelMetricsDeleteView`
- **Autenticación**: Requerida

#### `GET /api/v1/ml/metrics/stats/`
- **Descripción**: Estadísticas de métricas
- **View**: `ModelMetricsStatsView`
- **Autenticación**: Requerida

#### `GET /api/v1/ml/metrics/latest/`
- **Descripción**: Últimas métricas por target
- **View**: `LatestMetricsView`
- **Cache**: 1 minuto
- **Autenticación**: Requerida

#### `GET /api/v1/ml/performance-trend/` o `GET /api/v1/model-metrics/trend/`
- **Descripción**: Tendencia de rendimiento de modelos
- **View**: `ModelPerformanceTrendView`
- **Autenticación**: Requerida

#### `GET /api/v1/ml/best-models/` o `GET /api/v1/model-metrics/best/`
- **Descripción**: Mejores modelos según métricas
- **View**: `BestModelsView`
- **Autenticación**: Requerida

#### `GET /api/v1/ml/production-models/` o `GET /api/v1/model-metrics/production/`
- **Descripción**: Modelos en producción
- **View**: `ProductionModelsView`
- **Autenticación**: Requerida

#### `POST /api/v1/ml/model-comparison/` o `POST /api/v1/model-metrics/compare/`
- **Descripción**: Compara modelos
- **View**: `ModelComparisonView`
- **Autenticación**: Requerida

#### `POST /api/v1/ml/promote/<version>/`
- **Descripción**: Promueve modelo a producción (solo admin)
- **View**: `PromoteModelView`
- **Autenticación**: Requerida (solo admin)

---

### 9. **Configuración del Sistema**

#### `GET /api/v1/config/ml/`
- **Descripción**: Configuración del sistema ML
- **View**: `SystemMLConfigView`
- **Autenticación**: Requerida

---

## 🏗️ Arquitectura de Exposición

### Estructura de Vistas ML

```
backend/api/views/ml/
├── __init__.py                    # Exporta todas las vistas
├── model_views.py                 # Gestión de modelos (status, load, unload)
├── training_views.py              # Trabajos de entrenamiento
├── calibration_views.py          # Calibración
├── incremental_views.py           # Entrenamiento incremental
├── metrics_crud_views.py          # CRUD de métricas
├── metrics_analysis_views.py      # Análisis de métricas
└── metrics_comparison_views.py    # Comparación de modelos
```

### Servicios ML

```
backend/training/services/ml/
├── ml_service.py                  # Servicio principal (singleton)
└── prediction_service.py          # Servicio de predicción
```

### Módulo ML Core

```
backend/ml/
├── prediction/                    # Predicción
│   ├── predict.py                 # PredictorCacao
│   └── calibrated_predict.py      # Predictor calibrado
├── regression/                    # Modelos de regresión
├── segmentation/                  # Segmentación
├── measurement/                   # Medición y calibración
└── pipeline/                      # Pipelines de entrenamiento
```

---

## 📝 Documentación Swagger/OpenAPI

Todos los endpoints están documentados con **drf-yasg** (Swagger/OpenAPI):

- **Acceso**: `http://127.0.0.1:8000/swagger/` o `/redoc/`
- **Tags**: Los endpoints ML están organizados en tags:
  - `Modelos`
  - `ML`
  - `Dataset`
  - `Inicialización`
  - `Medición`
  - `Entrenamiento`

---

## 🔐 Autenticación

Todos los endpoints ML requieren:
- **Autenticación JWT**: Token en header `Authorization: Bearer <token>`
- **Permisos**: La mayoría requiere `IsAuthenticated`
- **Admin**: Algunos endpoints requieren `IsAdminUser`:
  - `AutoTrainView`
  - `PromoteModelView`

---

## 💡 Funcionalidades Adicionales que Podrían Exponerse

### 1. **Health Check Específico de ML**
```python
GET /api/v1/ml/health/
```
- Verificar estado de modelos, GPU, memoria
- Útil para monitoreo

### 2. **Información de Modelos Disponibles**
```python
GET /api/v1/ml/models/available/
```
- Listar todos los modelos entrenados disponibles
- Versiones, métricas, fechas

### 3. **Descarga de Modelos**
```python
GET /api/v1/ml/models/<version>/download/
```
- Descargar artefactos de modelos (para backup/transferencia)

### 4. **Predicción sin Guardar**
```python
POST /api/v1/ml/predict/
```
- Endpoint dedicado solo para predicción (sin guardar en BD)
- Útil para testing/desarrollo

### 5. **Estadísticas de Uso de Modelos**
```python
GET /api/v1/ml/usage/stats/
```
- Número de predicciones por modelo
- Tiempo promedio de predicción
- Tasa de éxito/error

### 6. **Exportar Métricas**
```python
GET /api/v1/ml/metrics/export/
```
- Exportar métricas en Excel/CSV

### 7. **Validación de Imagen antes de Predicción**
```python
POST /api/v1/ml/validate-image/
```
- Validar si una imagen es adecuada para predicción
- Sin ejecutar predicción completa

---

## 🚀 Cómo Usar los Endpoints

### Ejemplo: Análisis de Imagen

```bash
# 1. Autenticarse
POST /api/v1/auth/login/
{
  "username": "usuario",
  "password": "contraseña"
}

# 2. Verificar estado de modelos
GET /api/v1/models/status/
Authorization: Bearer <token>

# 3. Si no están cargados, cargarlos
POST /api/v1/models/load/
Authorization: Bearer <token>

# 4. Analizar imagen
POST /api/v1/scan/measure/
Authorization: Bearer <token>
Content-Type: multipart/form-data
{
  "image": <archivo_imagen>,
  "lote_id": 1,
  "finca_id": 1
}
```

### Ejemplo: Entrenamiento

```bash
# 1. Crear trabajo de entrenamiento
POST /api/v1/ml/train/
Authorization: Bearer <token>
{
  "epochs": 50,
  "batch_size": 16,
  "learning_rate": 0.0001,
  "model_type": "hybrid"
}

# 2. Ver estado
GET /api/v1/train/jobs/<job_id>/status/
Authorization: Bearer <token>
```

---

## 📊 Resumen de Endpoints por Categoría

| Categoría | Endpoints | Descripción |
|-----------|-----------|-------------|
| **Predicción** | 3 | Análisis individual, calibrado, batch |
| **Modelos** | 3 | Status, load, unload |
| **Entrenamiento** | 4 | Crear, listar, status, auto-train |
| **Calibración** | 2 | Status, upload |
| **Incremental** | 5 | Status, train, upload, models, data |
| **Métricas** | 10+ | CRUD, análisis, comparación, tendencias |
| **Configuración** | 1 | Config ML |
| **Inicialización** | 1 | Auto-initialize |
| **Dataset** | 1 | Validación |

**Total: ~30 endpoints ML**

---

## ✅ Conclusión

El sistema ML de CacaoScan está **completamente expuesto** a través de una API REST bien estructurada. Los endpoints cubren:

- ✅ Predicción y análisis
- ✅ Gestión de modelos
- ✅ Entrenamiento
- ✅ Calibración
- ✅ Métricas y monitoreo
- ✅ Configuración

La exposición sigue buenas prácticas:
- Autenticación JWT
- Documentación Swagger
- Manejo de errores
- Cache donde es apropiado
- Patrones de servicio (singleton para modelos)

Si necesitas exponer funcionalidades adicionales, puedes seguir el mismo patrón usado en `backend/api/views/ml/`.

