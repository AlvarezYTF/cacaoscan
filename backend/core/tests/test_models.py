"""
Tests for Core Models.
"""
import pytest
from django.core.exceptions import ValidationError

from core.models import TimeStampedModel, SystemSettings


@pytest.mark.django_db
class TestTimeStampedModel:
    """Tests for TimeStampedModel abstract model."""

    def test_timestamped_model_is_abstract(self):
        """Test that TimeStampedModel is abstract."""
        assert TimeStampedModel._meta.abstract is True


@pytest.mark.django_db
class TestSystemSettings:
    """Tests for SystemSettings model."""

    def test_create_system_settings(self):
        """Test creating system settings."""
        settings = SystemSettings.objects.create(
            nombre_sistema='Test System',
            email_contacto='test@example.com'
        )
        
        assert settings.nombre_sistema == 'Test System'
        assert settings.email_contacto == 'test@example.com'
        assert settings.pk == 1  # Should always be pk=1

    def test_get_singleton_creates_if_not_exists(self):
        """Test that get_singleton creates instance if it doesn't exist."""
        # Delete any existing instance
        SystemSettings.objects.all().delete()
        
        settings = SystemSettings.get_singleton()
        
        assert settings is not None
        assert settings.pk == 1

    def test_get_singleton_returns_existing(self):
        """Test that get_singleton returns existing instance."""
        SystemSettings.objects.all().delete()
        
        settings1 = SystemSettings.get_singleton()
        settings2 = SystemSettings.get_singleton()
        
        assert settings1.pk == settings2.pk
        assert settings1.id == settings2.id

    def test_save_always_sets_pk_to_1(self):
        """Test that save always sets pk to 1."""
        SystemSettings.objects.all().delete()
        
        settings = SystemSettings(nombre_sistema='Test')
        settings.save()
        
        assert settings.pk == 1
        
        # Try to create another
        settings2 = SystemSettings(nombre_sistema='Test 2')
        settings2.save()
        
        # Should update the existing one
        assert SystemSettings.objects.count() == 1
        assert SystemSettings.objects.first().nombre_sistema == 'Test 2'

    def test_str_representation(self):
        """Test string representation."""
        settings = SystemSettings.get_singleton()
        settings.nombre_sistema = 'Test System'
        settings.save()
        
        assert 'Test System' in str(settings)

    def test_default_values(self):
        """Test default values."""
        SystemSettings.objects.all().delete()
        settings = SystemSettings.get_singleton()
        
        assert settings.nombre_sistema == 'CacaoScan'
        assert settings.recaptcha_enabled is True
        assert settings.session_timeout == 60
        assert settings.login_attempts == 5
        assert settings.two_factor_auth is False
        assert settings.active_model == 'yolov8'

