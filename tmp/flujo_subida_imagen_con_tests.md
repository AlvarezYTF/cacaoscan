# Flujo de Subida de Imagen con Comandos de Test

## Resumen del Flujo

El flujo de subida de imagen en CacaoScan permite subir una o múltiples imágenes de cacao a través de una API REST. Las imágenes se validan, almacenan y se asocian al usuario autenticado.

---

## Componentes del Flujo

### 1. Frontend (Vue.js)

**Archivo:** `frontend/src/views/UploadImagesView.vue`

- El usuario selecciona archivos mediante un input de tipo file
- Se valida el tamaño y tipo de archivo antes de subir
- Se crea un `FormData` con las imágenes
- Se envía petición POST a `/api/v1/images/upload/`
- Se muestra el progreso y resultados de la subida

**Código clave:**
```172:233:frontend/src/views/UploadImagesView.vue
const uploadImages = async () => {
  if (files.value.length === 0) {
    return
  }

  isUploading.value = true
  uploadStatus.value = null

  const formData = new FormData()
  for (const file of files.value) {
    formData.append('images', file)
  }

  try {
    const res = await api.post('/images/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })

    const { uploaded, total_uploaded, total_errors, errors } = res.data

    if (total_uploaded > 0) {
      uploadedImages.value = [...uploadedImages.value, ...uploaded]
      uploadStatus.value = {
        type: 'success',
        title: '✅ Subida completada',
        message: (() => {
          const imagesText = total_uploaded === 1 ? 'imagen' : 'imágenes'
          const successMsg = `Se subieron ${total_uploaded} ${imagesText} correctamente.`
          if (total_errors > 0) {
            const errorsText = total_errors === 1 ? 'imagen' : 'imágenes'
            return `${successMsg} ${total_errors} ${errorsText} con errores.`
          }
          return successMsg
        })(),
        errors: errors || []
      }
      
      // Limpiar archivos subidos exitosamente (pero mantener el status)
      clearFiles(false)
    } else {
      uploadStatus.value = {
        type: 'error',
        title: '❌ Error al subir imágenes',
        message: 'No se pudo subir ninguna imagen.',
        errors: errors || []
      }
    }
  } catch (error) {
    console.error('Error al subir imágenes:', error)
    uploadStatus.value = {
      type: 'error',
      title: '❌ Error al subir imágenes',
      message: error.response?.data?.error || error.message || 'Error desconocido al subir las imágenes',
      errors: error.response?.data?.errors || []
    }
  } finally {
    isUploading.value = false
  }
}
```

### 2. Backend - Vista (Django REST Framework)

**Archivo:** `backend/images_app/views.py`

**Vista:** `CacaoImageUploadView`

**Flujo:**
1. Recibe múltiples imágenes en `request.FILES.getlist('images')`
2. Valida cada imagen (tamaño máximo 20MB, tipos permitidos: jpeg, jpg, png, webp)
3. Crea instancias de `CacaoImage` para cada imagen válida
4. Asocia la imagen con el usuario autenticado
5. Opcionalmente asocia con una finca si se proporciona `finca_id`
6. Retorna respuesta con imágenes subidas y errores (si los hay)

**Código clave:**
```84:119:backend/images_app/views.py
    def post(self, request):
        """
        Sube múltiples imágenes de cacao.
        
        Permite subir una o varias imágenes en una sola petición.
        Las imágenes se almacenan en AWS S3 (si está configurado) o localmente.
        """
        images = request.FILES.getlist('images')
        
        if not images:
            return Response(
                {'error': 'No se proporcionaron imágenes'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        uploaded = []
        errors = []
        
        for idx, image_file in enumerate(images):
            result, error = self._process_single_image(request, image_file, idx)
            if result:
                uploaded.append(result)
            else:
                errors.append(error)
        
        response_data = {
            'uploaded': uploaded,
            'total_uploaded': len(uploaded),
            'total_errors': len(errors)
        }
        
        if errors:
            response_data['errors'] = errors
        
        http_status = self._determine_http_status(len(uploaded), len(errors))
        return Response(response_data, status=http_status)
```

### 3. Backend - Servicio (Opcional)

**Archivo:** `backend/images_app/services/image/management_service.py`

**Servicio:** `ImageManagementService`

Proporciona una capa de abstracción adicional para la gestión de imágenes, incluyendo validaciones y metadatos.

---

## Endpoint de la API

**URL:** `POST /api/v1/images/upload/`

**Autenticación:** Requerida (IsAuthenticated)

**Content-Type:** `multipart/form-data`

**Parámetros:**
- `images`: Archivo(s) de imagen (múltiples permitidos)
- `finca_id`: (Opcional) ID de la finca a asociar

