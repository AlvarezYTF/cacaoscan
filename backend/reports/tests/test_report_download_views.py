"""
Tests for report download views.
"""
import pytest
from unittest.mock import Mock, patch
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from reports.views.reports import ReporteDownloadView
from reports.models import ReporteGenerado


@pytest.mark.django_db
class TestReporteDownloadView:
    """Tests for ReporteDownloadView."""
    
    @pytest.fixture
    def api_client(self):
        """Create API client."""
        return APIClient()
    
    @pytest.fixture
    def user(self, db):
        """Create test user with unique username and email."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def reporte(self, user):
        """Create test report."""
        return ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='analisis',
            estado='completado',
            archivo='reports/test_report.xlsx'
        )
    
    def test_download_report_success(self, api_client, user, reporte):
        """Test downloading report successfully."""
        from rest_framework.test import APIRequestFactory
        from rest_framework.test import force_authenticate
        
        api_factory = APIRequestFactory()
        view = ReporteDownloadView()
        
        # Create a real file for the report
        from django.core.files.uploadedfile import SimpleUploadedFile
        test_file = SimpleUploadedFile('test_report.xlsx', b'fake file content')
        reporte.archivo = test_file
        reporte.nombre_archivo = 'test_report.xlsx'
        reporte.formato = 'excel'
        reporte.titulo = 'Test Report'
        reporte.save()
        
        request = api_factory.get(f'/api/reports/{reporte.id}/download/')
        force_authenticate(request, user=user)
        request.user = user
        
        response = view.get(request, reporte_id=reporte.id)
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_download_report_not_found(self, api_client, user):
        """Test downloading non-existent report."""
        api_client.force_authenticate(user=user)
        
        response = api_client.get('/api/reports/999/download/')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_download_report_not_completed(self, api_client, user):
        """Test downloading report that's not completed."""
        from rest_framework.test import APIRequestFactory
        from rest_framework.test import force_authenticate
        
        api_factory = APIRequestFactory()
        view = ReporteDownloadView()
        
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='analisis',
            estado='procesando'
        )
        
        request = api_factory.get(f'/api/reports/{reporte.id}/download/')
        force_authenticate(request, user=user)
        request.user = user
        
        response = view.get(request, reporte_id=reporte.id)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_download_report_expired(self, api_client, user):
        """Test downloading expired report."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Create report first
        reporte = ReporteGenerado.objects.create(
            usuario=user,
            tipo_reporte='analisis',
            estado='completado',
            archivo='reports/test_report.xlsx',
            fecha_solicitud=timezone.now() - timedelta(days=31)  # Expired
        )
        # Refresh to get updated values
        reporte.refresh_from_db()
        
        api_client.force_authenticate(user=user)
        
        response = api_client.get(f'/api/reports/{reporte.id}/download/')
        
        # Should return 410 or 404 depending on implementation
        assert response.status_code in [status.HTTP_410_GONE, status.HTTP_404_NOT_FOUND]
    
    def test_download_report_unauthenticated(self, api_client, reporte):
        """Test downloading report without authentication."""
        from rest_framework.test import APIRequestFactory
        from rest_framework.permissions import IsAuthenticated
        from django.contrib.auth.models import AnonymousUser
        api_factory = APIRequestFactory()
        view = ReporteDownloadView()
        
        request = api_factory.get(f'/api/reports/{reporte.id}/download/')
        request.user = AnonymousUser()
        
        # Use dispatch to properly handle permission checks (DRF's way)
        response = view.dispatch(request, reporte_id=reporte.id)
        
        # Should return 401 for unauthenticated requests
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

