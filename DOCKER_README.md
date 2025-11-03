# 🐳 CacaoScan - Guía de Docker

Guía completa para ejecutar CacaoScan usando Docker Compose.

## 📋 Prerrequisitos

- Docker Desktop o Docker Engine instalado
- Docker Compose v3.8 o superior
- Git

## 🚀 Inicio Rápido

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd cacaoscan
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y configura tus variables:

```bash
cp .env.example .env
```

Edita `.env` con tus configuraciones (opcional para desarrollo):

```env
# Base de datos
DB_NAME=cacaoscan_db
DB_USER=postgres
DB_PASSWORD=postgres123

# Django
SECRET_KEY=tu-secret-key-aqui
DEBUG=True

# Redis
USE_REDIS=True

# Email (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password
```

### 3. Construir y ejecutar los contenedores

```bash
docker-compose up -d --build
```

Este comando construirá las imágenes y levantará todos los servicios:
- **PostgreSQL** (puerto 5432)
- **Redis** (puerto 6379)
- **Backend Django** (puerto 8000)
- **Frontend Vue/Vite** (puerto 5173)
- **Celery Worker**
- **Celery Beat**

### 4. Verificar que todo esté funcionando

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 5. Acceder a la aplicación

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1/
- **Admin Django**: http://localhost:8000/admin/
- **Swagger API Docs**: http://localhost:8000/swagger/
- **ReDoc**: http://localhost:8000/redoc/

### 6. Credenciales por defecto

El sistema crea automáticamente un usuario administrador:

- **Username**: `admin_training`
- **Email**: `admin@cacaoscan.com`
- **Password**: `admin123`

⚠️ **Importante**: Cambia estas credenciales en producción.

## 📁 Estructura de Contenedores

### Backend (Python/Django)
- **Imagen**: `cacaoscan_backend`
- **Puerto**: 8000
- **Base**: Python 3.11-slim
- **Comando**: Gunicorn con 4 workers

### Frontend (Vue/Vite)
- **Imagen**: `cacaoscan_frontend`
- **Puerto**: 5173 → 80 (nginx)
- **Base**: Node.js 20-alpine + Nginx
- **Build**: Multi-stage con pnpm

### Base de Datos
- **Imagen**: PostgreSQL 15-alpine
- **Puerto**: 5432
- **Volumen**: `postgres_data`

### Redis
- **Imagen**: Redis 7-alpine
- **Puerto**: 6379
- **Volumen**: `redis_data`

### Celery Worker
- **Imagen**: Basada en backend
- **Comando**: `celery -A cacaoscan worker --loglevel=info --concurrency=4`

### Celery Beat
- **Imagen**: Basada en backend
- **Comando**: `celery -A cacaoscan beat --loglevel=info`

## 🔧 Comandos Útiles

### Gestión de contenedores

```bash
# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ borra datos)
docker-compose down -v

# Reiniciar un servicio específico
docker-compose restart backend

# Ver estado de los servicios
docker-compose ps

# Reconstruir las imágenes
docker-compose build --no-cache
```

### Ejecutar comandos en contenedores

```bash
# Django management commands
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Django shell
docker-compose exec backend python manage.py shell

# Bash en el backend
docker-compose exec backend bash

# Logs de PostgreSQL
docker-compose exec db psql -U postgres -d cacaoscan_db
```

### Base de datos

```bash
# Hacer backup
docker-compose exec db pg_dump -U postgres cacaoscan_db > backup.sql

# Restaurar backup
docker-compose exec -T db psql -U postgres cacaoscan_db < backup.sql

# Ver logs de PostgreSQL
docker-compose logs -f db
```

## 🔍 Desarrollo

### Modo desarrollo con hot-reload

El `docker-compose.yml` monta volúmenes para desarrollo:

```yaml
volumes:
  - ./backend:/app          # Código backend montado
  - ./frontend:/app          # Código frontend montado
```

Los cambios se reflejan automáticamente en los contenedores.

### Ejecutar tests

```bash
# Tests del backend
docker-compose exec backend python manage.py test

# Tests del frontend (si están configurados)
docker-compose exec frontend npm test
```

## 🐛 Solución de Problemas

### Los contenedores no inician

```bash
# Ver logs detallados
docker-compose logs -f

# Verificar estado
docker-compose ps

# Reconstruir desde cero
docker-compose down -v
docker-compose up -d --build
```

### Error de conexión a la base de datos

```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps db

# Ver logs de PostgreSQL
docker-compose logs db

# Verificar variables de entorno
docker-compose exec backend env | grep DB_
```

### Frontend no se conecta al backend

1. Verificar que ambos contenedores estén en la misma red:
```bash
docker-compose ps
```

2. Verificar configuración de CORS en `.env`:
```env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
FRONTEND_URL=http://localhost:5173
```

### Celery no procesa tareas

```bash
# Ver logs de Celery Worker
docker-compose logs -f celery_worker

# Verificar conexión a Redis
docker-compose exec redis redis-cli ping

# Verificar queue
docker-compose exec celery_worker celery -A cacaoscan inspect active
```

### Limpiar todo y empezar de nuevo

```bash
# ⚠️ Esto elimina TODOS los datos
docker-compose down -v --rmi all
docker-compose up -d --build
```

## 📦 Producción

Para desplegar en producción:

1. **Cambiar variables de entorno**:
   ```env
   DEBUG=False
   SECRET_KEY=generar-una-clave-segura-aqui
   ALLOWED_HOSTS=tu-dominio.com
   ```

2. **Configurar base de datos externa** (opcional):
   ```env
   DB_HOST=tu-servidor-db.com
   DB_PORT=5432
   ```

3. **Configurar email real**:
   ```env
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_HOST_USER=tu-email@gmail.com
   EMAIL_HOST_PASSWORD=tu-app-password
   ```

4. **Usar AWS S3 para media**:
   ```env
   USE_S3=True
   AWS_ACCESS_KEY_ID=tu-access-key
   AWS_SECRET_ACCESS_KEY=tu-secret-key
   AWS_STORAGE_BUCKET_NAME=cacaoscan-prod
   ```

5. **Construir para producción**:
   ```bash
   docker-compose -f docker-compose.yml build --no-cache
   docker-compose up -d
   ```

## 🔐 Seguridad

- ✅ Nunca comitees el archivo `.env` al repositorio
- ✅ Usa claves seguras en producción
- ✅ Habilita HTTPS en producción
- ✅ Configura firewall adecuado
- ✅ Habilita autenticación fuerte
- ✅ Realiza backups regulares

## 📝 Notas Adicionales

- Los volúmenes de PostgreSQL y Redis persisten entre reinicios
- El código está montado como volumen para desarrollo rápido
- En producción, considera usar volúmenes nombrados para mejor rendimiento
- Los healthchecks aseguran que los servicios dependientes esperen a que estén listos

## 🆘 Soporte

Para más ayuda:
- Ver logs: `docker-compose logs -f`
- Documentación Django: https://docs.djangoproject.com/
- Documentación Vue: https://vuejs.org/
- Documentación Docker Compose: https://docs.docker.com/compose/

## 📊 Monitoreo

```bash
# Ver uso de recursos
docker stats

# Ver logs en tiempo real
docker-compose logs -f --tail=100

# Ver estado de salud
docker-compose ps
```

---

¡Listo para usar CacaoScan con Docker! 🚀

