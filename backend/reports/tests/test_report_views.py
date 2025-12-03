"""
Tests for Reports App views.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta

from reports.models import ReporteGenerado
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_ADMIN_PASSWORD,
    TEST_OTHER_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_ADMIN_USERNAME,
    TEST_OTHER_USER_USERNAME,
)


class ReporteListCreateViewTest(APITestCase):
    """Tests for ReporteListCreateView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
        
        self.reporte1 = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad',
            formato='excel',
            titulo='Reporte 1',
            estado='completado'
        )
        
        self.reporte2 = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='finca',
            formato='pdf',
            titulo='Reporte 2',
            estado='generando'
        )
        
        self.other_reporte = ReporteGenerado.objects.create(
            usuario=self.admin_user,
            tipo_reporte='calidad',
            formato='excel',
            titulo='Other Report',
            estado='completado'
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_list_reportes_success(self):
        """Test listing reportes successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reportes-list-create')
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_list_reportes_with_tipo_filter(self):
        """Test listing reportes with tipo_reporte filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reportes-list-create')
        
        response = self.client.get(url, {'tipo_reporte': 'calidad'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['tipo_reporte'], 'calidad')
    
    def test_list_reportes_with_formato_filter(self):
        """Test listing reportes with formato filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reportes-list-create')
        
        response = self.client.get(url, {'formato': 'excel'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['formato'], 'excel')
    
    def test_list_reportes_with_estado_filter(self):
        """Test listing reportes with estado filter."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reportes-list-create')
        
        response = self.client.get(url, {'estado': 'completado'}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['estado'], 'completado')
    
    def test_list_reportes_with_pagination(self):
        """Test listing reportes with pagination."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reportes-list-create')
        
        response = self.client.get(url, {'page': 1, 'page_size': 1}, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('page', response.data)
        self.assertIn('total_pages', response.data)
    
    @patch('reports.views.reports.report_crud_views.ReporteGenerado.generar_reporte')
    def test_create_reporte_success(self, mock_generar):
        """Test creating reporte successfully."""
        mock_generar.return_value = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad',
            formato='excel',
            titulo='New Report',
            estado='generando'
        )
        
        headers = self._get_auth_headers(self.user)
        url = reverse('reportes-list-create')
        
        reporte_data = {
            'tipo_reporte': 'calidad',
            'formato': 'excel',
            'titulo': 'New Report',
            'descripcion': 'Test description',
            'parametros': {},
            'filtros': {}
        }
        
        response = self.client.post(url, reporte_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('reporte', response.data)
    
    def test_create_reporte_missing_required_fields(self):
        """Test creating reporte with missing required fields."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reportes-list-create')
        
        reporte_data = {
            'titulo': 'New Report'
        }
        
        response = self.client.post(url, reporte_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_reporte_invalid_tipo(self):
        """Test creating reporte with invalid tipo_reporte."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reportes-list-create')
        
        reporte_data = {
            'tipo_reporte': 'invalid_type',
            'formato': 'excel',
            'titulo': 'New Report'
        }
        
        response = self.client.post(url, reporte_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_create_reporte_invalid_formato(self):
        """Test creating reporte with invalid formato."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reportes-list-create')
        
        reporte_data = {
            'tipo_reporte': 'calidad',
            'formato': 'invalid_format',
            'titulo': 'New Report'
        }
        
        response = self.client.post(url, reporte_data, format='json', **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_list_reportes_unauthenticated(self):
        """Test listing reportes without authentication."""
        url = reverse('reportes-list-create')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_reporte_unauthenticated(self):
        """Test creating reporte without authentication."""
        url = reverse('reportes-list-create')
        
        reporte_data = {
            'tipo_reporte': 'calidad',
            'formato': 'excel',
            'titulo': 'New Report'
        }
        
        response = self.client.post(url, reporte_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReporteDetailViewTest(APITestCase):
    """Tests for ReporteDetailView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email='other@example.com',
            password=TEST_OTHER_USER_PASSWORD
        )
        
        self.reporte = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad',
            formato='excel',
            titulo='Test Report',
            estado='completado',
            parametros={'key': 'value'},
            filtros_aplicados={'filter': 'value'}
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_reporte_detail_success(self):
        """Test getting reporte detail successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reporte-detail', kwargs={'reporte_id': self.reporte.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.reporte.id)
        self.assertEqual(response.data['titulo'], 'Test Report')
        self.assertIn('parametros', response.data)
        self.assertIn('filtros_aplicados', response.data)
    
    def test_get_reporte_detail_not_found(self):
        """Test getting non-existent reporte."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reporte-detail', kwargs={'reporte_id': 99999})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_get_reporte_detail_permission_denied(self):
        """Test getting reporte detail without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('reporte-detail', kwargs={'reporte_id': self.reporte.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_get_reporte_detail_unauthenticated(self):
        """Test getting reporte detail without authentication."""
        url = reverse('reporte-detail', kwargs={'reporte_id': self.reporte.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReporteDeleteViewTest(APITestCase):
    """Tests for ReporteDeleteView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email='other@example.com',
            password=TEST_OTHER_USER_PASSWORD
        )
        
        self.reporte = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad',
            formato='excel',
            titulo='Test Report',
            estado='completado'
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_delete_reporte_success(self):
        """Test deleting reporte successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reporte-delete', kwargs={'reporte_id': self.reporte.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ReporteGenerado.objects.filter(id=self.reporte.id).exists())
    
    @patch('reports.models.ReporteGenerado.archivo')
    def test_delete_reporte_with_file(self, mock_archivo):
        """Test deleting reporte with associated file."""
        mock_archivo.delete = Mock()
        
        headers = self._get_auth_headers(self.user)
        url = reverse('reporte-delete', kwargs={'reporte_id': self.reporte.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_archivo.delete.assert_called_once()
    
    def test_delete_reporte_permission_denied(self):
        """Test deleting reporte without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('reporte-delete', kwargs={'reporte_id': self.reporte.id})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(ReporteGenerado.objects.filter(id=self.reporte.id).exists())
    
    def test_delete_reporte_not_found(self):
        """Test deleting non-existent reporte."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reporte-delete', kwargs={'reporte_id': 99999})
        
        response = self.client.delete(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_delete_reporte_unauthenticated(self):
        """Test deleting reporte without authentication."""
        url = reverse('reporte-delete', kwargs={'reporte_id': self.reporte.id})
        
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReporteDownloadViewTest(APITestCase):
    """Tests for ReporteDownloadView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.other_user = User.objects.create_user(
            username=TEST_OTHER_USER_USERNAME,
            email='other@example.com',
            password=TEST_OTHER_USER_PASSWORD
        )
        
        test_file = ContentFile(b'fake excel content', name='test_report.xlsx')
        self.reporte = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad',
            formato='excel',
            titulo='Test Report',
            estado='completado',
            archivo=test_file
        )
        
        self.reporte_generando = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad',
            formato='excel',
            titulo='Generating Report',
            estado='generando'
        )
        
        self.reporte_expirado = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad',
            formato='excel',
            titulo='Expired Report',
            estado='completado',
            fecha_expiracion=timezone.now() - timedelta(days=1)
        )
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_download_reporte_success(self):
        """Test downloading reporte successfully."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reporte-download', kwargs={'reporte_id': self.reporte.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_download_reporte_not_completed(self):
        """Test downloading reporte that is not completed."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reporte-download', kwargs={'reporte_id': self.reporte_generando.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_download_reporte_expired(self):
        """Test downloading expired reporte."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reporte-download', kwargs={'reporte_id': self.reporte_expirado.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        self.assertIn('error', response.data)
    
    def test_download_reporte_no_file(self):
        """Test downloading reporte without file."""
        reporte_no_file = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad',
            formato='excel',
            titulo='No File Report',
            estado='completado'
        )
        
        headers = self._get_auth_headers(self.user)
        url = reverse('reporte-download', kwargs={'reporte_id': reporte_no_file.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_download_reporte_permission_denied(self):
        """Test downloading reporte without permission."""
        headers = self._get_auth_headers(self.other_user)
        url = reverse('reporte-download', kwargs={'reporte_id': self.reporte.id})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_download_reporte_not_found(self):
        """Test downloading non-existent reporte."""
        headers = self._get_auth_headers(self.user)
        url = reverse('reporte-download', kwargs={'reporte_id': 99999})
        
        response = self.client.get(url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
    
    def test_download_reporte_unauthenticated(self):
        """Test downloading reporte without authentication."""
        url = reverse('reporte-download', kwargs={'reporte_id': self.reporte.id})
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReporteStatsViewTest(APITestCase):
    """Tests for ReporteStatsView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        
        self.reporte1 = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad',
            formato='excel',
            titulo='Reporte 1',
            estado='completado'
        )
        
        self.reporte2 = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='finca',
            formato='pdf',
            titulo='Reporte 2',
            estado='generando'
        )
        
        self.reporte3 = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad',
            formato='excel',
            titulo='Reporte 3',
            estado='fallido'
        )
        
        self.url = reverse('reportes-stats')
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    def test_get_reporte_stats_success(self):
        """Test getting reporte stats successfully."""
        headers = self._get_auth_headers(self.user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_reportes', response.data)
        self.assertIn('reportes_completados', response.data)
        self.assertIn('reportes_generando', response.data)
        self.assertIn('reportes_fallidos', response.data)
        self.assertIn('reportes_por_tipo', response.data)
        self.assertIn('reportes_por_formato', response.data)
        self.assertIn('reportes_recientes', response.data)
    
    def test_get_reporte_stats_values(self):
        """Test that reporte stats values are correct."""
        headers = self._get_auth_headers(self.user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_reportes'], 3)
        self.assertEqual(response.data['reportes_completados'], 1)
        self.assertEqual(response.data['reportes_generando'], 1)
        self.assertEqual(response.data['reportes_fallidos'], 1)
    
    def test_get_reporte_stats_unauthenticated(self):
        """Test getting reporte stats without authentication."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReporteAgricultoresViewTest(APITestCase):
    """Tests for ReporteAgricultoresView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
        
        self.url = reverse('reporte-agricultores')
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    @patch('reports.views.reports.report_download_views.Finca')
    def test_get_agricultores_report_success(self, mock_finca_model):
        """Test getting agricultores report successfully."""
        from fincas_app.models import Finca
        from django.contrib.auth.models import User
        
        finca = Finca.objects.create(
            nombre='Test Finca',
            ubicacion='Test Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=5.0,
            agricultor=self.user,
            activa=True
        )
        
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_get_agricultores_report_permission_denied(self):
        """Test non-admin cannot get agricultores report."""
        headers = self._get_auth_headers(self.user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_agricultores_report_unauthenticated(self):
        """Test getting agricultores report without authentication."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReporteUsuariosViewTest(APITestCase):
    """Tests for ReporteUsuariosView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
        
        self.url = reverse('reporte-usuarios')
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    @patch('reports.views.reports.report_download_views.ExcelUsuariosGenerator')
    def test_get_usuarios_report_success(self, mock_generator_class):
        """Test getting usuarios report successfully."""
        mock_generator = Mock()
        mock_generator.generate_users_report.return_value = b'fake excel content'
        mock_generator_class.return_value = mock_generator
        
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment', response['Content-Disposition'])
        mock_generator.generate_users_report.assert_called_once()
    
    @patch('reports.views.reports.report_download_views.ExcelUsuariosGenerator')
    def test_get_usuarios_report_empty_content(self, mock_generator_class):
        """Test getting usuarios report with empty content."""
        mock_generator = Mock()
        mock_generator.generate_users_report.return_value = b''
        mock_generator_class.return_value = mock_generator
        
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)
    
    def test_get_usuarios_report_permission_denied(self):
        """Test non-admin cannot get usuarios report."""
        headers = self._get_auth_headers(self.user)
        
        response = self.client.get(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_usuarios_report_unauthenticated(self):
        """Test getting usuarios report without authentication."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ReporteCleanupViewTest(APITestCase):
    """Tests for ReporteCleanupView."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email='test@example.com',
            password=TEST_USER_PASSWORD
        )
        self.admin_user = User.objects.create_superuser(
            username=TEST_ADMIN_USERNAME,
            email='admin@example.com',
            password=TEST_ADMIN_PASSWORD
        )
        
        self.url = reverse('reportes-cleanup')
    
    def _get_auth_headers(self, user):
        """Get authentication headers for user."""
        refresh = RefreshToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {refresh.access_token}'}
    
    @patch('reports.models.ReporteGenerado.limpiar_expirados')
    def test_cleanup_reportes_success(self, mock_limpiar):
        """Test cleaning up expired reportes successfully."""
        mock_limpiar.return_value = 5
        
        headers = self._get_auth_headers(self.admin_user)
        
        response = self.client.post(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('cleaned_count', response.data)
        self.assertEqual(response.data['cleaned_count'], 5)
        mock_limpiar.assert_called_once()
    
    def test_cleanup_reportes_permission_denied(self):
        """Test non-admin cannot cleanup reportes."""
        headers = self._get_auth_headers(self.user)
        
        response = self.client.post(self.url, **headers)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
    
    def test_cleanup_reportes_unauthenticated(self):
        """Test cleaning up reportes without authentication."""
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

