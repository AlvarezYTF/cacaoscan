"""
Visualizador de resultados de calibración para granos de cacao.

Este módulo maneja la visualización de resultados de calibración,
siguiendo principios SOLID:
- Single Responsibility: solo visualización, no generación de nombres
- Dependency Inversion: implementa IVisualizadorCalibracion
"""
import cv2
import numpy as np
from pathlib import Path

from ...utils.logs import get_ml_logger
from .generadores import GeneradorNombreArchivo

logger = get_ml_logger("cacaoscan.ml.measurement.visualizers")


class VisualizadorCalibracion:
    """
    Visualizador para resultados de calibración de granos de cacao.
    
    Responsabilidad única: guardar imágenes de calibración.
    La generación de nombres está delegada a GeneradorNombreArchivo (SRP).
    """
    
    def __init__(self):
        """Inicializa el visualizador de calibración."""
        self.generador_nombre = GeneradorNombreArchivo()
    
    def save_calibration_image(
        self,
        image: np.ndarray,
        calibration_dir: Path
    ) -> Path:
        """
        Guarda imagen de calibración.
        
        Args:
            image: Imagen a guardar
            calibration_dir: Directorio para guardar imagen
            
        Returns:
            Ruta a la imagen guardada
        """
        filepath = self.generador_nombre.generar_ruta_archivo(calibration_dir)
        cv2.imwrite(str(filepath), image)
        logger.info(f"Imagen de calibración guardada: {filepath}")
        return filepath

