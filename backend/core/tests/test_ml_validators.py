"""
Tests for ML validation utilities.
"""
import pytest
from unittest.mock import patch, MagicMock
from rest_framework import status

from core.utils.ml_validators import validate_target


@patch('core.utils.ml_validators.TARGETS', ['alto_mm', 'ancho_mm', 'grosor_mm', 'peso_g'])
def test_validate_target_valid():
    """Test validating a valid target."""
    result = validate_target('alto_mm')
    assert result is None


@patch('core.utils.ml_validators.TARGETS', ['alto_mm', 'ancho_mm', 'grosor_mm', 'peso_g'])
def test_validate_target_invalid():
    """Test validating an invalid target."""
    result = validate_target('invalid_target')
    
    assert result is not None
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in result.data
    assert 'target debe ser uno de' in result.data['error']


@patch('core.utils.ml_validators.TARGETS', ['alto_mm', 'ancho_mm', 'grosor_mm', 'peso_g'])
def test_validate_target_none():
    """Test validating None target."""
    result = validate_target(None)
    
    assert result is not None
    assert result.status_code == status.HTTP_400_BAD_REQUEST


@patch('core.utils.ml_validators.TARGETS', ['alto_mm', 'ancho_mm', 'grosor_mm', 'peso_g'])
def test_validate_target_all_valid_targets():
    """Test validating all valid targets."""
    targets = ['alto_mm', 'ancho_mm', 'grosor_mm', 'peso_g']
    
    for target in targets:
        result = validate_target(target)
        assert result is None, f"Target {target} should be valid"


