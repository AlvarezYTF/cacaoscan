"""
URLs para la app personas.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('registrar/', views.PersonaRegistroView.as_view(), name='persona-registrar'),
    path('lista/', views.PersonaListaView.as_view(), name='persona-lista'),
    path('detalle/<int:persona_id>/', views.PersonaDetalleView.as_view(), name='persona-detalle'),
    path('tipos-documento/', views.TipoDocumentoListaView.as_view(), name='tipos-documento'),
    path('generos/', views.GeneroListaView.as_view(), name='generos'),
    path('ubicaciones/', views.UbicacionListaView.as_view(), name='ubicaciones'),
]

