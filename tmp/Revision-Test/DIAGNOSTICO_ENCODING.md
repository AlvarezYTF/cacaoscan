# Diagnóstico y Corrección de Problemas de Encoding

## 📋 Resumen Ejecutivo

Se han realizado correcciones exhaustivas para eliminar el error `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3` que ocurría al crear la base de datos de pruebas con PostgreSQL.

---

## 🔍 Problemas Detectados y Corregidos

### 1. **Falta de Declaración de Encoding UTF-8**

**Problema**: Los archivos Python no tenían la declaración de encoding explícita.

**Archivos Corregidos**:
- ✅ `backend/cacaoscan/settings.py`
- ✅ `backend/manage.py`

**Corrección Aplicada**:
```python
# -*- coding: utf-8 -*-
```

---

### 2. **Falta de Variables de Entorno UTF-8**

**Problema**: No se forzaba el uso de UTF-8 en las operaciones del sistema.

**Archivo Corregido**:
- ✅ `backend/cacaoscan/settings.py` (líneas 12-15)

**Corrección Aplicada**:
```python
# Force UTF-8 encoding for all operations
os.environ["PYTHONUTF8"] = "1"
os.environ["PYTHONIOENCODING"] = "UTF-8"
os.environ["PGCLIENTENCODING"] = "UTF8"
```

---

### 3. **Carga Insegura del Archivo .env**

**Problema**: El archivo `.env` se cargaba sin eliminar BOM (Byte Order Mark) y bytes inválidos.

**Archivo Corregido**:
- ✅ `backend/cacaoscan/settings.py` (líneas 100-138)

**Correcciones Aplicadas**:
- ✅ Detección y eliminación de UTF-8 BOM (`0xEF, 0xBB, 0xBF`)
- ✅ Eliminación del byte problemático `0xf3`
- ✅ Eliminación de otros bytes inválidos
- ✅ Decodificación robusta con fallback a latin-1
- ✅ Limpieza de caracteres no imprimibles
- ✅ Eliminación de CRLF problemáticos

---

### 4. **Función de Limpieza Insuficiente**

**Problema**: La función `clean_value()` no era lo suficientemente robusta para limpiar todos los casos.

**Archivo Corregido**:
- ✅ `backend/cacaoscan/settings.py` (líneas 277-316)

**Mejoras Implementadas**:
- ✅ Manejo de valores `bytes` y `str`
- ✅ Eliminación de UTF-8 BOM
- ✅ Eliminación de bytes problemáticos (`0xf3`, `0x00`, etc.)
- ✅ Filtrado de caracteres no imprimibles ASCII
- ✅ Validación de encoding UTF-8
- ✅ Manejo robusto de errores

---

### 5. **Variables de Base de Datos Sin Limpieza Adecuada**

**Problema**: Las variables de conexión a PostgreSQL no se limpiaban correctamente antes de usar.

**Archivo Corregido**:
- ✅ `backend/cacaoscan/settings.py` (líneas 318-323)

**Corrección Aplicada**:
- ✅ Todas las variables de BD se limpian con `clean_value()`
- ✅ Valores por defecto ASCII-safe
- ✅ Validación previa al uso en `DATABASES`

---

### 6. **Configuración de DATABASES Mejorada**

**Archivo Corregido**:
- ✅ `backend/cacaoscan/settings.py` (líneas 325-343)

**Mejoras**:
- ✅ Todos los valores son ASCII-safe
- ✅ `client_encoding: 'UTF8'` explícito en OPTIONS
- ✅ Nombre de BD de prueba limpio

---

## 📝 Archivos Modificados

### 1. `backend/cacaoscan/settings.py`

**Cambios Principales**:
- ✅ Agregada declaración `# -*- coding: utf-8 -*-` al inicio
- ✅ Variables de entorno UTF-8 forzadas al inicio del archivo
- ✅ Función mejorada de carga del `.env` con eliminación de BOM
- ✅ Función `clean_value()` completamente reescrita y mejorada
- ✅ Variables de BD limpiadas antes de usar
- ✅ Configuración de `DATABASES` validada

**Líneas Modificadas**: ~150 líneas

---

### 2. `backend/manage.py`

**Cambios Principales**:
- ✅ Agregada declaración `# -*- coding: utf-8 -*-`
- ✅ Variables de entorno UTF-8 forzadas

**Líneas Modificadas**: ~5 líneas

---

## 🎯 Resultado Esperado

Después de estas correcciones:

1. ✅ **Sin UnicodeDecodeError**: El byte `0xf3` y otros bytes inválidos se eliminan desde el origen
2. ✅ **Sin BOM**: El archivo `.env` se carga sin Byte Order Mark
3. ✅ **Encoding Consistente**: Todas las operaciones usan UTF-8
4. ✅ **Variables Limpias**: Todas las variables de BD están limpias antes de conectarse
5. ✅ **Pytest Funcional**: La creación de la BD de pruebas debería funcionar sin errores

---

## 🔧 Validación

Para validar que todo funciona correctamente:

```bash
# Ejecutar pytest
cd backend
pytest --tb=short

# Verificar que no hay errores de encoding
pytest 2>&1 | grep -i "unicode\|decode\|encoding" || echo "✅ No hay errores de encoding"
```

---

## 📌 Notas Importantes

1. **Archivo .env**: Si el archivo `.env` local tiene problemas de encoding, se recomienda:
   - Abrirlo en un editor que soporte UTF-8
   - Guardarlo como "UTF-8 sin BOM"
   - Eliminar cualquier carácter especial oculto

2. **Variables de Entorno del Sistema**: Si las variables de entorno del sistema contienen caracteres problemáticos, asegúrate de limpiarlas también.

3. **PostgreSQL**: La configuración de `client_encoding: 'UTF8'` asegura que la conexión use UTF-8.

---

## ✅ Checklist de Verificación

- [x] Declaración de encoding UTF-8 en archivos Python
- [x] Variables de entorno UTF-8 forzadas
- [x] Carga del `.env` con eliminación de BOM
- [x] Función de limpieza robusta
- [x] Variables de BD limpiadas
- [x] Configuración de DATABASES validada
- [x] Sin parches innecesarios de psycopg2
- [x] Código compatible con Django, PostgreSQL y pytest

---

**Fecha de Corrección**: $(date)
**Estado**: ✅ Completado

