-- Script de configuración de PostgreSQL para CacaoScan
-- Ejecutar como superusuario de PostgreSQL

-- Crear usuario para CacaoScan
CREATE USER cacaoscan_user WITH PASSWORD 'cacaoscan_pass';

-- Crear base de datos
CREATE DATABASE cacaoscan_db WITH 
    OWNER cacaoscan_user
    ENCODING 'UTF8'
    LC_COLLATE = 'es_ES.UTF-8'
    LC_CTYPE = 'es_ES.UTF-8'
    TEMPLATE template0;

-- Otorgar privilegios al usuario
GRANT ALL PRIVILEGES ON DATABASE cacaoscan_db TO cacaoscan_user;

-- Conectar a la base de datos y otorgar privilegios en el schema
\c cacaoscan_db;

-- Otorgar privilegios en el schema public
GRANT ALL ON SCHEMA public TO cacaoscan_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cacaoscan_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cacaoscan_user;

-- Configurar privilegios por defecto para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cacaoscan_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO cacaoscan_user;

-- Crear extensiones útiles para machine learning y análisis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- Mostrar información de la configuración
\l cacaoscan_db
\du cacaoscan_user

-- Mensaje de confirmación
SELECT 'Base de datos cacaoscan_db configurada exitosamente para el usuario cacaoscan_user' AS status;
