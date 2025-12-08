# Flujo Completo: Crear Agricultor (Frontend → Backend)

## Resumen del Flujo

El flujo de creación de agricultor permite a un administrador registrar un nuevo agricultor en el sistema, creando su cuenta de usuario y asociándolo con su información personal.

**Endpoint:** `POST /api/v1/personas/registro/` o `POST /api/v1/users/agricultores/`

**Autenticación:** Requerida (IsAuthenticated, rol Administrador)

**Flujo:**
1. Administrador accede a gestión de usuarios/agricultores
2. Administrador completa formulario con datos del agricultor
3. Frontend envía POST con datos del agricultor
4. Backend valida permisos (solo administradores)
5. Backend valida que el email no esté registrado
6. Backend valida formato de email y documento
7. Backend crea usuario con rol "agricultor"
8. Backend crea registro de Persona asociado
9. Backend envía email de bienvenida con credenciales
10. Backend registra evento en auditoría

**Parámetros:**
- `email`: Email del agricultor (será username)
- `password`: Contraseña temporal (o se genera)
- `first_name`: Nombre
- `last_name`: Apellido
- `documento`: Número de documento
- `telefono`: Teléfono (opcional)
- `direccion`: Dirección (opcional)
- `municipio`: Municipio (opcional)
- `departamento`: Departamento (opcional)

**Respuesta:**
```json
{
  "message": "Agricultor creado exitosamente",
  "email": "agricultor@example.com",
  "persona_id": 1,
  "user_id": 1
}
```

**Validaciones:**
- Email único en el sistema
- Documento único (si se valida)
- Formato de email válido
- Contraseña con requisitos de fortaleza

**Tests:**
```bash
pytest personas/tests/test_views.py::TestPersonaRegistroView::test_post_success -v
pytest personas/tests/test_views.py::TestPersonaRegistroView::test_post_duplicate_email -v
```

