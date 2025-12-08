# Análisis Arquitectónico Completo - CacaoScan

## Resumen del Proyecto

**CacaoScan** es una plataforma web para análisis digital de granos de cacao mediante visión por computadora y aprendizaje automático. Utiliza Django REST Framework en el backend y Vue.js 3 en el frontend.

---

## 1. MODELOS / ENTITIES

### Backend - Modelos de Dominio

#### `fincas_app/models.py`
- **Finca**: Modelo para gestionar fincas de cacao con información geográfica y estadísticas
- **Lote**: Modelo para gestionar lotes de cacao dentro de fincas

#### `images_app/models.py`
- **CacaoImage**: Modelo para almacenar imágenes de granos de cacao procesadas
- **CacaoPrediction**: Modelo para almacenar resultados de predicciones ML (dimensiones, peso, confianza)

#### `training/models.py`
- **TrainingJob**: Modelo para gestionar trabajos de entrenamiento de modelos ML
- **ModelMetrics**: Modelo para almacenar métricas detalladas de modelos de machine learning

#### `auth_app/models.py`
- **EmailVerificationToken**: Modelo para tokens de verificación de email
- **UserProfile**: Perfil extendido del usuario con información específica de agricultores
- **PendingEmailVerification**: Modelo para verificación pendiente de email con código OTP

#### `personas/models.py`
- **Persona**: Modelo para información personal complementaria del usuario (normalizado 3FN)
- **PendingRegistration**: Modelo para almacenar registros pendientes de verificación de correo

#### `notifications/models.py`
- **Notification**: Modelo para notificaciones del sistema

#### `audit/models.py`
- **ActivityLog**: Modelo para registrar actividades del sistema
- **LoginHistory**: Modelo para registrar el historial de inicios de sesión

#### `core/models.py`
- **TimeStampedModel**: Modelo abstracto que provee campos created_at y updated_at
- **SystemSettings**: Modelo para almacenar la configuración del sistema (singleton)

#### `catalogos/models.py`
- **Departamento**: Tabla que almacena los departamentos de Colombia
- **Municipio**: Tabla que almacena los municipios de Colombia
- **Tema**: Tabla de catálogo que almacena las categorías generales del sistema
- **Parametro**: Tabla que almacena los parámetros o valores asociados a un tema

#### `reports/models.py`
- **ReporteGenerado**: Modelo para gestionar reportes generados del sistema

---

## 2. SERVICIOS / SERVICES

### Backend - Servicios de Negocio

#### `api/services/base.py`
- **BaseService**: Clase base para todos los servicios con funcionalidades comunes
- **ServiceResult**: Clase para encapsular resultados de servicios
- **ServiceError**: Excepción base para errores de servicios
- **ValidationServiceError**: Error de validación en servicios
- **PermissionServiceError**: Error de permisos en servicios
- **NotFoundServiceError**: Error de recurso no encontrado en servicios

#### `api/services/auth/`
- **LoginService**: Servicio para autenticación y login de usuarios
- **RegistrationService**: Servicio para registro de nuevos usuarios
- **PasswordService**: Servicio para gestión de contraseñas
- **VerificationService**: Servicio para verificación de emails
- **ProfileService**: Servicio para gestión de perfiles de usuario
- **AuthenticationService**: Servicio combinado de autenticación (compatibilidad hacia atrás)

#### `api/services/`
- **AnalysisService**: Servicio para análisis de imágenes y predicciones
- **StatsService**: Servicio para estadísticas del sistema

#### `api/services/email/`
- **EmailService**: Servicio para envío de emails

#### `fincas_app/services/`
- **FincaService**: Servicio para gestión de fincas
- **LoteService**: Servicio para gestión de lotes
- **FincaCRUDService**: Servicio CRUD para fincas
- **FincaStatsService**: Servicio para estadísticas de fincas
- **FincaValidationService**: Servicio para validación de fincas

#### `images_app/services/image/`
- **ImageManagementService**: Servicio para gestión de imágenes
- **ImageProcessingService**: Servicio para procesamiento de imágenes
- **ImageStorageService**: Servicio para almacenamiento de imágenes

#### `reports/services/report/`
- **ReportService**: Servicio principal para reportes
- **ReportGenerationService**: Servicio para generación de reportes
- **ReportManagementService**: Servicio para gestión de reportes

