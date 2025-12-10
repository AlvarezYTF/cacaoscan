# Flujo de Registro de Usuario con Comandos de Test

## Resumen del Flujo

El flujo de registro de usuario en CacaoScan permite a un usuario nuevo crear una cuenta proporcionando sus datos personales y credenciales. El sistema valida los datos, crea el usuario, genera tokens de verificación de email y envía un correo de verificación.

---

## Componentes del Flujo

### 1. Frontend (Vue.js)

**Archivo:** `frontend/src/views/RegisterView.vue` o componente de registro

- El usuario completa el formulario con: nombre, apellido, email, contraseña y confirmación
- Se valida el formulario en el cliente antes de enviar
- Se envía petición POST a `/api/v1/auth/register/`
- Se muestra mensaje de confirmación y se redirige a verificación de email

**Código clave:**
```javascript
// Ejemplo de flujo en el frontend
const handleRegister = async (formData) => {
  try {
    const response = await authApi.register({
      email: formData.email,
      password: formData.password,
      password_confirm: formData.password_confirm,
      first_name: formData.first_name,
      last_name: formData.last_name
    })
    
    // Manejar respuesta exitosa
    if (response.data.verification_required) {
      // Redirigir a página de verificación
    }
  } catch (error) {
    // Manejar errores de validación
  }
}
```

### 2. Backend - Vista (Django REST Framework)

**Archivo:** `backend/auth_app/views/auth/registration_views.py`

**Vista:** `RegisterView`

**Flujo:**
1. Recibe datos del formulario en `request.data`
2. Valida datos mediante `RegisterSerializer`
3. Llama al servicio `RegistrationService.register_user_with_email_verification()`
4. Crea usuario con estado inactivo
5. Genera token de verificación de email
6. Envía email de verificación
7. Retorna respuesta con datos del usuario y token de verificación

**Código clave:**
```49:91:backend/auth_app/views/auth/registration_views.py
    def post(self, request):
        """
        Registra un nuevo usuario y genera tokens JWT automáticamente.
        """
        # Crear una copia de los datos y eliminar el campo 'role' si viene del frontend
        data = request.data.copy()
        data.pop('role', None)  # Elimina si viene en la solicitud
        
        serializer = RegisterSerializer(data=data)
        
        if serializer.is_valid():
            # Usar servicio de autenticación para registrar usuario
            registration_service = RegistrationService()
            result = registration_service.register_user_with_email_verification(
                serializer.validated_data,
                request
            )
            
            if result.success:
                return create_success_response(
                    message=result.message,
                    data={
                        'user': UserSerializer(User.objects.get(id=result.data['user']['id'])).data,
                        'verification_required': result.data.get('verification_required', True),
                        'email': result.data.get('email'),
                        'verification_token': result.data.get('verification_token')
                    },
                    status_code=status.HTTP_201_CREATED
                )
            else:
                return create_error_response(
                    message=result.error.message,
                    error_type='validation_error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details=result.error.details
                )
        
        return create_error_response(
            message='Error en los datos proporcionados',
            error_type='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
        )
```

### 3. Backend - Servicio

**Archivo:** `backend/api/services/auth/registration_service.py`

**Servicio:** `RegistrationService`

Proporciona lógica de negocio para registro de usuarios, validación de datos, creación de usuarios y gestión de tokens de verificación.

---

## Endpoint de la API

**URL:** `POST /api/v1/auth/register/`

**Autenticación:** No requerida (AllowAny)

**Content-Type:** `application/json`

**Parámetros:**
- `email`: Email del usuario (requerido, único)
- `password`: Contraseña (requerido, mínimo 8 caracteres)
- `password_confirm`: Confirmación de contraseña (requerido)
- `first_name`: Nombre (opcional)
- `last_name`: Apellido (opcional)

