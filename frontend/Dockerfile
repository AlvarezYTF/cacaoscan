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
USER 101

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8080/health || exit 1

CMD ["/usr/sbin/nginx", "-g", "daemon off;"]
