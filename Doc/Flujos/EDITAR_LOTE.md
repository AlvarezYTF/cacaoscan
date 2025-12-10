# Flujo Completo: Editar Lote (Frontend → Backend)

## Resumen del Flujo

El flujo de edición de lote permite actualizar la información de un lote existente, modificando sus datos de variedad, fechas, área u otros atributos.

```
Frontend (Vue.js)
  ↓
LoteForm.vue (Componente con isEditing=true)
  ↓
useLotes.js (Composable)
  ↓
lotesApi.js (Service API)
  ↓ HTTP PATCH/PUT /api/v1/lotes/{lote_id}/
Backend (Django REST Framework)
  ↓
LoteDetailView.patch() (Controller/View)
  ↓
LoteSerializer (Validación)
  ↓
Lote Model (Base de Datos)
  ↓
PostgreSQL
```

---

## Componentes del Flujo

### 1. Frontend - Componente Vue

**Archivo:** `frontend/src/components/LoteForm.vue` o similar

**Flujo:**
1. Usuario accede a editar lote desde la lista
2. Se carga el lote existente con datos precargados
3. Usuario modifica los campos deseados
4. Al hacer submit, se ejecuta `handleSubmit()`
5. Se llama a `updateLote()` del composable `useLotes`

### 2. Backend - Vista/Controller

**Archivo:** `backend/fincas_app/views/finca/lote_views.py`

**Clase:** `LoteDetailView`

**Flujo:**
1. Recibe petición PATCH/PUT con `lote_id` en la URL
2. Valida permisos del usuario (propietario de la finca o admin)
3. Obtiene el lote existente
4. Deserializa y valida datos modificados
5. Valida que las fechas sigan siendo coherentes
6. Valida que el área no exceda el área disponible de la finca
7. Actualiza el registro de Lote
8. Retorna respuesta HTTP con datos actualizados

---

## Endpoint de la API

**URL:** `PATCH /api/v1/lotes/{lote_id}/` o `PUT /api/v1/lotes/{lote_id}/`

**Autenticación:** Requerida (IsAuthenticated)

**Content-Type:** `application/json`

**Parámetros:**
- `lote_id`: ID del lote (en la URL)
- Campos a actualizar en el body

**Respuesta exitosa (200 OK):**
```json
{
  "id": 1,
  "nombre": "Lote Norte Actualizado",
  "variedad": "Criollo",
  "fecha_plantacion": "2023-01-15",
  "area_hectareas": 2.5,
  "updated_at": "2024-12-19T11:00:00Z"
}
```

---

## Comandos de Test

### Tests de Vistas (Editar Lote)

**Archivo:** `backend/fincas_app/tests/test_lote_views.py` (si existe)

```bash
# Test: Editar lote exitoso
pytest fincas_app/tests/test_lote_views.py::TestLoteDetailView::test_patch_success -v

# Test: Sin permisos
pytest fincas_app/tests/test_lote_views.py::TestLoteDetailView::test_patch_no_permission -v

# Test: Fechas inválidas
pytest fincas_app/tests/test_lote_views.py::TestLoteDetailView::test_patch_invalid_dates -v

# Test: Área excedida
pytest fincas_app/tests/test_lote_views.py::TestLoteDetailView::test_patch_area_exceeded -v
```

---

## Validaciones Implementadas

- Solo el propietario de la finca o un administrador pueden editar el lote
- Las fechas deben ser coherentes (plantación antes de cosecha)
- El área no debe exceder el área disponible de la finca
- Se mantiene historial de cambios

---

## Archivos Relacionados

### Backend
- `backend/fincas_app/views/finca/lote_views.py` - Vistas de lotes
- `backend/fincas_app/serializers/lote_serializers.py` - Serializers

### Frontend
- `frontend/src/components/LoteForm.vue` - Formulario
- `frontend/src/composables/useLotes.js` - Composable

---

## Notas Adicionales

- Se implementa control de concurrencia para ediciones simultáneas
- Los cambios se registran en auditoría
- Se valida que los cambios no afecten análisis históricos asociados

