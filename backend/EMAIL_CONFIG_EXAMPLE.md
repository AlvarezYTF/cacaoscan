# Configuración de Email para CacaoScan
# Copia este archivo como .env y configura tus valores

# ===========================================
# CONFIGURACIÓN BÁSICA DE EMAIL
# ===========================================

# Backend de email (smtp o sendgrid)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# Configuración SMTP (Gmail, Outlook, etc.)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password
EMAIL_TIMEOUT=30

# Email por defecto del sistema
DEFAULT_FROM_EMAIL=CacaoScan <noreply@cacaoscan.com>
SERVER_EMAIL=noreply@cacaoscan.com
ADMIN_EMAIL=admin@cacaoscan.com

# ===========================================
# CONFIGURACIÓN SENDGRID (OPCIONAL)
# ===========================================

# API Key de SendGrid (alternativa a SMTP)
SENDGRID_API_KEY=SG.tu_api_key_aqui
SENDGRID_FROM_EMAIL=noreply@cacaoscan.com

# ===========================================
# CONFIGURACIÓN DE NOTIFICACIONES
# ===========================================

# Habilitar notificaciones por email
EMAIL_NOTIFICATIONS_ENABLED=True

# Configuración de cola de emails (para producción)
EMAIL_QUEUE_ENABLED=False
EMAIL_BATCH_SIZE=50
EMAIL_RETRY_ATTEMPTS=3

# ===========================================
# INSTRUCCIONES DE CONFIGURACIÓN
# ===========================================

# 1. CONFIGURACIÓN CON GMAIL:
#    - Activa la verificación en 2 pasos
#    - Genera una "Contraseña de aplicación"
#    - Usa esa contraseña en EMAIL_HOST_PASSWORD
#    - Configura EMAIL_HOST_USER con tu email de Gmail

# 2. CONFIGURACIÓN CON SENDGRID:
#    - Crea una cuenta en SendGrid
#    - Genera una API Key
#    - Configura SENDGRID_API_KEY
#    - Cambia EMAIL_BACKEND a sendgrid si quieres usar solo SendGrid

# 3. CONFIGURACIÓN CON OUTLOOK/HOTMAIL:
#    - EMAIL_HOST=smtp-mail.outlook.com
#    - EMAIL_PORT=587
#    - EMAIL_USE_TLS=True
#    - Usa tu email y contraseña normal

# 4. CONFIGURACIÓN CON OTROS PROVEEDORES:
#    - Consulta la documentación de tu proveedor de email
#    - Ajusta EMAIL_HOST, EMAIL_PORT y EMAIL_USE_TLS según corresponda

# ===========================================
# VARIABLES DE DESARROLLO
# ===========================================

# Para desarrollo, puedes usar el backend de consola
# EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Para pruebas, puedes usar el backend de archivo
# EMAIL_BACKEND=django.core.mail.backends.filebased.EmailBackend
# EMAIL_FILE_PATH=/tmp/app-messages

# ===========================================
# NOTAS IMPORTANTES
# ===========================================

# - Nunca subas este archivo con credenciales reales a Git
# - Usa variables de entorno en producción
# - Considera usar servicios como AWS SES o Mailgun para producción
# - Configura SPF, DKIM y DMARC para mejorar la entrega de emails
# - Monitorea las tasas de rebote y spam
