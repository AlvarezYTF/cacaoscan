"""
URL configuration for cacaoscan project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import JsonResponse

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
                return view
            
            @staticmethod
            def with_ui(ui, cache_timeout):
                def view(request):
                    return JsonResponse({'error': 'Swagger UI not available'}, status=503)
                return view
        
        return DummySchemaView()

schema_view = get_schema_view_lazy()

def health_check(request):
    """Endpoint simple para health check."""
    return JsonResponse({'status': 'ok', 'service': 'cacaoscan-backend'}, status=200)

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('health', health_check, name='health-check-no-slash'),
    path('admin/', admin.site.urls),
]

# Cargar URLs de apps de forma segura
try:
    urlpatterns += [
        # API de personas (incluida en v1 con prefijo personas/)
        path('api/v1/personas/', include('personas.urls')),
    ]
except Exception:
    pass

try:
    urlpatterns += [
        # API de catálogos (incluida en v1 para consistencia)
        path('api/v1/', include('catalogos.urls')),
    ]
except Exception:
    pass

try:
    urlpatterns += [
        # API de imágenes (debe ir antes de api.urls para evitar conflictos)
        path('api/v1/', include('images_app.urls')),
    ]
except Exception:
    pass

try:
    urlpatterns += [
        # API principal de CacaoScan (debe ir después de rutas específicas)
        path('api/v1/', include('api.urls')),
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


