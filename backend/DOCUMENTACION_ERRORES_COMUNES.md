# Documentación de Errores Comunes

## Error 500 en `/api/v1/auth/forgot-password/`

### Síntoma
```
POST /api/v1/auth/forgot-password/ 500 (Internal Server Error)
{
    "success": false,
    "message": "Error al enviar el correo. Intente nuevamente más tarde."
}
```

### Causa
El servicio de email no está configurado correctamente o las credenciales SMTP son inválidas.

### Solución

1. **Verificar configuración SMTP en `.env`**:
   ```env
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=tu-email@gmail.com
   EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicación
   EMAIL_FROM_ADDRESS=noreply@cacaoscan.com
   ```

2. **Para Gmail, usar "Contraseña de aplicación"**:
   - Ve a tu cuenta de Google
   - Seguridad > Verificación en 2 pasos (debe estar activada)
   - Contraseñas de aplicaciones > Generar nueva
   - Usa esa contraseña en `EMAIL_HOST_PASSWORD`

3. **Verificar logs del servidor**:
   ```bash
   # Revisar logs de Django para ver el error específico
   tail -f logs/django.log | grep FORGOT_PASSWORD
   ```

4. **Probar configuración de email**:
   ```python
   # En Django shell
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
   ```

5. **Si el email no es crítico en desarrollo**, puedes deshabilitar temporalmente el envío de emails modificando `settings.py`:
   ```python
   # Para desarrollo: usar backend de consola
   EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
   ```

## Error 403 de Google OAuth

### Síntoma
```
[GSI_LOGGER]: The given origin is not allowed for the given client ID.
```

### Causa
El origen (URL) desde el que se está intentando usar Google OAuth no está autorizado en la configuración del cliente OAuth en Google Cloud Console.

### Solución

1. **Ir a Google Cloud Console**:
   - https://console.cloud.google.com/
   - Selecciona tu proyecto

2. **Configurar OAuth Client**:
   - Ve a "APIs & Services" > "Credentials"
   - Encuentra tu OAuth 2.0 Client ID (el que está en `GOOGLE_CLIENT_ID`)
   - Haz clic en editar

3. **Agregar orígenes autorizados**:
   - En "Authorized JavaScript origins", agrega:
     - `http://localhost:8000` (desarrollo)
     - `http://localhost:5173` (si usas Vite)
     - `https://tu-dominio.com` (producción)

4. **Agregar URIs de redirección**:
   - En "Authorized redirect URIs", agrega:
     - `http://localhost:8000/api/v1/auth/google-login/`
     - `https://tu-dominio.com/api/v1/auth/google-login/`

5. **Guardar y esperar**:
   - Guarda los cambios
   - Espera 5-10 minutos para que los cambios se propaguen
   - Recarga la página de la aplicación

### Nota
Si estás en desarrollo local, asegúrate de que el puerto coincida exactamente con el que está configurado en Google Cloud Console.

## Verificación de Configuración

### Verificar configuración de email
```bash
# En el backend
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_HOST)
>>> print(settings.EMAIL_PORT)
>>> print(settings.EMAIL_USE_TLS)
```

### Verificar configuración de Google OAuth
```bash
# En el frontend, en la consola del navegador
console.log('Google Client ID:', GOOGLE_CLIENT_ID)
```

## Logs Útiles

### Backend (Django)
```bash
# Ver logs de autenticación
tail -f logs/django.log | grep -E "(FORGOT_PASSWORD|GOOGLE|AUTH)"

# Ver todos los errores
tail -f logs/django.log | grep ERROR
```

### Frontend (Navegador)
- Abre las herramientas de desarrollador (F12)
- Ve a la pestaña "Console"
- Filtra por "ERROR" o "GSI_LOGGER"

## Contacto

Si estos problemas persisten después de seguir las soluciones, contacta al equipo de desarrollo con:
- El error completo del log
- La configuración (sin credenciales sensibles)
- El entorno (desarrollo/producción)



