# FAQ Técnico - Sistema CacaoScan Completo
## Guía de Respuestas para Ingenieros (Sistema General)

Este documento contiene las preguntas técnicas más comunes sobre el sistema completo de CacaoScan, incluyendo arquitectura, backend, frontend, base de datos, seguridad, deployment y más.

---

## 🏗️ ARQUITECTURA GENERAL

### Q1: ¿Cuál es la arquitectura general del sistema?

**Respuesta:**
**Arquitectura de 3 capas separadas**:

1. **Frontend (Vue.js 3)**:
   - SPA (Single Page Application)
   - Framework: Vue.js 3 + Vite
   - Estado: Pinia (gestión de estado global)
   - UI: TailwindCSS + Flowbite
   - HTTP Client: Axios
   - WebSockets: Conexión en tiempo real

2. **Backend (Django REST Framework)**:
   - API REST: Django REST Framework
   - ORM: Django ORM (PostgreSQL)
   - Autenticación: JWT (JSON Web Tokens)
   - Tareas asíncronas: Celery + Redis
   - WebSockets: Django Channels
   - Servicios: Arquitectura por servicios (Services Layer)

3. **Base de Datos (PostgreSQL 15)**:
   - Base de datos relacional
   - Normalización 3FN
   - Foreign keys y constraints
   - Índices optimizados

4. **ML/IA (PyTorch)**:
   - Módulo separado: `backend/ml/`
   - Modelos: ResNet18, ConvNeXt, U-Net, YOLOv8
   - Predicción: Servicio dedicado

**Patrón de comunicación**: REST API (HTTP/JSON) + WebSockets (tiempo real)

---

### Q2: ¿Por qué eligieron Django + Vue.js en lugar de otras tecnologías?

**Respuesta:**

**Django (Backend)**:
- **Framework maduro**: Más de 15 años de desarrollo
- **ORM potente**: Django ORM facilita queries complejas
- **Admin panel**: Panel administrativo incorporado
- **Seguridad**: Protecciones incorporadas (CSRF, XSS, SQL injection)
- **Ecosistema**: Muchas librerías y paquetes disponibles
- **ML Integration**: Python es ideal para integración con PyTorch
- **Comunidad**: Gran comunidad y documentación

**Vue.js (Frontend)**:
- **Progresivo**: Se puede adoptar gradualmente
- **Rendimiento**: Más ligero que React/Angular
- **Curva de aprendizaje**: Más fácil que React/Angular
- **Composition API**: Mejor para proyectos grandes
- **Ecosistema**: Vue Router, Pinia, Vite bien integrados
- **DX (Developer Experience)**: Excelente tooling

**Alternativas consideradas**:
- **Backend**: FastAPI (muy nuevo), Flask (demasiado minimalista)
- **Frontend**: React (más complejo), Angular (muy pesado)

---

### Q3: ¿Cómo está estructurado el código del backend?

**Respuesta:**
**Arquitectura modular por dominio (Django Apps)**:

```
backend/
├── api/                    # API principal (endpoints, serializers, views)
│   ├── views/             # Views organizadas por dominio
│   ├── services/          # Lógica de negocio
│   ├── serializers/       # Serialización de datos
│   └── tasks/             # Tareas Celery
├── auth_app/              # Autenticación y autorización
├── fincas_app/            # Gestión de fincas y lotes
├── images_app/            # Gestión de imágenes
├── reports/               # Generación de reportes
├── training/              # Entrenamiento ML
├── notifications/         # Sistema de notificaciones
├── audit/                 # Auditoría y logs
├── personas/              # Información de personas
├── catalogos/             # Catálogos (departamentos, municipios)
├── core/                  # Funcionalidades core compartidas
├── ml/                    # Módulo ML completo
└── legal/                 # Términos y condiciones
```

**Principios aplicados**:
- **Separación por dominio**: Cada app tiene responsabilidad única
- **Services Layer**: Lógica de negocio en servicios
- **DRY**: Funcionalidades compartidas en `core/`
- **SOLID**: Principios SOLID aplicados

---

## 🔐 AUTENTICACIÓN Y AUTORIZACIÓN

### Q4: ¿Cómo funciona la autenticación con JWT?

**Respuesta:**
**Flujo de autenticación JWT**:

1. **Login**:
   - Usuario envía credenciales: `POST /api/v1/auth/login/`
   - Backend valida credenciales
   - Genera dos tokens:
     - **Access Token**: Válido 1 hora (para autenticación)
     - **Refresh Token**: Válido 7 días (para renovar access token)

