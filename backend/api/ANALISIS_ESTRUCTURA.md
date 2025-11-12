# 📊 Análisis de Estructura - API de CacaoScan

## 🎯 Resumen General

La app `api` es el núcleo de la API REST de CacaoScan. Actúa como punto de entrada principal y coordina las diferentes apps modulares del sistema.

---

## 📋 Tablas/Modelos Principales

### Modelos Propios de la App `api`

#### 1. **LoginHistory** (`api_loginhistory`)
**Propósito**: Registrar historial de inicios de sesión de usuarios.

**Campos principales**:
- `usuario` (ForeignKey → User)
- `ip_address` (GenericIPAddressField)
- `user_agent` (TextField)
- `login_time` (DateTimeField)
- `logout_time` (DateTimeField, nullable)
- `session_duration` (DurationField, nullable)
- `success` (BooleanField)
- `failure_reason` (CharField, nullable)

**Índices**:
- `usuario`, `-login_time`
- `ip_address`
- `login_time`
- `success`

---

#### 2. **ReporteGenerado** (`api_reportegenerado`)
**Propósito**: Gestionar reportes generados del sistema.

**Campos principales**:
- `usuario` (ForeignKey → User)
- `tipo_reporte` (CharField): calidad, defectos, rendimiento, finca, lote, usuario, auditoria, personalizado
- `formato` (CharField): pdf, excel, csv, json
- `estado` (CharField): generando, completado, fallido, expirado
- `titulo` (CharField)
- `descripcion` (TextField, nullable)
- `archivo` (FileField)
- `parametros` (JSONField)
- `filtros_aplicados` (JSONField)
- `fecha_solicitud`, `fecha_generacion`, `fecha_expiracion` (DateTimeField)

**Propiedades**:
- `tamano_archivo_mb`: Tamaño en MB
- `archivo_url`: URL del archivo
- `tiempo_generacion_segundos`: Tiempo en segundos
- `esta_expirado`: Si el reporte expiró

---

#### 3. **ModelMetrics** (`api_modelmetrics`)
**Propósito**: Almacenar métricas detalladas de modelos de machine learning.

**Campos principales**:
- `model_name` (CharField)
- `model_type` (CharField): regression, classification, segmentation, incremental
- `target` (CharField): alto, ancho, grosor, peso, calidad, variedad
- `version` (CharField)
- `created_by` (ForeignKey → User)
- `metric_type` (CharField): training, validation, test, incremental

**Métricas**:
- `mae`, `mse`, `rmse`, `r2_score`, `mape` (FloatField)
- `additional_metrics` (JSONField)

**Dataset**:
- `dataset_size`, `train_size`, `validation_size`, `test_size` (PositiveIntegerField)

**Parámetros de entrenamiento**:
- `epochs`, `batch_size` (PositiveIntegerField)
- `learning_rate` (FloatField)
- `model_params` (JSONField)

**Tiempos**:
- `training_time_seconds` (PositiveIntegerField, nullable)
- `inference_time_ms` (FloatField, nullable)

**Métricas adicionales**:
- `stability_score` (FloatField, nullable)
- `knowledge_retention` (FloatField, nullable)

**Flags**:
- `is_best_model` (BooleanField)
- `is_production_model` (BooleanField)

---

### Modelos Importados desde Apps Modulares

La app `api` importa modelos desde otras apps para evitar duplicación:

#### Desde `auth_app`:
- **EmailVerificationToken**: Tokens de verificación de email
- **UserProfile**: Perfil extendido de usuario

#### Desde `fincas_app`:
- **Finca**: Fincas de cacao
- **Lote**: Lotes dentro de fincas

#### Desde `images_app`:
- **CacaoImage**: Imágenes de granos de cacao
- **CacaoPrediction**: Predicciones de modelos ML

#### Desde `notifications`:
- **Notification**: Notificaciones del sistema

#### Desde `audit`:
- **ActivityLog**: Logs de actividad/auditoría

#### Desde `training`:
- **TrainingJob**: Trabajos de entrenamiento ML

#### Desde `core`:
- **SystemSettings**: Configuración del sistema

---

