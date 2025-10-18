"""
Módulo especializado para predicción de peso con YOLOv8.

Este módulo implementa:
1. Carga y gestión del modelo YOLOv8 entrenado
2. Recorte inteligente estilo iPhone con segmentación
3. Aplicación de máscara transparente
4. Predicción de peso basada en dimensiones detectadas
5. Integración con el sistema existente de CacaoScan
"""

import os
import logging
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import torch
from PIL import Image, ImageFilter
import json
import base64
from datetime import datetime

# Configurar Django si no está configurado
import django
if not django.apps.apps.ready:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    logging.warning("Ultralytics YOLO no está disponible. Instalar con: pip install ultralytics")

from ..config import MODEL_CONFIGS, YOLO_CONFIG, YOLO_CALIBRATION, YOLO_WEIGHT_PREDICTION
from ..utils import performance_profiler, validate_image_format

# Configurar logging
logger = logging.getLogger('ml')


class SmartCropProcessor:
    """
    Procesador de recorte inteligente estilo iPhone.
    
    Implementa segmentación avanzada y aplicación de máscara transparente
    para aislar granos de cacao de manera precisa.
    """
    
    def __init__(self, 
                 blur_radius: int = 15,
                 feather_edges: bool = True,
                 background_alpha: float = 0.0):
        """
        Inicializa el procesador de recorte inteligente.
        
        Args:
            blur_radius: Radio de desenfoque para suavizar bordes
            feather_edges: Si aplicar suavizado en los bordes
            background_alpha: Transparencia del fondo (0.0 = transparente)
        """
        self.blur_radius = blur_radius
        self.feather_edges = feather_edges
        self.background_alpha = background_alpha
        
        logger.info(f"SmartCropProcessor inicializado (blur={blur_radius}, feather={feather_edges})")
    
    def process_detection(self, 
                         image: np.ndarray, 
                         bbox: Tuple[int, int, int, int],
                         confidence: float) -> Dict[str, Any]:
        """
        Procesa una detección para crear recorte inteligente.
        
        Args:
            image: Imagen original
            bbox: Bounding box (x1, y1, x2, y2)
            confidence: Confianza de la detección
            
        Returns:
            Dict con imagen procesada y metadatos
        """
        try:
            x1, y1, x2, y2 = bbox
            
            # Expandir bbox para incluir contexto
            expanded_bbox = self._expand_bbox(bbox, image.shape, expansion_factor=0.1)
            ex1, ey1, ex2, ey2 = expanded_bbox
            
            # Extraer región de interés
            roi = image[ey1:ey2, ex1:ex2]
            
            # Crear máscara usando segmentación
            mask = self._create_smart_mask(roi, bbox, expanded_bbox)
            
            # Aplicar recorte inteligente
            cropped_image = self._apply_smart_crop(roi, mask)
            
            # Crear imagen con fondo transparente
            transparent_image = self._create_transparent_background(cropped_image, mask)
            
            # Calcular métricas de calidad
            quality_metrics = self._calculate_quality_metrics(mask, confidence)
            
            return {
                'cropped_image': cropped_image,
                'transparent_image': transparent_image,
                'mask': mask,
                'bbox': bbox,
                'expanded_bbox': expanded_bbox,
                'quality_metrics': quality_metrics,
                'processing_successful': True
            }
            
        except Exception as e:
            logger.error(f"Error en procesamiento de recorte inteligente: {e}")
            return {
                'cropped_image': None,
                'transparent_image': None,
                'mask': None,
                'bbox': bbox,
                'expanded_bbox': bbox,
                'quality_metrics': {'quality_score': 0.0},
                'processing_successful': False,
                'error': str(e)
            }
    
    def _expand_bbox(self, 
                    bbox: Tuple[int, int, int, int], 
                    image_shape: Tuple[int, int, int],
                    expansion_factor: float = 0.1) -> Tuple[int, int, int, int]:
        """
        Expande el bounding box para incluir más contexto.
        
        Args:
            bbox: Bounding box original
            image_shape: Dimensiones de la imagen
            expansion_factor: Factor de expansión (0.1 = 10%)
            
        Returns:
            Bounding box expandido
        """
        x1, y1, x2, y2 = bbox
        h, w = image_shape[:2]
        
        # Calcular dimensiones del bbox
        bbox_width = x2 - x1
        bbox_height = y2 - y1
        
        # Calcular expansión
        expand_x = int(bbox_width * expansion_factor)
        expand_y = int(bbox_height * expansion_factor)
        
        # Aplicar expansión con límites de imagen
        ex1 = max(0, x1 - expand_x)
        ey1 = max(0, y1 - expand_y)
        ex2 = min(w, x2 + expand_x)
        ey2 = min(h, y2 + expand_y)
        
        return (ex1, ey1, ex2, ey2)
    
    def _create_smart_mask(self, 
                          roi: np.ndarray, 
                          original_bbox: Tuple[int, int, int, int],
                          expanded_bbox: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Crea una máscara inteligente usando segmentación avanzada.
        
        Args:
            roi: Región de interés
            original_bbox: Bounding box original
            expanded_bbox: Bounding box expandido
            
        Returns:
            Máscara binaria
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
            
            # Aplicar filtro gaussiano para suavizar
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detectar bordes usando Canny
            edges = cv2.Canny(blurred, 50, 150)
            
            # Dilatar bordes para cerrar contornos
            kernel = np.ones((3, 3), np.uint8)
            edges = cv2.dilate(edges, kernel, iterations=1)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if len(contours) == 0:
                # Fallback: crear máscara rectangular
                mask = np.zeros(gray.shape, dtype=np.uint8)
                h, w = gray.shape
                cv2.rectangle(mask, (w//4, h//4), (3*w//4, 3*h//4), 255, -1)
                return mask
            
            # Encontrar el contorno más grande
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Crear máscara basada en el contorno
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.fillPoly(mask, [largest_contour], 255)
            
            # Aplicar operaciones morfológicas para suavizar
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Suavizar bordes si está habilitado
            if self.feather_edges:
                mask = self._feather_mask_edges(mask)
            
            return mask
            
        except Exception as e:
            logger.error(f"Error creando máscara inteligente: {e}")
            # Fallback: máscara rectangular
            mask = np.zeros(roi.shape[:2], dtype=np.uint8)
            h, w = mask.shape
            cv2.rectangle(mask, (w//4, h//4), (3*w//4, 3*h//4), 255, -1)
            return mask
    
    def _feather_mask_edges(self, mask: np.ndarray) -> np.ndarray:
        """
        Suaviza los bordes de la máscara para transición suave.
        
        Args:
            mask: Máscara binaria
            
        Returns:
            Máscara suavizada
        """
        try:
            # Crear kernel gaussiano para suavizado
            kernel_size = self.blur_radius
            if kernel_size % 2 == 0:
                kernel_size += 1
            
            # Aplicar desenfoque gaussiano
            blurred_mask = cv2.GaussianBlur(mask.astype(np.float32), 
                                          (kernel_size, kernel_size), 
                                          kernel_size / 3)
            
            # Normalizar a rango 0-255
            feathered_mask = (blurred_mask * 255).astype(np.uint8)
            
            return feathered_mask
            
        except Exception as e:
            logger.error(f"Error suavizando bordes: {e}")
            return mask
    
    def _apply_smart_crop(self, roi: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Aplica recorte inteligente usando la máscara.
        
        Args:
            roi: Región de interés
            mask: Máscara binaria
            
        Returns:
            Imagen recortada
        """
        try:
            # Normalizar máscara a rango 0-1
            mask_normalized = mask.astype(np.float32) / 255.0
            
            # Aplicar máscara a cada canal
            if len(roi.shape) == 3:
                cropped = roi.copy().astype(np.float32)
                for i in range(roi.shape[2]):
                    cropped[:, :, i] *= mask_normalized
                cropped = cropped.astype(np.uint8)
            else:
                cropped = (roi.astype(np.float32) * mask_normalized).astype(np.uint8)
            
            return cropped
            
        except Exception as e:
            logger.error(f"Error aplicando recorte inteligente: {e}")
            return roi
    
    def _create_transparent_background(self, 
                                     cropped_image: np.ndarray, 
                                     mask: np.ndarray) -> np.ndarray:
        """
        Crea imagen con fondo transparente estilo iPhone.
        
        Args:
            cropped_image: Imagen recortada
            mask: Máscara binaria
            
        Returns:
            Imagen RGBA con transparencia
        """
        try:
            # Convertir a RGBA
            if len(cropped_image.shape) == 3:
                rgba_image = cv2.cvtColor(cropped_image, cv2.COLOR_RGB2RGBA)
            else:
                rgba_image = cv2.cvtColor(cropped_image, cv2.COLOR_GRAY2RGBA)
            
            # Normalizar máscara
            mask_normalized = mask.astype(np.float32) / 255.0
            
            # Aplicar transparencia
            rgba_image[:, :, 3] = (mask_normalized * 255).astype(np.uint8)
            
            # Aplicar transparencia de fondo si se especifica
            if self.background_alpha > 0:
                background_mask = 1.0 - mask_normalized
                rgba_image[:, :, 3] = np.maximum(
                    rgba_image[:, :, 3],
                    (background_mask * self.background_alpha * 255).astype(np.uint8)
                )
            
            return rgba_image
            
        except Exception as e:
            logger.error(f"Error creando fondo transparente: {e}")
            return cropped_image
    
    def _calculate_quality_metrics(self, mask: np.ndarray, confidence: float) -> Dict[str, float]:
        """
        Calcula métricas de calidad del recorte.
        
        Args:
            mask: Máscara binaria
            confidence: Confianza de detección
            
        Returns:
            Dict con métricas de calidad
        """
        try:
            # Calcular área de la máscara
            mask_area = np.sum(mask > 0)
            total_area = mask.shape[0] * mask.shape[1]
            area_ratio = mask_area / total_area
            
            # Calcular compacidad (perímetro² / área)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 0:
                largest_contour = max(contours, key=cv2.contourArea)
                perimeter = cv2.arcLength(largest_contour, True)
                compactness = (perimeter ** 2) / max(mask_area, 1)
            else:
                compactness = 0
            
            # Calcular calidad general
            quality_score = min(1.0, confidence * area_ratio * (1.0 / (1.0 + compactness / 1000)))
            
            return {
                'quality_score': float(quality_score),
                'area_ratio': float(area_ratio),
                'compactness': float(compactness),
                'detection_confidence': float(confidence),
                'mask_area': int(mask_area),
                'total_area': int(total_area)
            }
            
        except Exception as e:
            logger.error(f"Error calculando métricas de calidad: {e}")
            return {
                'quality_score': 0.0,
                'area_ratio': 0.0,
                'compactness': 0.0,
                'detection_confidence': float(confidence),
                'mask_area': 0,
                'total_area': 0
            }


class WeightPredictorYOLO:
    """
    Predictor de peso especializado usando YOLOv8.
    
    Combina detección de objetos, recorte inteligente y predicción de peso
    para análisis completo de granos de cacao.
    """
    
    def __init__(self, 
                 model_path: Optional[str] = None,
                 device: str = 'auto',
                 confidence_threshold: float = 0.5,
                 enable_smart_crop: bool = True):
        """
        Inicializa el predictor de peso YOLOv8.
        
        Args:
            model_path: Ruta al modelo entrenado
            device: Device para inferencia
            confidence_threshold: Umbral de confianza mínimo
            enable_smart_crop: Si habilitar recorte inteligente
        """
        if not YOLO_AVAILABLE:
            raise ImportError("Ultralytics YOLO no está disponible. Instalar con: pip install ultralytics")
        
        self.device = self._setup_device(device)
        self.confidence_threshold = confidence_threshold
        self.enable_smart_crop = enable_smart_crop
        
        # Configuración del modelo
        self.model_path = model_path or self._get_default_model_path()
        self.model = None
        self.is_loaded = False
        
        # Procesador de recorte inteligente
        self.smart_crop_processor = SmartCropProcessor() if enable_smart_crop else None
        
        # Configuración de calibración
        self.calibration_data = self._load_calibration_data()
        
        # Estadísticas de uso
        self.prediction_count = 0
        self.total_inference_time = 0.0
        
        logger.info(f"WeightPredictorYOLO inicializado (device={self.device}, smart_crop={enable_smart_crop})")
    
    def _setup_device(self, device: str) -> str:
        """Configura el device para inferencia."""
        if device == 'auto':
            if torch.cuda.is_available():
                return 'cuda'
            else:
                return 'cpu'
        return device
    
    def _get_default_model_path(self) -> str:
        """Obtiene la ruta por defecto del modelo YOLOv8."""
        models_dir = Path(__file__).parent.parent / 'models' / 'weight_predictor_yolo'
        models_dir.mkdir(parents=True, exist_ok=True)
        return str(models_dir / 'weight_yolo.pt')
    
    def _load_calibration_data(self) -> Dict[str, Any]:
        """Carga datos de calibración para conversión de píxeles a milímetros."""
        calibration_file = Path(__file__).parent.parent / 'models' / 'weight_predictor_yolo' / 'calibration.json'
        
        if calibration_file.exists():
            try:
                with open(calibration_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error cargando calibración: {e}")
        
        # Valores por defecto
        return {
            'pixels_per_mm': YOLO_CALIBRATION['default_pixels_per_mm'],
            'reference_object_size_mm': YOLO_CALIBRATION['reference_object_size_mm'],
            'calibration_date': None,
            'calibration_method': 'default'
        }
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Carga el modelo YOLOv8 entrenado.
        
        Args:
            model_path: Ruta al modelo
            
        Returns:
            bool: True si se cargó exitosamente
        """
        try:
            model_path = model_path or self.model_path
            
            if not Path(model_path).exists():
                logger.error(f"Modelo YOLOv8 no encontrado: {model_path}")
                return False
            
            self.model = YOLO(model_path)
            self.model.to(self.device)
            self.is_loaded = True
            
            logger.info(f"Modelo YOLOv8 cargado desde: {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error cargando modelo YOLOv8: {e}")
            self.is_loaded = False
            return False
    
    @performance_profiler.profile_function("yolo_weight_prediction")
    def predict_weight(self, 
                     image_input: Union[str, Path, np.ndarray, Image.Image],
                     return_cropped_image: bool = False,
                     return_transparent_image: bool = False) -> Dict[str, Any]:
        """
        Predice peso y dimensiones desde una imagen usando YOLOv8.
        
        Args:
            image_input: Imagen de entrada
            return_cropped_image: Si devolver imagen recortada
            return_transparent_image: Si devolver imagen con fondo transparente
            
        Returns:
            Dict con predicciones completas
        """
        start_time = datetime.now()
        
        try:
            if not self.is_loaded:
                if not self.load_model():
                    raise RuntimeError("No se pudo cargar el modelo YOLOv8")
            
            # Preprocesar imagen
            image_array = self._preprocess_image(image_input)
            
            # Realizar detección YOLOv8
            results = self.model(
                image_array,
                conf=self.confidence_threshold,
                verbose=False
            )
            
            # Procesar resultados
            prediction_result = self._process_detection_results(
                results, 
                image_array,
                return_cropped_image,
                return_transparent_image
            )
            
            # Actualizar estadísticas
            self.prediction_count += 1
            processing_time = (datetime.now() - start_time).total_seconds()
            self.total_inference_time += processing_time
            prediction_result['processing_time'] = processing_time
            
            logger.info(f"Predicción YOLOv8 completada en {processing_time:.3f}s")
            
            return prediction_result
            
        except Exception as e:
            logger.error(f"Error en predicción YOLOv8: {e}")
            return self._get_fallback_prediction(str(e))
    
    def _preprocess_image(self, image_input: Union[str, Path, np.ndarray, Image.Image]) -> np.ndarray:
        """
        Preprocesa la imagen para YOLOv8.
        
        Args:
            image_input: Imagen de entrada
            
        Returns:
            np.ndarray: Imagen preprocesada
        """
        try:
            # Convertir a numpy array
            if isinstance(image_input, (str, Path)):
                image_array = cv2.imread(str(image_input))
                if image_array is None:
                    raise ValueError(f"No se pudo cargar la imagen: {image_input}")
                image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            
            elif isinstance(image_input, Image.Image):
                image_array = np.array(image_input)
                if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                    pass  # Ya está en RGB
                else:
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            
            elif isinstance(image_input, np.ndarray):
                image_array = image_input.copy()
                if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                    pass  # Ya está en RGB
                else:
                    image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
            
            else:
                raise ValueError(f"Tipo de imagen no soportado: {type(image_input)}")
            
            # Validar formato
            if len(image_array.shape) != 3 or image_array.shape[2] != 3:
                raise ValueError("La imagen debe ser RGB de 3 canales")
            
            return image_array
            
        except Exception as e:
            raise ValueError(f"Error preprocesando imagen: {e}")
    
    def _process_detection_results(self, 
                                 results: List, 
                                 image_array: np.ndarray,
                                 return_cropped_image: bool,
                                 return_transparent_image: bool) -> Dict[str, Any]:
        """
        Procesa los resultados de detección YOLOv8.
        
        Args:
            results: Resultados de YOLOv8
            image_array: Imagen original
            return_cropped_image: Si incluir imagen recortada
            return_transparent_image: Si incluir imagen transparente
            
        Returns:
            Dict: Resultados procesados
        """
        try:
            if not results or len(results) == 0:
                return self._get_no_detection_result()
            
            # Obtener la mejor detección
            best_detection = self._get_best_detection(results[0])
            
            if best_detection is None:
                return self._get_no_detection_result()
            
            # Extraer información de la detección
            bbox = best_detection.boxes.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2]
            confidence = float(best_detection.boxes.conf[0].cpu().numpy())
            
            # Calcular dimensiones en píxeles
            width_pixels = bbox[2] - bbox[0]
            height_pixels = bbox[3] - bbox[1]
            
            # Convertir a milímetros usando calibración
            width_mm = self._pixels_to_mm(width_pixels)
            height_mm = self._pixels_to_mm(height_pixels)
            
            # Estimar grosor
            thickness_mm = self._estimate_thickness(width_mm, height_mm)
            
            # Predecir peso
            predicted_weight = self._predict_weight_from_dimensions(width_mm, height_mm, thickness_mm)
            
            # Procesar recorte inteligente si está habilitado
            smart_crop_result = None
            if self.enable_smart_crop and self.smart_crop_processor:
                smart_crop_result = self.smart_crop_processor.process_detection(
                    image_array, bbox, confidence
                )
            
            # Preparar resultado
            result = {
                'peso_estimado': round(predicted_weight, 3),
                'altura_mm': round(height_mm, 2),
                'ancho_mm': round(width_mm, 2),
                'grosor_mm': round(thickness_mm, 2),
                'nivel_confianza': round(confidence, 3),
                'detection_info': {
                    'bbox_pixels': bbox.tolist(),
                    'width_pixels': int(width_pixels),
                    'height_pixels': int(height_pixels),
                    'detection_method': 'yolo_v8',
                    'smart_crop_enabled': self.enable_smart_crop
                },
                'method': 'yolo_v8',
                'success': True
            }
            
            # Agregar información de recorte inteligente
            if smart_crop_result and smart_crop_result['processing_successful']:
                result['smart_crop'] = {
                    'quality_metrics': smart_crop_result['quality_metrics'],
                    'expanded_bbox': smart_crop_result['expanded_bbox'],
                    'processing_successful': True
                }
                
                # Agregar imágenes si se solicitan
                if return_cropped_image and smart_crop_result['cropped_image'] is not None:
                    result['cropped_image'] = self._encode_image(smart_crop_result['cropped_image'])
                
                if return_transparent_image and smart_crop_result['transparent_image'] is not None:
                    result['transparent_image'] = self._encode_image(smart_crop_result['transparent_image'])
            else:
                result['smart_crop'] = {
                    'processing_successful': False,
                    'error': smart_crop_result.get('error', 'Recorte inteligente no disponible') if smart_crop_result else 'Procesador no habilitado'
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Error procesando resultados de detección: {e}")
            return self._get_fallback_prediction(str(e))
    
    def _get_best_detection(self, result) -> Optional[Any]:
        """Obtiene la mejor detección basada en confianza."""
        if not hasattr(result, 'boxes') or result.boxes is None or len(result.boxes) == 0:
            return None
        
        # Obtener la detección con mayor confianza
        confidences = result.boxes.conf.cpu().numpy()
        best_idx = np.argmax(confidences)
        
        if confidences[best_idx] >= self.confidence_threshold:
            return result
        else:
            return None
    
    def _pixels_to_mm(self, pixels: float) -> float:
        """Convierte píxeles a milímetros usando datos de calibración."""
        return pixels / self.calibration_data['pixels_per_mm']
    
    def _estimate_thickness(self, width_mm: float, height_mm: float) -> float:
        """
        Estima el grosor del grano basado en ancho y alto.
        
        Usa una relación empírica basada en la forma típica de granos de cacao.
        """
        # Relación empírica: grosor ≈ 0.4 * min(ancho, alto)
        min_dimension = min(width_mm, height_mm)
        estimated_thickness = 0.4 * min_dimension
        
        # Aplicar límites razonables (3-12 mm para granos de cacao)
        estimated_thickness = max(3.0, min(12.0, estimated_thickness))
        
        return estimated_thickness
    
    def _predict_weight_from_dimensions(self, width_mm: float, height_mm: float, thickness_mm: float) -> float:
        """
        Predice el peso del grano basado en sus dimensiones.
        
        Usa la configuración de YOLO_WEIGHT_PREDICTION.
        """
        # Fórmula empírica: peso ≈ densidad * volumen
        # Volumen aproximado como elipsoide: V = (4/3) * π * a * b * c
        volume_mm3 = (4/3) * np.pi * (width_mm/2) * (height_mm/2) * (thickness_mm/2)
        
        # Usar configuración
        density = YOLO_WEIGHT_PREDICTION['density_g_per_cm3']  # g/cm³
        density_g_per_mm3 = density * 0.001  # Convertir a g/mm³
        
        # Peso estimado
        estimated_weight = volume_mm3 * density_g_per_mm3
        
        # Aplicar factor de corrección
        shape_factor = YOLO_WEIGHT_PREDICTION['shape_factor']
        estimated_weight *= shape_factor
        
        # Aplicar límites razonables
        min_weight = YOLO_WEIGHT_PREDICTION['min_weight_g']
        max_weight = YOLO_WEIGHT_PREDICTION['max_weight_g']
        estimated_weight = max(min_weight, min(max_weight, estimated_weight))
        
        return estimated_weight
    
    def _encode_image(self, image_array: np.ndarray) -> str:
        """
        Codifica imagen como base64 para respuesta JSON.
        
        Args:
            image_array: Imagen como array numpy
            
        Returns:
            str: Imagen codificada en base64
        """
        try:
            # Convertir a formato PIL
            if len(image_array.shape) == 3 and image_array.shape[2] == 4:
                # RGBA
                pil_image = Image.fromarray(image_array, 'RGBA')
            elif len(image_array.shape) == 3:
                # RGB
                pil_image = Image.fromarray(image_array, 'RGB')
            else:
                # Escala de grises
                pil_image = Image.fromarray(image_array, 'L')
            
            # Convertir a bytes
            import io
            buffer = io.BytesIO()
            pil_image.save(buffer, format='PNG')
            image_bytes = buffer.getvalue()
            
            # Codificar en base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            return f"data:image/png;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Error codificando imagen: {e}")
            return ""
    
    def _get_no_detection_result(self) -> Dict[str, Any]:
        """Devuelve resultado cuando no se detecta ningún grano."""
        return {
            'peso_estimado': 0.0,
            'altura_mm': 0.0,
            'ancho_mm': 0.0,
            'grosor_mm': 0.0,
            'nivel_confianza': 0.0,
            'detection_info': {
                'bbox_pixels': [0, 0, 0, 0],
                'width_pixels': 0,
                'height_pixels': 0,
                'detection_method': 'yolo_v8',
                'status': 'no_detection'
            },
            'method': 'yolo_v8',
            'success': False,
            'error': 'No se detectó ningún grano de cacao',
            'smart_crop': {
                'processing_successful': False,
                'error': 'No hay detección para procesar'
            }
        }
    
    def _get_fallback_prediction(self, error_message: str) -> Dict[str, Any]:
        """Devuelve predicción de fallback en caso de error."""
        return {
            'peso_estimado': 1.0,  # Valor por defecto
            'altura_mm': 10.0,
            'ancho_mm': 8.0,
            'grosor_mm': 4.0,
            'nivel_confianza': 0.1,
            'detection_info': {
                'bbox_pixels': [0, 0, 0, 0],
                'width_pixels': 0,
                'height_pixels': 0,
                'detection_method': 'yolo_v8',
                'status': 'error'
            },
            'method': 'yolo_v8',
            'success': False,
            'error': error_message,
            'smart_crop': {
                'processing_successful': False,
                'error': error_message
            }
        }
    
    def calibrate_model(self, reference_images: List[str], reference_sizes_mm: List[float]) -> bool:
        """
        Calibra el modelo usando imágenes de referencia con tamaños conocidos.
        
        Args:
            reference_images: Lista de rutas a imágenes de referencia
            reference_sizes_mm: Lista de tamaños reales en mm
            
        Returns:
            bool: True si la calibración fue exitosa
        """
        try:
            logger.info("Iniciando calibración del modelo YOLOv8")
            
            pixel_sizes = []
            
            for img_path, real_size_mm in zip(reference_images, reference_sizes_mm):
                # Cargar imagen
                image_array = self._preprocess_image(img_path)
                
                # Realizar detección
                results = self.model(image_array, conf=0.3, verbose=False)
                
                if results and len(results) > 0 and hasattr(results[0], 'boxes') and results[0].boxes is not None:
                    # Obtener la mejor detección
                    best_detection = self._get_best_detection(results[0])
                    
                    if best_detection:
                        bbox = best_detection.boxes.xyxy[0].cpu().numpy()
                        width_pixels = bbox[2] - bbox[0]
                        height_pixels = bbox[3] - bbox[1]
                        
                        # Usar la dimensión promedio
                        avg_pixels = (width_pixels + height_pixels) / 2
                        pixels_per_mm = avg_pixels / real_size_mm
                        
                        pixel_sizes.append(pixels_per_mm)
            
            if len(pixel_sizes) > 0:
                # Calcular promedio
                avg_pixels_per_mm = np.mean(pixel_sizes)
                
                # Actualizar calibración
                self.calibration_data['pixels_per_mm'] = avg_pixels_per_mm
                self.calibration_data['calibration_date'] = datetime.now().isoformat()
                self.calibration_data['calibration_method'] = 'automatic'
                
                # Guardar calibración
                calibration_file = Path(__file__).parent.parent / 'models' / 'weight_predictor_yolo' / 'calibration.json'
                with open(calibration_file, 'w') as f:
                    json.dump(self.calibration_data, f, indent=2)
                
                logger.info(f"Calibración completada: {avg_pixels_per_mm:.2f} píxeles/mm")
                return True
            else:
                logger.error("No se pudieron obtener datos de calibración")
                return False
                
        except Exception as e:
            logger.error(f"Error en calibración: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Obtiene información del modelo."""
        return {
            'model_name': 'WeightPredictorYOLO',
            'model_path': self.model_path,
            'device': self.device,
            'is_loaded': self.is_loaded,
            'confidence_threshold': self.confidence_threshold,
            'smart_crop_enabled': self.enable_smart_crop,
            'calibration_data': self.calibration_data,
            'prediction_count': self.prediction_count,
            'avg_inference_time': self.total_inference_time / max(1, self.prediction_count),
            'yolo_available': YOLO_AVAILABLE
        }
    
    def warmup(self) -> bool:
        """Precarga el modelo para mejor rendimiento."""
        try:
            if not self.is_loaded:
                return self.load_model()
            
            # Realizar una predicción de prueba
            dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)
            self.predict_weight(dummy_image)
            
            logger.info("Modelo YOLOv8 precargado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error en precarga del modelo YOLOv8: {e}")
            return False


def create_weight_predictor(model_path: Optional[str] = None, **kwargs) -> WeightPredictorYOLO:
    """
    Función de conveniencia para crear una instancia del predictor de peso.
    
    Args:
        model_path: Ruta al modelo entrenado
        **kwargs: Argumentos adicionales
        
    Returns:
        WeightPredictorYOLO: Instancia del predictor
    """
    return WeightPredictorYOLO(model_path=model_path, **kwargs)


def load_weight_predictor(model_name: str = 'yolo_weight_model') -> WeightPredictorYOLO:
    """
    Carga el predictor de peso desde la configuración.
    
    Args:
        model_name: Nombre del modelo en configuración
        
    Returns:
        WeightPredictorYOLO: Predictor cargado
    """
    try:
        config = MODEL_CONFIGS.get(model_name, {})
        model_path = config.get('model_path')
        
        if model_path:
            return WeightPredictorYOLO(model_path=str(model_path))
        else:
            return WeightPredictorYOLO()
        
    except Exception as e:
        logger.error(f"Error cargando predictor de peso: {e}")
        return WeightPredictorYOLO()


if __name__ == "__main__":
    # Ejemplo de uso
    print("Inicializando predictor de peso YOLOv8...")
    
    # Crear predictor
    predictor = create_weight_predictor(enable_smart_crop=True)
    
    # Mostrar información
    info = predictor.get_model_info()
    print(f"Predictor creado: {info['model_name']}")
    print(f"YOLO disponible: {info['yolo_available']}")
    print(f"Device: {info['device']}")
    print(f"Recorte inteligente: {info['smart_crop_enabled']}")
    
    # Intentar cargar modelo si existe
    if Path(predictor.model_path).exists():
        if predictor.load_model():
            print("✓ Modelo YOLOv8 cargado exitosamente")
        else:
            print("✗ Error cargando modelo YOLOv8")
    else:
        print(f"✗ Modelo no encontrado: {predictor.model_path}")
        print("Ejecutar entrenamiento para crear el modelo")
    
    print("\nEjemplo de uso:")
    print("1. predictor.predict_weight('path/to/image.jpg')")
    print("2. predictor.predict_weight('image.jpg', return_transparent_image=True)")
    print("3. predictor.calibrate_model(['ref1.jpg'], [20.0])")
    print("4. predictor.get_model_info()")
