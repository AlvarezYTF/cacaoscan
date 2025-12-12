"""
Mixin for finca views to reduce code duplication in error handling.
"""
import logging
from rest_framework.response import Response
from rest_framework import status
from core.utils import create_error_response

logger = logging.getLogger("cacaoscan.api")

# Error message constants
ERROR_INTERNAL_SERVER = 'Error interno del servidor'
ERROR_INVALID_INPUT = 'Datos de entrada inválidos'
ERROR_FINCA_NOT_FOUND = 'Finca no encontrada'


class FincaErrorMixin:
    """
    Mixin that provides common error handling patterns for finca views.
    """
    
    def handle_finca_not_found(self, finca_id: int = None) -> Response:
        """
        Centralized handling for Finca.DoesNotExist errors.
        
        Args:
            finca_id: Optional finca ID for logging
            
        Returns:
            Response with 404 error
        """
        if finca_id:
            logger.warning(f"Finca {finca_id} no encontrada")
        return create_error_response(
            message=ERROR_FINCA_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND
        )
    
    def handle_finca_error(self, error: Exception, operation_name: str, finca_id: int = None) -> Response:
        """
        Centralized error handling for finca operations.
        
        Args:
            error: The exception that occurred
            operation_name: Name of the operation for logging (e.g., "obteniendo detalles de finca")
            finca_id: Optional finca ID for logging
            
        Returns:
            Response with error details
        """
        log_message = f"Error {operation_name}"
        if finca_id:
            log_message += f" {finca_id}"
        logger.error(f"{log_message}: {error}")
        return create_error_response(
            message=ERROR_INTERNAL_SERVER,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def handle_validation_error(self, errors: dict = None) -> Response:
        """
        Centralized validation error handling.
        
        Args:
            errors: Optional validation errors dictionary
            
        Returns:
            Response with validation error
        """
        return create_error_response(
            message=ERROR_INVALID_INPUT,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=errors
        )

