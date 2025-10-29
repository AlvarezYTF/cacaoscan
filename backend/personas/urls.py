"""
URLs para la app personas.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.PersonaRegistroView.as_view(), name='persona-registrar'),
    path('perfil/', views.PersonaPerfilView.as_view(), name='persona-perfil'),
    path('lista/', views.PersonaListaView.as_view(), name='persona-lista'),
    path('detalle/<int:persona_id>/', views.PersonaDetalleView.as_view(), name='persona-detalle'),
    # Nota: Los catálogos están disponibles en /api/temas/ y /api/parametros/
    # Las ubicaciones están disponibles en /api/departamentos/ y /api/municipios/
]

