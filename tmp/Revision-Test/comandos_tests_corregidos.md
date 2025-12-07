# Comandos Corregidos para Ejecutar Tests

## Problema Identificado

Estás ejecutando desde el directorio `backend/` pero usando rutas con el prefijo `backend/`, lo cual es incorrecto.

## Solución

Desde el directorio `backend/`, usa rutas relativas sin el prefijo `backend/`.

---

## Comandos Correctos

### Desde el directorio `backend/`

```bash
# Asegúrate de estar en el directorio backend/
cd backend

# Ejecutar tests del servicio de lotes
pytest fincas_app/tests/test_lote_service.py -v

# Ejecutar un test específico
pytest fincas_app/tests/test_lote_service.py::TestLoteService::test_create_lote_success -v

# Ejecutar todos los tests de fincas_app
pytest fincas_app/tests/ -v

# Ejecutar con cobertura
pytest fincas_app/tests/test_lote_service.py --cov=fincas_app.services.lote_service --cov-report=html

# Ejecutar tests de vistas (si existen)
pytest fincas_app/tests/test_finca_views.py -v
```

### Desde el directorio raíz del proyecto

Si estás en el directorio raíz (`cacaoscan/`):

```bash
# Ejecutar tests del servicio de lotes
pytest backend/fincas_app/tests/test_lote_service.py -v

# Ejecutar todos los tests de fincas_app
pytest backend/fincas_app/tests/ -v
```

---

## Verificar Ubicación Actual

```bash
# Ver dónde estás
pwd  # Linux/Mac
cd   # Windows

# Ver estructura de tests
ls fincas_app/tests/  # Linux/Mac
dir fincas_app\tests\  # Windows
```

---

## Archivos de Test Existentes

En `backend/fincas_app/tests/`:
- ✅ `test_lote_service.py` - Tests del servicio de lotes
- ✅ `test_finca_views.py` - Tests de vistas de fincas
- ⚠️ `test_views.py` - Solo tests básicos de importación
- ❌ `test_lote_views.py` - **NO EXISTE** (necesita crearse)

---

## Crear Tests de Vistas de Lotes

Si quieres crear tests para las vistas de lotes, crea el archivo:

```bash
# Desde backend/
touch fincas_app/tests/test_lote_views.py  # Linux/Mac
# O crear manualmente en Windows
```

Luego agrega los tests como se muestra en el documento `flujo_crear_lote.md`.

---

## Ejecutar Todos los Tests del Proyecto

```bash
# Desde backend/
pytest -v

# Esto ejecutará todos los tests según la configuración en pytest.ini
# que incluye: api/tests, fincas_app/tests, etc.
```

---

## Troubleshooting

### Error: "file or directory not found"

**Causa**: Estás usando la ruta incorrecta para tu ubicación actual.

**Solución**:
1. Verifica dónde estás: `pwd` o `cd`
2. Si estás en `backend/`, usa: `pytest fincas_app/tests/test_lote_service.py`
3. Si estás en la raíz, usa: `pytest backend/fincas_app/tests/test_lote_service.py`

### Error: "collected 0 items"

**Causa**: Los tests no se están encontrando o no hay tests en el archivo.

**Solución**:
1. Verifica que el archivo existe: `ls fincas_app/tests/test_lote_service.py`
2. Verifica que tiene tests: `grep "def test_" fincas_app/tests/test_lote_service.py`
3. Ejecuta con más verbosidad: `pytest fincas_app/tests/test_lote_service.py -vv`

---

## Ejemplo Completo

```bash
# 1. Navegar al directorio backend
cd C:\Documentos\trabajos\Programing\proyecyto de cacao\Proyecto_Git\cacaoscan\backend

# 2. Activar entorno virtual (si no está activo)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Ejecutar tests
pytest fincas_app/tests/test_lote_service.py -v

# 4. Ver resultados
# Deberías ver algo como:
# ============================= test session starts ==============================
# collected 23 items
# 
# fincas_app/tests/test_lote_service.py::TestLoteService::test_extract_lote_data PASSED
# fincas_app/tests/test_lote_service.py::TestLoteService::test_create_lote_success PASSED
# ...
```

