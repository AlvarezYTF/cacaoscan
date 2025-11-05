#!/bin/bash
set -e

echo "🚀 Iniciando CacaoScan Backend..."

# Asegurar que el PATH incluya los binarios de usuario
export PATH="/root/.local/bin:$PATH"

# Optimizar pkg_resources para evitar escaneo excesivo de archivos
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Configurar pkg_resources para que no escanee directorios problemáticos
# Esto reduce significativamente el uso de memoria
export PKG_RESOURCES_CACHE_DIR=/tmp/pkg_resources_cache
mkdir -p "$PKG_RESOURCES_CACHE_DIR" 2>/dev/null || true

# Crear directorios necesarios para la aplicación
mkdir -p /app/logs /app/media/logs /app/staticfiles 2>/dev/null || true

# Verificar que gunicorn está disponible
if ! python -m gunicorn --version > /dev/null 2>&1; then
    echo "⚠️  Gunicorn no encontrado, instalando..."
    pip install --user gunicorn
fi

# Esperar a que la base de datos esté lista
if [ -n "$DB_HOST" ]; then
    echo "⏳ Esperando a que la base de datos esté lista..."
    until nc -z "$DB_HOST" "${DB_PORT:-5432}"; do
        echo "   Base de datos no disponible, esperando..."
        sleep 1
    done
    echo "✅ Base de datos disponible"
fi

# Ejecutar migraciones (con manejo de errores mejorado)
echo "📦 Ejecutando migraciones..."
python manage.py migrate --noinput 2>&1 || {
    echo "⚠️  Error en migraciones (continuando...)"
    # No detener si hay error en migraciones
}

# Recopilar archivos estáticos (con manejo de errores mejorado)
echo "📦 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput 2>&1 || {
    echo "⚠️  Error al recopilar estáticos (continuando...)"
    # No detener si hay error en collectstatic
}

# Ejecutar comando
echo "✅ Iniciando servidor..."
# Detectar el tipo de comando a ejecutar
if [ "$1" = "celery" ]; then
    # Comando de Celery (worker o beat)
    echo "Iniciando Celery..."
    exec "$@"
elif [ "$1" = "python" ] && [ "$2" = "-m" ] && [ "$3" = "gunicorn" ]; then
    # Comando de Gunicorn explícito
    exec "$@"
else
    # Usar python -m gunicorn por defecto para el backend
    exec python -m gunicorn cacaoscan.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
fi
