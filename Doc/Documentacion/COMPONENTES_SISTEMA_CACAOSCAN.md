# Componentes del Sistema CacaoScan

## Resumen Ejecutivo

Este documento identifica todos los componentes del sistema CacaoScan, clasificados por capas arquitectónicas. Los componentes se definen como módulos, servicios, entidades, adaptadores, controladores y repositorios, excluyendo funciones, métodos, endpoints y flujos de proceso.

---

## Frontend (Vue.js)

### Componentes de Interfaz

- **PresentationLayer** (Módulo Vue): Capa de presentación con todos los componentes de interfaz de usuario (autenticación, dashboard, análisis, fincas, reportes, administración).

### Gestión de Estado

- **StateManagementLayer** (Store Pinia): Capa de gestión de estado global que agrupa todos los stores (autenticación, análisis, fincas, reportes, notificaciones, configuración).

### Comunicación con Backend

- **APIClientLayer** (Servicio HTTP): Capa de comunicación HTTP que agrupa cliente API, servicios de endpoints y manejo de errores.

### Lógica Reutilizable

- **ComposablesLayer** (Composable): Capa de composables que agrupa toda la lógica reutilizable (autenticación, análisis, predicciones, formularios, paginación).

### Navegación

- **RoutingLayer** (Módulo Router): Módulo de enrutamiento y protección de rutas.

### Utilidades

- **UtilitiesLayer** (Utilidad): Capa de utilidades que agrupa formateo, validación, exportación y seguridad.

---

## Backend (Django REST Framework)

### Capa de Aplicación

- **ApplicationLayer** (App Django): Capa que agrupa todas las apps Django (API, autenticación, fincas, imágenes, reportes, entrenamiento, notificaciones, auditoría, catálogos, personas, core, legal).

### Capa de Servicios

- **AuthService** (Servicio): Servicio de autenticación que agrupa login, registro, verificación y gestión de perfiles.
- **ImageService** (Servicio): Servicio de imágenes que agrupa gestión, procesamiento y almacenamiento de imágenes.
- **FincaService** (Servicio): Servicio de fincas que agrupa CRUD, validación, estadísticas y gestión de lotes.
- **ReportService** (Servicio): Servicio de reportes que agrupa generación en Excel/PDF, gestión y estadísticas.
- **MLService** (Servicio): Servicio de machine learning que agrupa predicción y entrenamiento.
- **EmailService** (Servicio): Servicio de envío de emails transaccionales.
- **AnalysisService** (Servicio): Servicio de análisis de datos e imágenes.
- **StatsService** (Servicio): Servicio de cálculo de estadísticas del sistema.
- **RealtimeService** (Servicio): Servicio de notificaciones en tiempo real vía WebSockets.

### Capa de Serialización

- **SerializationLayer** (Serializer): Capa que agrupa todos los serializadores (autenticación, imágenes, fincas, ML, comunes).

### Capa de Controladores

- **ControllerLayer** (Controlador): Capa que agrupa todos los controladores/views (autenticación, imágenes, fincas, reportes, entrenamiento, administración, notificaciones, ML, calibración, métricas).

### Capa de Middleware

- **MiddlewareLayer** (Middleware): Capa que agrupa middleware de manejo de errores y tiempo real.

### Capa de Tareas Asíncronas

- **TaskLayer** (Tarea Celery): Capa que agrupa todas las tareas asíncronas (imágenes, ML, entrenamiento, estadísticas, limpieza).

### Capa de Utilidades

- **UtilitiesLayer** (Utilidad): Capa que agrupa utilidades core (caché, validadores, respuestas, seguridad).

---

## Módulo ML / Entrenamiento

### Segmentación

- **SegmentationComponent** (Módulo): Componente de segmentación que agrupa procesamiento, extracción de crops y modelos (YOLO, U-Net).

### Regresión

- **RegressionComponent** (Módulo): Componente de regresión que agrupa modelos, entrenadores, métricas, escalado y data augmentation.

### Predicción

- **PredictionComponent** (Módulo): Componente de predicción que agrupa predicción estándar y calibrada.

### Gestión de Datos

- **DataComponent** (Módulo): Componente de datos que agrupa datasets, carga, transformaciones y extracción de características.

### Pipeline de Entrenamiento

- **TrainingPipelineComponent** (Módulo): Componente de pipeline que agrupa pipelines de entrenamiento (híbrido, unificado).

