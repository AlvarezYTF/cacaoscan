"""
URL configuration for CacaoScan project.

Configuración principal de URLs que incluye:
- Panel de administración Django
- APIs REST para predicción de imágenes
- Documentación Swagger/OpenAPI
- Archivos media (imágenes subidas)
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración de Swagger/OpenAPI para documentación de API
schema_view = get_schema_view(
    openapi.Info(
        title="CacaoScan API",
        default_version='v1',
        description="""
        API REST para el sistema de análisis de granos de cacao CacaoScan.
        
        ## Funcionalidades principales:
        
        ### Predicción de imágenes
        - **POST /api/images/predict/** - Sube imagen y obtiene predicción ML
        - **GET /api/images/** - Lista historial de predicciones
        - **GET /api/images/{id}/** - Detalles de predicción específica
        - **GET /api/images/stats/** - Estadísticas globales
        
        ### Características predichas
        - **Dimensiones físicas**: ancho, alto, grosor (mm)
        - **Peso**: peso estimado del grano (g)
        - **Calidad**: nivel de calidad predicho
        - **Confianza**: métricas de confiabilidad
        
        ### Filtros soportados
        - Estado de procesamiento (processed=true/false)
        - Calidad (quality=excellent/good/fair/poor)
        - Número de lote (batch=XXX)
        - Rango de fechas (date_from/date_to)
        
        ### Formatos de respuesta
        Todas las respuestas están en formato JSON con estructura consistente.
        Los endpoints de predicción incluyen métricas de confianza y tiempo de procesamiento.
        """,
        terms_of_service="https://www.cacaoscan.com/terms/",
        contact=openapi.Contact(email="api@cacaoscan.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Panel de administración Django
    path('admin/', admin.site.urls),
    
    # APIs de la aplicación
    path('api/images/', include('apps.images.urls', namespace='images')),
    
    # Documentación de API (Swagger/OpenAPI)
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('api/schema.yaml', schema_view.without_ui(cache_timeout=0), name='schema-yaml'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Endpoint adicional para desarrollo/debugging
    from django.http import JsonResponse
    from django.views.decorators.http import require_http_methods
    
    @require_http_methods(["GET"])
    def health_check(request):
        return JsonResponse({'status': 'ok', 'version': '1.0'})
    
    urlpatterns += [
        path('api/health/', health_check, name='health-check'),
    ]

"""
Estructura final de URLs:

## URLs principales:
- /admin/ - Panel de administración Django
- /api/images/ - APIs de predicción de imágenes
- /api/docs/ - Documentación Swagger interactiva  
- /api/redoc/ - Documentación ReDoc
- /media/ - Archivos media (solo en desarrollo)

## APIs de predicción:
- POST /api/images/predict/ - Predicción desde imagen
- GET /api/images/ - Lista predicciones con filtros
- GET /api/images/{id}/ - Detalles de predicción
- GET /api/images/stats/ - Estadísticas globales
- PUT /api/images/{id}/ - Actualizar metadatos
- DELETE /api/images/{id}/ - Eliminar predicción

## Documentación:
- /api/docs/ - UI interactiva para probar endpoints
- /api/redoc/ - Documentación estática elegante
- /api/schema.json - Schema OpenAPI en JSON
- /api/schema.yaml - Schema OpenAPI en YAML

## Ejemplo de uso completo:

1. **Realizar predicción**:
   ```
   POST /api/images/predict/
   Content-Type: multipart/form-data
   
   {
     "image": <archivo_imagen>,
     "batch_number": "LOTE001",
     "origin": "Colombia"
   }
   ```

2. **Ver historial**:
   ```
   GET /api/images/?processed=true&quality=excellent&date_from=2024-01-01
   ```

3. **Obtener estadísticas**:
   ```
   GET /api/images/stats/
   ```

4. **Ver documentación**:
   ```
   GET /api/docs/
   ```
"""
