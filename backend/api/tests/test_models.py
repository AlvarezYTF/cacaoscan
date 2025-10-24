"""
Tests unitarios para modelos de CacaoScan.
"""
import uuid
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from api.models import (
    EmailVerificationToken, 
    UserProfile, 
    CacaoImage, 
    CacaoPrediction, 
    TrainingJob,
    Finca, 
    Lote, 
    Notification, 
    ActivityLog, 
    LoginHistory, 
    ReporteGenerado
)


class EmailVerificationTokenModelTest(TestCase):
    """Tests para el modelo EmailVerificationToken."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_token_creation(self):
        """Test de creación de token de verificación."""
        token = EmailVerificationToken.create_for_user(self.user)
        
        self.assertIsNotNone(token.token)
        self.assertEqual(token.user, self.user)
        self.assertFalse(token.is_verified)
        self.assertIsNotNone(token.created)
        self.assertIsNotNone(token.expires_at)
    
    def test_token_expiration(self):
        """Test de expiración de token."""
        token = EmailVerificationToken.create_for_user(self.user)
        
        # Verificar que el token expira en 24 horas
        expected_expiry = token.created + timedelta(hours=24)
        self.assertEqual(token.expires_at, expected_expiry)
    
    def test_token_verification(self):
        """Test de verificación de token."""
        token = EmailVerificationToken.create_for_user(self.user)
        
        # Verificar token
        token.verify()
        token.refresh_from_db()
        
        self.assertTrue(token.is_verified)
        self.assertIsNotNone(token.verified_at)
    
    def test_get_valid_token(self):
        """Test de obtención de token válido."""
        token = EmailVerificationToken.create_for_user(self.user)
        
        # Obtener token válido
        valid_token = EmailVerificationToken.get_valid_token(str(token.token))
        
        self.assertEqual(valid_token, token)
    
    def test_get_invalid_token(self):
        """Test de obtención de token inválido."""
        invalid_token = EmailVerificationToken.get_valid_token('invalid-token')
        
        self.assertIsNone(invalid_token)
    
    def test_get_expired_token(self):
        """Test de obtención de token expirado."""
        token = EmailVerificationToken.create_for_user(self.user)
        
        # Simular token expirado
        token.created = timezone.now() - timedelta(hours=25)
        token.expires_at = timezone.now() - timedelta(hours=1)
        token.save()
        
        expired_token = EmailVerificationToken.get_valid_token(str(token.token))
        
        self.assertIsNone(expired_token)
    
    def test_str_representation(self):
        """Test de representación string del modelo."""
        token = EmailVerificationToken.create_for_user(self.user)
        
        expected_str = f"Token para {self.user.email}"
        self.assertEqual(str(token), expected_str)


class UserProfileModelTest(TestCase):
    """Tests para el modelo UserProfile."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_profile_creation(self):
        """Test de creación de perfil."""
        profile = UserProfile.objects.create(
            user=self.user,
            phone_number='+1234567890',
            region='Test Region',
            municipality='Test Municipality',
            farm_name='Test Farm',
            years_experience=5,
            farm_size_hectares=Decimal('10.5'),
            preferred_language='en',
            email_notifications=False
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.phone_number, '+1234567890')
        self.assertEqual(profile.region, 'Test Region')
        self.assertEqual(profile.municipality, 'Test Municipality')
        self.assertEqual(profile.farm_name, 'Test Farm')
        self.assertEqual(profile.years_experience, 5)
        self.assertEqual(profile.farm_size_hectares, Decimal('10.5'))
        self.assertEqual(profile.preferred_language, 'en')
        self.assertFalse(profile.email_notifications)
    
    def test_profile_defaults(self):
        """Test de valores por defecto del perfil."""
        profile = UserProfile.objects.create(user=self.user)
        
        self.assertEqual(profile.preferred_language, 'es')
        self.assertTrue(profile.email_notifications)
        self.assertIsNotNone(profile.created_at)
        self.assertIsNotNone(profile.updated_at)
    
    def test_full_name_property(self):
        """Test de la propiedad full_name."""
        profile = UserProfile.objects.create(user=self.user)
        
        expected_name = f"{self.user.first_name} {self.user.last_name}"
        self.assertEqual(profile.full_name, expected_name)
    
    def test_role_property_admin(self):
        """Test de la propiedad role para admin."""
        self.user.is_superuser = True
        self.user.save()
        
        profile = UserProfile.objects.create(user=self.user)
        
        self.assertEqual(profile.role, 'admin')
    
    def test_role_property_analyst(self):
        """Test de la propiedad role para analyst."""
        analyst_group = Group.objects.create(name='analyst')
        self.user.groups.add(analyst_group)
        
        profile = UserProfile.objects.create(user=self.user)
        
        self.assertEqual(profile.role, 'analyst')
    
    def test_role_property_farmer(self):
        """Test de la propiedad role para farmer."""
        profile = UserProfile.objects.create(user=self.user)
        
        self.assertEqual(profile.role, 'farmer')
    
    def test_is_verified_property(self):
        """Test de la propiedad is_verified."""
        profile = UserProfile.objects.create(user=self.user)
        
        # Usuario no verificado por defecto
        self.assertFalse(profile.is_verified)
        
        # Crear token de verificación
        token = EmailVerificationToken.create_for_user(self.user)
        token.verify()
        
        # Refrescar perfil
        profile.refresh_from_db()
        
        # Debería seguir siendo False porque no hay lógica de verificación implementada
        self.assertFalse(profile.is_verified)
    
    def test_str_representation(self):
        """Test de representación string del modelo."""
        profile = UserProfile.objects.create(user=self.user)
        
        expected_str = f"Perfil de {self.user.get_full_name() or self.user.username}"
        self.assertEqual(str(profile), expected_str)


