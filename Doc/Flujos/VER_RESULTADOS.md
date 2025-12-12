# Flujo de Ver Resultados de Análisis con Comandos de Test

## Resumen del Flujo

El flujo de visualización de resultados permite al usuario ver los resultados de un análisis de imagen de cacao, incluyendo dimensiones predichas, peso estimado y visualización de la imagen procesada.

---

## Componentes del Flujo

### 1. Frontend (Vue.js)

**Archivo:** `frontend/src/views/DetalleAnalisisView.vue` o `frontend/src/components/analysis/DetalleAnalisis.vue`

- El usuario accede a la vista de resultados desde el historial o después de un análisis
- Se carga el ID de la imagen o predicción
- Se envía petición GET a `/api/v1/images/{image_id}/` o `/api/v1/images/` con filtros
- Se muestran los resultados: dimensiones, peso, imágenes (original y procesada)

**Código clave:**
```javascript
// Ejemplo de flujo en el frontend
const loadAnalysisResults = async (imageId) => {
  try {
    const response = await imagesApi.getImageDetails(imageId)
    const imageData = response.data
    
    // Mostrar resultados
    results.value = {
      dimensions: {
        alto: imageData.prediction?.alto_mm,
        ancho: imageData.prediction?.ancho_mm,
        grosor: imageData.prediction?.grosor_mm
      },
      peso: imageData.prediction?.peso_g,
      imageUrl: imageData.image_url,
      processedImageUrl: imageData.processed_image_url,
      confidence: imageData.prediction?.confidence
    }
  } catch (error) {
    // Manejar errores
  }
}
```

### 2. Backend - Vista (Django REST Framework)

**Archivo:** `backend/images_app/views/image/user/image_views.py` (si existe)

**Vista:** `ImageDetailView` o `CacaoImageDetailView`

**Flujo:**
1. Recibe petición GET con `image_id`
2. Valida permisos del usuario (propietario o admin)
3. Obtiene `CacaoImage` con predicción relacionada
4. Serializa datos con `CacaoImageSerializer` (incluye predicción)
5. Retorna respuesta con datos completos

---

## Endpoint de la API

**URL:** `GET /api/v1/images/{image_id}/`

**Autenticación:** Requerida (IsAuthenticated)

**Content-Type:** `application/json`

**Parámetros:**
- `image_id`: ID de la imagen (en la URL)

**Respuesta exitosa (200 OK):**
```json
{
  "id": 1,
  "file_name": "cacao_image.jpg",
  "image_url": "http://example.com/media/cacao_images/cacao_image.jpg",
  "processed_image_url": "http://example.com/media/crops/cacao_image_processed.png",
  "file_size": 1024000,
  "file_type": "image/jpeg",
  "processed": true,
  "created_at": "2024-12-19T10:00:00Z",
  "user": 1,
  "prediction": {
    "id": 1,
    "alto_mm": 25.5,
    "ancho_mm": 18.3,
    "grosor_mm": 12.1,
    "peso_g": 8.7,
    "confidence": 0.92,
    "created_at": "2024-12-19T10:05:00Z"
  }
}
```

**Respuesta con errores (404 Not Found):**
```json
{
  "error": "Imagen no encontrada",
  "details": "La imagen solicitada no existe o no tienes permisos para acceder a ella"
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

### Tests de Vistas (Ver Resultados)

**Archivo:** `backend/images_app/tests/test_image_views.py` (si existe)

#### Ejecutar todos los tests de visualización:

```bash
# Desde backend/
pytest images_app/tests/test_image_views.py::TestImageDetailView -v
```

#### Tests específicos:

```bash
# Test: Obtener detalles de imagen exitoso
pytest images_app/tests/test_image_views.py::TestImageDetailView::test_get_success -v

# Test: Imagen no encontrada
pytest images_app/tests/test_image_views.py::TestImageDetailView::test_get_not_found -v

# Test: Sin permisos para ver imagen
pytest images_app/tests/test_image_views.py::TestImageDetailView::test_get_no_permission -v

# Test: Imagen sin predicción
pytest images_app/tests/test_image_views.py::TestImageDetailView::test_get_no_prediction -v

# Test: Listar imágenes del usuario
pytest images_app/tests/test_image_views.py::TestImageListView::test_get_user_images -v
```

### Tests de Servicio (Analysis Service)

**Archivo:** `backend/api/tests/test_analysis_service.py` (si existe)

```bash
# Test: Obtener historial de análisis
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_get_analysis_history -v

