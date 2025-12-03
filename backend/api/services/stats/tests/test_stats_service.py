"""
Tests unitarios para StatsService de CacaoScan.
Pruebas de cobertura completa para el servicio de estadisticas.
"""
import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import timedelta, datetime
from decimal import Decimal
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User, Group
from django.utils import timezone

from api.services.stats.stats_service import StatsService
from auth_app.models import EmailVerificationToken


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def stats_service():
    """Fixture para crear una instancia de StatsService."""
    return StatsService()


@pytest.fixture
def user_factory(db):
    """Factory para crear usuarios de prueba."""
    def _create_user(
        username=None,
        email=None,
        password='testpass123',
        is_active=True,
        is_staff=False,
        is_superuser=False,
        date_joined=None
    ):
        # Generar username único si no se proporciona
        if username is None:
            username = f'testuser_{uuid.uuid4().hex[:8]}'
        
        # Generar email único si no se proporciona
        if email is None:
            email = f'{username}@example.com'
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=is_active,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        if date_joined:
            user.date_joined = date_joined
            user.save()
        return user
    return _create_user


@pytest.fixture
def cacao_image_factory(db, user_factory):
    """Factory para crear imagenes de cacao de prueba."""
    def _create_image(
        user=None,
        processed=False,
        region='',
        finca=None,
        created_at=None
    ):
        from images_app.models import CacaoImage
        
        if user is None:
            user = user_factory()
        
        test_image = SimpleUploadedFile(
            'test_image.jpg',
            b'fake image content',
            content_type='image/jpeg'
        )
        
        image = CacaoImage.objects.create(
            user=user,
            image=test_image,
            file_name='test_image.jpg',
            file_size=1024,
            file_type='image/jpeg',
            processed=processed,
            region=region,
            finca=finca,
            finca_nombre=finca.nombre if finca else ''
        )
        
        if created_at:
            CacaoImage.objects.filter(id=image.id).update(created_at=created_at)
            image.refresh_from_db()
        
        return image
    return _create_image


@pytest.fixture
def cacao_prediction_factory(db, cacao_image_factory):
    """Factory para crear predicciones de cacao de prueba."""
    def _create_prediction(
        image=None,
        user=None,
        alto_mm=25.0,
        ancho_mm=15.0,
        grosor_mm=8.0,
        peso_g=1.5,
        confidence_alto=0.9,
        confidence_ancho=0.85,
        confidence_grosor=0.8,
        confidence_peso=0.75,
        processing_time_ms=100,
        created_at=None
    ):
        from images_app.models import CacaoPrediction
        
        if image is None:
            image = cacao_image_factory(user=user, processed=True)
        
        prediction = CacaoPrediction.objects.create(
            image=image,
            user=user or image.user,
            alto_mm=alto_mm,
            ancho_mm=ancho_mm,
            grosor_mm=grosor_mm,
            peso_g=peso_g,
            confidence_alto=confidence_alto,
            confidence_ancho=confidence_ancho,
            confidence_grosor=confidence_grosor,
            confidence_peso=confidence_peso,
            processing_time_ms=processing_time_ms,
            model_version='v1.0'
        )
        
        if created_at:
            CacaoPrediction.objects.filter(id=prediction.id).update(created_at=created_at)
            prediction.refresh_from_db()
        
        return prediction
    return _create_prediction


@pytest.fixture
def finca_factory(db, user_factory):
    """Factory para crear fincas de prueba."""
    def _create_finca(
        user=None,
        nombre='Finca Test',
        municipio='Test Municipio',
        departamento='Test Departamento',
        hectareas=Decimal('20.0'),
        fecha_registro=None
    ):
        from fincas_app.models import Finca
        
        if user is None:
            user = user_factory()
        
        finca = Finca.objects.create(
            nombre=nombre,
            agricultor=user,
            ubicacion='Test Location',
            municipio=municipio,
            departamento=departamento,
            hectareas=hectareas,
            descripcion='Test farm description'
        )
        
        if fecha_registro:
            Finca.objects.filter(id=finca.id).update(fecha_registro=fecha_registro)
            finca.refresh_from_db()
        
        return finca
    return _create_finca


# ============================================================================
# TESTS PARA get_user_stats()
# ============================================================================

