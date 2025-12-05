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
            # Handle area_total alias for backward compatibility
            if 'area_total' in finca_data and 'hectareas' not in finca_data:
                finca_data['hectareas'] = finca_data['area_total']
            
            if is_create:
                # Validate required fields for creation
                # Check if hectareas or area_total is present
                has_hectareas = 'hectareas' in finca_data or 'area_total' in finca_data
                required_fields = ['nombre', 'ubicacion', 'municipio', 'departamento']
                self.validate_required_fields(finca_data, required_fields)
                
                # Validate hectareas separately
                if not has_hectareas:
                    raise ValidationServiceError("Las hectáreas (area_total) son requeridas", details={"field": "hectareas"})
            
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
                from decimal import Decimal
                validations['hectareas'] = {'type': (int, float, Decimal), 'min': 0.01}
            
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

