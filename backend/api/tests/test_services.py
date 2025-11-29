"""
Tests unitarios para servicios de CacaoScan.
"""
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import json

from api.services import (
    AuthenticationService,
    AnalysisService,
    ImageManagementService,
    FincaService,
    LoteService,
    ReportService
)
# ImageManagementService ahora está en api.services.image.management_service
from api.services.base import (
    ServiceResult,
    ServiceError,
    ValidationServiceError,
    PermissionServiceError,
    NotFoundServiceError
)
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
    TEST_OTHER_USER_PASSWORD,
    TEST_WEAK_PASSWORD,
    TEST_USER_USERNAME,
    TEST_USER_EMAIL,
    TEST_USER_FIRST_NAME,
    TEST_USER_LAST_NAME,
)


class AuthenticationServiceTest(TestCase):
    """Tests para AuthenticationService."""
    
    def setUp(self):
        """Configuración inicial."""
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        user_credential = TEST_USER_PASSWORD
        self.service = AuthenticationService()
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=user_credential,
            first_name=TEST_USER_FIRST_NAME,
            last_name=TEST_USER_LAST_NAME
        )
    
    def test_login_user_success(self):
        """Test de login exitoso."""
        result = self.service.login_user(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        
        self.assertTrue(result.success)
        self.assertIn('access', result.data)
        self.assertIn('refresh', result.data)
        self.assertIn('user', result.data)
    
    def test_login_user_invalid_credentials(self):
        """Test de login con credenciales inválidas."""
        result = self.service.login_user(TEST_USER_EMAIL, 'wrongpassword')
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ValidationServiceError)
        self.assertEqual(result.error.message, 'Credenciales inválidas')
    
    def test_login_user_missing_fields(self):
        """Test de login con campos faltantes."""
        result = self.service.login_user('', TEST_USER_PASSWORD)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ValidationServiceError)
    
    @patch('api.services.auth_service.RefreshToken')
    def test_login_user_token_generation(self, mock_refresh_token):
        """Test de generación de tokens."""
        mock_token = Mock()
        mock_token.access_token = 'access_token'
        mock_refresh_token.for_user.return_value = mock_token
        
        result = self.service.login_user(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        
        self.assertTrue(result.success)
        self.assertEqual(result.data['access'], 'access_token')
        mock_refresh_token.for_user.assert_called_once_with(self.user)
    
    def test_register_user_success(self):
        """Test de registro exitoso."""
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': TEST_USER_PASSWORD  # NOSONAR(S2068)
        }
        
        result = self.service.register_user(user_data)
        
        self.assertTrue(result.success)
        self.assertIn('user', result.data)
        self.assertIn('verification_token', result.data)
        
        # Verificar que el usuario fue creado
        user = User.objects.get(email='new@example.com')
        self.assertEqual(user.username, 'newuser')
    
    def test_register_user_email_exists(self):
        """Test de registro con email existente."""
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        user_data = {
            'username': 'testuser2',
            'email': 'test@example.com',  # Email ya existe
            'first_name': 'Test',
            'last_name': 'User2',
            'password': TEST_USER_PASSWORD  # NOSONAR(S2068)
        }
        
        result = self.service.register_user(user_data)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ValidationServiceError)
    
    def test_register_user_validation_errors(self):
        """Test de errores de validación en registro."""
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        # This is intentionally a weak password for validation testing
        user_data = {
            'username': '',
            'email': 'invalid-email',
            'first_name': '',
            'last_name': '',
            'password': TEST_WEAK_PASSWORD  # NOSONAR(S2068)
        }
        
        result = self.service.register_user(user_data)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ValidationServiceError)
    
    def test_verify_email_success(self):
        """Test de verificación de email exitosa."""
        token = EmailVerificationToken.create_for_user(self.user)
        
        result = self.service.verify_email(str(token.token))
        
        self.assertTrue(result.success)
        
        # Verificar que el token fue marcado como verificado
        token.refresh_from_db()
        self.assertTrue(token.is_verified)
    
    def test_verify_email_invalid_token(self):
        """Test de verificación con token inválido."""
        result = self.service.verify_email('invalid-token')
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ValidationServiceError)
    
    def test_resend_verification_success(self):
        """Test de reenvío de verificación exitoso."""
        result = self.service.resend_verification('test@example.com')
        
        self.assertTrue(result.success)
        self.assertIn('token', result.data)
    
    def test_resend_verification_user_not_found(self):
        """Test de reenvío con usuario no encontrado."""
        result = self.service.resend_verification('nonexistent@example.com')
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, NotFoundServiceError)


