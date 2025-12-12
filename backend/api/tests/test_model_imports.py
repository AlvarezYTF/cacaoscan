"""
Tests for model import utilities.
"""
import pytest
from unittest.mock import patch, MagicMock

from api.utils.model_imports import get_model_safely, get_models_safely


def test_get_model_safely_valid():
    """Test getting a valid model."""
    # Test with a real Django model
    result = get_model_safely('django.contrib.auth.models.User')
    
    assert result is not None
    from django.contrib.auth.models import User
    assert result == User


def test_get_model_safely_invalid_module():
    """Test getting a model from invalid module."""
    result = get_model_safely('nonexistent.module.Model')
    
    assert result is None


def test_get_model_safely_invalid_class():
    """Test getting a non-existent class from valid module."""
    result = get_model_safely('django.contrib.auth.models.NonExistentModel')
    
    assert result is None


def test_get_model_safely_invalid_path():
    """Test getting a model with invalid path format."""
    result = get_model_safely('invalid_path')
    
    assert result is None


def test_get_model_safely_empty_path():
    """Test getting a model with empty path."""
    result = get_model_safely('')
    
    assert result is None


@patch('api.utils.model_imports.importlib.import_module')
def test_get_model_safely_import_error(mock_import):
    """Test getting a model when import fails."""
    mock_import.side_effect = ImportError("Module not found")
    
    result = get_model_safely('test.module.Model')
    
    assert result is None


@patch('api.utils.model_imports.importlib.import_module')
def test_get_model_safely_attribute_error(mock_import):
    """Test getting a model when attribute doesn't exist."""
    mock_module = MagicMock()
    del mock_module.Model
    mock_import.return_value = mock_module
    
    result = get_model_safely('test.module.Model')
    
    assert result is None


def test_get_models_safely_valid():
    """Test getting multiple valid models."""
    model_paths = {
        'User': 'django.contrib.auth.models.User',
        'Group': 'django.contrib.auth.models.Group'
    }
    
    result = get_models_safely(model_paths)
    
    assert 'User' in result
    assert 'Group' in result
    assert result['User'] is not None
    assert result['Group'] is not None


def test_get_models_safely_mixed():
    """Test getting models with some valid and some invalid."""
    model_paths = {
        'User': 'django.contrib.auth.models.User',
        'Invalid': 'nonexistent.module.Model'
    }
    
    result = get_models_safely(model_paths)
    
    assert 'User' in result
    assert 'Invalid' in result
    assert result['User'] is not None
    assert result['Invalid'] is None


def test_get_models_safely_empty():
    """Test getting models with empty dictionary."""
    result = get_models_safely({})
    
    assert result == {}


def test_get_models_safely_all_invalid():
    """Test getting models when all are invalid."""
    model_paths = {
        'Model1': 'nonexistent.module.Model1',
        'Model2': 'nonexistent.module.Model2'
    }
    
    result = get_models_safely(model_paths)
    
    assert 'Model1' in result
    assert 'Model2' in result
    assert result['Model1'] is None
    assert result['Model2'] is None


