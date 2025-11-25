"""
Validation service for finca management.
Handles finca data validation.
"""
import logging
from typing import Dict, Any

from api.services.base import BaseService, ValidationServiceError

logger = logging.getLogger("cacaoscan.services.fincas.validation")


class FincaValidationService(BaseService):
    """
    Service for handling finca data validation.
    """
    
    def __init__(self):
        super().__init__()
    
    def validate_finca_data(self, finca_data: Dict[str, Any], is_create: bool = True) -> Dict[str, Any]:
        """
        Validates finca data.
        
        Args:
            finca_data: Finca data to validate
            is_create: Whether this is for creation (requires all fields) or update
            
        Returns:
            Dict with 'valid' (bool) and 'error' (str) if invalid
        """
        try:
            if is_create:
                # Validate required fields for creation
                required_fields = ['nombre', 'ubicacion', 'municipio', 'departamento', 'hectareas']
                self.validate_required_fields(finca_data, required_fields)
            
            # Validate field values
            validations = {}
            if 'nombre' in finca_data:
                validations['nombre'] = {'min_length': 2, 'max_length': 200}
            if 'ubicacion' in finca_data:
                validations['ubicacion'] = {'min_length': 5, 'max_length': 300}
            if 'municipio' in finca_data:
                validations['municipio'] = {'min_length': 2, 'max_length': 100}
            if 'departamento' in finca_data:
                validations['departamento'] = {'min_length': 2, 'max_length': 100}
            if 'hectareas' in finca_data:
                validations['hectareas'] = {'type': (int, float), 'min': 0.01}
            
            if validations:
                self.validate_field_values(finca_data, validations)
            
            return {'valid': True}
            
        except ValidationServiceError as e:
            return {
                'valid': False,
                'error': str(e),
                'details': getattr(e, 'details', {})
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f"Error de validación: {str(e)}",
                'details': {}
            }

