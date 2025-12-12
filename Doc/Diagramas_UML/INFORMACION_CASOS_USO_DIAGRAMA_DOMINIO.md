# 📊 Información de Casos de Uso para Diagrama de Dominio - CacaoScan

Este documento contiene la información detallada de cada caso de uso necesaria para generar el diagrama de dominio, incluyendo entidades, relaciones, atributos y reglas de negocio.

---

## Caso de Uso 1: Registrar Usuario

### Entidades Principales
- **User** (Django User Model)
- **EmailVerificationToken**
- **ActivityLog** (Auditoría)

### Relaciones
- `User` → tiene uno → `EmailVerificationToken` (OneToOne, opcional)
- `User` → genera → `ActivityLog` (OneToMany)

### Atributos Clave
- **User**: username, email, password, first_name, last_name, is_active, date_joined
- **EmailVerificationToken**: token (UUID), user (FK), created_at, expires_at, is_verified

### Reglas de Negocio
- Email debe ser único en el sistema
- Username = Email (automático)
- Usuario creado con `is_active=False` hasta verificación de email
- Contraseña mínimo 8 caracteres, letras y números
- Se genera token de verificación automáticamente
- Se asignan tokens JWT (access y refresh) tras registro
- Rol "farmer" asignado automáticamente por signal (si no es admin/staff)

### Operaciones
- `RegistrationService.register_user_with_email_verification()`
- `EmailVerificationToken.create_for_user()`
- Validaciones: email único, fortaleza de contraseña, formato de email

---

## Caso de Uso 2: Iniciar Sesión

### Entidades Principales
- **User**
- **LoginHistory**
- **ActivityLog**

### Relaciones
- `User` → tiene múltiples → `LoginHistory` (OneToMany)
- `User` → genera → `ActivityLog` (OneToMany)

### Atributos Clave
- **User**: username, email, password, is_active
- **LoginHistory**: user (FK), login_time, ip_address, user_agent, success, failure_reason

### Reglas de Negocio
- Usuario debe estar activo (`is_active=True`)
- Email verificado (si se requiere verificación)
- Credenciales correctas (username/email + password)
- Se generan tokens JWT (access y refresh)
- Se registra login en `LoginHistory`
- Se crea log de auditoría
- Redirección según rol: admin → `/admin/dashboard`, analyst → `/analisis`, farmer → `/agricultor-dashboard`

### Operaciones
- `LoginService.login_user()`
- `authenticate()` (Django)
- `RefreshToken.for_user()` (JWT)

---

## Caso de Uso 3: Subir Imagen

### Entidades Principales
- **CacaoImage**
- **User**
- **Finca** (opcional)
- **Lote** (opcional)

### Relaciones
- `User` → sube múltiples → `CacaoImage` (OneToMany)
- `CacaoImage` → puede pertenecer a → `Finca` (ManyToOne, nullable)
- `CacaoImage` → puede pertenecer a → `Lote` (ManyToOne, nullable)

### Atributos Clave
- **CacaoImage**: 
  - `image` (ImageField), `user` (FK), `uploaded_at`, `processed` (Boolean)
  - `finca` (FK, nullable), `lote` (FK, nullable), `finca_nombre`, `region`, `variedad`
  - `file_name`, `file_size`, `file_type`, `notas`
  - `created_at`, `updated_at`

### Reglas de Negocio
- Usuario debe estar autenticado
- Formatos permitidos: jpeg, jpg, png, webp
- Tamaño máximo: 20MB por imagen
- Se puede subir múltiples imágenes en batch
- Subida puede ser síncrona o asíncrona (Celery para batch)
- Almacenamiento local o S3 (configurable)
- Se invalidan cachés de estadísticas tras subida
- Se crea log de auditoría por cada imagen

### Operaciones
- `ImageManagementService.upload_image()`
- `ImageStorageService.save_uploaded_image()`
- Validaciones: formato, tamaño, usuario autenticado

---

## Caso de Uso 4: Procesar Imagen

### Entidades Principales
- **CacaoImage**
- **Modelo ML** (U-Net o OpenCV)

### Relaciones
- `CacaoImage` → se procesa mediante → Modelo de Segmentación

### Atributos Clave
- **CacaoImage**: `processed` (Boolean), `processed_image_path` (opcional)

