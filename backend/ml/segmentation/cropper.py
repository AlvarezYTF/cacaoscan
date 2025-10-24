"""
Procesador de recortes con máscaras para granos de cacao.
"""
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from PIL import Image
import logging

from ..utils.paths import get_crops_dir, get_masks_dir, ensure_dir_exists
from ..utils.io import save_image, get_file_timestamp
from .infer_yolo_seg import YOLOSegmentationInference
from ..data.transforms import (
    create_transparent_crop,
    resize_crop_to_square,
    validate_crop_quality
)
from ..utils.logs import get_ml_logger


logger = get_ml_logger("cacaoscan.ml.segmentation")


class CacaoCropper:
    """Procesador de recortes de granos de cacao."""
    
    def __init__(
        self,
        yolo_inference: Optional[YOLOSegmentationInference] = None,
        crop_size: int = 512,
        padding: int = 10,
        save_masks: bool = False,
        overwrite: bool = False
    ):
        """
        Inicializa el procesador de recortes.
        
        Args:
            yolo_inference: Instancia de inferencia YOLO
            crop_size: Tamaño del recorte cuadrado
            padding: Padding adicional para el recorte
            save_masks: Si guardar máscaras para debug
            overwrite: Si sobrescribir archivos existentes
        """
        self.yolo_inference = yolo_inference
        self.crop_size = crop_size
        self.padding = padding
        self.save_masks = save_masks
        self.overwrite = overwrite
        
        # Asegurar que los directorios existen
        ensure_dir_exists(get_crops_dir())
        if self.save_masks:
            ensure_dir_exists(get_masks_dir())
    
    def process_image(
        self,
        image_path: Path,
        image_id: int,
        force_process: bool = False
    ) -> Dict[str, Any]:
        """
        Procesa una imagen para generar el recorte del grano.
        
        Args:
            image_path: Ruta a la imagen original
            image_id: ID de la imagen
            force_process: Forzar procesamiento aunque el crop ya exista
            
        Returns:
            Diccionario con información del procesamiento
        """
        crop_path = get_crops_dir() / f"{image_id}.png"
        mask_path = get_masks_dir() / f"{image_id}.png" if self.save_masks else None
        
        # Verificar si ya existe el crop y no se debe sobrescribir
        if not force_process and not self.overwrite and crop_path.exists():
            # Verificar si la imagen original es más nueva
            if not self._should_reprocess(image_path, crop_path):
                logger.debug(f"Crop ya existe para ID {image_id}, saltando")
                return {
                    'success': True,
                    'skipped': True,
                    'crop_path': crop_path,
                    'mask_path': mask_path,
                    'message': 'Crop ya existe y no necesita reprocesamiento'
                }
        
        try:
            # Realizar inferencia YOLO
            if self.yolo_inference is None:
                raise ValueError("YOLO inference no está inicializado")
            
            prediction = self.yolo_inference.get_best_prediction(image_path)
            
            if not prediction:
                return {
                    'success': False,
                    'error': 'No se encontraron detecciones',
                    'crop_path': None,
                    'mask_path': None
                }
            
            # Validar calidad de la predicción
            if not self.yolo_inference.validate_prediction_quality(prediction):
                return {
                    'success': False,
                    'error': 'Predicción de baja calidad',
                    'crop_path': None,
                    'mask_path': None
                }
            
            # Cargar imagen original
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"No se pudo cargar la imagen: {image_path}")
            
            # Convertir de BGR a RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Obtener máscara de la predicción
            mask = prediction['mask']
            
            # Validar calidad del recorte
            if not validate_crop_quality(image_rgb, mask):
                return {
                    'success': False,
                    'error': 'Recorte de baja calidad (proporciones extremas)',
                    'crop_path': None,
                    'mask_path': None
                }
            
            # Crear recorte con transparencia
            transparent_crop = create_transparent_crop(
                image_rgb, mask, self.padding
            )
            
            # Redimensionar a cuadrado
            square_crop = resize_crop_to_square(
                transparent_crop, self.crop_size
            )
            
            # Convertir a PIL Image
            pil_crop = Image.fromarray(square_crop, 'RGBA')
            
            # Guardar recorte
            save_image(pil_crop, crop_path)
            
            # Guardar máscara si se solicita
            if self.save_masks and mask_path:
                mask_normalized = (mask * 255).astype(np.uint8)
                pil_mask = Image.fromarray(mask_normalized, 'L')
                save_image(pil_mask, mask_path)
            
            logger.debug(f"Procesado exitosamente ID {image_id}")
            
            return {
                'success': True,
                'skipped': False,
                'crop_path': crop_path,
                'mask_path': mask_path,
                'confidence': prediction['confidence'],
                'area': prediction['area'],
                'bbox': prediction['bbox']
            }
            
        except Exception as e:
            logger.error(f"Error procesando imagen {image_path}: {e}")
            return {
                'success': False,
                'error': str(e),
                'crop_path': None,
                'mask_path': None
            }
    
    def _should_reprocess(self, source_path: Path, target_path: Path) -> bool:
        """
        Determina si se debe reprocesar basado en timestamps.
        
        Args:
            source_path: Ruta de la imagen fuente
            target_path: Ruta de la imagen objetivo
            
        Returns:
            True si se debe reprocesar
        """
        source_time = get_file_timestamp(source_path)
        target_time = get_file_timestamp(target_path)
        
        if source_time is None or target_time is None:
            return True
        
        return source_time > target_time
    
    def process_batch(
        self,
        image_records: list,
        limit: int = 0,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Procesa un lote de imágenes.
        
        Args:
            image_records: Lista de registros de imágenes
            limit: Límite de imágenes a procesar (0 = todas)
            progress_callback: Función de callback para progreso
            
        Returns:
            Diccionario con estadísticas del procesamiento
        """
        total_images = len(image_records)
        if limit > 0:
            image_records = image_records[:limit]
            total_images = min(total_images, limit)
        
        logger.info(f"Iniciando procesamiento de {total_images} imágenes")
        
        stats = {
            'total': total_images,
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }
        
        for i, record in enumerate(image_records):
            try:
                result = self.process_image(
                    record['raw_image_path'],
                    record['id']
                )
                
                stats['processed'] += 1
                
                if result['success']:
                    if result.get('skipped', False):
                        stats['skipped'] += 1
                    else:
                        stats['successful'] += 1
                else:
                    stats['failed'] += 1
                    stats['errors'].append({
                        'id': record['id'],
                        'error': result.get('error', 'Error desconocido')
                    })
                
                # Actualizar callback de progreso
                if progress_callback:
                    progress_callback(i + 1, total_images, result)
                
                # Log periódico
                if (i + 1) % 10 == 0:
                    logger.info(f"Procesadas {i + 1}/{total_images} imágenes")
                
            except Exception as e:
                logger.error(f"Error procesando registro {record['id']}: {e}")
                stats['failed'] += 1
                stats['errors'].append({
                    'id': record['id'],
                    'error': str(e)
                })
        
        # Log final
        success_rate = (stats['successful'] / stats['processed'] * 100) if stats['processed'] > 0 else 0
        logger.info(f"Procesamiento completado: {stats['successful']} exitosos, {stats['failed']} fallidos, {stats['skipped']} saltados")
        logger.info(f"Tasa de éxito: {success_rate:.2f}%")
        
        return stats


def create_cacao_cropper(
    confidence_threshold: float = 0.5,
    crop_size: int = 512,
    padding: int = 10,
    save_masks: bool = False,
    overwrite: bool = False
) -> CacaoCropper:
    """
    Función de conveniencia para crear un procesador de recortes.
    
    Args:
        confidence_threshold: Umbral de confianza para YOLO
        crop_size: Tamaño del recorte cuadrado
        padding: Padding adicional
        save_masks: Si guardar máscaras
        overwrite: Si sobrescribir archivos
        
    Returns:
        Instancia de CacaoCropper
    """
    from .infer_yolo_seg import create_yolo_inference
    
    yolo_inference = create_yolo_inference(confidence_threshold=confidence_threshold)
    
    return CacaoCropper(
        yolo_inference=yolo_inference,
        crop_size=crop_size,
        padding=padding,
        save_masks=save_masks,
        overwrite=overwrite
    )
