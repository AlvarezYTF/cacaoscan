# ========================================
# Dockerfile Multistage para Backend Django de CacaoScan
# ========================================

FROM python:3.13-slim AS builder

ARG APP_VERSION=v1.3.0

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_CONNECT_TIMEOUT=60

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libgif-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    libpq-dev \
    libtiff5-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar solo requirements.txt primero para aprovechar el cache de Docker
# Si requirements.txt no cambia, esta capa se cachea y no reinstala dependencias
COPY requirements.txt ./

# Instalar dependencias (esta capa se cachea si requirements.txt no cambia)
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ========================================
# Etapa 2: Runtime base
# ========================================
FROM python:3.13-slim AS runtime-base

ARG APP_VERSION=v1.3.0

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/opt/venv/bin:$PATH \
    APP_VERSION=${APP_VERSION}

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libfontconfig1 \
    libfreetype6 \
    libgif7 \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libjpeg62-turbo \
    libpng16-16 \
    libpq5 \
    libsm6 \
    libtiff6 \
    libwebp7 \
    libxext6 \
    libxrender1 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system appgroup \
    && useradd --system --gid appgroup --create-home --shell /bin/bash appuser \
    && mkdir -p /app /app/logs /var/www/staticfiles /var/www/media /var/log/cacaoscan /tmp/cacaoscan \
    && chown -R appuser:appgroup /app /var/www /var/log/cacaoscan /tmp/cacaoscan

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

COPY . .

# Crear directorios necesarios para la aplicación
RUN mkdir -p staticfiles logs \
    media/logs \
    media/datasets \
    media/reportes \
    media/cacao_images/raw \
    media/cacao_images/crops \
    media/cacao_images/crops_runtime \
    media/cacao_images/processed \
    media/cacao_images/masks \
    media/cacao_images/converted_jpg

# Script de inicio - convertir finales de línea Windows (CRLF) a Unix (LF)
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

# Render inyecta PORT automáticamente (puede ser 10000 u otro)
# Exponemos múltiples puertos comunes que Render puede usar
EXPOSE 8000 10000

# Usar el entrypoint para ejecutar migraciones antes de iniciar Gunicorn
ENTRYPOINT ["/docker-entrypoint.sh"]

# HEALTHCHECK para que Render detecte el servicio correctamente
# Render inyecta PORT, pero en HEALTHCHECK puede no estar disponible, usar 10000 como fallback
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD sh -c 'curl -f http://localhost:${PORT:-10000}/health || curl -f http://localhost:10000/health || exit 1'

# No establecer PORT por defecto, Render lo inyectará
# El entrypoint ejecutará este comando después de las migraciones
CMD ["sh", "-c", "gunicorn cacaoscan.wsgi:application --bind 0.0.0.0:${PORT} --workers 2 --timeout 300 --graceful-timeout 60"]

