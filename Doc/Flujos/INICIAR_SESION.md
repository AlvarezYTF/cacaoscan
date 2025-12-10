# Flujo de Inicio de Sesión con Comandos de Test

## Resumen del Flujo

El flujo de inicio de sesión en CacaoScan permite a un usuario autenticarse en el sistema utilizando sus credenciales (email/username y contraseña). El sistema valida las credenciales, genera tokens JWT y establece la sesión del usuario.

---

## Componentes del Flujo

### 1. Frontend (Vue.js)

**Archivo:** `frontend/src/views/LoginView.vue` o componente de login

- El usuario ingresa email/username y contraseña
- Se valida el formulario en el cliente
- Se envía petición POST a `/api/v1/auth/login/`
- Se almacenan los tokens JWT en el store/localStorage
- Se redirige al dashboard según el rol del usuario

**Código clave:**
```javascript
// Ejemplo de flujo en el frontend
const handleLogin = async (formData) => {
  try {
    const response = await authApi.login({
      email: formData.email,
      password: formData.password
    })
    
    // Almacenar tokens
    authStore.setTokens({
      access: response.data.access,
      refresh: response.data.refresh
    })
    
    // Almacenar datos del usuario
    authStore.setUser(response.data.user)
    
    // Redirigir según rol
    router.push(getDashboardRoute(response.data.user.role))
  } catch (error) {
    // Manejar errores de autenticación
  }
}
```

### 2. Backend - Vista (Django REST Framework)

**Archivo:** `backend/auth_app/views/auth/login_views.py`

**Vista:** `LoginView`

**Flujo:**
1. Recibe credenciales en `request.data`
2. Valida datos mediante `LoginSerializer`
3. Autentica usuario con `authenticate()`
4. Verifica que el usuario esté activo
5. Genera tokens JWT (access y refresh)
6. Establece sesión del usuario
7. Registra el inicio de sesión en auditoría
8. Retorna tokens y datos del usuario

**Código clave:**
```53:93:backend/auth_app/views/auth/login_views.py
    def post(self, request):
        """
        Autentica un usuario y devuelve tokens JWT.
        """
        try:
            serializer = LoginSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.validated_data['user']
                
                # Generar tokens JWT
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                # Login en la sesión
                login(request, user)
                
                return create_success_response(
                    message='Login exitoso',
                    data={
                        'access': str(access_token),
                        'refresh': str(refresh),
                        'user': UserSerializer(user).data,
                        'access_expires_at': access_token['exp'],
                        'refresh_expires_at': refresh['exp']
                    }
                )
            
            return create_error_response(
                message='Credenciales inválidas',
                error_type='invalid_credentials',
                status_code=status.HTTP_401_UNAUTHORIZED,
                details=serializer.errors
            )
        except Exception as e:
            logger.error(f"Error en LoginView: {str(e)}", exc_info=True)
            return create_error_response(
                message='Error interno del servidor',
                error_type='internal_server_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
```

### 3. Backend - Servicio

**Archivo:** `backend/api/services/auth/login_service.py`

**Servicio:** `LoginService`

Proporciona lógica de negocio para autenticación, validación de credenciales y generación de tokens.

---

## Endpoint de la API

**URL:** `POST /api/v1/auth/login/`

**Autenticación:** No requerida (AllowAny)

**Content-Type:** `application/json`

**Parámetros:**
- `email` o `username`: Email o nombre de usuario (requerido)
- `password`: Contraseña (requerido)

**Respuesta exitosa (200 OK):**
```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "email": "usuario@example.com",
      "username": "usuario",
      "first_name": "Juan",
      "last_name": "Pérez",
      "role": "agricultor",
      "is_active": true
    },
    "access_expires_at": 1234567890,
    "refresh_expires_at": 1234567890
  }
}
```

**Respuesta con errores (401 Unauthorized):**
```json
{
  "success": false,
  "message": "Credenciales inválidas",
  "error_type": "invalid_credentials",
  "details": {
    "non_field_errors": ["Credenciales inválidas."]
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

### Tests de Vistas (Login)

**Archivo:** `backend/auth_app/tests/test_login_views.py` (si existe)

#### Ejecutar todos los tests de login:

```bash
# Desde backend/
pytest auth_app/tests/test_login_views.py -v
```

#### Tests específicos (ejemplos esperados):

```bash
# Test: Login exitoso
pytest auth_app/tests/test_login_views.py::TestLoginView::test_post_success -v

# Test: Credenciales incorrectas
pytest auth_app/tests/test_login_views.py::TestLoginView::test_post_invalid_credentials -v

# Test: Usuario inactivo
pytest auth_app/tests/test_login_views.py::TestLoginView::test_post_inactive_user -v

# Test: Email no existe
pytest auth_app/tests/test_login_views.py::TestLoginView::test_post_user_not_found -v

# Test: Contraseña incorrecta
pytest auth_app/tests/test_login_views.py::TestLoginView::test_post_wrong_password -v

# Test: Campos requeridos faltantes
pytest auth_app/tests/test_login_views.py::TestLoginView::test_post_missing_fields -v
```

### Tests de Servicio (Login Service)

**Archivo:** `backend/api/tests/test_login_service.py` (si existe)

#### Ejecutar todos los tests del servicio:

```bash
# Desde backend/
pytest api/tests/test_login_service.py -v
```

#### Tests específicos:

```bash
# Test: Login exitoso mediante servicio
pytest api/tests/test_login_service.py::TestLoginService::test_login_user_success -v

# Test: Credenciales inválidas
pytest api/tests/test_login_service.py::TestLoginService::test_login_user_invalid_credentials -v