@pytest.mark.django_db
class TestGetUserStats:
    """Tests para el metodo get_user_stats()."""
    
    def test_get_user_stats_empty_database(self, stats_service):
        """Test con base de datos vacia."""
        # Arrange & Act
        result = stats_service.get_user_stats()
        
        # Assert
        assert result['total'] == 0
        assert result['active'] == 0
        assert result['staff'] == 0
        assert result['superusers'] == 0
        assert result['analysts'] == 0
        assert result['farmers'] == 0
        assert result['verified'] == 0
        assert result['this_week'] == 0
        assert result['this_month'] == 0
    
    def test_get_user_stats_active_users(self, stats_service, user_factory):
        """Test con usuarios activos."""
        # Arrange
        user_factory(username='user1', is_active=True)
        user_factory(username='user2', is_active=True)
        user_factory(username='user3', is_active=False)
        
        # Act
        result = stats_service.get_user_stats()
        
        # Assert
        assert result['total'] == 3
        assert result['active'] == 2
    
    def test_get_user_stats_staff_users(self, stats_service, user_factory):
        """Test con usuarios staff."""
        # Arrange
        user_factory(username='staff1', is_staff=True)
        user_factory(username='staff2', is_staff=True)
        user_factory(username='regular', is_staff=False)
        
        # Act
        result = stats_service.get_user_stats()
        
        # Assert
        assert result['staff'] == 2
        assert result['total'] == 3
    
    def test_get_user_stats_superusers(self, stats_service, user_factory):
        """Test con superusuarios."""
        # Arrange
        user_factory(username='super1', is_superuser=True)
        user_factory(username='super2', is_superuser=True)
        user_factory(username='regular', is_superuser=False)
        
        # Act
        result = stats_service.get_user_stats()
        
        # Assert
        assert result['superusers'] == 2
        assert result['total'] == 3
    
    def test_get_user_stats_analyst_group(self, stats_service, user_factory, db):
        """Test con usuarios en grupo analyst."""
        # Arrange
        analyst_group, _ = Group.objects.get_or_create(name='analyst')
        user1 = user_factory(username='analyst1')
        user1.groups.add(analyst_group)
        user2 = user_factory(username='analyst2')
        user2.groups.add(analyst_group)
        user_factory(username='farmer1')
        
        # Act
        result = stats_service.get_user_stats()
        
        # Assert
        assert result['analysts'] == 2
        assert result['total'] == 3
    
    def test_get_user_stats_farmers(self, stats_service, user_factory, db):
        """Test con usuarios farmers (no staff, no superuser, no analyst)."""
        # Arrange
        analyst_group, _ = Group.objects.get_or_create(name='analyst')
        user_factory(username='farmer1')
        user_factory(username='farmer2')
        staff_user = user_factory(username='staff1', is_staff=True)
        super_user = user_factory(username='super1', is_superuser=True)
        analyst_user = user_factory(username='analyst1')
        analyst_user.groups.add(analyst_group)
        
        # Act
        result = stats_service.get_user_stats()
        
        # Assert
        assert result['farmers'] == 2
        assert result['total'] == 5
    
    @pytest.mark.django_db
    def test_get_user_stats_verified_with_token(self, stats_service, user_factory, db):
        """Test con usuarios verificados mediante auth_email_token."""
        # Arrange
        user1 = user_factory(username='verified1', is_active=True)
        EmailVerificationToken.objects.create(user=user1, is_verified=True)
        user2 = user_factory(username='verified2', is_active=True)
        EmailVerificationToken.objects.create(user=user2, is_verified=True)
        user3 = user_factory(username='unverified', is_active=True)
        EmailVerificationToken.objects.create(user=user3, is_verified=False)
        
        # Act
        result = stats_service.get_user_stats()
        
        # Assert
        assert result['verified'] == 2
    
    @pytest.mark.django_db
    def test_get_user_stats_verified_fallback_on_exception(self, stats_service, user_factory, db, monkeypatch):
        """Test fallback a is_active cuando falla auth_email_token."""
        # Arrange
        user1 = user_factory(username='active1', is_active=True)
        user_factory(username='active2', is_active=True)
        user_factory(username='inactive', is_active=False)
        
        # Mock para que falle el acceso a auth_email_token
        original_filter = User.objects.filter
        
        def mock_filter(*args, **kwargs):
            if 'auth_email_token__is_verified' in str(kwargs) or any('auth_email_token__is_verified' in str(arg) for arg in args):
                raise Exception("Mocked exception")
            return original_filter(*args, **kwargs)
        
        monkeypatch.setattr(User.objects, 'filter', mock_filter)
        
        # Act
        result = stats_service.get_user_stats()
        
        # Assert - deberia usar fallback a is_active
        assert result['verified'] == 2
    
    def test_get_user_stats_this_week(self, stats_service, user_factory):
        """Test con usuarios creados esta semana."""
        # Arrange
        today = timezone.now().date()
        this_week_date = today - timedelta(days=3)
        last_week_date = today - timedelta(days=10)
        
        user_factory(username='this_week', date_joined=timezone.make_aware(
            datetime.combine(this_week_date, datetime.min.time())
        ))
        user_factory(username='last_week', date_joined=timezone.make_aware(
            datetime.combine(last_week_date, datetime.min.time())
        ))
        
        # Act
        result = stats_service.get_user_stats()
        
        # Assert
        assert result['this_week'] == 1
    
    def test_get_user_stats_this_month(self, stats_service, user_factory):
        """Test con usuarios creados este mes."""
        # Arrange
        today = timezone.now().date()
        this_month_date = today - timedelta(days=15)
        last_month_date = today - timedelta(days=35)
        
        user_factory(username='this_month', date_joined=timezone.make_aware(
            datetime.combine(this_month_date, datetime.min.time())
        ))
        user_factory(username='last_month', date_joined=timezone.make_aware(
            datetime.combine(last_month_date, datetime.min.time())
        ))
        
        # Act
        result = stats_service.get_user_stats()
        
        # Assert
        assert result['this_month'] == 1


# ============================================================================
# TESTS PARA get_image_stats()
# ============================================================================

