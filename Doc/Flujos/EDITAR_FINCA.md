# Flujo Completo: Editar Finca (Frontend → Backend)

## Resumen del Flujo

El flujo de edición de finca permite actualizar la información de una finca existente, modificando sus datos de ubicación, dimensiones u otros atributos.

```
Frontend (Vue.js)
  ↓
FincaForm.vue (Componente con isEditing=true)
  ↓
useFincas.js (Composable)
  ↓
fincasApi.js (Service API)
  ↓ HTTP PATCH/PUT /api/v1/fincas/{finca_id}/
Backend (Django REST Framework)
  ↓
FincaDetailView.patch() (Controller/View)
  ↓
FincaSerializer (Validación)
  ↓
Finca Model (Base de Datos)
  ↓
PostgreSQL
```

---

## Componentes del Flujo

### 1. Frontend - Componente Vue

**Archivo:** `frontend/src/components/common/FincasViewComponents/FincaForm.vue`

**Flujo:**
1. Usuario accede a editar finca desde la lista
2. Se carga la finca existente con datos precargados
3. Usuario modifica los campos deseados
4. Al hacer submit, se ejecuta `handleSubmit()`
5. Se llama a `updateFinca()` del composable `useFincas`

### 2. Backend - Vista/Controller

**Archivo:** `backend/fincas_app/views/finca/finca_views.py`

**Clase:** `FincaDetailView`

**Flujo:**
1. Recibe petición PATCH/PUT con `finca_id` en la URL
2. Valida permisos del usuario (propietario o admin)
3. Obtiene la finca existente
4. Deserializa y valida datos modificados
5. Actualiza el registro de Finca
6. Retorna respuesta HTTP con datos actualizados

---

## Endpoint de la API

**URL:** `PATCH /api/v1/fincas/{finca_id}/` o `PUT /api/v1/fincas/{finca_id}/`

**Autenticación:** Requerida (IsAuthenticated)

**Content-Type:** `application/json`

**Parámetros:**
- `finca_id`: ID de la finca (en la URL)
- Campos a actualizar en el body (todos opcionales excepto validaciones)

**Respuesta exitosa (200 OK):**
```json
{
  "id": 1,
  "nombre": "Finca El Paraíso Actualizada",
  "ubicacion": "Nueva Ubicación",
  "municipio": "San José",
  "departamento": "Cundinamarca",
  "hectareas": 6.0,
  "updated_at": "2024-12-19T11:00:00Z"
}
```

**Respuesta con errores (400 Bad Request):**
```json
{
  "error": "Error de validación",
  "details": {
    "nombre": ["Ya existe una finca con este nombre"]
  }
}
```

---

## Comandos de Test

### Tests de Vistas (Editar Finca)

**Archivo:** `backend/fincas_app/tests/test_finca_views.py` (si existe)

```bash
# Test: Editar finca exitosa
pytest fincas_app/tests/test_finca_views.py::TestFincaDetailView::test_patch_success -v

# Test: Sin permisos para editar
pytest fincas_app/tests/test_finca_views.py::TestFincaDetailView::test_patch_no_permission -v

# Test: Finca no encontrada
pytest fincas_app/tests/test_finca_views.py::TestFincaDetailView::test_patch_not_found -v

# Test: Nombre duplicado
pytest fincas_app/tests/test_finca_views.py::TestFincaDetailView::test_patch_duplicate_name -v
```

---

## Validaciones Implementadas

- Solo el propietario de la finca o un administrador pueden editarla
- El nombre de la finca debe seguir siendo único por agricultor
- Las hectáreas deben seguir siendo positivas
- Se mantiene historial de cambios si está habilitado

---

## Archivos Relacionados

### Backend
- `backend/fincas_app/views/finca/finca_views.py` - Vistas de fincas
- `backend/fincas_app/serializers/finca_serializers.py` - Serializers

### Frontend
- `frontend/src/components/common/FincasViewComponents/FincaForm.vue` - Formulario
- `frontend/src/composables/useFincas.js` - Composable

---

## Notas Adicionales

- Se implementa control de concurrencia (optimistic locking) para ediciones simultáneas
- Los cambios se registran en auditoría
- La fecha de modificación se actualiza automáticamente