## 🔗 Relaciones entre Modelos

```
User (Django)
├── LoginHistory (1:N) - Historial de logins
├── ReporteGenerado (1:N) - Reportes generados
├── ModelMetrics (1:N) - Métricas de modelos creados
├── UserProfile (1:1) - Perfil extendido
├── EmailVerificationToken (1:1) - Token de verificación
├── Finca (1:N) - Fincas del agricultor
│   └── Lote (1:N) - Lotes de la finca
│       └── CacaoImage (1:N) - Imágenes del lote
│           └── CacaoPrediction (1:1) - Predicción de la imagen
└── Notification (1:N) - Notificaciones del usuario
```

---

## 📁 Estructura de Archivos

### Vistas Principales

1. **`views.py`** (5160 líneas) - Vista principal con todos los endpoints
2. **`fincas_views.py`** - Endpoints de fincas
3. **`lotes_views.py`** - Endpoints de lotes
4. **`incremental_views.py`** - Entrenamiento incremental
5. **`model_metrics_views.py`** - Métricas de modelos
6. **`ml_views.py`** - Endpoints ML
7. **`calibration_views.py`** - Calibración de píxeles
8. **`batch_analysis_views.py`** - Análisis por lotes
9. **`config_views.py`** - Configuración del sistema
10. **`notifications_views.py`** - Notificaciones
11. **`audit_views.py`** - Auditoría
12. **`email_views.py`** - Emails
13. **`otp_views.py`** - OTP de verificación
14. **`report_views.py`** - Reportes
15. **`refactored_views.py`** - Vistas refactorizadas

### Servicios

1. **`services/auth_service.py`** - Servicio de autenticación
2. **`services/analysis_service.py`** - Servicio de análisis
3. **`services/finca_service.py`** - Servicio de fincas
4. **`services/image_service.py`** - Servicio de imágenes
5. **`services/report_service.py`** - Servicio de reportes
6. **`services/base.py`** - Clase base para servicios

### Otros Archivos Importantes

- **`serializers.py`** (1177 líneas) - Todos los serializers
- **`urls.py`** - Configuración de URLs
- **`utils.py`** - Utilidades (create_error_response, etc.)
- **`middleware.py`** - Middleware personalizado
- **`tasks.py`** - Tareas (antes Celery, ahora sincrónicas)
- **`models.py`** - Modelos únicos de API

---

## 🌐 Endpoints Principales

### Autenticación (`/api/v1/auth/`)
- `POST /auth/login/` - Iniciar sesión
- `POST /auth/register/` - Registro
- `POST /auth/logout/` - Cerrar sesión
- `GET /auth/profile/` - Perfil de usuario
- `POST /auth/refresh/` - Refrescar token
- `POST /auth/change-password/` - Cambiar contraseña
- `POST /auth/verify-email/` - Verificar email
- `POST /auth/resend-verification/` - Reenviar verificación
- `POST /auth/send-otp/` - Enviar OTP
- `POST /auth/verify-otp/` - Verificar OTP
- `POST /auth/forgot-password/` - Recuperar contraseña
- `POST /auth/reset-password/` - Resetear contraseña

### Imágenes (`/api/v1/images/`)
- `GET /images/` - Listar imágenes
- `GET /images/<id>/` - Detalle de imagen
- `PUT /images/<id>/update/` - Actualizar imagen
- `DELETE /images/<id>/delete/` - Eliminar imagen
- `GET /images/<id>/download/` - Descargar imagen
- `GET /images/stats/` - Estadísticas
- `GET /images/export/` - Exportar imágenes

### Fincas (`/api/v1/fincas/`)
- `GET, POST /fincas/` - Listar/Crear fincas
- `GET /fincas/<id>/` - Detalle de finca
- `PUT /fincas/<id>/update/` - Actualizar finca
- `DELETE /fincas/<id>/delete/` - Eliminar finca
- `POST /fincas/<id>/activate/` - Activar finca
- `GET /fincas/<id>/stats/` - Estadísticas de finca

