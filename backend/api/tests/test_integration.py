"""
Tests de integración para las APIs de CacaoScan.
"""
import json
import tempfile
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import datetime, timedelta
import os

from api.models import (
    CacaoImage, CacaoPrediction, TrainingJob, Finca, Lote, 
    Notification, ActivityLog
)
from audit.models import LoginHistory
from reports.models import ReporteGenerado
# Removed: optimizations.py deleted (YAGNI - only used in tests, not in production)
from api.cache_config import API_CACHE_TIMEOUTS


class CacaoImageAPITestCase(APITestCase):
    """Tests de integración para la API de imágenes de cacao."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = APIClient()
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear token de autenticación
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Crear finca y lote de prueba
        self.finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Test Location',
            area_total=10.5,
            propietario=self.user
        )
        
        self.lote = Lote.objects.create(
            identificador='LOTE-001',
            variedad='Criollo',
            area=2.5,
            fecha_siembra=timezone.now().date(),
            finca=self.finca
        )
        
        # Crear archivo de imagen de prueba
        self.image_file = self.create_test_image()
    
    def create_test_image(self):
        """Crea un archivo de imagen de prueba."""
        # Crear una imagen simple de prueba
        from PIL import Image
        import io
        
        img = Image.new('RGB', (100, 100), color='red')
        img_io = io.BytesIO()
        img.save(img_io, format='JPEG')
        img_io.seek(0)
        
        return SimpleUploadedFile(
            'test_image.jpg',
            img_io.getvalue(),
            content_type='image/jpeg'
        )
    
    def test_upload_image_success(self):
        """Test de subida exitosa de imagen."""
        url = reverse('cacao-image-list')
        data = {
            'imagen': self.image_file,
            'lote': self.lote.id,
            'descripcion': 'Imagen de prueba'
        }
        
        response = self.client.post(url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CacaoImage.objects.filter(usuario=self.user).exists())
        
        # Verificar que se creó el log de actividad
        self.assertTrue(ActivityLog.objects.filter(
            usuario=self.user,
            accion='upload_image'
        ).exists())
    
    def test_upload_image_without_authentication(self):
        """Test de subida de imagen sin autenticación."""
        self.client.credentials()  # Remover autenticación
        
        url = reverse('cacao-image-list')
        data = {
            'imagen': self.image_file,
            'lote': self.lote.id
        }
        
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_image_list(self):
        """Test de obtención de lista de imágenes."""
        # Crear algunas imágenes de prueba
        for i in range(3):
            CacaoImage.objects.create(
                usuario=self.user,
                lote=self.lote,
                imagen=self.image_file,
                descripcion=f'Imagen {i+1}'
            )
        
        url = reverse('cacao-image-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_get_image_detail(self):
        """Test de obtención de detalle de imagen."""
        image = CacaoImage.objects.create(
            usuario=self.user,
            lote=self.lote,
            imagen=self.image_file,
            descripcion='Imagen de prueba'
        )
        
        url = reverse('cacao-image-detail', kwargs={'pk': image.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['descripcion'], 'Imagen de prueba')
    
    def test_delete_image(self):
        """Test de eliminación de imagen."""
        image = CacaoImage.objects.create(
            usuario=self.user,
            lote=self.lote,
            imagen=self.image_file,
            descripcion='Imagen de prueba'
        )
        
        url = reverse('cacao-image-detail', kwargs={'pk': image.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CacaoImage.objects.filter(id=image.id).exists())
        
        # Verificar que se creó el log de actividad
        self.assertTrue(ActivityLog.objects.filter(
            usuario=self.user,
            accion='delete_image'
        ).exists())


class FincaAPITestCase(APITestCase):
    """Tests de integración para la API de fincas."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_create_finca_success(self):
        """Test de creación exitosa de finca."""
        url = reverse('finca-list-create')
        data = {
            'nombre': 'Finca Nueva',
            'ubicacion': 'Nueva Ubicación',
            'area_total': 15.5,
            'descripcion': 'Finca de prueba'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Finca.objects.filter(nombre='Finca Nueva').exists())
        
        # Verificar que se creó el log de actividad
        self.assertTrue(ActivityLog.objects.filter(
            usuario=self.user,
            accion='create_finca'
        ).exists())
    
    def test_get_finca_list(self):
        """Test de obtención de lista de fincas."""
        # Crear algunas fincas de prueba
        for i in range(3):
            Finca.objects.create(
                nombre=f'Finca {i+1}',
                ubicacion=f'Ubicación {i+1}',
                area_total=10.0 + i,
                propietario=self.user
            )
        
        url = reverse('finca-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_update_finca(self):
        """Test de actualización de finca."""
        finca = Finca.objects.create(
            nombre='Finca Original',
            ubicacion='Ubicación Original',
            area_total=10.0,
            propietario=self.user
        )
        
        url = reverse('finca-detail', kwargs={'pk': finca.id})
        data = {
            'nombre': 'Finca Actualizada',
            'ubicacion': 'Ubicación Actualizada',
            'area_total': 12.0
        }
        
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        finca.refresh_from_db()
        self.assertEqual(finca.nombre, 'Finca Actualizada')
        
        # Verificar que se creó el log de actividad
        self.assertTrue(ActivityLog.objects.filter(
            usuario=self.user,
            accion='update_finca'
        ).exists())


class NotificationAPITestCase(APITestCase):
    """Tests de integración para la API de notificaciones."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_create_notification(self):
        """Test de creación de notificación."""
        url = reverse('notification-list-create')
        data = {
            'titulo': 'Notificación de prueba',
            'mensaje': 'Este es un mensaje de prueba',
            'tipo': 'info',
            'datos_extra': {'test': 'value'}
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(
            usuario=self.user,
            titulo='Notificación de prueba'
        ).exists())
    
    def test_mark_notification_as_read(self):
        """Test de marcar notificación como leída."""
        notification = Notification.objects.create(
            usuario=self.user,
            titulo='Notificación de prueba',
            mensaje='Mensaje de prueba',
            tipo='info'
        )
        
        url = reverse('notification-mark-read', kwargs={'pk': notification.id})
        response = self.client.patch(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertTrue(notification.leida)
        self.assertIsNotNone(notification.fecha_lectura)
    
    def test_get_unread_notifications(self):
        """Test de obtención de notificaciones no leídas."""
        # Crear notificaciones leídas y no leídas
        Notification.objects.create(
            usuario=self.user,
            titulo='Notificación 1',
            mensaje='Mensaje 1',
            tipo='info',
            leida=True
        )
        
        Notification.objects.create(
            usuario=self.user,
            titulo='Notificación 2',
            mensaje='Mensaje 2',
            tipo='warning',
            leida=False
        )
        
        url = reverse('notification-list-create')
        response = self.client.get(url, {'leida': 'false'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['titulo'], 'Notificación 2')


class ReportAPITestCase(APITestCase):
    """Tests de integración para la API de reportes."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_create_report(self):
        """Test de creación de reporte."""
        url = reverse('reportes-list-create')
        data = {
            'tipo_reporte': 'calidad',
            'formato': 'pdf',
            'titulo': 'Reporte de Calidad',
            'descripcion': 'Reporte de prueba',
            'parametros': {'include_charts': True},
            'filtros_aplicados': {'fecha_desde': '2024-01-01'}
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ReporteGenerado.objects.filter(
            usuario=self.user,
            titulo='Reporte de Calidad'
        ).exists())
    
    def test_get_reports_list(self):
        """Test de obtención de lista de reportes."""
        # Crear algunos reportes de prueba
        for i in range(3):
            ReporteGenerado.objects.create(
                usuario=self.user,
                tipo_reporte='calidad',
                formato='pdf',
                titulo=f'Reporte {i+1}',
                estado='completado'
            )
        
        url = reverse('reportes-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_download_report(self):
        """Test de descarga de reporte."""
        reporte = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='calidad',
            formato='pdf',
            titulo='Reporte de prueba',
            estado='completado',
            archivo=self.create_test_file()
        )
        
        url = reverse('reporte-download', kwargs={'reporte_id': reporte.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
    
    def create_test_file(self):
        """Crea un archivo de prueba."""
        from django.core.files.base import ContentFile
        return ContentFile(b'Test PDF content', name='test.pdf')


# Removed: CacheIntegrationTestCase - tested optimizations.py which was deleted (YAGNI)


# Removed: QueryOptimizationTestCase - tested optimizations.py which was deleted (YAGNI)


# Removed: PerformanceTestCase - tested optimizations.py which was deleted (YAGNI)


class IntegrationWorkflowTestCase(TransactionTestCase):
    """Tests de flujos de trabajo completos."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = APIClient()
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_complete_workflow(self):
        """Test de flujo de trabajo completo."""
        # 1. Crear finca
        finca_data = {
            'nombre': 'Finca Completa',
            'ubicacion': 'Ubicación Completa',
            'area_total': 20.0
        }
        
        finca_response = self.client.post('/api/fincas/', finca_data)
        self.assertEqual(finca_response.status_code, status.HTTP_201_CREATED)
        finca_id = finca_response.data['id']
        
        # 2. Crear lote
        lote_data = {
            'identificador': 'LOTE-COMPLETO',
            'variedad': 'Criollo',
            'area': 5.0,
            'fecha_siembra': timezone.now().date().isoformat(),
            'finca': finca_id
        }
        
        lote_response = self.client.post('/api/lotes/', lote_data)
        self.assertEqual(lote_response.status_code, status.HTTP_201_CREATED)
        lote_id = lote_response.data['id']
        
        # 3. Subir imagen
        image_file = self.create_test_image()
        image_data = {
            'imagen': image_file,
            'lote': lote_id,
            'descripcion': 'Imagen del flujo completo'
        }
        
        image_response = self.client.post('/api/images/', image_data, format='multipart')
        self.assertEqual(image_response.status_code, status.HTTP_201_CREATED)
        image_id = image_response.data['id']
        
        # 4. Crear notificación
        notification_data = {
            'titulo': 'Flujo completado',
            'mensaje': 'El flujo de trabajo se completó exitosamente',
            'tipo': 'success'
        }
        
        notification_response = self.client.post('/api/notifications/', notification_data)
        self.assertEqual(notification_response.status_code, status.HTTP_201_CREATED)
        
        # 5. Crear reporte
        report_data = {
            'tipo_reporte': 'finca',
            'formato': 'pdf',
            'titulo': 'Reporte del flujo completo',
            'parametros': {'finca_id': finca_id}
        }
        
        report_response = self.client.post('/api/reportes/', report_data)
        self.assertEqual(report_response.status_code, status.HTTP_201_CREATED)
        
        # Verificar que todos los objetos fueron creados
        self.assertTrue(Finca.objects.filter(id=finca_id).exists())
        self.assertTrue(Lote.objects.filter(id=lote_id).exists())
        self.assertTrue(CacaoImage.objects.filter(id=image_id).exists())
        self.assertTrue(Notification.objects.filter(usuario=self.user).exists())
        self.assertTrue(ReporteGenerado.objects.filter(usuario=self.user).exists())
        
        # Verificar logs de actividad
        self.assertTrue(ActivityLog.objects.filter(usuario=self.user).exists())
    
    def create_test_image(self):
        """Crea un archivo de imagen de prueba."""
        from django.core.files.base import ContentFile
        return ContentFile(b'fake image content', name='test.jpg')


