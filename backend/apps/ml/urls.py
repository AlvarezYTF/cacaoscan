"""
URLs para el módulo ML de CacaoScan.

Proporciona endpoints específicos para predicciones de ML
incluyendo YOLOv8 y recorte inteligente.
"""

from django.urls import path
from .views import IncrementalTrainingView

app_name = 'ml'

urlpatterns = [
    # Endpoint para entrenamiento incremental
    path('train/incremental-weight/', IncrementalTrainingView.as_view(), name='incremental-training'),
]
