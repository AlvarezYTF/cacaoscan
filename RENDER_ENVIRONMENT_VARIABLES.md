# 🔐 Variables de Entorno para Render - CacaoScan

Esta guía lista todas las variables de entorno que debes configurar en Render Dashboard para cada servicio.

---

## 📋 ÍNDICE

1. [Variables Comunes (Backend, Worker, Beat)](#variables-comunes)
2. [Variables Solo para Backend](#variables-solo-para-backend)
3. [Variables para Frontend](#variables-para-frontend)
4. [Valores de Ejemplo](#valores-de-ejemplo)
5. [Configuración Paso a Paso](#configuración-paso-a-paso)

---

## 🔄 VARIABLES COMUNES
**Configurar en:** `cacaoscan-backend`, `cacaoscan-celery-worker`, `cacaoscan-celery-beat`

### Base de Datos
✅ **NO CONFIGURAR MANUALMENTE** - Render las configura automáticamente desde la base de datos:
- `DB_NAME` (automático)
- `DB_USER` (automático)
- `DB_PASSWORD` (automático)
- `DB_HOST` (automático)
- `DB_PORT` (automático)

### Django Core
```bash
DEBUG=False
SECRET_KEY=tu-secret-key-aqui-mismo-para-todos-los-servicios
ALLOWED_HOSTS=cacaoscan-backend.onrender.com
APP_ENV=production
```

### Redis (REQUERIDO para Celery)
```bash
USE_REDIS=true
USE_CELERY_REDIS=true
REDIS_HOST=tu-redis-host.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=tu-redis-password
REDIS_DB=0
```

### Celery URLs (REQUERIDO para Celery)
```bash
CELERY_BROKER_URL=redis://:tu-redis-password@tu-redis-host.upstash.io:6379/0
CELERY_RESULT_BACKEND=redis://:tu-redis-password@tu-redis-host.upstash.io:6379/0
```

### Email (Opcional - para producción)
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-gmail
DEFAULT_FROM_EMAIL=CacaoScan <noreply@cacaoscan.com>
SERVER_EMAIL=CacaoScan <noreply@cacaoscan.com>
ADMIN_EMAIL=admin@cacaoscan.com
```

### CORS y Frontend
```bash
CORS_ALLOWED_ORIGINS=https://cacaoscan-frontend.onrender.com
FRONTEND_URL=https://cacaoscan-frontend.onrender.com
```

### WebSockets (Opcional)
```bash
WEBSOCKET_URL=wss://cacaoscan-backend.onrender.com/ws/
REALTIME_NOTIFICATIONS_ENABLED=True
NOTIFICATION_BROADCAST_ENABLED=True
NOTIFICATION_PERSISTENCE_ENABLED=True
```

### Archivos Estáticos
```bash
DJANGO_STATIC_ROOT=/var/www/staticfiles
DJANGO_MEDIA_ROOT=/var/www/media
USE_STATICFILES_MANIFEST=True
```

### Otros
```bash
SERVICE_ROLE=web  # Para backend
# SERVICE_ROLE=celery-worker  # Para worker
# SERVICE_ROLE=celery-beat  # Para beat

SEED_INITIAL_DATA=true  # Solo en el primer deploy
AUTO_TRAIN_ENABLED=0
SECURE_SSL_REDIRECT=True
```

---

## 🎯 VARIABLES SOLO PARA BACKEND

**Configurar en:** `cacaoscan-backend` únicamente

### Superusuario (Opcional - solo si quieres creación automática)
```bash
DJANGO_CREATE_SUPERUSER=true
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@cacaoscan.com
DJANGO_SUPERUSER_PASSWORD=tu-contraseña-segura-min-8-caracteres
```

⚠️ **IMPORTANTE:** `DJANGO_SUPERUSER_PASSWORD` debe tener mínimo 8 caracteres.

---

## 🎨 VARIABLES PARA FRONTEND

**Configurar en:** `cacaoscan-frontend`

✅ **NO CONFIGURAR MANUALMENTE** - Render las configura automáticamente:
- `VITE_API_BASE_URL` (automático desde backend)
- `RUNTIME_API_BASE_URL` (automático desde backend)

---

## 📝 VALORES DE EJEMPLO COMPLETOS

### Ejemplo 1: Backend con Redis (Upstash)

```bash
# Django
DEBUG=False
SECRET_KEY=django-insecure-ejemplo-cambiar-por-una-real-generada
ALLOWED_HOSTS=cacaoscan-backend.onrender.com
APP_ENV=production

# Redis (Upstash)
USE_REDIS=true
USE_CELERY_REDIS=true
REDIS_HOST=global-ample-12345.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=AXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
REDIS_DB=0

# Celery
CELERY_BROKER_URL=redis://:AXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@global-ample-12345.upstash.io:6379/0
CELERY_RESULT_BACKEND=redis://:AXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@global-ample-12345.upstash.io:6379/0

# Email (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
DEFAULT_FROM_EMAIL=CacaoScan <noreply@cacaoscan.com>
ADMIN_EMAIL=admin@cacaoscan.com

# CORS
CORS_ALLOWED_ORIGINS=https://cacaoscan-frontend.onrender.com
FRONTEND_URL=https://cacaoscan-frontend.onrender.com

# Superusuario
DJANGO_CREATE_SUPERUSER=true
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@cacaoscan.com
DJANGO_SUPERUSER_PASSWORD=Admin123!Secure

# Otros
SERVICE_ROLE=web
SEED_INITIAL_DATA=true
AUTO_TRAIN_ENABLED=0
SECURE_SSL_REDIRECT=True
```

### Ejemplo 2: Celery Worker (mismo Redis)

```bash
# Django (mismo SECRET_KEY que backend)
DEBUG=False
SECRET_KEY=django-insecure-ejemplo-cambiar-por-una-real-generada
ALLOWED_HOSTS=cacaoscan-backend.onrender.com
APP_ENV=production

# Redis (mismo que backend)
USE_REDIS=true
USE_CELERY_REDIS=true
REDIS_HOST=global-ample-12345.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=AXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
REDIS_DB=0

# Celery (mismo que backend)
CELERY_BROKER_URL=redis://:AXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@global-ample-12345.upstash.io:6379/0
CELERY_RESULT_BACKEND=redis://:AXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@global-ample-12345.upstash.io:6379/0

# Service Role
SERVICE_ROLE=celery-worker
```

### Ejemplo 3: Celery Beat (mismo Redis)

```bash
# Django (mismo SECRET_KEY que backend)
DEBUG=False
SECRET_KEY=django-insecure-ejemplo-cambiar-por-una-real-generada
ALLOWED_HOSTS=cacaoscan-backend.onrender.com
APP_ENV=production

# Redis (mismo que backend)
USE_REDIS=true
USE_CELERY_REDIS=true
REDIS_HOST=global-ample-12345.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=AXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
REDIS_DB=0

# Celery (mismo que backend)
CELERY_BROKER_URL=redis://:AXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@global-ample-12345.upstash.io:6379/0
CELERY_RESULT_BACKEND=redis://:AXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@global-ample-12345.upstash.io:6379/0

# Service Role
SERVICE_ROLE=celery-beat
```

---

## 🚀 CONFIGURACIÓN PASO A PASO

### Paso 1: Generar SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado y úsalo como valor de `SECRET_KEY` en **todos los servicios**.

### Paso 2: Configurar Redis (Upstash)

1. Ve a [Upstash](https://upstash.com/) y crea una cuenta
2. Crea una nueva base de datos Redis
3. Elige la región más cercana
4. Copia:
   - **Endpoint** (REDIS_HOST)
   - **Port** (REDIS_PORT)
   - **Password** (REDIS_PASSWORD)

### Paso 3: Configurar Variables en Render

#### Para `cacaoscan-backend`:

1. Ve a Render Dashboard → `cacaoscan-backend` → Environment
2. Agrega todas las variables de la sección "Variables Comunes" + "Variables Solo para Backend"
3. Usa los valores de tu Redis de Upstash
4. Genera y copia la SECRET_KEY

#### Para `cacaoscan-celery-worker`:

1. Ve a Render Dashboard → `cacaoscan-celery-worker` → Environment
2. Agrega todas las variables de la sección "Variables Comunes"
3. **IMPORTANTE:** Usa la **misma SECRET_KEY** que el backend
4. Usa los **mismos valores de Redis** que el backend
5. Cambia `SERVICE_ROLE=celery-worker`

#### Para `cacaoscan-celery-beat`:

1. Ve a Render Dashboard → `cacaoscan-celery-beat` → Environment
2. Agrega todas las variables de la sección "Variables Comunes"
3. **IMPORTANTE:** Usa la **misma SECRET_KEY** que el backend
4. Usa los **mismos valores de Redis** que el backend
5. Cambia `SERVICE_ROLE=celery-beat`

### Paso 4: Verificar

1. Despliega todos los servicios
2. Revisa los logs:
   - Backend: debe iniciar Gunicorn
   - Worker: debe mostrar "celery@hostname ready"
   - Beat: debe mostrar "beat: Starting..."

---

## ⚠️ NOTAS IMPORTANTES

### 🔒 Seguridad

1. **SECRET_KEY**: Debe ser la misma para todos los servicios (backend, worker, beat)
2. **DJANGO_SUPERUSER_PASSWORD**: Nunca la pongas en `render.yaml`, solo en Dashboard
3. **REDIS_PASSWORD**: Manténla segura, no la compartas
4. **EMAIL_HOST_PASSWORD**: Si usas Gmail, genera una "App Password", no tu contraseña normal

### 🔄 Sincronización

- **SECRET_KEY**: Mismo valor en backend, worker y beat
- **Redis**: Mismas credenciales en backend, worker y beat
- **Database**: Render las configura automáticamente, no las cambies manualmente

### 📊 Orden de Despliegue

1. Primero: Base de datos (automático)
2. Segundo: Backend
3. Tercero: Redis externo (Upstash)
4. Cuarto: Worker y Beat (después de configurar Redis)

### 🐛 Troubleshooting

**Error: "Celery not connected"**
- Verifica que Redis esté configurado correctamente
- Verifica que `USE_CELERY_REDIS=true`
- Verifica que las URLs de Celery sean correctas

**Error: "SECRET_KEY missing"**
- Asegúrate de configurar SECRET_KEY en todos los servicios
- Debe ser la misma en backend, worker y beat

**Error: "Database connection failed"**
- Render configura automáticamente las variables DB_*
- No las sobrescribas manualmente

---

## 📋 CHECKLIST FINAL

Antes de desplegar, verifica:

- [ ] SECRET_KEY configurada en backend, worker y beat (mismo valor)
- [ ] Redis configurado (Upstash o similar)
- [ ] USE_REDIS=true en todos los servicios
- [ ] USE_CELERY_REDIS=true en todos los servicios
- [ ] CELERY_BROKER_URL y CELERY_RESULT_BACKEND configurados
- [ ] SERVICE_ROLE correcto en cada servicio
- [ ] DJANGO_CREATE_SUPERUSER configurado solo en backend (si lo necesitas)
- [ ] Email configurado (si lo necesitas)
- [ ] CORS_ALLOWED_ORIGINS apunta al frontend correcto
- [ ] FRONTEND_URL configurada

---

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en Render Dashboard
2. Verifica que todas las variables estén configuradas
3. Asegúrate de que Redis esté accesible desde Render
4. Verifica que SECRET_KEY sea la misma en todos los servicios