### Reglas de Negocio
- Imagen debe existir (`CacaoImage` creada)
- Imagen no procesada (`processed=False`)
- Backend preferido: U-Net (si disponible)
- Fallback: OpenCV si U-Net no disponible
- Se crea crop sin fondo de la imagen
- Crop guardado en `media/cacao_images/crops/`
- Se marca `processed=True` tras procesamiento exitoso
- Procesamiento puede fallar silenciosamente (imagen marcada como procesada sin crop)

### Operaciones
- `ImageProcessingService.process_image()`
- Segmentación U-Net o OpenCV
- Creación de crop

---

## Caso de Uso 5: Analizar Imagen

### Entidades Principales
- **CacaoImage**
- **CacaoPrediction**
- **User**
- **Modelo ML** (HybridCacaoRegression)

### Relaciones
- `CacaoImage` → genera una → `CacaoPrediction` (OneToOne)
- `User` → realiza múltiples → `CacaoPrediction` (OneToMany)
- Modelo ML → genera → `CacaoPrediction`

### Atributos Clave
- **CacaoPrediction**:
  - `image` (OneToOne FK), `user` (FK)
  - Predicciones: `alto_mm`, `ancho_mm`, `grosor_mm`, `peso_g`
  - Confianza: `confidence_alto`, `confidence_ancho`, `confidence_grosor`, `confidence_peso`
  - Metadatos: `model_version`, `device_used`, `processing_time_ms`, `crop_url`
  - Estado: `analysis_status` (pending, processing, completed, failed)
  - Calidad: `quality_score`, `maturity_percentage`, `defects_count`
  - `created_at`

### Reglas de Negocio
- Imagen debe existir y estar procesada (`processed=True`)
- Modelos ML deben estar cargados en memoria
- Se puede usar crop procesado o imagen original
- Preprocesamiento: redimensionamiento 224x224, normalización ImageNet
- Predicciones desnormalizadas con StandardScaler
- Se calcula confianza promedio (`average_confidence`)
- Se puede usar calibración de píxeles si existe `pixel_calibration.json`
- Predicción con baja confianza (<0.6) se marca como advertencia

### Operaciones
- `AnalysisService.process_image_with_segmentation()`
- `PredictionService.predict()`
- Carga de modelos ML, preprocesamiento, predicción, guardado de resultados

---

## Caso de Uso 6: Ver Resultados

### Entidades Principales
- **CacaoImage**
- **CacaoPrediction**
- **User**

### Relaciones
- `CacaoImage` → tiene una → `CacaoPrediction` (OneToOne)
- `User` → puede ver → `CacaoPrediction` (si es propietario o admin)

### Atributos Clave
- **CacaoPrediction**: Todas las predicciones y metadatos (ver CU5)
- **CacaoImage**: Imagen original y crop procesado

### Reglas de Negocio
- Usuario debe estar autenticado
- Usuario solo ve sus propias predicciones (excepto admin que ve todas)
- Si no hay predicción, se muestra mensaje "Imagen pendiente de análisis"
- Resultados incluyen: dimensiones (mm), peso (g), confianza, tiempo de procesamiento, fecha

### Operaciones
- `ImageDetailView.get()` - Obtener detalle de imagen con predicción
- `ImagesListView.get()` - Listar imágenes con filtros

---

## Caso de Uso 7: Descargar Reporte

### Entidades Principales
- **ReporteGenerado**
- **User**
- **CacaoPrediction** (fuente de datos)
- **Finca** (fuente de datos)
- **Lote** (fuente de datos)

### Relaciones
- `User` → genera múltiples → `ReporteGenerado` (OneToMany)
- `ReporteGenerado` → puede incluir → `CacaoPrediction`, `Finca`, `Lote` (datos de consulta)

### Atributos Clave
- **ReporteGenerado**:
  - `user` (FK), `tipo_reporte` (calidad, finca, lote, auditoria)
  - `formato` (pdf, excel, csv, json)
  - `estado` (pendiente, generando, completado, fallido, expirado)
  - `archivo` (FileField), `fecha_generacion`, `fecha_expiracion`
  - `parametros` (JSON con filtros aplicados)

### Reglas de Negocio
- Usuario debe estar autenticado
- Tipos de reporte: calidad, finca, lote, auditoría, personalizado
- Formatos: PDF, Excel, CSV, JSON
- Generación puede ser síncrona (reportes pequeños) o asíncrona (Celery, reportes grandes)
- Reportes tienen fecha de expiración (configurable)
- Usuario solo descarga sus propios reportes (excepto admin)
- Reporte debe estar en estado "completado" para descarga

