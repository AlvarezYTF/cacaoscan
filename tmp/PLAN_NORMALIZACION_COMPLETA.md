# Plan de Normalización Completa - CacaoScan

## Resumen de Violaciones Detectadas

### 1. Tablas Duplicadas

#### 1.1 UserProfile
- `api_userprofile` (obsoleta)
- `auth_app_userprofile` (activa, normalizada)
- **Acción**: Eliminar `api_userprofile`, migrar datos a `auth_app_userprofile`

#### 1.2 Finca/Lote
- `api_finca` / `api_lote` (obsoletas, con campos texto)
- `fincas_app_finca` / `fincas_app_lote` (activas, normalizadas)
- **Acción**: Eliminar `api_finca` y `api_lote`, migrar datos a `fincas_app`

#### 1.3 CacaoImage/CacaoPrediction
- `api_cacaoimage` / `api_cacaoprediction` (obsoletas, con campos texto)
- `images_app_cacaoimage` / `images_app_cacaoprediction` (activas, normalizadas)
- **Acción**: Eliminar `api_cacaoimage` y `api_cacaoprediction`, migrar datos a `images_app`

#### 1.4 EmailVerificationToken
- `api_emailverificationtoken` (obsoleta)
- `auth_app_emailverificationtoken` (activa)
- **Acción**: Eliminar `api_emailverificationtoken`, migrar datos a `auth_app`

#### 1.5 TrainingJob
- `api_trainingjob` (obsoleta)
- `training_trainingjob` (activa)
- **Acción**: Eliminar `api_trainingjob`, migrar datos a `training`

### 2. Campos de Texto que Deben Ser ForeignKeys

#### 2.1 Persona
- `departamento_id` → Eliminar (dependencia transitiva, ya está en `municipio.departamento`)

#### 2.2 ReporteGenerado
- `tipo_reporte` → Crear catálogo `TipoReporte`
- `formato` → Crear catálogo `FormatoReporte`
- `estado` → Crear catálogo `EstadoReporte`

#### 2.3 ActivityLog
- `resource_type` y `resource_id` → Mantener como está (polimórfico, no se puede FK)

### 3. Dependencias Transitivas

#### 3.1 Persona
- `departamento_id` → Eliminar (ya está en `municipio.departamento`)

### 4. JSONB Normalización

#### 4.1 PendingEmailVerification
- `temp_data` → Revisar si contiene datos tabulares, si es así normalizar

## Plan de Implementación

### Fase 1: Crear Catálogos Faltantes
1. Crear `TipoReporte`
2. Crear `FormatoReporte`
3. Crear `EstadoReporte`

### Fase 2: Migrar Datos de Tablas Duplicadas
1. Migrar `api_userprofile` → `auth_app_userprofile`
2. Migrar `api_finca` → `fincas_app_finca`
3. Migrar `api_lote` → `fincas_app_lote`
4. Migrar `api_cacaoimage` → `images_app_cacaoimage`
5. Migrar `api_cacaoprediction` → `images_app_cacaoprediction`
6. Migrar `api_emailverificationtoken` → `auth_app_emailverificationtoken`
7. Migrar `api_trainingjob` → `training_trainingjob`

### Fase 3: Normalizar Campos
1. Normalizar `ReporteGenerado`: convertir `tipo_reporte`, `formato`, `estado` a FKs
2. Eliminar `Persona.departamento_id`

### Fase 4: Eliminar Tablas Obsoletas
1. Eliminar todas las tablas `api_*` duplicadas

### Fase 5: Actualizar Referencias
1. Actualizar todos los imports y referencias en el código
2. Actualizar serializers, views, admin, etc.

