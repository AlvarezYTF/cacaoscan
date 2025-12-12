"""
Modelos de datos para calibración.

Este módulo define estructuras de datos y enums para calibración,
siguiendo el principio de Responsabilidad Única.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple

from ..utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.measurement.models")


class CalibrationMethod(Enum):
    """Métodos de calibración disponibles para medición de granos de cacao."""
    DATASET_CALIBRATION = "dataset_calibration"  # Usa pixel_calibration.json (método principal)
    MANUAL_POINTS = "manual_points"  # Puntos manuales para calibración


@dataclass
class CalibrationResult:
    """Resultado de calibración para granos de cacao."""
    success: bool
    pixels_per_mm: float
    confidence: float
    method: CalibrationMethod
    detected_points: List[Tuple[int, int]]
    error_message: Optional[str] = None
    calibration_image_path: Optional[str] = None


@dataclass
class CalibrationParams:
    """Parámetros de calibración para granos de cacao."""
    pixels_per_mm: float
    method: CalibrationMethod
    confidence: float
    timestamp: str
    image_dimensions: Tuple[int, int]
    validation_score: Optional[float] = None