2. **Uso de tokens**:
   - Cliente incluye token en header: `Authorization: Bearer <access_token>`
   - Backend valida token en cada request
   - Si expira, usar refresh token para obtener nuevo access token

3. **Refresh Token**:
   - Endpoint: `POST /api/v1/auth/refresh/`
   - Rotación automática: Refresh token se rota en cada uso
   - Blacklist: Tokens antiguos se invalidan

**Configuración**:
- Algoritmo: HS256 (HMAC-SHA256)
- Payload: User ID, username, roles, exp, iat
- Secret key: Almacenado en variables de entorno
- Rotación: Activada para mayor seguridad

**Ventajas**:
- Stateless: No requiere sesión en servidor
- Escalable: Funciona con múltiples instancias
- Seguro: Tokens firmados, expiración corta

---

### Q5: ¿Qué roles y permisos tiene el sistema?

**Respuesta:**
**Roles implementados**:

1. **Admin (Administrador)**:
   - Acceso total al sistema
   - Gestión de usuarios
   - Configuración del sistema
   - Entrenamiento de modelos ML
   - Acceso a todas las fincas e imágenes
   - Generación de reportes administrativos

2. **Agricultor (Farmer)**:
   - Gestión de sus propias fincas y lotes
   - Subir y analizar imágenes de sus granos
   - Ver sus propias predicciones y reportes
   - No puede gestionar otros usuarios

3. **Técnico (Technician)**:
   - Acceso a múltiples fincas (asignadas)
   - Analizar imágenes de granos
   - Ver reportes de fincas asignadas
   - No puede gestionar usuarios

**Implementación**:
- Basado en grupos de Django
- Permisos: `IsAuthenticated`, `IsAdminUser`, permisos custom
- Ownership validation: Usuarios solo acceden a sus recursos
- Middleware: Validación de permisos en cada request

---

### Q6: ¿Cómo protegen contra ataques comunes (SQL injection, XSS, CSRF)?

**Respuesta:**
**Protecciones implementadas**:

1. **SQL Injection**:
   - Django ORM: Todos los queries usan ORM (parametrizados)
   - No se usan queries raw sin sanitización
   - Validación de inputs en serializers

2. **XSS (Cross-Site Scripting)**:
   - Django auto-escapes templates (si se usaran)
   - Frontend: Vue.js auto-escapa contenido
   - Content Security Policy (CSP) headers
   - Validación de inputs en backend

3. **CSRF (Cross-Site Request Forgery)**:
   - Django CSRF middleware activado
   - Tokens CSRF en formularios
   - Excepciones solo donde es necesario (API REST)

4. **Otras protecciones**:
   - **Rate Limiting**: Protección contra fuerza bruta
   - **CORS**: Configurado estrictamente
   - **Password Policy**: Contraseñas robustas (mínimo 8 caracteres)
   - **HTTPS**: Forzado en producción
   - **Secrets Management**: Variables de entorno (no en código)

---

## 💾 BASE DE DATOS

### Q7: ¿Por qué PostgreSQL en lugar de MySQL o SQLite?

**Respuesta:**
**PostgreSQL elegido por**:

1. **Características avanzadas**:
   - JSON/JSONB: Soporte nativo para JSON
   - Full-text search: Búsqueda de texto completo
   - Arrays: Tipos de array nativos
   - Extensions: PostGIS, pg_trgm, etc.

2. **Rendimiento**:
   - Mejor optimizador de queries que MySQL
   - Mejor manejo de concurrencia
   - Índices avanzados (GIN, GiST, BRIN)

3. **Confiabilidad**:
   - ACID compliance estricto
   - Mejor integridad de datos
   - Transacciones más robustas

4. **Escalabilidad**:
   - Mejor para proyectos que crecerán
   - Replicación y sharding avanzados
   - Mejor soporte para cargas pesadas

5. **Django compatibility**:
   - Excelente soporte en Django ORM
   - Migraciones robustas
   - Tipos de datos específicos

**SQLite**: Solo para desarrollo local, no producción
**MySQL**: Menos features avanzadas, optimizador menos sofisticado

---

### Q8: ¿Cómo manejan las migraciones de base de datos?

**Respuesta:**
**Proceso de migraciones**:

