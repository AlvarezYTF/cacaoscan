"""
Configuración de URLs para la app de imágenes de cacao.

Define las rutas para:
- Endpoints de predicción e historial de imágenes (usuario)
- Endpoints administrativos para gestión de datos
- Endpoints de entrenamiento de modelos ML
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CacaoImagePredictionView, CacaoImageViewSet
from .admin_views import AdminImageViewSet, MLTrainingView, AdminDataManagementView

# Configurar router para ViewSet de usuarios
router = DefaultRouter()
router.register(r'', CacaoImageViewSet, basename='cacaoimage')

# Configurar router para ViewSet administrativo
admin_router = DefaultRouter()
admin_router.register(r'images', AdminImageViewSet, basename='admin-cacaoimage')

# Nombre de la aplicación para namespacing
app_name = 'images'

urlpatterns = [
    # ==========================================
    # ENDPOINTS DE USUARIO
    # ==========================================
    
    # Endpoint específico para predicción
    path('predict/', CacaoImagePredictionView.as_view(), name='predict'),
    
    # Endpoints del ViewSet de usuario (CRUD básico)
    # GET /api/images/ - Lista imágenes (filtros básicos)
    # POST /api/images/ - Crea nueva imagen (sin predicción)
    # GET /api/images/{id}/ - Obtiene imagen específica
    # PUT/PATCH /api/images/{id}/ - Actualiza metadatos básicos
    # DELETE /api/images/{id}/ - Elimina imagen (si es propietario)
    # GET /api/images/stats/ - Estadísticas de predicciones
    path('', include(router.urls)),
    
    # ==========================================
    # ENDPOINTS ADMINISTRATIVOS
    # ==========================================
    
    # Gestión avanzada de imágenes (solo administradores)
    path('admin/', include([
        # CRUD administrativo completo con filtros avanzados
        # GET /api/images/admin/images/ - Lista todas las imágenes (filtros admin)
        # POST /api/images/admin/images/ - Crea imagen con datos completos
        # GET /api/images/admin/images/{id}/ - Detalles completos de imagen
        # PUT/PATCH /api/images/admin/images/{id}/ - Actualiza cualquier campo
        # DELETE /api/images/admin/images/{id}/ - Elimina imagen (cualquiera)
        # GET /api/images/admin/images/admin-stats/ - Estadísticas administrativas
        # POST /api/images/admin/images/bulk-update/ - Actualización masiva
        # GET /api/images/admin/images/export-csv/ - Exportar datos CSV
        path('', include(admin_router.urls)),
        
        # Entrenamiento de modelos ML
        # POST /api/images/admin/train/regression/ - Entrenar modelo de regresión
        # POST /api/images/admin/train/vision/ - Entrenar modelo de visión
        # GET /api/images/admin/train/status/{job_id}/ - Estado de entrenamiento
        # GET /api/images/admin/train/jobs/ - Lista todos los trabajos
        path('train/regression/', MLTrainingView.as_view(), {'model_type': 'regression'}, name='train-regression'),
        path('train/vision/', MLTrainingView.as_view(), {'model_type': 'vision'}, name='train-vision'),
        path('train/status/<str:job_id>/', MLTrainingView.as_view(), name='training-status'),
        path('train/jobs/', MLTrainingView.as_view(), name='training-jobs'),
        
        # Gestión avanzada de datos
        # POST /api/images/admin/data/validate-integrity/ - Validar integridad de datos
        path('data/', include([
            path('validate-integrity/', AdminDataManagementView.as_view(), name='validate-integrity'),
        ])),
    ])),
]

"""
Estructura completa de URLs:

==========================================
ENDPOINTS DE USUARIO (Acceso público/autenticado)
==========================================

POST /api/images/predict/
    - Sube imagen y realiza predicción completa
    - Guarda en BD y devuelve resultados ML
    - Formato respuesta: {"id": 1, "width": ..., "height": ..., etc.}

GET /api/images/
    - Lista predicciones realizadas por el usuario
    - Filtros: ?processed=true&quality=good&batch=001&date_from=2024-01-01
    - Paginación automática
    - Formato respuesta: {"count": N, "results": [...]}

GET /api/images/{id}/
    - Obtiene detalles de una predicción específica
    - Solo si es propietario o administrador
    - Formato respuesta: CacaoImageSerializer completo

PUT/PATCH /api/images/{id}/
    - Actualiza metadatos básicos (batch_number, origin, notes)
    - Solo propietario o administrador
    - Campos ML son read-only para usuarios normales

DELETE /api/images/{id}/
    - Elimina imagen y registro
    - Solo propietario o administrador

GET /api/images/stats/
    - Estadísticas básicas de predicciones del usuario
    - Totales, distribución de calidad, promedios

==========================================
ENDPOINTS ADMINISTRATIVOS (Solo administradores)
==========================================

## Gestión avanzada de imágenes

GET /api/images/admin/images/
    - Lista TODAS las imágenes del sistema
    - Filtros avanzados: ?data_quality=complete&min_quality=0.8&defect=none
    - Acceso completo a todos los registros

