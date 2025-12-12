# Flujo Completo: Editar Perfil (Frontend → Backend)

## Resumen del Flujo

El flujo de edición de perfil permite a un usuario autenticado actualizar sus propios datos personales sin necesidad de intervención administrativa.

**Endpoint:** `PATCH /api/v1/auth/profile/` o `PATCH /api/v1/users/me/`

**Autenticación:** Requerida (IsAuthenticated)

**Flujo:**
1. Usuario accede a "Mi Perfil" o "Configuración"
2. Usuario modifica campos deseados
3. Frontend envía PATCH con datos modificados
4. Backend valida que el usuario edite solo su propio perfil
5. Backend valida datos modificados
6. Si cambia contraseña, valida contraseña actual
7. Si cambia email, requiere verificación
8. Backend actualiza registro del usuario
9. Backend registra cambios críticos en auditoría

**Parámetros:**
- `first_name`: Nombre (opcional)
- `last_name`: Apellido (opcional)
- `telefono`: Teléfono (opcional)
- `direccion`: Dirección (opcional)
- `password`: Nueva contraseña (opcional, requiere `current_password`)
- `current_password`: Contraseña actual (requerido si se cambia password)

**Respuesta:**
```json
{
  "message": "Perfil actualizado exitosamente",
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "first_name": "Juan",
    "last_name": "Pérez"
  }
}
```

**Validaciones:**
- Usuario solo puede editar su propio perfil
- Email no se puede cambiar desde el perfil (requiere proceso administrativo)
- Contraseña debe cumplir requisitos de fortaleza
- Contraseña actual debe ser correcta para cambiar contraseña

**Tests:**
```bash
pytest auth_app/tests/test_profile_views.py::TestUserProfileView::test_patch_success -v
pytest auth_app/tests/test_profile_views.py::TestUserProfileView::test_patch_wrong_password -v
```

