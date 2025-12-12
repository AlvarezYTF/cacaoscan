"""
URL configuration for cacaoscan project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_safe, require_http_methods

# Swagger schema view - cargado de forma lazy para evitar problemas de memoria con pkg_resources
def get_schema_view_lazy():
    """Carga drf_yasg solo cuando se necesita para evitar problemas de memoria al iniciar."""
    try:
        from rest_framework import permissions
        from drf_yasg.views import get_schema_view
        from drf_yasg import openapi
        
        return get_schema_view(
            openapi.Info(
                title="CacaoScan API",
                default_version='v1',
                description="API para medición de dimensiones y peso de granos de cacao usando ML",
                terms_of_service="https://www.google.com/policies/terms/",
                contact=openapi.Contact(email="contact@cacaoscan.local"),
                license=openapi.License(name="BSD License"),
            ),
            public=True,
            permission_classes=[permissions.AllowAny],
        )
    except Exception:
        # Si hay error al cargar drf_yasg, retornar una vista dummy
        from django.views.generic import TemplateView
        from django.http import JsonResponse
        
        class DummySchemaView:
            @staticmethod
            def without_ui(cache_timeout):
                def view(request, format=None):
                    return JsonResponse({'error': 'Swagger not available'}, status=503)
                # Only allow safe methods for diagnostic/schema endpoints to avoid
                # accidental state changes if a client attempts to use unsafe
                # HTTP methods against this fallback view.
                return require_http_methods(["GET", "HEAD"])(view)
            
            @staticmethod
            def with_ui(ui, cache_timeout):
                def view(request):
                    return JsonResponse({'error': 'Swagger UI not available'}, status=503)
                # Ensure only safe methods are permitted on this diagnostic UI
                # fallback to mitigate CSRF/unsafe-method risks (S3752).
                return require_http_methods(["GET", "HEAD"])(view)
        
        return DummySchemaView()

schema_view = get_schema_view_lazy()

# Constants
METHOD_NOT_ALLOWED_MESSAGE = 'Method not allowed'

@require_safe
def health_check(request):
    """
    Endpoint simple para health check. Solo permite métodos seguros (GET, HEAD).
    
    Esta vista solo acepta métodos HTTP seguros que no modifican datos,
    por lo que no requiere protección CSRF adicional.
    """
    # Explicit check to ensure only safe methods are processed
    if request.method not in ('GET', 'HEAD'):
        return JsonResponse({'error': METHOD_NOT_ALLOWED_MESSAGE}, status=405)
    return JsonResponse({'status': 'ok', 'service': 'cacaoscan-backend'}, status=200)

@require_safe
def api_info(request):
    """
    Endpoint de información del API para diagnóstico. Solo permite métodos seguros (GET, HEAD).
    
    Esta vista solo acepta métodos HTTP seguros que no modifican datos,
    por lo que no requiere protección CSRF adicional.
    """
    # Explicit check to ensure only safe methods are processed
    if request.method not in ('GET', 'HEAD'):
        return JsonResponse({'error': METHOD_NOT_ALLOWED_MESSAGE}, status=405)
    from django.conf import settings
    return JsonResponse({
        'status': 'ok',
        'service': 'cacaoscan-backend',
        'cors_allowed_origins': getattr(settings, 'CORS_ALLOWED_ORIGINS', []),
        'cors_allow_all': getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', False),
        'allowed_hosts': getattr(settings, 'ALLOWED_HOSTS', []),
        'debug': getattr(settings, 'DEBUG', False),
        'request_origin': request.META.get('HTTP_ORIGIN', 'No origin header'),
        'request_host': request.META.get('HTTP_HOST', 'No host header'),
    }, status=200)

@require_safe
def root_view(request):
    """
    Vista informativa para la ruta raíz. Solo permite métodos seguros (GET, HEAD).
    
    Esta vista solo acepta métodos HTTP seguros que no modifican datos,
    por lo que no requiere protección CSRF adicional.
    """
    # Explicit check to ensure only safe methods are processed
    if request.method not in ('GET', 'HEAD'):
        return HttpResponse(METHOD_NOT_ALLOWED_MESSAGE, status=405)
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CacaoScan API</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                max-width: 600px;
                width: 100%;
                padding: 40px;
                text-align: center;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                color: #667eea;
                font-size: 1.2em;
                margin-bottom: 30px;
                font-weight: 500;
            }
            .description {
                color: #666;
                line-height: 1.6;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .endpoints {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
                text-align: left;
            }
            .endpoints h3 {
                color: #333;
                margin-bottom: 15px;
                font-size: 1.1em;
            }
            .endpoint {
                margin: 10px 0;
                padding: 10px;
                background: white;
                border-radius: 6px;
                border-left: 3px solid #667eea;
            }
            .endpoint a {
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
            }
            .endpoint a:hover {
                text-decoration: underline;
            }
            .status {
                display: inline-block;
                background: #10b981;
                color: white;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 0.9em;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌱 CacaoScan API</h1>
            <p class="subtitle">API Backend para Medición de Granos de Cacao</p>
            <p class="description">
                API REST para medición de dimensiones y peso de granos de cacao 
                utilizando Machine Learning y visión por computadora.
            </p>
            <div class="endpoints">
                <h3>📚 Endpoints Disponibles</h3>
                <div class="endpoint">
                    <a href="/api/v1/">API v1</a> - Endpoints principales de la aplicación
                </div>
                <div class="endpoint">
                    <a href="/swagger/">Swagger UI</a> - Documentación interactiva del API
                </div>
                <div class="endpoint">
                    <a href="/redoc/">ReDoc</a> - Documentación alternativa del API
                </div>
                <div class="endpoint">
                    <a href="/admin/">Admin Panel</a> - Panel de administración Django
                </div>
                <div class="endpoint">
                    <a href="/health">Health Check</a> - Estado del servicio
                </div>
            </div>
            <div class="status">✓ Servicio en línea</div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content, content_type='text/html')

# URL prefix constants
API_V1_PREFIX = 'api/v1/'

urlpatterns = [
    path('', root_view, name='root'),
    path('health/', health_check, name='health-check'),
    path('health', health_check, name='health-check-no-slash'),
    path('api-info/', api_info, name='api-info'),
    path('admin/', admin.site.urls),
]

# Cargar URLs de apps de forma segura
# IMPORTANTE: Rutas específicas deben ir ANTES de rutas generales
try:
    urlpatterns += [
        # API de personas (debe ir ANTES de api.urls para evitar conflictos)
        path(f'{API_V1_PREFIX}personas/', include('personas.urls')),
    ]
except Exception as e:
    # Log error instead of silently failing
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Error loading personas.urls: {e}", exc_info=True)
    # Re-raise to see the error in development
    if settings.DEBUG:
        raise

try:
    urlpatterns += [
        # API principal de CacaoScan (debe ir DESPUÉS de rutas específicas)
        path(API_V1_PREFIX, include('api.urls')),
    ]
except Exception as e:
    # Log error instead of silently failing
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Error loading api.urls: {e}", exc_info=True)
    # Re-raise to see the error in development
    if settings.DEBUG:
        raise

try:
    urlpatterns += [
        # API de catálogos (incluida en v1 para consistencia)
        path(API_V1_PREFIX, include('catalogos.urls')),
    ]
except Exception:
    pass

try:
    urlpatterns += [
        # API de imágenes (debe ir después de api.urls para evitar conflictos)
        path(API_V1_PREFIX, include('images_app.urls')),
    ]
except Exception:
    pass

try:
    urlpatterns += [
        # API de reportes (debe ir después de api.urls para evitar conflictos)
        path(API_V1_PREFIX, include('reports.urls')),
    ]
except Exception:
    pass

# Swagger URLs - solo si está disponible
try:
    urlpatterns += [
        re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
except Exception:
    pass

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()