#### `reports/services/report/excel/`
- **ExcelBaseGenerator**: Clase base para generadores de Excel
- **ExcelAgricultoresGenerator**: Generador de reportes Excel de agricultores
- **ExcelUsuariosGenerator**: Generador de reportes Excel de usuarios
- **ExcelAnalisisGenerator**: Generador de reportes Excel de análisis
- **CacaoReportExcelGenerator**: Generador principal de reportes Excel

#### `reports/services/report/`
- **CacaoReportPDFGenerator**: Generador de reportes PDF

#### `training/services/ml/`
- **MLService**: Servicio para gestión del ciclo de vida de modelos ML (singleton)
- **PredictionService**: Servicio para predicciones ML

---

## 3. CONTROLADORES / VIEWS / CONTROLLERS

### Backend - Vistas API

#### `auth_app/views/`
- **LoginView**: Vista para login de usuarios
- **RegisterView**: Vista para registro de usuarios
- **LogoutView**: Vista para logout
- **UserProfileView**: Vista para perfil de usuario
- **RefreshTokenView**: Vista para refrescar tokens JWT
- **ChangePasswordView**: Vista para cambio de contraseña
- **EmailVerificationView**: Vista para verificación de email
- **ResendVerificationView**: Vista para reenvío de verificación
- **PreRegisterView**: Vista para pre-registro
- **VerifyEmailPreRegistrationView**: Vista para verificar email en pre-registro
- **ForgotPasswordView**: Vista para recuperación de contraseña
- **ResetPasswordView**: Vista para reset de contraseña
- **SendOtpView**: Vista para envío de OTP
- **VerifyOtpView**: Vista para verificación de OTP
- **UserListView**: Vista para listar usuarios
- **UserUpdateView**: Vista para actualizar usuarios
- **UserDeleteView**: Vista para eliminar usuarios
- **UserStatsView**: Vista para estadísticas de usuarios
- **AdminStatsView**: Vista para estadísticas administrativas
- **UserDetailView**: Vista para detalle de usuario

#### `fincas_app/views/`
- **FincaListCreateView**: Vista para listar y crear fincas
- **FincaDetailView**: Vista para detalle de finca
- **FincaUpdateView**: Vista para actualizar finca
- **FincaDeleteView**: Vista para eliminar finca
- **FincaActivateView**: Vista para activar/desactivar finca
- **FincaStatsView**: Vista para estadísticas de fincas
- **LoteListCreateView**: Vista para listar y crear lotes
- **LoteDetailView**: Vista para detalle de lote
- **LoteUpdateView**: Vista para actualizar lote
- **LoteDeleteView**: Vista para eliminar lote
- **LoteStatsView**: Vista para estadísticas de lotes
- **LotesPorFincaView**: Vista para listar lotes por finca

#### `images_app/views/`
- **ScanMeasureView**: Vista para escanear y medir granos
- **ImagesListView**: Vista para listar imágenes
- **ImageDetailView**: Vista para detalle de imagen
- **ImagesStatsView**: Vista para estadísticas de imágenes
- **ImageUpdateView**: Vista para actualizar imagen
- **ImageDeleteView**: Vista para eliminar imagen
- **ImageDownloadView**: Vista para descargar imagen
- **ImagesExportView**: Vista para exportar imágenes
- **AdminImagesListView**: Vista administrativa para listar imágenes
- **AdminImageDetailView**: Vista administrativa para detalle de imagen
- **AdminImageUpdateView**: Vista administrativa para actualizar imagen
- **AdminImageDeleteView**: Vista administrativa para eliminar imagen
- **AdminBulkUpdateView**: Vista administrativa para actualización masiva
- **AdminDatasetStatsView**: Vista administrativa para estadísticas de dataset
- **BatchAnalysisView**: Vista para análisis por lotes