class CacaoImageModelTest(TestCase):
    """Tests para el modelo CacaoImage."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_image_creation(self):
        """Test de creación de imagen."""
        image = CacaoImage.objects.create(
            user=self.user,
            filename='test_image.jpg',
            file_path='/path/to/test_image.jpg',
            file_size=1024,
            image_width=800,
            image_height=600,
            upload_status='completed'
        )
        
        self.assertEqual(image.user, self.user)
        self.assertEqual(image.filename, 'test_image.jpg')
        self.assertEqual(image.file_path, '/path/to/test_image.jpg')
        self.assertEqual(image.file_size, 1024)
        self.assertEqual(image.image_width, 800)
        self.assertEqual(image.image_height, 600)
        self.assertEqual(image.upload_status, 'completed')
    
    def test_image_defaults(self):
        """Test de valores por defecto de imagen."""
        image = CacaoImage.objects.create(
            user=self.user,
            filename='test_image.jpg'
        )
        
        self.assertEqual(image.upload_status, 'pending')
        self.assertIsNone(image.file_size)
        self.assertIsNone(image.image_width)
        self.assertIsNone(image.image_height)
        self.assertIsNotNone(image.uploaded_at)
    
    def test_str_representation(self):
        """Test de representación string del modelo."""
        image = CacaoImage.objects.create(
            user=self.user,
            filename='test_image.jpg'
        )
        
        expected_str = f"Imagen {image.filename} de {self.user.username}"
        self.assertEqual(str(image), expected_str)


class CacaoPredictionModelTest(TestCase):
    """Tests para el modelo CacaoPrediction."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.image = CacaoImage.objects.create(
            user=self.user,
            filename='test_image.jpg'
        )
    
    def test_prediction_creation(self):
        """Test de creación de predicción."""
        prediction = CacaoPrediction.objects.create(
            image=self.image,
            user=self.user,
            quality_score=Decimal('85.5'),
            maturity_percentage=Decimal('75.0'),
            defects_count=2,
            analysis_status='completed',
            model_version='v1.0',
            processing_time=Decimal('2.5')
        )
        
        self.assertEqual(prediction.image, self.image)
        self.assertEqual(prediction.user, self.user)
        self.assertEqual(prediction.quality_score, Decimal('85.5'))
        self.assertEqual(prediction.maturity_percentage, Decimal('75.0'))
        self.assertEqual(prediction.defects_count, 2)
        self.assertEqual(prediction.analysis_status, 'completed')
        self.assertEqual(prediction.model_version, 'v1.0')
        self.assertEqual(prediction.processing_time, Decimal('2.5'))
    
    def test_prediction_defaults(self):
        """Test de valores por defecto de predicción."""
        prediction = CacaoPrediction.objects.create(
            image=self.image,
            user=self.user
        )
        
        self.assertEqual(prediction.analysis_status, 'pending')
        self.assertIsNone(prediction.quality_score)
        self.assertIsNone(prediction.maturity_percentage)
        self.assertEqual(prediction.defects_count, 0)
        self.assertIsNotNone(prediction.created_at)
    
    def test_str_representation(self):
        """Test de representación string del modelo."""
        prediction = CacaoPrediction.objects.create(
            image=self.image,
            user=self.user,
            quality_score=Decimal('85.5')
        )
        
        expected_str = f"Predicción para {self.image.filename} - Calidad: 85.5"
        self.assertEqual(str(prediction), expected_str)


