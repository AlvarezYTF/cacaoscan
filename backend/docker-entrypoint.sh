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

# Función para esperar a que la base de datos esté lista
wait_for_database() {
    if [ -n "${DB_HOST:-}" ]; then
        log "⏳ Esperando a que la base de datos esté lista..."
        until nc -z "${DB_HOST}" "${DB_PORT:-5432}"; do
            log "   Base de datos no disponible, esperando..."
            sleep 1
        done
        log "✅ Base de datos disponible"
    fi
}

run_management_command() {
    local command=$1
    shift
    log "📦 Ejecutando ${command}..."
    python manage.py "${command}" "$@"
}

if [[ "${ROLE}" == "web" ]]; then
    wait_for_database
    # Ejecutar todas las migraciones, incluyendo las de apps de terceros como token_blacklist
    log "📦 Ejecutando migraciones de todas las apps..."
    run_management_command migrate --noinput
    
    # Asegurar que las migraciones de token_blacklist se ejecuten explícitamente
    log "📦 Verificando migraciones de token_blacklist..."
    if python manage.py migrate token_blacklist --noinput 2>&1 | grep -q "No migrations to apply"; then
        log "✅ Migraciones de token_blacklist ya aplicadas"
    elif python manage.py migrate token_blacklist --noinput; then
        log "✅ Migraciones de token_blacklist aplicadas exitosamente"
    else
        log "⚠️ Error aplicando migraciones de token_blacklist, continuando..."
    fi
    
    # Ejecutar collectstatic limpiando primero para regenerar el manifest correctamente
    log "📦 Recolectando archivos estáticos..."
    run_management_command collectstatic --noinput --clear
    log "✅ Archivos estáticos recolectados"
    if [[ "${CREATE_DEFAULT_SUPERUSER:-true}" == "true" ]]; then
        log "👤 Asegurando superusuario predeterminado"
        run_management_command create_admin_user || log "⚠️ No se pudo crear el superusuario predeterminado"
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
    *)
        log "✅ Ejecutando comando personalizado: $*"
        exec "$@"
        ;;
esac
