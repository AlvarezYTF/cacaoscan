"""
Mixin for incremental training views to reduce code duplication.
"""
import logging
from rest_framework.response import Response
from rest_framework import status
from core.utils import create_error_response, create_success_response

logger = logging.getLogger("cacaoscan.api")


class IncrementalViewMixin:
    """
    Mixin that provides common error handling and response patterns for incremental views.
    """
    
    def handle_incremental_error(self, error: Exception, operation_name: str) -> Response:
        """
        Centralized error handling for incremental operations.
        
        Args:
            error: The exception that occurred
            operation_name: Name of the operation for logging (e.g., "entrenamiento incremental")
            
        Returns:
            Response with error details
        """
        logger.error(f"Error en {operation_name}: {str(error)}")
        return create_error_response(
            message=f"Error interno en {operation_name}",
            details={"error": str(error)},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def handle_validation_error(self, message: str) -> Response:
        """
        Centralized validation error handling.
        
        Args:
            message: Validation error message
            
        Returns:
            Response with validation error
        """
        return create_error_response(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST
        )

