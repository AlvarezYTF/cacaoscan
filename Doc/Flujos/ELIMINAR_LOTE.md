# Flujo Completo: Eliminar Lote (Frontend → Backend)

## Resumen del Flujo

El flujo de eliminación de lote permite remover un lote del sistema cuando ya no es válido o necesario, implementando eliminación lógica para preservar el historial.

**Endpoint:** `DELETE /api/v1/lotes/{lote_id}/`

**Autenticación:** Requerida (IsAuthenticated)

**Flujo:**
1. Usuario selecciona lote y confirma eliminación
2. Frontend envía DELETE a `/api/v1/lotes/{lote_id}/`
3. Backend valida permisos (propietario o admin)
4. Backend valida dependencias (análisis asociados)
5. Backend implementa eliminación lógica (soft delete)
6. Backend registra evento en auditoría
7. Frontend actualiza lista de lotes

**Validaciones:**
- Solo propietario de la finca o administrador pueden eliminar
- Se valida si hay análisis asociados que requieren preservación
- Se implementa eliminación lógica para mantener integridad histórica

**Tests:**
```bash
pytest fincas_app/tests/test_lote_views.py::TestLoteDetailView::test_delete_success -v
pytest fincas_app/tests/test_lote_views.py::TestLoteDetailView::test_delete_with_restrictions -v
```

