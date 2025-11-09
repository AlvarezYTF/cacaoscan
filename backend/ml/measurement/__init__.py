"""
Módulo de medición y calibración para CacaoScan.
"""

from .calibration import (
    CalibrationManager,
    CalibrationMethod,
    CalibrationResult,
    CalibrationParams,
    ReferenceObject,
    CoinDetector,
    RulerDetector,
    get_calibration_manager,
    calibrate_image,
    convert_pixels_to_mm,
    convert_mm_to_pixels
)

__all__ = [
    'CalibrationManager',
    'CalibrationMethod', 
    'CalibrationResult',
    'CalibrationParams',
    'ReferenceObject',
    'CoinDetector',
    'RulerDetector',
    'get_calibration_manager',
    'calibrate_image',
    'convert_pixels_to_mm',
    'convert_mm_to_pixels'
]