### Medición

- **MeasurementComponent** (Módulo): Componente de medición que agrupa calibración de píxeles y medición de dimensiones.

### Utilidades ML

- **MLUtilitiesComponent** (Utilidad): Componente que agrupa utilidades ML (early stopping, I/O, logging, pérdidas, métricas, rutas).

---

## Base de Datos / Modelos

### Entidades de Dominio

- **AuthEntities** (Entidad): Entidades de autenticación (Usuario, Perfil, Tokens de verificación).
- **FincaEntities** (Entidad): Entidades de fincas (Finca, Lote).
- **ImageEntities** (Entidad): Entidades de imágenes (Imagen de Cacao, Predicción).
- **PersonEntities** (Entidad): Entidades de personas.
- **CatalogEntities** (Entidad): Entidades de catálogos de referencia.
- **NotificationEntities** (Entidad): Entidades de notificaciones.
- **AuditEntities** (Entidad): Entidades de auditoría (Logs de actividad, Historial de login).
- **TrainingEntities** (Entidad): Entidades de entrenamiento (Trabajos de entrenamiento, Métricas de modelos).
- **ReportEntities** (Entidad): Entidades de reportes generados.
- **CoreEntities** (Entidad): Entidades core (Configuración del sistema, Modelo base con timestamps).

---

## Servicios / Integraciones / Worker

### Tareas Asíncronas

- **CeleryWorker** (Worker): Worker de tareas asíncronas con programador de tareas periódicas.

### Comunicación en Tiempo Real

- **WebSocketComponent** (Adaptador): Componente de WebSockets que agrupa adaptador Django Channels y consumidores.

### Servicios Externos

- **EmailAdapter** (Adaptador): Adaptador de servicio de email (SendGrid).
- **StorageAdapter** (Adaptador): Adaptador de almacenamiento que agrupa almacenamiento local y S3.
- **CacheAdapter** (Adaptador): Adaptador de caché (Redis).
- **DatabaseAdapter** (Adaptador): Adaptador de base de datos (PostgreSQL).

---

## Componentes recomendados para el Diagrama de Componentes UML

### Bloques Principales

1. **Frontend Layer**
   - **FrontendApplication** (Componente principal Vue.js): Agrupa toda la capa de presentación, estado, comunicación API y utilidades.

2. **Backend API Layer**
   - **RESTAPIGateway** (Django REST Framework): Punto de entrada de la API REST.
   - **BusinessLogicLayer** (Servicios): Agrupa todos los servicios de negocio (autenticación, imágenes, fincas, reportes, ML).
   - **DataAccessLayer** (ORM): Agrupa acceso a datos y entidades de dominio.

3. **ML/IA Layer**
   - **MLComponent** (Módulo ML): Agrupa segmentación, regresión, predicción, datos, pipeline y utilidades ML.

4. **Data Layer**
   - **DatabaseComponent** (PostgreSQL): Base de datos relacional.
   - **FileStorageComponent**: Almacenamiento de archivos.
   - **CacheComponent** (Redis): Sistema de caché.

5. **Integration Layer**
   - **AsyncTaskComponent** (Celery): Worker de tareas asíncronas.
   - **RealtimeComponent** (WebSockets): Comunicación en tiempo real.
   - **ExternalServicesComponent**: Servicios externos (email, storage, cache).

### Conexiones Principales

- FrontendApplication → RESTAPIGateway (HTTP)
- FrontendApplication → RealtimeComponent (WebSocket)
- RESTAPIGateway → BusinessLogicLayer
- BusinessLogicLayer → DataAccessLayer
- BusinessLogicLayer → MLComponent
- BusinessLogicLayer → AsyncTaskComponent
- DataAccessLayer → DatabaseComponent
- BusinessLogicLayer → FileStorageComponent
- BusinessLogicLayer → CacheComponent
- AsyncTaskComponent → MLComponent
- AsyncTaskComponent → ExternalServicesComponent
- RealtimeComponent → ExternalServicesComponent

---

## Notas Finales

- Todos los componentes están identificados a nivel de módulo/servicio/entidad.
- No se incluyen funciones, métodos ni flujos de proceso.
- La clasificación sigue una arquitectura por capas clara.
- Los componentes están listos para ser representados en un Diagrama de Componentes UML.