### Lotes (`/api/v1/lotes/`)
- `GET, POST /lotes/` - Listar/Crear lotes
- `GET /lotes/<id>/` - Detalle de lote
- `PUT /lotes/<id>/update/` - Actualizar lote
- `DELETE /lotes/<id>/delete/` - Eliminar lote
- `GET /lotes/<id>/stats/` - Estadísticas de lote
- `GET /fincas/<id>/lotes/` - Lotes por finca

### Machine Learning (`/api/v1/ml/`, `/api/v1/train/`)
- `POST /scan/measure/` - Medir grano (predicción)
- `GET /models/status/` - Estado de modelos
- `POST /models/load/` - Cargar modelos
- `POST /ml/train/` - Entrenar modelo
- `GET /ml/metrics/latest/` - Últimas métricas
- `POST /ml/promote/<version>/` - Promover modelo a producción
- `GET /train/jobs/` - Listar trabajos de entrenamiento
- `POST /train/jobs/create/` - Crear trabajo de entrenamiento

### Entrenamiento Incremental (`/api/v1/incremental/`)
- `GET /incremental/status/` - Estado del sistema incremental
- `POST /incremental/train/` - Entrenar incrementalmente
- `POST /incremental/upload/` - Subir datos incrementales
- `GET /incremental/models/` - Versiones de modelos
- `GET /incremental/data/` - Versiones de datos

### Métricas de Modelos (`/api/v1/model-metrics/`)
- `GET /model-metrics/` - Listar métricas
- `POST /model-metrics/create/` - Crear métricas
- `GET /model-metrics/<id>/` - Detalle de métricas
- `PUT /model-metrics/<id>/update/` - Actualizar métricas
- `DELETE /model-metrics/<id>/delete/` - Eliminar métricas
- `GET /model-metrics/stats/` - Estadísticas
- `GET /model-metrics/trend/` - Tendencia de rendimiento
- `GET /model-metrics/compare/` - Comparar modelos
- `GET /model-metrics/best/` - Mejores modelos
- `GET /model-metrics/production/` - Modelos en producción

### Notificaciones (`/api/v1/notifications/`)
- `GET /notifications/` - Listar notificaciones
- `POST /notifications/create/` - Crear notificación
- `GET /notifications/<id>/` - Detalle de notificación
- `POST /notifications/<id>/read/` - Marcar como leída
- `POST /notifications/mark-all-read/` - Marcar todas como leídas
- `GET /notifications/unread-count/` - Contador de no leídas
- `GET /notifications/stats/` - Estadísticas

### Auditoría (`/api/v1/audit/`)
- `GET /audit/activity-logs/` - Logs de actividad
- `GET /audit/login-history/` - Historial de logins
- `GET /audit/stats/` - Estadísticas de auditoría

### Reportes (`/api/v1/reportes/`)
- `GET, POST /reportes/` - Listar/Crear reportes
- `GET /reportes/<id>/` - Detalle de reporte
- `GET /reportes/<id>/download/` - Descargar reporte
- `DELETE /reportes/<id>/delete/` - Eliminar reporte
- `GET /reportes/stats/` - Estadísticas
- `POST /reportes/cleanup/` - Limpiar reportes expirados

### Calibración (`/api/v1/calibration/`)
- `GET /calibration/status/` - Estado de calibración
- `POST /calibration/` - Calibrar píxeles
- `POST /scan/measure/calibrated/` - Medir con calibración

### Configuración (`/api/v1/config/`)
- `GET, PUT /config/` - Configuración general
- `GET, PUT /config/general/` - Configuración general
- `GET, PUT /config/security/` - Configuración de seguridad
- `GET, PUT /config/ml/` - Configuración ML
- `GET /config/system/` - Información del sistema

---

## 🔧 Servicios Disponibles

### 1. **AuthenticationService** (`services/auth_service.py`)
**Responsabilidades**:
- Login/Logout de usuarios
- Registro de usuarios
- Verificación de email
- Recuperación de contraseña
- Gestión de tokens JWT

### 2. **AnalysisService** (`services/analysis_service.py`)
**Responsabilidades**:
- Análisis de imágenes de cacao
- Predicciones de modelos ML
- Procesamiento de imágenes

