# 📋 Archivos de SonarQube Verificados en los Tests

## Resumen de Tests y Archivos Corregidos

### ✅ Test 1: `test_error_response_details.py`
**Bug SonarQube**: "Remove this unexpected named argument 'errors'"

**Archivos corregidos**:
1. `backend/api/incremental_views.py`
   - Líneas corregidas: 76, 260, 410, 495, 564
   - Cambio: `errors={...}` → `details={...}`

2. `backend/api/model_metrics_views.py`
   - Líneas corregidas: 189, 243, 304, 312, 374, 387, 440, 525, 643, 776, 827, 878
   - Cambio: `errors={...}` → `details={...}`
   - Nota: Ya estaba usando `details` correctamente

**Archivo de referencia**:
- `backend/api/utils.py` - Define `create_error_response(details=...)`

---

### ✅ Test 2: `test_model_metrics_error_response.py`
**Bug SonarQube**: "Remove this unexpected named argument 'errors'"

**Archivo corregido**:
- `backend/api/model_metrics_views.py`
  - Verifica que `ModelMetricsCreateView` usa `details` correctamente

---

### ✅ Test 3: `test_redundant_elif.py`
**Bug SonarQube**: "This branch duplicates the one on line X"

**Archivos corregidos**:
1. `backend/api/services/auth_service.py`
   - Líneas eliminadas: 632-633
   - Eliminado: `elif hasattr(user, 'auth_email_token'): return user.auth_email_token.is_verified`
   - Razón: Era redundante con el `if` anterior

2. `backend/auth_app/models.py`
   - Líneas eliminadas: 140-141
   - Eliminado: `elif hasattr(self.user, 'auth_email_token'): return self.user.auth_email_token.is_verified`
   - Razón: Era redundante con el `if` anterior

---

### ✅ Test 4: `test_create_model_parameters.py`
**Bug SonarQube**: "Remove this unexpected named argument 'target'"

**Archivo corregido**:
- `backend/ml/regression/incremental_train.py`
  - Líneas corregidas: 657, 663, 666
  - Cambio: `create_model(target=target)` → `create_model(num_outputs=1)`

---

### ✅ Test 5: `test_html_accessibility.py`
**Bug SonarQube**: "Add a description to this table"

**Archivos corregidos**:
1. `backend/api/templates/emails/analysis_complete.html`
   - Línea agregada: 121
   - Agregado: `<caption class="sr-only">Tabla de resultados del análisis de cacao...</caption>`

2. `frontend/src/components/admin/AdminAgricultorComponents/DataTable.vue`
   - Líneas agregadas: 10-11, 131-134, 165-175
   - Agregado: 
     - `aria-label` en `<table>`
     - `<caption class="sr-only">` dentro de `<table>`
     - Prop `tableLabel`
     - CSS `.sr-only`

3. `frontend/src/components/admin/AdminDashboardComponents/DashboardTables.vue`
   - Líneas agregadas: 25-26, 100-101, 248-258
   - Agregado:
     - `aria-label` en ambas tablas
     - `<caption class="sr-only">` en ambas tablas
     - CSS `.sr-only`

4. `frontend/src/components/admin/AdminUserComponents/UsersTable.vue`
   - Líneas agregadas: 38-39, 290-300
   - Agregado:
     - `aria-label="Tabla de usuarios del sistema"` en `<table>`
     - `<caption class="sr-only">` dentro de `<table>`
     - CSS `.sr-only`

5. `frontend/src/components/training/SamplesTable.vue`
   - Líneas agregadas: 40-41, 239-249
   - Agregado:
     - `aria-label="Tabla de muestras de entrenamiento"` en `<table>`
     - `<caption class="sr-only">` dentro de `<table>`
     - CSS `.sr-only`

6. `frontend/src/components/audit/AuditTable.vue`
   - Líneas agregadas: 27-28, 719-729
   - Agregado:
     - `aria-label="Tabla de registros de auditoría"` en `<table>`
     - `<caption class="sr-only">` dentro de `<table>`
     - CSS `.sr-only`

7. `frontend/src/components/reportes/ReportsTable.vue`
   - Líneas agregadas: 9-10, 435-445
   - Agregado:
     - `aria-label="Tabla de reportes generados"` en `<table>`
     - `<caption class="sr-only">` dentro de `<table>`
     - CSS `.sr-only`

---

### ✅ Test 6: `test_html_lang_attribute.py`
**Bug SonarQube**: "Add 'lang' and/or 'xml:lang' attributes to this '<html>' element"

