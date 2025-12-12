"""
Compatibilidad hacia atrás para CalibrationManager.

Este archivo mantiene compatibilidad con código existente.
La implementación real está en gestor_calibracion.py.
"""

from .gestor_calibracion import (
    GestorCalibracion,
    obtener_gestor_calibracion,
    calibrar_imagen,
    convertir_pixeles_a_mm,
    convertir_mm_a_pixeles
)

# Alias para compatibilidad hacia atrás
CalibrationManager = GestorCalibracion
get_calibration_manager = obtener_gestor_calibracion
calibrate_image = calibrar_imagen
convert_pixels_to_mm = convertir_pixeles_a_mm
convert_mm_to_pixels = convertir_mm_a_pixeles
