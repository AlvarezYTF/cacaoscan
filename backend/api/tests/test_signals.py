"""
Tests for API signals.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth.models import User
from django.utils import timezone

from api import signals


@pytest.fixture
def mock_notification():
    """Create a mock notification."""
    notification = Mock()
    notification.id = 1
    notification.tipo = 'success'
    notification.titulo = 'Test'
    notification.mensaje = 'Test message'
    return notification


@pytest.fixture
def mock_realtime_service():
    """Create a mock realtime service."""
    service = Mock()
    service.create_and_send_notification = Mock(return_value=Mock())
    return service


@pytest.mark.django_db
class TestCacaoPredictionSignals:
    """Tests for CacaoPrediction signals."""
    
    def test_notify_prediction_completed_high_confidence(self, mock_realtime_service):
        """Test notification when prediction completed with high confidence."""
        with patch('api.signals.CacaoPrediction', Mock()):
            with patch('api.signals.realtime_service', mock_realtime_service):
                with patch('api.services.email.send_email_notification', Mock(return_value={'success': True})):
                    # Create mock prediction
                    mock_image = Mock()
                    mock_image.user = Mock()
                    mock_image.user.id = 1
                    mock_image.user.username = 'testuser'
                    mock_image.user.email = 'test@example.com'
                    mock_image.user.get_full_name = Mock(return_value='Test User')
                    mock_image.id = 1
                    
                    mock_prediction = Mock()
                    mock_prediction.id = 1
                    mock_prediction.image = mock_image
                    mock_prediction.average_confidence = 0.85
                    mock_prediction.alto_mm = 25.5
                    mock_prediction.ancho_mm = 20.3
                    mock_prediction.grosor_mm = 15.2
                    mock_prediction.peso_g = 8.5
                    mock_prediction.processing_time_ms = 150
                    mock_prediction.created_at = timezone.now()
                    
                    # Call signal handler
                    signals.notify_prediction_completed(
                        sender=Mock(),
                        instance=mock_prediction,
                        created=True
                    )
                    
                    # Verify notification was created
                    assert mock_realtime_service.create_and_send_notification.called
                    call_args = mock_realtime_service.create_and_send_notification.call_args
                    assert call_args[1]['tipo'] == 'SUCCESS'
                    assert 'Alta Calidad' in call_args[1]['titulo']
    
    def test_notify_prediction_completed_medium_confidence(self, mock_realtime_service):
        """Test notification when prediction completed with medium confidence."""
        with patch('api.signals.CacaoPrediction', Mock()):
            with patch('api.signals.realtime_service', mock_realtime_service):
                with patch('api.services.email.send_email_notification', Mock(return_value={'success': True})):
                    mock_image = Mock()
                    mock_image.user = Mock()
                    mock_image.user.id = 1
                    mock_image.user.username = 'testuser'
                    mock_image.user.email = 'test@example.com'
                    mock_image.user.get_full_name = Mock(return_value='Test User')
                    mock_image.id = 1
                    
                    mock_prediction = Mock()
                    mock_prediction.id = 1
                    mock_prediction.image = mock_image
                    mock_prediction.average_confidence = 0.65
                    mock_prediction.alto_mm = 25.5
                    mock_prediction.ancho_mm = 20.3
                    mock_prediction.grosor_mm = 15.2
                    mock_prediction.peso_g = 8.5
                    mock_prediction.processing_time_ms = 150
                    mock_prediction.created_at = timezone.now()
                    
                    signals.notify_prediction_completed(
                        sender=Mock(),
                        instance=mock_prediction,
                        created=True
                    )
                    
                    call_args = mock_realtime_service.create_and_send_notification.call_args
                    assert call_args[1]['tipo'] == 'INFO'
                    assert 'Calidad Estándar' in call_args[1]['titulo']
    
    def test_notify_prediction_completed_low_confidence(self, mock_realtime_service):
        """Test notification when prediction completed with low confidence."""
        with patch('api.signals.CacaoPrediction', Mock()):
            with patch('api.signals.realtime_service', mock_realtime_service):
                with patch('api.services.email.send_email_notification', Mock(return_value={'success': True})):
                    mock_image = Mock()
                    mock_image.user = Mock()
                    mock_image.user.id = 1
                    mock_image.user.username = 'testuser'
                    mock_image.user.email = 'test@example.com'
                    mock_image.user.get_full_name = Mock(return_value='Test User')
                    mock_image.id = 1
                    
                    mock_prediction = Mock()
                    mock_prediction.id = 1
                    mock_prediction.image = mock_image
                    mock_prediction.average_confidence = 0.45
                    mock_prediction.alto_mm = 25.5
                    mock_prediction.ancho_mm = 20.3
                    mock_prediction.grosor_mm = 15.2
                    mock_prediction.peso_g = 8.5
                    mock_prediction.processing_time_ms = 150
                    mock_prediction.created_at = timezone.now()
                    
                    signals.notify_prediction_completed(
                        sender=Mock(),
                        instance=mock_prediction,
                        created=True
                    )
                    
                    call_args = mock_realtime_service.create_and_send_notification.call_args
                    assert call_args[1]['tipo'] == 'WARNING'
                    assert 'Calidad Baja' in call_args[1]['titulo']
    
    def test_notify_prediction_completed_not_created(self, mock_realtime_service):
        """Test that signal doesn't trigger when prediction is not newly created."""
        with patch('api.signals.CacaoPrediction', Mock()):
            with patch('api.signals.realtime_service', mock_realtime_service):
                mock_prediction = Mock()
                
                signals.notify_prediction_completed(
                    sender=Mock(),
                    instance=mock_prediction,
                    created=False
                )
                
                assert not mock_realtime_service.create_and_send_notification.called
    
    def test_notify_prediction_completed_email_error(self, mock_realtime_service):
        """Test notification when email sending fails."""
        with patch('api.signals.CacaoPrediction', Mock()):
            with patch('api.signals.realtime_service', mock_realtime_service):
                with patch('api.services.email.send_email_notification', Mock(return_value={'success': False, 'error': 'Email error'})):
                    mock_image = Mock()
                    mock_image.user = Mock()
                    mock_image.user.id = 1
                    mock_image.user.username = 'testuser'
                    mock_image.user.email = 'test@example.com'
                    mock_image.user.get_full_name = Mock(return_value='Test User')
                    mock_image.id = 1
                    
                    mock_prediction = Mock()
                    mock_prediction.id = 1
                    mock_prediction.image = mock_image
                    mock_prediction.average_confidence = 0.85
                    mock_prediction.alto_mm = 25.5
                    mock_prediction.ancho_mm = 20.3
                    mock_prediction.grosor_mm = 15.2
                    mock_prediction.peso_g = 8.5
                    mock_prediction.processing_time_ms = 150
                    mock_prediction.created_at = timezone.now()
                    
                    signals.notify_prediction_completed(
                        sender=Mock(),
                        instance=mock_prediction,
                        created=True
                    )
                    
                    assert mock_realtime_service.create_and_send_notification.called


