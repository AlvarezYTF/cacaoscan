# 🗄️ Configuración de Base de Datos PostgreSQL - CacaoScan

## 📋 Instrucciones de Configuración

### 1. Instalar PostgreSQL

#### Windows:
```bash
# Descargar desde: https://www.postgresql.org/download/windows/
# O usar chocolatey:
choco install postgresql
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### macOS:
```bash
# Usando Homebrew:
brew install postgresql
```

### 2. Crear Base de Datos

```bash
# Conectar a PostgreSQL como superusuario
sudo -u postgres psql

# Crear base de datos
CREATE DATABASE cacaoscan_db;

# Crear usuario (opcional)
CREATE USER cacaoscan_user WITH PASSWORD 'tu_password_seguro';

# Dar permisos al usuario
GRANT ALL PRIVILEGES ON DATABASE cacaoscan_db TO cacaoscan_user;

# Salir
\q
```

### 3. Configurar Variables de Entorno

#### Crear archivo `.env` en el directorio `backend/`:

```bash
# Copiar el archivo de ejemplo
cp backend/env.example backend/.env
```

#### Editar `backend/.env` con tus datos:

```env
# ===========================
# Configuración de Base de Datos PostgreSQL
# ===========================
DB_NAME=cacaoscan_db
DB_USER=postgres
DB_PASSWORD=tu_password_aqui
DB_HOST=localhost
DB_PORT=5432

# ===========================
# Configuración de Django
# ===========================
SECRET_KEY=tu-secret-key-muy-seguro-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 4. Instalar Dependencias

```bash
# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt
```

### 5. Ejecutar Migraciones

```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear Superusuario (Opcional)

```bash
python manage.py createsuperuser
```

## 🔧 Configuración de Producción

### Variables de Entorno Recomendadas:

```env
# Base de Datos
DB_NAME=cacaoscan_production
DB_USER=cacaoscan_user
DB_PASSWORD=password_muy_seguro
DB_HOST=tu-servidor-postgresql.com
DB_PORT=5432

# Django
SECRET_KEY=secret-key-muy-largo-y-seguro-para-produccion
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# CORS
CORS_ALLOWED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com
```

## 🐛 Solución de Problemas

### Error: "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### Error: "database does not exist"
```bash
# Crear la base de datos en PostgreSQL
sudo -u postgres createdb cacaoscan_db
```

### Error: "permission denied"
```bash
# Dar permisos al usuario
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE cacaoscan_db TO tu_usuario;
```

### Error: "connection refused"
```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql
# o en Windows:
services.msc -> PostgreSQL
```

## 📊 Verificar Conexión

```bash
cd backend
python manage.py dbshell
```

## 🔒 Seguridad

1. **Nunca** commitees el archivo `.env` al repositorio
2. Usa contraseñas seguras para producción
3. Configura SSL para conexiones remotas
4. Usa variables de entorno en el servidor de producción

## 📝 Notas Importantes

- El archivo `.env` debe estar en `backend/.env`
- Las variables de entorno tienen prioridad sobre los valores por defecto
- Para desarrollo local, puedes usar `localhost` como host
- Para producción, usa el host de tu servidor PostgreSQL
