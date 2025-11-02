from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TemaViewSet, 
    ParametroViewSet,
    DepartamentoViewSet,
    MunicipioViewSet
)

# Router para los ViewSets
router = DefaultRouter()
router.register(r'temas', TemaViewSet, basename='tema')
router.register(r'parametros', ParametroViewSet, basename='parametro')
router.register(r'departamentos', DepartamentoViewSet, basename='departamento')
router.register(r'municipios', MunicipioViewSet, basename='municipio')

urlpatterns = [
    path('', include(router.urls)),
]


