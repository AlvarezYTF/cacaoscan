"""
Generador de nombres de archivo para imágenes de calibración.

Responsabilidad única: generar nombres de archivo únicos,
siguiendo el principio de Single Responsibility (SOLID).
"""
import time
from pathlib import Path

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.measurement.visualizers.generadores")


class GeneradorNombreArchivo:
    """
    Generador de nombres de archivo para imágenes de calibración.
    
    Genera nombres únicos basados en timestamp para evitar
    colisiones de archivos.
    """
    
    PREFIJO_ARCHIVO: str = "calibration"
    EXTENSION_ARCHIVO: str = ".jpg"
    
    @staticmethod
    def generar_nombre_archivo() -> str:
        """
        Genera un nombre de archivo único para imagen de calibración.
        
        Returns:
            Nombre de archivo con formato: calibration_{timestamp}.jpg
        """
        timestamp = int(time.time())
        return f"{GeneradorNombreArchivo.PREFIJO_ARCHIVO}_{timestamp}{GeneradorNombreArchivo.EXTENSION_ARCHIVO}"
    
    @staticmethod
    def generar_ruta_archivo(calibration_dir: Path) -> Path:
        """
        Genera la ruta completa del archivo de calibración.
        
        Args:
            calibration_dir: Directorio donde se guardará el archivo
            
        Returns:
            Ruta completa del archivo
        """
        nombre_archivo = GeneradorNombreArchivo.generar_nombre_archivo()
        return calibration_dir / nombre_archivo

