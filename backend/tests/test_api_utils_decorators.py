"""
Tests unitarios para api.utils.decorators.

Cubre el decorador handle_api_errors con todos sus casos:
- Manejo de excepciones normales
- Manejo de APIException
- Filtrado por tipo de excepción
- Logging con y sin exc_info
- Mensajes de error personalizados
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException, NotFound, ValidationError as DRFValidationError

from api.utils.decorators import handle_api_errors


class TestView:
    """Mock view class for testing decorators."""
    
    def __init__(self):
        self.response_data = None
    
    @handle_api_errors()
    def method_with_defaults(self, request):
        """Test method with default error handling."""
        raise Exception("Test error")
    
    @handle_api_errors(
        error_message="Custom error message",
        status_code=status.HTTP_400_BAD_REQUEST
    )
    def method_with_custom_message(self, request):
        """Test method with custom error message."""
        raise Exception("Test error")
    
    @handle_api_errors(
        log_message="Custom log message",
        exc_info=False
    )
    def method_with_custom_logging(self, request):
        """Test method with custom logging."""
        raise Exception("Test error")
    
    @handle_api_errors(
        exception_types=(ValueError, TypeError)
    )
    def method_with_filtered_exceptions(self, request):
        """Test method with filtered exceptions."""
        raise ValueError("Filtered error")
    
    @handle_api_errors(
        exception_types=(ValueError,)
    )
    def method_with_unfiltered_exception(self, request):
        """Test method that raises exception not in filter."""
        raise KeyError("Not filtered error")
    
    @handle_api_errors()
    def method_with_api_exception(self, request):
        """Test method that raises APIException."""
        raise NotFound("Resource not found")
    
    @handle_api_errors()
    def method_success(self, request):
        """Test method that succeeds."""
        return Response({"success": True}, status=status.HTTP_200_OK)
    
    @handle_api_errors(
        error_message="Validation error",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )
    def method_with_drf_validation_error(self, request):
        """Test method with DRF ValidationError."""
        raise DRFValidationError({"field": ["Invalid value"]})


class DecoratorsTestCase(TestCase):
    """Tests para el decorador handle_api_errors."""

    def setUp(self):
        """Set up test fixtures."""
        self.view = TestView()
        self.mock_request = MagicMock()

    @patch('api.utils.decorators.logger')
    @patch('api.utils.decorators.create_error_response')
    def test_handle_api_errors_defaults(self, mock_create_response, mock_logger):
        """Test handle_api_errors with default parameters."""
        mock_response = Response(
            {"success": False, "message": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        mock_create_response.return_value = mock_response
        
        result = self.view.method_with_defaults(self.mock_request)
        
        self.assertIsInstance(result, Response)
        mock_create_response.assert_called_once()
        mock_logger.error.assert_called_once()
        
        # Check that exc_info=True was used (default)
        call_args = mock_logger.error.call_args
        self.assertIn('exc_info', call_args.kwargs)
        self.assertTrue(call_args.kwargs['exc_info'])

    @patch('api.utils.decorators.logger')
    @patch('api.utils.decorators.create_error_response')
    def test_handle_api_errors_custom_message(self, mock_create_response, mock_logger):
        """Test handle_api_errors with custom error message."""
        mock_response = Response({}, status=status.HTTP_400_BAD_REQUEST)
        mock_create_response.return_value = mock_response
        
        result = self.view.method_with_custom_message(self.mock_request)
        
        mock_create_response.assert_called_once()
        call_args = mock_create_response.call_args
        self.assertEqual(call_args.kwargs['message'], "Custom error message")
        self.assertEqual(call_args.kwargs['status_code'], status.HTTP_400_BAD_REQUEST)

    @patch('api.utils.decorators.logger')
    @patch('api.utils.decorators.create_error_response')
    def test_handle_api_errors_custom_logging(self, mock_create_response, mock_logger):
        """Test handle_api_errors with custom logging."""
        mock_response = Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        mock_create_response.return_value = mock_response
        
        self.view.method_with_custom_logging(self.mock_request)
        
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        self.assertIn("Custom log message", call_args[0][0])
        # Check that exc_info=False was used
        self.assertFalse(call_args.kwargs.get('exc_info', True))

    @patch('api.utils.decorators.logger')
    @patch('api.utils.decorators.create_error_response')
    def test_handle_api_errors_filtered_exception(self, mock_create_response, mock_logger):
        """Test handle_api_errors catches filtered exception types."""
        mock_response = Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        mock_create_response.return_value = mock_response
        
        result = self.view.method_with_filtered_exceptions(self.mock_request)
        
        # Should catch ValueError
        mock_create_response.assert_called_once()
        mock_logger.error.assert_called_once()

    @patch('api.utils.decorators.logger')
    def test_handle_api_errors_unfiltered_exception_raises(self, mock_logger):
        """Test handle_api_errors re-raises unfiltered exceptions."""
        # KeyError is not in the filter (ValueError, TypeError)
        with self.assertRaises(KeyError):
            self.view.method_with_unfiltered_exception(self.mock_request)
        
        # Should not log or handle the exception
        mock_logger.error.assert_not_called()

    @patch('api.utils.decorators.logger')
    @patch('api.utils.decorators.create_error_response')
    def test_handle_api_errors_api_exception(self, mock_create_response, mock_logger):
        """Test handle_api_errors handles APIException correctly."""
        mock_response = Response({}, status=status.HTTP_404_NOT_FOUND)
        mock_create_response.return_value = mock_response
        
        result = self.view.method_with_api_exception(self.mock_request)
        
        mock_create_response.assert_called_once()
        call_args = mock_create_response.call_args
        
        # Should use APIException's status_code
        self.assertEqual(call_args.kwargs['status_code'], status.HTTP_404_NOT_FOUND)
        # Should use APIException's detail as message
        self.assertIn("Resource not found", call_args.kwargs['message'])

    @patch('api.utils.decorators.logger')
    @patch('api.utils.decorators.create_error_response')
    def test_handle_api_errors_success_no_error(self, mock_create_response, mock_logger):
        """Test handle_api_errors doesn't interfere with successful execution."""
        result = self.view.method_success(self.mock_request)
        
        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data["success"], True)
        
        # Should not create error response or log
        mock_create_response.assert_not_called()
        mock_logger.error.assert_not_called()

    @patch('api.utils.decorators.logger')
    @patch('api.utils.decorators.create_error_response')
    def test_handle_api_errors_drf_validation_error(self, mock_create_response, mock_logger):
        """Test handle_api_errors with DRF ValidationError."""
        mock_response = Response({}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        mock_create_response.return_value = mock_response
        
        result = self.view.method_with_drf_validation_error(self.mock_request)
        
        mock_create_response.assert_called_once()
        call_args = mock_create_response.call_args
        
        # Should use custom status code
        self.assertEqual(call_args.kwargs['status_code'], status.HTTP_422_UNPROCESSABLE_ENTITY)
        # Should extract message from ValidationError
        self.assertIn("Validation error", call_args.kwargs['message'])

    @patch('api.utils.decorators.logger')
    @patch('api.utils.decorators.create_error_response')
    def test_handle_api_errors_logs_class_and_method_name(self, mock_create_response, mock_logger):
        """Test that error log includes class and method name."""
        mock_response = Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        mock_create_response.return_value = mock_response
        
        self.view.method_with_defaults(self.mock_request)
        
        mock_logger.error.assert_called_once()
        log_message = mock_logger.error.call_args[0][0]
        self.assertIn("TestView", log_message)
        self.assertIn("method_with_defaults", log_message)

    @patch('api.utils.decorators.logger')
    @patch('api.utils.decorators.create_error_response')
    def test_handle_api_errors_includes_error_type(self, mock_create_response, mock_logger):
        """Test that error response includes error type."""
        mock_response = Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        mock_create_response.return_value = mock_response
        
        self.view.method_with_defaults(self.mock_request)
        
        mock_create_response.assert_called_once()
        call_args = mock_create_response.call_args
        self.assertEqual(call_args.kwargs['error_type'], 'Exception')

    @patch('api.utils.decorators.logger')
    @patch('api.utils.decorators.create_error_response')
    def test_handle_api_errors_includes_details_for_non_api_exception(self, mock_create_response, mock_logger):
        """Test that details are included for non-APIException."""
        mock_response = Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        mock_create_response.return_value = mock_response
        
        self.view.method_with_defaults(self.mock_request)
        
        call_args = mock_create_response.call_args
        self.assertIsNotNone(call_args.kwargs.get('details'))
        self.assertIn('error', call_args.kwargs['details'])

    @patch('api.utils.decorators.logger')
    @patch('api.utils.decorators.create_error_response')
    def test_handle_api_errors_no_details_for_api_exception(self, mock_create_response, mock_logger):
        """Test that details are None for APIException."""
        mock_response = Response({}, status=status.HTTP_404_NOT_FOUND)
        mock_create_response.return_value = mock_response
        
        self.view.method_with_api_exception(self.mock_request)
        
        call_args = mock_create_response.call_args
        self.assertIsNone(call_args.kwargs.get('details'))

