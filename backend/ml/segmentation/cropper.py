"""
Procesador de recortes con mÃ¡scaras para granos de cacao.
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
from ..utils.logs import get_ml_logger
from ..data.transforms import validate_crop_quality, create_transparent_crop


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
            crop_size: TamaÃ±o del recorte cuadrado
            padding: Padding adicional para el recorte
            save_masks: Si guardar mÃ¡scaras para debug
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
            Diccionario con informaciÃ³n del procesamiento
        """
        crop_path = get_crops_dir() / f"{image_id}.png"
        mask_path = get_masks_dir() / f"{image_id}.png" if self.save_masks else None
        
        # Verificar si ya existe el crop y no se debe sobrescribir
        if not force_process and not self.overwrite and crop_path.exists():
            # Verificar si la imagen original es mÃ¡s nueva
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
                raise ValueError("YOLO inference no estÃ¡ inicializado")
            
            prediction = self.yolo_inference.get_best_prediction(image_path)
            
            if not prediction:
                # Intentar con umbrales progresivamente más bajos
                logger.warning(f"YOLO no detectó grano en {image_path.name}. Intentando con umbrales más bajos...")
                lower_thresholds = [0.25, 0.2, 0.15, 0.1]
                
                for lower_threshold in lower_thresholds:
                    predictions_low = self.yolo_inference.predict(image_path, conf_threshold=lower_threshold)
                    if predictions_low:
                        # Filtrar la mejor predicción (más confianza y mayor área)
                        best_pred = max(predictions_low, key=lambda p: p['confidence'] * p.get('area', 1))
                        
                        # Solo aceptar si tiene un mínimo de confianza
                        if best_pred['confidence'] >= lower_threshold * 0.7:
                            prediction = best_pred
                            logger.info(f"Detección encontrada con umbral {lower_threshold}, confianza: {best_pred['confidence']:.2f}")
                            break
                
                if not prediction:
                    return {
                        'success': False,
                        'error': 'No se encontraron detecciones incluso con umbral mínimo (0.1)',
                        'crop_path': None,
                        'mask_path': None
                    }
            
            # Validar calidad de la predicción
            # Aceptar predicciones con confianza razonable, pero advertir si es baja
            if prediction['confidence'] < 0.5:
                logger.warning(
                    f"Predicción YOLO con confianza baja ({prediction['confidence']:.2f}) para {image_path.name}. "
                    f"Se recomienda mejorar la imagen o el modelo YOLO."
                )
            
            # Verificar que la máscara tenga contenido significativo
            mask_area = np.sum(prediction['mask'] > 0.5) if prediction.get('mask') is not None else 0
            if mask_area < 100:  # Mínimo de píxeles
                logger.warning(f"Máscara muy pequeña ({mask_area} píxeles) para {image_path.name}")
            
            # Cargar imagen original
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"No se pudo cargar la imagen: {image_path}")
            
            # Convertir de BGR a RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Obtener mÃ¡scara de la predicciÃ³n
            mask = prediction['mask']
            
            # Redimensionar y normalizar máscara al tamaño de la imagen original si es necesario
            image_height, image_width = image_rgb.shape[:2]
            mask_height, mask_width = mask.shape[:2]
            
            # Redimensionar máscara si es necesario
            if mask_height != image_height or mask_width != image_width:
                # Redimensionar máscara al tamaño de la imagen original
                mask = cv2.resize(mask, (image_width, image_height), interpolation=cv2.INTER_LINEAR)
                logger.debug(f"Máscara redimensionada de {mask_width}x{mask_height} a {image_width}x{image_height}")
            
            # Normalizar máscara a valores 0-255 si es necesario
            if mask.dtype != np.uint8:
                # Normalizar valores flotantes a 0-255
                if mask.max() <= 1.0:
                    mask = (mask * 255).astype(np.uint8)
                else:
                    mask = mask.astype(np.uint8)
            elif mask.max() > 1:
                # Asegurar que esté en rango 0-255
                mask = np.clip(mask, 0, 255).astype(np.uint8)
            
            # Importar funciones necesarias (import dinámico para evitar problemas de caché)
            from ..data.transforms import validate_crop_quality, create_transparent_crop
            
            # Validar calidad del recorte (con validación más permisiva)
            # Usar rangos más amplios para granos de cacao variados
            try:
                is_valid = validate_crop_quality(
                    image_rgb, 
                    mask, 
                    min_aspect_ratio=0.05,  # Muy permisivo (1:20)
                    max_aspect_ratio=20.0,  # Muy permisivo (20:1)
                    min_area=50  # Área mínima pequeña
                )
                if not is_valid:
                    # Si falla la validación, continuar de todos modos con advertencia
                    logger.warning(f"Validación de crop falló para {image_path}, pero continuando...")
            except Exception as e:
                # Si hay error en la validación, continuar de todos modos
                logger.warning(f"Error en validación de crop para {image_path}: {e}, continuando...")
            
            # Crear imagen con fondo transparente (recortar solo el bounding box del grano, eliminar espacios en blanco)
            # Usar padding=0 para recorte exacto sin bordes blancos, mantener calidad original
            transparent_crop = create_transparent_crop(
                image_rgb, mask, padding=0, crop_only=True
            )
            
            # Convertir a PIL Image directamente (mantener calidad original, sin redimensionar)
            pil_crop = Image.fromarray(transparent_crop, 'RGBA')
            
            # Guardar recorte
            save_image(pil_crop, crop_path)
            
            # Guardar mÃ¡scara si se solicita
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
                'bbox': prediction['bbox'],
                'mask': prediction.get('mask'),  # Incluir máscara de YOLO para refinamiento
                'original_image_path': str(image_path)  # Para refinamiento con imagen original
            }
            
        except Exception as e:
            logger.error(f"Error procesando imagen {image_path}: {e}")
            # Intentar fallback a OpenCV si YOLO falla completamente
            try:
                logger.warning(f"Intentando fallback OpenCV después de error en YOLO...")
                return self._process_with_opencv_fallback(image_path, image_id)
            except Exception as fallback_error:
                logger.error(f"Fallback OpenCV también falló: {fallback_error}")
                return {
                    'success': False,
                    'error': f"YOLO: {str(e)}; OpenCV fallback: {str(fallback_error)}",
                    'crop_path': None,
                    'mask_path': None
                }
    
    def _process_with_opencv_fallback(self, image_path: Path, image_id: int) -> Dict[str, Any]:
        """
        Procesa la imagen usando OpenCV como fallback cuando YOLO no detecta nada.
        
        Args:
            image_path: Ruta a la imagen original
            image_id: ID de la imagen
            
        Returns:
            Diccionario con información del procesamiento
        """
        try:
            from .processor import _remove_background_opencv
            
            # Cargar imagen original
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"No se pudo cargar la imagen: {image_path}")
            
            # Usar OpenCV para remover fondo
            rgba_image = _remove_background_opencv(str(image_path))
            
            # Convertir PIL Image a numpy array si es necesario
            if isinstance(rgba_image, Image.Image):
                rgba_array = np.array(rgba_image)
            else:
                rgba_array = rgba_image
            
            # Extraer RGB y alpha
            image_rgb = rgba_array[:, :, :3]
            mask = rgba_array[:, :, 3]
            
            # Validar calidad del recorte (permisivo)
            try:
                is_valid = validate_crop_quality(
                    image_rgb, 
                    mask, 
                    min_aspect_ratio=0.05,
                    max_aspect_ratio=20.0,
                    min_area=50
                )
                if not is_valid:
                    logger.warning(f"Validación de crop falló para {image_path}, pero continuando...")
            except Exception as e:
                logger.warning(f"Error en validación de crop para {image_path}: {e}, continuando...")
            
            # Crear imagen con fondo transparente (recortar solo el bounding box del grano, eliminar espacios en blanco)
            # Usar padding=0 para recorte exacto sin bordes blancos, mantener calidad original
            transparent_crop = create_transparent_crop(
                image_rgb, mask, padding=0, crop_only=True
            )
            
            # Convertir a PIL Image directamente (mantener calidad original, sin redimensionar)
            pil_crop = Image.fromarray(transparent_crop, 'RGBA')
            
            # Guardar recorte usando el image_id
            crop_path = get_crops_dir() / f"{image_id}_opencv.png"
            save_image(pil_crop, crop_path)
            
            # Guardar máscara si se solicita
            mask_path = None
            if self.save_masks:
                mask_path = get_masks_dir() / f"{image_id}_opencv.png"
                mask_normalized = (mask * 255).astype(np.uint8) if mask.max() <= 1 else mask.astype(np.uint8)
                pil_mask = Image.fromarray(mask_normalized, 'L')
                save_image(pil_mask, mask_path)
            
            logger.info(f"Procesado exitosamente con OpenCV fallback: {image_path.name}")
            
            return {
                'success': True,
                'skipped': False,
                'crop_path': crop_path,
                'mask_path': mask_path,
                'confidence': 0.5,  # Confianza fija para OpenCV
                'area': int(np.sum(mask > 128)),
                'bbox': None,
                'method': 'opencv_fallback'
            }
            
        except Exception as e:
            logger.error(f"Error en fallback OpenCV para {image_path}: {e}")
            return {
                'success': False,
                'error': f"Fallback OpenCV falló: {str(e)}",
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
        Procesa un lote de imÃ¡genes.
        
        Args:
            image_records: Lista de registros de imÃ¡genes
            limit: LÃ­mite de imÃ¡genes a procesar (0 = todas)
            progress_callback: FunciÃ³n de callback para progreso
            
        Returns:
            Diccionario con estadÃ­sticas del procesamiento
        """
        total_images = len(image_records)
        if limit > 0:
            image_records = image_records[:limit]
            total_images = min(total_images, limit)
        
        logger.info(f"Iniciando procesamiento de {total_images} imÃ¡genes")
        
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
                
                # Log periÃ³dico
                if (i + 1) % 10 == 0:
                    logger.info(f"Procesadas {i + 1}/{total_images} imÃ¡genes")
                
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
        logger.info(f"Tasa de Ã©xito: {success_rate:.2f}%")
        
        return stats


def create_cacao_cropper(
    confidence_threshold: float = 0.5,
    crop_size: int = 512,
    padding: int = 10,
    save_masks: bool = False,
    overwrite: bool = False
) -> CacaoCropper:
    """
    FunciÃ³n de conveniencia para crear un procesador de recortes.
    
    Args:
        confidence_threshold: Umbral de confianza para YOLO
        crop_size: TamaÃ±o del recorte cuadrado
        padding: Padding adicional
        save_masks: Si guardar mÃ¡scaras
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


