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
        overwrite: bool = False,
        enable_yolo: bool = True  # <-- NUEVO FLAG
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
        self.enable_yolo = enable_yolo # <-- NUEVO FLAG
        
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
            # --- INICIO DE CORRECCIÓN ---
            # Si YOLO está desactivado o no se inicializó, saltar al fallback
            if not self.yolo_inference or not self.enable_yolo:
                logger.info(f"YOLO desactivado para ID {image_id}. Usando fallback OpenCV...")
                return self._process_with_opencv_fallback(image_path, image_id)
            # --- FIN DE CORRECCIÓN ---

            # Realizar inferencia YOLO
            if self.yolo_inference is None:
                raise ValueError("YOLO inference no está inicializado")
            
            prediction = self.yolo_inference.get_best_prediction(image_path)
            
            if not prediction:
                # Intentar con umbrales progresivamente ms bajos
                logger.warning(f"YOLO no detect grano en {image_path.name}. Intentando con umbrales ms bajos...")
                lower_thresholds = [0.25, 0.2, 0.15, 0.1]
                
                for lower_threshold in lower_thresholds:
                    predictions_low = self.yolo_inference.predict(image_path, conf_threshold=lower_threshold)
                    if predictions_low:
                        # Filtrar la mejor prediccin (ms confianza y mayor rea)
                        best_pred = max(predictions_low, key=lambda p: p['confidence'] * p.get('area', 1))
                        
                        # Solo aceptar si tiene un mnimo de confianza
                        if best_pred['confidence'] >= lower_threshold * 0.7:
                            prediction = best_pred
                            logger.info(f"Deteccin encontrada con umbral {lower_threshold}, confianza: {best_pred['confidence']:.2f}")
                            break
                
                if not prediction:
                    return {
                        'success': False,
                        'error': 'No se encontraron detecciones incluso con umbral mnimo (0.1)',
                        'crop_path': None,
                        'mask_path': None
                    }
            
            # Validar calidad de la prediccin
            # Aceptar predicciones con confianza razonable, pero advertir si es baja
            if prediction['confidence'] < 0.5:
                logger.warning(
                    f"Prediccin YOLO con confianza baja ({prediction['confidence']:.2f}) para {image_path.name}. "
                    f"Se recomienda mejorar la imagen o el modelo YOLO."
                )
            
            # Verificar que la mscara tenga contenido significativo
            mask_area = np.sum(prediction['mask'] > 0.5) if prediction.get('mask') is not None else 0
            if mask_area < 100:  # Mnimo de pxeles
                logger.warning(f"Mscara muy pequea ({mask_area} pxeles) para {image_path.name}")
            
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"No se pudo cargar la imagen: {image_path}")
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Obtener máscara de la predicción
            mask = prediction['mask']
            
            # Redimensionar y normalizar mscara al tamao de la imagen original si es necesario
            image_height, image_width = image_rgb.shape[:2]
            mask_height, mask_width = mask.shape[:2]
            
            # Redimensionar mscara si es necesario
            if mask_height != image_height or mask_width != image_width:
                # Redimensionar mscara al tamao de la imagen original
                mask = cv2.resize(mask, (image_width, image_height), interpolation=cv2.INTER_LINEAR)
                logger.debug(f"Mscara redimensionada de {mask_width}x{mask_height} a {image_width}x{image_height}")
            
            # Normalizar mscara a valores 0-255 si es necesario
            if mask.dtype != np.uint8:
                if mask.max() <= 1.0:
                    mask = (mask * 255).astype(np.uint8)
                else:
                    mask = mask.astype(np.uint8)
            elif mask.max() > 1:
                # Asegurar que est en rango 0-255
                mask = np.clip(mask, 0, 255).astype(np.uint8)
            
            # Importar funciones necesarias (import dinmico para evitar problemas de cach)
            from ..data.transforms import validate_crop_quality, create_transparent_crop
            
            # Validar calidad del recorte (con validacin ms permisiva)
            # Usar rangos ms amplios para granos de cacao variados
            try:
                is_valid = validate_crop_quality(
                    image_rgb, 
                    mask, 
                    min_aspect_ratio=0.05,  # Muy permisivo (1:20)
                    max_aspect_ratio=20.0,  # Muy permisivo (20:1)
                    min_area=50  # rea mnima pequea
                )
                if not is_valid:
                    # Si falla la validacin, continuar de todos modos con advertencia
                    logger.warning(f"Validacin de crop fall para {image_path}, pero continuando...")
            except Exception as e:
                # Si hay error en la validacin, continuar de todos modos
                logger.warning(f"Error en validacin de crop para {image_path}: {e}, continuando...")
            
            transparent_crop = create_transparent_crop(
                image_rgb, mask, padding=0, crop_only=True
            )
            
            pil_crop = Image.fromarray(transparent_crop, 'RGBA')
            save_image(pil_crop, crop_path)
            
            # Guardar máscara si se solicita
            if self.save_masks and mask_path:
                mask_normalized = (mask * 255).astype(np.uint8)
                pil_mask = Image.fromarray(mask_normalized, 'L')
                save_image(pil_mask, mask_path)
            
            logger.debug(f"Procesado exitosamente ID {image_id} (con YOLO)")
            
            return {
                'success': True,
                'skipped': False,
                'crop_path': crop_path,
                'mask_path': mask_path,
                'confidence': prediction['confidence'],
                'area': prediction['area'],
                'bbox': prediction['bbox'],
                'mask': prediction.get('mask'),  # Incluir mscara de YOLO para refinamiento
                'original_image_path': str(image_path)  # Para refinamiento con imagen original
            }
            
        except Exception as e:
            logger.error(f"Error procesando imagen {image_path}: {e}")
            try:
                logger.warning("Intentando fallback OpenCV después de error en YOLO...")
                return self._process_with_opencv_fallback(image_path, image_id)
            except Exception as fallback_error:
                logger.error(f"Fallback OpenCV tambin fall: {fallback_error}")
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
            Diccionario con informacin del procesamiento
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
                    logger.warning(f"Validacin de crop fall para {image_path}, pero continuando...")
            except Exception as e:
                logger.warning(f"Error en validacin de crop para {image_path}: {e}, continuando...")
            
            # Crear imagen con fondo transparente (recortar solo el bounding box del grano, eliminar espacios en blanco)
            # Usar padding=0 para recorte exacto sin bordes blancos, mantener calidad original
            transparent_crop = create_transparent_crop(
                image_rgb, mask, padding=0, crop_only=True
            )

            # Convertir a PIL antes de guardar
            pil_crop = Image.fromarray(transparent_crop, "RGBA")

            # Esta es la ruta que el pipeline de entrenamiento espera
            crop_path = get_crops_dir() / f"{image_id}.png"
            save_image(pil_crop, crop_path)
            
            # Guardar mscara si se solicita
            mask_path = None
            if self.save_masks:
                mask_path = get_masks_dir() / f"{image_id}_opencv.png"
                # Extraer máscara de la imagen RGBA
                crop_array = np.array(pil_crop)
                if crop_array.shape[2] == 4:
                    mask = crop_array[:, :, 3]
                    pil_mask = Image.fromarray(mask, "L")
                    save_image(pil_mask, mask_path)

            logger.info(f"Procesado exitosamente con Fallback (rembg/OpenCV): {image_path.name}")
            
            return {
                'success': True,
                'skipped': False,
                'crop_path': crop_path,
                'mask_path': mask_path,
                'confidence': 0.5,  # Confianza fija para fallback
                'area': int(np.sum(np.array(pil_crop)[:, :, 3] > 128)),
                'bbox': None,
                'method': 'fallback_chain'
            }
            
        except Exception as e:
            logger.error(f"Error en fallback OpenCV/rembg para {image_path}: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Fallback OpenCV fall: {str(e)}",
                'crop_path': None,
                'mask_path': None
            }
    
    def _should_reprocess(self, source_path: Path, target_path: Path) -> bool:
        """
        Determina si se debe reprocesar basado en timestamps.
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
        
        success_rate = (stats['successful'] / stats['processed'] * 100) if stats['processed'] > 0 else 0
        logger.info(f"Procesamiento completado: {stats['successful']} exitosos, {stats['failed']} fallidos, {stats['skipped']} saltados")
        logger.info(f"Tasa de éxito: {success_rate:.2f}%")
        
        return stats


def create_cacao_cropper(
    confidence_threshold: float = 0.5,
    crop_size: int = 512,
    padding: int = 10,
    save_masks: bool = False,
    overwrite: bool = False,
    enable_yolo: bool = True  # <-- NUEVO FLAG
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
    
    # --- INICIO DE CORRECCIÓN ---
    # Solo cargar YOLO si está habilitado
    yolo_inference = None
    if enable_yolo:
        try:
            yolo_inference = create_yolo_inference(confidence_threshold=confidence_threshold)
        except Exception as e:
            logger.warning(f"No se pudo cargar YOLO (enable_yolo=True): {e}. Se desactivará YOLO.")
            enable_yolo = False
    else:
        logger.info("Creando CacaoCropper con YOLO desactivado.")
    # --- FIN DE CORRECCIÓN ---
    
    return CacaoCropper(
        yolo_inference=yolo_inference,
        crop_size=crop_size,
        padding=padding,
        save_masks=save_masks,
        overwrite=overwrite,
        enable_yolo=enable_yolo # <-- Pasar el flag
    )