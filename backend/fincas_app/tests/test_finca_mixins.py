"""
Tests for finca mixins.
"""
import pytest
from unittest.mock import Mock, patch
from rest_framework.test import APIRequestFactory
from rest_framework import status
from django.contrib.auth.models import User

from fincas_app.views.finca.mixins.finca_error_mixin import FincaErrorMixin
from fincas_app.views.finca.mixins.finca_serializer_mixin import FincaSerializerMixin


@pytest.fixture
def request_factory():
    """Create API request factory."""
    return APIRequestFactory()


@pytest.fixture
def user(db):
    """Create test user with unique username and email."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    return User.objects.create_user(
        username=f'testuser_{unique_id}',
        email=f'test_{unique_id}@example.com',
        password='testpass123'
    )


@pytest.fixture
def finca(user, municipio):
    """Create test finca."""
    from fincas_app.models import Finca
    from decimal import Decimal
    return Finca.objects.create(
        nombre='Test Finca',
        ubicacion='Test Location',
        municipio=municipio,
        hectareas=Decimal('10.5'),
        agricultor=user,
        activa=True
    )


class TestFincaErrorMixin:
    """Tests for FincaErrorMixin class."""
    
    def test_handle_finca_not_found(self, request_factory):
        """Test handle_finca_not_found method."""
        mixin = FincaErrorMixin()
        response = mixin.handle_finca_not_found(finca_id=1)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'error' in response.data or 'message' in response.data
    
    def test_handle_finca_not_found_no_id(self, request_factory):
        """Test handle_finca_not_found without finca_id."""
        mixin = FincaErrorMixin()
        response = mixin.handle_finca_not_found()
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_handle_finca_error(self, request_factory):
        """Test handle_finca_error method."""
        mixin = FincaErrorMixin()
        error = Exception("Test error")
        response = mixin.handle_finca_error(error, "test operation", finca_id=1)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_handle_finca_error_no_id(self, request_factory):
        """Test handle_finca_error without finca_id."""
        mixin = FincaErrorMixin()
        error = Exception("Test error")
        response = mixin.handle_finca_error(error, "test operation")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_handle_validation_error(self, request_factory):
        """Test handle_validation_error method."""
        mixin = FincaErrorMixin()
        errors = {'field1': ['Error 1']}
        response = mixin.handle_validation_error(errors)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_handle_validation_error_no_errors(self, request_factory):
        """Test handle_validation_error without errors."""
        mixin = FincaErrorMixin()
        response = mixin.handle_validation_error()
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestFincaSerializerMixin:
    """Tests for FincaSerializerMixin class."""
    
    def test_get_finca_with_error_handling(self, request_factory, finca):
        """Test get_finca_with_error_handling method."""
        mixin = FincaSerializerMixin()
        mixin.request = request_factory.get('/')
        mixin.get_queryset = Mock(return_value=type('QuerySet', (), {
            'get': Mock(return_value=finca)
        })())
        
        result_finca, error_response = mixin.get_finca_with_error_handling(finca.id)
        assert result_finca == finca
        assert error_response is None
    
    def test_get_finca_with_error_handling_not_found(self, request_factory):
        """Test get_finca_with_error_handling with finca not found."""
        from fincas_app.models import Finca
        mixin = FincaSerializerMixin()
        mixin.request = request_factory.get('/')
        mixin.get_queryset = Mock(return_value=type('QuerySet', (), {
            'get': Mock(side_effect=Finca.DoesNotExist())
        })())
        mixin.handle_finca_not_found = Mock(return_value=Mock(status_code=404))
        
        result_finca, error_response = mixin.get_finca_with_error_handling(99999)
        assert result_finca is None
        assert error_response is not None
    
    def test_get_finca_with_error_handling_exception(self, request_factory):
        """Test get_finca_with_error_handling with exception."""
        mixin = FincaSerializerMixin()
        mixin.request = request_factory.get('/')
        mixin.get_queryset = Mock(return_value=type('QuerySet', (), {
            'get': Mock(side_effect=Exception("Error"))
        })())
        mixin.handle_finca_error = Mock(return_value=Mock(status_code=500))
        
        result_finca, error_response = mixin.get_finca_with_error_handling(1)
        assert result_finca is None
        assert error_response is not None
    
    def test_serialize_finca_response(self, request_factory, finca):
        """Test serialize_finca_response method."""
        from api.serializers import FincaSerializer
        mixin = FincaSerializerMixin()
        mixin.request = request_factory.get('/')
        
        response = mixin.serialize_finca_response(finca)
        assert response.status_code == status.HTTP_200_OK
        assert 'id' in response.data or 'nombre' in response.data
    
    def test_serialize_finca_response_with_success(self, request_factory, finca):
        """Test serialize_finca_response with include_success."""
        from api.serializers import FincaSerializer
        mixin = FincaSerializerMixin()
        mixin.request = request_factory.get('/')
        
        response = mixin.serialize_finca_response(finca, include_success=True)
        assert response.status_code == status.HTTP_200_OK
    
    def test_create_finca_response(self, request_factory, finca):
        """Test create_finca_response method."""
        from api.serializers import FincaSerializer
        mixin = FincaSerializerMixin()
        mixin.request = request_factory.get('/')
        
        response = mixin.create_finca_response(finca)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'success' in response.data or 'finca' in response.data
    
    def test_update_finca_response(self, request_factory, finca):
        """Test update_finca_response method."""
        from api.serializers import FincaSerializer
        mixin = FincaSerializerMixin()
        mixin.request = request_factory.get('/')
        
        response = mixin.update_finca_response(finca)
        assert response.status_code == status.HTTP_200_OK
        assert 'success' in response.data or 'finca' in response.data


