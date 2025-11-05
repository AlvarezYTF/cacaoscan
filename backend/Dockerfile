# ========================================
# Dockerfile Multistage para Backend Django de CacaoScan
# ========================================

# ========================================
# Etapa 1: Builder - Instalación de dependencias
# ========================================
FROM python:3.11-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_CONNECT_TIMEOUT=60

# Instalar dependencias del sistema necesarias para compilar paquetes
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

# Copiar y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip --default-timeout=100 --retries=5 && \
    pip install --user -r requirements.txt --default-timeout=100 --retries=5

# ========================================
# Etapa 2: Runtime - Imagen final
# ========================================
FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Instalar solo dependencias runtime necesarias
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
    libxrender-dev \
    libgomp1 \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /root/.local

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p staticfiles logs media/logs media/cacao_images media/datasets media/reportes

# Script de inicio - convertir finales de línea Windows (CRLF) a Unix (LF)
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r$//' /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["python", "-m", "gunicorn", "cacaoscan.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