### Operaciones
- `ReportGenerationService.generate_report()`
- `ExcelAnalisisGenerator.generate_quality_report()`
- `ReporteDownloadView.get()` - Descargar archivo

---

## Caso de Uso 8: Crear Finca

### Entidades Principales
- **Finca**
- **User** (Agricultor)

### Relaciones
- `User` (agricultor) → tiene múltiples → `Finca` (OneToMany)
- `Finca` → pertenece a → `User` (agricultor) (ManyToOne)

### Atributos Clave
- **Finca**:
  - `nombre`, `ubicacion`, `municipio`, `departamento`, `hectareas` (Decimal)
  - `agricultor` (FK a User)
  - Opcionales: `descripcion`, `coordenadas_lat`, `coordenadas_lng`, `tipo_suelo`, `clima`, `altitud`, `precipitacion_anual`, `temperatura_promedio`
  - `activa` (Boolean, default=True)
  - `created_at`, `updated_at`

### Reglas de Negocio
- Usuario debe estar autenticado (agricultor o admin)
- Campos obligatorios: nombre, ubicacion, municipio, departamento, hectareas
- Hectáreas debe ser > 0
- Si es admin, puede crear finca para otro agricultor (proporcionando `agricultor_id`)
- No hay validación de unicidad de nombre (se permite mismo nombre para diferentes agricultores)
- Se crea log de auditoría
- Se invalidan cachés de estadísticas

### Operaciones
- `FincaCRUDService.create_finca()`
- Validaciones: campos requeridos, hectareas > 0, agricultor existe

---

## Caso de Uso 9: Editar Finca

### Entidades Principales
- **Finca**
- **User** (Agricultor propietario o Admin)

### Relaciones
- Mismas que CU8

### Atributos Clave
- Mismos que CU8 (actualización parcial permitida)

### Reglas de Negocio
- Usuario debe ser propietario de la finca o admin
- Actualización parcial (PATCH) permitida
- Si se modifica `hectareas`, debe ser > 0
- Admin puede cambiar `agricultor_id` (cambio de propietario)
- Se registra modificación en auditoría
- Se invalidan cachés relacionadas

### Operaciones
- `FincaCRUDService.update_finca()`
- Validaciones: permisos, hectareas > 0 (si se modifica)

---

## Caso de Uso 10: Crear Lote

### Entidades Principales
- **Lote**
- **Finca**
- **User** (Agricultor propietario de finca)

### Relaciones
- `Finca` → contiene múltiples → `Lote` (OneToMany)
- `Lote` → pertenece a → `Finca` (ManyToOne)
- `User` (agricultor) → indirectamente tiene → `Lote` (a través de Finca)

### Atributos Clave
- **Lote**:
  - `finca` (FK), `identificador`, `nombre`, `variedad`
  - `fecha_plantacion`, `fecha_cosecha` (nullable)
  - `area_hectareas` (Decimal)
  - `estado` (activo, inactivo, cosechado, renovado)
  - Opcionales: `descripcion`, `coordenadas_lat`, `coordenadas_lng`, `edad_plantas`
  - `created_at`, `updated_at`

### Reglas de Negocio
- Usuario debe ser propietario de la finca o admin
- Campos obligatorios: finca, identificador, variedad, fecha_plantacion, area_hectareas
- Área debe ser > 0
- Fecha de plantación debe ser <= fecha de cosecha (si ambas proporcionadas)
- Identificador puede generarse automáticamente si no se proporciona
- Validación opcional: área total de lotes no exceda área de finca
- Se crea log de auditoría

### Operaciones
- `LoteService.create_lote()`
- Validaciones: finca existe, permisos, área > 0, fechas coherentes

---

## Caso de Uso 11: Editar Lote

### Entidades Principales
- **Lote**
- **Finca**
- **User**

### Relaciones
- Mismas que CU10

### Atributos Clave
- Mismos que CU10 (actualización parcial permitida)

### Reglas de Negocio
- Usuario debe ser propietario de la finca del lote o admin
- Actualización parcial (PATCH) permitida
- Si se modifica `area_hectareas`, debe ser > 0
- Si se modifican fechas, deben ser coherentes (plantación <= cosecha)
- Admin puede cambiar `finca_id` (cambio de finca)
- Se registra modificación en auditoría

