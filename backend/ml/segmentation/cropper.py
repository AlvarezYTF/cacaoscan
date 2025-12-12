"""
Procesador de recortes con máscaras para granos de cacao.

REFACTORIZADO: Aplicando principios SOLID
- Funciones auxiliares extraídas para mejorar SRP
- Mejores docstrings y type hints
- Separación de responsabilidades mejorada
"""
import numpy as np
import cv2
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Callable
from PIL import Image
import logging

from ..utils.paths import get_crops_dir, get_masks_dir, ensure_dir_exists
from ..utils.io import save_image, get_file_timestamp
from .infer_yolo_seg import YOLOSegmentationInference
from ..utils.logs import get_ml_logger
from ..data.transforms import validate_crop_quality, create_transparent_crop


logger = get_ml_logger("cacaoscan.ml.segmentation")


def _intentar_umbrales_bajos(
    yolo_inference: YOLOSegmentationInference,
    image_path: Path,
    umbrales: List[float]
) -> Optional[Dict[str, Any]]:
    """
    Intenta obtener predicción YOLO con umbrales más bajos.
    
    Args:
        yolo_inference: Instancia de inferencia YOLO
        image_path: Ruta a la imagen
        umbrales: Lista de umbrales a probar
        
    Returns:
        Mejor predicción encontrada o None
    """
    for lower_threshold in umbrales:
        predictions_low = yolo_inference.predict(image_path, conf_threshold=lower_threshold)
        if predictions_low:
            best_pred = max(predictions_low, key=lambda p: p['confidence'] * p.get('area', 1))
            if best_pred['confidence'] >= lower_threshold * 0.7:
                logger.info(f"Detección encontrada con umbral {lower_threshold}, confianza: {best_pred['confidence']:.2f}")
                return best_pred
    return None


def _calcular_area_mascara(mask: Optional[np.ndarray]) -> int:
    """Calcula el área de la máscara en píxeles."""
    if mask is None:
        return 0
    return int(np.sum(mask > 0.5))


def _normalizar_mascara_tipo(mask: np.ndarray) -> np.ndarray:
    """Normaliza el tipo de datos de la máscara a uint8."""
    if mask.dtype != np.uint8:
        if mask.max() <= 1.0:
            return (mask * 255).astype(np.uint8)
        return mask.astype(np.uint8)
    elif mask.max() > 1:
        return np.clip(mask, 0, 255).astype(np.uint8)
    return mask


def _validar_calidad_crop(
    image_rgb: np.ndarray,
    mask: np.ndarray,
    min_aspect_ratio: float = 0.05,
    max_aspect_ratio: float = 20.0,
    min_area: int = 50
) -> bool:
    """
    Valida la calidad del crop.
    
    Returns:
        True si el crop es válido, False en caso contrario
    """
    try:
        return validate_crop_quality(
            image_rgb,
            mask,
            min_aspect_ratio=min_aspect_ratio,
            max_aspect_ratio=max_aspect_ratio,
            min_area=min_area
        )
    except Exception as e:
        logger.warning(f"Error en validación de crop: {e}, continuando...")
        return True  # Continuar aunque falle la validación


def _crear_imagen_transparente(image_rgb: np.ndarray, mask: np.ndarray) -> Image.Image:
    """Crea una imagen transparente a partir de RGB y máscara."""
    transparent_crop = create_transparent_crop(image_rgb, mask, padding=0, crop_only=True)
    return Image.fromarray(transparent_crop, 'RGBA')


def _extraer_mascara_desde_rgba(rgba_array: np.ndarray) -> np.ndarray:
    """Extrae la máscara desde un array RGBA."""
    if rgba_array.shape[2] == 4:
        return rgba_array[:, :, 3]
    return None


