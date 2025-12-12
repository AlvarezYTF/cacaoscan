# Plan de Migración: Unificación de Catálogos

## 1. ANÁLISIS DEL IMPACTO EN LA BASE DE DATOS

### 1.1. Catálogos a Migrar

Los siguientes catálogos serán convertidos a temas + parámetros:

| Catálogo Actual | Tabla | Tema Código | Tema Nombre |
|----------------|-------|-------------|-------------|
| Clima | `catalogos_clima` | `TEMA_CLIMA` | Tipo de Clima |
| EstadoFinca | `catalogos_estadofinca` | `TEMA_ESTADO_FINCA` | Estado de Finca |
| EstadoLote | `catalogos_estadolote` | `TEMA_ESTADO_LOTE` | Estado de Lote |
| EstadoReporte | `catalogos_estadoreporte` | `TEMA_ESTADO_REPORTE` | Estado de Reporte |
| FormatoReporte | `catalogos_formatoreporte` | `TEMA_FORMATO_REPORTE` | Formato de Reporte |
| TipoArchivo | `catalogos_tipoarchivo` | `TEMA_TIPO_ARCHIVO` | Tipo de Archivo |
| TipoDispositivo | `catalogos_tipodispositivo` | `TEMA_TIPO_DISPOSITIVO` | Tipo de Dispositivo |
| TipoNotificacion | `catalogos_tiponotificacion` | `TEMA_TIPO_NOTIFICACION` | Tipo de Notificación |
| TipoReporte | `catalogos_tiporeporte` | `TEMA_TIPO_REPORTE` | Tipo de Reporte |
| TipoSuelo | `catalogos_tiposuelo` | `TEMA_TIPO_SUELO` | Tipo de Suelo |
| VariedadCacao | `catalogos_variedadcacao` | `TEMA_VARIEDAD_CACAO` | Variedad de Cacao |
| VersionModelo | `catalogos_versionmodelo` | `TEMA_VERSION_MODELO` | Versión de Modelo |

### 1.2. Catálogos que NO se Migran

- `catalogos_departamento` - Se mantiene (requerimiento explícito)
- `catalogos_municipio` - Se mantiene (requerimiento explícito)

### 1.3. Tablas Dependientes y Nuevos FKs

| Tabla | Campo Actual | FK Actual | Nuevo Campo | Nuevo FK | Notas |
|-------|--------------|-----------|-------------|----------|-------|
| `api_finca` | `tipo_suelo_id` | `catalogos_tiposuelo` | `tipo_suelo_id` | `catalogos_parametro` | Cambiar FK |
| `api_finca` | `clima_id` | `catalogos_clima` | `clima_id` | `catalogos_parametro` | Cambiar FK |
| `api_finca` | `estado_id` | `catalogos_estadofinca` | `estado_id` | `catalogos_parametro` | Cambiar FK |
| `fincas_app_lote` | `variedad_id` | `catalogos_variedadcacao` | `variedad_id` | `catalogos_parametro` | Cambiar FK |
| `fincas_app_lote` | `estado_id` | `catalogos_estadolote` | `estado_id` | `catalogos_parametro` | Cambiar FK |
| `images_app_cacaoimage` | `file_type_id` | `catalogos_tipoarchivo` | `file_type_id` | `catalogos_parametro` | Cambiar FK |
| `images_app_cacaoprediction` | `model_version_id` | `catalogos_versionmodelo` | `model_version_id` | `catalogos_parametro` | Cambiar FK |
| `images_app_cacaoprediction` | `device_used_id` | `catalogos_tipodispositivo` | `device_used_id` | `catalogos_parametro` | Cambiar FK |
| `api_reportegenerado` | `tipo_reporte_id` | `catalogos_tiporeporte` | `tipo_reporte_id` | `catalogos_parametro` | Cambiar FK |
| `api_reportegenerado` | `formato_id` | `catalogos_formatoreporte` | `formato_id` | `catalogos_parametro` | Cambiar FK |
| `api_reportegenerado` | `estado_id` | `catalogos_estadoreporte` | `estado_id` | `catalogos_parametro` | Cambiar FK |
| `notifications_notification` | `tipo_id` | `catalogos_tiponotificacion` | `tipo_id` | `catalogos_parametro` | Cambiar FK |

### 1.4. Campos Especiales

**TipoArchivo** tiene un campo adicional `mime_type` que debe preservarse. Se almacenará en `Parametro.descripcion` o se puede agregar un campo JSONB adicional.

**VersionModelo** tiene un campo adicional `fecha_lanzamiento` que debe preservarse. Se almacenará en `Parametro.descripcion` o se puede agregar un campo JSONB adicional.

## 2. ESTRATEGIA DE MIGRACIÓN

### Fase 1: Crear Temas y Migrar Datos
1. Crear registros en `catalogos_tema` para cada catálogo
2. Migrar todos los registros de cada catálogo a `catalogos_parametro`
3. Preservar campos adicionales (mime_type, fecha_lanzamiento) en descripcion o JSONB

### Fase 2: Actualizar Foreign Keys
1. Para cada tabla dependiente:
   - Agregar columna temporal `{campo}_parametro_id`
   - Migrar datos: buscar el parámetro correspondiente por tema y código
   - Eliminar FK antigua
   - Renombrar columna temporal a nombre original
   - Agregar nueva FK a `catalogos_parametro`

### Fase 3: Actualizar Modelos
1. Cambiar imports en modelos
2. Actualizar ForeignKey definitions
3. Agregar métodos helper para obtener parámetros por tema

### Fase 4: Limpieza
1. Eliminar tablas de catálogos antiguos
2. Eliminar modelos obsoletos

## 3. ADVERTENCIAS

### Tablas Afectadas
- `api_finca` (3 campos)
- `fincas_app_lote` (2 campos)
- `images_app_cacaoimage` (1 campo)
- `images_app_cacaoprediction` (2 campos)
- `api_reportegenerado` (3 campos)
- `notifications_notification` (1 campo)

### Riesgos
1. **Integridad Referencial**: Durante la migración, las FKs temporales pueden causar inconsistencias
2. **Datos Perdidos**: Si un registro del catálogo antiguo no tiene equivalente en parámetros, se perderá la referencia
3. **Performance**: Las queries con `parametro.tema.codigo` pueden ser más lentas que las directas

### Validaciones Requeridas
1. Verificar que todos los registros de catálogos antiguos tengan equivalente en parámetros
2. Verificar que todas las FKs se migraron correctamente
3. Verificar que no hay registros huérfanos

## 4. PLAN DE ROLLBACK

Si es necesario revertir la migración:

1. **Restaurar tablas de catálogos antiguos** desde backup
2. **Revertir FKs** en tablas dependientes
3. **Eliminar temas y parámetros** creados
4. **Restaurar modelos** desde control de versiones

**NOTA**: El rollback es complejo y requiere backup completo de la BD antes de la migración.