### Operaciones
- `LoteService.update_lote()`
- Validaciones: permisos, área > 0 (si se modifica), fechas coherentes

---

## Caso de Uso 12: Eliminar Lote

### Entidades Principales
- **Lote**
- **CacaoImage** (verificación de dependencias)
- **User**

### Relaciones
- `Lote` → puede tener múltiples → `CacaoImage` (OneToMany)
- Eliminación: `Lote` → se elimina si no tiene → `CacaoImage`

### Atributos Clave
- Mismos que CU10

### Reglas de Negocio
- Usuario debe ser propietario de la finca del lote o admin
- NO se puede eliminar si tiene imágenes asociadas (`CacaoImage` con `lote_id`)
- Se verifica dependencias antes de eliminar
- Se crea log de auditoría antes de eliminar
- Si tiene imágenes, se retorna error 400 con mensaje descriptivo

### Operaciones
- `LoteService.delete_lote()`
- Validaciones: permisos, sin dependencias (`not lote.cacao_images.exists()`)

---

## Caso de Uso 13: Ver Historial

### Entidades Principales
- **CacaoPrediction**
- **CacaoImage**
- **User**
- **Finca** (filtro opcional)
- **Lote** (filtro opcional)

### Relaciones
- `User` → tiene múltiples → `CacaoPrediction` (OneToMany, a través de CacaoImage)
- `CacaoPrediction` → pertenece a → `CacaoImage` (OneToOne)
- `CacaoImage` → puede pertenecer a → `Finca`, `Lote`

### Atributos Clave
- **CacaoPrediction**: Todas las predicciones y metadatos
- **CacaoImage**: Imagen asociada
- Filtros: fecha desde/hasta, confianza mínima/máxima, finca, lote

### Reglas de Negocio
- Usuario debe estar autenticado
- Usuario solo ve sus propios análisis (excepto admin que ve todos)
- Ordenamiento por fecha descendente (más recientes primero)
- Paginación por defecto (20 por página)
- Filtros opcionales: fechas, confianza, finca, lote
- Sin resultados: mostrar mensaje "Sin análisis"

### Operaciones
- `AnalysisService.get_analysis_history()`
- `ImagesListView.get()` con filtros y paginación

---

## Caso de Uso 14: Buscar Análisis

### Entidades Principales
- **CacaoPrediction**
- **CacaoImage**
- **User**
- **Finca**, **Lote** (criterios de búsqueda)

### Relaciones
- Mismas que CU13

### Atributos Clave
- Mismos que CU13
- Criterios de búsqueda: fechas, lote, finca, rango de peso, dimensiones, variedad, confianza

### Reglas de Negocio
- Usuario debe estar autenticado
- Filtros múltiples combinables:
  - Fechas: `date_from`, `date_to` (date_from <= date_to)
  - Confianza: `min_confidence`, `max_confidence`
  - Finca/Lote: por ID
  - Rango de peso: `min_peso_g`, `max_peso_g`
  - Dimensiones: `min_alto_mm`, `max_alto_mm`, etc.
  - Variedad: búsqueda por texto
- Búsqueda por texto en notas, metadatos, nombre de finca
- Resultados paginados
- Validación de criterios (fechas coherentes, rangos válidos)

### Operaciones
- `AnalysisService.get_analysis_history()` con filtros
- `AdminImagesListView._apply_filters()` - Aplicar múltiples filtros
- Búsqueda con `Q` objects (Django ORM)

---

## Caso de Uso 15: Entrenar Modelo

### Entidades Principales
- **TrainingJob**
- **User** (Admin/Técnico)
- **CacaoImage** (dataset para entrenamiento)
- **CacaoPrediction** (targets para entrenamiento)
- **Modelo ML** (PyTorch, YOLOv8)

### Relaciones
- `User` → puede iniciar múltiples → `TrainingJob` (OneToMany)
- `TrainingJob` → usa → `CacaoImage`, `CacaoPrediction` (datos de entrenamiento)
- `TrainingJob` → genera → Modelo ML entrenado