@pytest.mark.django_db
class TestGetImageStats:
    """Tests para el metodo get_image_stats()."""
    
    def test_get_image_stats_empty_database(self, stats_service):
        """Test con base de datos vacia."""
        # Arrange & Act
        result = stats_service.get_image_stats()
        
        # Assert
        assert result['total'] == 0
        assert result['processed'] == 0
        assert result['unprocessed'] == 0
        assert result['this_week'] == 0
        assert result['this_month'] == 0
        assert result['processing_rate'] == 0
    
    def test_get_image_stats_total(self, stats_service, cacao_image_factory):
        """Test conteo total de imagenes."""
        # Arrange
        cacao_image_factory()
        cacao_image_factory()
        cacao_image_factory()
        
        # Act
        result = stats_service.get_image_stats()
        
        # Assert
        assert result['total'] == 3
    
    def test_get_image_stats_processed_unprocessed(self, stats_service, cacao_image_factory):
        """Test conteo de imagenes procesadas y no procesadas."""
        # Arrange
        cacao_image_factory(processed=True)
        cacao_image_factory(processed=True)
        cacao_image_factory(processed=False)
        cacao_image_factory(processed=False)
        cacao_image_factory(processed=False)
        
        # Act
        result = stats_service.get_image_stats()
        
        # Assert
        assert result['total'] == 5
        assert result['processed'] == 2
        assert result['unprocessed'] == 3
    
    def test_get_image_stats_processing_rate(self, stats_service, cacao_image_factory):
        """Test calculo de processing_rate."""
        # Arrange
        cacao_image_factory(processed=True)
        cacao_image_factory(processed=True)
        cacao_image_factory(processed=False)
        
        # Act
        result = stats_service.get_image_stats()
        
        # Assert
        assert result['total'] == 3
        assert result['processing_rate'] == round((2 / 3 * 100), 2)
        assert result['processing_rate'] == pytest.approx(66.67, abs=0.01)
    
    def test_get_image_stats_processing_rate_zero_images(self, stats_service):
        """Test processing_rate con cero imagenes."""
        # Arrange & Act
        result = stats_service.get_image_stats()
        
        # Assert
        assert result['processing_rate'] == 0
    
    def test_get_image_stats_this_week(self, stats_service, cacao_image_factory):
        """Test con imagenes creadas esta semana."""
        # Arrange
        today = timezone.now().date()
        this_week_date = today - timedelta(days=3)
        last_week_date = today - timedelta(days=10)
        
        cacao_image_factory(created_at=timezone.make_aware(
            datetime.combine(this_week_date, datetime.min.time())
        ))
        cacao_image_factory(created_at=timezone.make_aware(
            datetime.combine(last_week_date, datetime.min.time())
        ))
        
        # Act
        result = stats_service.get_image_stats()
        
        # Assert
        assert result['this_week'] == 1
    
    def test_get_image_stats_this_month(self, stats_service, cacao_image_factory):
        """Test con imagenes creadas este mes."""
        # Arrange
        today = timezone.now().date()
        this_month_date = today - timedelta(days=15)
        last_month_date = today - timedelta(days=35)
        
        cacao_image_factory(created_at=timezone.make_aware(
            datetime.combine(this_month_date, datetime.min.time())
        ))
        cacao_image_factory(created_at=timezone.make_aware(
            datetime.combine(last_month_date, datetime.min.time())
        ))
        
        # Act
        result = stats_service.get_image_stats()
        
        # Assert
        assert result['this_month'] == 1


# ============================================================================
# TESTS PARA get_prediction_stats()
# ============================================================================