1. **Crear migraciones**:
   ```bash
   python manage.py makemigrations
   ```
   - Analiza cambios en modelos
   - Genera archivos de migración
   - Incluye operaciones SQL

2. **Aplicar migraciones**:
   ```bash
   python manage.py migrate
   ```
   - Ejecuta migraciones pendientes
   - Mantiene historial en tabla `django_migrations`
   - Transaccional (rollback si falla)

3. **Migraciones de datos**:
   - Separadas de migraciones de esquema
   - Comandos custom: `python manage.py init_catalogos`
   - Datos iniciales: Fixtures o seeders

4. **Estrategia**:
   - Migraciones incrementales
   - Compatibilidad hacia atrás cuando es posible
   - Migraciones reversibles
   - Testing de migraciones en staging

**Versionado**:
- Migraciones en control de versiones (Git)
- Numeración automática: `0001_initial.py`, `0002_add_field.py`
- Sin conflictos: Django detecta y previene

---

## 🌐 FRONTEND (VUE.JS)

### Q9: ¿Por qué Vue.js 3 con Composition API en lugar de Options API?

**Respuesta:**
**Composition API elegida por**:

1. **Organización de código**:
   - Agrupa lógica relacionada (vs. separada por tipo)
   - Mejor para componentes grandes
   - Reutilización con composables

2. **TypeScript readiness**:
   - Mejor soporte para TypeScript
   - Type inference mejorado
   - Mejor para proyectos grandes

3. **Performance**:
   - Mejor tree-shaking
   - Menos overhead
   - Más optimizable

4. **Mantenibilidad**:
   - Código más fácil de seguir
   - Lógica relacionada junta
   - Mejor testing

**Estructura típica**:
```javascript
// Composition API
<script setup>
import { ref, computed } from 'vue'
import { useStore } from '@/stores/auth'

const count = ref(0)
const doubleCount = computed(() => count.value * 2)
</script>
```

---

### Q10: ¿Cómo manejan el estado global en el frontend?

**Respuesta:**
**Pinia (State Management)**:

1. **Stores organizados por dominio**:
   - `auth.js`: Autenticación y usuario
   - `prediction.js`: Predicciones y análisis
   - `finca.js`: Fincas y lotes
   - `notification.js`: Notificaciones
   - `config.js`: Configuración

2. **Características**:
   - Estado reactivo
   - Actions: Lógica asíncrona
   - Getters: Computed values
   - Persistencia: localStorage/sessionStorage

3. **Ventajas sobre Vuex**:
   - Más simple y directo
   - TypeScript support mejor
   - DevTools integradas
   - Menos boilerplate

**Ejemplo**:
```javascript
// store/auth.js
export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null
  }),
  actions: {
    async login(credentials) {
      // Lógica de login
    }
  }
})
```

---

### Q11: ¿Cómo manejan el routing y protección de rutas?

**Respuesta:**
**Vue Router con guards**:

1. **Rutas definidas**:
   - Rutas públicas: `/login`, `/register`
   - Rutas protegidas: Requieren autenticación
   - Rutas admin: Requieren rol admin

2. **Navigation Guards**:
   - `beforeEach`: Valida autenticación antes de entrar
   - Redirige a login si no autenticado
   - Valida permisos según rol

3. **Implementación**:
```javascript
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next('/unauthorized')
  } else {
    next()
  }
})
```

**Meta fields**:
- `requiresAuth`: Requiere autenticación
- `requiresAdmin`: Requiere rol admin
- `title`: Título de la página

---

## 🔄 API REST

### Q12: ¿Cuál es la estructura de la API REST?

**Respuesta:**
**RESTful API con Django REST Framework**:

**Estructura de URLs**:
```
/api/v1/
├── auth/              # Autenticación
│   ├── login/
│   ├── register/
│   ├── refresh/
│   └── profile/
├── fincas/            # Fincas
│   ├── /              # List/Create
│   └── <id>/          # Retrieve/Update/Delete
├── images/            # Imágenes
│   ├── /              # List/Create
│   └── <id>/          # Detail/Update/Delete
├── scan/measure/      # Análisis ML
├── ml/                # Endpoints ML
│   ├── models/status/
│   ├── train/
│   └── metrics/
└── reports/           # Reportes
```

**Convenciones**:
- URLs en plural: `/fincas/`, `/images/`
- Métodos HTTP semánticos: GET, POST, PUT, PATCH, DELETE
- Códigos HTTP apropiados: 200, 201, 400, 401, 404, 500
- Paginación: `?page=1&page_size=20`
- Filtrado: `?finca_id=1&status=active`