# Test: Obtener estadísticas de análisis
pytest api/tests/test_analysis_service.py::TestAnalysisService::test_get_analysis_statistics -v
```

### Ejecutar Todos los Tests de Visualización

```bash
# Desde backend/
pytest images_app/tests/test_image_views.py api/tests/test_analysis_service.py -v -k "detail|history|result"
```

### Ejecutar con Cobertura

```bash
# Desde backend/
pytest images_app/tests/test_image_views.py --cov=images_app.views.image.user.image_views --cov-report=html
```

---

## Flujo Completo Paso a Paso

### 1. Usuario accede a resultados
- Desde historial de análisis o después de completar un análisis
- Se obtiene el ID de la imagen o predicción

### 2. Petición HTTP GET al backend
- Endpoint: `/api/v1/images/{image_id}/`
- Headers: `Authorization: Bearer <token>`

### 3. Backend procesa la petición
- **Validación de autenticación:** Verifica que el usuario esté autenticado
- **Validación de permisos:** Verifica que el usuario sea propietario o admin
- **Obtención de datos:** Obtiene `CacaoImage` con predicción relacionada
- **Serialización:** Serializa datos con `CacaoImageSerializer`

### 4. Respuesta al frontend
- **200 OK:** Datos completos de la imagen y predicción
- **404 Not Found:** Imagen no encontrada o sin permisos

### 5. Frontend procesa la respuesta
- Muestra dimensiones (alto, ancho, grosor en mm)
- Muestra peso estimado (en gramos)
- Muestra imágenes (original y procesada)
- Muestra información adicional (fecha, confianza, etc.)

---

## Validaciones Implementadas

### Permisos
- **Propietario:** El usuario puede ver sus propias imágenes
- **Administrador:** Los administradores pueden ver todas las imágenes
- **Validación:** En backend mediante permisos
- **Error:** 404 Not Found si no tiene permisos

### Existencia de Datos
- **Imagen:** Debe existir en el sistema
- **Predicción:** Puede no existir si el análisis no se completó
- **Validación:** En backend al obtener datos
- **Error:** 404 Not Found si la imagen no existe

---

## Ejemplo de Uso con cURL

```bash
# Obtener detalles de una imagen
curl -X GET http://localhost:8000/api/v1/images/1/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Listar imágenes del usuario
curl -X GET http://localhost:8000/api/v1/images/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Troubleshooting

### Error: "Imagen no encontrada"
**Causa:** La imagen no existe o el usuario no tiene permisos.
**Solución:** Verificar que el ID de imagen sea correcto y que el usuario tenga permisos.

### Error: "No tienes permisos para ver esta imagen"
**Causa:** El usuario no es propietario de la imagen ni es administrador.
**Solución:** Verificar permisos o contactar al administrador.

### Error: Imagen sin predicción
**Causa:** El análisis no se completó o falló.
**Solución:** Verificar que el análisis se haya completado exitosamente.

### Error: Imágenes no se cargan
**Causa:** Problema con URLs de imágenes o almacenamiento.
**Solución:** Verificar configuración de almacenamiento y URLs de medios.

---

## Archivos Relacionados

### Backend
- `backend/images_app/views/image/user/image_views.py` - Vistas de imágenes
- `backend/images_app/serializers/image_serializers.py` - Serializers de imágenes
- `backend/images_app/models.py` - Modelos CacaoImage y CacaoPrediction
- `backend/api/services/analysis_service.py` - Servicio de análisis

### Frontend
- `frontend/src/views/DetalleAnalisisView.vue` - Vista de detalles
- `frontend/src/components/analysis/DetalleAnalisis.vue` - Componente de detalles
- `frontend/src/services/imagesApi.js` - Servicio de API de imágenes
- `frontend/src/stores/analysis.js` - Store de análisis (Pinia)

---

## Notas Adicionales

- Los resultados se muestran con precisión de 2 decimales para dimensiones y peso
- Las imágenes se muestran con URLs completas para acceso directo
- El sistema muestra confianza del modelo si está disponible
- Los usuarios solo pueden ver análisis de sus propias imágenes o de fincas/lotes a los que tienen acceso
- Los administradores pueden ver todos los análisis del sistema