class AnalysisServiceTest(TestCase):
    """Tests para AnalysisService."""
    
    def setUp(self):
        """Configuración inicial."""
        self.service = AnalysisService()
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        user_credential = TEST_USER_PASSWORD
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=user_credential
        )
        self.image = CacaoImage.objects.create(
            user=self.user,
            filename='test_image.jpg',
            upload_status='completed'
        )
    
    @patch('api.services.analysis_service.get_predictor')
    def test_analyze_image_success(self, mock_get_predictor):
        """Test de análisis de imagen exitoso."""
        # Mock del predictor
        mock_predictor = Mock()
        mock_predictor.predict.return_value = {
            'quality_score': 85.5,
            'maturity_percentage': 75.0,
            'defects_count': 2,
            'recommendations': ['Cosecha recomendada']
        }
        mock_get_predictor.return_value = mock_predictor
        
        result = self.service.analyze_image(self.image.id, self.user)
        
        self.assertTrue(result.success)
        self.assertIn('prediction', result.data)
        
        # Verificar que se creó la predicción
        prediction = CacaoPrediction.objects.get(image=self.image)
        self.assertEqual(prediction.quality_score, Decimal('85.5'))
        self.assertEqual(prediction.maturity_percentage, Decimal('75.0'))
        self.assertEqual(prediction.defects_count, 2)
    
    def test_analyze_image_not_found(self):
        """Test de análisis con imagen no encontrada."""
        result = self.service.analyze_image(999, self.user)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, NotFoundServiceError)
    
    def test_analyze_image_permission_denied(self):
        """Test de análisis sin permisos."""
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        other_user_credential = TEST_OTHER_USER_PASSWORD
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password=other_user_credential
        )
        
        result = self.service.analyze_image(self.image.id, other_user)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, PermissionServiceError)
    
    @patch('api.services.analysis_service.get_predictor')
    def test_analyze_image_prediction_error(self, mock_get_predictor):
        """Test de análisis con error en predicción."""
        mock_get_predictor.side_effect = Exception('Prediction error')
        
        result = self.service.analyze_image(self.image.id, self.user)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ServiceError)
    
    def test_get_analysis_history(self):
        """Test de obtención de historial de análisis."""
        # Crear predicciones
        _ = CacaoPrediction.objects.create(
            image=self.image,
            user=self.user,
            quality_score=Decimal('85.5'),
            analysis_status='completed'
        )
        
        result = self.service.get_analysis_history(self.user)
        
        self.assertTrue(result.success)
        self.assertIn('predictions', result.data)
        self.assertEqual(len(result.data['predictions']), 1)
    
    def test_get_analysis_statistics(self):
        """Test de obtención de estadísticas de análisis."""
        # Crear predicciones
        CacaoPrediction.objects.create(
            image=self.image,
            user=self.user,
            quality_score=Decimal('85.5'),
            maturity_percentage=Decimal('75.0'),
            analysis_status='completed'
        )
        
        result = self.service.get_analysis_statistics(self.user)
        
        self.assertTrue(result.success)
        self.assertIn('total_analyses', result.data)
        self.assertIn('average_quality', result.data)
        self.assertIn('average_maturity', result.data)


class ImageManagementServiceTest(TestCase):
    """Tests para ImageManagementService."""
    
    def setUp(self):
        """Configuración inicial."""
        self.service = ImageManagementService()
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        user_credential = TEST_USER_PASSWORD
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=user_credential
        )
    
    @patch('api.services.image_service.default_storage')
    def test_upload_image_success(self, mock_storage):
        """Test de carga de imagen exitosa."""
        mock_file = Mock()
        mock_file.name = 'test_image.jpg'
        mock_file.size = 1024
        mock_storage.save.return_value = '/path/to/test_image.jpg'
        
        image_data = {
            'filename': 'test_image.jpg',
            'file': mock_file,
            'image_width': 800,
            'image_height': 600
        }
        
        result = self.service.upload_image(image_data, self.user)
        
        self.assertTrue(result.success)
        self.assertIn('image', result.data)
        
        # Verificar que se creó la imagen
        image = CacaoImage.objects.get(user=self.user, filename='test_image.jpg')
        self.assertEqual(image.file_size, 1024)
        self.assertEqual(image.image_width, 800)
        self.assertEqual(image.image_height, 600)
    
    def test_upload_image_validation_error(self):
        """Test de carga con error de validación."""
        image_data = {
            'filename': '',
            'file': None
        }
        
        result = self.service.upload_image(image_data, self.user)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ValidationServiceError)
    
    def test_get_user_images(self):
        """Test de obtención de imágenes del usuario."""
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
        
        result = self.service.get_user_images(self.user)
        
        self.assertTrue(result.success)
        self.assertIn('images', result.data)
        self.assertEqual(len(result.data['images']), 2)
    
    def test_delete_image_success(self):
        """Test de eliminación de imagen exitosa."""
        image = CacaoImage.objects.create(
            user=self.user,
            filename='test_image.jpg',
            upload_status='completed'
        )
        
        result = self.service.delete_image(image.id, self.user)
        
        self.assertTrue(result.success)
        
        # Verificar que la imagen fue eliminada
        self.assertFalse(CacaoImage.objects.filter(id=image.id).exists())
    
    def test_delete_image_not_found(self):
        """Test de eliminación con imagen no encontrada."""
        result = self.service.delete_image(999, self.user)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, NotFoundServiceError)
    
    def test_delete_image_permission_denied(self):
        """Test de eliminación sin permisos."""
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        other_user_credential = TEST_OTHER_USER_PASSWORD
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password=other_user_credential
        )
        image = CacaoImage.objects.create(
            user=self.user,
            filename='test_image.jpg',
            upload_status='completed'
        )
        
        result = self.service.delete_image(image.id, other_user)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, PermissionServiceError)


