# Guía de Seguridad y Permisos - CacaoScan

Esta guía documenta el sistema completo de seguridad, permisos y rate limiting implementado en CacaoScan.

## 🔐 Arquitectura de Seguridad

### Capas de Protección

1. **Middleware de Seguridad** - Primera línea de defensa
2. **Autenticación JWT** - Verificación de identidad
3. **Permisos por Rol** - Control de acceso granular
4. **Rate Limiting** - Protección contra abuso
5. **Validación de Archivos** - Seguridad en uploads
6. **Logging de Auditoría** - Trazabilidad completa

## 👥 Roles y Permisos

### Roles del Sistema

#### 🌱 **Agricultor (`farmer`)**
- **Permisos**:
  - Subir imágenes para predicción
  - Ver sus propias predicciones
  - Gestionar su perfil personal
  - Consultar estadísticas propias
- **Restricciones**:
  - No puede ver datos de otros usuarios
  - Requiere verificación de cuenta para uploads
  - Límites de rate limiting más estrictos

#### 📊 **Analista (`analyst`)**
- **Permisos**:
  - Ver todas las predicciones del sistema
  - Generar reportes y estadísticas
  - Gestionar dataset de entrenamiento
  - Consultar métricas del sistema
- **Restricciones**:
  - No puede gestionar usuarios
  - No puede entrenar modelos
  - Solo lectura en configuraciones

#### 👑 **Administrador (`admin`)**
- **Permisos**:
  - Acceso completo al sistema
  - Gestión de usuarios y roles
  - Entrenamiento de modelos ML
  - Configuraciones del sistema
  - Acciones masivas sobre usuarios
- **Sin restricciones significativas**

### Matriz de Permisos

| Funcionalidad | Agricultor | Analista | Admin |
|---------------|------------|----------|-------|
| Subir imágenes | ✅ (verificado) | ❌ | ✅ |
| Ver predicciones propias | ✅ | ✅ | ✅ |
| Ver todas las predicciones | ❌ | ✅ | ✅ |
| Gestionar dataset | ❌ | ✅ | ✅ |
| Entrenar modelos | ❌ | ❌ | ✅ |
| Gestionar usuarios | ❌ | ❌ | ✅ |
| Ver estadísticas sistema | ❌ | ✅ | ✅ |
| Configurar sistema | ❌ | ❌ | ✅ |

## 🛡️ Clases de Permisos Personalizadas

### Permisos Básicos

```python
# En apps/users/permissions.py

IsOwnerOrReadOnly       # Solo propietario puede editar
IsFarmerUser           # Solo agricultores
IsAnalystUser          # Solo analistas
IsAdminUser            # Solo administradores
IsVerifiedUser         # Solo usuarios verificados
IsAdminOrAnalyst       # Administradores o analistas
IsAdminOrOwner         # Administradores o propietarios
IsSameUserOrAdmin      # Mismo usuario o admin
```

### Permisos Especializados

```python
CanUploadImages        # Puede subir imágenes (verificado + farmer/admin)
CanViewPredictions     # Puede ver predicciones (según rol)
CanManageDataset       # Puede gestionar dataset (analyst/admin)
CanTrainModels         # Puede entrenar modelos (solo admin)
ReadOnlyForFarmers     # Agricultores solo lectura
```

## 🚦 Rate Limiting por Rol

### Límites Generales (por hora)

- **Anónimos**: 20 requests/hora
- **Agricultores**: 60 requests/hora  
- **Analistas**: 120 requests/hora
- **Administradores**: 300 requests/hora

### Límites Específicos por Endpoint

#### Predicciones ML
- **Agricultores**: 30 predicciones/hora
- **Analistas**: 60 predicciones/hora
- **Administradores**: 120 predicciones/hora

#### Autenticación
- **Login**: 5 intentos/minuto (por IP)
- **Registro**: 3 registros/hora (por IP)
- **Reset Password**: 3 intentos/hora (por IP)

#### Uploads
- **Agricultores**: 50 uploads/hora
- **Analistas**: 100 uploads/hora
- **Administradores**: 200 uploads/hora

#### Burst Protection
- **Todos los usuarios**: 10 requests/minuto (ráfagas)

## 🔒 Middleware de Seguridad

### 1. SecurityHeadersMiddleware
Agrega headers de seguridad estándar:
- Content Security Policy
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- Strict-Transport-Security (HTTPS)

### 2. RateLimitMiddleware
Control de velocidad dinámico:
- Por IP para usuarios anónimos
- Por usuario para autenticados
- Límites específicos por endpoint
- Protección contra DDoS

### 3. APILoggingMiddleware
Logging completo de APIs:
- Requests entrantes con IP y usuario
- Responses con status y tiempo
- Errores con stack trace

### 4. UserActivityMiddleware
Tracking de actividad:
- Última actividad de usuarios
- Estadísticas de uso
- Detección de cuentas inactivas

### 5. FileUploadSecurityMiddleware
Validación de archivos:
- Tamaño máximo (10MB)
- Tipos MIME permitidos
- Nombres de archivo seguros
- Extensiones peligrosas bloqueadas

### 6. RequestSizeMiddleware
Control de tamaño de requests:
- Máximo 15MB por request
- Protección contra memory exhaustion