POST /api/images/admin/images/
    - Crea imagen con datos completos (incluyendo predicciones)
    - Permite establecer todos los campos ML manualmente

GET /api/images/admin/images/{id}/
    - Detalles completos de cualquier imagen
    - Acceso a todos los campos y metadatos

PUT/PATCH /api/images/admin/images/{id}/
    - Actualiza CUALQUIER campo de la imagen
    - Incluye campos ML (width, height, thickness, weight, quality_score)
    - Validaciones específicas para administradores

DELETE /api/images/admin/images/{id}/
    - Elimina cualquier imagen del sistema
    - Elimina también el archivo físico

GET /api/images/admin/images/admin-stats/
    - Estadísticas administrativas detalladas
    - Métricas de todo el sistema
    - Distribución de calidad, defectos, dimensiones
    - Estadísticas temporales y de rendimiento
    - Uso de almacenamiento

POST /api/images/admin/images/bulk-update/
    - Actualización masiva de múltiples imágenes
    - Aplicar cambios a lotes de hasta 100 imágenes
    - Formato: {"image_ids": [1,2,3], "batch_number": "LOTE001"}

GET /api/images/admin/images/export-csv/
    - Exporta datos completos en formato CSV
    - Incluye todos los campos y metadatos
    - Respeta filtros aplicados en la consulta

## Entrenamiento de modelos ML

POST /api/images/admin/train/regression/
    - Inicia entrenamiento del modelo de regresión
    - Parámetros: epochs, learning_rate, batch_size, validation_split
    - Filtros de datos: min_quality_score, exclude_defective, only_processed
    - Respuesta: job_id para monitorear progreso

POST /api/images/admin/train/vision/
    - Inicia entrenamiento del modelo de visión CNN
    - Parámetros específicos para modelos de visión
    - Validaciones adicionales para CNN
    - Respuesta: job_id para monitorear progreso

GET /api/images/admin/train/status/{job_id}/
    - Estado detallado de un trabajo de entrenamiento
    - Progreso en tiempo real (% completado, época actual)
    - Métricas actuales (loss, accuracy, validation metrics)
    - Tiempos estimados de finalización

GET /api/images/admin/train/jobs/
    - Lista todos los trabajos de entrenamiento
    - Histórico completo con estados y resultados
    - Filtros por estado: pending, running, completed, failed

## Gestión avanzada de datos

POST /api/images/admin/data/validate-integrity/
    - Valida integridad de todos los datos
    - Verifica archivos de imagen existentes
    - Detecta inconsistencias en metadatos
    - Identifica valores atípicos en dimensiones
    - Calcula densidades anómalas

==========================================
PERMISOS Y SEGURIDAD
==========================================

Usuarios normales:
- Pueden subir imágenes y obtener predicciones
- Solo ven sus propias imágenes
- No pueden modificar campos ML
- Acceso limitado a estadísticas

Administradores (IsAdminUser):
- Acceso completo a todos los endpoints
- Pueden modificar cualquier campo
- Acceso a funciones de entrenamiento
- Estadísticas completas del sistema
- Operaciones masivas y de mantenimiento

==========================================
EJEMPLOS DE USO
==========================================

## Usuario normal - Predicción básica:
```
POST /api/images/predict/
Content-Type: multipart/form-data

{
  "image": <archivo>,
  "batch_number": "LOTE001"
}
```

## Administrador - Actualización masiva:
```
POST /api/images/admin/images/bulk-update/
Content-Type: application/json

{
  "image_ids": [1, 2, 3, 4, 5],
  "predicted_quality": "excellent",
  "batch_number": "LOTE_CORREGIDO_001"
}
```

## Administrador - Entrenamiento:
```
POST /api/images/admin/train/regression/
Content-Type: application/json

{
  "epochs": 100,
  "learning_rate": 0.001,
  "batch_size": 32,
  "validation_split": 0.2,
  "min_quality_score": 0.7,
  "exclude_defective": true
}
```

## Administrador - Filtros avanzados:
```
GET /api/images/admin/images/?data_quality=complete&min_quality=0.8&date_from=2024-01-01&defect=none
```

==========================================
RESPUESTAS TÍPICAS
==========================================

## Predicción exitosa:
```json
{
  "success": true,
  "id": 1,
  "width": 12.5,
  "height": 8.3,
  "thickness": 4.2,
  "predicted_weight": 1.25,
  "confidence_level": "high",
  "processing_time": 0.125
}
```

## Estado de entrenamiento:
```json
{
  "job_id": "uuid-123",
  "model_type": "regression",
  "status": "running",
  "progress": 45.50,
  "current_epoch": 45,
  "total_epochs": 100,
  "current_loss": 0.125,
  "validation_accuracy": 0.876
}
```

## Estadísticas administrativas:
```json
{
  "total_images": 1250,
  "processed_images": 1180,
  "quality_distribution": {
    "excellent": 450,
    "good": 520,
    "fair": 180,
    "poor": 30
  },
  "model_performance": {
    "vision_model": {"accuracy": 0.89},
    "regression_model": {"r2_score": 0.82}
  }
}
```
"""