class FincaServiceTest(TestCase):
    """Tests para FincaService."""
    
    def setUp(self):
        """Configuración inicial."""
        self.service = FincaService()
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        user_credential = TEST_USER_PASSWORD
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=user_credential
        )
    
    def test_create_finca_success(self):
        """Test de creación de finca exitosa."""
        finca_data = {
            'nombre': 'Finca Test',
            'ubicacion': 'Test Location',
            'area_total': Decimal('15.5'),
            'descripcion': 'Test farm description',
            'coordenadas_lat': Decimal('0.0'),
            'coordenadas_lng': Decimal('0.0')
        }
        
        result = self.service.create_finca(finca_data, self.user)
        
        self.assertTrue(result.success)
        self.assertIn('finca', result.data)
        
        # Verificar que se creó la finca
        finca = Finca.objects.get(nombre='Finca Test')
        self.assertEqual(finca.propietario, self.user)
        self.assertEqual(finca.area_total, Decimal('15.5'))
    
    def test_create_finca_validation_error(self):
        """Test de creación con error de validación."""
        finca_data = {
            'nombre': '',  # Nombre vacío
            'area_total': Decimal('-5.0')  # Área negativa
        }
        
        result = self.service.create_finca(finca_data, self.user)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ValidationServiceError)
    
    def test_get_user_fincas(self):
        """Test de obtención de fincas del usuario."""
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
        
        result = self.service.get_user_fincas(self.user)
        
        self.assertTrue(result.success)
        self.assertIn('fincas', result.data)
        self.assertEqual(len(result.data['fincas']), 2)
    
    def test_update_finca_success(self):
        """Test de actualización de finca exitosa."""
        finca = Finca.objects.create(
            nombre='Finca Original',
            propietario=self.user,
            area_total=Decimal('10.0')
        )
        
        update_data = {
            'nombre': 'Finca Actualizada',
            'area_total': Decimal('15.0')
        }
        
        result = self.service.update_finca(finca.id, update_data, self.user)
        
        self.assertTrue(result.success)
        
        # Verificar que se actualizó
        finca.refresh_from_db()
        self.assertEqual(finca.nombre, 'Finca Actualizada')
        self.assertEqual(finca.area_total, Decimal('15.0'))
    
    def test_update_finca_not_found(self):
        """Test de actualización con finca no encontrada."""
        update_data = {'nombre': 'Finca Actualizada'}
        
        result = self.service.update_finca(999, update_data, self.user)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, NotFoundServiceError)
    
    def test_delete_finca_success(self):
        """Test de eliminación de finca exitosa."""
        finca = Finca.objects.create(
            nombre='Finca Test',
            propietario=self.user,
            area_total=Decimal('10.0')
        )
        
        result = self.service.delete_finca(finca.id, self.user)
        
        self.assertTrue(result.success)
        
        # Verificar que la finca fue eliminada
        self.assertFalse(Finca.objects.filter(id=finca.id).exists())
    
    def test_get_finca_statistics(self):
        """Test de obtención de estadísticas de fincas."""
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
        
        result = self.service.get_finca_statistics(self.user)
        
        self.assertTrue(result.success)
        self.assertIn('total_fincas', result.data)
        self.assertIn('total_area', result.data)
        self.assertEqual(result.data['total_fincas'], 2)
        self.assertEqual(result.data['total_area'], Decimal('30.0'))


