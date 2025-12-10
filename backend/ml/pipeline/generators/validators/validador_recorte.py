"""
Validador de calidad de recortes para granos de cacao.

Este módulo maneja la validación de calidad de recortes,
siguiendo principios SOLID:
- Single Responsibility: solo validación, no carga ni validaciones específicas
- Dependency Inversion: implementa IValidadorRecorte
"""
from pathlib import Path
from typing import Dict, List, Any, Tuple

from ....utils.logs import get_ml_logger
from .cargadores import CargadorImagen
from .validadores import ValidadorDimensiones, ValidadorCanalAlpha

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.validators")


class ValidadorRecorte:
    """
    Validador de calidad de recortes para granos de cacao.
    
    Responsabilidad única: orquestar la validación de recortes.
    La carga de imágenes está delegada a CargadorImagen (SRP).
    Las validaciones específicas están delegadas a validadores específicos (SRP).
    """
    
    def __init__(
        self,
        min_crop_size: int = 100,
        min_visible_ratio: float = 0.1
    ):
        """
        Inicializa el validador de recortes.
        
        Args:
            min_crop_size: Tamaño mínimo del recorte en píxeles
            min_visible_ratio: Ratio mínimo de píxeles visibles (para imágenes RGBA)
        """
        self.cargador = CargadorImagen()
        self.validador_dimensiones = ValidadorDimensiones(min_crop_size)
        self.validador_alpha = ValidadorCanalAlpha(min_visible_ratio)
    
    def validar_recorte_unico(self, record: Dict[str, Any]) -> bool:
        """
        Valida un recorte individual.
        
        Args:
            record: Registro que contiene crop_image_path
            
        Returns:
            True si el recorte es válido, False en caso contrario
        """
        try:
            crop_path = record.get("crop_image_path")
            if not crop_path:
                return False
            
            crop_path = Path(crop_path) if not isinstance(crop_path, Path) else crop_path
            
            # Cargar imagen
            imagen_rgb = self.cargador.cargar_imagen_rgb(crop_path)
            if imagen_rgb is None:
                return False
            
            # Validar dimensiones
            if not self.validador_dimensiones.validar(imagen_rgb, crop_path.name):
                return False
            
            # Validar canal alpha (si es RGBA)
            if not self.validador_alpha.validar(imagen_rgb, crop_path.name):
                return False
            
            return True
            
        except Exception as e:
            logger.warning(
                f"Error validando recorte {record.get('id', 'desconocido')}: {e}"
            )
            return False
    
    def validar_lote(
        self,
        crop_records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Valida la calidad de recortes para un lote de registros.
        
        Args:
            crop_records: Lista de registros con recortes
            
        Returns:
            Tupla de (registros_válidos, registros_inválidos)
        """
        logger.info("Validando calidad de recortes existentes...")
        registros_inválidos: List[Dict[str, Any]] = []
        registros_válidos: List[Dict[str, Any]] = []
        
        for record in crop_records:
            if self.validar_recorte_unico(record):
                registros_válidos.append(record)
            else:
                registros_inválidos.append(record)
        
        logger.info(
            f"Recortes válidos: {len(registros_válidos)}, "
            f"recortes inválidos: {len(registros_inválidos)}"
        )
        
        return registros_válidos, registros_inválidos
    
    # Métodos de compatibilidad hacia atrás
    def validate_single_crop(self, record: Dict[str, Any]) -> bool:
        """Alias de compatibilidad hacia atrás para validar_recorte_unico."""
        return self.validar_recorte_unico(record)
    
    def validate_batch(
        self,
        crop_records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Alias de compatibilidad hacia atrás para validar_lote."""
        return self.validar_lote(crop_records)