**Respuesta exitosa (201 Created):**
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente. Se ha enviado un email de verificación.",
  "data": {
    "user": {
      "id": 1,
      "email": "usuario@example.com",
      "first_name": "Juan",
      "last_name": "Pérez",
      "is_active": false
    },
    "verification_required": true,
    "email": "usuario@example.com",
    "verification_token": "uuid-token-here"
  }
}
```

**Respuesta con errores (400 Bad Request):**
```json
{
  "success": false,
  "message": "Error en los datos proporcionados",
  "error_type": "validation_error",
  "details": {
    "email": ["Este email ya está registrado"],
    "password": ["La contraseña debe tener al menos 8 caracteres"]
  }
}
```

---

## Comandos de Test

### Configuración Inicial

**Desde el directorio `backend/`:**

```bash
# Asegúrate de estar en el directorio backend/
cd backend

# Activar entorno virtual (si no está activo)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### Tests de Vistas (Registro)

**Archivo:** `backend/auth_app/tests/test_registration_views.py` (si existe)

#### Ejecutar todos los tests de registro:

```bash
# Desde backend/
pytest auth_app/tests/test_registration_views.py -v
```

#### Tests específicos (ejemplos esperados):

```bash
# Test: Registro exitoso de usuario
pytest auth_app/tests/test_registration_views.py::TestRegisterView::test_post_success -v

# Test: Email duplicado
pytest auth_app/tests/test_registration_views.py::TestRegisterView::test_post_duplicate_email -v

# Test: Contraseña débil
pytest auth_app/tests/test_registration_views.py::TestRegisterView::test_post_weak_password -v

# Test: Contraseñas no coinciden
pytest auth_app/tests/test_registration_views.py::TestRegisterView::test_post_password_mismatch -v

# Test: Campos requeridos faltantes
pytest auth_app/tests/test_registration_views.py::TestRegisterView::test_post_missing_fields -v
```

### Tests de Servicio (Registration Service)

**Archivo:** `backend/api/tests/test_registration_service.py` (si existe)

#### Ejecutar todos los tests del servicio:

```bash
# Desde backend/
pytest api/tests/test_registration_service.py -v
```

#### Tests específicos:

```bash
# Test: Registro exitoso mediante servicio
pytest api/tests/test_registration_service.py::TestRegistrationService::test_register_user_success -v

# Test: Validación de email único
pytest api/tests/test_registration_service.py::TestRegistrationService::test_register_user_duplicate_email -v

# Test: Generación de token de verificación
pytest api/tests/test_registration_service.py::TestRegistrationService::test_generate_verification_token -v

# Test: Envío de email de verificación
pytest api/tests/test_registration_service.py::TestRegistrationService::test_send_verification_email -v
```

### Tests de Serializers

**Archivo:** `backend/api/tests/test_auth_serializers.py` (si existe)

```bash
# Test: Validación de RegisterSerializer
pytest api/tests/test_auth_serializers.py::TestRegisterSerializer -v

# Test: Validación de email
pytest api/tests/test_auth_serializers.py::TestRegisterSerializer::test_email_validation -v

# Test: Validación de contraseña
pytest api/tests/test_auth_serializers.py::TestRegisterSerializer::test_password_validation -v
```

### Ejecutar Todos los Tests de Registro

```bash
# Desde backend/
pytest auth_app/tests/ api/tests/test_registration_service.py api/tests/test_auth_serializers.py -v -k register
```

### Ejecutar con Cobertura

```bash
# Desde backend/
pytest auth_app/tests/test_registration_views.py --cov=auth_app.views.auth.registration_views --cov-report=html
pytest api/tests/test_registration_service.py --cov=api.services.auth.registration_service --cov-report=html
```

---

## Flujo Completo Paso a Paso

### 1. Usuario completa formulario en el frontend
- Validación inicial en el cliente (email válido, contraseñas coinciden, longitud mínima)
- Preparación de datos para envío

### 2. Petición HTTP POST al backend
- Endpoint: `/api/v1/auth/register/`
- Headers: `Content-Type: application/json`
- Body: Datos del formulario en JSON

