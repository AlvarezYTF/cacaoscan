"""
Generador de recortes simple (método legacy).

Este módulo maneja la generación de recortes usando redimensionamiento simple,
siguiendo principios SOLID:
- Single Responsibility: solo generación con redimensionamiento
- Dependency Inversion: implementa IGeneradorRecorte
"""
from pathlib import Path
from typing import Dict, List, Any, Tuple

from ml.utils.logs import get_ml_logger
from .base_generador import GeneradorRecorteBase
from .procesadores import RedimensionadorImagen

logger = get_ml_logger("cacaoscan.ml.pipeline.generators.generators.simple")


class GeneradorRecorteSimple(GeneradorRecorteBase):
    """
    Generador de recortes usando redimensionamiento simple (método legacy).
    
    Redimensiona la imagen original sin segmentación.
    """
    
    def __init__(self, target_size: Tuple[int, int] = (512, 512)):
        """
        Inicializa el generador de recortes simple.
        
        Args:
            target_size: Tamaño objetivo para recortes redimensionados
        """
        super().__init__()
        self.target_size = target_size
        self.redimensionador = RedimensionadorImagen()
        logger.info(f"GeneradorRecorteSimple inicializado (tamaño_objetivo={target_size})")
    
    def generate_crops(
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
        if not valid_records:
            return []
        
        logger.info(
            f"Generando recortes automáticamente (método legacy) para {len(valid_records)} registros..."
        )
        
        generated_records: List[Dict[str, Any]] = []
        successful = 0
        failed = 0
        
        # Crear directorio de recortes si no existe
        crops_dir = Path("media/cacao_images/crops")
        crops_dir.mkdir(parents=True, exist_ok=True)
        
        for i, record in enumerate(valid_records):
            try:
                # Obtener ruta de imagen
                image_path = self._obtener_ruta_imagen(record)
                if not image_path:
                    failed += 1
                    continue
                
                if not image_path.exists():
                    logger.warning(f"Imagen original no encontrada: {image_path}")
                    failed += 1
                    continue
                
                # Obtener ruta de recorte
                crop_path = self._obtener_ruta_recorte(record)
                if not crop_path:
                    failed += 1
                    continue
                
                # Verificar si el recorte ya existe
                if self._verificar_recorte_existe(crop_path, overwrite):
                    generated_records.append(record)
                    successful += 1
                    continue
                
                # Generar recorte simple (redimensionar imagen original)
                imagen = self.procesador.cargar_imagen(image_path)
                if not imagen:
                    failed += 1
                    continue
                
                imagen_redimensionada = self.redimensionador.redimensionar(imagen, self.target_size)
                
                if self.guardador.guardar(imagen_redimensionada, crop_path, "PNG"):
                    record["crop_image_path"] = crop_path
                    generated_records.append(record)
                    successful += 1
                    logger.debug(f"Recorte generado: {crop_path}")
                else:
                    failed += 1
                
                # Log de progreso cada 50 imágenes
                if (i + 1) % 50 == 0:
                    logger.info(f"Generados {i + 1}/{len(valid_records)} recortes...")
                    
            except Exception as e:
                logger.error(
                    f"Error generando recorte para ID {record.get('id', 'desconocido')}: {e}"
                )
                failed += 1
        
        logger.info(
            f"Generación de recortes completada: {successful} exitosos, {failed} fallidos"
        )
        return generated_records


# Compatibilidad hacia atrás
SimpleCropGenerator = GeneradorRecorteSimple