@pytest.mark.django_db
class TestTrainingJobSignals:
    """Tests for TrainingJob signals."""
    
    def test_notify_training_completed(self, mock_realtime_service):
        """Test notification when training job is completed."""
        with patch('api.signals.TrainingJob', Mock()):
            with patch('api.signals.realtime_service', mock_realtime_service):
                with patch('api.services.email.send_email_notification', Mock(return_value={'success': True})):
                    with patch('api.signals.Notification', Mock()):
                        with patch('api.signals.User') as mock_user_class:
                            mock_user = Mock()
                            mock_user.id = 1
                            mock_user.username = 'testuser'
                            mock_user.email = 'test@example.com'
                            mock_user.get_full_name = Mock(return_value='Test User')
                            mock_user_class.objects.filter.return_value = []
                            
                            mock_job = Mock()
                            mock_job.job_id = 'job_123'
                            mock_job.model_name = 'test_model'
                            mock_job.metrics = {'accuracy': 0.95}
                            mock_job.duration_formatted = '1h 30m'
                            mock_job.status = 'completed'
                            mock_job.created_by = mock_user
                            mock_job.job_type = 'full_training'
                            mock_job.updated_at = timezone.now()
                            
                            signals.notify_training_completed(
                                sender=Mock(),
                                instance=mock_job,
                                created=False
                            )
                            
                            assert mock_realtime_service.create_and_send_notification.called
    
    def test_notify_training_completed_not_completed_status(self, mock_realtime_service):
        """Test that signal doesn't trigger when status is not completed."""
        with patch('api.signals.TrainingJob', Mock()):
            with patch('api.signals.realtime_service', mock_realtime_service):
                mock_job = Mock()
                mock_job.status = 'running'
                
                signals.notify_training_completed(
                    sender=Mock(),
                    instance=mock_job,
                    created=False
                )
                
                assert not mock_realtime_service.create_and_send_notification.called
    
    def test_notify_training_failed(self, mock_realtime_service):
        """Test notification when training job fails."""
        with patch('api.signals.TrainingJob', Mock()):
            with patch('api.signals.realtime_service', mock_realtime_service):
                mock_user = Mock()
                mock_user.id = 1
                mock_user.username = 'testuser'
                
                mock_job = Mock()
                mock_job.job_id = 'job_123'
                mock_job.model_name = 'test_model'
                mock_job.error_message = 'Training failed'
                mock_job.status = 'failed'
                mock_job.created_by = mock_user
                
                signals.notify_training_failed(
                    sender=Mock(),
                    instance=mock_job,
                    created=False
                )
                
                assert mock_realtime_service.create_and_send_notification.called
                call_args = mock_realtime_service.create_and_send_notification.call_args
                assert call_args[1]['tipo'] == 'ERROR'


