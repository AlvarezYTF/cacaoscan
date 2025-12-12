"""
Módulo de medición y calibración para CacaoScan.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: calibrators, storage, converters
- Enfocado exclusivamente en granos de cacao usando pixel_calibration.json
"""

from .gestor_calibracion import (
    GestorCalibracion,
    obtener_gestor_calibracion,
    calibrar_imagen,
    convertir_pixeles_a_mm,
    convertir_mm_a_pixeles
)

from .calibration import (
    CalibrationManager,
    get_calibration_manager,
    calibrate_image,
    convert_pixels_to_mm,
    convert_mm_to_pixels
)

from .models import (
    CalibrationMethod,
    CalibrationResult,
    CalibrationParams
)

__all__ = [
    # Nombres en español
    'GestorCalibracion',
    'obtener_gestor_calibracion',
    'calibrar_imagen',
    'convertir_pixeles_a_mm',
    'convertir_mm_a_pixeles',
    # Compatibilidad hacia atrás
    'CalibrationManager',
    'CalibrationMethod', 
    'CalibrationResult',
    'CalibrationParams',
    'get_calibration_manager',
    'calibrate_image',
    'convert_pixels_to_mm',
    'convert_mm_to_pixels'
]