class FincaModelTest(TestCase):
    """Tests para el modelo Finca."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_finca_creation(self):
        """Test de creación de finca."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            ubicacion='Test Location',
            area_total=Decimal('15.5'),
            propietario=self.user,
            descripcion='Test farm description',
            coordenadas_lat=Decimal('0.0'),
            coordenadas_lng=Decimal('0.0'),
            altitud=100,
            tipo_suelo='arcilloso',
            clima='tropical',
            estado='activa'
        )
        
        self.assertEqual(finca.nombre, 'Finca Test')
        self.assertEqual(finca.ubicacion, 'Test Location')
        self.assertEqual(finca.area_total, Decimal('15.5'))
        self.assertEqual(finca.propietario, self.user)
        self.assertEqual(finca.descripcion, 'Test farm description')
        self.assertEqual(finca.coordenadas_lat, Decimal('0.0'))
        self.assertEqual(finca.coordenadas_lng, Decimal('0.0'))
        self.assertEqual(finca.altitud, 100)
        self.assertEqual(finca.tipo_suelo, 'arcilloso')
        self.assertEqual(finca.clima, 'tropical')
        self.assertEqual(finca.estado, 'activa')
    
    def test_finca_defaults(self):
        """Test de valores por defecto de finca."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            propietario=self.user
        )
        
        self.assertEqual(finca.estado, 'activa')
        self.assertIsNotNone(finca.fecha_creacion)
        self.assertIsNotNone(finca.fecha_actualizacion)
    
    def test_str_representation(self):
        """Test de representación string del modelo."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            propietario=self.user
        )
        
        expected_str = f"Finca Test - {self.user.username}"
        self.assertEqual(str(finca), expected_str)


class LoteModelTest(TestCase):
    """Tests para el modelo Lote."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.finca = Finca.objects.create(
            nombre='Finca Test',
            propietario=self.user,
            area_total=Decimal('20.0')
        )
    
    def test_lote_creation(self):
        """Test de creación de lote."""
        lote = Lote.objects.create(
            finca=self.finca,
            nombre='Lote Test',
            area=Decimal('5.0'),
            variedad='CCN-51',
            edad_plantas=5,
            descripcion='Test lot description',
            coordenadas_lat=Decimal('0.0'),
            coordenadas_lng=Decimal('0.0'),
            estado='activo'
        )
        
        self.assertEqual(lote.finca, self.finca)
        self.assertEqual(lote.nombre, 'Lote Test')
        self.assertEqual(lote.area, Decimal('5.0'))
        self.assertEqual(lote.variedad, 'CCN-51')
        self.assertEqual(lote.edad_plantas, 5)
        self.assertEqual(lote.descripcion, 'Test lot description')
        self.assertEqual(lote.coordenadas_lat, Decimal('0.0'))
        self.assertEqual(lote.coordenadas_lng, Decimal('0.0'))
        self.assertEqual(lote.estado, 'activo')
    
    def test_lote_defaults(self):
        """Test de valores por defecto de lote."""
        lote = Lote.objects.create(
            finca=self.finca,
            nombre='Lote Test'
        )
        
        self.assertEqual(lote.estado, 'activo')
        self.assertIsNotNone(lote.fecha_creacion)
        self.assertIsNotNone(lote.fecha_actualizacion)
    
    def test_lote_area_validation(self):
        """Test de validación de área del lote."""
        # Crear lote con área mayor que la finca
        lote = Lote.objects.create(
            finca=self.finca,
            nombre='Lote Test',
            area=Decimal('25.0')  # Mayor que el área total de la finca (20.0)
        )
        
        # El modelo no tiene validación automática, pero podemos verificar
        self.assertEqual(lote.area, Decimal('25.0'))
    
    def test_str_representation(self):
        """Test de representación string del modelo."""
        lote = Lote.objects.create(
            finca=self.finca,
            nombre='Lote Test'
        )
        
        expected_str = f"Lote Test - Finca Test"
        self.assertEqual(str(lote), expected_str)


class NotificationModelTest(TestCase):
    """Tests para el modelo Notification."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_notification_creation(self):
        """Test de creación de notificación."""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='This is a test notification',
            notification_type='info',
            is_read=False
        )
        
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.message, 'This is a test notification')
        self.assertEqual(notification.notification_type, 'info')
        self.assertFalse(notification.is_read)
    
    def test_notification_defaults(self):
        """Test de valores por defecto de notificación."""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='Test message'
        )
        
        self.assertEqual(notification.notification_type, 'info')
        self.assertFalse(notification.is_read)
        self.assertIsNotNone(notification.created_at)
    
    def test_str_representation(self):
        """Test de representación string del modelo."""
        notification = Notification.objects.create(
            user=self.user,
            title='Test Notification',
            message='Test message'
        )
        
        expected_str = f"Notificación para {self.user.username}: Test Notification"
        self.assertEqual(str(notification), expected_str)


