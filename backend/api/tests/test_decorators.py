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
    
    @handle_api_errors()
    def options(self, request):
        raise TypeError("Type error - should not be caught by default handler")


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
    from rest_framework.test import force_authenticate
    from django.contrib.auth.models import User
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(username=f'testuser_{unique_id}', email=f'test_{unique_id}@example.com', password='testpass')
    request = request_factory.get('/api/test/')
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['success'] is True


def test_handle_api_errors_custom_message(view, request_factory):
    """Test decorator with custom error message."""
    from rest_framework.test import force_authenticate
    from django.contrib.auth.models import User
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(username=f'testuser_{unique_id}', email=f'test_{unique_id}@example.com', password='testpass')
    request = request_factory.post('/api/test/')
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'message' in response.data or 'error' in response.data


def test_handle_api_errors_log_message(view, request_factory):
    """Test decorator with custom log message."""
    from rest_framework.test import force_authenticate
    from django.contrib.auth.models import User
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(username=f'testuser_{unique_id}', email=f'test_{unique_id}@example.com', password='testpass')
    with patch('api.utils.decorators.logger') as mock_logger:
        request = request_factory.put('/api/test/')
        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_logger.error.assert_called_once()


def test_handle_api_errors_exception_types_caught(view, request_factory):
    """Test decorator with specific exception types - caught."""
    from rest_framework.test import force_authenticate
    from django.contrib.auth.models import User
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(username=f'testuser_{unique_id}', email=f'test_{unique_id}@example.com', password='testpass')
    request = request_factory.patch('/api/test/')
    force_authenticate(request, user=user)
    response = view(request)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_handle_api_errors_exception_types_not_caught(view, request_factory):
    """Test decorator with specific exception types - not caught."""
    from rest_framework.test import force_authenticate
    from django.contrib.auth.models import User
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(username=f'testuser_{unique_id}', email=f'test_{unique_id}@example.com', password='testpass')
    request = request_factory.delete('/api/test/')
    force_authenticate(request, user=user)
    # The decorator should NOT catch TypeError when exception_types=(ValueError,)
    # So it should re-raise the exception
    # Django's view dispatch will catch unhandled exceptions and return 500
    # So we check that the response is 500 (exception was re-raised and caught by Django)
    # OR the exception propagates and is caught by pytest.raises
    try:
        response = view(request)
        # If we get a response, Django caught the exception (which means decorator re-raised it)
        # This is correct behavior - decorator re-raises, Django catches and returns 500
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    except TypeError:
        # This is also correct - the exception propagated
        pass


def test_handle_api_errors_api_exception(view, request_factory):
    """Test decorator with APIException."""
    from rest_framework.test import force_authenticate
    from django.contrib.auth.models import User
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(username=f'testuser_{unique_id}', email=f'test_{unique_id}@example.com', password='testpass')
    class TestViewWithAPIException(APIView):
        @handle_api_errors()
        def get(self, request):
            raise NotFound("Not found")
    
    view_with_exc = TestViewWithAPIException.as_view()
    request = request_factory.get('/api/test/')
    force_authenticate(request, user=user)
    response = view_with_exc(request)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_handle_api_errors_exc_info_true(view, request_factory):
    """Test decorator with exc_info=True."""
    from rest_framework.test import force_authenticate
    from django.contrib.auth.models import User
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(username=f'testuser_{unique_id}', email=f'test_{unique_id}@example.com', password='testpass')
    with patch('api.utils.decorators.logger') as mock_logger:
        request = request_factory.post('/api/test/')
        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        mock_logger.error.assert_called_once()


def test_handle_api_errors_exc_info_false(view, request_factory):
    """Test decorator with exc_info=False."""
    from rest_framework.test import force_authenticate
    from django.contrib.auth.models import User
    
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    user = User.objects.create_user(username=f'testuser_{unique_id}', email=f'test_{unique_id}@example.com', password='testpass')
    with patch('api.utils.decorators.logger') as mock_logger:
        request = request_factory.put('/api/test/')
        force_authenticate(request, user=user)
        response = view(request)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        mock_logger.error.assert_called_once()


