"""
Unit tests for API utils decorators module.
Tests handle_api_errors decorator.
"""
import pytest
from unittest.mock import Mock, patch
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException

from api.utils.decorators import handle_api_errors


class TestHandleApiErrors:
    """Tests for handle_api_errors decorator."""
    
    def test_decorator_handles_exception(self):
        """Test that decorator handles exceptions."""
        @handle_api_errors(error_message="Test error", status_code=500)
        def failing_view(self, request):
            raise ValueError("Something went wrong")
        
        mock_self = Mock()
        mock_request = Mock()
        
        response = failing_view(mock_self, mock_request)
        
        assert isinstance(response, Response)
        assert response.status_code == 500
        assert response.data['success'] is False
        assert "Test error" in response.data['message']
    
    def test_decorator_returns_success_response(self):
        """Test that decorator returns success response when no error."""
        @handle_api_errors()
        def success_view(self, request):
            return Response({"data": "success"}, status=200)
        
        mock_self = Mock()
        mock_request = Mock()
        
        response = success_view(mock_self, mock_request)
        
        assert isinstance(response, Response)
        assert response.status_code == 200
    
    def test_decorator_handles_api_exception(self):
        """Test that decorator handles APIException correctly."""
        @handle_api_errors()
        def api_error_view(self, request):
            raise APIException("API error")
        
        mock_self = Mock()
        mock_request = Mock()
        
        response = api_error_view(mock_self, mock_request)
        
        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def test_decorator_with_custom_status_code(self):
        """Test decorator with custom status code."""
        @handle_api_errors(error_message="Not found", status_code=404)
        def not_found_view(self, request):
            raise ValueError("Resource not found")
        
        mock_self = Mock()
        mock_request = Mock()
        
        response = not_found_view(mock_self, mock_request)
        
        assert response.status_code == 404
    
    def test_decorator_with_exception_types(self):
        """Test decorator with specific exception types."""
        @handle_api_errors(exception_types=(ValueError,))
        def specific_error_view(self, request):
            raise ValueError("Value error")
        
        @handle_api_errors(exception_types=(ValueError,))
        def other_error_view(self, request):
            raise TypeError("Type error")
        
        mock_self = Mock()
        mock_request = Mock()
        
        # ValueError should be caught
        response1 = specific_error_view(mock_self, mock_request)
        assert isinstance(response1, Response)
        
        # TypeError should not be caught
        with pytest.raises(TypeError):
            other_error_view(mock_self, mock_request)
    
    def test_decorator_logs_errors(self):
        """Test that decorator logs errors."""
        @handle_api_errors(log_message="Custom log message", exc_info=True)
        def logging_view(self, request):
            raise ValueError("Error to log")
        
        mock_self = Mock()
        mock_request = Mock()
        
        with patch('api.utils.decorators.logger') as mock_logger:
            response = logging_view(mock_self, mock_request)
            
            mock_logger.error.assert_called_once()
            assert "Custom log message" in str(mock_logger.error.call_args)