#### `api/views/ml/`
- **CalibrationStatusView**: Vista para estado de calibración
- **CalibrationView**: Vista para calibración
- **CalibratedScanMeasureView**: Vista para escaneo calibrado
- **IncrementalTrainingStatusView**: Vista para estado de entrenamiento incremental
- **IncrementalTrainingView**: Vista para entrenamiento incremental
- **IncrementalDataUploadView**: Vista para subida de datos incrementales
- **IncrementalModelVersionsView**: Vista para versiones de modelos incrementales
- **IncrementalDataVersionsView**: Vista para versiones de datos incrementales
- **ModelMetricsListView**: Vista para listar métricas de modelos
- **ModelMetricsDetailView**: Vista para detalle de métricas
- **ModelMetricsCreateView**: Vista para crear métricas
- **ModelMetricsUpdateView**: Vista para actualizar métricas
- **ModelMetricsDeleteView**: Vista para eliminar métricas
- **ModelMetricsStatsView**: Vista para estadísticas de métricas
- **ModelPerformanceTrendView**: Vista para tendencias de rendimiento
- **ModelComparisonView**: Vista para comparación de modelos
- **BestModelsView**: Vista para mejores modelos
- **ProductionModelsView**: Vista para modelos en producción
- **ModelsStatusView**: Vista para estado de modelos
- **DatasetValidationView**: Vista para validación de dataset
- **LoadModelsView**: Vista para cargar modelos
- **UnloadModelsView**: Vista para descargar modelos
- **AutoInitializeView**: Vista para inicialización automática
- **LatestMetricsView**: Vista para últimas métricas
- **PromoteModelView**: Vista para promover modelo a producción
- **AutoTrainView**: Vista para entrenamiento automático
- **TrainingJobListView**: Vista para listar trabajos de entrenamiento
- **TrainingJobCreateView**: Vista para crear trabajo de entrenamiento
- **TrainingJobStatusView**: Vista para estado de trabajo de entrenamiento

#### `api/views/notifications/`
- **NotificationListCreateView**: Vista para listar y crear notificaciones
- **NotificationDetailView**: Vista para detalle de notificación
- **NotificationMarkReadView**: Vista para marcar notificación como leída
- **NotificationMarkAllReadView**: Vista para marcar todas como leídas
- **NotificationUnreadCountView**: Vista para contar no leídas
- **NotificationStatsView**: Vista para estadísticas de notificaciones
- **NotificationCreateView**: Vista para crear notificación

#### `api/views/admin/`
- **ActivityLogListView**: Vista para listar logs de actividad
- **LoginHistoryListView**: Vista para listar historial de logins
- **AuditStatsView**: Vista para estadísticas de auditoría
- **SystemSettingsView**: Vista para configuración del sistema
- **SystemGeneralConfigView**: Vista para configuración general
- **SystemSecurityConfigView**: Vista para configuración de seguridad
- **SystemMLConfigView**: Vista para configuración ML
- **SystemInfoView**: Vista para información del sistema
- **TaskStatusView**: Vista para estado de tareas

#### `reports/views/`
- **ReporteListCreateView**: Vista para listar y crear reportes
- **ReporteDetailView**: Vista para detalle de reporte
- **ReporteDownloadView**: Vista para descargar reporte
- **ReporteDeleteView**: Vista para eliminar reporte
- **ReporteStatsView**: Vista para estadísticas de reportes
- **ReporteCleanupView**: Vista para limpieza de reportes
- **ReporteAgricultoresView**: Vista para reporte de agricultores
- **ReporteUsuariosView**: Vista para reporte de usuarios

#### `catalogos/views.py`
- **TemaViewSet**: ViewSet para temas
- **ParametroViewSet**: ViewSet para parámetros
- **DepartamentoViewSet**: ViewSet para departamentos
- **MunicipioViewSet**: ViewSet para municipios

#### `personas/views.py`
- **PersonaRegistroView**: Vista para registro de personas

---

## 4. REPOSITORIOS / MANAGERS / DAO

### Backend - Acceso a Datos

En Django, los repositorios están implícitos en los modelos a través de `Model.objects`. No hay una capa de repositorio explícita, pero los servicios actúan como capa de abstracción sobre los modelos.

**Managers personalizados:**
- Los modelos utilizan el `objects` manager estándar de Django
- Algunos modelos tienen métodos de clase que actúan como consultas especializadas (ej: `ModelMetrics.get_performance_trend()`)

---

## 5. TAREAS / WORKERS / JOBS

### Backend - Tareas Asíncronas (Celery)

