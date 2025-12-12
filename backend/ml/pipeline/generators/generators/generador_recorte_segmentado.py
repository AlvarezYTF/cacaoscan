"""
Generador de recortes usando segmentación en cascada.

Este módulo maneja la generación de recortes usando segmentación,
siguiendo principios SOLID:
- Single Responsibility: solo generación con segmentación
- Dependency Inversion: implementa IGeneradorRecorte
"""
from pathlib import Path
from typing import Dict, List, Any
from PIL import Image

from ml.utils.logs import get_ml_logger
from ml.segmentation.processor import segment_and_crop_cacao_bean
from .base_generador import GeneradorRecorteBase

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.generators.segmented")


class GeneradorRecorteSegmentado(GeneradorRecorteBase):
    """
    Generador de recortes usando segmentación en cascada.
    
    Usa cascada de segmentación (U-Net -> rembg -> OpenCV) para
    remover el fondo y generar recortes de granos de cacao.
    """
    
    def __init__(self, segmentation_backend: str = "auto"):
        """
        Inicializa el generador de recortes segmentados.
        
        Args:
            segmentation_backend: Método de segmentación ("auto", "ai", "opencv", "rembg")
        """
        super().__init__()
        
        # Determinar método de segmentación
        if segmentation_backend == "auto":
            self.seg_method = "ai"  # Usa cascada (U-Net -> rembg -> OpenCV)
        else:
            self.seg_method = segmentation_backend
        
        logger.info(f"GeneradorRecorteSegmentado inicializado (método={self.seg_method})")
    
    def generate_crops(
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
        if not missing_records:
            return []
        
        logger.info(f"Generando recortes para {len(missing_records)} registros faltantes...")
        logger.info(
            f"Usando método de segmentación: {self.seg_method} "
            f"(cascada: U-Net -> rembg -> OpenCV)"
        )
        
        generated_records: List[Dict[str, Any]] = []
        successful = 0
        failed = 0
        
        for i, record in enumerate(missing_records):
            try:
                # Obtener ruta de imagen
                image_path = self._obtener_ruta_imagen(record)
                if not image_path:
                    logger.warning(
                        f"Registro {record.get('id', 'desconocido')} no tiene image_path"
                    )
                    failed += 1
                    continue
                
                if not image_path.exists():
                    logger.warning(f"Imagen original no encontrada: {image_path}")
                    failed += 1
                    continue
                
                # Obtener ruta de recorte
                crop_path = self._obtener_ruta_recorte(record)
                if not crop_path:
                    logger.warning(
                        f"Registro {record.get('id', 'desconocido')} no tiene crop_image_path"
                    )
                    failed += 1
                    continue
                
                # Verificar si el recorte ya existe
                if self._verificar_recorte_existe(crop_path, overwrite=False):
                    generated_records.append(record)
                    successful += 1
                    continue
                
                # Generar recorte usando segmentación (remueve fondo)
                try:
                    png_path_str = segment_and_crop_cacao_bean(
                        str(image_path),
                        method=self.seg_method
                    )
                    
                    if not png_path_str:
                        raise ValueError("La segmentación no retornó ruta de imagen")
                    
                    # Cargar imagen segmentada
                    segmented_image = Image.open(png_path_str)
                    
                    # Guardar en la ubicación correcta
                    if self.guardador.guardar(segmented_image, crop_path, "PNG"):
                        record["crop_image_path"] = crop_path
                        generated_records.append(record)
                        successful += 1
                        logger.debug(f"Recorte generado con segmentación: {crop_path}")
                    else:
                        failed += 1
                    
                except Exception as seg_error:
                    logger.warning(
                        f"Error en segmentación para ID {record.get('id', 'desconocido')}: {seg_error}"
                    )
                    failed += 1
                    continue
                
                # Log de progreso cada 10 imágenes
                if (i + 1) % 10 == 0:
                    logger.info(
                        f"Generados {i + 1}/{len(missing_records)} recortes faltantes..."
                    )
                    
            except Exception as e:
                logger.error(
                    f"Error generando recorte para registro {record.get('id', 'desconocido')}: {e}",
                    exc_info=True
                )
                failed += 1
        
        logger.info(
            f"Generación de recortes completada: {successful} exitosos, {failed} fallidos"
        )
        return generated_records


# Compatibilidad hacia atrás
SegmentedCropGenerator = GeneradorRecorteSegmentado

