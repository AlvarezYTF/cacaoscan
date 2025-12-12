"""
URLs para la app personas.
"""
from django.urls import path
from . import persona_views
from .views.crud_views import (
    PersonaCreateView,
    PersonaUpdateView,
    PersonaDeleteView
)

urlpatterns = [
    # Existing views
    path('registrar/', persona_views.PersonaRegistroView.as_view(), name='persona-registrar'),
    path('perfil/', persona_views.PersonaPerfilView.as_view(), name='persona-perfil'),
    path('lista/', persona_views.PersonaListaView.as_view(), name='persona-lista'),
    path('detalle/<int:persona_id>/', persona_views.PersonaDetalleView.as_view(), name='persona-detalle'),
    path('admin/<int:user_id>/', persona_views.AdminPersonaByUserView.as_view(), name='persona-admin-by-user'),
    # CRUD views
    path('crear/', PersonaCreateView.as_view(), name='persona-crear'),
    path('actualizar/<int:persona_id>/', PersonaUpdateView.as_view(), name='persona-actualizar'),
    path('eliminar/<int:persona_id>/', PersonaDeleteView.as_view(), name='persona-eliminar'),
    # Nota: Los catálogos están disponibles en /api/temas/ y /api/parametros/
    # Las ubicaciones están disponibles en /api/departamentos/ y /api/municipios/
]