@pytest.mark.django_db
class TestGetPredictionStats:
    """Tests para el metodo get_prediction_stats()."""
    
    def test_get_prediction_stats_empty_database(self, stats_service):
        """Test con base de datos vacia."""
        # Arrange & Act
        result = stats_service.get_prediction_stats()
        
        # Assert
        assert result['total'] == 0
        assert result['average_dimensions']['alto_mm'] == 0
        assert result['average_dimensions']['ancho_mm'] == 0
        assert result['average_dimensions']['grosor_mm'] == 0
        assert result['average_dimensions']['peso_g'] == 0
        assert result['average_confidence'] == 0
        assert result['average_processing_time_ms'] == 0
        assert result['quality_distribution'] == {
            'excelente': 0,
            'buena': 0,
            'regular': 0,
            'baja': 0
        }
    
    def test_get_prediction_stats_total(self, stats_service, cacao_prediction_factory):
        """Test conteo total de predicciones."""
        # Arrange
        cacao_prediction_factory()
        cacao_prediction_factory()
        cacao_prediction_factory()
        
        # Act
        result = stats_service.get_prediction_stats()
        
        # Assert
        assert result['total'] == 3
    
    def test_get_prediction_stats_average_dimensions(self, stats_service, cacao_prediction_factory):
        """Test calculo de promedios de dimensiones."""
        # Arrange
        cacao_prediction_factory(alto_mm=25.0, ancho_mm=15.0, grosor_mm=8.0, peso_g=1.5)
        cacao_prediction_factory(alto_mm=30.0, ancho_mm=20.0, grosor_mm=10.0, peso_g=2.0)
        cacao_prediction_factory(alto_mm=20.0, ancho_mm=10.0, grosor_mm=6.0, peso_g=1.0)
        
        # Act
        result = stats_service.get_prediction_stats()
        
        # Assert
        assert result['average_dimensions']['alto_mm'] == round((25.0 + 30.0 + 20.0) / 3, 2)
        assert result['average_dimensions']['ancho_mm'] == round((15.0 + 20.0 + 10.0) / 3, 2)
        assert result['average_dimensions']['grosor_mm'] == round((8.0 + 10.0 + 6.0) / 3, 2)
        assert result['average_dimensions']['peso_g'] == round((1.5 + 2.0 + 1.0) / 3, 2)
    
    def test_get_prediction_stats_average_confidence(self, stats_service, cacao_prediction_factory):
        """Test calculo de confianza promedio."""
        # Arrange
        # avg_conf = (0.9 + 0.85 + 0.8 + 0.75) / 4 = 0.825
        cacao_prediction_factory(confidence_alto=0.9, confidence_ancho=0.85, confidence_grosor=0.8, confidence_peso=0.75)
        # avg_conf = (0.8 + 0.75 + 0.7 + 0.65) / 4 = 0.725
        cacao_prediction_factory(confidence_alto=0.8, confidence_ancho=0.75, confidence_grosor=0.7, confidence_peso=0.65)
        
        # Act
        result = stats_service.get_prediction_stats()
        
        # Assert
        expected_avg = (0.825 + 0.725) / 2
        assert result['average_confidence'] == pytest.approx(expected_avg, abs=0.001)
    
    def test_get_prediction_stats_processing_time(self, stats_service, cacao_prediction_factory):
        """Test calculo de tiempo de procesamiento promedio."""
        # Arrange
        cacao_prediction_factory(processing_time_ms=100)
        cacao_prediction_factory(processing_time_ms=200)
        cacao_prediction_factory(processing_time_ms=300)
        
        # Act
        result = stats_service.get_prediction_stats()
        
        # Assert
        assert result['average_processing_time_ms'] == round((100 + 200 + 300) / 3, 0)
    
    def test_get_prediction_stats_quality_distribution_excelente(self, stats_service, cacao_prediction_factory):
        """Test distribucion de calidad - excelente (>= 0.8)."""
        # Arrange
        # avg_conf = (0.9 + 0.85 + 0.8 + 0.8) / 4 = 0.8375 >= 0.8
        cacao_prediction_factory(confidence_alto=0.9, confidence_ancho=0.85, confidence_grosor=0.8, confidence_peso=0.8)
        cacao_prediction_factory(confidence_alto=0.95, confidence_ancho=0.9, confidence_grosor=0.85, confidence_peso=0.8)
        
        # Act
        result = stats_service.get_prediction_stats()
        
        # Assert
        assert result['quality_distribution']['excelente'] == 2
        assert result['quality_distribution']['buena'] == 0
        assert result['quality_distribution']['regular'] == 0
        assert result['quality_distribution']['baja'] == 0
    
    def test_get_prediction_stats_quality_distribution_buena(self, stats_service, cacao_prediction_factory):
        """Test distribucion de calidad - buena (0.6 <= avg < 0.8)."""
        # Arrange
        # avg_conf = (0.7 + 0.65 + 0.6 + 0.6) / 4 = 0.6375
        cacao_prediction_factory(confidence_alto=0.7, confidence_ancho=0.65, confidence_grosor=0.6, confidence_peso=0.6)
        cacao_prediction_factory(confidence_alto=0.75, confidence_ancho=0.7, confidence_grosor=0.65, confidence_peso=0.6)
        
        # Act
        result = stats_service.get_prediction_stats()
        
        # Assert
        assert result['quality_distribution']['excelente'] == 0
        assert result['quality_distribution']['buena'] == 2
        assert result['quality_distribution']['regular'] == 0
        assert result['quality_distribution']['baja'] == 0
    
    def test_get_prediction_stats_quality_distribution_regular(self, stats_service, cacao_prediction_factory):
        """Test distribucion de calidad - regular (0.4 <= avg < 0.6)."""
        # Arrange
        # avg_conf = (0.5 + 0.45 + 0.4 + 0.4) / 4 = 0.4375
        cacao_prediction_factory(confidence_alto=0.5, confidence_ancho=0.45, confidence_grosor=0.4, confidence_peso=0.4)
        cacao_prediction_factory(confidence_alto=0.55, confidence_ancho=0.5, confidence_grosor=0.45, confidence_peso=0.4)
        
        # Act
        result = stats_service.get_prediction_stats()
        
        # Assert
        assert result['quality_distribution']['excelente'] == 0
        assert result['quality_distribution']['buena'] == 0
        assert result['quality_distribution']['regular'] == 2
        assert result['quality_distribution']['baja'] == 0
    
    def test_get_prediction_stats_quality_distribution_baja(self, stats_service, cacao_prediction_factory):
        """Test distribucion de calidad - baja (< 0.4)."""
        # Arrange
        # avg_conf = (0.3 + 0.25 + 0.2 + 0.2) / 4 = 0.2375
        cacao_prediction_factory(confidence_alto=0.3, confidence_ancho=0.25, confidence_grosor=0.2, confidence_peso=0.2)
        cacao_prediction_factory(confidence_alto=0.35, confidence_ancho=0.3, confidence_grosor=0.25, confidence_peso=0.2)
        
        # Act
        result = stats_service.get_prediction_stats()
        
        # Assert
        assert result['quality_distribution']['excelente'] == 0
        assert result['quality_distribution']['buena'] == 0
        assert result['quality_distribution']['regular'] == 0
        assert result['quality_distribution']['baja'] == 2
    
    def test_get_prediction_stats_quality_distribution_mixed(self, stats_service, cacao_prediction_factory):
        """Test distribucion de calidad con todas las categorias."""
        # Arrange
        # Excelente
        cacao_prediction_factory(confidence_alto=0.9, confidence_ancho=0.85, confidence_grosor=0.8, confidence_peso=0.8)
        # Buena
        cacao_prediction_factory(confidence_alto=0.7, confidence_ancho=0.65, confidence_grosor=0.6, confidence_peso=0.6)
        # Regular
        cacao_prediction_factory(confidence_alto=0.5, confidence_ancho=0.45, confidence_grosor=0.4, confidence_peso=0.4)
        # Baja
        cacao_prediction_factory(confidence_alto=0.3, confidence_ancho=0.25, confidence_grosor=0.2, confidence_peso=0.2)
        
        # Act
        result = stats_service.get_prediction_stats()
        
        # Assert
        assert result['quality_distribution']['excelente'] == 1
        assert result['quality_distribution']['buena'] == 1
        assert result['quality_distribution']['regular'] == 1
        assert result['quality_distribution']['baja'] == 1


