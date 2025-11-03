# ========================================
# Dockerfile Multistage para Frontend Vue 3 + Vite de CacaoScan
# ========================================

# ========================================
# Etapa 1: Builder - Build de la aplicación
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
# Usar variable de entorno para la URL de la API
ARG VITE_API_BASE_URL=http://backend:8000/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN pnpm build

# ========================================
# Etapa 2: Runtime - Nginx para servir la aplicación
# ========================================
FROM nginx:alpine AS runtime

# Copiar archivos construidos desde la etapa de build
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuración personalizada de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
