# 📋 Documentación Completa de Casos de Uso - CacaoScan
## Información para Construcción de Diagramas de Flujo

---

## 📌 Índice

1. [Registrar Usuario](#caso-de-uso-1-registrar-usuario)
2. [Iniciar Sesión](#caso-de-uso-2-iniciar-sesión)
3. [Subir Imagen](#caso-de-uso-3-subir-imagen)
4. [Procesar Imagen](#caso-de-uso-4-procesar-imagen)
5. [Analizar Imagen](#caso-de-uso-5-analizar-imagen)
6. [Ver Resultados](#caso-de-uso-6-ver-resultados)
7. [Descargar Reporte](#caso-de-uso-7-descargar-reporte)
8. [Crear Finca](#caso-de-uso-8-crear-finca)
9. [Editar Finca](#caso-de-uso-9-editar-finca)
10. [Crear Lote](#caso-de-uso-10-crear-lote)
11. [Editar Lote](#caso-de-uso-11-editar-lote)
12. [Eliminar Lote](#caso-de-uso-12-eliminar-lote)
13. [Ver Historial](#caso-de-uso-13-ver-historial)
14. [Buscar Análisis](#caso-de-uso-14-buscar-análisis)
15. [Entrenar Modelo](#caso-de-uso-15-entrenar-modelo)
16. [Crear Agricultor](#caso-de-uso-16-crear-agricultor)
17. [Editar Agricultor](#caso-de-uso-17-editar-agricultor)
18. [Asignar Rol](#caso-de-uso-18-asignar-rol)
19. [Editar Perfil](#caso-de-uso-19-editar-perfil)

---

## Caso de Uso 1: Registrar Usuario

**Actor(es):** Usuario no autenticado (Visitante)

**Descripción del proceso:** Permite a un nuevo usuario crear una cuenta en el sistema mediante un formulario de registro que incluye validación de email, creación de credenciales y envío de verificación por correo electrónico.

**Evento de inicio:** El usuario accede a la página de registro (`/registro`) y completa el formulario con sus datos personales.

**Precondiciones:**
- El usuario no tiene una cuenta activa en el sistema
- El sistema está disponible y operativo
- El servicio de email está configurado (para verificación)

**Postcondiciones:**
- Se crea un nuevo registro de usuario en el sistema (inactivo inicialmente)
- Se genera un token de verificación de email
- Se envía un email de verificación al usuario
- Se crea un registro de auditoría del registro
- El usuario queda en estado "pendiente de verificación"

### ✔ Flujo Principal

1. Usuario accede a la ruta `/registro`
2. Sistema muestra formulario de registro
3. Usuario completa campos obligatorios:
   - Email (usado como username)
   - Contraseña
   - Confirmación de contraseña
   - Nombre (first_name)
   - Apellido (last_name)
4. Frontend valida formato de email en tiempo real
5. Frontend valida que las contraseñas coincidan
6. Frontend valida fortaleza de contraseña (mínimo 8 caracteres, letras y números)
7. Usuario hace clic en "Registrarse"
8. Frontend envía POST a `/api/v1/auth/register/` con los datos
9. Backend recibe petición en `RegisterView.post()`
10. `RegisterSerializer` valida los datos recibidos
11. Se ejecuta `RegistrationService.register_user_with_email_verification()`
12. Servicio valida que el email no esté registrado
13. Servicio valida fortaleza de contraseña con `validate_password_strength()`
14. Servicio crea usuario con `User.objects.create_user()` (is_active=False)
15. Servicio crea token de verificación con `EmailVerificationToken.create_for_user()`
16. Servicio genera tokens JWT (access y refresh)
17. Servicio crea log de auditoría del registro
18. Servicio envía email de verificación (si está configurado)
19. Backend retorna respuesta 201 con datos del usuario y token de verificación
20. Frontend muestra mensaje de éxito y redirige a página de verificación de email
21. Usuario recibe email con link de verificación

### ✔ Flujos Alternativos

**A1. Email ya registrado:**
- 3.1. Usuario ingresa email que ya existe
- 3.2. Backend valida duplicado en `RegisterSerializer.validate()`
- 3.3. Se retorna error 400: "Este email ya está registrado"
- 3.4. Frontend muestra mensaje de error específico

**A2. Contraseñas no coinciden:**
- 5.1. Usuario ingresa contraseñas diferentes
- 5.2. Frontend valida en tiempo real y muestra error
- 5.3. Backend valida con `validate_passwords_match()`
- 5.4. Se retorna error 400 si no coinciden

**A3. Contraseña débil:**
- 6.1. Usuario ingresa contraseña que no cumple requisitos
- 6.2. Frontend valida en tiempo real y muestra requisitos
- 6.3. Backend valida con `validate_password_strength()`
- 6.4. Se retorna error 400 con requisitos no cumplidos

**A4. Pre-registro (verificación previa):**
- 1.1. Usuario accede a endpoint `/api/v1/auth/preregistro/`
- 1.2. Sistema guarda datos temporalmente sin crear usuario
- 1.3. Se envía email de verificación
- 1.4. Usuario verifica email con token
- 1.5. Se crea usuario final en `VerifyEmailPreRegistrationView`

### ✔ Errores y Excepciones

- **400 Bad Request:** Datos inválidos, email duplicado, contraseñas no coinciden
- **500 Internal Server Error:** Error en base de datos, error enviando email
- **Email no enviado:** Sistema continúa, pero usuario debe usar resend verification

### ✔ Puntos de Decisión

- ¿Email ya existe? → Sí: Error, No: Continuar
- ¿Contraseñas coinciden? → No: Error, Sí: Continuar
- ¿Contraseña cumple requisitos? → No: Error, Sí: Continuar
- ¿Servicio de email disponible? → No: Continuar sin email, Sí: Enviar email

### ✔ Backend

**Endpoint(s):**
- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/preregistro/` (alternativo)
- `GET /api/v1/auth/verificar/<uuid:token>/` (verificación)

**View / ViewSet:**
- `RegisterView` (`backend/auth_app/views/auth/registration_views.py:24`)
- `PreRegisterView` (`backend/auth_app/views/auth/registration_views.py:94`)
- `VerifyEmailPreRegistrationView` (`backend/auth_app/views/auth/registration_views.py:169`)

**Serializers:**
- `RegisterSerializer` (`backend/api/serializers/auth_serializers.py:94`)

**Models:**
- `User` (Django User model)
- `EmailVerificationToken` (`backend/auth_app/models.py:14`)
- `ActivityLog` (auditoría)

**Services:**
- `RegistrationService` (`backend/api/services/auth/registration_service.py:22`)
  - `register_user_with_email_verification()`
  - `register_user()`
  - `_validate_user_registration_data()`
  - `_create_user_from_data()`

**Validaciones aplicadas:**
- Email único en el sistema
- Email con formato válido
- Contraseña: mínimo 8 caracteres, letras y números
- Contraseñas coinciden
- Nombre y apellido no vacíos
- Username igual a email

### ✔ Frontend

**Componente(s) involucrado(s):**
- `RegisterView.vue` (`frontend/src/views/Auth/RegisterView.vue`)
- `RegisterForm.vue` (si existe como componente separado)

**Acciones del usuario:**
- Completar formulario de registro
- Hacer clic en botón "Registrarse"
- Verificar email (opcional)

**Validaciones previas:**
- Validación de formato de email en tiempo real
- Validación de coincidencia de contraseñas en tiempo real
- Validación de fortaleza de contraseña en tiempo real
- Validación de campos requeridos

**Estado global (Pinia) usado:**
- `useAuthStore` (`frontend/src/stores/auth.js`)
  - `register()`: Registra usuario
  - `isLoading`: Estado de carga
  - `error`: Manejo de errores

**Rutas frontend:**
- `/registro` → `RegisterView.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Usuario no registrado → Registrando → Usuario creado (inactivo) → Verificando email → Usuario activo

**Condiciones:**
- Email único: `User.objects.filter(email=email).exists()`
- Contraseñas coinciden: `password == password_confirm`
- Contraseña válida: `validate_password_strength(password)`
- Servicio email disponible: `settings.EMAIL_BACKEND`

**Bifurcaciones:**
- Email existe? → Sí: Error, No: Crear usuario
- Validación exitosa? → Sí: Crear usuario, No: Retornar errores
- Email enviado? → Sí: Mostrar mensaje, No: Continuar

**Actividades del usuario:**
- Acceder a `/registro`
- Completar formulario
- Enviar datos
- Verificar email (opcional)

**Actividades del sistema:**
- Mostrar formulario
- Validar datos en frontend
- Enviar POST a API
- Validar datos en backend
- Crear usuario
- Generar token verificación
- Enviar email
- Crear log auditoría
- Retornar respuesta

**Acciones automáticas:**
- Validación en tiempo real de campos
- Generación de token de verificación
- Envío de email (si configurado)
- Asignación automática de rol "farmer" (por signal)

**Procesos asincrónicos:**
- Envío de email (puede ser asíncrono si se usa Celery)
- No hay procesos Celery para registro directo

---

## Caso de Uso 2: Iniciar Sesión

**Actor(es):** Usuario con cuenta existente

**Descripción del proceso:** Permite a un usuario autenticarse en el sistema proporcionando sus credenciales (email/username y contraseña), obteniendo tokens JWT para acceso a recursos protegidos.

**Evento de inicio:** El usuario accede a la página de login (`/login`) e ingresa sus credenciales.

**Precondiciones:**
- El usuario tiene una cuenta creada en el sistema
- El usuario tiene su email/username y contraseña
- La cuenta del usuario está activa (is_active=True)
- El email del usuario está verificado (si se requiere verificación)

**Postcondiciones:**
- El usuario queda autenticado en el sistema
- Se generan tokens JWT (access y refresh)
- Se registra el inicio de sesión en auditoría
- Se actualiza el historial de logins
- El usuario puede acceder a recursos protegidos

### ✔ Flujo Principal

1. Usuario accede a la ruta `/login`
2. Sistema muestra formulario de login
3. Usuario ingresa email o username
4. Usuario ingresa contraseña
5. Frontend valida que los campos no estén vacíos
6. Usuario hace clic en "Iniciar Sesión"
7. Frontend envía POST a `/api/v1/auth/login/` con credenciales
8. Backend recibe petición en `LoginView.post()`
9. `LoginSerializer` valida y normaliza datos (username/email)
10. `LoginSerializer.validate()` autentica usuario con `authenticate()`
11. Se valida que el usuario existe y credenciales son correctas
12. Se valida que el usuario está activo (`is_active=True`)
13. Se valida verificación de email si aplica (`_validate_user_active()`)
14. Se genera refresh token con `RefreshToken.for_user(user)`
15. Se genera access token desde refresh token
16. Se ejecuta `login(request, user)` para sesión Django (opcional)
17. Se registra login en `LoginHistory` (auditoría)
18. Se crea log de auditoría con `create_audit_log()`
19. Backend retorna respuesta 200 con tokens y datos del usuario
20. Frontend guarda tokens en localStorage
21. Frontend guarda datos del usuario en store Pinia
22. Frontend actualiza estado de autenticación
23. Frontend redirige según rol del usuario:
    - Admin → `/admin/dashboard`
    - Analyst → `/analisis`
    - Farmer → `/agricultor-dashboard`

### ✔ Flujos Alternativos

**A1. Credenciales inválidas:**
- 11.1. Usuario o contraseña incorrectos
- 11.2. `authenticate()` retorna None
- 11.3. Se retorna error 401: "Credenciales inválidas"
- 11.4. Frontend muestra mensaje de error

**A2. Usuario inactivo:**
- 12.1. Usuario existe pero `is_active=False`
- 12.2. `_validate_user_active()` detecta usuario inactivo
- 12.3. Si no está verificado, se retorna error: "Cuenta no verificada"
- 12.4. Si está inactivo por otra razón, se retorna error: "Usuario inactivo"
- 12.5. Frontend muestra mensaje específico

**A3. Login con email:**
- 9.1. Usuario ingresa email en lugar de username
- 9.2. `_normalize_username_email()` detecta email
- 9.3. `_authenticate_user()` busca usuario por email con `User.objects.filter(email__iexact=email)`
- 9.4. Autentica usando username real del usuario

**A4. Refresh token expirado:**
- 20.1. Access token expira después de login
- 20.2. Frontend detecta token expirado automáticamente
- 20.3. Frontend usa refresh token en `/api/v1/auth/refresh/`
- 20.4. Backend genera nuevo access token
- 20.5. Frontend actualiza token en localStorage

### ✔ Errores y Excepciones

- **401 Unauthorized:** Credenciales inválidas, usuario inactivo
- **400 Bad Request:** Datos faltantes, formato inválido
- **403 Forbidden:** Cuenta no verificada (si se requiere verificación)
- **500 Internal Server Error:** Error en base de datos, error generando tokens

### ✔ Puntos de Decisión

- ¿Credenciales válidas? → No: Error 401, Sí: Continuar
- ¿Usuario activo? → No: Error, Sí: Continuar
- ¿Email verificado? → No: Error (si requerido), Sí: Continuar
- ¿Es email o username? → Email: Buscar por email, Username: Autenticar directo

### ✔ Backend

**Endpoint(s):**
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/refresh/` (renovación de token)

**View / ViewSet:**
- `LoginView` (`backend/auth_app/views/auth/login_views.py:26`)

**Serializers:**
- `LoginSerializer` (`backend/api/serializers/auth_serializers.py:16`)
  - `_normalize_username_email()`: Normaliza entrada
  - `_authenticate_user()`: Autentica con username o email
  - `_validate_user_active()`: Valida estado y verificación

**Models:**
- `User` (Django User model)
- `LoginHistory` (`backend/audit/models.py`)
- `ActivityLog` (auditoría)

**Services:**
- `LoginService` (`backend/api/services/auth/login_service.py:18`)
  - `login_user()`: Lógica de autenticación
  - `_log_user_login()`: Registra login en auditoría

**Validaciones aplicadas:**
- Username o email no vacío
- Contraseña no vacía
- Credenciales correctas
- Usuario activo
- Email verificado (si se requiere)

### ✔ Frontend

**Componente(s) involucrado(s):**
- `LoginView.vue` (`frontend/src/views/Auth/LoginView.vue`)
- `LoginForm.vue` (`frontend/src/components/auth/LoginForm.vue`)

**Acciones del usuario:**
- Ingresar email/username
- Ingresar contraseña
- Hacer clic en "Iniciar Sesión"
- Opcional: "Recordar sesión"

**Validaciones previas:**
- Campos no vacíos
- Formato de email (si se ingresa email)

**Estado global (Pinia) usado:**
- `useAuthStore` (`frontend/src/stores/auth.js`)
  - `login()`: Inicia sesión
  - `setTokens()`: Guarda tokens
  - `setUser()`: Guarda datos de usuario
  - `isAuthenticated`: Estado de autenticación
  - `getRedirectPath()`: Redirección según rol

**Rutas frontend:**
- `/login` → `LoginView.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- No autenticado → Autenticando → Autenticado → Redirigido según rol

**Condiciones:**
- Credenciales válidas: `authenticate(username, password) is not None`
- Usuario activo: `user.is_active == True`
- Email verificado: `user.auth_email_token.is_verified == True` (si aplica)

**Bifurcaciones:**
- Credenciales válidas? → No: Error, Sí: Generar tokens
- Usuario activo? → No: Error, Sí: Continuar
- ¿Email o username? → Email: Buscar usuario, Username: Autenticar

**Actividades del usuario:**
- Acceder a `/login`
- Ingresar credenciales
- Enviar formulario

**Actividades del sistema:**
- Mostrar formulario
- Validar datos
- Autenticar usuario
- Generar tokens JWT
- Registrar login
- Retornar respuesta
- Guardar tokens en frontend
- Redirigir según rol

**Acciones automáticas:**
- Detección automática de email vs username
- Generación de tokens JWT
- Registro en auditoría
- Redirección según rol

**Procesos asincrónicos:**
- No hay procesos asincrónicos en login

---

## Caso de Uso 3: Subir Imagen

**Actor(es):** Usuario autenticado (Agricultor, Técnico, Admin)

**Descripción del proceso:** Permite al usuario subir una o múltiples imágenes de granos de cacao al sistema, con validación de formato, tamaño y almacenamiento en el servidor o S3.

**Evento de inicio:** El usuario accede a la funcionalidad de subir imágenes y selecciona uno o varios archivos de imagen desde su dispositivo.

**Precondiciones:**
- El usuario está autenticado
- El usuario tiene permisos para subir imágenes
- El sistema tiene almacenamiento disponible (local o S3)

**Postcondiciones:**
- Las imágenes se almacenan en el sistema
- Se crea registro `CacaoImage` para cada imagen
- Se actualiza el historial de imágenes del usuario
- Se registra la acción en auditoría

### ✔ Flujo Principal

1. Usuario accede a ruta `/upload-images` o `/user/prediction`
2. Sistema muestra interfaz de carga de imágenes
3. Usuario selecciona una o múltiples imágenes desde su dispositivo
4. Frontend valida formato de archivo (jpeg, jpg, png, webp)
5. Frontend valida tamaño máximo (20MB por imagen)
6. Frontend muestra preview de imágenes seleccionadas
7. Usuario opcionalmente asigna finca_id o lote_id
8. Usuario hace clic en "Subir Imágenes"
9. Frontend crea FormData con imágenes y metadatos
10. Frontend envía POST a `/api/v1/images/` o `/api/v1/analysis/batch/`
11. Backend recibe petición en `CacaoImageUploadView.post()`
12. Se extraen imágenes de `request.FILES.getlist('images')`
13. Para cada imagen:
    13.1. Se valida tamaño con `_validate_file_size()` (max 20MB)
    13.2. Se valida tipo con `_validate_file_type()` (jpeg, jpg, png, webp)
    13.3. Se crea instancia `CacaoImage` con usuario, imagen y metadatos
    13.4. Se asigna finca si se proporciona `finca_id`
    13.5. Se guarda imagen con `cacao_image.save()`
    13.6. Se serializa imagen con `CacaoImageSerializer`
14. Se invalidan cachés de estadísticas (`invalidate_system_stats_cache()`)
15. Se crean logs de auditoría para cada imagen subida
16. Backend retorna respuesta 201/207 con lista de imágenes subidas
17. Si hay errores parciales, se retorna 207 Multi-Status
18. Frontend muestra mensaje de éxito con cantidad de imágenes subidas
19. Frontend actualiza lista de imágenes si está visible

### ✔ Flujos Alternativos

**A1. Subida individual (con procesamiento inmediato):**
- 9.1. Usuario sube imagen y hace clic en "Analizar"
- 9.2. Frontend envía POST a `/api/v1/scan/measure/`
- 9.3. Se ejecuta flujo completo de subida + procesamiento + análisis
- 9.4. Backend retorna imagen subida + resultados de análisis

**A2. Subida batch (múltiples imágenes):**
- 9.1. Usuario selecciona múltiples imágenes
- 9.2. Frontend envía POST a `/api/v1/analysis/batch/`
- 9.3. Backend procesa todas las imágenes en batch
- 9.4. Backend retorna task_id para seguimiento asincrónico (Celery)

**A3. Archivo demasiado grande:**
- 13.1.1. Imagen excede 20MB
- 13.1.2. `_validate_file_size()` retorna error
- 13.1.3. Imagen se marca como error en respuesta
- 13.1.4. Otras imágenes válidas se procesan normalmente
- 13.1.5. Backend retorna 207 Multi-Status con errores

**A4. Formato no soportado:**
- 13.2.1. Imagen tiene formato no permitido
- 13.2.2. `_validate_file_type()` retorna error
- 13.2.3. Imagen se marca como error en respuesta
- 13.2.4. Backend retorna error específico por imagen

**A5. Almacenamiento en S3:**
- 13.5.1. Si está configurado `django-storages` con S3
- 13.5.2. Imagen se sube a bucket S3
- 13.5.3. Se guarda URL S3 en campo `image` del modelo

### ✔ Errores y Excepciones

- **400 Bad Request:** No se proporcionaron imágenes, datos inválidos
- **413 Payload Too Large:** Imagen excede tamaño máximo
- **415 Unsupported Media Type:** Formato de imagen no soportado
- **401 Unauthorized:** Usuario no autenticado
- **500 Internal Server Error:** Error guardando imagen, error en almacenamiento

### ✔ Puntos de Decisión

- ¿Imágenes proporcionadas? → No: Error, Sí: Continuar
- ¿Formato válido? → No: Error por imagen, Sí: Continuar
- ¿Tamaño válido? → No: Error por imagen, Sí: Continuar
- ¿Subida individual o batch? → Individual: Procesar, Batch: Encolar Celery
- ¿Almacenamiento S3 o local? → S3: Subir a S3, Local: Guardar en media/

### ✔ Backend

**Endpoint(s):**
- `POST /api/v1/images/` (subida múltiple)
- `POST /api/v1/scan/measure/` (subida + análisis)
- `POST /api/v1/analysis/batch/` (batch con Celery)

**View / ViewSet:**
- `CacaoImageUploadView` (`backend/images_app/views.py:14`)
- `ScanMeasureView` (`backend/images_app/views/image/user/scan_views.py:24`)
- `BatchAnalysisView` (`backend/images_app/views/image/batch/batch_upload_views.py:39`)

**Serializers:**
- `CacaoImageSerializer` (`backend/images_app/serializers.py`)

**Models:**
- `CacaoImage` (`backend/images_app/models.py:9`)

**Services:**
- `ImageManagementService` (`backend/images_app/services/image/management_service.py:31`)
  - `upload_image()`: Sube imagen con validaciones
  - `_validate_image_file()`: Valida archivo
  - `_create_cacao_image_instance()`: Crea instancia
- `ImageStorageService` (`backend/images_app/services/image/storage_service.py:24`)
  - `save_uploaded_image()`: Guarda imagen en almacenamiento

**Validaciones aplicadas:**
- Formato: jpeg, jpg, png, webp
- Tamaño máximo: 20MB
- Usuario autenticado
- Finca existe (si se proporciona finca_id)
- Lote existe (si se proporciona lote_id)

### ✔ Frontend

**Componente(s) involucrado(s):**
- `UploadImagesView.vue` (`frontend/src/views/UploadImagesView.vue`)
- `ImageUpload.vue` (`frontend/src/components/user/ImageUpload.vue`)
- `UserPrediction.vue` (`frontend/src/views/UserPrediction.vue`)

**Acciones del usuario:**
- Seleccionar archivo(s) desde dispositivo
- Ver preview de imágenes
- Opcionalmente seleccionar finca/lote
- Enviar formulario

**Validaciones previas:**
- Formato de archivo válido
- Tamaño de archivo dentro del límite
- Al menos una imagen seleccionada

**Estado global (Pinia) usado:**
- `useAnalysisStore` (`frontend/src/stores/analysis.js`)
  - `submitBatch()`: Envía batch de imágenes
  - `uploadProgress`: Progreso de subida
  - `uploadError`: Errores de subida

**Rutas frontend:**
- `/upload-images` → `UploadImagesView.vue`
- `/user/prediction` → `UserPrediction.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Sin imágenes → Seleccionando → Validando → Subiendo → Subida exitosa / Error

**Condiciones:**
- Formato válido: `['image/jpeg', 'image/jpg', 'image/png', 'image/webp'].includes(content_type)`
- Tamaño válido: `file.size <= 20 * 1024 * 1024`
- Usuario autenticado: `request.user.is_authenticated`

**Bifurcaciones:**
- ¿Imágenes proporcionadas? → No: Error, Sí: Procesar
- ¿Formato válido? → No: Error, Sí: Continuar
- ¿Tamaño válido? → No: Error, Sí: Continuar
- ¿Subida batch? → Sí: Encolar Celery, No: Procesar directo

**Actividades del usuario:**
- Seleccionar archivos
- Ver preview
- Enviar formulario

**Actividades del sistema:**
- Validar formato
- Validar tamaño
- Crear instancias CacaoImage
- Guardar en almacenamiento (local/S3)
- Crear logs auditoría
- Retornar respuesta

**Acciones automáticas:**
- Validación de formato y tamaño
- Invalidación de caché de estadísticas
- Registro en auditoría

**Procesos asincrónicos:**
- Subida batch puede usar Celery (`process_batch_analysis_task`)
- Almacenamiento S3 puede ser asíncrono

---

## Caso de Uso 4: Procesar Imagen

**Actor(es):** Sistema (proceso automático)

**Descripción del proceso:** El sistema procesa una imagen de cacao subida, aplicando segmentación de fondo, creación de crops y preparación para análisis mediante modelos ML.

**Evento de inicio:** Una imagen es subida y marcada para procesamiento, o se solicita procesamiento explícito de una imagen existente.

**Precondiciones:**
- La imagen existe en el sistema (`CacaoImage`)
- La imagen no está procesada (`processed=False`)
- Los modelos de segmentación están disponibles (U-Net o OpenCV)

**Postcondiciones:**
- La imagen queda marcada como procesada (`processed=True`)
- Se crea imagen procesada (crop sin fondo) si es exitoso
- Se almacena ruta de imagen procesada
- La imagen está lista para análisis

### ✔ Flujo Principal

1. Sistema recibe imagen para procesar (trigger: subida o solicitud explícita)
2. Se carga imagen desde almacenamiento
3. Se determina backend de segmentación (U-Net o OpenCV)
4. Si U-Net disponible:
    4.1. Se carga modelo U-Net entrenado (`ml/segmentation/cacao_unet.pth`)
    4.2. Se aplica segmentación con U-Net
    4.3. Se elimina fondo de la imagen
5. Si U-Net no disponible o falla:
    5.1. Se usa OpenCV para segmentación básica
    5.2. Se aplica threshold y detección de contornos
6. Se crea crop de la imagen sin fondo
7. Se guarda crop en `media/cacao_images/crops/`
8. Se calculan dimensiones del crop (ancho, alto)
9. Se actualiza `CacaoImage.processed = True`
10. Se almacena ruta del crop en `processed_image_path` (si existe campo)
11. Se guarda imagen actualizada
12. Se registra procesamiento en logs

### ✔ Flujos Alternativos

**A1. Procesamiento con análisis inmediato:**
- 1.1. Usuario sube imagen y solicita análisis inmediato
- 1.2. Se ejecuta procesamiento dentro de `AnalysisService.process_image_with_segmentation()`
- 1.3. Después de procesar, se ejecuta análisis automáticamente

**A2. Procesamiento batch:**
- 1.1. Múltiples imágenes se procesan en batch
- 1.2. Se usa Celery task `process_batch_analysis_task`
- 1.3. Cada imagen se procesa de forma independiente
- 1.4. Progreso se reporta por tarea

**A3. Segmentación fallida:**
- 4.1. U-Net falla o no está disponible
- 4.2. Sistema intenta OpenCV como fallback
- 4.3. Si OpenCV también falla, imagen se marca como procesada sin crop
- 4.4. Error se registra pero no bloquea el flujo

### ✔ Errores y Excepciones

- **Modelo U-Net no encontrado:** Se usa OpenCV como fallback
- **Error cargando imagen:** Error 500, imagen no procesada
- **Error guardando crop:** Error registrado, imagen marcada como procesada
- **Error en segmentación:** Se registra, se intenta fallback

### ✔ Puntos de Decisión

- ¿U-Net disponible? → Sí: Usar U-Net, No: Usar OpenCV
- ¿Segmentación exitosa? → Sí: Crear crop, No: Marcar procesada sin crop
- ¿Procesamiento individual o batch? → Individual: Directo, Batch: Celery

### ✔ Backend

**Endpoint(s):**
- Procesamiento interno (no endpoint directo, parte de análisis)
- `POST /api/v1/scan/measure/` (incluye procesamiento)
- `POST /api/v1/analysis/batch/` (batch con procesamiento)

**View / ViewSet:**
- Procesamiento se realiza en servicios

**Models:**
- `CacaoImage` (`backend/images_app/models.py:9`)

**Services:**
- `ImageProcessingService` (`backend/images_app/services/image/processing_service.py:16`)
  - Métodos de segmentación y procesamiento
- `ImageStorageService` (`backend/images_app/services/image/storage_service.py:24`)
  - `save_uploaded_image_with_segmentation()`: Guarda y procesa

**Validaciones aplicadas:**
- Imagen existe
- Formato de imagen válido
- Modelo disponible (para U-Net)

### ✔ Frontend

**Componente(s) involucrado(s):**
- Procesamiento es automático del backend
- Frontend solo muestra estado de procesamiento

**Estado global (Pinia) usado:**
- `useAnalysisStore`: Estado de procesamiento en batch

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Imagen subida (processed=False) → Procesando → Procesada (processed=True) / Error

**Condiciones:**
- U-Net disponible: `os.path.exists('ml/segmentation/cacao_unet.pth')`
- Segmentación exitosa: `crop creado correctamente`

**Bifurcaciones:**
- ¿U-Net disponible? → Sí: Usar U-Net, No: Usar OpenCV
- ¿Segmentación exitosa? → Sí: Guardar crop, No: Continuar sin crop

**Actividades del sistema:**
- Cargar imagen
- Aplicar segmentación
- Crear crop
- Guardar crop
- Actualizar estado

**Acciones automáticas:**
- Detección de backend de segmentación
- Fallback a OpenCV si U-Net falla

**Procesos asincrónicos:**
- Procesamiento batch usa Celery
- Procesamiento individual puede ser síncrono o asíncrono

---

## Caso de Uso 5: Analizar Imagen

**Actor(es):** Usuario autenticado, Sistema (ML)

**Descripción del proceso:** El sistema analiza una imagen de cacao procesada utilizando modelos de Machine Learning para predecir dimensiones (alto, ancho, grosor) y peso del grano.

**Evento de inicio:** Usuario solicita análisis de una imagen subida, o el análisis se ejecuta automáticamente después de subir imagen.

**Precondiciones:**
- La imagen existe y está procesada
- Los modelos ML están cargados en memoria
- La imagen tiene crop disponible (opcional pero recomendado)

**Postcondiciones:**
- Se crea registro `CacaoPrediction` con resultados
- Se almacenan predicciones: alto, ancho, grosor, peso
- Se almacena confianza del modelo
- Se calculan estadísticas del análisis

### ✔ Flujo Principal

1. Usuario solicita análisis de imagen (trigger: subida + análisis o solicitud explícita)
2. Sistema verifica que imagen existe y está procesada
3. Se carga imagen procesada (crop si existe, sino original)
4. Se cargan modelos ML desde memoria o disco:
    4.1. Modelo híbrido (`ml/artifacts/regressors/hybrid.pt`)
    4.2. Escaladores (`StandardScaler` para targets)
5. Se preprocesa imagen para el modelo:
    5.1. Redimensionamiento a tamaño del modelo (224x224)
    5.2. Normalización ImageNet
    5.3. Conversión a tensor PyTorch
6. Si modelo híbrido:
    6.1. Se extraen features de píxeles (área, perímetro, etc.)
    6.2. Se combinan features de imagen CNN + features de píxeles
7. Se ejecuta predicción con modelo:
    7.1. Modelo predice valores normalizados
    7.2. Se desnormalizan predicciones con escaladores
    7.3. Se obtienen: alto (mm), ancho (mm), grosor (mm), peso (g)
8. Se calcula confianza del modelo (si está disponible)
9. Se mide tiempo de procesamiento
10. Se crea registro `CacaoPrediction`:
    10.1. Se asocia con `CacaoImage`
    10.2. Se almacenan predicciones
    10.3. Se almacena confianza
    10.4. Se almacena tiempo de procesamiento
    10.5. Se almacena versión del modelo
11. Se actualiza `CacaoImage` con referencia a predicción
12. Se registra análisis en auditoría
13. Backend retorna resultados al frontend
14. Frontend muestra resultados de análisis

### ✔ Flujos Alternativos

**A1. Análisis con calibración de píxeles:**
- 5.1. Si existe `pixel_calibration.json`
- 5.2. Se usa factor de escala píxel→mm específico
- 5.3. Predicciones se ajustan con calibración

**A2. Análisis sin crop (imagen original):**
- 3.1. Imagen no tiene crop procesado
- 3.2. Se usa imagen original
- 3.3. Se aplica segmentación rápida inline
- 3.4. Se analiza imagen resultante

**A3. Modelo no disponible:**
- 4.1. Modelos no están cargados
- 4.2. Sistema intenta cargar desde disco
- 4.3. Si falla, se retorna error 503: "Modelos no disponibles"
- 4.4. Frontend muestra mensaje de error

**A4. Predicción con baja confianza:**
- 8.1. Confianza < 0.6
- 8.2. Se marca predicción como "baja confianza"
- 8.3. Frontend muestra advertencia al usuario

### ✔ Errores y Excepciones

- **503 Service Unavailable:** Modelos ML no disponibles
- **404 Not Found:** Imagen no encontrada
- **400 Bad Request:** Imagen no procesada
- **500 Internal Server Error:** Error en predicción, error guardando resultados

### ✔ Puntos de Decisión

- ¿Imagen procesada? → No: Procesar primero, Sí: Analizar
- ¿Modelos disponibles? → No: Error, Sí: Continuar
- ¿Crop disponible? → Sí: Usar crop, No: Usar original
- ¿Calibración disponible? → Sí: Aplicar, No: Usar valores directos

### ✔ Backend

**Endpoint(s):**
- `POST /api/v1/scan/measure/` (análisis individual)
- `POST /api/v1/analysis/batch/` (análisis batch)

**View / ViewSet:**
- `ScanMeasureView` (`backend/images_app/views/image/user/scan_views.py:24`)

**Models:**
- `CacaoPrediction` (`backend/images_app/models.py` - si existe)
- `CacaoImage` (`backend/images_app/models.py:9`)

**Services:**
- `AnalysisService` (`backend/api/services/analysis_service.py:20`)
  - `process_image_with_segmentation()`: Proceso completo
- `PredictionService` (`backend/ml/prediction/` - si existe)
  - `predict()`: Ejecuta predicción con modelo

**Validaciones aplicadas:**
- Imagen existe
- Imagen procesada
- Modelos disponibles
- Formato de imagen válido

### ✔ Frontend

**Componente(s) involucrado(s):**
- `PredictionView.vue` (`frontend/src/views/PredictionView.vue`)
- `UserPrediction.vue` (`frontend/src/views/UserPrediction.vue`)
- `PredictionResults.vue` (`frontend/src/components/user/PredictionResults.vue`)

**Acciones del usuario:**
- Subir imagen y solicitar análisis
- Ver resultados de análisis
- Guardar análisis (opcional)

**Estado global (Pinia) usado:**
- `useAnalysisStore`: Estado de análisis
- `usePredictionStore` (`frontend/src/stores/prediction.js`): Resultados

**Rutas frontend:**
- `/prediccion` → `PredictionView.vue`
- `/user/prediction` → `UserPrediction.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Imagen lista → Analizando → Resultados generados / Error

**Condiciones:**
- Modelos disponibles: `models_loaded == True`
- Imagen procesada: `cacao_image.processed == True`

**Bifurcaciones:**
- ¿Modelos disponibles? → No: Error, Sí: Analizar
- ¿Crop disponible? → Sí: Usar crop, No: Usar original

**Actividades del usuario:**
- Solicitar análisis
- Ver resultados

**Actividades del sistema:**
- Cargar modelos
- Preprocesar imagen
- Ejecutar predicción
- Guardar resultados
- Retornar resultados

**Acciones automáticas:**
- Carga de modelos en memoria
- Preprocesamiento de imagen
- Desnormalización de predicciones

**Procesos asincrónicos:**
- Análisis batch usa Celery
- Análisis individual puede ser síncrono o asíncrono

---

## Caso de Uso 6: Ver Resultados

**Actor(es):** Usuario autenticado

**Descripción del proceso:** Permite al usuario visualizar los resultados de un análisis de imagen de cacao, mostrando las predicciones de dimensiones y peso junto con la imagen analizada.

**Evento de inicio:** El usuario accede a la vista de resultados después de un análisis, o navega al historial para ver resultados previos.

**Precondiciones:**
- Existe un análisis completado (`CacaoPrediction` asociado a `CacaoImage`)
- El usuario tiene permisos para ver el análisis (es el propietario o admin)

**Postcondiciones:**
- El usuario visualiza los resultados del análisis
- Se muestra la imagen analizada junto con las predicciones

### ✔ Flujo Principal

1. Usuario accede a resultados (después de análisis o desde historial)
2. Sistema obtiene ID de imagen o predicción
3. Frontend envía GET a `/api/v1/images/{image_id}/` o `/api/v1/images/` con filtros
4. Backend recibe petición en `ImageDetailView.get()` o `ImagesListView.get()`
5. Backend verifica permisos (usuario propietario o admin)
6. Backend obtiene `CacaoImage` con predicción relacionada
7. Backend serializa datos con `CacaoImageSerializer` (incluye predicción)
8. Backend retorna datos completos: imagen, predicciones, estadísticas
9. Frontend recibe datos y los almacena en store
10. Frontend muestra componente `PredictionResults.vue`:
    10.1. Muestra imagen original y/o crop procesado
    10.2. Muestra predicciones: alto (mm), ancho (mm), grosor (mm), peso (g)
    10.3. Muestra confianza del modelo
    10.4. Muestra tiempo de procesamiento
    10.5. Muestra fecha y hora del análisis
11. Frontend formatea valores numéricos según configuración regional
12. Frontend muestra indicador de confianza (alta/media/baja)

### ✔ Flujos Alternativos

**A1. Ver desde historial:**
- 1.1. Usuario accede a `/agricultor/historial`
- 1.2. Frontend carga lista de imágenes con predicciones
- 1.3. Usuario hace clic en imagen para ver detalles
- 1.4. Frontend navega a `/detalle-analisis/{id}`

**A2. Resultados desde análisis batch:**
- 1.1. Usuario sube múltiples imágenes en batch
- 1.2. Sistema procesa en background (Celery)
- 1.3. Usuario consulta estado con `task_id`
- 1.4. Cuando completado, se muestran todos los resultados

**A3. Sin predicción disponible:**
- 5.1. Imagen existe pero no tiene predicción
- 5.2. Sistema retorna imagen sin datos de predicción
- 5.3. Frontend muestra mensaje: "Imagen pendiente de análisis"

### ✔ Errores y Excepciones

- **404 Not Found:** Imagen no encontrada
- **403 Forbidden:** Usuario sin permisos para ver imagen
- **500 Internal Server Error:** Error obteniendo datos

### ✔ Puntos de Decisión

- ¿Predicción existe? → Sí: Mostrar resultados, No: Mostrar mensaje pendiente
- ¿Usuario tiene permisos? → Sí: Mostrar, No: Error 403

### ✔ Backend

**Endpoint(s):**
- `GET /api/v1/images/{image_id}/`
- `GET /api/v1/images/` (lista con filtros)

**View / ViewSet:**
- `ImageDetailView` (`backend/images_app/views/image/user/detail_views.py`)
- `ImagesListView` (`backend/images_app/views/image/user/list_views.py:24`)

**Serializers:**
- `CacaoImageSerializer` (`backend/images_app/serializers.py`)

**Models:**
- `CacaoImage` (`backend/images_app/models.py:9`)
- `CacaoPrediction` (si existe modelo separado)

**Services:**
- `ImageManagementService.get_image_details()` (si existe)

**Validaciones aplicadas:**
- Usuario autenticado
- Permisos de acceso (propietario o admin)
- Imagen existe

### ✔ Frontend

**Componente(s) involucrado(s):**
- `PredictionResults.vue` (`frontend/src/components/user/PredictionResults.vue`)
- `PredictionView.vue` (`frontend/src/views/PredictionView.vue`)
- `DetalleAnalisisView.vue` (`frontend/src/views/DetalleAnalisisView.vue`)

**Acciones del usuario:**
- Ver resultados después de análisis
- Navegar a historial
- Hacer clic en imagen para ver detalles

**Estado global (Pinia) usado:**
- `usePredictionStore` (`frontend/src/stores/prediction.js`)
- `useAnalysisStore`: Resultados de análisis

**Rutas frontend:**
- `/prediccion` → `PredictionView.vue`
- `/detalle-analisis/:id` → `DetalleAnalisisView.vue`
- `/agricultor/historial` → `AgricultorHistorial.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Análisis completado → Obteniendo datos → Mostrando resultados / Error

**Condiciones:**
- Predicción existe: `cacao_image.prediction is not None`
- Permisos: `image.user == request.user or user.is_admin`

**Bifurcaciones:**
- ¿Predicción existe? → Sí: Mostrar, No: Mostrar pendiente
- ¿Permisos? → Sí: Continuar, No: Error

**Actividades del usuario:**
- Acceder a resultados
- Ver detalles
- Navegar historial

**Actividades del sistema:**
- Obtener datos
- Validar permisos
- Serializar datos
- Retornar respuesta
- Renderizar componentes

---

## Caso de Uso 7: Descargar Reporte

**Actor(es):** Usuario autenticado

**Descripción del proceso:** Permite al usuario generar y descargar reportes en diferentes formatos (PDF, Excel, CSV) con información de análisis, fincas, lotes o estadísticas del sistema.

**Evento de inicio:** El usuario solicita generar un reporte desde la interfaz de reportes o desde una vista específica (finca, lote, análisis).

**Precondiciones:**
- El usuario está autenticado
- El usuario tiene datos para generar reporte (análisis, fincas, etc.)
- El sistema tiene capacidad de generación de reportes configurada

**Postcondiciones:**
- Se genera archivo de reporte en formato solicitado
- Se almacena reporte en sistema (opcional)
- El usuario puede descargar el archivo

### ✔ Flujo Principal

1. Usuario accede a sección de reportes (`/reportes`)
2. Usuario selecciona tipo de reporte:
   - Reporte de calidad
   - Reporte de finca
   - Reporte de lote
   - Reporte de auditoría
   - Reporte personalizado
3. Usuario configura parámetros:
   - Formato (PDF, Excel, CSV)
   - Rango de fechas (opcional)
   - Filtros específicos
4. Usuario hace clic en "Generar Reporte"
5. Frontend envía POST a `/api/v1/reportes/` con configuración
6. Backend recibe en `ReporteListCreateView.post()`
7. Se valida tipo de reporte y formato
8. Se crea registro `ReporteGenerado` con estado "pendiente"
9. Se encola tarea Celery para generación asíncrona (si es necesario)
   O se genera reporte síncronamente
10. Según tipo de reporte:
    10.1. **Calidad:** `ExcelAnalisisGenerator.generate_quality_report()`
    10.2. **Finca:** `ExcelAnalisisGenerator.generate_finca_report()`
    10.3. **Auditoría:** `ExcelAnalisisGenerator.generate_audit_report()`
11. Se consulta datos desde base de datos según filtros
12. Se genera archivo (Excel con openpyxl, PDF con reportlab)
13. Se almacena archivo en `media/reportes/`
14. Se actualiza `ReporteGenerado` con archivo y estado "completado"
15. Backend retorna respuesta con ID de reporte
16. Frontend muestra mensaje: "Reporte generado"
17. Usuario hace clic en "Descargar"
18. Frontend envía GET a `/api/v1/reportes/{reporte_id}/download/`
19. Backend recibe en `ReporteDownloadView.get()`
20. Se valida que reporte existe y pertenece al usuario
21. Se valida que reporte está "completado"
22. Se valida que reporte no está expirado
23. Se retorna archivo con `FileResponse` y headers de descarga
24. Frontend descarga archivo al dispositivo del usuario

### ✔ Flujos Alternativos

**A1. Generación síncrona (reportes pequeños):**
- 9.1. Reporte simple (pocos datos)
- 9.2. Se genera inmediatamente sin Celery
- 9.3. Backend retorna archivo directamente en respuesta

**A2. Reporte en generación:**
- 8.1. Reporte grande requiere tiempo
- 8.2. Backend retorna `reporte_id` y estado "generando"
- 8.3. Frontend consulta estado periódicamente
- 8.4. Cuando "completado", se habilita descarga

**A3. Reporte expirado:**
- 22.1. Reporte tiene más de X días (configurado)
- 22.2. Sistema marca como "expirado"
- 22.3. Usuario debe generar nuevo reporte

**A4. Error en generación:**
- 12.1. Error durante generación
- 12.2. `ReporteGenerado` se marca como "fallido"
- 12.3. Usuario recibe mensaje de error
- 12.4. Usuario puede reintentar

### ✔ Errores y Excepciones

- **400 Bad Request:** Parámetros inválidos, tipo de reporte no soportado
- **404 Not Found:** Reporte no encontrado
- **410 Gone:** Reporte expirado
- **500 Internal Server Error:** Error generando reporte

### ✔ Puntos de Decisión

- ¿Generación asíncrona? → Sí: Encolar Celery, No: Generar directo
- ¿Reporte completado? → Sí: Permitir descarga, No: Mostrar progreso
- ¿Reporte expirado? → Sí: Error, No: Permitir descarga

### ✔ Backend

**Endpoint(s):**
- `POST /api/v1/reportes/` (crear/generar)
- `GET /api/v1/reportes/{reporte_id}/download/` (descargar)
- `GET /api/v1/reportes/` (listar)

**View / ViewSet:**
- `ReporteListCreateView` (`backend/reports/views/reports/report_crud_views.py:51`)
- `ReporteDownloadView` (`backend/reports/views/reports/report_download_views.py:39`)

**Serializers:**
- `ReporteGeneradoSerializer` (si existe)

**Models:**
- `ReporteGenerado` (`backend/reports/models.py:9`)

**Services:**
- `ReportGenerationService` (`backend/reports/services/report/report_generation_service.py:33`)
- `ExcelAnalisisGenerator` (`backend/reports/services/`)
- Generadores PDF (si existen)

**Validaciones aplicadas:**
- Tipo de reporte válido
- Formato válido (pdf, excel, csv, json)
- Permisos de usuario
- Reporte no expirado

### ✔ Frontend

**Componente(s) involucrado(s):**
- `Reportes.vue` (`frontend/src/views/Reportes.vue`)
- `ReportsManagement.vue` (`frontend/src/views/ReportsManagement.vue`)
- `ReportDownloadButton.vue` (`frontend/src/components/reportes/ReportDownloadButton.vue`)

**Acciones del usuario:**
- Seleccionar tipo de reporte
- Configurar parámetros
- Generar reporte
- Descargar archivo

**Estado global (Pinia) usado:**
- `useReportsStore` (`frontend/src/stores/reports.js`)
  - `createReport()`: Genera reporte
  - `downloadReport()`: Descarga archivo
  - `reports`: Lista de reportes

**Rutas frontend:**
- `/reportes` → `Reportes.vue`
- `/reportes/management` → `ReportsManagement.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Solicitando → Generando → Completado → Descargando / Error / Expirado

**Condiciones:**
- Tipo válido: `tipo_reporte in ['calidad', 'finca', 'auditoria', ...]`
- Formato válido: `formato in ['pdf', 'excel', 'csv']`
- Reporte completado: `reporte.estado == 'completado'`
- Reporte no expirado: `not reporte.esta_expirado`

**Bifurcaciones:**
- ¿Asíncrono? → Sí: Encolar, No: Generar
- ¿Completado? → Sí: Descargar, No: Esperar
- ¿Expirado? → Sí: Error, No: Descargar

**Actividades del usuario:**
- Configurar reporte
- Generar
- Descargar

**Actividades del sistema:**
- Validar parámetros
- Consultar datos
- Generar archivo
- Almacenar archivo
- Retornar archivo

**Procesos asincrónicos:**
- Generación de reportes grandes usa Celery
- Consulta periódica de estado desde frontend

---

## Caso de Uso 8: Crear Finca

**Actor(es):** Usuario autenticado (Agricultor, Admin)

**Descripción del proceso:** Permite al usuario crear un nuevo registro de finca en el sistema, asociándola a su cuenta y proporcionando información de ubicación, dimensiones y características.

**Evento de inicio:** El usuario accede a la gestión de fincas y selecciona "Crear Nueva Finca".

**Precondiciones:**
- El usuario está autenticado
- El usuario tiene rol de agricultor o admin
- El sistema tiene catalogos de departamentos/municipios cargados (opcional)

**Postcondiciones:**
- Se crea nuevo registro `Finca` en el sistema
- La finca queda asociada al usuario agricultor
- Se registra la acción en auditoría

### ✔ Flujo Principal

1. Usuario accede a `/fincas`
2. Usuario hace clic en "Crear Nueva Finca"
3. Sistema muestra formulario de creación
4. Usuario completa campos obligatorios:
   - Nombre de la finca
   - Ubicación
   - Municipio
   - Departamento
   - Hectáreas
5. Usuario completa campos opcionales:
   - Descripción
   - Coordenadas GPS (lat, lng)
   - Tipo de suelo
   - Clima
   - Altitud
   - Precipitación anual
   - Temperatura promedio
6. Frontend valida campos obligatorios
7. Frontend valida que hectáreas sea número positivo
8. Usuario hace clic en "Guardar"
9. Frontend envía POST a `/api/v1/fincas/` con datos
10. Backend recibe en `FincaListCreateView.post()`
11. Se valida permisos (usuario autenticado)
12. Se obtiene agricultor (request.user o desde request.data si admin)
13. `FincaSerializer` valida datos recibidos
14. Se ejecuta `FincaCRUDService.create_finca()`
15. Servicio valida campos requeridos
16. Servicio valida que hectáreas > 0
17. Servicio valida que agricultor existe
18. Se crea instancia `Finca` con datos
19. Se asigna agricultor a finca
20. Se guarda finca en base de datos
21. Se crea log de auditoría con `create_audit_log()`
22. Se invalidan cachés de estadísticas
23. Backend retorna respuesta 201 con datos de finca creada
24. Frontend muestra mensaje de éxito
25. Frontend redirige a detalle de finca o lista actualizada

### ✔ Flujos Alternativos

**A1. Crear finca como admin para otro agricultor:**
- 12.1. Admin proporciona `agricultor_id` en request.data
- 12.2. Sistema valida que agricultor existe
- 12.3. Finca se asocia al agricultor especificado

**A2. Validación de hectáreas inválidas:**
- 16.1. Hectáreas <= 0 o no es número
- 16.2. Servicio retorna error de validación
- 16.3. Frontend muestra error específico

**A3. Finca duplicada (mismo nombre y agricultor):**
- 18.1. Sistema permite múltiples fincas con mismo nombre
- 18.2. No hay validación de unicidad (por diseño)

### ✔ Errores y Excepciones

- **400 Bad Request:** Datos inválidos, campos faltantes, hectáreas inválidas
- **401 Unauthorized:** Usuario no autenticado
- **403 Forbidden:** Usuario sin permisos
- **500 Internal Server Error:** Error guardando en BD

### ✔ Puntos de Decisión

- ¿Campos válidos? → No: Error, Sí: Continuar
- ¿Hectáreas > 0? → No: Error, Sí: Continuar
- ¿Admin creando para otro? → Sí: Validar agricultor, No: Usar request.user

### ✔ Backend

**Endpoint(s):**
- `POST /api/v1/fincas/`

**View / ViewSet:**
- `FincaListCreateView` (`backend/fincas_app/views/finca/finca_views.py:58`)

**Serializers:**
- `FincaSerializer` (`backend/fincas_app/serializers.py`)

**Models:**
- `Finca` (`backend/fincas_app/models.py:12`)

**Services:**
- `FincaCRUDService` (`backend/fincas_app/services/finca/finca_crud_service.py:26`)
  - `create_finca()`: Crea finca con validaciones

**Validaciones aplicadas:**
- Campos obligatorios: nombre, ubicacion, municipio, departamento, hectareas
- Hectáreas > 0
- Agricultor existe
- Formato de coordenadas (si se proporcionan)

### ✔ Frontend

**Componente(s) involucrado(s):**
- `FincasView.vue` (`frontend/src/views/common/FincasView.vue`)
- `FincaForm.vue` (componente de formulario)

**Acciones del usuario:**
- Acceder a gestión de fincas
- Completar formulario
- Guardar finca

**Validaciones previas:**
- Campos obligatorios no vacíos
- Hectáreas es número positivo
- Coordenadas válidas (si se ingresan)

**Estado global (Pinia) usado:**
- `useFincas` (`frontend/src/composables/useFincas.js`)
  - `createFinca()`: Crea finca
- `useFincasStore` (`frontend/src/stores/fincas.js`)

**Rutas frontend:**
- `/fincas` → `FincasView.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Sin finca → Completando formulario → Guardando → Finca creada / Error

**Condiciones:**
- Campos válidos: `all(campos_obligatorios)`
- Hectáreas válidas: `hectareas > 0`
- Agricultor existe: `User.objects.filter(id=agricultor_id).exists()`

**Bifurcaciones:**
- ¿Validación exitosa? → Sí: Crear, No: Mostrar errores
- ¿Admin? → Sí: Puede asignar a otro, No: Asigna a sí mismo

**Actividades del usuario:**
- Completar formulario
- Guardar

**Actividades del sistema:**
- Validar datos
- Crear finca
- Guardar en BD
- Crear auditoría
- Retornar respuesta

---

## Caso de Uso 9: Editar Finca

**Actor(es):** Usuario autenticado (Agricultor propietario, Admin)

**Descripción del proceso:** Permite al usuario modificar la información de una finca existente, actualizando sus datos de ubicación, dimensiones u otros atributos.

**Evento de inicio:** El usuario accede a los detalles de una finca y selecciona "Editar Finca".

**Precondiciones:**
- La finca existe en el sistema
- El usuario es propietario de la finca o tiene rol de admin
- El usuario está autenticado

**Postcondiciones:**
- Los datos de la finca se actualizan en el sistema
- Se registra la modificación en auditoría
- La información actualizada es visible inmediatamente

### ✔ Flujo Principal

1. Usuario accede a detalle de finca `/fincas/{finca_id}`
2. Usuario hace clic en "Editar"
3. Sistema muestra formulario pre-poblado con datos actuales
4. Usuario modifica campos deseados (mismos campos que creación)
5. Frontend valida cambios
6. Usuario hace clic en "Guardar Cambios"
7. Frontend envía PATCH a `/api/v1/fincas/{finca_id}/update/`
8. Backend recibe en `FincaUpdateView.patch()`
9. Se valida que finca existe
10. Se valida que usuario tiene permisos (propietario o admin)
11. `FincaSerializer` valida datos parciales
12. Se ejecuta `FincaCRUDService.update_finca()`
13. Servicio actualiza campos proporcionados
14. Servicio valida hectáreas si se modifica (> 0)
15. Se guardan cambios en base de datos
16. Se crea log de auditoría con cambios realizados
17. Se invalidan cachés relacionadas
18. Backend retorna respuesta 200 con finca actualizada
19. Frontend muestra mensaje de éxito
20. Frontend actualiza vista con datos nuevos

### ✔ Flujos Alternativos

**A1. Actualización parcial (PATCH):**
- 7.1. Usuario solo modifica algunos campos
- 7.2. Backend actualiza solo campos proporcionados
- 7.3. Otros campos mantienen valores originales

**A2. Sin permisos:**
- 10.1. Usuario no es propietario ni admin
- 10.2. Backend retorna error 403
- 10.3. Frontend muestra mensaje de acceso denegado

**A3. Cambio de agricultor (solo admin):**
- 13.1. Admin modifica `agricultor_id`
- 13.2. Sistema valida que nuevo agricultor existe
- 13.3. Finca cambia de propietario
- 13.4. Se registra cambio en auditoría

### ✔ Errores y Excepciones

- **400 Bad Request:** Datos inválidos
- **403 Forbidden:** Sin permisos
- **404 Not Found:** Finca no encontrada
- **500 Internal Server Error:** Error guardando cambios

### ✔ Puntos de Decisión

- ¿Usuario tiene permisos? → Sí: Continuar, No: Error 403
- ¿Finca existe? → Sí: Continuar, No: Error 404
- ¿Validación exitosa? → Sí: Guardar, No: Mostrar errores

### ✔ Backend

**Endpoint(s):**
- `PATCH /api/v1/fincas/{finca_id}/update/`
- `PUT /api/v1/fincas/{finca_id}/update/` (actualización completa)

**View / ViewSet:**
- `FincaUpdateView` (`backend/fincas_app/views/finca/finca_views.py:214`)

**Serializers:**
- `FincaSerializer` (actualización parcial)

**Models:**
- `Finca` (`backend/fincas_app/models.py:12`)

**Services:**
- `FincaCRUDService.update_finca()` (`backend/fincas_app/services/finca/finca_crud_service.py:248`)

**Validaciones aplicadas:**
- Permisos de edición
- Finca existe
- Datos válidos (si se modifican)
- Hectáreas > 0 (si se modifica)

### ✔ Frontend

**Componente(s) involucrado(s):**
- `FincaDetailView.vue` (`frontend/src/views/FincaDetailView.vue`)
- `FincaForm.vue` (modo edición)

**Acciones del usuario:**
- Acceder a detalle
- Editar
- Guardar cambios

**Validaciones previas:**
- Campos modificados válidos
- Permisos de edición

**Estado global (Pinia) usado:**
- `useFincas`: `updateFinca()`

**Rutas frontend:**
- `/fincas/:id` → `FincaDetailView.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Finca existente → Editando → Guardando → Actualizada / Error

**Condiciones:**
- Permisos: `finca.agricultor == user or user.is_admin`
- Finca existe: `Finca.objects.filter(id=finca_id).exists()`

**Bifurcaciones:**
- ¿Permisos? → Sí: Editar, No: Error
- ¿Validación? → Sí: Guardar, No: Errores

**Actividades del usuario:**
- Modificar datos
- Guardar

**Actividades del sistema:**
- Validar permisos
- Validar datos
- Actualizar finca
- Guardar cambios
- Auditoría

---

## Caso de Uso 10: Crear Lote

**Actor(es):** Usuario autenticado (Agricultor propietario de finca, Admin)

**Descripción del proceso:** Permite al usuario crear un nuevo lote dentro de una finca existente, asociándolo con información de variedad, fechas de plantación y cosecha, y área.

**Evento de inicio:** El usuario accede a la gestión de lotes de una finca y selecciona "Crear Nuevo Lote".

**Precondiciones:**
- El usuario está autenticado
- Existe una finca a la cual asociar el lote
- El usuario es propietario de la finca o tiene rol de admin

**Postcondiciones:**
- Se crea nuevo registro `Lote` en el sistema
- El lote queda asociado a la finca especificada
- Se registra la acción en auditoría

### ✔ Flujo Principal

1. Usuario accede a `/fincas/{finca_id}/lotes` o `/lotes`
2. Usuario hace clic en "Crear Nuevo Lote"
3. Sistema muestra formulario de creación
4. Usuario selecciona finca (si no viene pre-seleccionada)
5. Usuario completa campos obligatorios:
   - Identificador del lote
   - Variedad de cacao
   - Fecha de plantación
   - Área en hectáreas
6. Usuario completa campos opcionales:
   - Nombre (si diferente de identificador)
   - Fecha de cosecha
   - Estado (activo, inactivo, cosechado, renovado)
   - Descripción
   - Coordenadas GPS
   - Edad de plantas
7. Frontend valida campos obligatorios
8. Frontend valida que área sea número positivo
9. Frontend valida que fecha de plantación sea anterior a fecha de cosecha (si ambas proporcionadas)
10. Usuario hace clic en "Guardar"
11. Frontend envía POST a `/api/v1/lotes/` con datos
12. Backend recibe en `LoteListCreateView.post()`
13. Se valida que finca existe y pertenece al usuario (si no es admin)
14. `LoteSerializer` valida datos recibidos
15. Se ejecuta `LoteService.create_lote()`
16. Servicio valida campos requeridos
17. Servicio valida que finca existe y usuario tiene acceso
18. Servicio valida que área > 0
19. Servicio valida fechas (plantación <= cosecha si ambas proporcionadas)
20. Se crea instancia `Lote` con datos
21. Se asigna finca al lote
22. Se guarda lote en base de datos
23. Se crea log de auditoría
24. Backend retorna respuesta 201 con datos de lote creado
25. Frontend muestra mensaje de éxito
26. Frontend redirige a detalle de lote o lista actualizada

### ✔ Flujos Alternativos

**A1. Lote sin identificador (se genera automáticamente):**
- 5.1. Usuario no proporciona identificador
- 5.2. Sistema genera identificador automático basado en nombre o secuencia
- 5.3. Lote se crea con identificador generado

**A2. Validación de área excede finca:**
- 18.1. Área total de lotes excedería área de finca
- 18.2. Sistema puede permitir o validar según configuración
- 18.3. Si se valida, se retorna error

**A3. Fecha de cosecha anterior a plantación:**
- 19.1. Fecha de cosecha < fecha de plantación
- 19.2. Sistema retorna error de validación
- 19.3. Frontend muestra mensaje específico

### ✔ Errores y Excepciones

- **400 Bad Request:** Datos inválidos, campos faltantes, fechas inválidas
- **403 Forbidden:** Sin permisos en finca
- **404 Not Found:** Finca no encontrada
- **500 Internal Server Error:** Error guardando en BD

### ✔ Puntos de Decisión

- ¿Finca existe y tiene permisos? → Sí: Continuar, No: Error
- ¿Campos válidos? → Sí: Continuar, No: Error
- ¿Fechas coherentes? → Sí: Continuar, No: Error

### ✔ Backend

**Endpoint(s):**
- `POST /api/v1/lotes/`

**View / ViewSet:**
- `LoteListCreateView` (`backend/fincas_app/views/finca/lote_views.py:110`)

**Serializers:**
- `LoteSerializer` (`backend/fincas_app/serializers.py`)

**Models:**
- `Lote` (`backend/fincas_app/models.py:171`)
- `Finca` (`backend/fincas_app/models.py:12`)

**Services:**
- `LoteService` (`backend/fincas_app/services/lote_service.py:31`)
  - `create_lote()`: Crea lote con validaciones

**Validaciones aplicadas:**
- Campos obligatorios: finca, identificador, variedad, fecha_plantacion, area_hectareas
- Finca existe y usuario tiene acceso
- Área > 0
- Fecha plantación <= fecha cosecha (si ambas)
- Identificador único por finca (opcional, según diseño)

### ✔ Frontend

**Componente(s) involucrado(s):**
- `LotesView.vue` (`frontend/src/views/LotesView.vue`)
- `LoteForm.vue` (`frontend/src/components/LoteForm.vue`)
- `FincaLotesView.vue` (`frontend/src/views/FincaLotesView.vue`)

**Acciones del usuario:**
- Acceder a gestión de lotes
- Seleccionar finca
- Completar formulario
- Guardar lote

**Validaciones previas:**
- Campos obligatorios no vacíos
- Área es número positivo
- Fechas coherentes

**Estado global (Pinia) usado:**
- `useLotes` (`frontend/src/composables/useLotes.js`)
  - `createLote()`: Crea lote

**Rutas frontend:**
- `/lotes` → `LotesView.vue`
- `/fincas/:id/lotes` → `FincaLotesView.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Sin lote → Completando formulario → Guardando → Lote creado / Error

**Condiciones:**
- Finca válida: `Finca.objects.filter(id=finca_id, agricultor=user).exists()`
- Área válida: `area_hectareas > 0`
- Fechas coherentes: `fecha_plantacion <= fecha_cosecha`

**Bifurcaciones:**
- ¿Permisos en finca? → Sí: Continuar, No: Error
- ¿Validación exitosa? → Sí: Crear, No: Errores

**Actividades del usuario:**
- Seleccionar finca
- Completar formulario
- Guardar

**Actividades del sistema:**
- Validar permisos
- Validar datos
- Crear lote
- Guardar en BD
- Auditoría

---

## Caso de Uso 11: Editar Lote

**Actor(es):** Usuario autenticado (Agricultor propietario, Admin)

**Descripción del proceso:** Permite al usuario modificar la información de un lote existente, actualizando variedad, fechas, área u otros atributos.

**Evento de inicio:** El usuario accede a los detalles de un lote y selecciona "Editar Lote".

**Precondiciones:**
- El lote existe en el sistema
- El usuario es propietario de la finca del lote o tiene rol de admin
- El usuario está autenticado

**Postcondiciones:**
- Los datos del lote se actualizan en el sistema
- Se registra la modificación en auditoría
- La información actualizada es visible inmediatamente

### ✔ Flujo Principal

1. Usuario accede a detalle de lote `/lotes/{lote_id}`
2. Usuario hace clic en "Editar"
3. Sistema muestra formulario pre-poblado con datos actuales
4. Usuario modifica campos deseados
5. Frontend valida cambios
6. Usuario hace clic en "Guardar Cambios"
7. Frontend envía PATCH a `/api/v1/lotes/{lote_id}/update/`
8. Backend recibe en `LoteUpdateView.patch()`
9. Se valida que lote existe
10. Se valida que usuario tiene permisos (propietario de finca o admin)
11. `LoteSerializer` valida datos parciales
12. Se ejecuta `LoteService.update_lote()`
13. Servicio actualiza campos proporcionados
14. Servicio valida área si se modifica (> 0)
15. Servicio valida fechas si se modifican
16. Se guardan cambios en base de datos
17. Se crea log de auditoría
18. Backend retorna respuesta 200 con lote actualizado
19. Frontend muestra mensaje de éxito
20. Frontend actualiza vista con datos nuevos

### ✔ Flujos Alternativos

**A1. Cambio de finca (solo admin):**
- 13.1. Admin modifica `finca_id`
- 13.2. Sistema valida que nueva finca existe
- 13.3. Lote cambia de finca
- 13.4. Se registra cambio en auditoría

**A2. Sin permisos:**
- 10.1. Usuario no tiene permisos
- 10.2. Backend retorna error 403
- 10.3. Frontend muestra mensaje de acceso denegado

### ✔ Errores y Excepciones

- **400 Bad Request:** Datos inválidos, fechas incoherentes
- **403 Forbidden:** Sin permisos
- **404 Not Found:** Lote no encontrado
- **500 Internal Server Error:** Error guardando cambios

### ✔ Puntos de Decisión

- ¿Usuario tiene permisos? → Sí: Continuar, No: Error 403
- ¿Lote existe? → Sí: Continuar, No: Error 404
- ¿Validación exitosa? → Sí: Guardar, No: Mostrar errores

### ✔ Backend

**Endpoint(s):**
- `PATCH /api/v1/lotes/{lote_id}/update/`
- `PUT /api/v1/lotes/{lote_id}/update/`

**View / ViewSet:**
- `LoteUpdateView` (`backend/fincas_app/views/finca/lote_views.py:286`)

**Serializers:**
- `LoteSerializer` (actualización parcial)

**Models:**
- `Lote` (`backend/fincas_app/models.py:171`)

**Services:**
- `LoteService.update_lote()` (`backend/fincas_app/services/lote_service.py:408`)

**Validaciones aplicadas:**
- Permisos de edición
- Lote existe
- Datos válidos
- Área > 0 (si se modifica)
- Fechas coherentes

### ✔ Frontend

**Componente(s) involucrado(s):**
- `LoteDetailView.vue` (`frontend/src/views/LoteDetailView.vue`)
- `LoteForm.vue` (modo edición)

**Acciones del usuario:**
- Acceder a detalle
- Editar
- Guardar cambios

**Estado global (Pinia) usado:**
- `useLotes`: `updateLote()`

**Rutas frontend:**
- `/lotes/:id` → `LoteDetailView.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Lote existente → Editando → Guardando → Actualizado / Error

**Condiciones:**
- Permisos: `lote.finca.agricultor == user or user.is_admin`
- Lote existe: `Lote.objects.filter(id=lote_id).exists()`

**Bifurcaciones:**
- ¿Permisos? → Sí: Editar, No: Error
- ¿Validación? → Sí: Guardar, No: Errores

**Actividades del usuario:**
- Modificar datos
- Guardar

**Actividades del sistema:**
- Validar permisos
- Validar datos
- Actualizar lote
- Guardar cambios
- Auditoría

---

## Caso de Uso 12: Eliminar Lote

**Actor(es):** Usuario autenticado (Agricultor propietario, Admin)

**Descripción del proceso:** Permite al usuario eliminar un lote del sistema cuando ya no es válido o necesario, verificando que no tenga dependencias antes de eliminarlo.

**Evento de inicio:** El usuario accede a los detalles de un lote y selecciona "Eliminar Lote".

**Precondiciones:**
- El lote existe en el sistema
- El usuario es propietario de la finca del lote o tiene rol de admin
- El usuario está autenticado

**Postcondiciones:**
- El lote se elimina del sistema
- Se registra la eliminación en auditoría
- Las imágenes asociadas quedan sin lote (se establece lote=None)

### ✔ Flujo Principal

1. Usuario accede a detalle de lote `/lotes/{lote_id}`
2. Usuario hace clic en "Eliminar"
3. Frontend muestra diálogo de confirmación
4. Usuario confirma eliminación
5. Frontend envía DELETE a `/api/v1/lotes/{lote_id}/delete/`
6. Backend recibe en `LoteDeleteView.delete()`
7. Se valida que lote existe
8. Se valida que usuario tiene permisos
9. Se verifica si lote tiene imágenes asociadas (`lote.cacao_images.exists()`)
10. Si tiene imágenes asociadas:
    10.1. Se retorna error 400: "No se puede eliminar el lote porque tiene análisis asociados"
    10.2. Frontend muestra mensaje de error
11. Si no tiene imágenes:
    11.1. Se crea log de auditoría antes de eliminar
    11.2. Se elimina lote de base de datos (`lote.delete()`)
    11.3. Backend retorna respuesta 204 No Content
    11.4. Frontend muestra mensaje de éxito
    11.5. Frontend redirige a lista de lotes o finca

### ✔ Flujos Alternativos

**A1. Lote con imágenes (no se puede eliminar):**
- 9.1. Lote tiene `CacaoImage` asociadas
- 9.2. Sistema no permite eliminación
- 9.3. Usuario debe primero eliminar o reasignar imágenes

**A2. Eliminación forzada (solo admin, futuro):**
- 9.1. Admin puede forzar eliminación
- 9.2. Imágenes asociadas se actualizan a `lote=None`
- 9.3. Lote se elimina

**A3. Sin permisos:**
- 8.1. Usuario no tiene permisos
- 8.2. Backend retorna error 403
- 8.3. Frontend muestra mensaje de acceso denegado

### ✔ Errores y Excepciones

- **400 Bad Request:** Lote tiene dependencias (imágenes asociadas)
- **403 Forbidden:** Sin permisos
- **404 Not Found:** Lote no encontrado
- **500 Internal Server Error:** Error eliminando

### ✔ Puntos de Decisión

- ¿Usuario tiene permisos? → Sí: Continuar, No: Error 403
- ¿Lote existe? → Sí: Continuar, No: Error 404
- ¿Tiene imágenes asociadas? → Sí: Error 400, No: Eliminar

### ✔ Backend

**Endpoint(s):**
- `DELETE /api/v1/lotes/{lote_id}/delete/`

**View / ViewSet:**
- `LoteDeleteView` (`backend/fincas_app/views/finca/lote_views.py:370`)

**Models:**
- `Lote` (`backend/fincas_app/models.py:171`)
- `CacaoImage` (verificar dependencias)

**Services:**
- `LoteService.delete_lote()` (`backend/fincas_app/services/lote_service.py:478`)

**Validaciones aplicadas:**
- Permisos de eliminación
- Lote existe
- No tiene imágenes asociadas

### ✔ Frontend

**Componente(s) involucrado(s):**
- `LoteDetailView.vue` (`frontend/src/views/LoteDetailView.vue`)

**Acciones del usuario:**
- Acceder a detalle
- Confirmar eliminación

**Estado global (Pinia) usado:**
- `useLotes`: `deleteLote()`

**Rutas frontend:**
- `/lotes/:id` → `LoteDetailView.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Lote existente → Confirmando → Eliminando → Eliminado / Error

**Condiciones:**
- Permisos: `lote.finca.agricultor == user or user.is_admin`
- Sin dependencias: `not lote.cacao_images.exists()`

**Bifurcaciones:**
- ¿Permisos? → Sí: Continuar, No: Error
- ¿Tiene dependencias? → Sí: Error, No: Eliminar

**Actividades del usuario:**
- Confirmar eliminación

**Actividades del sistema:**
- Validar permisos
- Verificar dependencias
- Crear auditoría
- Eliminar lote
- Retornar respuesta

---

## Caso de Uso 13: Ver Historial

**Actor(es):** Usuario autenticado

**Descripción del proceso:** Permite al usuario visualizar el historial completo de sus análisis de imágenes, con opciones de filtrado, búsqueda y paginación.

**Evento de inicio:** El usuario accede a la sección de historial desde el dashboard o menú de navegación.

**Precondiciones:**
- El usuario está autenticado
- El usuario tiene al menos un análisis realizado en el sistema

**Postcondiciones:**
- El usuario visualiza lista de análisis históricos
- El usuario puede filtrar y buscar análisis específicos

### ✔ Flujo Principal

1. Usuario accede a `/agricultor/historial` o vista similar
2. Frontend carga componente `ImageHistoryCard` o similar
3. Frontend envía GET a `/api/v1/images/` con parámetros:
   - `page`: Número de página
   - `page_size`: Tamaño de página (ej: 12)
   - `processed`: true (solo procesadas)
   - Opcional: filtros de fecha, confianza, etc.
4. Backend recibe en `ImagesListView.get()`
5. Se aplica filtro por usuario (`CacaoImage.objects.filter(user=request.user)`)
6. Se aplican filtros adicionales si se proporcionan
7. Se ordena por fecha de creación descendente (`-created_at`)
8. Se aplica paginación
9. Se serializan imágenes con predicciones relacionadas
10. Backend retorna respuesta paginada con:
    - `results`: Lista de imágenes con análisis
    - `count`: Total de registros
    - `next`: URL siguiente página
    - `previous`: URL página anterior
11. Frontend recibe datos y los almacena en store
12. Frontend renderiza lista de tarjetas de análisis:
    12.1. Imagen thumbnail
    12.2. Fecha del análisis
    12.3. Predicciones resumidas (peso, dimensiones)
    12.4. Confianza del modelo
    12.5. Botón para ver detalles
13. Usuario puede aplicar filtros:
    13.1. Por rango de fechas
    13.2. Por nivel de confianza
    13.3. Por estado (completado/pendiente)
    13.4. Búsqueda por texto
14. Frontend actualiza lista según filtros
15. Usuario puede hacer clic en análisis para ver detalles completos

### ✔ Flujos Alternativos

**A1. Historial vacío:**
- 5.1. Usuario no tiene análisis
- 5.2. Backend retorna lista vacía
- 5.3. Frontend muestra mensaje: "No hay análisis en el historial"

**A2. Filtros aplicados:**
- 6.1. Usuario aplica múltiples filtros
- 6.2. Backend aplica filtros en queryset
- 6.3. Frontend muestra resultados filtrados

**A3. Paginación:**
- 8.1. Usuario navega a página siguiente
- 8.2. Frontend carga nueva página
- 8.3. Se mantienen filtros aplicados

### ✔ Errores y Excepciones

- **401 Unauthorized:** Usuario no autenticado
- **500 Internal Server Error:** Error obteniendo datos

### ✔ Puntos de Decisión

- ¿Tiene análisis? → Sí: Mostrar lista, No: Mostrar vacío
- ¿Filtros aplicados? → Sí: Filtrar, No: Mostrar todos

### ✔ Backend

**Endpoint(s):**
- `GET /api/v1/images/` (con filtros)

**View / ViewSet:**
- `ImagesListView` (`backend/images_app/views/image/user/list_views.py:24`)

**Serializers:**
- `CacaoImageSerializer`

**Models:**
- `CacaoImage` (`backend/images_app/models.py:9`)
- `CacaoPrediction`

**Services:**
- `ImageManagementService` (si tiene métodos de filtrado)
- `AnalysisService.get_analysis_history()` (`backend/api/services/analysis_service.py:140`)

**Validaciones aplicadas:**
- Usuario autenticado
- Filtros válidos
- Paginación válida

### ✔ Frontend

**Componente(s) involucrado(s):**
- `AgricultorHistorial.vue` (`frontend/src/views/Agricultor/AgricultorHistorial.vue`)
- `ImageHistoryCard.vue` (`frontend/src/components/dashboard/ImageHistoryCard.vue`)
- `BaseHistoryCard.vue` (`frontend/src/components/common/BaseHistoryCard.vue`)

**Acciones del usuario:**
- Ver historial
- Aplicar filtros
- Navegar páginas
- Ver detalles de análisis

**Estado global (Pinia) usado:**
- `usePredictionStore`: Historial de predicciones
- Store de imágenes (si existe)

**Rutas frontend:**
- `/agricultor/historial` → `AgricultorHistorial.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Cargando → Historial cargado → Filtrado / Sin resultados

**Condiciones:**
- Usuario autenticado: `request.user.is_authenticated`
- Tiene análisis: `CacaoImage.objects.filter(user=user).exists()`

**Bifurcaciones:**
- ¿Tiene análisis? → Sí: Mostrar, No: Vacío
- ¿Filtros? → Sí: Aplicar, No: Todos

**Actividades del usuario:**
- Ver historial
- Filtrar
- Navegar
- Ver detalles

**Actividades del sistema:**
- Consultar BD
- Aplicar filtros
- Paginar resultados
- Serializar datos
- Retornar respuesta

---

## Caso de Uso 14: Buscar Análisis

**Actor(es):** Usuario autenticado (Agricultor, Técnico, Admin)

**Descripción del proceso:** Permite al usuario buscar análisis específicos utilizando criterios como fechas, confianza, finca, lote, variedad u otros filtros avanzados.

**Evento de inicio:** El usuario accede a la búsqueda de análisis y define criterios de búsqueda.

**Precondiciones:**
- El usuario está autenticado
- El sistema tiene análisis almacenados

**Postcondiciones:**
- El usuario visualiza resultados de búsqueda según criterios
- Los resultados pueden ser exportados o filtrados adicionalmente

### ✔ Flujo Principal

1. Usuario accede a búsqueda de análisis (puede ser desde historial o vista dedicada)
2. Sistema muestra formulario de búsqueda con campos:
   - Rango de fechas (desde/hasta)
   - Nivel de confianza (min/max)
   - Finca
   - Lote
   - Variedad
   - Búsqueda por texto libre
3. Usuario define criterios de búsqueda
4. Usuario hace clic en "Buscar"
5. Frontend construye parámetros de consulta
6. Frontend envía GET a `/api/v1/images/` o `/api/v1/images/admin/images/` (si admin) con query params:
   - `date_from`: Fecha inicio
   - `date_to`: Fecha fin
   - `min_confidence`: Confianza mínima
   - `max_confidence`: Confianza máxima
   - `finca`: ID o nombre de finca
   - `search`: Texto libre
   - `model_version`: Versión del modelo
7. Backend recibe en `ImagesListView` o `AdminImagesListView`
8. Se obtiene queryset base filtrado por usuario (o todos si admin)
9. Se aplican filtros según parámetros:
   - Por fecha: `filter(created_at__date__gte=date_from, created_at__date__lte=date_to)`
   - Por confianza: `filter(prediction__average_confidence__gte=min_confidence)`
   - Por finca: `filter(finca__nombre__icontains=finca)`
   - Por texto: `filter(Q(notas__icontains=search) | Q(...))`
10. Se ordena por relevancia o fecha
11. Se aplica paginación
12. Se serializan resultados
13. Backend retorna resultados con metadatos de filtros aplicados
14. Frontend recibe y muestra resultados
15. Frontend muestra resumen: "X resultados encontrados"
16. Usuario puede refinar búsqueda o exportar resultados

### ✔ Flujos Alternativos

**A1. Búsqueda avanzada (admin):**
- 7.1. Admin usa endpoint `/api/v1/images/admin/images/`
- 7.2. Puede buscar en todos los usuarios
- 7.3. Filtros adicionales: por usuario, región, etc.

**A2. Sin resultados:**
- 13.1. Búsqueda no encuentra coincidencias
- 13.2. Backend retorna lista vacía
- 13.3. Frontend muestra: "No se encontraron análisis con esos criterios"

**A3. Exportar resultados:**
- 16.1. Usuario selecciona "Exportar"
- 16.2. Se genera reporte con resultados de búsqueda
- 16.3. Usuario descarga archivo

### ✔ Errores y Excepciones

- **400 Bad Request:** Parámetros de búsqueda inválidos
- **401 Unauthorized:** Usuario no autenticado
- **500 Internal Server Error:** Error en búsqueda

### ✔ Puntos de Decisión

- ¿Admin? → Sí: Búsqueda global, No: Solo propio usuario
- ¿Resultados encontrados? → Sí: Mostrar, No: Mensaje vacío

### ✔ Backend

**Endpoint(s):**
- `GET /api/v1/images/` (con query params)
- `GET /api/v1/images/admin/images/` (admin, búsqueda global)

**View / ViewSet:**
- `ImagesListView` (`backend/images_app/views/image/user/list_views.py:24`)
- `AdminImagesListView` (`backend/images_app/views/image/admin/list_views.py:32`)

**Models:**
- `CacaoImage`
- `CacaoPrediction`

**Services:**
- `ImageManagementService._apply_filters_to_queryset()` (`backend/images_app/services/image/management_service.py:171`)
- `AdminImagesListView._apply_filters()` (`backend/images_app/views/image/admin/list_views.py:38`)

**Validaciones aplicadas:**
- Formato de fechas válido
- Rangos de confianza válidos (0-1)
- Parámetros de búsqueda válidos

### ✔ Frontend

**Componente(s) involucrado(s):**
- `ImageHistoryCard.vue` (con filtros)
- Componentes de búsqueda avanzada (si existen)

**Acciones del usuario:**
- Definir criterios
- Buscar
- Refinar búsqueda
- Exportar resultados

**Estado global (Pinia) usado:**
- Store de búsqueda/filtros (si existe)
- Store de imágenes

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Sin búsqueda → Buscando → Resultados mostrados / Sin resultados

**Condiciones:**
- Parámetros válidos: `date_from <= date_to`, `0 <= confidence <= 1`

**Bifurcaciones:**
- ¿Admin? → Sí: Global, No: Por usuario
- ¿Resultados? → Sí: Mostrar, No: Vacío

**Actividades del usuario:**
- Definir criterios
- Buscar
- Revisar resultados

**Actividades del sistema:**
- Validar parámetros
- Aplicar filtros
- Consultar BD
- Paginar
- Retornar resultados

---

## Caso de Uso 15: Entrenar Modelo

**Actor(es):** Usuario autenticado (Admin, Técnico con permisos)

**Descripción del proceso:** Permite a un administrador o técnico entrenar o re-entrenar modelos de Machine Learning para mejorar la precisión de las predicciones de dimensiones y peso de granos de cacao.

**Evento de inicio:** El usuario accede al panel de entrenamiento y solicita entrenar un nuevo modelo.

**Precondiciones:**
- El usuario tiene rol de admin o técnico
- Existe dataset de entrenamiento disponible
- El sistema tiene capacidad computacional (CPU/GPU)
- Los datos de entrenamiento están calibrados

**Postcondiciones:**
- Se genera nuevo modelo entrenado
- Se almacenan métricas de entrenamiento
- El modelo queda disponible para uso (opcional: se promueve a producción)

### ✔ Flujo Principal

1. Usuario accede a `/admin/entrenamiento` o panel similar
2. Sistema muestra opciones de entrenamiento
3. Usuario configura parámetros:
   - Tipo de modelo (regression, hybrid, multi-head)
   - Epochs (número de iteraciones)
   - Batch size
   - Learning rate
   - Usar pixel features (si híbrido)
   - Backend de segmentación (U-Net, OpenCV)
4. Usuario hace clic en "Iniciar Entrenamiento"
5. Frontend envía POST a `/api/v1/ml/auto-train/` o `/api/v1/train/jobs/create/`
6. Backend recibe en `AutoTrainView.post()` o `TrainingJobCreateView.post()`
7. Se valida que usuario es admin
8. Se valida que existe dataset válido
9. Se valida parámetros de entrenamiento
10. Opción A - Entrenamiento síncrono:
    10.1. Se ejecuta `run_training_pipeline()` directamente
    10.2. Se entrenan modelos (puede tomar horas)
    10.3. Se generan métricas y artefactos
    10.4. Backend retorna resultados cuando completa
11. Opción B - Entrenamiento asíncrono (Celery):
    11.1. Se crea `TrainingJob` con estado "pending"
    11.2. Se encola tarea Celery `train_model_task`
    11.3. Backend retorna `job_id` inmediatamente
    12. Frontend consulta estado con `GET /api/v1/train/jobs/{job_id}/status/`
    13. Celery ejecuta entrenamiento en background
    14. Progreso se actualiza periódicamente
15. Durante entrenamiento:
    15.1. Se cargan datos de entrenamiento
    15.2. Se normalizan targets
    15.3. Se crean DataLoaders
    15.4. Se entrena modelo epoch por epoch
    15.5. Se calculan métricas (loss, R², MAE, RMSE)
    15.6. Se guardan checkpoints del mejor modelo
16. Al completar:
    16.1. Se guarda modelo final en `ml/artifacts/regressors/hybrid.pt`
    16.2. Se almacenan métricas en `TrainingJob.metrics`
    17. Se actualiza `TrainingJob` a estado "completed"
18. Frontend muestra resultados de entrenamiento:
    - Métricas finales
    - Gráficas de pérdida
    - Opción para promover modelo a producción
19. Usuario puede promover modelo a producción (opcional)

### ✔ Flujos Alternativos

**A1. Entrenamiento incremental:**
- 3.1. Usuario selecciona "Entrenamiento Incremental"
- 3.2. Se entrena con datos nuevos agregados al dataset existente
- 3.3. Se usa modelo base y se ajusta

**A2. Error durante entrenamiento:**
- 15.1. Error en carga de datos o entrenamiento
- 15.2. `TrainingJob` se marca como "failed"
- 15.3. Se registra error en logs
- 15.4. Usuario puede revisar logs y reintentar

**A3. Entrenamiento cancelado:**
- 11.1. Usuario cancela entrenamiento
- 11.2. Celery task se cancela
- 11.3. `TrainingJob` se marca como "cancelled"

**A4. Validación de dataset:**
- 8.1. Sistema valida que dataset existe y es válido
- 8.2. Si no válido, se retorna error
- 8.3. Usuario debe preparar dataset primero

### ✔ Errores y Excepciones

- **403 Forbidden:** Usuario no es admin
- **400 Bad Request:** Parámetros inválidos, dataset no válido
- **500 Internal Server Error:** Error en entrenamiento
- **503 Service Unavailable:** Recursos computacionales no disponibles

### ✔ Puntos de Decisión

- ¿Usuario es admin? → Sí: Continuar, No: Error 403
- ¿Dataset válido? → Sí: Continuar, No: Error
- ¿Entrenamiento síncrono o asíncrono? → Síncrono: Ejecutar directo, Asíncrono: Encolar Celery
- ¿Entrenamiento exitoso? → Sí: Guardar modelo, No: Marcar fallido

### ✔ Backend

**Endpoint(s):**
- `POST /api/v1/ml/auto-train/` (síncrono)
- `POST /api/v1/train/jobs/create/` (asíncrono)
- `GET /api/v1/train/jobs/{job_id}/status/` (consultar estado)
- `POST /api/v1/ml/incremental/start/` (incremental)

**View / ViewSet:**
- `AutoTrainView` (`backend/api/views/ml/model_views.py:537`)
- `TrainingJobCreateView` (`backend/api/views/ml/`)

**Models:**
- `TrainingJob` (`backend/training/models.py:9`)

**Services:**
- `run_training_pipeline()` (`backend/ml/pipeline/train_all.py`)

**Tasks (Celery):**
- `train_model_task` (`backend/api/tasks/training_tasks.py:104`)

**Validaciones aplicadas:**
- Usuario es admin
- Dataset existe y es válido
- Parámetros de entrenamiento válidos
- Recursos disponibles

### ✔ Frontend

**Componente(s) involucrado(s):**
- `AdminTraining.vue` (`frontend/src/views/Admin/AdminTraining.vue`)

**Acciones del usuario:**
- Configurar parámetros
- Iniciar entrenamiento
- Monitorear progreso
- Ver resultados
- Promover modelo

**Estado global (Pinia) usado:**
- Store de entrenamiento (si existe)

**Rutas frontend:**
- `/admin/entrenamiento` → `AdminTraining.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Sin entrenamiento → Configurando → Entrenando → Completado / Fallido / Cancelado

**Condiciones:**
- Usuario admin: `user.is_admin or user.is_superuser`
- Dataset válido: `os.path.exists('backend/media/datasets/')`

**Bifurcaciones:**
- ¿Admin? → Sí: Continuar, No: Error
- ¿Síncrono? → Sí: Ejecutar, No: Encolar
- ¿Exitoso? → Sí: Guardar, No: Error

**Actividades del usuario:**
- Configurar
- Iniciar
- Monitorear

**Actividades del sistema:**
- Validar dataset
- Cargar datos
- Entrenar modelo
- Guardar artefactos
- Actualizar estado

**Procesos asincrónicos:**
- Entrenamiento usa Celery para ejecución en background
- Frontend consulta estado periódicamente

---

## Caso de Uso 16: Crear Agricultor

**Actor(es):** Administrador

**Descripción del proceso:** Permite a un administrador crear un nuevo usuario con rol de agricultor, asociándolo con información personal y de contacto.

**Evento de inicio:** El administrador accede a la gestión de agricultores y selecciona "Crear Nuevo Agricultor".

**Precondiciones:**
- El usuario tiene rol de Administrador
- El sistema tiene catalogos cargados (departamentos, municipios, etc.)

**Postcondiciones:**
- Se crea nuevo usuario con rol de agricultor
- Se crea registro de Persona asociado (opcional)
- Se envía email de bienvenida (si configurado)
- El agricultor queda disponible para asociar fincas

### ✔ Flujo Principal

1. Admin accede a `/admin/agricultores`
2. Admin hace clic en "Crear Nuevo Agricultor"
3. Sistema muestra modal `CreateFarmerModal`
4. Admin completa formulario:
   - Nombre (first_name)
   - Apellido (last_name)
   - Email (usado como username)
   - Contraseña temporal (o se genera automática)
   - Número de documento
   - Teléfono (opcional)
   - Dirección (opcional)
   - Municipio (opcional)
   - Departamento (opcional)
5. Frontend valida campos obligatorios
6. Frontend valida formato de email
7. Admin hace clic en "Guardar"
8. Frontend envía POST a `/api/v1/auth/register/` con datos
9. Backend recibe en `RegisterView.post()`
10. Se valida que usuario es admin (puede requerir verificación adicional)
11. `RegisterSerializer` valida datos
12. Se ejecuta `RegistrationService.register_user_with_email_verification()`
13. Se crea usuario con `User.objects.create_user()`
14. Se asigna rol "farmer" automáticamente (por signal o manualmente)
15. Si se proporciona información de Persona:
    15.1. Se crea registro `Persona` asociado al usuario
    15.2. Se llenan campos de documento, dirección, etc.
16. Se envía email de bienvenida con credenciales (si configurado)
17. Se crea log de auditoría
18. Backend retorna respuesta 201 con datos del agricultor creado
19. Frontend muestra mensaje de éxito
20. Frontend actualiza lista de agricultores
21. Admin puede asignar fincas al nuevo agricultor

### ✔ Flujos Alternativos

**A1. Crear sin verificación de email:**
- 12.1. Admin marca opción "Activar cuenta inmediatamente"
- 12.2. Usuario se crea con `is_active=True`
- 12.3. No se requiere verificación de email

**A2. Generación automática de contraseña:**
- 4.1. Admin no proporciona contraseña
- 4.2. Sistema genera contraseña temporal aleatoria
- 4.3. Contraseña se envía por email

**A3. Email ya existe:**
- 11.1. Email ya está registrado
- 11.2. Backend retorna error 400
- 11.3. Frontend muestra mensaje: "Este email ya está registrado"

### ✔ Errores y Excepciones

- **400 Bad Request:** Datos inválidos, email duplicado
- **403 Forbidden:** Usuario no es admin
- **500 Internal Server Error:** Error creando usuario, error enviando email

### ✔ Puntos de Decisión

- ¿Usuario es admin? → Sí: Continuar, No: Error 403
- ¿Email único? → Sí: Continuar, No: Error
- ¿Crear Persona? → Sí: Crear registro, No: Solo usuario

### ✔ Backend

**Endpoint(s):**
- `POST /api/v1/auth/register/` (reutiliza registro, con validación de admin)

**View / ViewSet:**
- `RegisterView` (`backend/auth_app/views/auth/registration_views.py:24`)
- Puede haber vista específica para admin

**Serializers:**
- `RegisterSerializer` (`backend/api/serializers/auth_serializers.py:94`)

**Models:**
- `User` (Django User)
- `Persona` (`backend/personas/models.py`)
- `Group` (para rol farmer)

**Services:**
- `RegistrationService` (`backend/api/services/auth/registration_service.py:22`)

**Validaciones aplicadas:**
- Usuario es admin (en frontend y opcionalmente backend)
- Email único
- Formato de email válido
- Documento único (si se valida)

### ✔ Frontend

**Componente(s) involucrado(s):**
- `AdminAgricultores.vue` (`frontend/src/views/Admin/AdminAgricultores.vue`)
- `CreateFarmerModal.vue` (`frontend/src/components/admin/AdminAgricultorComponents/CreateFarmerModal.vue`)

**Acciones del usuario:**
- Acceder a gestión
- Abrir modal
- Completar formulario
- Guardar

**Estado global (Pinia) usado:**
- `useAuthStore`: Para registro
- Store de agricultores (si existe)

**Rutas frontend:**
- `/admin/agricultores` → `AdminAgricultores.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Sin agricultor → Completando → Guardando → Agricultor creado / Error

**Condiciones:**
- Admin: `user.is_admin or user.is_superuser`
- Email único: `not User.objects.filter(email=email).exists()`

**Bifurcaciones:**
- ¿Admin? → Sí: Crear, No: Error
- ¿Email único? → Sí: Continuar, No: Error

**Actividades del usuario (admin):**
- Completar formulario
- Guardar

**Actividades del sistema:**
- Validar datos
- Crear usuario
- Asignar rol
- Crear Persona (opcional)
- Enviar email
- Auditoría

---

## Caso de Uso 17: Editar Agricultor

**Actor(es):** Administrador

**Descripción del proceso:** Permite a un administrador modificar la información de un agricultor existente, actualizando datos personales, contacto o estado de cuenta.

**Evento de inicio:** El administrador accede a la gestión de agricultores, selecciona un agricultor y hace clic en "Editar".

**Precondiciones:**
- El agricultor existe en el sistema
- El usuario tiene rol de Administrador
- El usuario está autenticado

**Postcondiciones:**
- Los datos del agricultor se actualizan en el sistema
- Se registra la modificación en auditoría
- Los cambios son visibles inmediatamente

### ✔ Flujo Principal

1. Admin accede a `/admin/agricultores`
2. Admin selecciona agricultor de la lista
3. Admin hace clic en "Editar"
4. Sistema muestra modal `EditFarmerModal` pre-poblado
5. Admin modifica campos deseados:
   - Nombre, apellido
   - Email (con validación de unicidad)
   - Teléfono
   - Dirección, municipio, departamento
   - Estado de cuenta (activo/inactivo)
6. Frontend valida cambios
7. Admin hace clic en "Guardar Cambios"
8. Frontend envía PATCH a `/api/v1/auth/users/{user_id}/update/`
9. Backend recibe en `UserUpdateView.patch()`
10. Se valida que usuario es admin
11. Se valida que agricultor existe
12. Se validan cambios:
    - Email único (si se modifica)
    - No auto-desactivación (admin no puede desactivarse a sí mismo)
13. Se actualiza `User` con nuevos datos
14. Si se modifican datos de Persona:
    14.1. Se actualiza registro `Persona` asociado
    14.2. Se actualizan campos de documento, dirección, etc.
15. Si se cambia estado de cuenta:
    15.1. Se actualiza `user.is_active`
    15.2. Si se desactiva, se invalidan sesiones activas
16. Se crea log de auditoría
17. Backend retorna respuesta 200 con usuario actualizado
18. Frontend muestra mensaje de éxito
19. Frontend actualiza lista de agricultores

### ✔ Flujos Alternativos

**A1. Cambio de email:**
- 12.1. Admin modifica email
- 12.2. Sistema valida que nuevo email no existe
- 12.3. Se actualiza email y username
- 12.4. Usuario deberá usar nuevo email para login

**A2. Desactivar cuenta:**
- 15.1. Admin desactiva cuenta de agricultor
- 15.2. Usuario no puede iniciar sesión
- 15.3. Sesiones activas se invalidan

**A3. Sin permisos:**
- 10.1. Usuario no es admin
- 10.2. Backend retorna error 403
- 10.3. Frontend muestra mensaje de acceso denegado

### ✔ Errores y Excepciones

- **400 Bad Request:** Datos inválidos, email duplicado
- **403 Forbidden:** Sin permisos de admin
- **404 Not Found:** Agricultor no encontrado
- **500 Internal Server Error:** Error guardando cambios

### ✔ Puntos de Decisión

- ¿Usuario es admin? → Sí: Continuar, No: Error 403
- ¿Agricultor existe? → Sí: Continuar, No: Error 404
- ¿Email único? → Sí: Continuar, No: Error
- ¿Auto-desactivación? → Sí: Error, No: Continuar

### ✔ Backend

**Endpoint(s):**
- `PATCH /api/v1/auth/users/{user_id}/update/`

**View / ViewSet:**
- `UserUpdateView` (`backend/auth_app/views/auth/user_views.py:150`)

**Serializers:**
- `UserSerializer` (actualización parcial)

**Models:**
- `User`
- `Persona` (`backend/personas/models.py`)

**Services:**
- Servicios de actualización de usuario (si existen)

**Validaciones aplicadas:**
- Usuario es admin
- Agricultor existe
- Email único (si se modifica)
- No auto-desactivación
- Campos permitidos

### ✔ Frontend

**Componente(s) involucrado(s):**
- `AdminAgricultores.vue`
- `EditFarmerModal.vue` (`frontend/src/components/admin/AdminAgricultorComponents/EditFarmerModal.vue`)

**Acciones del usuario:**
- Seleccionar agricultor
- Editar
- Guardar cambios

**Estado global (Pinia) usado:**
- Store de usuarios/agricultores

**Rutas frontend:**
- `/admin/agricultores` → `AdminAgricultores.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Agricultor existente → Editando → Guardando → Actualizado / Error

**Condiciones:**
- Admin: `user.is_admin`
- Agricultor existe: `User.objects.filter(id=user_id).exists()`
- Email único: `not User.objects.filter(email=new_email).exclude(id=user_id).exists()`

**Bifurcaciones:**
- ¿Admin? → Sí: Editar, No: Error
- ¿Email único? → Sí: Continuar, No: Error
- ¿Auto-desactivación? → Sí: Error, No: Continuar

**Actividades del usuario:**
- Modificar datos
- Guardar

**Actividades del sistema:**
- Validar permisos
- Validar datos
- Actualizar usuario
- Actualizar Persona
- Auditoría

---

## Caso de Uso 18: Asignar Rol

**Actor(es):** Administrador

**Descripción del proceso:** Permite a un administrador asignar o modificar el rol de un usuario, determinando sus permisos y capacidades en el sistema.

**Evento de inicio:** El administrador accede a la gestión de usuarios, selecciona un usuario y modifica su rol.

**Precondiciones:**
- El usuario objetivo existe en el sistema
- El usuario tiene rol de Administrador
- El sistema tiene grupos/roles configurados (admin, analyst, farmer)

**Postcondiciones:**
- El rol del usuario se actualiza
- Los permisos del usuario se actualizan según el nuevo rol
- Se registra el cambio en auditoría
- Si se cambia rol de admin, se valida que no sea el último admin

### ✔ Flujo Principal

1. Admin accede a gestión de usuarios (`/admin/usuarios` o similar)
2. Admin selecciona usuario de la lista
3. Admin accede a edición de usuario
4. Sistema muestra rol actual del usuario
5. Sistema muestra roles disponibles:
   - Administrador (admin): Acceso completo
   - Técnico/Analista (analyst): Análisis y gestión de lotes
   - Agricultor (farmer): Gestión de fincas y lotes propios
6. Admin selecciona nuevo rol del menú desplegable
7. Frontend valida que no se está removiendo el último admin
8. Admin confirma cambio
9. Frontend envía PATCH a `/api/v1/auth/users/{user_id}/update/` con campo `groups: [rol_seleccionado]`
10. Backend recibe en `UserUpdateView.patch()`
11. Se valida que usuario es admin
12. Se valida que usuario objetivo existe
13. Se valida que no se está removiendo el último admin del sistema:
    - Si usuario objetivo es admin y se le quita rol admin:
    - Se cuenta cuántos admins quedan
    - Si es el último, se retorna error
14. Se actualiza grupos del usuario con `_update_user_groups()`:
    14.1. Se limpian grupos actuales
    14.2. Se agrega nuevo grupo según rol seleccionado
15. Django actualiza permisos automáticamente según grupos
16. Se invalidan sesiones activas del usuario (si aplica)
17. Se crea log de auditoría con cambio de rol
18. Backend retorna respuesta 200 con usuario actualizado
19. Frontend muestra mensaje de éxito
20. Frontend actualiza vista con nuevo rol
21. Cambios de permisos son efectivos inmediatamente

### ✔ Flujos Alternativos

**A1. Remover rol admin del último administrador:**
- 13.1. Se intenta quitar rol admin al último admin
- 13.2. Sistema detecta que es el último
- 13.3. Backend retorna error 400: "No se puede remover el último administrador"
- 13.4. Frontend muestra mensaje de advertencia

**A2. Auto-asignación de rol (no permitido):**
- 6.1. Admin intenta quitarse su propio rol admin
- 6.2. Sistema previene auto-remoción
- 6.3. Se retorna error o se previene en frontend

**A3. Múltiples roles (si está permitido):**
- 14.1. Sistema permite asignar múltiples grupos
- 14.2. Usuario tiene permisos combinados

### ✔ Errores y Excepciones

- **400 Bad Request:** Intentando remover último admin, datos inválidos
- **403 Forbidden:** Usuario no es admin
- **404 Not Found:** Usuario objetivo no encontrado
- **500 Internal Server Error:** Error actualizando grupos

### ✔ Puntos de Decisión

- ¿Usuario es admin? → Sí: Continuar, No: Error 403
- ¿Usuario objetivo existe? → Sí: Continuar, No: Error 404
- ¿Es último admin? → Sí: Error, No: Continuar
- ¿Auto-remoción? → Sí: Prevenir, No: Continuar

### ✔ Backend

**Endpoint(s):**
- `PATCH /api/v1/auth/users/{user_id}/update/` (con campo `groups`)

**View / ViewSet:**
- `UserUpdateView` (`backend/auth_app/views/auth/user_views.py:150`)
  - `_update_user_groups()`: Actualiza grupos

**Models:**
- `User`
- `Group` (Django Groups para roles)

**Services:**
- Lógica de actualización de grupos

**Validaciones aplicadas:**
- Usuario es admin
- Usuario objetivo existe
- No remover último admin
- Grupos válidos

### ✔ Frontend

**Componente(s) involucrado(s):**
- `AdminUsuarios.vue` (`frontend/src/views/Admin/AdminUsuarios.vue`)
- Componente de edición de usuario

**Acciones del usuario:**
- Seleccionar usuario
- Cambiar rol
- Confirmar

**Estado global (Pinia) usado:**
- Store de usuarios

**Rutas frontend:**
- `/admin/usuarios` → `AdminUsuarios.vue`

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Rol actual → Seleccionando nuevo → Asignando → Rol actualizado / Error

**Condiciones:**
- Admin: `user.is_admin`
- Último admin: `User.objects.filter(groups__name='admin', is_active=True).count() == 1`
- Grupos válidos: `group_name in ['admin', 'analyst', 'farmer']`

**Bifurcaciones:**
- ¿Admin? → Sí: Continuar, No: Error
- ¿Último admin? → Sí: Error, No: Continuar
- ¿Grupo válido? → Sí: Asignar, No: Error

**Actividades del usuario:**
- Seleccionar nuevo rol
- Confirmar

**Actividades del sistema:**
- Validar permisos
- Validar último admin
- Actualizar grupos
- Actualizar permisos
- Invalidar sesiones
- Auditoría

---

## Caso de Uso 19: Editar Perfil

**Actor(es):** Usuario autenticado

**Descripción del proceso:** Permite al usuario autenticado modificar su propia información de perfil, incluyendo nombre, apellido, email y datos de contacto.

**Evento de inicio:** El usuario accede a su perfil o configuración y selecciona "Editar Perfil".

**Precondiciones:**
- El usuario está autenticado
- El usuario tiene una cuenta activa

**Postcondiciones:**
- Los datos del perfil se actualizan en el sistema
- El usuario puede ver los cambios inmediatamente
- Se registra la modificación en auditoría (opcional)

### ✔ Flujo Principal

1. Usuario accede a configuración de perfil (`/agricultor/configuracion` o `/auth/profile`)
2. Usuario hace clic en "Editar Perfil"
3. Sistema muestra formulario pre-poblado con datos actuales
4. Usuario modifica campos deseados:
   - Nombre (first_name)
   - Apellido (last_name)
   - Email (opcional, requiere verificación si cambia)
   - Teléfono (phone_number)
5. Frontend valida cambios
6. Frontend valida formato de email si se modifica
7. Usuario hace clic en "Guardar Cambios"
8. Frontend envía PATCH a `/api/v1/auth/profile/`
9. Backend recibe en `UserProfileView.patch()` o similar
10. Se valida que usuario está autenticado
11. Se ejecuta `ProfileService.update_user_profile()`
12. Servicio valida campos permitidos:
    - User: first_name, last_name, email
    - UserProfile: phone_number (si existe modelo extendido)
13. Si se modifica email:
    13.1. Se valida que nuevo email no existe (único)
    13.2. Se actualiza email y username
    13.3. Puede requerir verificación de nuevo email (según diseño)
14. Se actualiza modelo User con nuevos datos
15. Si existe UserProfile, se actualiza también
16. Se guardan cambios en base de datos
17. Se crea log de auditoría (opcional, puede ser solo para cambios críticos)
18. Backend retorna respuesta 200 con usuario actualizado
19. Frontend actualiza datos en store Pinia
20. Frontend muestra mensaje de éxito
21. Frontend actualiza vista con datos nuevos
22. Si cambió email, frontend puede mostrar advertencia sobre verificación

### ✔ Flujos Alternativos

**A1. Cambio de email:**
- 13.1. Usuario cambia email
- 13.2. Sistema valida unicidad
- 13.3. Se actualiza email y username
- 13.4. Sistema puede requerir verificación de nuevo email
- 13.5. Usuario recibe email de verificación

**A2. Actualización de Persona (si aplica):**
- 4.1. Usuario modifica datos que van en modelo Persona
- 4.2. Frontend envía también a `/api/v1/personas/perfil/`
- 4.3. Se actualiza registro Persona asociado
- 4.4. Se sincronizan datos entre User y Persona

**A3. Email ya existe:**
- 13.1. Usuario intenta usar email existente
- 13.2. Sistema valida y encuentra duplicado
- 13.3. Backend retorna error 400
- 13.4. Frontend muestra: "Este email ya está en uso"

**A4. Solo lectura de algunos campos:**
- 4.1. Algunos campos son de solo lectura (ej: username, fecha registro)
- 4.2. Frontend deshabilita campos no editables
- 4.3. Backend ignora cambios en campos protegidos

### ✔ Errores y Excepciones

- **400 Bad Request:** Datos inválidos, email duplicado
- **401 Unauthorized:** Usuario no autenticado
- **500 Internal Server Error:** Error guardando cambios

### ✔ Puntos de Decisión

- ¿Usuario autenticado? → Sí: Continuar, No: Error 401
- ¿Email único? → Sí: Continuar, No: Error
- ¿Cambió email? → Sí: Validar unicidad y posible verificación, No: Continuar

### ✔ Backend

**Endpoint(s):**
- `PATCH /api/v1/auth/profile/`
- `GET /api/v1/auth/profile/` (obtener perfil)

**View / ViewSet:**
- `UserProfileView` (`backend/auth_app/views/auth/`)

**Serializers:**
- `UserSerializer` (actualización parcial)
- `UserProfileSerializer` (si existe modelo extendido)

**Models:**
- `User`
- `UserProfile` (`backend/auth_app/models.py:99` - si existe)
- `Persona` (datos extendidos, opcional)

**Services:**
- `ProfileService` (`backend/api/services/auth/profile_service.py:14`)
  - `update_user_profile()`: Actualiza perfil con validaciones

**Validaciones aplicadas:**
- Usuario autenticado
- Campos permitidos
- Email único (si se modifica)
- Formato de email válido

### ✔ Frontend

**Componente(s) involucrado(s):**
- `AgricultorConfiguracion.vue` (`frontend/src/views/Agricultor/AgricultorConfiguracion.vue`)
- Componente de edición de perfil

**Acciones del usuario:**
- Acceder a configuración
- Editar datos
- Guardar cambios

**Validaciones previas:**
- Formato de email válido
- Campos no vacíos (si requeridos)

**Estado global (Pinia) usado:**
- `useAuthStore` (`frontend/src/stores/auth.js`)
  - `updateProfile()`: Actualiza perfil
  - `user`: Datos actualizados

**Rutas frontend:**
- `/agricultor/configuracion` → `AgricultorConfiguracion.vue`
- `/auth/profile` (si existe ruta específica)

### ✔ Datos que requiere el diagrama de flujo

**Estados:**
- Perfil actual → Editando → Guardando → Perfil actualizado / Error

**Condiciones:**
- Usuario autenticado: `request.user.is_authenticated`
- Email único: `not User.objects.filter(email=new_email).exclude(id=user.id).exists()`

**Bifurcaciones:**
- ¿Autenticado? → Sí: Continuar, No: Error
- ¿Email único? → Sí: Continuar, No: Error
- ¿Cambió email? → Sí: Validar y posible verificación, No: Continuar

**Actividades del usuario:**
- Modificar datos
- Guardar cambios

**Actividades del sistema:**
- Validar datos
- Actualizar User
- Actualizar UserProfile (si existe)
- Actualizar Persona (si aplica)
- Auditoría (opcional)
- Retornar respuesta

---

## 📝 Notas Finales

Este documento contiene la información completa de los 19 casos de uso principales del sistema CacaoScan, con todos los detalles necesarios para construir diagramas de flujo detallados en PlantUML o Mermaid.

Cada caso de uso incluye:
- ✅ Actores involucrados
- ✅ Descripción completa del proceso
- ✅ Precondiciones y postcondiciones
- ✅ Flujo principal paso a paso
- ✅ Flujos alternativos
- ✅ Manejo de errores y excepciones
- ✅ Puntos de decisión
- ✅ Información técnica completa (endpoints, views, serializers, models, services)
- ✅ Detalles de frontend (componentes, validaciones, estado)
- ✅ Datos para diagramas (estados, condiciones, bifurcaciones, actividades)

**Recomendaciones para construcción de diagramas:**
1. Usar diferentes colores para actividades del usuario vs. sistema
2. Marcar claramente puntos de decisión (rombos)
3. Incluir manejo de errores como flujos paralelos
4. Mostrar procesos asincrónicos (Celery) con notas especiales
5. Indicar validaciones tanto frontend como backend
6. Incluir estados intermedios para mejor claridad

---

**Documento generado para:** CacaoScan  
**Versión:** 1.0  
**Fecha:** 2025  

