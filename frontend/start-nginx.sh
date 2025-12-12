#!/bin/sh
set -e

# Puerto interno del contenedor (evita conflictos con otros servicios)
PORT=${PORT:-18081}

# Reemplazar el puerto en nginx.conf dinámicamente
sed -i "s/listen 18081;/listen ${PORT};/g" /etc/nginx/conf.d/default.conf

# Inyectar API_BASE_URL en runtime si está disponible
# Esto permite que la URL del API se configure dinámicamente sin rebuild
# Prioridad: RUNTIME_API_BASE_URL > VITE_API_BASE_URL (build-time)
API_URL="${RUNTIME_API_BASE_URL:-${VITE_API_BASE_URL:-}}"
CONFIG_SCRIPT="/usr/share/nginx/html/config.js"

if [ -n "${API_URL}" ]; then
    # Escribir configuración en el archivo (ya existe con permisos correctos)
    # Agregar logging para debug
    cat > "$CONFIG_SCRIPT" << EOF
// Runtime API configuration injected by start-nginx.sh
window.__API_BASE_URL__ = '${API_URL}';
console.log('✅ [Config] Runtime API URL injected:', window.__API_BASE_URL__);
EOF
    if [ $? -eq 0 ]; then
        echo "✅ API Base URL configurada en runtime: ${API_URL}"
    else
        echo "⚠️ No se pudo escribir config.js, usando build-time URL"
    fi
else
    # Mantener contenido por defecto si no hay URL configurada
    cat > "$CONFIG_SCRIPT" << EOF
// No runtime API URL configured, using build-time or default
console.warn('⚠️ [Config] No runtime API URL configured');
EOF
    echo "⚠️ No se encontró API_URL, usando build-time o default"
fi

# Iniciar nginx
exec nginx -g 'daemon off;'