### 3. Backend procesa la petición
- **Validación de serializer:** `RegisterSerializer` valida los datos
- **Validación de email único:** Verifica que el email no esté registrado
- **Validación de contraseña:** Verifica fortaleza y coincidencia
- **Creación de usuario:** Crea usuario con estado inactivo
- **Generación de token:** Crea token de verificación de email
- **Envío de email:** Envía correo con enlace de verificación
- **Auditoría:** Registra el evento de registro

### 4. Respuesta al frontend
- **201 Created:** Usuario creado exitosamente
- **400 Bad Request:** Errores de validación

### 5. Frontend procesa la respuesta
- Muestra mensaje de confirmación
- Redirige a página de verificación de email
- O muestra errores de validación específicos

---

## Validaciones Implementadas

### Email
- **Formato:** Debe ser un email válido
- **Unicidad:** Debe ser único en el sistema
- **Validación:** En frontend y backend
- **Error:** "Este email ya está registrado" o "Email inválido"

### Contraseña
- **Longitud mínima:** 8 caracteres
- **Requisitos:** Mayúsculas, minúsculas, números (según configuración)
- **Confirmación:** Debe coincidir con `password_confirm`
- **Validación:** En frontend y backend
- **Error:** "La contraseña debe tener al menos 8 caracteres" o "Las contraseñas no coinciden"

### Campos Requeridos
- **Email:** Requerido
- **Password:** Requerido
- **Password Confirm:** Requerido
- **Error:** "Este campo es requerido"

---

## Ejemplo de Uso con cURL

```bash
# Registrar un nuevo usuario
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nuevo@example.com",
    "password": "Password123!",
    "password_confirm": "Password123!",
    "first_name": "Juan",
    "last_name": "Pérez"
  }'
```

---

## Troubleshooting

### Error: "Este email ya está registrado"
**Causa:** El email ya existe en el sistema.
**Solución:** Usar otro email o iniciar sesión si ya tiene cuenta.

### Error: "Las contraseñas no coinciden"
**Causa:** Los campos `password` y `password_confirm` no son iguales.
**Solución:** Verificar que ambas contraseñas sean idénticas.

### Error: "La contraseña debe tener al menos 8 caracteres"
**Causa:** La contraseña no cumple con los requisitos mínimos.
**Solución:** Usar una contraseña más larga que cumpla con los requisitos.

### Error: "Email inválido"
**Causa:** El formato del email no es válido.
**Solución:** Verificar que el email tenga formato válido (ejemplo@dominio.com).

### Error: Email de verificación no recibido
**Causa:** Problema con el servicio de email o email en spam.
**Solución:** Verificar configuración de email, revisar carpeta de spam, o solicitar reenvío.

---

## Archivos Relacionados

### Backend
- `backend/auth_app/views/auth/registration_views.py` - Vistas de registro
- `backend/api/services/auth/registration_service.py` - Servicio de registro
- `backend/api/serializers/auth_serializers.py` - Serializers de autenticación
- `backend/auth_app/models.py` - Modelos de usuario y tokens
- `backend/api/urls.py` - URLs de la API (línea 85: `auth/register/`)

### Frontend
- `frontend/src/views/RegisterView.vue` - Vista de registro
- `frontend/src/services/authApi.js` - Servicio de API de autenticación
- `frontend/src/stores/auth.js` - Store de autenticación (Pinia)
- `frontend/src/composables/useAuth.js` - Composable de autenticación

---

## Notas Adicionales

- El usuario se crea con estado `is_active=False` hasta verificar el email
- Se genera un token de verificación con expiración de 24 horas
- El email de verificación contiene un enlace con el token
- En modo desarrollo, puede haber activación automática sin verificación
- Todos los eventos de registro se registran en auditoría
- El sistema previene ataques de fuerza bruta limitando intentos de registro

