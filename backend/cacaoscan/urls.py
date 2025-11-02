"""
URL configuration for cacaoscan project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="CacaoScan API",
        default_version='v1',
        description="API para mediciÃ³n de dimensiones y peso de granos de cacao usando ML",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@cacaoscan.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # API de documentos legales - COMENTADA: el contenido ahora está en el frontend
    # path('api/v1/legal/', include('legal.urls')),
    # API de personas (incluida en v1 con prefijo personas/)
    path('api/v1/personas/', include('personas.urls')),
    # API de catÃ¡logos (incluida en v1 para consistencia)
    path('api/v1/', include('catalogos.urls')),
    # API de imágenes (debe ir antes de api.urls para evitar conflictos)
    path('api/v1/', include('images_app.urls')),
    # API principal de CacaoScan (debe ir después de rutas específicas)
    path('api/v1/', include('api.urls')),
    
    # Swagger URLs
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