**Versionado**: `/api/v1/` permite futuras versiones

---

### Q13: ¿Cómo manejan errores y respuestas de la API?

**Respuesta:**
**Estandarización de respuestas**:

1. **Formato de éxito**:
```json
{
  "success": true,
  "message": "Operación exitosa",
  "data": { ... }
}
```

2. **Formato de error**:
```json
{
  "success": false,
  "error": "Descripción del error",
  "details": { ... }
}
```

3. **Códigos HTTP**:
   - `200`: Éxito
   - `201`: Creado
   - `400`: Bad Request (validación)
   - `401`: No autenticado
   - `403`: No autorizado
   - `404`: No encontrado
   - `500`: Error interno

4. **Manejo centralizado**:
   - Decorators: `@handle_api_errors`
   - Exceptions custom: `APIException`, `ValidationError`
   - Logging: Todos los errores se registran

**Frontend**: Interceptores de Axios manejan errores globalmente

---

## 📊 FUNCIONALIDADES DE NEGOCIO

### Q14: ¿Cómo funciona la gestión de fincas y lotes?

**Respuesta:**
**Modelo de datos**:

1. **Finca**:
   - Propietario (usuario)
   - Información geográfica (departamento, municipio)
   - Estadísticas (número de lotes, imágenes)
   - Estado (activo/inactivo)

2. **Lote**:
   - Pertenece a una Finca
   - Información específica del lote
   - Estadísticas de análisis
   - Relación con imágenes

**Funcionalidades**:
- CRUD completo de fincas y lotes
- Validación de ownership (usuarios solo ven sus fincas)
- Estadísticas agregadas (número de análisis, etc.)
- Relaciones: Finca → Lotes → Imágenes → Predicciones

**API endpoints**:
- `GET /api/v1/fincas/`: Listar fincas del usuario
- `POST /api/v1/fincas/`: Crear finca
- `GET /api/v1/fincas/<id>/lotes/`: Lotes de una finca
- `POST /api/v1/lotes/`: Crear lote

---

### Q15: ¿Cómo funciona el sistema de reportes?

**Respuesta:**
**Generación de reportes**:

1. **Tipos de reportes**:
   - Reporte de agricultores (Excel)
   - Reporte de usuarios (Excel)
   - Reporte de métricas (Excel/PDF)
   - Reportes personalizados

2. **Tecnologías**:
   - **Excel**: `openpyxl`, `XlsxWriter`
   - **PDF**: `reportlab` (opcional)
   - Generación asíncrona con Celery

3. **Proceso**:
   - Usuario solicita reporte
   - Tarea Celery genera archivo
   - Almacenamiento temporal
   - Descarga por URL
   - Limpieza automática después de X días

**Endpoints**:
- `POST /api/v1/reports/agricultores/`: Generar reporte
- `GET /api/v1/reports/<id>/download/`: Descargar reporte

---

## ⚡ PERFORMANCE Y OPTIMIZACIÓN

### Q16: ¿Cómo optimizan el rendimiento del sistema?

**Respuesta:**
**Optimizaciones implementadas**:

1. **Backend**:
   - **Queries optimizados**: `select_related()`, `prefetch_related()`
   - **Paginación**: Limita resultados por página
   - **Caching**: Redis para cache (opcional)
   - **Indexación**: Índices en campos frecuentemente consultados
   - **Lazy loading**: Modelos ML cargados solo cuando se necesitan

2. **Frontend**:
   - **Code splitting**: Lazy loading de rutas
   - **Image optimization**: Compresión de imágenes
   - **Caching**: Service workers (PWA ready)
   - **Debouncing**: En búsquedas y filtros

3. **Base de datos**:
   - **Índices**: En foreign keys y campos de búsqueda
   - **Query optimization**: Análisis de queries lentos
   - **Connection pooling**: PostgreSQL connection pool

4. **API**:
   - **Caching de endpoints**: Cache de respuestas estáticas
   - **Compression**: Gzip para respuestas grandes
   - **Pagination**: Limita datos transferidos

---

### Q17: ¿Cómo manejan tareas asíncronas y largas?

**Respuesta:**
**Celery + Redis para tareas asíncronas**:

