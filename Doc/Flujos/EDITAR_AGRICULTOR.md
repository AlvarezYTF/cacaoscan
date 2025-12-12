# Flujo Completo: Editar Agricultor (Frontend → Backend)

## Resumen del Flujo

El flujo de edición de agricultor permite a un administrador actualizar la información de un agricultor existente.

**Endpoint:** `PATCH /api/v1/users/{user_id}/` o `PATCH /api/v1/personas/{persona_id}/`

**Autenticación:** Requerida (IsAuthenticated, rol Administrador)

**Flujo:**
1. Administrador selecciona agricultor de la lista
2. Administrador modifica campos deseados
3. Frontend envía PATCH con datos modificados
4. Backend valida permisos
5. Backend valida que el email siga siendo único (si se modificó)
6. Backend actualiza usuario y persona
7. Backend registra cambios en auditoría

**Parámetros:**
- Campos a actualizar (todos opcionales)
- `is_active`: Cambiar estado de cuenta
- `password`: Resetear contraseña (opcional)

**Validaciones:**
- Solo administradores pueden editar
- Email debe seguir siendo único
- No se puede desactivar agricultor con fincas activas

**Tests:**
```bash
pytest personas/tests/test_views.py::TestPersonaDetailView::test_patch_success -v
pytest personas/tests/test_views.py::TestPersonaDetailView::test_patch_duplicate_email -v
```

