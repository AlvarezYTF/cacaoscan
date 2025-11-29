# ========================================
# Dockerfile Multistage para Frontend Vue 3 + Vite de CacaoScan
# ========================================

FROM node:20-alpine AS builder

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./
COPY pnpm-lock.yaml* ./

# Instalar pnpm y dependencias
RUN npm install -g pnpm && \
    pnpm install --frozen-lockfile || pnpm install

# Copiar código fuente
COPY . .

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

# Crear archivo config.js con permisos de escritura para el usuario 101 (nginx)
# Este archivo será actualizado en runtime por start-nginx.sh
RUN touch /usr/share/nginx/html/config.js && \
    chown 101:101 /usr/share/nginx/html/config.js && \
    chmod 666 /usr/share/nginx/html/config.js && \
    echo "// Runtime API configuration will be injected here" > /usr/share/nginx/html/config.js && \
    chmod +x /start-nginx.sh

USER 101

# Render inyecta PORT automáticamente
ENV PORT=8080

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS http://127.0.0.1:${PORT:-8080}/health || exit 1

CMD ["/start-nginx.sh"]
