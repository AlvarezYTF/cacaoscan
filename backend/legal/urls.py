"""
URLs para documentos legales de CacaoScan.
"""
from django.urls import path
from .views import TermsView, PrivacyView

urlpatterns = [
    path("terms/", TermsView.as_view(), name="legal-terms"),
    path("privacy/", PrivacyView.as_view(), name="legal-privacy"),
]