### 3. **FincaService** (`services/finca_service.py`)
**Responsabilidades**:
- Gestión de fincas
- Validaciones de fincas
- Estadísticas de fincas

### 4. **ImageService** (`services/image_service.py`)
**Responsabilidades**:
- Gestión de imágenes
- Procesamiento de imágenes
- Validación de imágenes

### 5. **ReportService** (`services/report_service.py`)
**Responsabilidades**:
- Generación de reportes
- Exportación de datos
- Gestión de reportes

---

## 📊 Serializers Principales

### Autenticación
- `LoginSerializer`
- `RegisterSerializer`
- `ChangePasswordSerializer`
- `EmailVerificationSerializer`
- `UserSerializer`
- `UserProfileSerializer`

### Imágenes y Predicciones
- `CacaoImageSerializer`
- `CacaoPredictionSerializer`
- `CacaoImageDetailSerializer`
- `ScanMeasureResponseSerializer`

### Fincas y Lotes
- `FincaSerializer`
- `FincaListSerializer`
- `FincaDetailSerializer`
- `LoteSerializer`
- `LoteListSerializer`
- `LoteDetailSerializer`

### Machine Learning
- `ModelsStatusSerializer`
- `TrainingJobSerializer`
- `TrainingJobCreateSerializer`
- `AutoTrainConfigSerializer`
- `ModelMetricsSerializer`
- `ModelMetricsCreateSerializer`
- `ModelMetricsUpdateSerializer`

### Notificaciones
- `NotificationSerializer`
- `NotificationListSerializer`
- `NotificationCreateSerializer`

### Reportes
- `ReporteGeneradoSerializer` (implícito)

---

## 🔄 Flujo de Datos Típico

### 1. **Análisis de Imagen**
```
Usuario → POST /scan/measure/
  → AnalysisService
    → ml.prediction.predict (modelo híbrido)
      → CacaoImage (guardar imagen)
      → CacaoPrediction (guardar predicción)
  → Response con medidas y confianzas
```

### 2. **Entrenamiento de Modelo**
```
Admin → POST /ml/train/
  → ml_views.AutoTrainView
    → ml.pipeline.train_all.run_training_pipeline
      → Entrenar modelo híbrido
      → Guardar modelo (hybrid.pt)
      → Guardar escaladores
      → ModelMetrics (guardar métricas)
  → Response con estado
```

### 3. **Gestión de Finca**
```
Agricultor → POST /fincas/
  → FincaService
    → Validaciones
    → Finca.objects.create()
  → Response con finca creada
```

---

## 🗄️ Base de Datos - Tablas Principales

### Tablas de la App `api`
1. `api_loginhistory` - Historial de logins
2. `api_reportegenerado` - Reportes generados
3. `api_modelmetrics` - Métricas de modelos

### Tablas de Apps Modulares (referenciadas)
- `auth_app_emailverificationtoken` - Tokens de verificación
- `auth_app_userprofile` - Perfiles de usuario
- `fincas_app_finca` (alias `api_finca`) - Fincas
- `fincas_app_lote` (alias `api_lote`) - Lotes
- `images_app_cacaoimage` - Imágenes
- `images_app_cacaoprediction` - Predicciones
- `notifications_notification` - Notificaciones
- `audit_activitylog` - Logs de auditoría
- `training_trainingjob` - Trabajos de entrenamiento

---

## 🎯 Puntos Clave

1. **Arquitectura Modular**: La app `api` coordina apps modulares especializadas
2. **Modelo Híbrido**: Usa un solo modelo `hybrid.pt` (no múltiples modelos)
3. **Sin Celery**: Entrenamiento ahora es sincrónico (sin workers)
4. **Servicios**: Lógica de negocio encapsulada en servicios
5. **Serializers**: Validación y transformación de datos centralizada

---

## 📝 Notas Importantes

- El mensaje "Eliminada FK antigua / Creada nueva FK" es normal durante migraciones
- Los modelos están siendo migrados de `fincas_app` a `api` (renombrado de tablas)
- `ModelMetrics.training_job` está comentado temporalmente
- Los tests de SonarQube verifican correcciones de bugs, no funcionalidad completa

