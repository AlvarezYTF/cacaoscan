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

log "🚀 Iniciando CacaoScan (${ROLE})..."

# Crear directorios necesarios (ya corremos como appuser)
mkdir -p "$STATIC_ROOT" "$MEDIA_ROOT" /tmp/cacaoscan /app/logs

wait_for_database() {
    local elapsed=0
    if [[ -z "${DB_HOST:-}" ]]; then
        log "⚠️  Variable DB_HOST no definida; se omite espera activa"
        return
    fi
    log "⏳ Esperando a la base de datos ${DB_HOST}:${DB_PORT:-5432}..."
    until nc -z "${DB_HOST}" "${DB_PORT:-5432}"; do
        sleep 2
        elapsed=$((elapsed + 2))
        if (( elapsed >= DB_WAIT_TIMEOUT )); then
            log "❌ Tiempo de espera alcanzado al conectar con la base de datos"
            exit 1
        fi
    done
    log "✅ Base de datos disponible"
}

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