@pytest.mark.django_db
class TestUserSignals:
    """Tests for User signals."""
    
    def test_notify_user_registered(self, mock_realtime_service):
        """Test notification when new user is registered."""
        with patch('api.signals.realtime_service', mock_realtime_service):
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            user = User.objects.create_user(
                username=f'newuser_{unique_id}',
                email=f'newuser_{unique_id}@example.com',
                password='testpass123'
            )
            
            signals.notify_user_registered(
                sender=User,
                instance=user,
                created=True
            )
            
            assert mock_realtime_service.create_and_send_notification.called
            call_args = mock_realtime_service.create_and_send_notification.call_args
            assert call_args[1]['tipo'] == 'WELCOME'
            assert 'Bienvenido' in call_args[1]['titulo']


@pytest.mark.django_db
class TestFincaLoteSignals:
    """Tests for Finca and Lote signals."""
    
    def test_notify_finca_created(self):
        """Test notification when finca is created."""
        with patch('api.signals.Finca', Mock()):
            with patch('api.signals.Notification') as mock_notification_class:
                mock_notification_class.create_notification = Mock(return_value=Mock())
                
                mock_agricultor = Mock()
                mock_agricultor.username = 'testuser'
                
                mock_finca = Mock()
                mock_finca.id = 1
                mock_finca.nombre = 'Test Finca'
                mock_finca.municipio = 'Test Municipio'
                mock_finca.departamento = 'Test Departamento'
                mock_finca.ubicacion_completa = 'Test Location'
                mock_finca.hectareas = 10.5
                mock_finca.agricultor = mock_agricultor
                
                signals.notify_finca_created(
                    sender=Mock(),
                    instance=mock_finca,
                    created=True
                )
                
                assert mock_notification_class.create_notification.called
    
    def test_notify_lote_created(self):
        """Test notification when lote is created."""
        with patch('api.signals.Lote', Mock()):
            with patch('api.signals.Notification') as mock_notification_class:
                mock_notification_class.create_notification = Mock(return_value=Mock())
                
                mock_agricultor = Mock()
                mock_agricultor.username = 'testuser'
                
                mock_finca = Mock()
                mock_finca.nombre = 'Test Finca'
                mock_finca.agricultor = mock_agricultor
                
                mock_lote = Mock()
                mock_lote.id = 1
                mock_lote.identificador = 'LOTE-001'
                mock_lote.variedad = 'Criollo'
                mock_lote.finca = mock_finca
                mock_lote.area_hectareas = 5.0
                
                signals.notify_lote_created(
                    sender=Mock(),
                    instance=mock_lote,
                    created=True
                )
                
                assert mock_notification_class.create_notification.called
    
    def test_notify_lote_cosechado(self):
        """Test notification when lote is marked as harvested."""
        with patch('api.signals.Lote', Mock()):
            with patch('api.signals.Notification') as mock_notification_class:
                mock_notification_class.create_notification = Mock(return_value=Mock())
                
                mock_agricultor = Mock()
                mock_agricultor.username = 'testuser'
                
                mock_finca = Mock()
                mock_finca.nombre = 'Test Finca'
                mock_finca.agricultor = mock_agricultor
                
                mock_lote = Mock()
                mock_lote.id = 1
                mock_lote.identificador = 'LOTE-001'
                mock_lote.variedad = 'Criollo'
                mock_lote.finca = mock_finca
                mock_lote.estado = 'cosechado'
                mock_lote.fecha_cosecha = timezone.now()
                
                signals.notify_lote_cosechado(
                    sender=Mock(),
                    instance=mock_lote,
                    created=False
                )
                
                assert mock_notification_class.create_notification.called


