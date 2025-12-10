# Flujo Completo: Asignar Rol (Frontend → Backend)

## Resumen del Flujo

El flujo de asignación de rol permite a un administrador definir y modificar los permisos de un usuario asignándole un rol específico.

**Endpoint:** `PATCH /api/v1/users/{user_id}/role/` o `POST /api/v1/users/{user_id}/assign-role/`

**Autenticación:** Requerida (IsAuthenticated, rol Administrador)

**Flujo:**
1. Administrador selecciona usuario de la lista
2. Administrador selecciona nuevo rol
3. Frontend envía PATCH/POST con nuevo rol
4. Backend valida permisos (solo administradores)
5. Backend valida que el rol sea válido
6. Backend valida que no se esté removiendo el último administrador
7. Backend actualiza rol del usuario
8. Backend actualiza permisos asociados
9. Backend invalida sesiones activas del usuario
10. Backend registra cambio en auditoría

**Parámetros:**
- `role`: Nuevo rol (administrador, tecnico, agricultor)

**Respuesta:**
```json
{
  "message": "Rol actualizado exitosamente",
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "role": "tecnico"
  }
}
```

**Validaciones:**
- Solo administradores pueden asignar roles
- Debe haber al menos un administrador activo
- Un usuario no puede quitarse su propio rol de administrador

**Tests:**
```bash
pytest auth_app/tests/test_role_views.py::TestAssignRoleView::test_post_success -v
pytest auth_app/tests/test_role_views.py::TestAssignRoleView::test_post_last_admin -v
```

