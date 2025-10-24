# 🧪 Tests de Autenticación - CacaoScan

## 📋 Instrucciones para Ejecutar Tests

### 1. Activar Entorno Virtual
```bash
# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar Migraciones
```bash
cd backend
python manage.py makemigrations api
python manage.py migrate
```

### 4. Ejecutar Tests
```bash
# Ejecutar todos los tests de autenticación
python manage.py test tests.test_auth

# Ejecutar tests específicos
python manage.py test tests.test_auth.AuthenticationTestCase.test_registration_success

# Ejecutar con verbose
python manage.py test tests.test_auth -v 2
```

## 🧪 Tests Incluidos

### AuthenticationTestCase
- ✅ **test_registration_success**: Registro exitoso con auto-login
- ✅ **test_registration_validation_errors**: Validaciones de registro
- ✅ **test_login_success**: Login exitoso
- ✅ **test_login_invalid_credentials**: Credenciales inválidas
- ✅ **test_protected_endpoint_access**: Acceso a endpoints protegidos
- ✅ **test_token_expiration**: Expiración de tokens
- ✅ **test_email_verification**: Verificación de email
- ✅ **test_email_verification_expired_token**: Token expirado
- ✅ **test_resend_verification**: Reenvío de verificación
- ✅ **test_logout**: Logout exitoso

### TokenCleanupTestCase
- ✅ **test_token_cleanup**: Limpieza automática de tokens expirados

### UserRoleTestCase
- ✅ **test_farmer_role_assignment**: Asignación automática de rol farmer
- ✅ **test_admin_role_no_auto_assignment**: Usuarios staff no reciben rol farmer

## 🔧 Configuración de Tests

Los tests utilizan:
- **APITestCase**: Para tests de endpoints REST
- **TestCase**: Para tests de modelos y lógica de negocio
- **Base de datos de prueba**: Automáticamente creada y destruida
- **Datos de prueba**: Configurados en `setUp()` de cada clase

## 📊 Cobertura de Tests

### Backend (Django)
- ✅ Registro de usuarios
- ✅ Login/Logout
- ✅ Verificación de email
- ✅ Expiración de tokens
- ✅ Asignación de roles
- ✅ Limpieza automática
- ✅ Validaciones de seguridad
- ✅ Endpoints protegidos

### Funcionalidades Probadas
- ✅ Auto-login tras registro
- ✅ Tokens con expiración (24 horas)
- ✅ Verificación de email opcional
- ✅ Asignación automática de rol farmer
- ✅ Limpieza de tokens expirados
- ✅ Validaciones robustas
- ✅ Manejo de errores consistente

## 🚀 Ejecución en CI/CD

Para integración continua, usar:
```bash
python manage.py test --keepdb --parallel
```

## 📝 Notas Importantes

1. **Base de datos**: Los tests usan una base de datos temporal
2. **Tokens**: Se crean y eliminan automáticamente
3. **Usuarios**: Se crean con datos de prueba específicos
4. **Limpieza**: Cada test es independiente y limpio
5. **Cobertura**: Todos los casos de uso críticos están cubiertos