# ============================================================================
# TESTS PARA get_finca_stats()
# ============================================================================

@pytest.mark.django_db
class TestGetFincaStats:
    """Tests para el metodo get_finca_stats()."""
    
    def test_get_finca_stats_empty_database(self, stats_service):
        """Test con base de datos vacia."""
        # Arrange & Act
        result = stats_service.get_finca_stats()
        
        # Assert
        assert result['total'] == 0
        assert result['this_week'] == 0
        assert result['this_month'] == 0
    
    def test_get_finca_stats_total(self, stats_service, finca_factory):
        """Test conteo total de fincas."""
        # Arrange
        finca_factory()
        finca_factory()
        finca_factory()
        
        # Act
        result = stats_service.get_finca_stats()
        
        # Assert
        assert result['total'] == 3
    
    def test_get_finca_stats_this_week(self, stats_service, finca_factory):
        """Test con fincas registradas esta semana."""
        # Arrange
        today = timezone.now().date()
        this_week_date = today - timedelta(days=3)
        last_week_date = today - timedelta(days=10)
        
        finca_factory(fecha_registro=timezone.make_aware(
            datetime.combine(this_week_date, datetime.min.time())
        ))
        finca_factory(fecha_registro=timezone.make_aware(
            datetime.combine(last_week_date, datetime.min.time())
        ))
        
        # Act
        result = stats_service.get_finca_stats()
        
        # Assert
        assert result['this_week'] == 1
    
    def test_get_finca_stats_this_month(self, stats_service, finca_factory):
        """Test con fincas registradas este mes."""
        # Arrange
        today = timezone.now().date()
        this_month_date = today - timedelta(days=15)
        last_month_date = today - timedelta(days=35)
        
        finca_factory(fecha_registro=timezone.make_aware(
            datetime.combine(this_month_date, datetime.min.time())
        ))
        finca_factory(fecha_registro=timezone.make_aware(
            datetime.combine(last_month_date, datetime.min.time())
        ))
        
        # Act
        result = stats_service.get_finca_stats()
        
        # Assert
        assert result['this_month'] == 1


# ============================================================================
# TESTS PARA get_activity_by_day() - MOCK
# ============================================================================

