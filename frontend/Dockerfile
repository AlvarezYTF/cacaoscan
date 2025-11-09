# ========================================
# Dockerfile Multistage para Frontend Vue 3 + Vite de CacaoScan
# ========================================

FROM node:20-alpine AS builder

ARG VITE_API_BASE_URL=http://backend:8000/api/v1

ENV PNPM_HOME=/home/node/.local/share/pnpm \
    VITE_API_BASE_URL=${VITE_API_BASE_URL}
ENV PATH="$PNPM_HOME:$PATH"

RUN apk add --no-cache libc6-compat \
    && npm install -g pnpm@9

USER node
WORKDIR /app

COPY --chown=node:node package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY --chown=node:node . .
RUN pnpm build \
    && pnpm store prune \
    && rm -rf node_modules

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
