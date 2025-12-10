"""
Normalizador de rutas para filtros.

Responsabilidad única: normalizar rutas de archivos,
siguiendo el principio de Single Responsibility (SOLID).
"""
from pathlib import Path
from typing import Optional

from ml.utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.filters.normalizadores")


class NormalizadorPath:
    """
    Normalizador de rutas para filtros.
    
    Convierte diferentes tipos de rutas (str, Path) a objetos Path
    consistentes para su procesamiento.
    """
    
    @staticmethod
    def normalizar_path(path_value: Optional[str | Path]) -> Optional[Path]:
        """
        Normaliza un valor de ruta a objeto Path.
        
        Args:
            path_value: Valor de ruta (str, Path o None)
            
        Returns:
            Objeto Path normalizado o None si no hay ruta
        """
        if path_value is None:
            return None
        
        if isinstance(path_value, Path):
            return path_value
        
        try:
            return Path(path_value)
        except (TypeError, ValueError) as e:
            logger.warning(f"Error normalizando ruta {path_value}: {e}")
            return None

