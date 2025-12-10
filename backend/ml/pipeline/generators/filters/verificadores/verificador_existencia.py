"""
Verificador de existencia de archivos para filtros.

Responsabilidad única: verificar existencia de archivos,
siguiendo el principio de Single Responsibility (SOLID).
"""
from pathlib import Path
from typing import Optional

from ml.utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.filters.verificadores")


class VerificadorExistencia:
    """
    Verificador de existencia de archivos.
    
    Verifica si un archivo o directorio existe en el sistema de archivos.
    """
    
    @staticmethod
    def existe(path: Optional[Path]) -> bool:
        """
        Verifica si un archivo existe.
        
        Args:
            path: Ruta a verificar
            
        Returns:
            True si el archivo existe, False en caso contrario
        """
        if path is None:
            return False
        
        try:
            return path.exists()
        except (OSError, PermissionError) as e:
            logger.warning(f"Error verificando existencia de {path}: {e}")
            return False