#### `api/tasks/`
- **training_tasks.py**:
  - `train_model_task`: Tarea para entrenar modelos de forma asíncrona
  - `auto_train_model_task`: Tarea para entrenamiento automático de modelos
- **image_tasks.py**: Tareas para procesamiento de imágenes
- **ml_tasks.py**: Tareas para operaciones ML
- **stats_tasks.py**: Tareas para cálculo de estadísticas
- **token_cleanup.py**: Tarea para limpieza de tokens expirados

---

## 6. MOTOR DE IA / ML / PIPELINE

### Backend - Componentes ML

#### `ml/data/`
- **CacaoDatasetLoader**: Cargador de datasets de cacao
- **CacaoDataset**: Dataset de PyTorch para cacao
- **HybridDataset**: Dataset híbrido con características de píxeles
- **PixelFeatureExtractor**: Extractor de características de píxeles
- **PixelFeaturesLoader**: Cargador de características de píxeles
- **ImprovedDataLoader**: Cargador de datos mejorado
- **transforms.py**: Transformaciones de imágenes

#### `ml/regression/`
- **models.py**:
  - `MultiHeadRegression`: Modelo de regresión multi-cabeza
  - `HybridCacaoRegression`: Modelo híbrido de regresión de cacao
  - `create_model`: Función para crear modelos
- **train.py**: Script de entrenamiento para modelos de regresión
- **train_improved.py**: Script de entrenamiento mejorado
- **hybrid_trainer.py**: Entrenador para modelos híbridos
- **hybrid_training.py**: Pipeline de entrenamiento híbrido
- **hybrid_v2_training.py**: Pipeline de entrenamiento híbrido v2
- **evaluate.py**: Evaluador de modelos de regresión
- **metrics.py**: Métricas de regresión
- **scalers.py**: Escaladores para normalización
- **augmentation.py**: Data augmentation para imágenes
- **incremental_train.py**: Entrenamiento incremental

#### `ml/segmentation/`
- **cropper.py**:
  - `CacaoCropper`: Procesador de recortes de granos de cacao
- **processor.py**: Procesador de segmentación
- **infer_yolo_seg.py**:
  - `YOLOSegmentationInference`: Inferencia de segmentación YOLO
- **train_yolo.py**: Entrenamiento de modelos YOLO

#### `ml/prediction/`
- **predict.py**: Módulo de predicción principal
- **calibrated_predict.py**: Predicción calibrada

#### `ml/pipeline/`
- **train_all.py**: Pipeline completo de entrenamiento
- **hybrid_training.py**: Pipeline de entrenamiento híbrido
- **hybrid_v2_training.py**: Pipeline de entrenamiento híbrido v2

#### `ml/measurement/`
- **calibration.py**: Calibración de mediciones

#### `ml/utils/`
- **early_stopping.py**: Early stopping para entrenamiento
- **io.py**: Utilidades de I/O
- **logs.py**: Utilidades de logging
- **losses.py**: Funciones de pérdida
- **metrics.py**: Métricas generales
- **paths.py**: Utilidades de rutas
- **scalers.py**: Escaladores generales

---

## 7. UTILIDADES / HELPERS

### Backend

#### `api/utils/`
- **decorators.py**: Decoradores para vistas y funciones
- **ml_helpers.py**: Helpers para ML
- **model_imports.py**: Utilidades para importación de modelos
- **pagination.py**: Utilidades de paginación
- **permissions.py**: Utilidades de permisos

#### `core/utils/`
- Utilidades del core del sistema

#### `core/middleware/`
- Middleware personalizado

#### `api/middleware.py`
- Middleware de la API

#### `api/realtime_middleware.py`
- Middleware para tiempo real

#### `api/realtime_service.py`
- Servicio para tiempo real (WebSockets)

---

## 8. CONFIGURACIÓN / SETTINGS

### Backend

#### `cacaoscan/settings.py`
- Configuración principal de Django

#### `cacaoscan/urls.py`
- URLs principales del proyecto

#### `cacaoscan/asgi.py`
- Configuración ASGI para WebSockets

#### `cacaoscan/wsgi.py`
- Configuración WSGI

#### `cacaoscan/celery.py`
- Configuración de Celery

