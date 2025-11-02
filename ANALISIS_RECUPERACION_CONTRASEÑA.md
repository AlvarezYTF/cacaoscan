# 🔍 Análisis Detallado del Sistema de Recuperación de Contraseñas - CacaoScan

## 📋 Índice
1. [Componentes Identificados](#componentes-identificados)
2. [Flujo Actual Paso a Paso](#flujo-actual)
3. [Configuración de Email](#configuracion-email)
4. [Problemas Identificados](#problemas-identificados)
5. [Propuesta de Mejora Mínima](#propuesta-mejora)

---

## 1. Componentes Identificados

### 🔧 Vistas (Views)

#### **`ForgotPasswordView`** (`backend/api/views.py:2154-2238`)
- **Endpoint**: `POST /api/v1/auth/forgot-password/`
- **Permisos**: `AllowAny` (público)
- **Ubicación**: `backend/api/views.py`, línea 2154
- **Responsabilidad**: Recibe el email del usuario y genera token de recuperación

#### **`ResetPasswordView`** (`backend/api/views.py:2241-2332`)
- **Endpoint**: `POST /api/v1/auth/reset-password/`
- **Permisos**: `AllowAny` (público)
- **Ubicación**: `backend/api/views.py`, línea 2241
- **Responsabilidad**: Valida el token y restablece la contraseña

#### **`ChangePasswordView`** (`backend/api/views.py:1230`)
- **Endpoint**: `POST /api/v1/auth/change-password/`
- **Permisos**: `IsAuthenticated`
- **Responsabilidad**: Cambio de contraseña cuando el usuario ya está autenticado

#### **Vistas Alternativas** (`backend/api/refactored_views.py`)
- **`ForgotPasswordView`** (línea 369): Versión que usa `auth_service`
- **`ResetPasswordView`** (línea 431): Versión que usa `auth_service`

### 📝 Serializers

#### **`ChangePasswordSerializer`** (`backend/api/serializers.py:254`)
- Valida cambio de contraseña cuando el usuario está autenticado
- Campos: `old_password`, `new_password`, `confirm_password`

### 🗄️ Modelos

#### **`EmailVerificationToken`** (`backend/auth_app/models.py:14-78`)
- **Modelo utilizado para tokens de recuperación** (reutilizado de verificación de email)
- **Campos clave**:
  - `user`: OneToOneField con User
  - `token`: UUIDField (UUID único)
  - `created_at`: DateTimeField (auto_now_add)
  - `is_verified`: BooleanField (default=False)
  - `verified_at`: DateTimeField (nullable)
- **Expiración**: 24 horas (`EXPIRATION_HOURS = 24`)
- **Métodos importantes**:
  - `create_for_user(user)`: Crea nuevo token y elimina tokens anteriores
  - `get_valid_token(token_uuid)`: Valida y retorna token si no está expirado
  - `is_expired`: Property que verifica expiración
  - `verify()`: Marca token como verificado

### 📧 Templates de Email

#### **`password_reset.html`** (`backend/api/templates/emails/password_reset.html`)
- Template HTML con diseño profesional
- Variables esperadas:
  - `user_name`
  - `user_email`
  - `token`
  - `reset_url`
  - `token_expiry_hours`
  - `current_year`

#### **`password_reset.txt`** (`backend/api/templates/emails/password_reset.txt`)
- Versión en texto plano del email

### 🔗 URLs Configuradas

```python
# backend/api/urls.py
path('auth/forgot-password/', views.ForgotPasswordView.as_view(), name='auth-forgot-password'),
path('auth/reset-password/', views.ResetPasswordView.as_view(), name='auth-reset-password'),
path('auth/change-password/', views.ChangePasswordView.as_view(), name='auth-change-password'),
```

### 🛠️ Servicios

#### **`AuthenticationService`** (`backend/api/services/auth_service.py`)
- **`forgot_password(email, request)`** (línea 407-464): Lógica de negocio para solicitar recuperación
- **`reset_password(token, new_password, confirm_password)`** (línea 466-542): Lógica de negocio para restablecer contraseña

#### **`EmailService`** / **`EmailNotificationService`** (`backend/api/email_service.py`)
- **`send_email_notification()`**: Envía emails usando templates
- Soporta tipo `'password_reset'` (línea 409)

---

## 2. Flujo Actual Paso a Paso

### 🔐 Flujo de Solicitud de Recuperación (`ForgotPasswordView`)

1. **Usuario solicita recuperación**:
   - Frontend envía `POST /api/v1/auth/forgot-password/`
   - Body: `{"email": "usuario@example.com"}`

2. **Backend procesa solicitud** (`views.py:2185-2238`):
   ```python
   # 1. Valida que email esté presente
   email = request.data.get('email')
   
   # 2. Busca usuario por email
   user = User.objects.get(email=email)
   
   # 3. Crea token de recuperación (reutiliza EmailVerificationToken)
   reset_token = EmailVerificationToken.create_for_user(user)
   
   # 4. Construye URL de restablecimiento
   reset_url = f"{request.build_absolute_uri('/')}auth/reset-password/?token={reset_token.token}"
   
   # 5. Prepara contexto para el email
   email_context = {
       'user_name': user.get_full_name() or user.username,
       'user_email': user.email,
       'token': str(reset_token.token),
       'reset_url': reset_url,
       'token_expiry_hours': 24
   }
   
   # 6. Intenta enviar email
   email_result = send_email_notification(
       user_email=user.email,
       notification_type='password_reset',
       context=email_context
   )
   
   # 7. Retorna éxito (aunque el email falle)
   return create_success_response(
       message=f'Instrucciones de recuperación enviadas a {email}',
       data={'token': str(reset_token.token), 'expires_at': ...}
   )
   ```

3. **Problema**: El email puede fallar silenciosamente, pero siempre retorna éxito

### 🔑 Flujo de Restablecimiento (`ResetPasswordView`)

1. **Usuario ingresa nueva contraseña**:
   - Frontend envía `POST /api/v1/auth/reset-password/`
   - Body: `{"token": "uuid-here", "new_password": "...", "confirm_password": "..."}`

2. **Backend valida y restablece** (`views.py:2274-2332`):
   ```python
   # 1. Valida campos requeridos
   if not all([token_uuid, new_password, confirm_password]): ...
   
   # 2. Valida que contraseñas coincidan
   if new_password != confirm_password: ...
   
   # 3. Valida fortaleza (mínimo 8 caracteres)
   if len(new_password) < 8: ...
   
   # 4. Obtiene y valida token
   token_obj = EmailVerificationToken.get_valid_token(token_uuid)
   if not token_obj: ...
   
   # 5. Restablece contraseña
   user = token_obj.user
   user.set_password(new_password)
   user.save()
   
   # 6. Elimina token (ya usado)
   token_obj.delete()
   
   # 7. Retorna éxito
   return create_success_response(...)
   ```

### 📧 Flujo de Envío de Email

1. **Llamada a `send_email_notification()`** (`email_service.py:482`)
2. **Busca template** `password_reset.html` y `password_reset.txt`
3. **Renderiza template** con contexto
4. **Envía usando Django Email Backend** configurado

---

## 3. Configuración de Email

### ✅ Configuración Actual (`settings.py:302-319`)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ch4130949@gmail.com'
EMAIL_HOST_PASSWORD = 'scdtfcpicnqjmiyo'  # App Password de Gmail
DEFAULT_FROM_EMAIL = 'ch4130949@gmail.com' o 'CacaoScan <noreply@cacaoscan.com>'
FRONTEND_URL = 'http://localhost:5173'
```

### ✅ Estado de Configuración
- **✅ Backend SMTP configurado**: Gmail con TLS
- **✅ Credenciales presentes**: Usuario y App Password
- **✅ Templates existentes**: HTML y TXT
- **✅ Servicio de email implementado**: `EmailNotificationService`

---

## 4. Problemas Identificados

### 🔴 Problema 1: Email NO se envía desde la vista principal

**Ubicación**: `backend/api/views.py:2204-2224`

**Código problemático**:
```python
# Enviar email de restablecimiento de contraseña
try:
    from .email_service import send_email_notification
    email_result = send_email_notification(...)
    if email_result['success']:
        logger.info(f"Email de restablecimiento enviado...")
    else:
        logger.error(f"Error enviando email...")  # ⚠️ Solo log, no propaga error
except Exception as e:
    logger.error(f"Error en envío de email...")  # ⚠️ Solo log, no propaga error

# ⚠️ SIEMPRE retorna éxito aunque el email falle
return create_success_response(...)
```

**Impacto**: El usuario recibe mensaje de éxito, pero nunca llega el email.

**Causa**: El bloque try-except captura todos los errores y no los propaga.

### 🔴 Problema 2: URL de restablecimiento incorrecta

**Ubicación**: `backend/api/views.py:2211`

**Código problemático**:
```python
reset_url = f"{request.build_absolute_uri('/')}auth/reset-password/?token={reset_token.token}"
```

**Problema**: 
- `request.build_absolute_uri('/')` genera URL del backend (`http://localhost:8000/`)
- Debería apuntar al frontend (`http://localhost:5173/auth/reset-password/...`)

**Impacto**: El enlace en el email apunta al backend, no al frontend.

**Solución esperada**:
```python
reset_url = f"{settings.FRONTEND_URL}/auth/reset-password/?token={reset_token.token}"
```

### 🔴 Problema 3: Vista duplicada / inconsistente

**Existen DOS versiones de `ForgotPasswordView` y `ResetPasswordView`**:
1. **`backend/api/views.py`** (líneas 2154, 2241): Versión directa que no usa `auth_service`
2. **`backend/api/refactored_views.py`** (líneas 369, 431): Versión que usa `auth_service`

**Problema**: 
- `auth_service.forgot_password()` **SÍ crea el token**, pero **NO envía el email** (línea 407-450)
- Solo registra en logs y auditoría, pero no hay llamada a `send_email_notification()`

**Impacto**: Si se usa `refactored_views.py`, el email nunca se envía.

### 🔴 Problema 4: Token no está marcado como "para recuperación"

**Modelo**: `EmailVerificationToken` es compartido entre:
- Verificación de email (registro)
- Recuperación de contraseña

**Problema**: 
- No hay distinción entre tipos de token
- Si un usuario solicita recuperación y luego verifica email, pueden colisionar

### 🟡 Problema 5: Falta manejo de errores de SMTP

**Si Gmail rechaza el email** (App Password incorrecta, cuenta bloqueada, etc.):
- Error se captura silenciosamente
- Usuario nunca se entera
- No hay retry o notificación al admin

### 🟡 Problema 6: El servicio `auth_service` no envía emails

**Ubicación**: `backend/api/services/auth_service.py:407-450`

**Código**:
```python
def forgot_password(self, email: str, request=None) -> ServiceResult:
    # ... crea token ...
    reset_token = EmailVerificationToken.create_for_user(user)
    # ... registra en logs ...
    # ❌ NO HAY LLAMADA A send_email_notification()
    return ServiceResult.success(...)
```

**Impacto**: Si se usa `refactored_views.py`, el email nunca se envía.

---

## 5. Propuesta de Mejora Mínima

### 🎯 Objetivo
Hacer funcional el sistema en **1 hora** sin eliminar código existente, solo corrigiendo los puntos críticos.

### ✅ Cambios Necesarios (Mínimos)

#### **1. Corregir URL de restablecimiento en `ForgotPasswordView`**

**Archivo**: `backend/api/views.py`, línea 2211

**Cambio**:
```python
# ANTES
reset_url = f"{request.build_absolute_uri('/')}auth/reset-password/?token={reset_token.token}"

# DESPUÉS
from django.conf import settings
reset_url = f"{settings.FRONTEND_URL}/auth/reset-password/?token={reset_token.token}"
```

#### **2. Agregar manejo de errores de email con logging visible**

**Archivo**: `backend/api/views.py`, líneas 2204-2224

**Cambio**:
```python
# Enviar email de restablecimiento de contraseña
try:
    from .email_service import send_email_notification
    email_context = {
        'user_name': user.get_full_name() or user.username,
        'user_email': user.email,
        'token': str(reset_token.token),
        'reset_url': f"{settings.FRONTEND_URL}/auth/reset-password/?token={reset_token.token}",
        'token_expiry_hours': 24,
        'current_year': timezone.now().year
    }
    email_result = send_email_notification(
        user_email=user.email,
        notification_type='password_reset',
        context=email_context
    )
    if email_result['success']:
        logger.info(f"[SUCCESS] Email de restablecimiento enviado a {user.email}")
    else:
        logger.error(f"[ERROR] Error enviando email de restablecimiento: {email_result.get('error')}")
            # NO fallar silenciosamente - log claro
except Exception as e:
    logger.error(f"[ERROR] Excepción enviando email de restablecimiento: {e}", exc_info=True)
    # Log completo para debugging
```

**Nota**: Mantener retorno de éxito por seguridad (no revelar si email existe), pero con logging claro.

#### **3. Agregar envío de email en `auth_service.forgot_password()`**

**Archivo**: `backend/api/services/auth_service.py`, línea 407-450

**Agregar después de crear el token** (línea 429):
```python
def forgot_password(self, email: str, request=None) -> ServiceResult:
    try:
        # ... validación y creación de token ...
        reset_token = EmailVerificationToken.create_for_user(user)
        
        # ✅ AGREGAR: Enviar email de recuperación
        try:
            from ..email_service import send_email_notification
            from django.conf import settings
            
            email_context = {
                'user_name': user.get_full_name() or user.username,
                'user_email': user.email,
                'token': str(reset_token.token),
                'reset_url': f"{settings.FRONTEND_URL}/auth/reset-password/?token={reset_token.token}",
                'token_expiry_hours': 24,
                'current_year': timezone.now().year
            }
            
            email_result = send_email_notification(
                user_email=user.email,
                notification_type='password_reset',
                context=email_context
            )
            
            if email_result['success']:
                self.log_info(f"Email de restablecimiento enviado a {user.email}")
            else:
                self.log_error(f"Error enviando email: {email_result.get('error')}")
        except Exception as e:
            self.log_error(f"Excepción enviando email: {e}", exc_info=True)
        
        # ... resto del código ...
```

#### **4. Verificar que `current_year` esté en el contexto**

**El template espera `current_year`** pero no se está pasando en la vista principal.

**Solución**: Agregar `'current_year': timezone.now().year` al contexto.

### ✅ Verificación Post-Implementación

1. **Probar solicitud de recuperación**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/forgot-password/ \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com"}'
   ```

2. **Verificar logs**:
   - Buscar `[SUCCESS] Email de restablecimiento enviado` o `[ERROR]`
   - Revisar `backend/logs/django.log`

3. **Verificar email recibido**:
   - Revisar bandeja de entrada de `test@example.com`
   - Verificar que el enlace apunte a `http://localhost:5173/auth/reset-password/?token=...`

4. **Probar restablecimiento**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/reset-password/ \
     -H "Content-Type: application/json" \
     -d '{"token": "uuid-aqui", "new_password": "nueva123", "confirm_password": "nueva123"}'
   ```

### 🎯 Resumen de Cambios (1 hora)

1. ✅ Corregir URL en `views.py:2211` (usar `FRONTEND_URL`)
2. ✅ Mejorar logging en `views.py:2204-2224` (agregar `current_year`)
3. ✅ Agregar envío de email en `auth_service.py:429` (después de crear token)
4. ✅ Verificar configuración de Gmail (App Password válida)

**Total**: 4 cambios pequeños, **sin eliminar código**, solo agregando lo faltante.

---

## 📊 Resumen Ejecutivo

### ✅ Lo que está bien
- Configuración de Gmail activa
- Templates de email completos
- Modelo de token funcional
- Validación de contraseña robusta
- URLs correctamente configuradas

### 🔴 Lo que está roto
- **Email no se envía** (falta llamada en `auth_service`)
- **URL apunta al backend** (debe apuntar al frontend)
- **Error silencioso** (no hay logging adecuado)

### ✅ Solución mínima
**4 cambios pequeños** que agregan lo faltante sin romper nada existente.

---

**Fin del análisis**