### Atributos Clave
- **TrainingJob**:
  - `job_id` (UUID), `user` (FK), `status` (pending, running, completed, failed)
  - `config` (JSON con parámetros: epochs, batch_size, learning_rate, model_type)
  - `progress` (0-100), `message` (estado actual)
  - `started_at`, `completed_at`, `error_message`
  - `metrics` (JSON con métricas de entrenamiento)
  - `model_path` (ruta al modelo guardado)

### Reglas de Negocio
- Solo usuarios admin o técnicos pueden iniciar entrenamiento
- Dataset debe estar disponible (`dataset_cacao.clean.csv`)
- Parámetros válidos: epochs > 0, batch_size > 0, learning_rate > 0
- Entrenamiento puede ser síncrono o asíncrono (Celery)
- Pipeline: carga datos → normaliza targets → crea splits → entrena → evalúa → guarda modelo
- Se guardan checkpoints durante entrenamiento
- Early stopping configurable
- Modelos guardados en `ml/artifacts/regressors/` o `ml/segmentation/`

### Operaciones
- `CacaoTrainingPipeline.run_full_training_pipeline()`
- `train_model_task()` (Celery task)
- Validaciones: permisos, dataset disponible, parámetros válidos

---

## Caso de Uso 16: Crear Agricultor

### Entidades Principales
- **User**
- **Persona** (opcional, información extendida)
- **UserProfile** (opcional)
- **TipoDocumento**, **Genero**, **Departamento**, **Municipio** (catálogos)

### Relaciones
- `User` → tiene una → `Persona` (OneToOne, opcional)
- `User` → tiene una → `UserProfile` (OneToOne, opcional)
- `Persona` → referencia → `TipoDocumento`, `Genero`, `Departamento`, `Municipio` (catálogos)

### Atributos Clave
- **User**: username, email, password, first_name, last_name, is_active
- **Persona** (si se crea):
  - `primer_nombre`, `segundo_nombre`, `primer_apellido`, `segundo_apellido`
  - `tipo_documento` (FK), `numero_documento`, `genero` (FK)
  - `fecha_nacimiento`, `telefono`, `direccion`
  - `departamento` (FK), `municipio` (FK)

### Reglas de Negocio
- Solo admin puede crear agricultores
- Si es admin, usuario creado con `is_active=True` (sin verificación de email)
- Campos obligatorios básicos: email, password, first_name, last_name
- Email debe ser único
- Persona opcional pero recomendada para información completa
- Se pueden crear fincas para el agricultor durante el registro
- Se asigna rol "farmer" automáticamente (si no es admin/staff)

### Operaciones
- `PersonaRegistroView.post()` (para admin, crea sin verificación)
- `RegistrationService.register_user()` (flujo normal)
- Validaciones: email único, datos válidos, catálogos válidos

---

## Caso de Uso 17: Editar Agricultor

### Entidades Principales
- **User**
- **Persona**
- **UserProfile**
- **Finca** (asociadas al agricultor)

### Relaciones
- Mismas que CU16
- `User` → puede tener múltiples → `Finca`

### Atributos Clave
- Mismos que CU16 (actualización parcial permitida)

### Reglas de Negocio
- Solo admin puede editar agricultores
- Actualización parcial (PATCH) permitida
- Campos permitidos: first_name, last_name, is_active, groups
- Email no se puede cambiar desde aquí (requiere proceso separado)
- Admin no puede desactivarse a sí mismo
- Se puede actualizar información de Persona simultáneamente
- Se registra modificación en auditoría

### Operaciones
- `UserUpdateView.patch()`
- `PersonaPerfilView.patch()` (para datos de Persona)
- Validaciones: permisos, no auto-desactivación

---

## Caso de Uso 18: Asignar Rol

### Entidades Principales
- **User**
- **Group** (Django Groups: admin, analyst, farmer)

### Relaciones
- `User` → pertenece a múltiples → `Group` (ManyToMany)
- `Group` → tiene múltiples → `User` (ManyToMany)

### Atributos Clave
- **User**: `groups` (ManyToMany)
- **Group**: `name` (admin, analyst, farmer), `permissions`

### Reglas de Negocio
- Solo admin puede asignar roles
- Roles disponibles: admin, analyst, farmer
- No se puede remover el último admin del sistema
- Cambio de rol invalida sesiones activas del usuario
- Se registra cambio de rol en auditoría
- Roles determinan permisos:
  - **admin**: Acceso completo, gestionar usuarios, entrenar modelos
  - **analyst**: Analizar imágenes, gestionar lotes, ver estadísticas
  - **farmer**: Gestionar fincas/lotes propios, subir imágenes, ver propios análisis

