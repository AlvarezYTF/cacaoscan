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
from rest_framework_simplejwt.tokens import RefreshToken
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
from api.tests.test_constants import (
    TEST_USER_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
)


class CacaoImageAPITestCase(APITestCase):
    """Tests de integración para la API de imágenes de cacao."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = APIClient()
        
        # Crear usuario de prueba
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD  # NOSONAR(S2068)
        )
        
        # Crear token de autenticación
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
        
        # Crear finca y lote de prueba
        self.finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Test Location',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=10.5,
            agricultor=self.user
        )
        
        self.lote = Lote.objects.create(
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=2.5,
            fecha_plantacion=timezone.now().date(),
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
        self.assertTrue(CacaoImage.objects.filter(user=self.user).exists())
        
        # Verificar que se creó el log de actividad
        self.assertTrue(ActivityLog.objects.filter(
            user=self.user,
            action='upload_image'
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
                user=self.user,
                lote=self.lote,
                image=self.image_file,
                notas=f'Imagen {i+1}'
            )
        
        url = reverse('cacao-image-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_get_image_detail(self):
        """Test de obtención de detalle de imagen."""
        image = CacaoImage.objects.create(
            user=self.user,
            lote=self.lote,
            image=self.image_file,
            notas='Imagen de prueba'
        )
        
        url = reverse('image-detail', kwargs={'image_id': image.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('notas', ''), 'Imagen de prueba')
    
    def test_delete_image(self):
        """Test de eliminación de imagen."""
        image = CacaoImage.objects.create(
            user=self.user,
            lote=self.lote,
            image=self.image_file,
            notas='Imagen de prueba'
        )
        
        url = reverse('image-delete', kwargs={'image_id': image.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CacaoImage.objects.filter(id=image.id).exists())
        
        # Verificar que se creó el log de actividad
        self.assertTrue(ActivityLog.objects.filter(
            user=self.user,
            action='delete_image'
        ).exists())


class FincaAPITestCase(APITestCase):
    """Tests de integración para la API de fincas."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = APIClient()
        
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD  # NOSONAR(S2068)
        )
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    
    def test_create_finca_success(self):
        """Test de creación exitosa de finca."""
        url = reverse('fincas-list-create')
        data = {
            'nombre': 'Finca Nueva',
            'ubicacion': 'Nueva Ubicación',
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento',
            'hectareas': 15.5,
            'descripcion': 'Finca de prueba'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Finca.objects.filter(nombre='Finca Nueva').exists())
        
        # Verificar que se creó el log de actividad
        self.assertTrue(ActivityLog.objects.filter(
            user=self.user,
            action='create_finca'
        ).exists())
    
    def test_get_finca_list(self):
        """Test de obtención de lista de fincas."""
        # Crear algunas fincas de prueba
        for i in range(3):
            Finca.objects.create(
                nombre=f'Finca {i+1}',
                ubicacion=f'Ubicación {i+1}',
                municipio='Test Municipio',
                departamento='Test Departamento',
                hectareas=10.0 + i,
                agricultor=self.user
            )
        
        url = reverse('fincas-list-create')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
    
    def test_update_finca(self):
        """Test de actualización de finca."""
        finca = Finca.objects.create(
            nombre='Finca Original',
            ubicacion='Ubicación Original',
            municipio='Test Municipio',
            departamento='Test Departamento',
            hectareas=10.0,
            agricultor=self.user
        )
        
        url = reverse('finca-update', kwargs={'finca_id': finca.id})
        data = {
            'nombre': 'Finca Actualizada',
            'ubicacion': 'Ubicación Actualizada',
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento',
            'hectareas': 12.0
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        finca.refresh_from_db()
        self.assertEqual(finca.nombre, 'Finca Actualizada')
        
        # Verificar que se creó el log de actividad
        self.assertTrue(ActivityLog.objects.filter(
            user=self.user,
            action='update_finca'
        ).exists())


class NotificationAPITestCase(APITestCase):
    """Tests de integración para la API de notificaciones."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = APIClient()
        
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD  # NOSONAR(S2068)
        )
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    
    def test_create_notification(self):
        """Test de creación de notificación."""
        url = reverse('notifications-list')
        data = {
            'titulo': 'Notificación de prueba',
            'mensaje': 'Este es un mensaje de prueba',
            'tipo': 'info',
            'datos_extra': {'test': 'value'}
        }
        
        response = self.client.post(url, data, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Notification.objects.filter(
            user=self.user,
            titulo='Notificación de prueba'
        ).exists())
    
    def test_mark_notification_as_read(self):
        """Test de marcar notificación como leída."""
        notification = Notification.objects.create(
            user=self.user,
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
            user=self.user,
            titulo='Notificación 1',
            mensaje='Mensaje 1',
            tipo='info',
            leida=True
        )
        
        Notification.objects.create(
            user=self.user,
            titulo='Notificación 2',
            mensaje='Mensaje 2',
            tipo='warning',
            leida=False
        )
        
        url = reverse('notifications-list')
        response = self.client.get(url, {'leida': 'false'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['titulo'], 'Notificación 2')


class ReportAPITestCase(APITestCase):
    """Tests de integración para la API de reportes."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = APIClient()
        
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD  # NOSONAR(S2068)
        )
        
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token.access_token}")
    
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
        
        response = self.client.post(url, data, format="json")
        
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
    
    def test_complete_workflow(self):
        """Test de flujo de trabajo completo E2E."""
        # 1. Registro de usuario
        register_data = {
            'username': 'workflow_user',
            'email': 'workflow@test.com',
            'password': TEST_USER_PASSWORD,
            'password_confirm': TEST_USER_PASSWORD,
            'first_name': 'Workflow',
            'last_name': 'User'
        }
        
        register_response = self.client.post('/api/v1/auth/register/', register_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(register_response.data['success'])
        self.assertIn('access', register_response.data)
        self.assertIn('refresh', register_response.data)
        self.assertIn('user', register_response.data)
        
        # Guardar tokens para autenticación
        access_token = register_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Verificar que el usuario fue creado
        user_id = register_response.data['user']['id']
        self.assertTrue(User.objects.filter(id=user_id).exists())
        user = User.objects.get(id=user_id)
        
        # Hacer al usuario admin para poder crear notificaciones
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        # 2. Login (opcional, pero verificar que funciona)
        self.client.credentials()  # Limpiar credenciales
        login_data = {
            'username': 'workflow_user',
            'password': TEST_USER_PASSWORD
        }
        
        login_response = self.client.post('/api/v1/auth/login/', login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertTrue(login_response.data['success'])
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)
        
        # Usar token de login
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # 3. Crear finca
        finca_data = {
            'nombre': 'Finca Completa',
            'ubicacion': 'Ubicación Completa',
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento',
            'hectareas': 20.0
        }
        
        finca_response = self.client.post('/api/v1/fincas/', finca_data, format='json')
        self.assertEqual(finca_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(finca_response.data['success'])
        self.assertIn('finca', finca_response.data)
        finca_id = finca_response.data['finca']['id']
        
        # 4. Crear lote
        lote_data = {
            'identificador': 'LOTE-COMPLETO',
            'variedad': 'Criollo',
            'area': 5.0,
            'finca': finca_id  # El endpoint espera 'finca', no 'finca_id'
        }
        
        lote_response = self.client.post('/api/v1/lotes/', lote_data, format='json')
        self.assertEqual(lote_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(lote_response.data['success'])
        self.assertIn('lote', lote_response.data)
        lote_id = lote_response.data['lote']['id']
        
        # 5. Subir imagen usando el servicio directamente
        # (El endpoint /api/images/ solo tiene GET, no POST)
        image_file = self.create_test_image()
        from images_app.services.image.management_service import ImageManagementService
        
        image_service = ImageManagementService()
        upload_result = image_service.upload_image(
            image_file=image_file,
            user=user,
            metadata={'lote_id': lote_id, 'notas': 'Imagen del flujo completo'}
        )
        
        self.assertTrue(upload_result.success)
        self.assertIn('id', upload_result.data)
        image_id = upload_result.data['id']
        
        # Verificar que la imagen fue creada
        self.assertTrue(CacaoImage.objects.filter(id=image_id).exists())
        
        # Verificar que se puede obtener el detalle de la imagen
        image_detail_response = self.client.get(f'/api/v1/images/{image_id}/')
        self.assertEqual(image_detail_response.status_code, status.HTTP_200_OK)
        
        # 6. Análisis de imagen usando el servicio
        from api.services.analysis_service import AnalysisService
        analysis_service = AnalysisService()
        analysis_result = analysis_service.analyze_image(image_id, user)
        
        self.assertTrue(analysis_result.success)
        self.assertIn('prediction', analysis_result.data)
        prediction_id = analysis_result.data['prediction']['id']
        
        # Verificar que se creó la predicción
        self.assertTrue(CacaoPrediction.objects.filter(id=prediction_id).exists())
        
        # 7. Crear notificación (usar endpoint admin ya que el usuario es admin)
        notification_data = {
            'user': user.id,
            'titulo': 'Flujo completado',
            'mensaje': 'El flujo de trabajo se completó exitosamente',
            'tipo': 'success'
        }
        
        notification_response = self.client.post('/api/admin/notifications/create/', notification_data, format="json")
        self.assertEqual(notification_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(notification_response.data['success'])
        self.assertIn('notification', notification_response.data)
        
        # 8. Crear reporte usando el endpoint
        report_data = {
            'tipo_reporte': 'calidad',
            'formato': 'json',
            'titulo': 'Reporte del flujo completo',
            'descripcion': 'Reporte generado del flujo E2E',
            'parametros': {'finca_id': finca_id}
        }
        
        report_response = self.client.post('/api/v1/reportes/', report_data, format='json')
        self.assertEqual(report_response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(report_response.data['success'])
        self.assertIn('reporte', report_response.data)
        reporte_id = report_response.data['reporte']['id']
        
        # Verificar que el reporte fue creado
        self.assertTrue(ReporteGenerado.objects.filter(id=reporte_id).exists())
        
        # Verificar que todos los objetos fueron creados
        self.assertTrue(Finca.objects.filter(id=finca_id).exists())
        self.assertTrue(Lote.objects.filter(id=lote_id).exists())
        self.assertTrue(CacaoImage.objects.filter(id=image_id).exists())
        self.assertTrue(CacaoPrediction.objects.filter(id=prediction_id).exists())
        self.assertTrue(Notification.objects.filter(user=user).exists())
        self.assertTrue(ReporteGenerado.objects.filter(usuario=user).exists())
        
        # Verificar logs de actividad
        self.assertTrue(ActivityLog.objects.filter(user=user).exists())
    
    def create_test_image(self):
        """Crea un archivo de imagen de prueba."""
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