#### `api/cache_config.py`
- Configuración de caché

#### `api/routing.py`
- Routing para WebSockets

#### `api/consumers.py`
- Consumers de WebSockets

---

## 9. SERIALIZERS

### Backend

#### `api/serializers/`
- **auth_serializers.py**:
  - `LoginSerializer`
  - `RegisterSerializer`
  - `ChangePasswordSerializer`
  - `EmailVerificationSerializer`
  - `ResendVerificationSerializer`
  - `UserSerializer`
  - `UserProfileSerializer`
  - `SendOtpSerializer`
  - `VerifyOtpSerializer`
- **finca_serializers.py**:
  - `FincaSerializer`
  - `FincaListSerializer`
  - `FincaDetailSerializer`
  - `FincaStatsSerializer`
  - `LoteSerializer`
  - `LoteListSerializer`
  - `LoteDetailSerializer`
  - `LoteStatsSerializer`
- **image_serializers.py**: Serializers para imágenes
- **ml_serializers.py**: Serializers para ML
- **common_serializers.py**: Serializers comunes

#### `personas/serializers.py`
- **PersonaSerializer**
- **PersonaRegistroSerializer**
- **PersonaActualizacionSerializer**

#### `images_app/serializers.py`
- Serializers para imágenes

#### `catalogos/serializers.py`
- Serializers para catálogos

---

## 10. MANAGEMENT COMMANDS

### Backend

#### `api/management/commands/`
- **create_admin_user.py**: Crear usuario administrador
- **check_fk_lotes.py**: Verificar foreign keys de lotes
- **check_training.py**: Verificar entrenamiento
- **cancel_training.py**: Cancelar entrenamiento
- **clean_dataset.py**: Limpiar dataset
- **convert_cacao_images.py**: Convertir imágenes de cacao
- **make_cacao_crops.py**: Crear crops de cacao

#### `training/management/commands/`
- **train_cacao_models.py**: Entrenar modelos de cacao
- **train_unet_background.py**: Entrenar U-Net para fondo
- **train_yolo_model.py**: Entrenar modelo YOLO
- **train_all_models.py**: Entrenar todos los modelos
- **calibrate_dataset_pixels.py**: Calibrar píxeles del dataset
- **convert_cacao_images.py**: Convertir imágenes
- **verify_training_data.py**: Verificar datos de entrenamiento
- **fix_duplicate_users.py**: Corregir usuarios duplicados
- **init_api.py**: Inicializar API

#### `fincas_app/management/commands/`
- **fix_lote_foreign_key.py**: Corregir foreign key de lotes
- **clean_orphaned_lotes.py**: Limpiar lotes huérfanos

#### `images_app/management/commands/`
- **upload_dataset.py**: Subir dataset

---

## 11. FRONTEND - COMPONENTES

### Stores (Pinia)

#### `frontend/src/stores/`
- **auth.js**: Store de autenticación
- **admin.js**: Store de administración
- **analysis.js**: Store de análisis
- **audit.js**: Store de auditoría
- **config.js**: Store de configuración
- **fincas.js**: Store de fincas
- **notifications.js**: Store de notificaciones
- **prediction.js**: Store de predicciones
- **reports.js**: Store de reportes

### Services (API Clients)

#### `frontend/src/services/`
- **api.js**: Cliente API principal
- **apiClient.js**: Cliente HTTP base
- **httpClient.js**: Cliente HTTP
- **apiErrorHandler.js**: Manejador de errores de API
- **authApi.js**: API de autenticación
- **adminApi.js**: API de administración
- **auditApi.js**: API de auditoría
- **catalogosApi.js**: API de catálogos
- **configApi.js**: API de configuración
- **datasetApi.js**: API de datasets
- **fincasApi.js**: API de fincas
- **lotesApi.js**: API de lotes
- **personasApi.js**: API de personas
- **predictionApi.js**: API de predicciones
- **reportsApi.js**: API de reportes
- **reportsService.js**: Servicio de reportes
- **dashboardStatsService.js**: Servicio de estadísticas del dashboard
- **servicioAnalisis.js**: Servicio de análisis

### Composables