@pytest.mark.django_db
class TestGetActivityByDay:
    """Tests para el metodo get_activity_by_day() usando mocks."""
    
    def test_get_activity_by_day_empty_activity(self, stats_service):
        """Test con actividad vacia."""
        # Arrange
        mock_images_qs = MagicMock()
        mock_images_qs.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = []
        
        mock_users_qs = MagicMock()
        mock_users_qs.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = []
        
        mock_predictions_qs = MagicMock()
        mock_predictions_qs.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = []
        
        mock_cacao_image = MagicMock()
        mock_cacao_image.objects = mock_images_qs
        
        mock_cacao_prediction = MagicMock()
        mock_cacao_prediction.objects = mock_predictions_qs
        
        with patch.object(stats_service, 'CacaoImage', mock_cacao_image, create=True), \
             patch.object(stats_service, 'CacaoPrediction', mock_cacao_prediction, create=True), \
             patch.object(User, 'objects', mock_users_qs):
            
            # Act
            result = stats_service.get_activity_by_day(max_days=7)
            
            # Assert
            assert 'labels' in result
            assert 'data' in result
            assert len(result['labels']) == 7
            assert len(result['data']) == 7
            assert all(count == 0 for count in result['data'])
    
    def test_get_activity_by_day_with_activity(self, stats_service):
        """Test con actividad por dia."""
        # Arrange
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        two_days_ago = today - timedelta(days=2)
        
        # Mock images by date
        mock_images_qs = MagicMock()
        mock_images_qs.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = [
            (today, 5),
            (yesterday, 3)
        ]
        
        # Mock users by date
        mock_users_qs = MagicMock()
        mock_users_qs.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = [
            (yesterday, 2)
        ]
        
        # Mock predictions by date
        mock_predictions_qs = MagicMock()
        mock_predictions_qs.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = [
            (two_days_ago, 4)
        ]
        
        mock_cacao_image = MagicMock()
        mock_cacao_image.objects = mock_images_qs
        
        mock_cacao_prediction = MagicMock()
        mock_cacao_prediction.objects = mock_predictions_qs
        
        with patch.object(stats_service, 'CacaoImage', mock_cacao_image, create=True), \
             patch.object(stats_service, 'CacaoPrediction', mock_cacao_prediction, create=True), \
             patch.object(User, 'objects', mock_users_qs):
            
            # Act
            result = stats_service.get_activity_by_day(max_days=7)
            
            # Assert
            assert 'labels' in result
            assert 'data' in result
            assert len(result['labels']) == 7
            assert len(result['data']) == 7
            # Verificar que 'Hoy' esta en labels
            assert 'Hoy' in result['labels'][-1] or 'Hoy' == result['labels'][-1]
    
    def test_get_activity_by_day_custom_max_days(self, stats_service):
        """Test con max_days personalizado."""
        # Arrange
        # Para que el método use max_days, necesitamos simular más de 10 días con actividad
        # Crear datos para 11 días diferentes para activar la lógica de max_days
        today = timezone.now().date()
        dates_with_activity = [
            (today - timedelta(days=i), 1) for i in range(11)
        ]
        
        mock_images_qs = MagicMock()
        mock_images_qs.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = dates_with_activity
        
        mock_users_qs = MagicMock()
        mock_users_qs.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = []
        
        mock_predictions_qs = MagicMock()
        mock_predictions_qs.filter.return_value.annotate.return_value.values.return_value.annotate.return_value.values_list.return_value = []
        
        mock_cacao_image = MagicMock()
        mock_cacao_image.objects = mock_images_qs
        
        mock_cacao_prediction = MagicMock()
        mock_cacao_prediction.objects = mock_predictions_qs
        
        with patch.object(stats_service, 'CacaoImage', mock_cacao_image, create=True), \
             patch.object(stats_service, 'CacaoPrediction', mock_cacao_prediction, create=True), \
             patch.object(User, 'objects', mock_users_qs):
            
            # Act
            result = stats_service.get_activity_by_day(max_days=14)
            
            # Assert
            assert len(result['labels']) == 14
            assert len(result['data']) == 14


# ============================================================================
# TESTS PARA get_top_regions() y get_top_fincas()
# ============================================================================

@pytest.mark.django_db
class TestGetTopRegions:
    """Tests para el metodo get_top_regions()."""
    
    def test_get_top_regions_empty_database(self, stats_service):
        """Test con base de datos vacia."""
        # Arrange & Act
        result = stats_service.get_top_regions()
        
        # Assert
        assert result == []
    
    def test_get_top_regions_grouping(self, stats_service, cacao_image_factory):
        """Test agrupacion por region."""
        # Arrange
        cacao_image_factory(region='Region A')
        cacao_image_factory(region='Region A')
        cacao_image_factory(region='Region B')
        cacao_image_factory(region='Region C')
        
        # Act
        result = stats_service.get_top_regions(limit=10)
        
        # Assert
        assert len(result) == 3
        # Verificar ordenamiento por count descendente
        counts = [r['count'] for r in result]
        assert counts == sorted(counts, reverse=True)
        assert result[0]['region'] == 'Region A'
        assert result[0]['count'] == 2
    
    def test_get_top_regions_processed_count(self, stats_service, cacao_image_factory):
        """Test conteo de imagenes procesadas por region."""
        # Arrange
        cacao_image_factory(region='Region A', processed=True)
        cacao_image_factory(region='Region A', processed=True)
        cacao_image_factory(region='Region A', processed=False)
        
        # Act
        result = stats_service.get_top_regions()
        
        # Assert
        assert len(result) == 1
        assert result[0]['region'] == 'Region A'
        assert result[0]['count'] == 3
        assert result[0]['processed_count'] == 2
    
    def test_get_top_regions_limit(self, stats_service, cacao_image_factory):
        """Test limite de resultados."""
        # Arrange
        for i in range(15):
            cacao_image_factory(region=f'Region {i}')
        
        # Act
        result = stats_service.get_top_regions(limit=5)
        
        # Assert
        assert len(result) == 5


