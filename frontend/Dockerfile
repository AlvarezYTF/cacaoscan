# ========================================
# Dockerfile Multistage para Frontend Vue 3 + Vite de CacaoScan
# ========================================

FROM node:20-alpine AS builder

WORKDIR /app

# Copiar archivos de dependencias
# Use specific file names instead of glob patterns to prevent copying sensitive files
COPY package.json ./
COPY pnpm-lock.yaml ./

# Instalar pnpm y dependencias
# SECURITY: Use corepack (included with Node.js 20) to enable pnpm instead of npm install -g
# This avoids the security risk of executing arbitrary scripts during package installation.
# Corepack is the official package manager manager from Node.js and doesn't execute user scripts.
RUN corepack enable && \
    corepack prepare pnpm@latest --activate && \
    pnpm install --frozen-lockfile --ignore-scripts || pnpm install --ignore-scripts

# Copiar únicamente los archivos necesarios para el build (evita copiar
# todo el contexto y posibles ficheros sensibles). `.dockerignore` ya
# excluye archivos/dirs sensibles, pero ser explícitos aquí reduce riesgo.
# Solo copiar archivos de configuración necesarios para el build, no archivos de test o desarrollo
COPY index.html vite.config.js tailwind.config.js ./
COPY public/ ./public/
COPY src/ ./src/

# Construir aplicación para producción
# Usar variable de entorno para la URL de la API (se inyecta desde docker-compose)
# El build ya toma la variable desde el entorno, no es necesario declararla aquí
RUN pnpm build

# ========================================
# Etapa Runtime - Nginx sin root
# ========================================
FROM nginxinc/nginx-unprivileged:1.25-alpine AS runtime

ARG APP_VERSION=v1.3.0

ENV APP_VERSION=${APP_VERSION}

USER root
RUN apk add --no-cache curl

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY start-nginx.sh /start-nginx.sh

# Crear archivo config.js, propiedad de UID 101 (nginx). No otorgar permisos
# de escritura a 'others' to avoid loosening filesystem permissions.
# start-nginx.sh runs as user 101 and will update this file at runtime.
RUN touch /usr/share/nginx/html/config.js && \
    chown 101:101 /usr/share/nginx/html/config.js && \
    chmod 644 /usr/share/nginx/html/config.js && \
    echo "// Runtime API configuration will be injected here" > /usr/share/nginx/html/config.js && \
    chmod +x /start-nginx.sh

USER 101

# Puerto interno del contenedor (evita conflictos con otros servicios)
ENV PORT=18081

EXPOSE 18081

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS http://127.0.0.1:${PORT:-18081}/health || exit 1

CMD ["/start-nginx.sh"]
