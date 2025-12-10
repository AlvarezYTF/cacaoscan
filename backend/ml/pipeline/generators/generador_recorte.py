"""
Generador de recortes para imágenes de granos de cacao.

REFACTORIZADO: Aplicando principios SOLID
- Separación de responsabilidades: filters, validators, generators
- Dependency Inversion: implementa IGeneradorRecorte
- Mantiene compatibilidad hacia atrás con la API original
"""
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from ...utils.logs import get_ml_logger
from .filters import FiltroRecorte
from .validators import CropValidator
from .generators import GeneradorRecorteSegmentado, GeneradorRecorteSimple
from .interfaces import IGeneradorRecorte

logger = get_ml_logger("cacaoscan.ml.pipeline.generators")


class GeneradorRecorte(IGeneradorRecorte):
    """
    Generador de imágenes recortadas a partir de imágenes crudas de granos de cacao.
    
    Esta clase orquesta:
    - Filtrado de registros por disponibilidad de recortes
    - Validación de recortes existentes
    - Generación de recortes faltantes
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    def __init__(
        self,
        segmentation_backend: str = "auto",
        min_crop_size: int = 100,
        min_visible_ratio: float = 0.1
    ):
        """
        Inicializa el generador de recortes.
        
        Args:
            segmentation_backend: Método de segmentación ("auto", "ai", "opencv", "rembg")
            min_crop_size: Tamaño mínimo del recorte en píxeles
            min_visible_ratio: Ratio mínimo de píxeles visibles (para imágenes RGBA)
        """
        # Inicializar componentes
        self.crop_filter = FiltroRecorte()
        self.crop_validator = CropValidator(min_crop_size, min_visible_ratio)
        self.segmented_generator = GeneradorRecorteSegmentado(segmentation_backend)
        self.simple_generator = GeneradorRecorteSimple()
        
        logger.info(
            f"GeneradorRecorte inicializado (método={segmentation_backend}, "
            f"tamaño_mín={min_crop_size}, visible_mín={min_visible_ratio})"
        )
    
    def filter_records_by_crops(
        self,
        valid_records: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Filtra registros por disponibilidad de recortes.
        
        Args:
            valid_records: Lista de registros a filtrar
            
        Returns:
            Tupla de (registros_con_recortes, registros_sin_recortes)
        """
        return self.crop_filter.filter_by_crops(valid_records)
    
    def validate_single_crop(self, record: Dict[str, Any]) -> bool:
        """
        Valida un recorte individual.
        
        Args:
            record: Registro que contiene crop_image_path
            
        Returns:
            True si el recorte es válido, False en caso contrario
        """
        return self.crop_validator.validate_single_crop(record)
    
    def validate_and_regenerate_crops(
        self,
        crop_records: List[Dict[str, Any]],
        validate_crops: bool = True,
        regenerate_bad: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Valida la calidad de los recortes y regenera los malos si es necesario.
        
        Args:
            crop_records: Lista de registros con recortes
            validate_crops: Si se deben validar los recortes
            regenerate_bad: Si se deben regenerar los recortes malos
            
        Returns:
            Lista de registros con recortes válidos
        """
        if not validate_crops or not crop_records:
            return crop_records
        
        good_crop_records, bad_crop_records = self.crop_validator.validate_batch(
            crop_records
        )
        
        if regenerate_bad and bad_crop_records:
            logger.info(
                f"Regenerando {len(bad_crop_records)} recortes de mala calidad..."
            )
            
            # Eliminar recortes malos
            for record in bad_crop_records:
                crop_path = record.get("crop_image_path")
                if crop_path and Path(crop_path).exists():
                    Path(crop_path).unlink()
            
            # Regenerar recortes
            new_crop_records = self.generate_crops_for_missing(bad_crop_records)
            good_crop_records.extend(new_crop_records)
        
        return good_crop_records
    
    def generate_crops_for_missing(
        self,
        missing_records: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Genera recortes para registros que no los tienen.
        Usa cascada de segmentación (U-Net -> rembg -> OpenCV) para remover fondo.
        
        Args:
            missing_records: Lista de registros sin recortes
            
        Returns:
            Lista de registros con recortes generados
        """
        return self.segmented_generator.generate_crops(missing_records)
    
    def generate_crops_automatically(
        self,
        valid_records: List[Dict[str, Any]],
        overwrite: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Genera recortes automáticamente para todos los registros (método legacy).
        Redimensionamiento simple sin segmentación.
        
        Args:
            valid_records: Lista de registros a procesar
            overwrite: Si se deben sobrescribir recortes existentes
            
        Returns:
            Lista de registros con recortes generados
        """
        return self.simple_generator.generate_crops(valid_records, overwrite)