def _calcular_estadisticas_crop(pil_crop: Image.Image) -> Dict[str, Any]:
    """Calcula estadísticas del crop procesado."""
    crop_array = np.array(pil_crop)
    mask = _extraer_mascara_desde_rgba(crop_array) if crop_array.shape[2] == 4 else None
    area = int(np.sum(mask > 128)) if mask is not None else 0
    return {
        'area': area,
        'confidence': 0.5,  # Confianza fija para fallback
        'bbox': None,
        'method': 'fallback_chain'
    }


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
    
    def _should_skip_processing(self, crop_path: Path, image_path: Path, force_process: bool) -> bool:
        """Determina si se debe saltar el procesamiento."""
        if force_process or self.overwrite or not crop_path.exists():
            return False
        return not self._should_reprocess(image_path, crop_path)
    
    def _get_yolo_prediction_with_fallback(self, image_path: Path) -> Optional[Dict[str, Any]]:
        """
        Obtiene predicción YOLO, intentando con umbrales más bajos si es necesario.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Mejor predicción encontrada o None
        """
        prediction = self.yolo_inference.get_best_prediction(image_path)
        
        if prediction:
            return prediction
        
        logger.warning(f"YOLO no detectó grano en {image_path.name}. Intentando con umbrales más bajos...")
        lower_thresholds = [0.25, 0.2, 0.15, 0.1]
        return _intentar_umbrales_bajos(self.yolo_inference, image_path, lower_thresholds)
    
    def _validate_prediction_quality(self, prediction: Dict[str, Any], image_path: Path) -> None:
        """
        Valida la calidad de la predicción y emite advertencias si es necesario.
        
        Args:
            prediction: Diccionario con la predicción
            image_path: Ruta a la imagen procesada
        """
        if prediction['confidence'] < 0.5:
            logger.warning(
                f"Predicción YOLO con confianza baja ({prediction['confidence']:.2f}) para {image_path.name}. "
                f"Se recomienda mejorar la imagen o el modelo YOLO."
            )
        
        mask_area = _calcular_area_mascara(prediction.get('mask'))
        if mask_area < 100:
            logger.warning(f"Máscara muy pequeña ({mask_area} píxeles) para {image_path.name}")
    
    def _prepare_mask(self, mask: np.ndarray, image_height: int, image_width: int) -> np.ndarray:
        """
        Redimensiona y normaliza la máscara al tamaño de la imagen.
        
        Args:
            mask: Máscara original
            image_height: Altura de la imagen
            image_width: Ancho de la imagen
            
        Returns:
            Máscara redimensionada y normalizada
        """
        mask_height, mask_width = mask.shape[:2]
        
        if mask_height != image_height or mask_width != image_width:
            mask = cv2.resize(mask, (image_width, image_height), interpolation=cv2.INTER_LINEAR)
            logger.debug(f"Máscara redimensionada de {mask_width}x{mask_height} a {image_width}x{image_height}")
        
        return _normalizar_mascara_tipo(mask)
    
    def _create_and_save_crop(self, image_rgb: np.ndarray, mask: np.ndarray, crop_path: Path, mask_path: Optional[Path]) -> None:
        """
        Crea y guarda el crop y la máscara si es necesario.
        
        Args:
            image_rgb: Imagen RGB
            mask: Máscara binaria
            crop_path: Ruta donde guardar el crop
            mask_path: Ruta donde guardar la máscara (opcional)
        """
        # Validar calidad del crop
        is_valid = _validar_calidad_crop(image_rgb, mask)
        if not is_valid:
            logger.warning("Validación de crop falló, pero continuando...")
        
        # Crear y guardar crop transparente
        pil_crop = _crear_imagen_transparente(image_rgb, mask)
        save_image(pil_crop, crop_path)
        
        # Guardar máscara si se solicita
        if self.save_masks and mask_path:
            mask_normalized = (mask * 255).astype(np.uint8)
            pil_mask = Image.fromarray(mask_normalized, 'L')
            save_image(pil_mask, mask_path)
    
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
        
        if self._should_skip_processing(crop_path, image_path, force_process):
            logger.debug(f"Crop ya existe para ID {image_id}, saltando")
            return {
                'success': True,
                'skipped': True,
                'crop_path': crop_path,
                'mask_path': mask_path,
                'message': 'Crop ya existe y no necesita reprocesamiento'
            }
        
        try:
            if not self.yolo_inference or not self.enable_yolo:
                logger.info(f"YOLO desactivado para ID {image_id}. Usando fallback OpenCV...")
                return self._process_with_opencv_fallback(image_path, image_id)

            if self.yolo_inference is None:
                raise ValueError("YOLO inference no está inicializado")
            
            prediction = self._get_yolo_prediction_with_fallback(image_path)
            if not prediction:
                return {
                    'success': False,
                    'error': 'No se encontraron detecciones incluso con umbral mínimo (0.1)',
                    'crop_path': None,
                    'mask_path': None
                }
            
            self._validate_prediction_quality(prediction, image_path)
            
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"No se pudo cargar la imagen: {image_path}")
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            mask = self._prepare_mask(prediction['mask'], image_rgb.shape[0], image_rgb.shape[1])
            
            self._create_and_save_crop(image_rgb, mask, crop_path, mask_path)
            
            logger.debug(f"Procesado exitosamente ID {image_id} (con YOLO)")
            
            return {
                'success': True,
                'skipped': False,
                'crop_path': crop_path,
                'mask_path': mask_path,
                'confidence': prediction['confidence'],
                'area': prediction['area'],
                'bbox': prediction['bbox'],
                'mask': prediction.get('mask'),
                'original_image_path': str(image_path)
            }
            
        except Exception as e:
            logger.error(f"Error procesando imagen {image_path}: {e}")
            try:
                logger.warning("Intentando fallback OpenCV después de error en YOLO...")
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
            is_valid = _validar_calidad_crop(image_rgb, mask)
            if not is_valid:
                logger.warning(f"Validación de crop falló para {image_path}, pero continuando...")
            
            # Crear imagen con fondo transparente
            pil_crop = _crear_imagen_transparente(image_rgb, mask)

            # Guardar crop
            crop_path = get_crops_dir() / f"{image_id}.png"
            save_image(pil_crop, crop_path)
            
            # Guardar máscara si se solicita
            mask_path = None
            if self.save_masks:
                mask_path = get_masks_dir() / f"{image_id}_opencv.png"
                crop_array = np.array(pil_crop)
                mask_extracted = _extraer_mascara_desde_rgba(crop_array)
                if mask_extracted is not None:
                    pil_mask = Image.fromarray(mask_extracted, "L")
                    save_image(pil_mask, mask_path)

            logger.info(f"Procesado exitosamente con Fallback (rembg/OpenCV): {image_path.name}")
            
            # Calcular estadísticas
            stats = _calcular_estadisticas_crop(pil_crop)
            
            return {
                'success': True,
                'skipped': False,
                'crop_path': crop_path,
                'mask_path': mask_path,
                **stats
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
    
    def _update_stats_from_result(
        self,
        stats: Dict[str, Any],
        record: Dict[str, Any],
        result: Dict[str, Any]
    ) -> None:
        """
        Actualiza estadísticas basadas en el resultado del procesamiento.
        
        Args:
            stats: Diccionario de estadísticas a actualizar
            record: Registro de la imagen procesada
            result: Resultado del procesamiento
        """
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
    
    def process_batch(
        self,
        image_records: List[Dict[str, Any]],
        limit: int = 0,
        progress_callback: Optional[Callable[[int, int, Dict[str, Any]], None]] = None
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
                
                self._update_stats_from_result(stats, record, result)
                
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