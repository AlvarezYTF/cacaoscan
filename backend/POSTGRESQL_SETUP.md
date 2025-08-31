# Configuración de PostgreSQL para CacaoScan

Esta guía te ayudará a configurar PostgreSQL para el proyecto CacaoScan.

## 📋 Prerequisitos

### 1. Instalar PostgreSQL

#### Windows:
```bash
# Descargar desde: https://www.postgresql.org/download/windows/
# O usar Chocolatey:
choco install postgresql

# O usar Scoop:
scoop install postgresql
```

#### macOS:
```bash
# Usar Homebrew:
brew install postgresql
brew services start postgresql
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 2. Verificar instalación
```bash
psql --version
# Debería mostrar: psql (PostgreSQL) 15.x o superior
```

## 🚀 Configuración Rápida

### Opción A: Script Automático (Recomendado)

1. **Ejecutar script de configuración de base de datos:**
```bash
# Como usuario postgres (Linux/macOS)
sudo -u postgres psql -f setup_database.sql

# Windows (como administrador)
psql -U postgres -f setup_database.sql
```

2. **Ejecutar script de configuración de desarrollo:**
```bash
python setup_dev.py
```

### Opción B: Configuración Manual

#### 1. Crear usuario y base de datos
```sql
-- Conectar como superusuario
psql -U postgres

-- Crear usuario
CREATE USER cacaoscan_user WITH PASSWORD 'cacaoscan_pass';

-- Crear base de datos
CREATE DATABASE cacaoscan_db WITH 
    OWNER cacaoscan_user
    ENCODING 'UTF8'
    LC_COLLATE = 'es_ES.UTF-8'
    LC_CTYPE = 'es_ES.UTF-8'
    TEMPLATE template0;

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE cacaoscan_db TO cacaoscan_user;

-- Salir
\q
```

#### 2. Configurar Django
```bash
# Crear y aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

## ⚙️ Configuración de Conexión

### Variables de entorno recomendadas:
```bash
# Database
DB_NAME=cacaoscan_db
DB_USER=cacaoscan_user
DB_PASSWORD=cacaoscan_pass
DB_HOST=localhost
DB_PORT=5432
```

### settings.py ya configurado:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cacaoscan_db',
        'USER': 'cacaoscan_user',
        'PASSWORD': 'cacaoscan_pass',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'prefer',
        },
    }
}
```

## 🧪 Usuarios de Prueba

El script `setup_dev.py` crea automáticamente:

### Administrador:
- **Email:** admin@cacaoscan.com
- **Password:** admin123
- **Rol:** Administrador

### Agricultores:
- **Email:** agricultor1@finca.com / agricultor2@finca.com
- **Password:** test123
- **Rol:** Agricultor

### Analista:
- **Email:** analista@cacaoscan.com
- **Password:** test123
- **Rol:** Analista

## 🔍 Verificación

### 1. Verificar conexión a la base de datos:
```bash
python manage.py dbshell
```

### 2. Verificar migraciones:
```bash
python manage.py showmigrations
```

### 3. Probar endpoints de autenticación:
```bash
# Iniciar servidor
python manage.py runserver

# Probar login (en otra terminal)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@cacaoscan.com","password":"admin123"}'
```

## 🛠️ Solución de Problemas

### Error: "role 'cacaoscan_user' does not exist"
```bash
# Verificar que el usuario existe
sudo -u postgres psql -c "\du"

# Si no existe, crear manualmente:
sudo -u postgres psql -f setup_database.sql
```

### Error: "database 'cacaoscan_db' does not exist"
```bash
# Verificar que la base de datos existe
sudo -u postgres psql -l | grep cacaoscan

# Si no existe, crear manualmente:
sudo -u postgres createdb -O cacaoscan_user cacaoscan_db
```

### Error de conexión: "could not connect to server"
```bash
# Verificar que PostgreSQL está ejecutándose
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS
sc query postgresql-x64-15  # Windows
```

### Error: "peer authentication failed"
```bash
# Editar pg_hba.conf para permitir autenticación por password
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Cambiar la línea:
# local   all             all                                     peer
# Por:
# local   all             all                                     md5

# Reiniciar PostgreSQL
sudo systemctl restart postgresql
```

## 📊 Comandos Útiles de PostgreSQL

```bash
# Conectar a la base de datos
psql -h localhost -U cacaoscan_user -d cacaoscan_db

# Ver tablas
\dt

# Ver usuarios
\du

# Ver bases de datos
\l

# Ver estructura de una tabla
\d apps_users_user

# Salir
\q
```

## 🚀 URLs Importantes

Una vez configurado:

- **Admin Django:** http://localhost:8000/admin/
- **API Documentation:** http://localhost:8000/api/docs/
- **Auth Endpoints:** http://localhost:8000/api/auth/
- **Prediction API:** http://localhost:8000/api/images/predict/

## 🔐 Seguridad en Producción

Para producción, asegúrate de:

1. **Cambiar credenciales por defecto**
2. **Usar variables de entorno**
3. **Configurar SSL/TLS**
4. **Restringir acceso de red**
5. **Configurar backups automáticos**

## 📞 Soporte

Si tienes problemas con la configuración:

1. Verifica que PostgreSQL esté instalado y ejecutándose
2. Ejecuta `python manage.py check` para validar la configuración
3. Revisa los logs de PostgreSQL y Django
4. Usa el script `setup_dev.py` para configuración automática
