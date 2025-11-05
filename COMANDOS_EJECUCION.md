# Comandos de Ejecución - CacaoScan

## ⚡ Comando Único para Ejecutar Todo

**Para nuevos desarrolladores o después de hacer pull:**

```bash
docker-compose up -d --build
```

**¡Eso es todo!** Este comando automáticamente:
- ✅ Construye las imágenes Docker
- ✅ Levanta todos los servicios (DB, Redis, Backend, Frontend, Celery)
- ✅ Espera a que la base de datos esté lista
- ✅ **Ejecuta migraciones automáticamente** (línea 39 de docker-entrypoint.sh)
- ✅ **Recopila archivos estáticos automáticamente** (línea 46 de docker-entrypoint.sh)
- ✅ Inicia todos los servicios

**No necesitas ejecutar comandos adicionales** - todo está automatizado en el `docker-entrypoint.sh`.

---

## 1. Construir y Levantar Contenedores

```bash
# Construir y levantar todos los servicios
docker-compose up -d --build
```

## 2. Verificar Estado de Contenedores

```bash
# Ver estado de todos los contenedores
docker-compose ps

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker
docker-compose logs -f celery_beat
```

## 3. Verificar Migraciones

**NOTA:** Las migraciones se ejecutan **automáticamente** al iniciar el contenedor. 
Estos comandos son solo para verificación o problemas específicos.

```bash
# Ver estado de todas las migraciones
docker exec cacaoscan_backend python manage.py showmigrations

# Ver migraciones pendientes
docker exec cacaoscan_backend python manage.py showmigrations --plan | Select-String -Pattern "\[ \]"

# Aplicar migraciones manualmente (solo si hay problemas)
docker exec cacaoscan_backend python manage.py migrate

# Aplicar migraciones de una app específica (solo si hay problemas)
docker exec cacaoscan_backend python manage.py migrate token_blacklist
```

## 4. Verificar Servicios

```bash
# Verificar healthcheck del backend
Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing

# Verificar frontend
curl.exe http://127.0.0.1:5173/health

# Verificar conectividad de red
docker exec cacaoscan_backend python -c "import socket; socket.gethostbyname('db')"
```

## 5. Gestión de Contenedores

```bash
# Reiniciar todos los servicios
docker-compose restart

# Reiniciar un servicio específico
docker-compose restart backend
docker-compose restart frontend
docker-compose restart celery_worker
docker-compose restart celery_beat

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (CUIDADO: elimina datos)
docker-compose down -v

# Reconstruir un servicio específico
docker-compose build --no-cache backend
docker-compose build --no-cache frontend
docker-compose build --no-cache celery_worker
docker-compose build --no-cache celery_beat
```

## 6. Comandos Django Útiles

```bash
# Crear superusuario
docker exec -it cacaoscan_backend python manage.py createsuperuser

# Recopilar archivos estáticos
docker exec cacaoscan_backend python manage.py collectstatic --noinput

# Shell de Django
docker exec -it cacaoscan_backend python manage.py shell

# Verificar configuración
docker exec cacaoscan_backend python manage.py check
```

## 7. Ver Logs en Tiempo Real

```bash
# Todos los servicios
docker-compose logs -f

# Backend
docker logs -f cacaoscan_backend

# Frontend
docker logs -f cacaoscan_frontend

# Celery Worker
docker logs -f cacaoscan_celery_worker

# Celery Beat
docker logs -f cacaoscan_celery_beat

# Base de datos
docker logs -f cacaoscan_db

# Redis
docker logs -f cacaoscan_redis
```

## 8. Acceso a Contenedores

```bash
# Acceder al shell del backend
docker exec -it cacaoscan_backend /bin/bash

# Acceder al shell del frontend
docker exec -it cacaoscan_frontend /bin/sh

# Acceder a PostgreSQL
docker exec -it cacaoscan_db psql -U postgres -d cacaoscan_db

# Acceder a Redis CLI
docker exec -it cacaoscan_redis redis-cli
```