**Respuesta exitosa (201 Created):**
```json
{
  "uploaded": [
    {
      "id": 1,
      "file_name": "test.jpg",
      "image_url": "http://example.com/media/cacao_images/test.jpg",
      "file_size": 1024,
      "file_type": "image/jpeg",
      "processed": false,
      "created_at": "2024-12-19T10:00:00Z"
    }
  ],
  "total_uploaded": 1,
  "total_errors": 0
}
```

**Respuesta con errores parciales (207 Multi-Status):**
```json
{
  "uploaded": [...],
  "total_uploaded": 2,
  "total_errors": 1,
  "errors": [
    {
      "file": "large.jpg",
      "error": "El archivo excede el tamaño máximo de 20MB"
    }
  ]
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

### Tests de Vistas (Upload)

**Archivo:** `backend/images_app/tests/test_views.py`

#### Ejecutar todos los tests de subida de imágenes:

```bash
# Desde backend/
pytest images_app/tests/test_views.py::TestCacaoImageUploadView -v
```

#### Tests específicos:

```bash
# Test: Subida de una imagen exitosa
pytest images_app/tests/test_views.py::TestCacaoImageUploadView::test_post_single_image_success -v

# Test: Subida de múltiples imágenes exitosa
pytest images_app/tests/test_views.py::TestCacaoImageUploadView::test_post_multiple_images_success -v

# Test: Validación de tamaño de archivo válido
pytest images_app/tests/test_views.py::TestCacaoImageUploadView::test_validate_file_size_valid -v

# Test: Validación de tamaño de archivo demasiado grande
pytest images_app/tests/test_views.py::TestCacaoImageUploadView::test_validate_file_size_too_large -v

# Test: Validación de tipo de archivo válido
pytest images_app/tests/test_views.py::TestCacaoImageUploadView::test_validate_file_type_valid -v

# Test: Validación de tipo de archivo inválido
pytest images_app/tests/test_views.py::TestCacaoImageUploadView::test_validate_file_type_invalid -v

# Test: Procesamiento de una imagen exitosa
pytest images_app/tests/test_views.py::TestCacaoImageUploadView::test_process_single_image_success -v

# Test: Error al procesar imagen por tamaño
pytest images_app/tests/test_views.py::TestCacaoImageUploadView::test_process_single_image_size_error -v

# Test: Error al procesar imagen por tipo
pytest images_app/tests/test_views.py::TestCacaoImageUploadView::test_process_single_image_type_error -v

# Test: Sin imágenes en la petición
pytest images_app/tests/test_views.py::TestCacaoImageUploadView::test_post_no_images -v

# Test: Asignación de finca válida
pytest images_app/tests/test_views.py::TestCacaoImageUploadView::test_assign_finca_with_valid_id -v

# Test: Asignación de finca inválida
pytest images_app/tests/test_views.py::TestCacaoImageUploadView::test_assign_finca_with_invalid_id -v
```

### Tests de Servicio (Management Service)

**Archivo:** `backend/images_app/tests/test_management_service.py`

#### Ejecutar todos los tests del servicio:

```bash
# Desde backend/
pytest images_app/tests/test_management_service.py::TestImageManagementService -v
```

#### Tests específicos:

```bash
# Test: Subida de imagen exitosa mediante servicio
pytest images_app/tests/test_management_service.py::TestImageManagementService::test_upload_image_success -v

# Test: Subida sin archivo
pytest images_app/tests/test_management_service.py::TestImageManagementService::test_upload_image_no_file -v

# Test: Obtener imágenes del usuario
pytest images_app/tests/test_management_service.py::TestImageManagementService::test_get_user_images -v

# Test: Obtener imágenes con filtros
pytest images_app/tests/test_management_service.py::TestImageManagementService::test_get_user_images_with_filters -v

# Test: Obtener detalles de imagen
pytest images_app/tests/test_management_service.py::TestImageManagementService::test_get_image_details -v

# Test: Imagen no encontrada
pytest images_app/tests/test_management_service.py::TestImageManagementService::test_get_image_details_not_found -v

# Test: Eliminar imagen exitosamente
pytest images_app/tests/test_management_service.py::TestImageManagementService::test_delete_image_success -v

# Test: Obtener estadísticas de imágenes
pytest images_app/tests/test_management_service.py::TestImageManagementService::test_get_image_statistics -v
```

### Tests de Listado de Imágenes

**Archivo:** `backend/images_app/tests/test_views.py`

```bash
# Test: Lista vacía
pytest images_app/tests/test_views.py::TestCacaoImageListView::test_get_list_empty -v

# Test: Lista con imágenes
pytest images_app/tests/test_views.py::TestCacaoImageListView::test_get_list_with_images -v

# Test: Ordenamiento por fecha de creación
pytest images_app/tests/test_views.py::TestCacaoImageListView::test_get_list_ordered_by_created_at -v