1. **Tareas asíncronas**:
   - Entrenamiento de modelos ML
   - Generación de reportes grandes
   - Validación de datasets
   - Procesamiento de imágenes en batch
   - Envío de emails masivos

2. **Configuración**:
   - **Broker**: Redis (o RabbitMQ)
   - **Workers**: Múltiples workers para escalabilidad
   - **Retries**: Reintentos automáticos en caso de fallo
   - **Priority queues**: Colas con prioridad

3. **Tracking**:
   - Task IDs para seguimiento
   - Estado: Pending, Started, Success, Failure
   - Endpoint: `GET /api/v1/tasks/<task_id>/status/`

4. **Ventajas**:
   - No bloquea el servidor web
   - Escalable: Múltiples workers
   - Resiliente: Reintentos y manejo de errores

---

## 🔔 WEBSOCKETS Y TIEMPO REAL

### Q18: ¿Cómo funcionan las notificaciones en tiempo real?

**Respuesta:**
**Django Channels + WebSockets**:

1. **Arquitectura**:
   - **Backend**: Django Channels
   - **Channel Layer**: Redis (o InMemory para desarrollo)
   - **Frontend**: WebSocket connection

2. **Eventos en tiempo real**:
   - Predicción completada
   - Entrenamiento completado
   - Notificaciones del sistema
   - Actualizaciones de estado

3. **Implementación**:
   - Consumers en `api/consumers.py`
   - Realtime service: `api/realtime_service.py`
   - Frontend: Composable `useWebSocket.js`

4. **Fallback**:
   - Polling si WebSocket no disponible
   - Notificaciones en BD como respaldo

---

## 🐳 DEPLOYMENT Y DEVOPS

### Q19: ¿Cómo despliegan el sistema en producción?

**Respuesta:**
**Opciones de deployment**:

1. **Docker (Recomendado)**:
   - `docker-compose.yml` para desarrollo y producción
   - Contenedores separados: Backend, Frontend, DB, Redis
   - Facilita deployment consistente

2. **Render/Railway**:
   - Configuraciones listas en `render.yaml`
   - Deploy automático desde Git
   - Variables de entorno configurables

3. **Kubernetes** (opcional):
   - Configuraciones en `k8s/`
   - Escalado horizontal
   - Service discovery

4. **Requisitos de producción**:
   - PostgreSQL 15+
   - Redis (para Celery y cache)
   - Variables de entorno configuradas
   - SSL/HTTPS habilitado
   - Backup de base de datos

---

### Q20: ¿Cómo manejan las variables de entorno y secrets?

**Respuesta:**
**Gestión de configuración**:

1. **Archivo `.env`**:
   - Variables de entorno en `.env`
   - No versionado (en `.gitignore`)
   - Ejemplo en `env.example`

2. **Variables críticas**:
   - `SECRET_KEY`: Clave secreta de Django
   - `DB_PASSWORD`: Contraseña de base de datos
   - `EMAIL_HOST_PASSWORD`: Contraseña de email
   - `JWT_SECRET`: Clave JWT (si diferente)

3. **Producción**:
   - Variables en plataforma (Render, Railway, etc.)
   - No hardcodeadas en código
   - Rotación periódica de secrets

4. **Validación**:
   - Verificación de variables requeridas al iniciar
   - Valores por defecto seguros
   - Logs de advertencia si faltan

---

## 🧪 TESTING

### Q21: ¿Cómo están estructurados los tests?

**Respuesta:**
**Testing implementado**:

1. **Backend (pytest)**:
   - Unit tests: Funciones y métodos
   - Integration tests: Endpoints y servicios
   - Test fixtures: `factories.py` (Factory Boy)
   - Coverage: Cobertura de código

2. **Frontend (Vitest)**:
   - Unit tests: Componentes y funciones
   - Integration tests: Flujos completos
   - Coverage: Cobertura de código

3. **Ejecutar tests**:
```bash
# Backend
pytest
pytest --cov

# Frontend
npm test
npm run test:coverage
```

4. **CI/CD** (recomendado):
   - Tests automáticos en PR
   - Coverage mínimo requerido
   - Validación antes de merge

---

## 📋 SEGURIDAD ADICIONAL

### Q22: ¿Cómo manejan la auditoría y logs?

**Respuesta:**
**Sistema de auditoría completo**:

1. **Activity Logs**:
   - Todas las acciones importantes registradas
   - Modelo: `ActivityLog` (usuario, acción, timestamp)
   - Incluye: Creaciones, actualizaciones, eliminaciones

