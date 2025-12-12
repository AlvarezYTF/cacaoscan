"""
Tests for core models.
"""
import pytest
from django.utils import timezone
from datetime import timedelta

from core.models import TimeStampedModel, SystemSettings


def test_timestamped_model_is_abstract():
    """Test that TimeStampedModel is abstract."""
    assert TimeStampedModel._meta.abstract is True


def test_system_settings_str(db):
    """Test SystemSettings __str__ method."""
    settings = SystemSettings.get_singleton()
    assert 'CacaoScan' in str(settings)


def test_system_settings_get_singleton_creates(db):
    """Test get_singleton creates instance if it doesn't exist."""
    SystemSettings.objects.all().delete()
    settings = SystemSettings.get_singleton()
    
    assert settings is not None
    assert settings.pk == 1


def test_system_settings_get_singleton_returns_existing(db):
    """Test get_singleton returns existing instance."""
    settings1 = SystemSettings.get_singleton()
    settings2 = SystemSettings.get_singleton()
    
    assert settings1.pk == settings2.pk
    assert settings1 == settings2


def test_system_settings_save_forces_pk(db):
    """Test that save forces pk to 1."""
    settings = SystemSettings()
    settings.nombre_sistema = 'Test System'
    settings.save()
    
    assert settings.pk == 1


def test_system_settings_default_values(db):
    """Test SystemSettings default values."""
    settings = SystemSettings.get_singleton()
    
    assert settings.nombre_sistema == 'CacaoScan'
    assert settings.recaptcha_enabled is True
    assert settings.session_timeout == 60
    assert settings.login_attempts == 5
    assert settings.two_factor_auth is False
    assert settings.active_model == 'yolov8'


def test_system_settings_created_at_auto(db):
    """Test that created_at is set automatically."""
    settings = SystemSettings.get_singleton()
    
    assert settings.created_at is not None
    assert isinstance(settings.created_at, timezone.datetime)


def test_system_settings_updated_at_auto(db):
    """Test that updated_at is set automatically."""
    import time
    settings = SystemSettings.get_singleton()
    original_updated = settings.updated_at
    
    # Add a small delay to ensure timestamp difference
    time.sleep(0.01)
    
    settings.nombre_sistema = 'Updated Name'
    settings.save()
    
    # Refresh from database to get updated timestamp
    settings.refresh_from_db()
    
    assert settings.updated_at > original_updated