## 9. Limpieza y Mantenimiento

```bash
# Ver contenedores detenidos
docker ps -a

# Eliminar contenedores detenidos
docker container prune

# Ver imágenes no utilizadas
docker images

# Limpiar imágenes no utilizadas
docker image prune -a

# Ver volúmenes
docker volume ls

# Limpiar volúmenes no utilizados
docker volume prune

# Verificar uso de recursos
docker stats
```

## 10. Verificación Final del Sistema

```bash
# Verificar que todos los servicios están corriendo
docker-compose ps

# Verificar que el backend responde
curl.exe http://localhost:8000/health

# Verificar que el frontend responde
curl.exe http://127.0.0.1:5173/health

# Verificar conexión a base de datos
docker exec cacaoscan_backend python manage.py dbshell

# Verificar que Celery está funcionando
docker logs cacaoscan_celery_worker --tail 20
docker logs cacaoscan_celery_beat --tail 20
```

## 11. URLs de Acceso

- **Frontend**: http://localhost:5173 o http://127.0.0.1:5173
- **Backend API**: http://localhost:8000
- **Swagger/API Docs**: http://localhost:8000/swagger/
- **Health Check**: http://localhost:8000/health
- **Admin Django**: http://localhost:8000/admin/

## 12. Comandos de Emergencia

```bash
# Si el backend no inicia, verificar logs
docker logs cacaoscan_backend --tail 100

# Si hay problemas de migraciones, forzar migración
docker exec cacaoscan_backend python manage.py migrate --run-syncdb

# Si hay problemas de red, verificar red Docker
docker network inspect cacaoscan_cacaoscan_network

# Si hay problemas de memoria, verificar uso
docker stats --no-stream

# Reiniciar todo desde cero (CUIDADO: elimina datos)
docker-compose down -v
docker-compose up -d --build
```

## Secuencia Recomendada para Primera Ejecución

### Para Nuevos Desarrolladores (Después de `git pull`):

1. **Solo necesitas esto:**
   ```bash
   docker-compose up -d --build
   ```

2. **Opcional - Verificar que todo funciona:**
   ```bash
   # Ver estado (esperar 30-60 segundos para que todo inicie)
   docker-compose ps
   
   # Ver logs si hay problemas
   docker-compose logs -f
   ```

3. **Abrir navegador:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/swagger/

**¡Las migraciones se ejecutan automáticamente!** No necesitas ejecutarlas manualmente.

### Si hay problemas:

Los comandos adicionales en este documento son solo para **depuración** o **tareas específicas**.

## Notas Importantes

### ✅ Automatización Incluida

- **Migraciones**: Se ejecutan automáticamente al iniciar (ver `docker-entrypoint.sh` línea 39)
- **Static Files**: Se recopilan automáticamente al iniciar (ver `docker-entrypoint.sh` línea 46)
- **Espera a DB**: El backend espera automáticamente a que la BD esté lista (ver `docker-entrypoint.sh` línea 28-35)
- **Dependencias**: Docker Compose maneja el orden de inicio con `depends_on` y `condition: service_healthy`

### ⚠️ Comportamiento Esperado

- Los contenedores de Celery pueden mostrar "unhealthy" - esto es normal, no tienen servidor web
- El frontend puede tardar unos segundos en estar disponible después de iniciar
- Si hay problemas de conexión, usar `127.0.0.1` en lugar de `localhost`
- Los logs se pueden ver en tiempo real con `-f` flag
- El primer inicio puede tardar 2-3 minutos mientras se construyen las imágenes

### 📝 Para Nuevos Desarrolladores

**Solo necesitas:**
1. `git pull` o `git clone`
2. `docker-compose up -d --build`
3. Esperar 1-2 minutos
4. Abrir http://localhost:5173

**¡Todo lo demás es automático!**