@pytest.mark.django_db
class TestGetTopFincas:
    """Tests para el metodo get_top_fincas()."""
    
    def test_get_top_fincas_empty_database(self, stats_service):
        """Test con base de datos vacia."""
        # Arrange & Act
        result = stats_service.get_top_fincas()
        
        # Assert
        assert result == []
    
    def test_get_top_fincas_grouping(self, stats_service, cacao_image_factory, finca_factory):
        """Test agrupacion por finca."""
        # Arrange
        finca1 = finca_factory(nombre='Finca A')
        finca2 = finca_factory(nombre='Finca B')
        finca3 = finca_factory(nombre='Finca C')
        
        cacao_image_factory(finca=finca1)
        cacao_image_factory(finca=finca1)
        cacao_image_factory(finca=finca2)
        cacao_image_factory(finca=finca3)
        
        # Act
        result = stats_service.get_top_fincas(limit=10)
        
        # Assert
        assert len(result) == 3
        # Verificar ordenamiento por count descendente
        counts = [r['count'] for r in result]
        assert counts == sorted(counts, reverse=True)
        assert result[0]['finca'] == finca1.id
        assert result[0]['count'] == 2
    
    def test_get_top_fincas_processed_count(self, stats_service, cacao_image_factory, finca_factory):
        """Test conteo de imagenes procesadas por finca."""
        # Arrange
        finca = finca_factory()
        cacao_image_factory(finca=finca, processed=True)
        cacao_image_factory(finca=finca, processed=True)
        cacao_image_factory(finca=finca, processed=False)
        
        # Act
        result = stats_service.get_top_fincas()
        
        # Assert
        assert len(result) == 1
        assert result[0]['finca'] == finca.id
        assert result[0]['count'] == 3
        assert result[0]['processed_count'] == 2
    
    def test_get_top_fincas_limit(self, stats_service, cacao_image_factory, finca_factory):
        """Test limite de resultados."""
        # Arrange
        fincas = [finca_factory() for _ in range(15)]
        for finca in fincas:
            cacao_image_factory(finca=finca)
        
        # Act
        result = stats_service.get_top_fincas(limit=5)
        
        # Assert
        assert len(result) == 5


# ============================================================================
# TESTS PARA get_all_stats() - MOCK
# ============================================================================

@pytest.mark.django_db
class TestGetAllStats:
    """Tests para el metodo get_all_stats() usando mocks."""
    
    def test_get_all_stats_success(self, stats_service):
        """Test ruta feliz de get_all_stats."""
        # Arrange
        mock_user_stats = {'total': 10, 'active': 8}
        mock_image_stats = {'total': 50, 'processed': 40}
        
        # Guardar el valor esperado de quality_distribution antes de que el método lo modifique con .pop()
        expected_quality_distribution = {'excelente': 10, 'buena': 20, 'regular': 5, 'baja': 5}
        
        mock_activity = {'labels': ['Hoy', 'Ayer'], 'data': [5, 3]}
        mock_finca_stats = {'total': 5, 'this_week': 1}
        mock_top_regions = [{'region': 'Region A', 'count': 10}]
        mock_top_fincas = [{'finca': 1, 'count': 5}]
        
        # Función que devuelve una copia nueva del diccionario para evitar efectos secundarios
        # cuando get_all_stats() hace .pop() sobre prediction_stats
        def get_prediction_stats_side_effect():
            return {
                'total': 40,
                'average_confidence': 0.85,
                'quality_distribution': expected_quality_distribution.copy()
            }
        
        with patch.object(stats_service, 'get_user_stats', return_value=mock_user_stats), \
             patch.object(stats_service, 'get_image_stats', return_value=mock_image_stats), \
             patch.object(stats_service, 'get_prediction_stats', side_effect=get_prediction_stats_side_effect), \
             patch.object(stats_service, 'get_activity_by_day', return_value=mock_activity), \
             patch.object(stats_service, 'get_finca_stats', return_value=mock_finca_stats), \
             patch.object(stats_service, 'get_top_regions', return_value=mock_top_regions), \
             patch.object(stats_service, 'get_top_fincas', return_value=mock_top_fincas):
            
            # Act
            result = stats_service.get_all_stats()
            
            # Assert
            assert 'users' in result
            assert 'images' in result
            assert 'fincas' in result
            assert 'predictions' in result
            assert 'top_regions' in result
            assert 'top_fincas' in result
            assert 'activity_by_day' in result
            assert 'quality_distribution' in result
            assert 'generated_at' in result
            
            assert result['users'] == mock_user_stats
            assert result['images'] == mock_image_stats
            assert result['fincas'] == mock_finca_stats
            assert result['top_regions'] == mock_top_regions
            assert result['top_fincas'] == mock_top_fincas
            assert result['activity_by_day'] == mock_activity
            assert result['quality_distribution'] == expected_quality_distribution
            
            # Verificar que quality_distribution fue removido de predictions
            assert 'quality_distribution' not in result['predictions']
    
    def test_get_all_stats_exception_returns_empty(self, stats_service):
        """Test que get_all_stats retorna get_empty_stats() en caso de excepcion."""
        # Arrange
        mock_empty_stats = stats_service.get_empty_stats()
        
        with patch.object(stats_service, 'get_user_stats', side_effect=Exception("Mocked error")):
            # Act
            result = stats_service.get_all_stats()
            
            # Assert
            # Verificar que generated_at existe y es un string
            assert 'generated_at' in result
            assert isinstance(result['generated_at'], str)
            
            # Comparar estructuras ignorando generated_at (que cambia en cada ejecución)
            result_without_timestamp = {k: v for k, v in result.items() if k != 'generated_at'}
            mock_empty_without_timestamp = {k: v for k, v in mock_empty_stats.items() if k != 'generated_at'}
            assert result_without_timestamp == mock_empty_without_timestamp
            
            # Verificaciones adicionales de valores específicos
            assert result['users']['total'] == 0
            assert result['images']['total'] == 0
    
    def test_get_all_stats_quality_distribution_removed_from_predictions(self, stats_service):
        """Test que quality_distribution se remueve de predictions."""
        # Arrange
        expected_quality_distribution = {'excelente': 10}
        
        # Función que devuelve una copia nueva para evitar mutaciones con .pop()
        def get_prediction_stats_side_effect():
            return {
                'total': 40,
                'average_confidence': 0.85,
                'quality_distribution': expected_quality_distribution.copy()
            }
        
        # Mocks con estructuras completas para evitar KeyErrors al acceder a campos
        mock_user_stats = {'total': 0}
        mock_image_stats = {'total': 0}
        
        with patch.object(stats_service, 'get_user_stats', return_value=mock_user_stats), \
             patch.object(stats_service, 'get_image_stats', return_value=mock_image_stats), \
             patch.object(stats_service, 'get_prediction_stats', side_effect=get_prediction_stats_side_effect), \
             patch.object(stats_service, 'get_activity_by_day', return_value={}), \
             patch.object(stats_service, 'get_finca_stats', return_value={'total': 0}), \
             patch.object(stats_service, 'get_top_regions', return_value=[]), \
             patch.object(stats_service, 'get_top_fincas', return_value=[]):
            
            # Act
            result = stats_service.get_all_stats()
            
            # Assert
            assert 'quality_distribution' not in result['predictions']
            assert 'quality_distribution' in result
            assert result['quality_distribution'] == expected_quality_distribution
    
    def test_get_all_stats_quality_distribution_fallback(self, stats_service):
        """Test fallback de quality_distribution cuando no esta presente."""
        # Arrange
        # Función que devuelve una copia nueva sin quality_distribution para probar el fallback
        def get_prediction_stats_side_effect():
            return {
                'total': 40,
                'average_confidence': 0.85
            }
        
        # Mocks con estructuras completas para evitar KeyErrors
        mock_user_stats = {'total': 0}
        mock_image_stats = {'total': 0}
        
        with patch.object(stats_service, 'get_user_stats', return_value=mock_user_stats), \
             patch.object(stats_service, 'get_image_stats', return_value=mock_image_stats), \
             patch.object(stats_service, 'get_prediction_stats', side_effect=get_prediction_stats_side_effect), \
             patch.object(stats_service, 'get_activity_by_day', return_value={}), \
             patch.object(stats_service, 'get_finca_stats', return_value={'total': 0}), \
             patch.object(stats_service, 'get_top_regions', return_value=[]), \
             patch.object(stats_service, 'get_top_fincas', return_value=[]):
            
            # Act
            result = stats_service.get_all_stats()
            
            # Assert
            assert 'quality_distribution' in result
            assert result['quality_distribution'] == {
                'excelente': 0,
                'buena': 0,
                'regular': 0,
                'baja': 0
            }


