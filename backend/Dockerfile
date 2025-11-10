# ========================================
# Dockerfile Multistage para Backend Django de CacaoScan
# ========================================

FROM python:3.11-slim AS builder

ARG APP_VERSION=v1.3.0

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_CONNECT_TIMEOUT=60

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    libgif-dev \
    libfreetype6-dev \
    libtiff5-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ========================================
# Etapa 2: Runtime base
# ========================================
FROM python:3.11-slim AS runtime-base

ARG APP_VERSION=v1.3.0

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/opt/venv/bin:$PATH \
    APP_VERSION=${APP_VERSION}

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo \
    libpng16-16 \
    libgif7 \
    libfreetype6 \
    libtiff6 \
    libwebp7 \
    libfontconfig1 \
    libxrender1 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libgomp1 \
    netcat-openbsd \
    curl \
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

EXPOSE 8000

CMD ["gunicorn", "cacaoscan.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]

# ========================================
# Etapa 4: Celery (worker/beat)
# ========================================
FROM runtime-base AS celery

ENV SERVICE_ROLE=worker \
    C_FORCE_ROOT=0

CMD ["celery", "-A", "cacaoscan", "worker", "--loglevel=info", "--concurrency=4"]