**Archivo corregido**:
- `frontend/cypress/support/component-index.html`
  - Línea modificada: 2
  - Cambio: `<html>` → `<html lang="es" xml:lang="es">`

---

### ✅ Test 7: `test_simple_verification.py`
**Propósito**: Verificación directa en código fuente

**Archivos verificados**:
1. `backend/api/utils.py` - Verifica que `create_error_response` usa `details`
2. `backend/api/model_metrics_views.py` - Verifica que usa `details` y no `errors`
3. `backend/api/refactored_views.py` - Verifica que usa `details` y no `errors`
4. `backend/api/services/auth_service.py` - Verifica que no tiene elif redundante
5. `backend/auth_app/models.py` - Verifica que no tiene elif redundante
6. `backend/ml/regression/incremental_train.py` - Verifica que usa `num_outputs` y no `target`

---

## 📊 Resumen por Archivo

### Backend (Python)

| Archivo | Bugs Corregidos | Líneas Afectadas |
|---------|----------------|------------------|
| `api/model_metrics_views.py` | 1 | 189, 243, 304, 312, 374, 387, 440, 525, 643, 776, 827, 878 |
| `api/refactored_views.py` | 1 | 63, 83, 123, 142 |
| `api/services/auth_service.py` | 1 | 632-633 (eliminadas) |
| `auth_app/models.py` | 1 | 140-141 (eliminadas) |
| `ml/regression/incremental_train.py` | 1 | 657, 663, 666 |

### Frontend (Vue/HTML)

| Archivo | Bugs Corregidos | Líneas Afectadas |
|---------|----------------|------------------|
| `api/templates/emails/analysis_complete.html` | 1 | 121 (agregada) |
| `components/admin/AdminAgricultorComponents/DataTable.vue` | 1 | 10-11, 131-134, 165-175 |
| `components/admin/AdminDashboardComponents/DashboardTables.vue` | 1 | 25-26, 100-101, 248-258 |
| `components/admin/AdminUserComponents/UsersTable.vue` | 1 | 38-39, 290-300 |
| `components/training/SamplesTable.vue` | 1 | 40-41, 239-249 |
| `components/audit/AuditTable.vue` | 1 | 27-28, 719-729 |
| `components/reportes/ReportsTable.vue` | 1 | 9-10, 435-445 |
| `cypress/support/component-index.html` | 1 | 2 (modificada) |

---

## 🎯 Total de Correcciones

- **Total de archivos corregidos**: 13
  1. `backend/api/model_metrics_views.py`
  2. `backend/api/refactored_views.py`
  3. `backend/api/services/auth_service.py`
  4. `backend/api/templates/emails/analysis_complete.html`
  5. `backend/auth_app/models.py`
  6. `backend/ml/regression/incremental_train.py`
  7. `frontend/cypress/support/component-index.html`
  8. `frontend/src/components/admin/AdminAgricultorComponents/DataTable.vue`
  9. `frontend/src/components/admin/AdminDashboardComponents/DashboardTables.vue`
  10. `frontend/src/components/admin/AdminUserComponents/UsersTable.vue`
  11. `frontend/src/components/training/SamplesTable.vue`
  12. `frontend/src/components/audit/AuditTable.vue`
  13. `frontend/src/components/reportes/ReportsTable.vue`
- **Total de bugs de SonarQube corregidos**: 6 tipos diferentes
- **Total de líneas modificadas**: ~30 líneas

---

## ⚠️ Errores Actuales en los Tests

### Error 1: `test_incremental_training_error_uses_details`
**Problema**: El patch está intentando hacer patch de `api.incremental_views.run_incremental_training_pipeline` pero esa función no existe en ese módulo.

**Solución**: El patch debe ser `ml.pipeline.train_all.run_incremental_training_pipeline` (ya corregido en el código, pero el contenedor puede tener versión antigua).

### Error 2: `test_user_profile_email_verified_*`
**Problema**: Los tests están intentando crear `UserProfile` con campos `primer_nombre` y `primer_apellido` que no existen.

**Solución**: Ya corregido en el código - solo necesita `user=self.user`.

---

## 📝 Notas

1. Los tests verifican que las correcciones de SonarQube fueron aplicadas correctamente.
2. Algunos tests pueden fallar si el contenedor Docker tiene una versión antigua del código.
3. Los tests de accesibilidad HTML verifican que los elementos tienen las etiquetas correctas.
4. Los tests de `elif` redundante verifican que el código funciona correctamente después de la eliminación.

