"""
Clase base para generadores de recortes.

Este módulo define la clase base abstracta para todos los generadores,
siguiendo el principio de Inversión de Dependencias (DIP).
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Any, Optional

from ml.utils.logs import get_ml_logger
from .procesadores import ProcesadorImagen
from .guardadores import GuardadorRecorte

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.generators")


class GeneradorRecorteBase(ABC):
    """
    Clase base abstracta para generadores de recortes.
    
    Proporciona la estructura común para todos los generadores,
    siguiendo el principio de Responsabilidad Única.
    """
    
    def __init__(self):
        """Inicializa el generador base."""
        self.procesador = ProcesadorImagen()
        self.guardador = GuardadorRecorte()
    
    @abstractmethod
    def generate_crops(
        self,
        records: List[Dict[str, Any]],
        overwrite: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Genera recortes para registros.
        
        Args:
            records: Lista de registros a procesar
            overwrite: Si se deben sobrescribir recortes existentes
            
        Returns:
            Lista de registros con recortes generados
        """
        pass
    
    def _obtener_ruta_imagen(self, record: Dict[str, Any]) -> Optional[Path]:
        """
        Obtiene la ruta de la imagen desde un registro.
        
        Args:
            record: Registro con información de imagen
            
        Returns:
            Ruta de la imagen o None si no existe
        """
        image_path = record.get("image_path") or record.get("original_image_path")
        if not image_path:
            return None
        
        if isinstance(image_path, Path):
            return image_path
        
        return Path(image_path)
    
    def _obtener_ruta_recorte(self, record: Dict[str, Any]) -> Optional[Path]:
        """
        Obtiene la ruta del recorte desde un registro.
        
        Args:
            record: Registro con información de recorte
            
        Returns:
            Ruta del recorte o None si no existe
        """
        crop_path = record.get("crop_image_path")
        if not crop_path:
            return None
        
        if isinstance(crop_path, Path):
            return crop_path
        
        return Path(crop_path)
    
    def _verificar_recorte_existe(
        self,
        crop_path: Path,
        overwrite: bool
    ) -> bool:
        """
        Verifica si un recorte ya existe y si debe sobrescribirse.
        
        Args:
            crop_path: Ruta del recorte
            overwrite: Si se deben sobrescribir recortes existentes
            
        Returns:
            True si el recorte existe y no se debe sobrescribir
        """
        if crop_path.exists() and not overwrite:
            logger.debug(f"Recorte ya existe: {crop_path}")
            return True
        return False