class LoteServiceTest(TestCase):
    """Tests para LoteService."""
    
    def setUp(self):
        """Configuración inicial."""
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        user_credential = TEST_USER_PASSWORD
        self.service = LoteService()
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=user_credential
        )
        self.finca = Finca.objects.create(
            nombre='Finca Test',
            propietario=self.user,
            area_total=Decimal('20.0')
        )
    
    def test_create_lote_success(self):
        """Test de creación de lote exitosa."""
        lote_data = {
            'finca_id': self.finca.id,
            'nombre': 'Lote Test',
            'area': Decimal('5.0'),
            'variedad': 'CCN-51',
            'edad_plantas': 5,
            'descripcion': 'Test lot description'
        }
        
        result = self.service.create_lote(lote_data, self.user)
        
        self.assertTrue(result.success)
        self.assertIn('lote', result.data)
        
        # Verificar que se creó el lote
        lote = Lote.objects.get(nombre='Lote Test')
        self.assertEqual(lote.finca, self.finca)
        self.assertEqual(lote.area, Decimal('5.0'))
    
    def test_create_lote_area_exceeds_finca(self):
        """Test de creación con área que excede la finca."""
        lote_data = {
            'finca_id': self.finca.id,
            'nombre': 'Lote Test',
            'area': Decimal('25.0'),  # Mayor que el área de la finca (20.0)
            'variedad': 'CCN-51'
        }
        
        result = self.service.create_lote(lote_data, self.user)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ValidationServiceError)
    
    def test_get_finca_lotes(self):
        """Test de obtención de lotes de una finca."""
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
        
        result = self.service.get_finca_lotes(self.finca.id, self.user)
        
        self.assertTrue(result.success)
        self.assertIn('lotes', result.data)
        self.assertEqual(len(result.data['lotes']), 2)
    
    def test_update_lote_success(self):
        """Test de actualización de lote exitosa."""
        lote = Lote.objects.create(
            finca=self.finca,
            nombre='Lote Original',
            area=Decimal('5.0')
        )
        
        update_data = {
            'nombre': 'Lote Actualizado',
            'area': Decimal('8.0')
        }
        
        result = self.service.update_lote(lote.id, update_data, self.user)
        
        self.assertTrue(result.success)
        
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
        
        result = self.service.delete_lote(lote.id, self.user)
        
        self.assertTrue(result.success)
        
        # Verificar que el lote fue eliminado
        self.assertFalse(Lote.objects.filter(id=lote.id).exists())


class ReportServiceTest(TestCase):
    """Tests para ReportService."""
    
    def setUp(self):
        """Configuración inicial."""
        self.service = ReportService()
        # Using test constant to avoid hard-coded password (SonarQube S2068)
        user_credential = TEST_USER_PASSWORD
        self.user = User.objects.create_user(
            username=TEST_USER_USERNAME,
            email=TEST_USER_EMAIL,
            password=user_credential
        )
    
    def test_generate_analysis_report_success(self):
        """Test de generación de reporte de análisis exitosa."""
        report_data = {
            'tipo_reporte': 'analisis_periodo',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31',
            'incluir_graficos': True,
            'incluir_recomendaciones': True
        }
        
        result = self.service.generate_analysis_report(self.user, report_data)
        
        self.assertTrue(result.success)
        self.assertIn('reporte', result.data)
        
        # Verificar que se creó el reporte
        reporte = ReporteGenerado.objects.get(usuario=self.user)
        self.assertEqual(reporte.tipo_reporte, 'analisis_periodo')
    
    def test_generate_analysis_report_validation_error(self):
        """Test de generación con error de validación."""
        report_data = {
            'tipo_reporte': '',  # Tipo vacío
            'fecha_inicio': 'invalid-date',
            'fecha_fin': 'invalid-date'
        }
        
        result = self.service.generate_analysis_report(self.user, report_data)
        
        self.assertFalse(result.success)
        self.assertIsInstance(result.error, ValidationServiceError)
    
    def test_get_user_reports(self):
        """Test de obtención de reportes del usuario."""
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
        
        result = self.service.get_user_reports(self.user)
        
        self.assertTrue(result.success)
        self.assertIn('reportes', result.data)
        self.assertEqual(len(result.data['reportes']), 2)
    
    def test_delete_report_success(self):
        """Test de eliminación de reporte exitosa."""
        reporte = ReporteGenerado.objects.create(
            usuario=self.user,
            tipo_reporte='analisis_periodo',
            estado='completado'
        )
        
        result = self.service.delete_report(reporte.id, self.user)
        
        self.assertTrue(result.success)
        
        # Verificar que el reporte fue eliminado
        self.assertFalse(ReporteGenerado.objects.filter(id=reporte.id).exists())
    
    def test_get_report_statistics(self):
        """Test de obtención de estadísticas de reportes."""
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
        
        result = self.service.get_report_statistics(self.user)
        
        self.assertTrue(result.success)
        self.assertIn('total_reportes', result.data)
        self.assertIn('reportes_por_tipo', result.data)
        self.assertEqual(result.data['total_reportes'], 2)


