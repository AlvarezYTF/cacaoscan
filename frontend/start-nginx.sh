#!/bin/sh
set -e

# Render inyecta PORT automáticamente, usar esa variable si está disponible
PORT=${PORT:-8080}

# Reemplazar el puerto en nginx.conf dinámicamente
sed -i "s/listen 8080;/listen ${PORT};/g" /etc/nginx/conf.d/default.conf

# Inyectar API_BASE_URL en runtime si está disponible
# Esto permite que la URL del API se configure dinámicamente sin rebuild
# Prioridad: RUNTIME_API_BASE_URL > VITE_API_BASE_URL (build-time)
API_URL="${RUNTIME_API_BASE_URL:-${VITE_API_BASE_URL:-}}"
CONFIG_SCRIPT="/usr/share/nginx/html/config.js"

if [ -n "${API_URL}" ]; then
    # Escribir configuración en el archivo (ya existe con permisos correctos)
    echo "window.__API_BASE_URL__ = '${API_URL}';" > "$CONFIG_SCRIPT" 2>/dev/null || {
        # Si falla, intentar con printf (más compatible)
        printf "window.__API_BASE_URL__ = '%s';\n" "${API_URL}" > "$CONFIG_SCRIPT" 2>/dev/null || {
            echo "⚠️ No se pudo escribir config.js, usando build-time URL"
        }
    }
    echo "✅ API Base URL configurada: ${API_URL}"
else
    # Mantener contenido por defecto si no hay URL configurada
    echo "// No runtime API URL configured, using build-time or default" > "$CONFIG_SCRIPT" 2>/dev/null || true
fi

# Iniciar nginx
exec nginx -g 'daemon off;'