# ============================================================================
# TESTS PARA get_empty_stats()
# ============================================================================

@pytest.mark.django_db
class TestGetEmptyStats:
    """Tests para el metodo get_empty_stats()."""
    
    def test_get_empty_stats_structure(self, stats_service):
        """Test estructura de get_empty_stats."""
        # Arrange & Act
        result = stats_service.get_empty_stats()
        
        # Assert
        assert 'users' in result
        assert 'images' in result
        assert 'fincas' in result
        assert 'predictions' in result
        assert 'top_regions' in result
        assert 'top_fincas' in result
        assert 'generated_at' in result
        
        # Verificar estructura de users
        assert result['users']['total'] == 0
        assert result['users']['active'] == 0
        assert result['users']['staff'] == 0
        assert result['users']['superusers'] == 0
        assert result['users']['analysts'] == 0
        assert result['users']['farmers'] == 0
        assert result['users']['verified'] == 0
        assert result['users']['this_week'] == 0
        assert result['users']['this_month'] == 0
        
        # Verificar estructura de images
        assert result['images']['total'] == 0
        assert result['images']['processed'] == 0
        assert result['images']['unprocessed'] == 0
        assert result['images']['this_week'] == 0
        assert result['images']['this_month'] == 0
        assert result['images']['processing_rate'] == 0
        
        # Verificar estructura de predictions
        assert result['predictions']['total'] == 0
        assert result['predictions']['average_dimensions']['alto_mm'] == 0
        assert result['predictions']['average_dimensions']['ancho_mm'] == 0
        assert result['predictions']['average_dimensions']['grosor_mm'] == 0
        assert result['predictions']['average_dimensions']['peso_g'] == 0
        assert result['predictions']['average_confidence'] == 0
        assert result['predictions']['average_processing_time_ms'] == 0
        
        # Verificar estructura de fincas
        assert result['fincas']['total'] == 0
        assert result['fincas']['this_week'] == 0
        assert result['fincas']['this_month'] == 0
        
        # Verificar listas vacias
        assert result['top_regions'] == []
        assert result['top_fincas'] == []
        
        # Verificar activity_by_day
        assert 'activity_by_day' in result
        assert 'labels' in result['activity_by_day']
        assert 'data' in result['activity_by_day']
        
        # Verificar quality_distribution
        assert 'quality_distribution' in result
        assert result['quality_distribution']['excelente'] == 0
        assert result['quality_distribution']['buena'] == 0
        assert result['quality_distribution']['regular'] == 0
        assert result['quality_distribution']['baja'] == 0
        
        # Verificar generated_at
        assert 'generated_at' in result
        assert isinstance(result['generated_at'], str)