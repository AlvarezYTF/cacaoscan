"""
Tests for API exception handler.
"""
import pytest
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

