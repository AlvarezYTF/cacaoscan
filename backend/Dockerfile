# ========================================
# Dockerfile Multistage para Backend Django de CacaoScan
# ========================================

FROM python:3.12-slim AS builder

ARG APP_VERSION=v1.3.0

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=300 \
    PIP_CONNECT_TIMEOUT=60 \
    PIP_RETRIES=5

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
# torch/torchvision (~280 MB) se instalan primero con loop de reintento a nivel shell:
# pip --retries no cubre IncompleteRead (error mid-stream), solo fallos de conexión inicial.
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && installed=0 \
    && for i in 1 2 3 4 5; do \
         if /opt/venv/bin/pip install --no-cache-dir \
              torch==2.5.1 torchvision==0.20.1 \
              --index-url https://download.pytorch.org/whl/cpu; \
         then installed=1 && break; fi; \
         echo "Intento $i/5 fallido"; \
         [ "$i" -lt 5 ] && sleep 15; \
       done \
    && [ "$installed" = "1" ] \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt \
    && /opt/venv/bin/pip uninstall -y opencv-python opencv-contrib-python 2>/dev/null || true

# ========================================
# Etapa 2: Runtime base
# ========================================
FROM python:3.12-slim AS runtime-base

ARG APP_VERSION=v1.3.0

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/opt/venv/bin:$PATH \
    APP_VERSION=${APP_VERSION}

# Runtime libs mínimas:
# - opencv-python-headless requiere libglib2.0-0; los libs X11/GL (libgl1, libsm6,
#   libxext6, libxrender1) NO se necesitan porque usamos la build headless.
# - matplotlib necesita libfontconfig1 para renderizar texto; freetype va bundle en su wheel.
# - Pillow trae libjpeg/libpng/libtiff/libwebp/libgif en su wheel manylinux, así que no
#   se instalan las versiones de sistema.
# - libgomp1 lo requieren scikit-learn / numpy para OpenMP.
# - libpq5 para psycopg2-binary; netcat-openbsd para el wait-for del entrypoint.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libfontconfig1 \
    libglib2.0-0 \
    libgomp1 \
    libpq5 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system appgroup \
    && useradd --system --gid appgroup --create-home --shell /bin/bash appuser \
    && mkdir -p /app /app/logs /var/www/staticfiles /var/www/media /var/log/cacaoscan /tmp/cacaoscan \
    && chown -R appuser:appgroup /app /var/www /var/log/cacaoscan /tmp/cacaoscan

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

# Copy application code explicitly to prevent copying sensitive data
# SECURITY: Copy only necessary application directories and files
# .dockerignore provides additional protection, but explicit copying is safer
# This prevents accidentally copying credentials, local configs, or other sensitive data
COPY ["manage.py", "/app/manage.py"]
COPY ["runtime.txt", "/app/runtime.txt"]
COPY ["pytest.ini", "/app/pytest.ini"]
# Copy Django project configuration
COPY cacaoscan/ ./cacaoscan/
# Copy all Django applications
COPY api/ ./api/
COPY audit/ ./audit/
COPY auth_app/ ./auth_app/
COPY catalogos/ ./catalogos/
COPY core/ ./core/
COPY fincas_app/ ./fincas_app/
COPY images_app/ ./images_app/
COPY legal/ ./legal/
COPY ml/ ./ml/
COPY notifications/ ./notifications/
COPY personas/ ./personas/
COPY reports/ ./reports/
COPY training/ ./training/
COPY users/ ./users/

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
    media/cacao_images/converted_jpg \
    && chown -R appuser:appgroup /app /opt/venv

# Script de inicio - convertir finales de línea Windows (CRLF) a Unix (LF)
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh && \
    chown appuser:appgroup /docker-entrypoint.sh

# Change to non-privileged user before running the application
USER appuser

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

# ========================================
# Aliases para CI: tags distintos comparten el mismo runtime.
# El comando final lo sobrescribe docker-compose / k8s.
# ========================================
FROM runtime-base AS backend

FROM runtime-base AS celery
CMD ["celery", "-A", "cacaoscan", "worker", "--loglevel=info", "--concurrency=4", "--max-tasks-per-child=1"]