# Test: Solo imágenes del usuario
pytest images_app/tests/test_views.py::TestCacaoImageListView::test_get_list_only_user_images -v
```

### Ejecutar Todos los Tests de Imágenes

```bash
# Desde backend/
pytest images_app/tests/ -v
```

### Ejecutar con Cobertura

```bash
# Desde backend/
pytest images_app/tests/test_views.py --cov=images_app.views --cov-report=html
pytest images_app/tests/test_management_service.py --cov=images_app.services.image.management_service --cov-report=html
```

---

## Flujo Completo Paso a Paso

### 1. Usuario selecciona imágenes en el frontend
- Validación inicial en el cliente (tamaño, tipo)
- Preparación de FormData

### 2. Petición HTTP POST al backend
- Endpoint: `/api/v1/images/upload/`
- Headers: `Content-Type: multipart/form-data`
- Autenticación: Token JWT o sesión

### 3. Backend procesa la petición
- **Validación de autenticación:** Verifica que el usuario esté autenticado
- **Extracción de archivos:** `request.FILES.getlist('images')`
- **Validación por archivo:**
  - Tamaño máximo: 20MB
  - Tipos permitidos: image/jpeg, image/jpg, image/png, image/webp
- **Creación de instancias:** `CacaoImage` para cada imagen válida
- **Asociación:** Usuario y opcionalmente finca
- **Almacenamiento:** Guarda en base de datos y sistema de archivos (local o S3)

### 4. Respuesta al frontend
- **201 Created:** Todas las imágenes se subieron exitosamente
- **207 Multi-Status:** Algunas imágenes se subieron, otras tuvieron errores
- **400 Bad Request:** Ninguna imagen se pudo subir

### 5. Frontend procesa la respuesta
- Muestra mensajes de éxito/error
- Actualiza la lista de imágenes subidas
- Limpia el formulario si todo fue exitoso

---

## Validaciones Implementadas

### Tamaño de Archivo
- **Máximo:** 20MB
- **Validación:** En frontend y backend
- **Error:** "El archivo excede el tamaño máximo de 20MB"

### Tipo de Archivo
- **Permitidos:** image/jpeg, image/jpg, image/png, image/webp
- **Validación:** En frontend y backend
- **Error:** "Tipo de archivo no permitido. Permitidos: ..."

### Autenticación
- **Requerida:** Sí
- **Permiso:** `IsAuthenticated`
- **Error:** 401 Unauthorized si no está autenticado

---

## Ejemplo de Uso con cURL

```bash
# Subir una imagen
curl -X POST http://localhost:8000/api/v1/images/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "images=@/path/to/image.jpg" \
  -F "finca_id=1"

# Subir múltiples imágenes
curl -X POST http://localhost:8000/api/v1/images/upload/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "images=@/path/to/image1.jpg" \
  -F "images=@/path/to/image2.jpg" \
  -F "images=@/path/to/image3.jpg"
```

---

## Troubleshooting

### Error: "No se proporcionaron imágenes"
**Causa:** No se enviaron archivos en la petición.
**Solución:** Verificar que el campo `images` esté presente en el FormData.

### Error: "El archivo excede el tamaño máximo de 20MB"
**Causa:** El archivo es demasiado grande.
**Solución:** Reducir el tamaño de la imagen o comprimirla.

### Error: "Tipo de archivo no permitido"
**Causa:** El tipo MIME no está en la lista de permitidos.
**Solución:** Convertir la imagen a JPEG, PNG o WebP.

### Error: 401 Unauthorized
**Causa:** El usuario no está autenticado.
**Solución:** Incluir el token de autenticación en los headers.

### Tests fallan con "collected 0 items"
**Causa:** Ruta incorrecta o archivo no encontrado.
**Solución:** Verificar que estás en el directorio `backend/` y usar rutas relativas:
```bash
pytest images_app/tests/test_views.py -v
```

---

## Archivos Relacionados

### Backend
- `backend/images_app/views.py` - Vistas de la API
- `backend/images_app/models.py` - Modelo CacaoImage
- `backend/images_app/serializers.py` - Serializadores
- `backend/images_app/services/image/management_service.py` - Servicio de gestión
- `backend/images_app/tests/test_views.py` - Tests de vistas
- `backend/images_app/tests/test_management_service.py` - Tests de servicio

### Frontend
- `frontend/src/views/UploadImagesView.vue` - Vista de subida
- `frontend/src/services/datasetApi.js` - Servicio de API
- `frontend/src/composables/useImageHandling.js` - Composable para manejo de imágenes
- `frontend/src/composables/useFileUpload.js` - Composable para subida de archivos

---

## Notas Adicionales

- Las imágenes se almacenan en AWS S3 si está configurado, o localmente en `media/cacao_images/`
- Cada imagen se asocia automáticamente con el usuario autenticado
- Se puede asociar opcionalmente con una finca mediante el parámetro `finca_id`
- Los tests usan fixtures con usuarios únicos (UUID) para evitar conflictos
- Todos los tests requieren `@pytest.mark.django_db` para acceso a la base de datos

