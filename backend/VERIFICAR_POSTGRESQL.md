# Verificación de PostgreSQL antes de Ejecutar Tests

## 🔍 Verificar si PostgreSQL está Corriendo

### En Windows:

```cmd
# Verificar si el servicio está corriendo
sc query postgresql-x64-16
# O para otras versiones:
sc query | findstr postgres

# Verificar si responde en el puerto 5432
netstat -an | findstr 5432

# O intentar conectar con psql
psql -U postgres -h localhost -p 5432 -c "SELECT version();"
```

### En Linux/Mac:

```bash
# Verificar si está corriendo
sudo systemctl status postgresql
# O
pg_isready

# Verificar el puerto
sudo netstat -tulpn | grep 5432
# O
sudo lsof -i :5432
```

---

## 🚀 Iniciar PostgreSQL

### En Windows (servicio):

```cmd
# Iniciar el servicio
net start postgresql-x64-16

# O desde Services (services.msc)
# Buscar "postgresql" y hacer clic en "Start"
```

### En Linux/Mac:

```bash
# Iniciar el servicio
sudo systemctl start postgresql

# O con brew (Mac)
brew services start postgresql@16
```

---

## 📝 Verificar Variables de Entorno

Antes de ejecutar los tests, verifica que tu archivo `.env` tenga las credenciales correctas:

```bash
# Verificar las variables
cd backend
cat .env | grep -E "DB_|POSTGRES"
```

Debes ver algo como:

```
DB_NAME=cacaoscan_db
DB_USER=cacaoscan_user
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

---

## ✅ Test Rápido de Conexión

Antes de ejecutar pytest, puedes probar la conexión manualmente:

```python
# En Python (puedes ejecutar esto en el shell de Django)
python manage.py shell

# Luego en el shell:
from django.db import connection
connection.ensure_connection()
print("✅ Conexión exitosa!")
```

---

## 🧪 Ejecutar Tests con PostgreSQL

Una vez que PostgreSQL esté corriendo:

```bash
cd backend

# Ejecutar todos los tests
pytest

# O con más detalle
pytest -v

# O solo tests rápidos (sin los marcados como 'slow')
pytest -m "not slow"
```

---

## 🐳 Alternativa: Usar Docker Compose

Si prefieres usar Docker para PostgreSQL:

```bash
# Desde la raíz del proyecto
docker-compose up -d db

# Esperar a que esté listo
docker-compose ps

# Luego ejecutar tests
cd backend
pytest
```

---

## ⚠️ Solución de Problemas

### Error: "connection refused" o "could not connect"

1. **Verifica que PostgreSQL esté corriendo**:
   ```cmd
   # Windows
   sc query postgresql-x64-16
   
   # Si no está corriendo, inícialo:
   net start postgresql-x64-16
   ```

2. **Verifica las credenciales en `.env`**:
   - `DB_HOST` debe ser `localhost` (no `db`, eso es para Docker)
   - `DB_PORT` debe ser `5432` (o el puerto donde corre tu PostgreSQL)
   - `DB_USER` y `DB_PASSWORD` deben ser correctos

3. **Verifica que el usuario tenga permisos**:
   ```sql
   -- Conectarte como superusuario
   psql -U postgres
   
   -- Crear la base de datos si no existe
   CREATE DATABASE cacaoscan_db;
   
   -- Crear el usuario si no existe
   CREATE USER cacaoscan_user WITH PASSWORD 'tu_password';
   
   -- Dar permisos
   GRANT ALL PRIVILEGES ON DATABASE cacaoscan_db TO cacaoscan_user;
   ```

### Error: "database does not exist"

Los tests crearán automáticamente una base de datos con el nombre `test_cacaoscan_db` (o `test_` + el nombre de tu BD).

Pero necesitas que el usuario tenga permisos para **crear bases de datos**:

```sql
-- Conectarte como superusuario
psql -U postgres

-- Dar permisos para crear bases de datos
ALTER USER cacaoscan_user CREATEDB;
```

---

## 📋 Checklist Pre-Tests

- [ ] PostgreSQL está corriendo
- [ ] El puerto 5432 está disponible (o el configurado en `.env`)
- [ ] El archivo `.env` existe en `backend/.env`
- [ ] Las variables `DB_*` están configuradas correctamente
- [ ] El usuario de BD tiene permisos (al menos para conectarse)
- [ ] El usuario tiene permisos para crear bases de datos (para tests)

---

## 🎯 Comando Todo-en-Uno (Windows)

```cmd
@echo off
echo Verificando PostgreSQL...
sc query postgresql-x64-16 | findstr RUNNING
if errorlevel 1 (
    echo PostgreSQL no esta corriendo. Iniciando...
    net start postgresql-x64-16
    timeout /t 5
)

echo Ejecutando tests...
cd backend
pytest --tb=short
```

Guarda esto como `run_tests.bat` y ejecútalo cuando quieras correr los tests.

