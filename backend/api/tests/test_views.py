"""
Tests unitarios para vistas de CacaoScan.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from api.models import (
    EmailVerificationToken,
    UserProfile,
    CacaoImage,
    CacaoPrediction,
    Finca,
    Lote,
    Notification,
    ActivityLog
)
from audit.models import LoginHistory
from reports.models import ReporteGenerado
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_EXISTING_USER_PASSWORD,
    TEST_OTHER_USER_PASSWORD,
    TEST_INVALID_PASSWORD,
)


class AuthenticationViewsTest(APITestCase):
    """Tests para vistas de autenticación."""
    
    def setUp(self):
        """Configuración inicial."""
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.logout_url = reverse('auth-logout')
        self.profile_url = reverse('auth-profile')
        self.verify_email_url = reverse('auth-verify-email')
        self.resend_verification_url = reverse('auth-resend-verification')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': TEST_USER_PASSWORD,  # NOSONAR - Test credential from constants
            'password_confirm': TEST_USER_PASSWORD  # NOSONAR - Test credential from constants
        }
        
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password=TEST_EXISTING_USER_PASSWORD,  # NOSONAR - Test credential from constants
            first_name='Existing',
            last_name='User'
        )
    
    def test_register_view_success(self):
        """Test de registro exitoso."""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_register_view_validation_errors(self):
        """Test de errores de validación en registro."""
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'existing@example.com'  # Email duplicado
        
        response = self.client.post(self.register_url, invalid_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_login_view_success(self):
        """Test de login exitoso."""
        login_data = {
            'username': 'existing@example.com',
            'password': TEST_EXISTING_USER_PASSWORD  # NOSONAR - Test credential from constants
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_view_invalid_credentials(self):
        """Test de login con credenciales inválidas."""
        login_data = {
            'username': 'existing@example.com',
            'password': TEST_INVALID_PASSWORD  # NOSONAR - Test credential from constants
        }
        
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
    
    def test_profile_view_unauthorized(self):
        """Test de acceso a perfil sin autenticación."""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_profile_view_authorized(self):
        """Test de acceso a perfil con autenticación."""
        refresh = RefreshToken.for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
    
    def test_logout_view_success(self):
        """Test de logout exitoso."""
        refresh = RefreshToken.for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.post(self.logout_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_email_verification_success(self):
        """Test de verificación de email exitosa."""
        token = EmailVerificationToken.create_for_user(self.existing_user)
        
        verify_data = {'token': str(token.token)}
        response = self.client.post(self.verify_email_url, verify_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_email_verification_invalid_token(self):
        """Test de verificación con token inválido."""
        verify_data = {'token': 'invalid-token'}
        response = self.client.post(self.verify_email_url, verify_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_resend_verification_success(self):
        """Test de reenvío de verificación exitoso."""
        resend_data = {'email': 'existing@example.com'}
        response = self.client.post(self.resend_verification_url, resend_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])


class ImageViewsTest(APITestCase):
    """Tests para vistas de imágenes."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=TEST_USER_PASSWORD  # NOSONAR - Test credential from constants
        )
        
        self.images_url = reverse('images-list')
        self.image_detail_url = lambda id: reverse('image-detail', kwargs={'image_id': id})
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    @patch('api.views.default_storage')
    def test_upload_image_success(self, mock_storage):
        """Test de carga de imagen exitosa."""
        mock_storage.save.return_value = '/path/to/test_image.jpg'
        
        with open('test_image.jpg', 'wb') as f:
            f.write(b'fake image data')
        
        with open('test_image.jpg', 'rb') as f:
            response = self.client.post(self.images_url, {
                'file': f,
                'filename': 'test_image.jpg'
            }, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('image', response.data)
    
    def test_get_images_list(self):
        """Test de obtención de lista de imágenes."""
        # Crear imágenes
        _ = CacaoImage.objects.create(
            user=self.user,
            filename='image1.jpg',
            upload_status='completed'
        )
        _ = CacaoImage.objects.create(
            user=self.user,
            filename='image2.jpg',
            upload_status='completed'
        )
        
        response = self.client.get(self.images_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('images', response.data)
        self.assertEqual(len(response.data['images']), 2)
    
    def test_get_image_detail(self):
        """Test de obtención de detalle de imagen."""
        image = CacaoImage.objects.create(
            user=self.user,
            filename='test_image.jpg',
            upload_status='completed'
        )
        
        response = self.client.get(self.image_detail_url(image.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image', response.data)
        self.assertEqual(response.data['image']['filename'], 'test_image.jpg')
    
    def test_get_image_detail_not_found(self):
        """Test de obtención de imagen no encontrada."""
        response = self.client.get(self.image_detail_url(999))
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_image_success(self):
        """Test de eliminación de imagen exitosa."""
        image = CacaoImage.objects.create(
            user=self.user,
            filename='test_image.jpg',
            upload_status='completed'
        )
        
        delete_url = reverse('image-delete', kwargs={'image_id': image.id})
        response = self.client.delete(delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que la imagen fue eliminada
        self.assertFalse(CacaoImage.objects.filter(id=image.id).exists())
    
    def test_delete_image_permission_denied(self):
        """Test de eliminación sin permisos."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password=TEST_OTHER_USER_PASSWORD  # NOSONAR - Test credential from constants
        )
        image = CacaoImage.objects.create(
            user=other_user,
            filename='test_image.jpg',
            upload_status='completed'
        )
        
        delete_url = reverse('image-delete', kwargs={'image_id': image.id})
        response = self.client.delete(delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class FincaViewsTest(APITestCase):
    """Tests para vistas de fincas."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=TEST_USER_PASSWORD  # NOSONAR - Test credential from constants
        )
        
        self.fincas_url = reverse('fincas-list')
        self.finca_detail_url = lambda id: reverse('fincas-detail', kwargs={'pk': id})
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_create_finca_success(self):
        """Test de creación de finca exitosa."""
        finca_data = {
            'nombre': 'Finca Test',
            'ubicacion': 'Test Location',
            'area_total': '15.5',
            'descripcion': 'Test farm description',
            'coordenadas_lat': '0.0',
            'coordenadas_lng': '0.0'
        }
        
        response = self.client.post(self.fincas_url, finca_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('finca', response.data)
        
        # Verificar que se creó la finca
        finca = Finca.objects.get(nombre='Finca Test')
        self.assertEqual(finca.propietario, self.user)
    
    def test_create_finca_validation_error(self):
        """Test de creación con error de validación."""
        finca_data = {
            'nombre': '',  # Nombre vacío
            'area_total': '-5.0'  # Área negativa
        }
        
        response = self.client.post(self.fincas_url, finca_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_get_fincas_list(self):
        """Test de obtención de lista de fincas."""
        # Crear fincas
        _ = Finca.objects.create(
            nombre='Finca 1',
            propietario=self.user,
            area_total=Decimal('10.0')
        )
        _ = Finca.objects.create(
            nombre='Finca 2',
            propietario=self.user,
            area_total=Decimal('20.0')
        )
        
        response = self.client.get(self.fincas_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('fincas', response.data)
        self.assertEqual(len(response.data['fincas']), 2)
    
    def test_get_finca_detail(self):
        """Test de obtención de detalle de finca."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            propietario=self.user,
            area_total=Decimal('10.0')
        )
        
        response = self.client.get(self.finca_detail_url(finca.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('finca', response.data)
        self.assertEqual(response.data['finca']['nombre'], 'Finca Test')
    
    def test_update_finca_success(self):
        """Test de actualización de finca exitosa."""
        finca = Finca.objects.create(
            nombre='Finca Original',
            propietario=self.user,
            area_total=Decimal('10.0')
        )
        
        update_data = {
            'nombre': 'Finca Actualizada',
            'area_total': '15.0'
        }
        
        response = self.client.put(self.finca_detail_url(finca.id), update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que se actualizó
        finca.refresh_from_db()
        self.assertEqual(finca.nombre, 'Finca Actualizada')
        self.assertEqual(finca.area_total, Decimal('15.0'))
    
    def test_delete_finca_success(self):
        """Test de eliminación de finca exitosa."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            propietario=self.user,
            area_total=Decimal('10.0')
        )
        
        response = self.client.delete(self.finca_detail_url(finca.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que la finca fue eliminada
        self.assertFalse(Finca.objects.filter(id=finca.id).exists())
    
    def test_finca_stats(self):
        """Test de estadísticas de fincas."""
        # Crear fincas
        Finca.objects.create(
            nombre='Finca 1',
            propietario=self.user,
            area_total=Decimal('10.0')
        )
        Finca.objects.create(
            nombre='Finca 2',
            propietario=self.user,
            area_total=Decimal('20.0')
        )
        
        stats_url = reverse('fincas-stats')
        response = self.client.get(stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_fincas', response.data)
        self.assertIn('total_area', response.data)
        self.assertEqual(response.data['total_fincas'], 2)


class LoteViewsTest(APITestCase):
    """Tests para vistas de lotes."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=TEST_USER_PASSWORD  # NOSONAR - Test credential from constants
        )
        
        self.finca = Finca.objects.create(
            nombre='Finca Test',
            propietario=self.user,
            area_total=Decimal('20.0')
        )
        
        self.lotes_url = reverse('lotes-list')
        self.lote_detail_url = lambda id: reverse('lotes-detail', kwargs={'pk': id})
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_create_lote_success(self):
        """Test de creación de lote exitosa."""
        lote_data = {
            'finca': self.finca.id,
            'nombre': 'Lote Test',
            'area': '5.0',
            'variedad': 'CCN-51',
            'edad_plantas': 5,
            'descripcion': 'Test lot description'
        }
        
        response = self.client.post(self.lotes_url, lote_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('lote', response.data)
        
        # Verificar que se creó el lote
        lote = Lote.objects.get(nombre='Lote Test')
        self.assertEqual(lote.finca, self.finca)
    
    def test_create_lote_area_exceeds_finca(self):
        """Test de creación con área que excede la finca."""
        lote_data = {
            'finca': self.finca.id,
            'nombre': 'Lote Test',
            'area': '25.0',  # Mayor que el área de la finca (20.0)
            'variedad': 'CCN-51'
        }
        
        response = self.client.post(self.lotes_url, lote_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    def test_get_lotes_list(self):
        """Test de obtención de lista de lotes."""
        # Crear lotes
        _ = Lote.objects.create(
            finca=self.finca,
            nombre='Lote 1',
            area=Decimal('5.0')
        )
        _ = Lote.objects.create(
            finca=self.finca,
            nombre='Lote 2',
            area=Decimal('10.0')
        )
        
        response = self.client.get(self.lotes_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('lotes', response.data)
        self.assertEqual(len(response.data['lotes']), 2)
    
    def test_get_lotes_by_finca(self):
        """Test de obtención de lotes por finca."""
        # Crear lotes
        Lote.objects.create(
            finca=self.finca,
            nombre='Lote 1',
            area=Decimal('5.0')
        )
        Lote.objects.create(
            finca=self.finca,
            nombre='Lote 2',
            area=Decimal('10.0')
        )
        
        lotes_por_finca_url = reverse('lotes-por-finca', kwargs={'finca_id': self.finca.id})
        response = self.client.get(lotes_por_finca_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('lotes', response.data)
        self.assertEqual(len(response.data['lotes']), 2)
    
    def test_get_lote_detail(self):
        """Test de obtención de detalle de lote."""
        lote = Lote.objects.create(
            finca=self.finca,
            nombre='Lote Test',
            area=Decimal('5.0')
        )
        
        response = self.client.get(self.lote_detail_url(lote.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('lote', response.data)
        self.assertEqual(response.data['lote']['nombre'], 'Lote Test')
    
    def test_update_lote_success(self):
        """Test de actualización de lote exitosa."""
        lote = Lote.objects.create(
            finca=self.finca,
            nombre='Lote Original',
            area=Decimal('5.0')
        )
        
        update_data = {
            'nombre': 'Lote Actualizado',
            'area': '8.0'
        }
        
        response = self.client.put(self.lote_detail_url(lote.id), update_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que se actualizó
        lote.refresh_from_db()
        self.assertEqual(lote.nombre, 'Lote Actualizado')
        self.assertEqual(lote.area, Decimal('8.0'))
    
    def test_delete_lote_success(self):
        """Test de eliminación de lote exitosa."""
        lote = Lote.objects.create(
            finca=self.finca,
            nombre='Lote Test',
            area=Decimal('5.0')
        )
        
        response = self.client.delete(self.lote_detail_url(lote.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que el lote fue eliminado
        self.assertFalse(Lote.objects.filter(id=lote.id).exists())


class NotificationViewsTest(APITestCase):
    """Tests para vistas de notificaciones."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=TEST_USER_PASSWORD  # NOSONAR - Test credential from constants
        )
        
        self.notifications_url = reverse('notifications-list')
        self.notification_detail_url = lambda id: reverse('notifications-detail', kwargs={'pk': id})
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_create_notification_success(self):
        """Test de creación de notificación exitosa."""
        notification_data = {
            'title': 'Test Notification',
            'message': 'This is a test notification',
            'notification_type': 'info'
        }
        
        response = self.client.post(self.notifications_url, notification_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('notification', response.data)
        
        # Verificar que se creó la notificación
        notification = Notification.objects.get(title='Test Notification')
        self.assertEqual(notification.user, self.user)
    
    def test_get_notifications_list(self):
        """Test de obtención de lista de notificaciones."""
        # Crear notificaciones
        _ = Notification.objects.create(
            user=self.user,
            title='Notification 1',
            message='Message 1'
        )
        _ = Notification.objects.create(
            user=self.user,
            title='Notification 2',
            message='Message 2'
        )
        
        response = self.client.get(self.notifications_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('notifications', response.data)
        self.assertEqual(len(response.data['notifications']), 2)
    
    def test_mark_notification_read(self):
        """Test de marcar notificación como leída."""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='Test message',
            is_read=False
        )
        
        mark_read_url = reverse('notifications-mark-read', kwargs={'pk': notification.id})
        response = self.client.post(mark_read_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que se marcó como leída
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
    
    def test_mark_all_notifications_read(self):
        """Test de marcar todas las notificaciones como leídas."""
        # Crear notificaciones no leídas
        Notification.objects.create(
            user=self.user,
            title='Notification 1',
            message='Message 1',
            is_read=False
        )
        Notification.objects.create(
            user=self.user,
            title='Notification 2',
            message='Message 2',
            is_read=False
        )
        
        mark_all_read_url = reverse('notifications-mark-all-read')
        response = self.client.post(mark_all_read_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que todas se marcaron como leídas
        unread_count = Notification.objects.filter(user=self.user, is_read=False).count()
        self.assertEqual(unread_count, 0)
    
    def test_get_unread_count(self):
        """Test de obtención de conteo de notificaciones no leídas."""
        # Crear notificaciones
        Notification.objects.create(
            user=self.user,
            title='Notification 1',
            message='Message 1',
            is_read=False
        )
        Notification.objects.create(
            user=self.user,
            title='Notification 2',
            message='Message 2',
            is_read=True
        )
        
        unread_count_url = reverse('notifications-unread-count')
        response = self.client.get(unread_count_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('unread_count', response.data)
        self.assertEqual(response.data['unread_count'], 1)


class ReportViewsTest(APITestCase):
    """Tests para vistas de reportes."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=TEST_USER_PASSWORD  # NOSONAR - Test credential from constants
        )
        
        self.reports_url = reverse('reportes-list')
        self.report_detail_url = lambda id: reverse('reportes-detail', kwargs={'pk': id})
        
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_generate_report_success(self):
        """Test de generación de reporte exitosa."""
        report_data = {
            'tipo_reporte': 'analisis_periodo',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31',
            'incluir_graficos': True,
            'incluir_recomendaciones': True
        }
        
        response = self.client.post(self.reports_url, report_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('reporte', response.data)
        
        # Verificar que se creó el reporte
        reporte = ReporteGenerado.objects.get(usuario=self.user)
        self.assertEqual(reporte.tipo_reporte, 'analisis_periodo')
    
    def test_get_reports_list(self):
        """Test de obtención de lista de reportes."""
        # Crear reportes
        _ = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='analisis_periodo',
            estado='completado'
        )
        _ = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad_finca',
            estado='completado'
        )
        
        response = self.client.get(self.reports_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reportes', response.data)
        self.assertEqual(len(response.data['reportes']), 2)
    
    def test_get_report_detail(self):
        """Test de obtención de detalle de reporte."""
        reporte = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='analisis_periodo',
            estado='completado'
        )
        
        response = self.client.get(self.report_detail_url(reporte.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('reporte', response.data)
        self.assertEqual(response.data['reporte']['tipo_reporte'], 'analisis_periodo')
    
    def test_download_report(self):
        """Test de descarga de reporte."""
        reporte = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='analisis_periodo',
            estado='completado',
            nombre_archivo='test_report.pdf',
            ruta_archivo='/path/to/test_report.pdf'
        )
        
        download_url = reverse('reportes-download', kwargs={'pk': reporte.id})
        response = self.client.get(download_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_report_success(self):
        """Test de eliminación de reporte exitosa."""
        reporte = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='analisis_periodo',
            estado='completado'
        )
        
        response = self.client.delete(self.report_detail_url(reporte.id))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que el reporte fue eliminado
        self.assertFalse(ReporteGenerado.objects.filter(id=reporte.id).exists())
    
    def test_report_stats(self):
        """Test de estadísticas de reportes."""
        # Crear reportes
        ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='analisis_periodo',
            estado='completado'
        )
        ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad_finca',
            estado='completado'
        )
        
        stats_url = reverse('reportes-stats')
        response = self.client.get(stats_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_reportes', response.data)
        self.assertIn('reportes_por_tipo', response.data)
        self.assertEqual(response.data['total_reportes'], 2)


