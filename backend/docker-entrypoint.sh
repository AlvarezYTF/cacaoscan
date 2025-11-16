#!/bin/bash
set -euo pipefail

log() {
    printf '%s %s\n' "[$(date -Iseconds)]" "$*"
}

STATIC_ROOT=${DJANGO_STATIC_ROOT:-/var/www/staticfiles}
MEDIA_ROOT=${DJANGO_MEDIA_ROOT:-/var/www/media}
ROLE=${SERVICE_ROLE:-web}
DB_WAIT_TIMEOUT=${DB_WAIT_TIMEOUT:-60}

export PATH="/opt/venv/bin:$PATH"
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Configurar pkg_resources para que no escanee directorios problemáticos
# Esto reduce significativamente el uso de memoria
export PKG_RESOURCES_CACHE_DIR=/tmp/pkg_resources_cache
mkdir -p "$PKG_RESOURCES_CACHE_DIR" 2>/dev/null || true

# Crear directorios necesarios para la aplicación
mkdir -p /app/logs /app/media/logs /app/staticfiles 2>/dev/null || true
mkdir -p /app/media/datasets /app/media/reportes 2>/dev/null || true
mkdir -p /app/media/cacao_images/raw \
         /app/media/cacao_images/crops \
         /app/media/cacao_images/crops_runtime \
         /app/media/cacao_images/processed \
         /app/media/cacao_images/masks \
         /app/media/cacao_images/converted_jpg 2>/dev/null || true

wait_for_database() {
    if [ -n "${DB_HOST:-}" ]; then
        echo "⏳ Esperando a que la base de datos esté lista..."
        until nc -z "$DB_HOST" "${DB_PORT:-5432}"; do
            echo "   Base de datos no disponible, esperando..."
            sleep 1
        done
        log "✅ Base de datos disponible"
    fi
}

# Verificar que gunicorn está disponible
if ! python -m gunicorn --version > /dev/null 2>&1; then
    echo "⚠️  Gunicorn no encontrado, instalando..."
    pip install --user gunicorn
fi

run_management_command() {
    local command=$1
    shift
    log "📦 Ejecutando ${command}..."
    python manage.py "${command}" "$@"
}

if [[ "${ROLE}" == "web" ]]; then
    wait_for_database
    run_management_command migrate --noinput
    run_management_command collectstatic --noinput
    if [[ "${CREATE_DEFAULT_SUPERUSER:-true}" == "true" ]]; then
        log "👤 Asegurando superusuario predeterminado"
        python create_admin_user.py || log "⚠️ No se pudo crear el superusuario predeterminado"
    fi
    if [[ "${SEED_INITIAL_DATA:-true}" == "true" ]]; then
        log "🌱 Inicializando catálogos y datos base"
        run_management_command init_catalogos
        run_management_command seed_colombia
    fi
fi

case "${ROLE}" in
    web)
        log "✅ Iniciando servidor Gunicorn"
        exec "$@"
        ;;
    worker)
        wait_for_database
        log "✅ Iniciando Celery Worker"
        exec celery -A cacaoscan worker --loglevel=${CELERY_LOG_LEVEL:-info} --concurrency=${CELERY_CONCURRENCY:-4} --queues=${CELERY_QUEUES:-default}
        ;;
    beat)
        wait_for_database
        log "✅ Iniciando Celery Beat"
        exec celery -A cacaoscan beat --loglevel=${CELERY_LOG_LEVEL:-info} --scheduler=${CELERY_SCHEDULER:-celery.beat.PersistentScheduler}
        ;;
    *)
        log "✅ Ejecutando comando personalizado: $*"
        exec "$@"
        ;;
 esac