## 🔍 Decoradores de Validación

### Decoradores Principales

```python
@require_role(['admin', 'analyst'])
def admin_only_view(request):
    # Solo administradores y analistas
    pass

@require_verified_user
def verified_only_view(request):
    # Solo usuarios con email verificado
    pass

@require_ownership(get_image_function)
def owner_only_view(request, image_id):
    # Solo propietario del objeto
    pass

@validate_file_upload(['jpg', 'png'], max_size_mb=5)
def upload_view(request):
    # Validar archivos antes de procesar
    pass

@log_api_access
def sensitive_view(request):
    # Logging automático de accesos
    pass
```

### Decoradores Combinados

```python
@farmer_upload_endpoint
def farmer_upload(request):
    # Combina: role, verificación, validación archivo, logging
    pass

@admin_management_endpoint  
def admin_action(request):
    # Combina: role admin, logging
    pass

@analyst_readonly_endpoint
def analyst_view(request):
    # Combina: role analyst/admin, logging
    pass
```

## 🚨 Sistema de Throttling Avanzado

### Throttles por Categoría

```python
# Throttles básicos por rol
FarmerThrottle     # 60/hour
AnalystThrottle    # 120/hour  
AdminThrottle      # 300/hour

# Throttles por funcionalidad
PredictionThrottle # Variable por rol
LoginThrottle      # 5/min
UploadThrottle     # Variable por rol
BurstThrottle      # 10/min
SustainedThrottle  # 1000/day

# Throttling inteligente
SmartThrottle      # Ajusta según comportamiento
```

### Configuración Dinámica

El sistema ajusta automáticamente los límites según:
- **Estado de verificación**: +50% para usuarios verificados
- **Historial de comportamiento**: -30% para usuarios abusivos
- **Rol del usuario**: Límites base diferentes
- **Endpoint específico**: Límites personalizados

## 📊 Logging y Auditoría

### Niveles de Logging

```python
# Configuración en settings.py
LOGGING = {
    'handlers': {
        'security_file': {
            'filename': 'logs/security.log',
            'level': 'WARNING',
        },
        'api_file': {
            'filename': 'logs/api.log', 
            'level': 'INFO',
        }
    }
}
```

### Eventos Registrados

- **Autenticación**: Login/logout, fallos de autenticación
- **Autorización**: Intentos de acceso denegado
- **Rate Limiting**: Violaciones de límites
- **File Uploads**: Archivos subidos, rechazados
- **API Access**: Todas las llamadas a API con tiempos
- **Errores**: Excepciones con contexto completo

## 🔧 Configuración de Producción

### Headers de Seguridad

```python
# En producción, configurar:
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

### Cache para Rate Limiting

```python
# Usar Redis en producción
CACHES = {
    'rate_limit': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/2',
        'TIMEOUT': 60,
    }
}
```

## 🚀 Endpoints Protegidos

### APIs de Autenticación
- `POST /api/auth/login/` - LoginThrottle
- `POST /api/auth/register/` - RegistrationThrottle
- `POST /api/auth/password-reset/` - PasswordResetThrottle

### APIs de Predicción
- `POST /api/images/predict/` - PredictionThrottle + CanUploadImages
- `GET /api/images/` - CanViewPredictions
- `GET /api/images/stats/` - IsAdminOrAnalyst

### APIs de Administración
- `GET /api/auth/admin/stats/` - IsAdminUser
- `POST /api/auth/admin/bulk-actions/` - IsAdminUser

## ⚠️ Consideraciones de Seguridad

### Vulnerabilidades Mitigadas

1. **Brute Force**: Rate limiting en login
2. **DDoS**: Rate limiting general y burst protection
3. **File Upload Abuse**: Validación de archivos y tamaños
4. **Information Disclosure**: Permisos granulares por rol
5. **CSRF**: Headers de seguridad y tokens
6. **XSS**: Content Security Policy
7. **Injection**: Validación de inputs y ORM seguro

### Monitoreo Recomendado

1. **Logs de seguridad**: Revisar intentos de acceso fallidos
2. **Rate limiting**: Monitorear violaciones frecuentes
3. **File uploads**: Auditar archivos rechazados
4. **Performance**: Tiempo de respuesta de APIs
5. **Usuarios**: Detectar comportamientos anómalos

## 🔄 Mejoras Futuras

### En Desarrollo
- [ ] 2FA para administradores
- [ ] Geo-blocking por país
- [ ] Machine Learning para detección de anomalías
- [ ] Integración con SIEM
- [ ] Backup automático de logs de seguridad

### Consideradas
- [ ] Rate limiting por región
- [ ] Honeypots para detectar bots
- [ ] Integración con servicios anti-fraude
- [ ] Análisis de comportamiento en tiempo real

## 📞 Contacto y Soporte

Para reportar vulnerabilidades de seguridad o consultas:

- **Email**: security@cacaoscan.com
- **Documentación**: Esta guía y código fuente
- **Logs**: `/backend/logs/` para debugging

---

**Nota**: Esta configuración de seguridad sigue las mejores prácticas de la industria y está diseñada para ser robusta pero usable. Revisa regularmente los logs y ajusta los límites según el uso real del sistema.