# Test: Usuario inactivo
pytest api/tests/test_login_service.py::TestLoginService::test_login_user_inactive -v

# Test: Generación de tokens JWT
pytest api/tests/test_login_service.py::TestLoginService::test_generate_tokens -v
```

### Tests de Serializers

**Archivo:** `backend/api/tests/test_auth_serializers.py` (si existe)

```bash
# Test: Validación de LoginSerializer
pytest api/tests/test_auth_serializers.py::TestLoginSerializer -v

# Test: Validación con email
pytest api/tests/test_auth_serializers.py::TestLoginSerializer::test_login_with_email -v

# Test: Validación con username
pytest api/tests/test_auth_serializers.py::TestLoginSerializer::test_login_with_username -v

# Test: Validación de contraseña incorrecta
pytest api/tests/test_auth_serializers.py::TestLoginSerializer::test_invalid_password -v
```

### Ejecutar Todos los Tests de Login

```bash
# Desde backend/
pytest auth_app/tests/ api/tests/test_login_service.py api/tests/test_auth_serializers.py -v -k login
```

### Ejecutar con Cobertura

```bash
# Desde backend/
pytest auth_app/tests/test_login_views.py --cov=auth_app.views.auth.login_views --cov-report=html
pytest api/tests/test_login_service.py --cov=api.services.auth.login_service --cov-report=html
```

---

## Flujo Completo Paso a Paso

### 1. Usuario ingresa credenciales en el frontend
- Validación inicial en el cliente (campos no vacíos)
- Preparación de datos para envío

### 2. Petición HTTP POST al backend
- Endpoint: `/api/v1/auth/login/`
- Headers: `Content-Type: application/json`
- Body: Credenciales en JSON

### 3. Backend procesa la petición
- **Validación de serializer:** `LoginSerializer` valida los datos
- **Autenticación:** `authenticate()` verifica credenciales
- **Validación de usuario activo:** Verifica que `is_active=True`
- **Generación de tokens:** Crea tokens JWT (access y refresh)
- **Establecimiento de sesión:** `login()` establece sesión
- **Auditoría:** Registra el inicio de sesión con IP y user agent

### 4. Respuesta al frontend
- **200 OK:** Login exitoso con tokens y datos del usuario
- **401 Unauthorized:** Credenciales inválidas

### 5. Frontend procesa la respuesta
- Almacena tokens JWT en localStorage/sessionStorage
- Almacena datos del usuario en el store
- Configura headers de autenticación para futuras peticiones
- Redirige al dashboard según rol del usuario

---

## Validaciones Implementadas

### Credenciales
- **Email/Username:** Debe existir en el sistema
- **Password:** Debe ser correcta
- **Validación:** En backend mediante `authenticate()`
- **Error:** "Credenciales inválidas" (genérico, no revela cuál campo es incorrecto)

### Usuario Activo
- **Estado:** El usuario debe tener `is_active=True`
- **Validación:** En backend después de autenticación
- **Error:** "Usuario inactivo" o "Cuenta desactivada"

### Límite de Intentos
- **Máximo:** 5 intentos fallidos antes de bloqueo temporal
- **Duración:** 30 minutos de bloqueo
- **Validación:** En backend mediante rate limiting
- **Error:** "Demasiados intentos fallidos. Intenta más tarde."

---

## Ejemplo de Uso con cURL

```bash
# Iniciar sesión con email
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "Password123!"
  }'

# Iniciar sesión con username
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "usuario",
    "password": "Password123!"
  }'
```

---

## Troubleshooting

### Error: "Credenciales inválidas"
**Causa:** El email/username o contraseña son incorrectos, o el usuario no existe.
**Solución:** Verificar credenciales, usar recuperación de contraseña si es necesario.

### Error: "Usuario inactivo"
**Causa:** El usuario no ha verificado su email o fue desactivado.
**Solución:** Verificar email o contactar al administrador.

### Error: "Demasiados intentos fallidos"
**Causa:** Se excedió el límite de intentos fallidos (5).
**Solución:** Esperar 30 minutos o usar recuperación de contraseña.

### Error: Tokens no se almacenan correctamente
**Causa:** Problema con localStorage/sessionStorage o configuración del store.
**Solución:** Verificar configuración del store de autenticación y manejo de tokens.

### Error: Redirección incorrecta después de login
**Causa:** Lógica de redirección según rol no configurada correctamente.
**Solución:** Verificar función `getDashboardRoute()` y configuración de rutas.

---

## Archivos Relacionados

### Backend
- `backend/auth_app/views/auth/login_views.py` - Vistas de login
- `backend/api/services/auth/login_service.py` - Servicio de login
- `backend/api/serializers/auth_serializers.py` - Serializers de autenticación
- `backend/api/urls.py` - URLs de la API (línea 84: `auth/login/`)

### Frontend
- `frontend/src/views/LoginView.vue` - Vista de login
- `frontend/src/services/authApi.js` - Servicio de API de autenticación
- `frontend/src/stores/auth.js` - Store de autenticación (Pinia)
- `frontend/src/composables/useAuth.js` - Composable de autenticación
- `frontend/src/router/index.js` - Configuración de rutas y guards

---

## Notas Adicionales

- Los tokens JWT tienen expiración: access token (60 minutos), refresh token (7 días)
- El sistema registra todos los intentos de login (exitosos y fallidos) en auditoría
- Se implementa protección contra ataques de fuerza bruta mediante rate limiting
- El mensaje de error es genérico para no revelar si el email o contraseña son incorrectos
- La sesión se establece mediante `login()` para compatibilidad con sesiones Django
- Los tokens se pueden usar para autenticación en peticiones subsiguientes mediante header `Authorization: Bearer <token>`

