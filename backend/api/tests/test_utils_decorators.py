"""
Tests for API decorators.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError, NotFound
from api.utils.decorators import handle_api_errors


class MockView:
    """Mock view class for testing decorators."""
    pass


class TestHandleApiErrors:
    """Test cases for handle_api_errors decorator."""
    
    def test_decorator_success_case(self):
        """Test decorator with successful function execution."""
        @handle_api_errors()
        def test_method(self, request):
            return Response({'success': True}, status=status.HTTP_200_OK)
        
        view = MockView()
        result = test_method(view, Mock())
        assert isinstance(result, Response)
        assert result.status_code == status.HTTP_200_OK
        assert result.data['success'] is True
    
    def test_decorator_with_generic_exception(self):
        """Test decorator catching generic exception."""
        @handle_api_errors()
        def test_method(self, request):
            raise Exception('Test error')
        
        view = MockView()
        with patch('api.utils.decorators.create_error_response') as mock_create_error:
            mock_response = Response({}, status=500)
            mock_create_error.return_value = mock_response
            result = test_method(view, Mock())
            assert result == mock_response
            mock_create_error.assert_called_once()
    
    def test_decorator_with_custom_error_message(self):
        """Test decorator with custom error message."""
        @handle_api_errors(error_message='Custom error')
        def test_method(self, request):
            raise Exception('Test error')
        
        view = MockView()
        with patch('api.utils.decorators.create_error_response') as mock_create_error:
            mock_response = Response({}, status=500)
            mock_create_error.return_value = mock_response
            result = test_method(view, Mock())
            mock_create_error.assert_called_once()
            call_args = mock_create_error.call_args
            assert call_args[1]['message'] == 'Custom error'
    
    def test_decorator_with_custom_status_code(self):
        """Test decorator with custom status code."""
        @handle_api_errors(status_code=status.HTTP_400_BAD_REQUEST)
        def test_method(self, request):
            raise Exception('Test error')
        
        view = MockView()
        with patch('api.utils.decorators.create_error_response') as mock_create_error:
            mock_response = Response({}, status=400)
            mock_create_error.return_value = mock_response
            result = test_method(view, Mock())
            mock_create_error.assert_called_once()
            call_args = mock_create_error.call_args
            assert call_args[1]['status_code'] == status.HTTP_400_BAD_REQUEST
    
    def test_decorator_with_custom_log_message(self):
        """Test decorator with custom log message."""
        @handle_api_errors(log_message='Custom log message')
        def test_method(self, request):
            raise Exception('Test error')
        
        view = MockView()
        with patch('api.utils.decorators.logger') as mock_logger:
            with patch('api.utils.decorators.create_error_response') as mock_create_error:
                mock_response = Response({}, status=500)
                mock_create_error.return_value = mock_response
                test_method(view, Mock())
                mock_logger.error.assert_called_once()
                log_call = mock_logger.error.call_args[0][0]
                assert 'Custom log message' in log_call
    
    def test_decorator_with_api_exception(self):
        """Test decorator with APIException."""
        @handle_api_errors()
        def test_method(self, request):
            raise APIException('API error')
        
        view = MockView()
        with patch('api.utils.decorators.create_error_response') as mock_create_error:
            mock_response = Response({}, status=500)
            mock_create_error.return_value = mock_response
            result = test_method(view, Mock())
            mock_create_error.assert_called_once()
            call_args = mock_create_error.call_args
            assert 'API error' in call_args[1]['message']
    
    def test_decorator_with_validation_error(self):
        """Test decorator with ValidationError."""
        @handle_api_errors()
        def test_method(self, request):
            raise ValidationError('Validation error')
        
        view = MockView()
        with patch('api.utils.decorators.create_error_response') as mock_create_error:
            mock_response = Response({}, status=400)
            mock_create_error.return_value = mock_response
            result = test_method(view, Mock())
            mock_create_error.assert_called_once()
    
    def test_decorator_with_not_found_exception(self):
        """Test decorator with NotFound exception."""
        @handle_api_errors()
        def test_method(self, request):
            raise NotFound('Resource not found')
        
        view = MockView()
        with patch('api.utils.decorators.create_error_response') as mock_create_error:
            mock_response = Response({}, status=404)
            mock_create_error.return_value = mock_response
            result = test_method(view, Mock())
            mock_create_error.assert_called_once()
            call_args = mock_create_error.call_args
            assert call_args[1]['status_code'] == 404
    
    def test_decorator_with_exc_info_false(self):
        """Test decorator with exc_info=False."""
        @handle_api_errors(exc_info=False)
        def test_method(self, request):
            raise Exception('Test error')
        
        view = MockView()
        with patch('api.utils.decorators.logger') as mock_logger:
            with patch('api.utils.decorators.create_error_response') as mock_create_error:
                mock_response = Response({}, status=500)
                mock_create_error.return_value = mock_response
                test_method(view, Mock())
                mock_logger.error.assert_called_once()
                # Check that exc_info is not passed or is False
                call_kwargs = mock_logger.error.call_args[1] if mock_logger.error.call_args[1] else {}
                assert call_kwargs.get('exc_info') is not True
    
    def test_decorator_with_exception_types(self):
        """Test decorator with specific exception types."""
        @handle_api_errors(exception_types=(ValueError, TypeError))
        def test_method(self, request):
            raise ValueError('Value error')
        
        view = MockView()
        with patch('api.utils.decorators.create_error_response') as mock_create_error:
            mock_response = Response({}, status=500)
            mock_create_error.return_value = mock_response
            result = test_method(view, Mock())
            mock_create_error.assert_called_once()
    
    def test_decorator_with_unhandled_exception_type(self):
        """Test decorator re-raising unhandled exception types."""
        @handle_api_errors(exception_types=(ValueError,))
        def test_method(self, request):
            raise KeyError('Key error')
        
        view = MockView()
        with pytest.raises(KeyError):
            test_method(view, Mock())
    
    def test_decorator_preserves_function_metadata(self):
        """Test that decorator preserves function metadata."""
        @handle_api_errors()
        def test_method(self, request):
            """Test method docstring."""
            return Response({})
        
        assert test_method.__name__ == 'test_method'
        assert 'Test method docstring' in test_method.__doc__
    
    def test_decorator_with_class_name_in_log(self):
        """Test that class name appears in log message."""
        class TestView:
            pass
        
        @handle_api_errors()
        def test_method(self, request):
            raise Exception('Test error')
        
        view = TestView()
        with patch('api.utils.decorators.logger') as mock_logger:
            with patch('api.utils.decorators.create_error_response') as mock_create_error:
                mock_response = Response({}, status=500)
                mock_create_error.return_value = mock_response
                test_method(view, Mock())
                mock_logger.error.assert_called_once()
                log_call = mock_logger.error.call_args[0][0]
                assert 'TestView' in log_call
                assert 'test_method' in log_call