### Operaciones
- `UserUpdateView._update_user_groups()`
- Validaciones: permisos, no remover último admin
- Asignación/remoción de grupos Django

---

## Caso de Uso 19: Editar Perfil

### Entidades Principales
- **User**
- **UserProfile**
- **Persona** (opcional)

### Relaciones
- `User` → tiene una → `UserProfile` (OneToOne)
- `User` → tiene una → `Persona` (OneToOne, opcional)

### Atributos Clave
- **User**: first_name, last_name, email (si se permite cambio)
- **UserProfile**:
  - `phone_number`, `region`, `municipality`
  - `farm_name`, `years_experience`, `farm_size_hectares`
  - `preferred_language`, `email_notifications`
- **Persona**: Todos los campos de información personal (si existe)

### Reglas de Negocio
- Usuario solo puede editar su propio perfil (o admin puede editar cualquier perfil)
- Campos permitidos User: first_name, last_name
- Email puede cambiar pero requiere verificación (proceso separado)
- Campos permitidos UserProfile: phone_number, region, municipality, preferencias
- Actualización parcial (PATCH) permitida
- Se valida email único si se cambia email
- Se puede actualizar Persona simultáneamente
- Se registra modificación en auditoría

### Operaciones
- `ProfileService.update_user_profile()`
- `PersonaPerfilView.patch()` (para datos de Persona)
- Validaciones: permisos, email único (si se cambia)

---

## Resumen de Entidades del Dominio

### Entidades Principales
1. **User** - Usuarios del sistema (agricultores, técnicos, admins)
2. **CacaoImage** - Imágenes de granos de cacao subidas
3. **CacaoPrediction** - Resultados de análisis ML de imágenes
4. **Finca** - Fincas de cacao de los agricultores
5. **Lote** - Lotes dentro de fincas
6. **ReporteGenerado** - Reportes generados por usuarios
7. **TrainingJob** - Trabajos de entrenamiento de modelos ML
8. **Persona** - Información extendida de usuarios (opcional)
9. **UserProfile** - Perfil extendido de usuario
10. **EmailVerificationToken** - Tokens de verificación de email
11. **LoginHistory** - Historial de inicios de sesión
12. **ActivityLog** - Logs de auditoría

### Entidades de Soporte (Catálogos)
- **TipoDocumento**, **Genero**, **Departamento**, **Municipio**
- **Group** (Django Groups para roles)

### Relaciones Principales del Dominio
- User → CacaoImage (1:N)
- CacaoImage → CacaoPrediction (1:1)
- User → Finca (1:N)
- Finca → Lote (1:N)
- Lote → CacaoImage (1:N)
- User → ReporteGenerado (1:N)
- User → TrainingJob (1:N)
- User → UserProfile (1:1)
- User → Persona (1:1, opcional)
- User → Group (N:M)
- User → LoginHistory (1:N)
- User → ActivityLog (1:N)

---

## Notas para el Diagrama de Dominio

### Agregados
- **Agregado Usuario**: User, UserProfile, Persona, EmailVerificationToken
- **Agregado Imagen**: CacaoImage, CacaoPrediction
- **Agregado Finca**: Finca, Lote
- **Agregado Reporte**: ReporteGenerado
- **Agregado Entrenamiento**: TrainingJob

### Value Objects
- Dimensiones (alto_mm, ancho_mm, grosor_mm)
- Peso (peso_g)
- Confianza (confidence_*)
- Coordenadas (coordenadas_lat, coordenadas_lng)
- Fechas (fecha_plantacion, fecha_cosecha)

### Servicios de Dominio
- RegistrationService
- LoginService
- ImageManagementService
- ImageProcessingService
- AnalysisService
- PredictionService
- FincaCRUDService
- LoteService
- ReportGenerationService
- ProfileService
- CacaoTrainingPipeline

### Eventos de Dominio (implícitos)
- UsuarioRegistrado
- ImagenSubida
- ImagenProcesada
- AnalisisCompletado
- FincaCreada
- LoteEliminado
- RolAsignado
- PerfilActualizado

---

**Última actualización**: Generado a partir de análisis del código base de CacaoScan