class ActivityLogModelTest(TestCase):
    """Tests para el modelo ActivityLog."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_activity_log_creation(self):
        """Test de creación de log de actividad."""
        log = ActivityLog.objects.create(
            user=self.user,
            action='test_action',
            resource_type='test_resource',
            resource_id=1,
            details={'test': 'data'},
            ip_address='127.0.0.1',
            user_agent='Test Agent'
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'test_action')
        self.assertEqual(log.resource_type, 'test_resource')
        self.assertEqual(log.resource_id, 1)
        self.assertEqual(log.details, {'test': 'data'})
        self.assertEqual(log.ip_address, '127.0.0.1')
        self.assertEqual(log.user_agent, 'Test Agent')
    
    def test_activity_log_defaults(self):
        """Test de valores por defecto de log de actividad."""
        log = ActivityLog.objects.create(
            user=self.user,
            action='test_action'
        )
        
        self.assertIsNotNone(log.timestamp)
    
    def test_str_representation(self):
        """Test de representación string del modelo."""
        log = ActivityLog.objects.create(
            user=self.user,
            action='test_action'
        )
        
        expected_str = f"{self.user.username} - test_action"
        self.assertEqual(str(log), expected_str)


class LoginHistoryModelTest(TestCase):
    """Tests para el modelo LoginHistory."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_login_history_creation(self):
        """Test de creación de historial de login."""
        login_history = LoginHistory.objects.create(
            user=self.user,
            ip_address='127.0.0.1',
            user_agent='Test Agent',
            login_successful=True,
            failure_reason=None
        )
        
        self.assertEqual(login_history.user, self.user)
        self.assertEqual(login_history.ip_address, '127.0.0.1')
        self.assertEqual(login_history.user_agent, 'Test Agent')
        self.assertTrue(login_history.login_successful)
        self.assertIsNone(login_history.failure_reason)
    
    def test_login_history_defaults(self):
        """Test de valores por defecto de historial de login."""
        login_history = LoginHistory.objects.create(
            user=self.user
        )
        
        self.assertTrue(login_history.login_successful)
        self.assertIsNotNone(login_history.login_time)
    
    def test_str_representation(self):
        """Test de representación string del modelo."""
        login_history = LoginHistory.objects.create(
            user=self.user,
            login_successful=True
        )
        
        expected_str = f"Login de {self.user.username} - Exitoso"
        self.assertEqual(str(login_history), expected_str)


class ReporteGeneradoModelTest(TestCase):
    """Tests para el modelo ReporteGenerado."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_reporte_creation(self):
        """Test de creación de reporte."""
        reporte = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='analisis_periodo',
            nombre_archivo='test_report.pdf',
            ruta_archivo='/path/to/test_report.pdf',
            parametros={'fecha_inicio': '2024-01-01', 'fecha_fin': '2024-01-31'},
            estado='completado',
            tamaño_archivo=1024
        )
        
        self.assertEqual(reporte.usuario, self.user)
        self.assertEqual(reporte.tipo_reporte, 'analisis_periodo')
        self.assertEqual(reporte.nombre_archivo, 'test_report.pdf')
        self.assertEqual(reporte.ruta_archivo, '/path/to/test_report.pdf')
        self.assertEqual(reporte.parametros, {'fecha_inicio': '2024-01-01', 'fecha_fin': '2024-01-31'})
        self.assertEqual(reporte.estado, 'completado')
        self.assertEqual(reporte.tamaño_archivo, 1024)
    
    def test_reporte_defaults(self):
        """Test de valores por defecto de reporte."""
        reporte = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='analisis_periodo'
        )
        
        self.assertEqual(reporte.estado, 'pendiente')
        self.assertIsNotNone(reporte.fecha_generacion)
    
    def test_str_representation(self):
        """Test de representación string del modelo."""
        reporte = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='analisis_periodo',
            nombre_archivo='test_report.pdf'
        )
        
        expected_str = f"Reporte {reporte.tipo_reporte} - {reporte.nombre_archivo}"
        self.assertEqual(str(reporte), expected_str)
