"""
Tests for API decorators.
"""
import pytest
from unittest.mock import Mock, patch
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound

from api.utils.decorators import handle_api_errors
from core.utils import create_error_response


class TestView(APIView):
    """Test view for decorator testing."""
    
    @handle_api_errors()
    def get(self, request):
        return Response({'success': True})
    
    @handle_api_errors(
        error_message="Custom error",
        status_code=status.HTTP_400_BAD_REQUEST
    )
    def post(self, request):
        raise ValueError("Test error")
    
    @handle_api_errors(
        log_message="Custom log message",
        exc_info=False
    )
    def put(self, request):
        raise Exception("Test exception")
    
    @handle_api_errors(
        exception_types=(ValueError,)
    )
    def patch(self, request):
        raise ValueError("Value error")
    
    @handle_api_errors(
        exception_types=(ValueError,)
    )
    def delete(self, request):
        raise TypeError("Type error - should not be caught")


@pytest.fixture
def request_factory():
    """Create API request factory."""
    return APIRequestFactory()


@pytest.fixture
def view():
    """Create test view instance."""
    return TestView.as_view()


def test_handle_api_errors_success(view, request_factory):
    """Test decorator with successful request."""
    request = request_factory.get('/api/test/')
    response = view(request)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['success'] is True


def test_handle_api_errors_custom_message(view, request_factory):
    """Test decorator with custom error message."""
    request = request_factory.post('/api/test/')
    response = view(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'message' in response.data or 'error' in response.data


def test_handle_api_errors_log_message(view, request_factory):
    """Test decorator with custom log message."""
    with patch('api.utils.decorators.logger') as mock_logger:
        request = request_factory.put('/api/test/')
        response = view(request)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_logger.error.assert_called_once()


def test_handle_api_errors_exception_types_caught(view, request_factory):
    """Test decorator with specific exception types - caught."""
    request = request_factory.patch('/api/test/')
    response = view(request)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_handle_api_errors_exception_types_not_caught(view, request_factory):
    """Test decorator with specific exception types - not caught."""
    request = request_factory.delete('/api/test/')
    with pytest.raises(TypeError):
        view(request)


def test_handle_api_errors_api_exception(view, request_factory):
    """Test decorator with APIException."""
    class TestViewWithAPIException(APIView):
        @handle_api_errors()
        def get(self, request):
            raise NotFound("Not found")
    
    view_with_exc = TestViewWithAPIException.as_view()
    request = request_factory.get('/api/test/')
    response = view_with_exc(request)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_handle_api_errors_exc_info_true(view, request_factory):
    """Test decorator with exc_info=True."""
    with patch('api.utils.decorators.logger') as mock_logger:
        request = request_factory.post('/api/test/')
        response = view(request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_logger.error.assert_called_once()


def test_handle_api_errors_exc_info_false(view, request_factory):
    """Test decorator with exc_info=False."""
    with patch('api.utils.decorators.logger') as mock_logger:
        request = request_factory.put('/api/test/')
        response = view(request)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_logger.error.assert_called_once()