2. **Login History**:
   - Registro de todos los logins
   - IP address, user agent, timestamp
   - Detección de accesos sospechosos

3. **Logging**:
   - Django logging configurado
   - Niveles: DEBUG, INFO, WARNING, ERROR
   - Archivos de log: `logs/django.log`
   - Rotación de logs

4. **Endpoints**:
   - `GET /api/v1/audit/activity-logs/`: Ver actividad
   - `GET /api/v1/audit/login-history/`: Ver logins
   - Solo accesibles por admin

---

### Q23: ¿Cómo validan la integridad de datos?

**Respuesta:**
**Validaciones implementadas**:

1. **Nivel de modelo**:
   - Constraints en base de datos (Foreign Keys, Unique, Check)
   - Validaciones en modelos Django
   - `clean()` methods para validación custom

2. **Nivel de serializer**:
   - Validación de inputs en serializers
   - Tipos de datos correctos
   - Campos requeridos

3. **Nivel de servicio**:
   - Validación de reglas de negocio
   - Ownership validation (usuarios solo sus recursos)
   - Estado validation (transiciones válidas)

4. **Base de datos**:
   - Foreign keys con `ON DELETE` apropiado
   - Unique constraints
   - Check constraints para valores válidos

---

## 🔄 ESCALABILIDAD

### Q24: ¿Cómo escalan el sistema si crece?

**Respuesta:**
**Estrategias de escalabilidad**:

1. **Horizontal Scaling**:
   - Múltiples instancias del backend (load balancer)
   - Múltiples workers de Celery
   - Read replicas de PostgreSQL

2. **Vertical Scaling**:
   - Más CPU/RAM para servidor
   - GPU para procesamiento ML
   - Optimización de queries

3. **Caching**:
   - Redis cache para respuestas frecuentes
   - CDN para archivos estáticos
   - Cache de predicciones ML

4. **Database Optimization**:
   - Índices optimizados
   - Query optimization
   - Connection pooling
   - Read replicas

5. **ML Scaling**:
   - Servidor ML dedicado (TorchServe)
   - Batch processing optimizado
   - Model quantization

---

## 📚 DOCUMENTACIÓN

### Q25: ¿Dónde está la documentación del sistema?

**Respuesta:**
**Documentación disponible**:

1. **README.md**: 
   - Instalación y setup
   - Dependencias
   - Comandos útiles

2. **Documentación técnica**:
   - `Doc/Documentacion/`: Documentación arquitectónica
   - `Doc/Diagramas_UML/`: Diagramas UML
   - `Doc/Flujos/`: Flujos de proceso

3. **API Documentation**:
   - Swagger: `http://localhost:8000/swagger/`
   - ReDoc: `http://localhost:8000/redoc/`
   - Generada automáticamente con drf-yasg

4. **Código**:
   - Docstrings en funciones y clases
   - Type hints donde aplica
   - Comentarios explicativos

---

## 💡 TIPS PARA RESPUESTAS IMPREVISTAS

Si te hacen una pregunta que no conoces:

1. **Admite desconocimiento**: "No tengo esa información exacta, pero puedo investigarla"

2. **Ofrece documentación**: 
   - "Tenemos documentación en `Doc/`"
   - "El código está comentado"

3. **Sugiere revisar código**: 
   - "Podemos revisar el código fuente"
   - "Los archivos principales están en..."

4. **Deja seguimiento abierto**: 
   - "Puedo investigar y responder después"
   - "Podemos programar sesión técnica"

---

## 📋 CHECKLIST RÁPIDO

**Arquitectura**:
- ✅ 3 capas: Frontend (Vue.js), Backend (Django), DB (PostgreSQL)
- ✅ API REST + WebSockets
- ✅ Servicios asíncronos con Celery

**Seguridad**:
- ✅ JWT authentication
- ✅ Role-based permissions
- ✅ Protección contra SQL injection, XSS, CSRF
- ✅ Rate limiting
- ✅ Audit logs

**Performance**:
- ✅ Query optimization
- ✅ Caching (Redis)
- ✅ Paginación
- ✅ Lazy loading

**Deployment**:
- ✅ Docker support
- ✅ Variables de entorno
- ✅ Configuraciones para Render/Railway

---

**¡Con este documento deberías estar preparado para cualquier pregunta técnica sobre el sistema completo! 🚀**



