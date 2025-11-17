# Solución para Error de Build de Docker

## Error Observado

```
failed to solve: failed to prepare extraction snapshot ... parent snapshot ... does not exist: not found
```

Este error indica que Docker tiene problemas con el cache o capas corruptas de la imagen.

## Soluciones (en orden de preferencia)

### Solución 1: Limpiar Cache y Reconstruir (Recomendado)

```bash
# 1. Limpiar cache de Docker
docker builder prune -af

# 2. Limpiar imágenes no utilizadas
docker image prune -af

# 3. Reconstruir sin cache
docker compose build --no-cache backend

# 4. Si aún falla, limpiar todo el sistema Docker
docker system prune -af --volumes
docker compose build --no-cache backend
```

### Solución 2: Reconstruir Solo el Backend

```bash
# Detener contenedores
docker compose down

# Reconstruir backend sin cache
docker compose build --no-cache backend

# Levantar servicios
docker compose up -d
```

### Solución 3: Limpiar BuildKit Cache

```bash
# Si usas BuildKit (Docker Desktop)
docker buildx prune -af

# Reconstruir
docker compose build --no-cache backend
```

### Solución 4: Verificar Variables de Entorno

Los warnings sobre variables no establecidas son solo advertencias, pero puedes crear un archivo `.env`:

```bash
# Crear archivo .env en la raíz del proyecto
cat > .env << EOF
# Variables opcionales (pueden estar vacías)
fn=
go=
ty=
REDIS_PASSWORD=your_redis_password_here
EOF
```

## Comandos Rápidos

### Opción A: Limpieza Completa
```bash
docker compose down
docker system prune -af
docker compose build --no-cache backend
docker compose up -d
```

### Opción B: Solo Backend
```bash
docker compose build --no-cache --pull backend
```

### Opción C: Reconstruir Todo
```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

## Verificación

Después de reconstruir, verifica que todo funciona:

```bash
# Ver logs del backend
docker compose logs backend

# Verificar que el contenedor está corriendo
docker compose ps

# Probar el comando de entrenamiento
docker compose exec backend python manage.py train_cacao_models \
    --hybrid \
    --use-pixel-features \
    --epochs 5 \
    --batch-size 16 \
    --segmentation-backend opencv
```

## Si el Problema Persiste

1. **Verificar espacio en disco:**
   ```bash
   docker system df
   ```

2. **Reiniciar Docker Desktop** (si usas Windows/Mac)

3. **Verificar Dockerfile:**
   - Asegúrate de que el Dockerfile en `backend/Dockerfile` existe
   - Verifica que no haya problemas de sintaxis

4. **Actualizar Docker:**
   ```bash
   # Verificar versión
   docker --version
   docker compose version
   ```

## Nota sobre los Warnings

Los warnings sobre variables (`fn`, `go`, `ty`, `REDIS_PASSWORD`) son solo advertencias y no causan el error. Son variables opcionales que pueden estar vacías. Si quieres eliminarlos, crea un archivo `.env` con valores vacíos:

```env
fn=
go=
ty=
REDIS_PASSWORD=
```

Pero estos warnings no afectan la funcionalidad.

