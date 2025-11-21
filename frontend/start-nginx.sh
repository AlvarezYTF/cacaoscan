#!/bin/sh
set -e

# Render inyecta PORT automáticamente, usar esa variable si está disponible
PORT=${PORT:-8080}

# Reemplazar el puerto en nginx.conf dinámicamente
sed -i "s/listen 8080;/listen ${PORT};/g" /etc/nginx/conf.d/default.conf

# Iniciar nginx
exec nginx -g 'daemon off;'

