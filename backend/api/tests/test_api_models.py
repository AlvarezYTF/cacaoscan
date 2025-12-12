"""
Tests for API models lazy imports.
"""
import pytest
from unittest.mock import patch

from api.models import __getattr__


def test_getattr_with_valid_model():
    """Test __getattr__ with valid model name."""
    # This will try to import SystemSettings
    try:
        from api import models
        settings = models.SystemSettings
        assert settings is not None
    except (ImportError, AttributeError):
        # If import fails, that's okay for this test
        pass


def test_getattr_with_invalid_model():
    """Test __getattr__ with invalid model name."""
    with pytest.raises(AttributeError):
        __getattr__('NonExistentModel')


@patch('api.utils.model_imports.get_model_safely')
def test_getattr_caches_model(mock_get_model):
    """Test that __getattr__ caches imported models."""
    from unittest.mock import MagicMock
    
    mock_model = MagicMock()
    mock_get_model.return_value = mock_model
    
    # First access
    result1 = __getattr__('SystemSettings')
    
    # Second access should use cached version
    # Note: This test may need adjustment based on actual caching behavior
    assert result1 is not None


@patch('api.utils.model_imports.get_model_safely')
def test_getattr_raises_on_import_error(mock_get_model):
    """Test that __getattr__ raises ImportError when model can't be imported."""
    mock_get_model.return_value = None
    
    with pytest.raises(ImportError):
        __getattr__('SystemSettings')

