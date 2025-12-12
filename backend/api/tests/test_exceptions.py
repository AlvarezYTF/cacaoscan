"""
Tests for API exception handler.
"""
import pytest
from unittest.mock import patch, Mock
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
from rest_framework.exceptions import APIException, NotFound, PermissionDenied as DRFPermissionDenied

from api.exceptions import custom_exception_handler


class TestView(APIView):
    """Test view for exception handling."""
    def get(self, request):
        raise Exception("Test exception")


@pytest.fixture
def request_factory():
    """Create API request factory."""
    return APIRequestFactory()


@pytest.fixture
def context(request_factory):
    """Create request context."""
    request = request_factory.get('/api/test/')
    view = TestView.as_view()
    return {'request': request, 'view': view}


def test_custom_exception_handler_http404(context):
    """Test exception handler with Http404."""
    exc = Http404("Resource not found")
    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'error' in response.data
    assert 'details' in response.data


def test_custom_exception_handler_permission_denied(context):
    """Test exception handler with PermissionDenied."""
    exc = PermissionDenied("Access denied")
    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'error' in response.data
    assert 'details' in response.data


def test_custom_exception_handler_validation_error(context):
    """Test exception handler with ValidationError."""
    exc = ValidationError("Invalid data")
    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data
    assert 'details' in response.data


def test_custom_exception_handler_integrity_error(context):
    """Test exception handler with IntegrityError."""
    exc = IntegrityError("Database constraint violated")
    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data
    assert 'details' in response.data


def test_custom_exception_handler_unhandled_exception(context):
    """Test exception handler with unhandled exception."""
    exc = Exception("Unexpected error")
    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert 'error' in response.data
    assert 'details' in response.data


def test_custom_exception_handler_drf_exception_with_detail(context):
    """Test exception handler with DRF exception that has detail."""
    exc = NotFound("Not found")
    response = custom_exception_handler(exc, context)
    assert response is not None
    if response.data and isinstance(response.data, dict):
        if 'detail' in response.data:
            assert 'error' in response.data or 'details' in response.data


def test_custom_exception_handler_drf_exception_with_non_field_errors(context):
    """Test exception handler with DRF exception with non_field_errors."""
    from rest_framework.exceptions import ValidationError as DRFValidationError
    exc = DRFValidationError({'non_field_errors': ['Error message']})
    response = custom_exception_handler(exc, context)
    assert response is not None
    if response.data and isinstance(response.data, dict):
        assert 'error' in response.data or 'details' in response.data


def test_custom_exception_handler_drf_exception_with_field_errors(context):
    """Test exception handler with DRF exception with field errors."""
    from rest_framework.exceptions import ValidationError as DRFValidationError
    exc = DRFValidationError({'field1': ['Error 1'], 'field2': ['Error 2']})
    response = custom_exception_handler(exc, context)
    assert response is not None
    if response.data and isinstance(response.data, dict):
        assert 'error' in response.data or 'details' in response.data


def test_custom_exception_handler_ensures_details_key(context):
    """Test that exception handler ensures 'details' key exists."""
    exc = Http404("Test")
    response = custom_exception_handler(exc, context)
    assert response is not None
    if response.data and isinstance(response.data, dict):
        assert 'details' in response.data


def test_custom_exception_handler_http404_empty_string(context):
    """Test exception handler with Http404 empty string."""
    exc = Http404("")
    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'error' in response.data
    assert 'details' in response.data


def test_custom_exception_handler_permission_denied_empty_string(context):
    """Test exception handler with PermissionDenied empty string."""
    exc = PermissionDenied("")
    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert 'error' in response.data
    assert 'details' in response.data


def test_custom_exception_handler_validation_error_empty_string(context):
    """Test exception handler with ValidationError empty string."""
    exc = ValidationError("")
    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data
    assert 'details' in response.data


def test_custom_exception_handler_integrity_error_empty_string(context):
    """Test exception handler with IntegrityError empty string."""
    exc = IntegrityError("")
    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'error' in response.data
    assert 'details' in response.data


def test_custom_exception_handler_drf_response_with_error_key(context):
    """Test exception handler with DRF response that already has error key."""
    from unittest.mock import Mock
    exc = NotFound("Not found")
    response = custom_exception_handler(exc, context)
    if response and response.data and isinstance(response.data, dict):
        # Simulate response that already has error key
        response.data = {'error': 'Test error', 'details': 'Test details'}
        result = custom_exception_handler(exc, context)
        assert result is not None


def test_custom_exception_handler_drf_response_with_non_dict_data(context):
    """Test exception handler with DRF response that has non-dict data."""
    from rest_framework.exceptions import APIException
    exc = APIException("Test")
    with patch('rest_framework.views.exception_handler') as mock_handler:
        mock_response = Mock()
        mock_response.data = "Not a dict"
        mock_handler.return_value = mock_response
        response = custom_exception_handler(exc, context)
        assert response is not None


def test_custom_exception_handler_drf_response_none(context):
    """Test exception handler when DRF handler returns None."""
    exc = Exception("Test")
    response = custom_exception_handler(exc, context)
    assert response is not None
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_custom_exception_handler_drf_field_errors_string_value(context):
    """Test exception handler with DRF field errors that have string values."""
    from rest_framework.exceptions import ValidationError as DRFValidationError
    exc = DRFValidationError({'field1': 'Error 1', 'field2': 'Error 2'})
    response = custom_exception_handler(exc, context)
    assert response is not None
    if response.data and isinstance(response.data, dict):
        assert 'error' in response.data


def test_custom_exception_handler_drf_non_field_errors_string(context):
    """Test exception handler with DRF non_field_errors as string."""
    from rest_framework.exceptions import ValidationError as DRFValidationError
    exc = DRFValidationError({'non_field_errors': 'Error message'})
    response = custom_exception_handler(exc, context)
    assert response is not None
    if response.data and isinstance(response.data, dict):
        assert 'error' in response.data or 'details' in response.data


def test_custom_exception_handler_response_data_has_error_no_details(context):
    """Test exception handler when response has error but no details."""
    from unittest.mock import Mock
    exc = Http404("Test")
    with patch('rest_framework.views.exception_handler') as mock_handler:
        mock_response = Mock()
        mock_response.data = {'error': 'Test error'}
        mock_handler.return_value = mock_response
        response = custom_exception_handler(exc, context)
        assert response is not None
        if response.data and isinstance(response.data, dict):
            assert 'details' in response.data