@pytest.mark.django_db
class TestHelperFunctions:
    """Tests for helper functions."""
    
    def test_send_custom_notification(self):
        """Test send_custom_notification helper function."""
        with patch('api.signals.Notification') as mock_notification_class:
            mock_notification = Mock()
            mock_notification_class.create_notification = Mock(return_value=mock_notification)
            
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            user = User.objects.create_user(
                username=f'testuser_{unique_id}',
                email=f'test_{unique_id}@example.com',
                password='testpass123'
            )
            
            result = signals.send_custom_notification(
                user=user,
                tipo='info',
                titulo='Test Title',
                mensaje='Test Message',
                datos_extra={'key': 'value'}
            )
            
            assert result == mock_notification
            assert mock_notification_class.create_notification.called
    
    def test_send_bulk_notification(self):
        """Test send_bulk_notification helper function."""
        with patch('api.signals.Notification') as mock_notification_class:
            mock_notification_class.create_notification = Mock(return_value=Mock())
            
            user1 = User.objects.create_user(
                username='user1',
                email='user1@example.com',
                password='testpass123'
            )
            user2 = User.objects.create_user(
                username='user2',
                email='user2@example.com',
                password='testpass123'
            )
            
            result = signals.send_bulk_notification(
                users=[user1, user2],
                tipo='info',
                titulo='Test Title',
                mensaje='Test Message',
                datos_extra={'key': 'value'}
            )
            
            assert result == 2
            assert mock_notification_class.create_notification.call_count == 2
    
    def test_send_bulk_notification_with_error(self):
        """Test send_bulk_notification when one notification fails."""
        with patch('api.signals.Notification') as mock_notification_class:
            call_count = 0
            def side_effect(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise RuntimeError("Notification error")
                return Mock()
            
            mock_notification_class.create_notification = Mock(side_effect=side_effect)
            
            user1 = User.objects.create_user(
                username='user1',
                email='user1@example.com',
                password='testpass123'
            )
            user2 = User.objects.create_user(
                username='user2',
                email='user2@example.com',
                password='testpass123'
            )
            
            result = signals.send_bulk_notification(
                users=[user1, user2],
                tipo='info',
                titulo='Test Title',
                mensaje='Test Message'
            )
            
            assert result == 1