#### `frontend/src/composables/`
- **useAuth.js**: Composable de autenticación
- **useAuthForm.js**: Composable de formularios de autenticación
- **useAdminView.js**: Composable de vista administrativa
- **useAnalysis.js**: Composable de análisis
- **useAudit.js**: Composable de auditoría
- **useChart.js**: Composable de gráficos
- **useDashboardStats.js**: Composable de estadísticas del dashboard
- **useFincas.js**: Composable de fincas
- **useLotes.js**: Composable de lotes
- **useNotifications.js**: Composable de notificaciones
- **usePagination.js**: Composable de paginación
- **usePrediction.js**: Composable de predicciones
- **useReports.js**: Composable de reportes
- **useWebSocket.js**: Composable de WebSocket
- Y muchos más...

### Utils

#### `frontend/src/utils/`
- **apiConfig.js**: Configuración de API
- **apiErrorHandler.js**: Manejador de errores
- **apiResponse.js**: Utilidades de respuesta API
- **formatters.js**: Formateadores
- **formDataUtils.js**: Utilidades de FormData
- **idGenerator.js**: Generador de IDs
- **imageValidationUtils.js**: Validación de imágenes
- **logger.js**: Logger
- **security.js**: Utilidades de seguridad
- Y más...

---

## 12. RELACIONES ENTRE CAPAS

### Flujo Principal

1. **Frontend (Vue.js)** → **API Services** → **Backend API Views** → **Services** → **Models** → **Database**

2. **Controladores → Servicios:**
   - `LoginView` → `LoginService`
   - `FincaListCreateView` → `FincaService`
   - `ScanMeasureView` → `AnalysisService` → `MLService` → `PredictionService`
   - `TrainingJobCreateView` → `MLService` → `train_model_task` (Celery)

3. **Servicios → Modelos:**
   - `FincaService` → `Finca`, `Lote`
   - `ImageManagementService` → `CacaoImage`, `CacaoPrediction`
   - `MLService` → `TrainingJob`, `ModelMetrics`
   - `ReportService` → `ReporteGenerado`

4. **Servicios ML → Componentes ML:**
   - `MLService` → `ml/prediction/predict.py`
   - `PredictionService` → `ml/regression/models.py`
   - `AnalysisService` → `ml/segmentation/cropper.py`

5. **Tareas Asíncronas:**
   - `train_model_task` → `ml/pipeline/train_all.py`
   - `image_tasks` → `ImageProcessingService`

6. **WebSockets:**
   - `consumers.py` → `realtime_service.py` → Frontend `useWebSocket.js`

---

## 13. DEPENDENCIAS CLAVE

### Backend
- Django → Django REST Framework → Services → Models
- Celery → Tasks → ML Pipeline
- Channels → WebSockets → Realtime Service
- PyTorch → ML Models → Prediction Service

### Frontend
- Vue.js → Pinia Stores → API Services → Backend
- Vue Router → Views → Components
- Axios → API Services

---

## 14. MÓDULOS GRANDES Y PROPUESTAS DE REORGANIZACIÓN

### Módulos que podrían reorganizarse:

1. **`api/views/`**: Muy grande, ya está parcialmente modularizado en subdirectorios (`ml/`, `admin/`, `notifications/`)

2. **`ml/regression/`**: Contiene muchos archivos de entrenamiento que podrían agruparse mejor:
   - `train.py`, `train_improved.py`, `hybrid_trainer.py`, `hybrid_training.py`, `hybrid_v2_training.py`
   - Propuesta: Agrupar en `ml/regression/training/`

3. **`frontend/src/components/`**: Muy grande, ya está bien organizado por dominio

4. **`api/services/`**: Bien organizado, pero `auth/` podría expandirse si crece más

---

## 15. OTROS COMPONENTES

### Signals
- `api/signals.py`: Signals de Django para eventos del sistema
- `users/signals.py`: Signals de usuarios

### Exceptions
- `api/exceptions.py`: Excepciones personalizadas de la API

### Factories (Testing)
- `backend/factories.py`: Factories para tests (Factory Boy)

### Tests
- Tests organizados en `*/tests/` en cada app
- Tests del frontend en `frontend/src/**/__tests__/`

---

## FIN DEL ANÁLISIS

Este documento proporciona una visión completa de la arquitectura del proyecto CacaoScan, organizada por capas y responsabilidades.

