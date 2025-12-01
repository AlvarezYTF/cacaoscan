"""
ML validation utilities for regression targets.
"""
from typing import Optional
from rest_framework.response import Response
from rest_framework import status

from ml.regression.models import TARGETS
from .response_helpers import create_error_response


def validate_target(target: Optional[str]) -> Optional[Response]:
    """
    Validates that target parameter is one of the valid regression targets.
    
    Args:
        target: Target parameter to validate
        
    Returns:
        Error response if invalid, None if valid
    """
    if target not in TARGETS:
        return create_error_response(
            message=f"target debe ser uno de: {', '.join(TARGETS)}",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    return None

