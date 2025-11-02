"""
URLs para la app de imágenes.
"""
from django.urls import path
from .views import CacaoImageUploadView, CacaoImageListView

urlpatterns = [
    path('images/upload/', CacaoImageUploadView.as_view(), name='upload-images'),
    path('images/', CacaoImageListView.as_view(), name='list-images'),
]

