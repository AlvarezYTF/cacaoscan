"""
Modelo YOLOv8 para detección y predicción de peso de granos de cacao.

Este módulo implementa un modelo YOLOv8 especializado que:
1. Detecta granos de cacao en imágenes
2. Calcula dimensiones físicas (alto, ancho, grosor) en milímetros
3. Predice el peso estimado en gramos usando las dimensiones

Integra con el sistema existente de CacaoScan sin duplicar funcionalidad.
"""

import os
import logging
import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional, Any, Union
from pathlib import Path
import torch
from PIL import Image
import json

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

from .config import MODEL_CONFIGS, get_model_config
from .utils import performance_profiler, validate_image_format

# Configurar logging
logger = logging.getLogger('ml')


class CacaoYOLOModel:
    """
    Modelo YOLOv8 especializado para detección y predicción de peso de granos de cacao.
    
    Combina detección de objetos con estimación de dimensiones físicas y predicción de peso.
    """
    
    def __init__(self, 
                 model_path: Optional[str] = None,
                 device: str = 'auto',
                 confidence_threshold: float = 0.5,
                 iou_threshold: float = 0.45):
        """
        Inicializa el modelo YOLOv8 para cacao.
        
        Args:
            model_path (str, optional): Ruta al modelo entrenado
            device (str): Device para inferencia ('auto', 'cpu', 'cuda')
            confidence_threshold (float): Umbral de confianza mínimo
            iou_threshold (float): Umbral IoU para NMS
        """
        if not YOLO_AVAILABLE:
            raise ImportError("Ultralytics YOLO no está disponible. Instalar con: pip install ultralytics")
        
        self.device = self._setup_device(device)
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        
        # Configuración del modelo
        self.model_path = model_path or self._get_default_model_path()
        self.model = None
        self.is_loaded = False
        
        # Configuración de calibración para dimensiones reales
        self.calibration_data = self._load_calibration_data()
        
        # Estadísticas de uso
        self.prediction_count = 0
        self.total_inference_time = 0.0
        
        logger.info(f"CacaoYOLOModel inicializado (device={self.device})")
    
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
        models_dir = Path(__file__).parent / 'models' / 'weight_predictor_yolo'
        models_dir.mkdir(parents=True, exist_ok=True)
        return str(models_dir / 'weight_yolo.pt')
    
    def _load_calibration_data(self) -> Dict[str, Any]:
        """Carga datos de calibración para conversión de píxeles a milímetros."""
        calibration_file = Path(__file__).parent / 'models' / 'weight_predictor_yolo' / 'calibration.json'
        
        if calibration_file.exists():
            try:
                with open(calibration_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error cargando calibración: {e}")
        
        # Valores por defecto (deben calibrarse con datos reales)
        return {
            'pixels_per_mm': 10.0,  # Píxeles por milímetro
            'reference_object_size_mm': 20.0,  # Tamaño de objeto de referencia
            'calibration_date': None,
            'calibration_method': 'manual'
        }
    
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """
        Carga el modelo YOLOv8 entrenado.
        
        Args:
            model_path (str, optional): Ruta al modelo
            
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
    
    @performance_profiler.profile_function("yolo_prediction")
    def predict_weight_from_image(self, 
                                image_input: Union[str, Path, np.ndarray, Image.Image],
                                return_detection_image: bool = False) -> Dict[str, Any]:
        """
        Predice peso y dimensiones desde una imagen usando YOLOv8.
        
        Args:
            image_input: Imagen de entrada (ruta, array numpy, PIL Image)
            return_detection_image: Si devolver imagen con detecciones
            
        Returns:
            Dict con predicciones: {
                'peso_estimado': float,
                'altura_mm': float,
                'ancho_mm': float, 
                'grosor_mm': float,
                'nivel_confianza': float,
                'detection_info': {...},
                'processing_time': float
            }
        """
        start_time = torch.cuda.Event(enable_timing=True) if self.device == 'cuda' else None
        end_time = torch.cuda.Event(enable_timing=True) if self.device == 'cuda' else None
        
        if start_time:
            start_time.record()
        else:
            start_time = torch.cuda.Event(enable_timing=True)
            start_time.record()
        
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
                iou=self.iou_threshold,
                verbose=False
            )
            
            # Procesar resultados
            prediction_result = self._process_detection_results(
                results, 
                image_array,
                return_detection_image
            )
            
            # Actualizar estadísticas
            self.prediction_count += 1
            
            if end_time:
                end_time.record()
                torch.cuda.synchronize()
                processing_time = start_time.elapsed_time(end_time) / 1000.0  # Convertir a segundos
            else:
                processing_time = 0.1  # Estimación
            
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
                                 return_detection_image: bool) -> Dict[str, Any]:
        """
        Procesa los resultados de detección YOLOv8.
        
        Args:
            results: Resultados de YOLOv8
            image_array: Imagen original
            return_detection_image: Si incluir imagen con detecciones
            
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
            
            # Estimar grosor (usando relación empírica)
            thickness_mm = self._estimate_thickness(width_mm, height_mm)
            
            # Predecir peso usando fórmula empírica
            predicted_weight = self._predict_weight_from_dimensions(width_mm, height_mm, thickness_mm)
            
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
                    'detection_method': 'yolo_v8'
                },
                'method': 'yolo_v8',
                'success': True
            }
            
            # Agregar imagen con detecciones si se solicita
            if return_detection_image:
                detection_image = self._create_detection_image(image_array, results[0])
                result['detection_image'] = detection_image
            
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
        
        Usa una fórmula empírica basada en el dataset de entrenamiento.
        """
        # Fórmula empírica: peso ≈ densidad * volumen
        # Volumen aproximado como elipsoide: V = (4/3) * π * a * b * c
        volume_mm3 = (4/3) * np.pi * (width_mm/2) * (height_mm/2) * (thickness_mm/2)
        
        # Densidad promedio del cacao: ~1.0 g/cm³ = 0.001 g/mm³
        density_g_per_mm3 = 0.001
        
        # Peso estimado
        estimated_weight = volume_mm3 * density_g_per_mm3
        
        # Aplicar factor de corrección basado en forma irregular
        shape_factor = 0.8  # Los granos no son elipsoides perfectos
        estimated_weight *= shape_factor
        
        # Aplicar límites razonables (0.5-3.0g para granos de cacao)
        estimated_weight = max(0.5, min(3.0, estimated_weight))
        
        return estimated_weight
    
    def _create_detection_image(self, image_array: np.ndarray, result) -> np.ndarray:
        """Crea una imagen con las detecciones visualizadas."""
        try:
            # Crear copia de la imagen
            detection_image = image_array.copy()
            
            # Dibujar bounding boxes
            if hasattr(result, 'boxes') and result.boxes is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()
                
                for box, conf in zip(boxes, confidences):
                    if conf >= self.confidence_threshold:
                        x1, y1, x2, y2 = box.astype(int)
                        
                        # Dibujar rectángulo
                        cv2.rectangle(detection_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        
                        # Dibujar etiqueta de confianza
                        label = f"Cacao: {conf:.2f}"
                        cv2.putText(detection_image, label, (x1, y1-10), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            return detection_image
            
        except Exception as e:
            logger.error(f"Error creando imagen de detección: {e}")
            return image_array
    
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
            'error': 'No se detectó ningún grano de cacao'
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
            'error': error_message
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
                self.calibration_data['calibration_date'] = str(np.datetime64('now'))
                self.calibration_data['calibration_method'] = 'automatic'
                
                # Guardar calibración
                calibration_file = Path(__file__).parent / 'models' / 'weight_predictor_yolo' / 'calibration.json'
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
            'model_name': 'CacaoYOLOModel',
            'model_path': self.model_path,
            'device': self.device,
            'is_loaded': self.is_loaded,
            'confidence_threshold': self.confidence_threshold,
            'iou_threshold': self.iou_threshold,
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
            self.predict_weight_from_image(dummy_image)
            
            logger.info("Modelo YOLOv8 precargado exitosamente")
            return True
            
        except Exception as e:
            logger.error(f"Error en precarga del modelo YOLOv8: {e}")
            return False


def create_yolo_model(model_path: Optional[str] = None, **kwargs) -> CacaoYOLOModel:
    """
    Función de conveniencia para crear una instancia del modelo YOLOv8.
    
    Args:
        model_path (str, optional): Ruta al modelo entrenado
        **kwargs: Argumentos adicionales
        
    Returns:
        CacaoYOLOModel: Instancia del modelo
    """
    return CacaoYOLOModel(model_path=model_path, **kwargs)


def load_yolo_model(model_name: str = 'yolo_weight_model') -> CacaoYOLOModel:
    """
    Carga el modelo YOLOv8 desde la configuración.
    
    Args:
        model_name (str): Nombre del modelo en configuración
        
    Returns:
        CacaoYOLOModel: Modelo cargado
    """
    try:
        config = get_model_config(model_name)
        model_path = config['model_path']
        
        return CacaoYOLOModel(model_path=str(model_path))
        
    except Exception as e:
        logger.error(f"Error cargando modelo YOLOv8: {e}")
        return CacaoYOLOModel()


if __name__ == "__main__":
    # Ejemplo de uso
    print("Inicializando modelo YOLOv8 para cacao...")
    
    # Crear modelo
    model = create_yolo_model()
    
    # Mostrar información
    info = model.get_model_info()
    print(f"Modelo creado: {info['model_name']}")
    print(f"YOLO disponible: {info['yolo_available']}")
    print(f"Device: {info['device']}")
    
    # Intentar cargar modelo si existe
    if Path(model.model_path).exists():
        if model.load_model():
            print("✓ Modelo YOLOv8 cargado exitosamente")
        else:
            print("✗ Error cargando modelo YOLOv8")
    else:
        print(f"✗ Modelo no encontrado: {model.model_path}")
        print("Ejecutar entrenamiento para crear el modelo")
    
    print("\nEjemplo de uso:")
    print("1. model.predict_weight_from_image('path/to/image.jpg')")
    print("2. model.calibrate_model(['ref1.jpg'], [20.0])")
    print("3. model.get_model_info()")
