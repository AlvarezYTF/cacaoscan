"""
Servicio de predicción centralizado para CacaoScan.

Este módulo proporciona una interfaz unificada para realizar predicciones
usando tanto el modelo de visión (CNN) como el modelo de regresión,
integrando ambos flujos para análisis completo de granos de cacao.
"""

import os
import logging
import time
import numpy as np
from typing import Dict, List, Union, Optional, Any, Tuple
from pathlib import Path
import io
from PIL import Image

# Configurar Django si no está configurado
import django
if not django.apps.apps.ready:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from .model_manager import get_vision_model, get_regression_model, model_manager
from .data_preprocessing import preprocess_single_image
from .utils import performance_profiler, validate_image_format, get_image_info
from .config import IMAGE_PREPROCESSING, EVALUATION_METRICS
from .yolo_model import CacaoYOLOModel, create_yolo_model
from .prediction.predict_weight_yolo import WeightPredictorYOLO, create_weight_predictor

# Configurar logging
logger = logging.getLogger('ml')


class PredictionError(Exception):
    """Excepción personalizada para errores de predicción."""
    pass


class CacaoPredictionService:
    """
    Servicio centralizado para predicciones de granos de cacao.
    
    Integra el modelo de visión CNN, modelo de regresión y YOLOv8 para
    proporcionar predicciones completas desde imágenes.
    """
    
    def __init__(self, 
                 enable_caching: bool = True,
                 device: str = 'auto',
                 confidence_threshold: float = 0.7,
                 enable_yolo: bool = True):
        """
        Inicializa el servicio de predicción.
        
        Args:
            enable_caching (bool): Si habilitar cache de resultados
            device (str): Device para modelos PyTorch
            confidence_threshold (float): Umbral de confianza mínimo
            enable_yolo (bool): Si habilitar modelo YOLOv8
        """
        self.enable_caching = enable_caching
        self.device = device
        self.confidence_threshold = confidence_threshold
        self.enable_yolo = enable_yolo
        
        # Cache de resultados
        self._prediction_cache = {} if enable_caching else None
        self._cache_stats = {'hits': 0, 'misses': 0}
        
        # Estadísticas de rendimiento
        self.prediction_stats = {
            'total_predictions': 0,
            'vision_predictions': 0,
            'regression_predictions': 0,
            'yolo_predictions': 0,
            'combined_predictions': 0,
            'avg_processing_time': 0.0,
            'errors': 0
        }
        
        # Configuración de preprocesamiento
        self.image_config = IMAGE_PREPROCESSING
        
        logger.info(f"CacaoPredictionService inicializado (device={device})")
    
    @performance_profiler.profile_function("vision_prediction")
    def predict_from_image(self, 
                          image_input: Union[str, Path, bytes, np.ndarray, Image.Image],
                          include_confidence: bool = True,
                          return_raw_output: bool = False) -> Dict[str, Any]:
        """
        Predice características físicas desde una imagen usando CNN.
        
        Args:
            image_input: Imagen (ruta, bytes, array numpy, PIL Image)
            include_confidence: Si incluir métricas de confianza
            return_raw_output: Si incluir salida cruda del modelo
            
        Returns:
            Dict con predicciones: {'width': float, 'height': float, 'thickness': float, 'weight': float}
        """
        start_time = time.time()
        
        try:
            # Verificar cache
            cache_key = self._get_cache_key(image_input, 'vision')
            if self.enable_caching and cache_key in self._prediction_cache:
                self._cache_stats['hits'] += 1
                logger.debug("Predicción obtenida desde cache")
                return self._prediction_cache[cache_key]
            
            self._cache_stats['misses'] += 1
            
            # Obtener modelo de visión
            vision_model = get_vision_model(device=self.device)
            if vision_model is None:
                raise PredictionError("Modelo de visión no disponible")
            
            # Preprocesar imagen
            processed_image = self._preprocess_image_for_vision(image_input)
            
            # Realizar predicción
            with performance_profiler.profile_function("vision_model_inference"):
                predictions = vision_model.predict_measurements(processed_image)
            
            # Formatear resultado
            result = self._format_vision_result(
                predictions, 
                include_confidence=include_confidence,
                return_raw_output=return_raw_output,
                processing_time=time.time() - start_time
            )
            
            # Guardar en cache
            if self.enable_caching:
                self._prediction_cache[cache_key] = result
            
            # Actualizar estadísticas
            self.prediction_stats['vision_predictions'] += 1
            self.prediction_stats['total_predictions'] += 1
            self._update_avg_processing_time(time.time() - start_time)
            
            logger.info(f"Predicción de visión completada en {time.time() - start_time:.3f}s")
            
            return result
            
        except Exception as e:
            self.prediction_stats['errors'] += 1
            logger.error(f"Error en predicción de visión: {e}")
            raise PredictionError(f"Error en predicción de visión: {e}")
    
    @performance_profiler.profile_function("regression_prediction")
    def predict_weight_from_dimensions(self, 
                                     width: float, 
                                     height: float, 
                                     thickness: float,
                                     include_confidence: bool = True) -> Dict[str, Any]:
        """
        Predice el peso usando el modelo de regresión.
        
        Args:
            width (float): Ancho en mm
            height (float): Alto en mm
            thickness (float): Grosor en mm
            include_confidence: Si incluir métricas de confianza
            
        Returns:
            Dict con predicción: {'predicted_weight': float, ...}
        """
        start_time = time.time()
        
        try:
            # Validar entrada
            if any(val <= 0 for val in [width, height, thickness]):
                raise PredictionError("Las dimensiones deben ser valores positivos")
            
            # Verificar cache
            cache_key = f"regression_{width}_{height}_{thickness}"
            if self.enable_caching and cache_key in self._prediction_cache:
                self._cache_stats['hits'] += 1
                return self._prediction_cache[cache_key]
            
            self._cache_stats['misses'] += 1
            
            # Obtener modelo de regresión
            regression_model = get_regression_model()
            if regression_model is None:
                raise PredictionError("Modelo de regresión no disponible")
            
            # Realizar predicción
            with performance_profiler.profile_function("regression_model_inference"):
                predicted_weight = regression_model.predict_single(width, height, thickness)
            
            # Formatear resultado
            result = self._format_regression_result(
                predicted_weight,
                width, height, thickness,
                include_confidence=include_confidence,
                processing_time=time.time() - start_time
            )
            
            # Guardar en cache
            if self.enable_caching:
                self._prediction_cache[cache_key] = result
            
            # Actualizar estadísticas
            self.prediction_stats['regression_predictions'] += 1
            self.prediction_stats['total_predictions'] += 1
            self._update_avg_processing_time(time.time() - start_time)
            
            logger.info(f"Predicción de regresión completada en {time.time() - start_time:.3f}s")
            
            return result
            
        except Exception as e:
            self.prediction_stats['errors'] += 1
            logger.error(f"Error en predicción de regresión: {e}")
            raise PredictionError(f"Error en predicción de regresión: {e}")
    
    @performance_profiler.profile_function("yolo_prediction")
    def predict_with_yolo(self, 
                         image_input: Union[str, Path, bytes, np.ndarray, Image.Image],
                         return_detection_image: bool = False) -> Dict[str, Any]:
        """
        Predice peso y dimensiones usando YOLOv8.
        
        Args:
            image_input: Imagen de entrada
            return_detection_image: Si devolver imagen con detecciones
            
        Returns:
            Dict con predicciones YOLOv8: {
                'peso_estimado': float,
                'altura_mm': float,
                'ancho_mm': float,
                'grosor_mm': float,
                'nivel_confianza': float,
                'detection_info': {...},
                'method': 'yolo_v8'
            }
        """
        start_time = time.time()
        
        try:
            if not self.enable_yolo:
                raise PredictionError("Modelo YOLOv8 no habilitado")
            
            logger.info("Iniciando predicción con YOLOv8")
            
            # Validar entrada
            if not validate_image_format(image_input):
                raise PredictionError("Formato de imagen no válido")
            
            # Generar clave de cache
            cache_key = None
            if self.enable_caching:
                cache_key = self._generate_cache_key(image_input, 'yolo')
                if cache_key in self._prediction_cache:
                    self._cache_stats['hits'] += 1
                    logger.info("Predicción YOLOv8 encontrada en cache")
                    return self._prediction_cache[cache_key]
                else:
                    self._cache_stats['misses'] += 1
            
            # Cargar modelo YOLOv8 si no está cargado
            if self.yolo_model is None:
                self.yolo_model = create_yolo_model(device=self.device)
                if not self.yolo_model.load_model():
                    raise PredictionError("No se pudo cargar el modelo YOLOv8")
            
            # Realizar predicción
            result = self.yolo_model.predict_weight_from_image(
                image_input, 
                return_detection_image=return_detection_image
            )
            
            # Agregar metadatos
            result.update({
                'processing_time': time.time() - start_time,
                'timestamp': time.time(),
                'model_version': 'yolo_v8',
                'device': self.device
            })
            
            # Guardar en cache
            if self.enable_caching and cache_key:
                self._prediction_cache[cache_key] = result
            
            # Actualizar estadísticas
            self.prediction_stats['yolo_predictions'] += 1
            self.prediction_stats['total_predictions'] += 1
            self._update_avg_processing_time(time.time() - start_time)
            
            logger.info(f"Predicción YOLOv8 completada en {time.time() - start_time:.3f}s")
            
            return result
            
        except Exception as e:
            self.prediction_stats['errors'] += 1
            logger.error(f"Error en predicción YOLOv8: {e}")
            raise PredictionError(f"Error en predicción YOLOv8: {e}")
    
    @performance_profiler.profile_function("smart_weight_prediction")
    def predict_weight_with_smart_crop(self, 
                                     image_input: Union[str, Path, bytes, np.ndarray, Image.Image],
                                     return_cropped_image: bool = False,
                                     return_transparent_image: bool = False) -> Dict[str, Any]:
        """
        Predice peso usando YOLOv8 con recorte inteligente estilo iPhone.
        
        Args:
            image_input: Imagen de entrada
            return_cropped_image: Si devolver imagen recortada
            return_transparent_image: Si devolver imagen con fondo transparente
            
        Returns:
            Dict con predicciones y imágenes procesadas
        """
        start_time = time.time()
        
        try:
            if not self.enable_yolo:
                raise PredictionError("Modelo YOLOv8 no habilitado")
            
            logger.info("Iniciando predicción con recorte inteligente YOLOv8")
            
            # Validar entrada
            if not validate_image_format(image_input):
                raise PredictionError("Formato de imagen no válido")
            
            # Generar clave de cache
            cache_key = None
            if self.enable_caching:
                cache_key = self._generate_cache_key(image_input, 'smart_yolo')
                if cache_key in self._prediction_cache:
                    self._cache_stats['hits'] += 1
                    logger.info("Predicción con recorte inteligente encontrada en cache")
                    return self._prediction_cache[cache_key]
                else:
                    self._cache_stats['misses'] += 1
            
            # Crear predictor especializado
            weight_predictor = create_weight_predictor(
                device=self.device,
                confidence_threshold=self.confidence_threshold,
                enable_smart_crop=True
            )
            
            # Cargar modelo si no está cargado
            if not weight_predictor.is_loaded:
                if not weight_predictor.load_model():
                    raise PredictionError("No se pudo cargar el modelo YOLOv8")
            
            # Realizar predicción con recorte inteligente
            result = weight_predictor.predict_weight(
                image_input,
                return_cropped_image=return_cropped_image,
                return_transparent_image=return_transparent_image
            )
            
            # Agregar metadatos
            result.update({
                'processing_time': time.time() - start_time,
                'timestamp': time.time(),
                'model_version': 'yolo_v8_smart_crop',
                'device': self.device,
                'smart_crop_enabled': True
            })
            
            # Guardar en cache
            if self.enable_caching and cache_key:
                self._prediction_cache[cache_key] = result
            
            # Actualizar estadísticas
            self.prediction_stats['yolo_predictions'] += 1
            self.prediction_stats['total_predictions'] += 1
            self._update_avg_processing_time(time.time() - start_time)
            
            logger.info(f"Predicción con recorte inteligente completada en {time.time() - start_time:.3f}s")
            
            return result
            
        except Exception as e:
            self.prediction_stats['errors'] += 1
            logger.error(f"Error en predicción con recorte inteligente: {e}")
            raise PredictionError(f"Error en predicción con recorte inteligente: {e}")
    
    @performance_profiler.profile_function("combined_prediction")
    def predict_complete_analysis(self, 
                                 image_input: Union[str, Path, bytes, np.ndarray, Image.Image],
                                 use_vision_for_weight: bool = True,
                                 include_confidence: bool = True,
                                 include_comparison: bool = True,
                                 include_yolo: bool = True) -> Dict[str, Any]:
        """
        Realiza análisis completo: imagen → dimensiones → peso predicho.
        
        Args:
            image_input: Imagen de entrada
            use_vision_for_weight: Si usar peso del modelo de visión o calcular con regresión
            include_confidence: Si incluir métricas de confianza
            include_comparison: Si comparar ambos métodos de predicción de peso
            include_yolo: Si incluir predicción con YOLOv8
            
        Returns:
            Dict completo: {
                'width': float,
                'height': float, 
                'thickness': float,
                'predicted_weight': float,
                'confidence': {...},
                'comparison': {...},
                'yolo_prediction': {...}  # Si include_yolo=True
            }
        """
        start_time = time.time()
        
        try:
            logger.info("Iniciando análisis completo de grano de cacao")
            
            # Paso 1: Predicción de visión (dimensiones + peso directo)
            vision_result = self.predict_from_image(
                image_input, 
                include_confidence=include_confidence,
                return_raw_output=True
            )
            
            # Extraer dimensiones
            width = vision_result['width']
            height = vision_result['height']
            thickness = vision_result['thickness']
            vision_weight = vision_result['weight']
            
            # Paso 2: Predicción de regresión (peso desde dimensiones)
            regression_result = self.predict_weight_from_dimensions(
                width, height, thickness,
                include_confidence=include_confidence
            )
            regression_weight = regression_result['predicted_weight']
            
            # Paso 3: Predicción YOLOv8 (si está habilitado)
            yolo_result = None
            if include_yolo and self.enable_yolo:
                try:
                    yolo_result = self.predict_with_yolo(image_input)
                    logger.info("Predicción YOLOv8 incluida en análisis completo")
                except Exception as e:
                    logger.warning(f"Error en predicción YOLOv8: {e}")
                    yolo_result = None
            
            # Determinar peso final
            if use_vision_for_weight:
                final_weight = vision_weight
                weight_method = 'vision_cnn'
            else:
                final_weight = regression_weight
                weight_method = 'regression'
            
            # Si YOLOv8 está disponible, usar su predicción como referencia
            if yolo_result and yolo_result.get('success', False):
                yolo_weight = yolo_result.get('peso_estimado', 0)
                # Opcional: usar YOLOv8 como peso principal si tiene alta confianza
                if yolo_result.get('nivel_confianza', 0) > 0.8:
                    final_weight = yolo_weight
                    weight_method = 'yolo_v8'
            
            # Formatear resultado completo
            result = {
                'width': width,
                'height': height,
                'thickness': thickness,
                'predicted_weight': final_weight,
                'weight_prediction_method': weight_method,
                'processing_time': time.time() - start_time,
                'timestamp': time.time()
            }
            
            # Agregar comparación si se solicita
            if include_comparison:
                comparison = {
                    'vision_weight': vision_weight,
                    'regression_weight': regression_weight,
                    'difference': abs(vision_weight - regression_weight),
                    'relative_difference_percent': abs(vision_weight - regression_weight) / max(vision_weight, regression_weight) * 100,
                    'agreement_level': self._assess_agreement(vision_weight, regression_weight)
                }
                
                # Agregar YOLOv8 a la comparación si está disponible
                if yolo_result and yolo_result.get('success', False):
                    yolo_weight = yolo_result.get('peso_estimado', 0)
                    comparison['yolo_weight'] = yolo_weight
                    comparison['yolo_confidence'] = yolo_result.get('nivel_confianza', 0)
                
                result['weight_comparison'] = comparison
            
            # Agregar métricas de confianza
            if include_confidence:
                result['confidence'] = self._calculate_combined_confidence(
                    vision_result, regression_result
                )
            
            # Calcular métricas derivadas
            result['derived_metrics'] = self._calculate_derived_metrics(
                width, height, thickness, final_weight
            )
            
            # Agregar predicción YOLOv8 si está disponible
            if yolo_result and include_yolo:
                result['yolo_prediction'] = {
                    'peso_estimado': yolo_result.get('peso_estimado', 0),
                    'altura_mm': yolo_result.get('altura_mm', 0),
                    'ancho_mm': yolo_result.get('ancho_mm', 0),
                    'grosor_mm': yolo_result.get('grosor_mm', 0),
                    'nivel_confianza': yolo_result.get('nivel_confianza', 0),
                    'detection_info': yolo_result.get('detection_info', {}),
                    'success': yolo_result.get('success', False)
                }
            
            # Actualizar estadísticas
            self.prediction_stats['combined_predictions'] += 1
            self.prediction_stats['total_predictions'] += 1
            self._update_avg_processing_time(time.time() - start_time)
            
            logger.info(f"Análisis completo completado en {time.time() - start_time:.3f}s")
            
            return result
            
        except Exception as e:
            self.prediction_stats['errors'] += 1
            logger.error(f"Error en análisis completo: {e}")
            raise PredictionError(f"Error en análisis completo: {e}")
    
    def _preprocess_image_for_vision(self, image_input: Any) -> Any:
        """
        Preprocesa imagen para el modelo de visión.
        
        Args:
            image_input: Entrada de imagen
            
        Returns:
            Tensor preprocesado
        """
        try:
            # Si es una ruta de archivo
            if isinstance(image_input, (str, Path)):
                if not validate_image_format(image_input):
                    raise PredictionError("Formato de imagen no soportado")
                processed = preprocess_single_image(
                    image_input,
                    target_size=self.image_config['target_size'],
                    normalize=self.image_config['normalize']
                )
            
            # Si son bytes
            elif isinstance(image_input, bytes):
                # Convertir bytes a PIL Image
                image = Image.open(io.BytesIO(image_input))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                processed = preprocess_single_image(
                    np.array(image),
                    target_size=self.image_config['target_size'],
                    normalize=self.image_config['normalize']
                )
            
            # Si es numpy array
            elif isinstance(image_input, np.ndarray):
                processed = preprocess_single_image(
                    image_input,
                    target_size=self.image_config['target_size'],
                    normalize=self.image_config['normalize']
                )
            
            # Si es PIL Image
            elif isinstance(image_input, Image.Image):
                if image_input.mode != 'RGB':
                    image_input = image_input.convert('RGB')
                
                processed = preprocess_single_image(
                    np.array(image_input),
                    target_size=self.image_config['target_size'],
                    normalize=self.image_config['normalize']
                )
            
            else:
                raise PredictionError(f"Tipo de entrada no soportado: {type(image_input)}")
            
            return processed
            
        except Exception as e:
            raise PredictionError(f"Error en preprocesamiento de imagen: {e}")
    
    def _format_vision_result(self, 
                             predictions: Dict, 
                             include_confidence: bool,
                             return_raw_output: bool,
                             processing_time: float) -> Dict[str, Any]:
        """Formatea el resultado del modelo de visión."""
        result = {
            'width': predictions['width'],
            'height': predictions['height'],
            'thickness': predictions['thickness'],
            'weight': predictions['weight'],
            'processing_time': processing_time,
            'model_type': 'vision_cnn'
        }
        
        if include_confidence:
            # Calcular métricas de confianza basadas en rangos esperados
            result['confidence'] = self._calculate_vision_confidence(predictions)
        
        if return_raw_output:
            result['raw_predictions'] = predictions
        
        return result
    
    def _format_regression_result(self, 
                                 predicted_weight: float,
                                 width: float, height: float, thickness: float,
                                 include_confidence: bool,
                                 processing_time: float) -> Dict[str, Any]:
        """Formatea el resultado del modelo de regresión."""
        result = {
            'predicted_weight': predicted_weight,
            'input_dimensions': {
                'width': width,
                'height': height,
                'thickness': thickness
            },
            'processing_time': processing_time,
            'model_type': 'regression'
        }
        
        if include_confidence:
            result['confidence'] = self._calculate_regression_confidence(
                predicted_weight, width, height, thickness
            )
        
        return result
    
    def _calculate_vision_confidence(self, predictions: Dict) -> Dict[str, Any]:
        """Calcula métricas de confianza para predicciones de visión."""
        # Rangos esperados para granos de cacao (basados en literatura)
        expected_ranges = {
            'width': (8.0, 15.0),
            'height': (6.0, 12.0),
            'thickness': (3.0, 8.0),
            'weight': (0.5, 2.0)
        }
        
        confidence_scores = {}
        overall_confidence = 1.0
        
        for metric, value in predictions.items():
            min_val, max_val = expected_ranges[metric]
            
            # Calcular confianza basada en si está dentro del rango esperado
            if min_val <= value <= max_val:
                confidence_scores[metric] = 1.0
            else:
                # Penalizar valores fuera del rango
                if value < min_val:
                    confidence_scores[metric] = max(0.0, 1.0 - (min_val - value) / min_val)
                else:
                    confidence_scores[metric] = max(0.0, 1.0 - (value - max_val) / max_val)
            
            overall_confidence *= confidence_scores[metric]
        
        return {
            'overall_confidence': overall_confidence,
            'individual_confidence': confidence_scores,
            'expected_ranges': expected_ranges,
            'confidence_level': self._classify_confidence(overall_confidence)
        }
    
    def _calculate_regression_confidence(self, 
                                       predicted_weight: float,
                                       width: float, height: float, thickness: float) -> Dict[str, Any]:
        """Calcula métricas de confianza para predicciones de regresión."""
        # Obtener métricas del modelo de regresión
        regression_model = get_regression_model()
        
        if regression_model and hasattr(regression_model, 'training_metrics'):
            training_metrics = regression_model.training_metrics
            test_mae = training_metrics.get('test_metrics', {}).get('mae', 0.1)
            test_r2 = training_metrics.get('test_metrics', {}).get('r2', 0.8)
        else:
            test_mae = 0.1
            test_r2 = 0.8
        
        # Calcular volumen aproximado
        volume = (4/3) * np.pi * (width/2) * (height/2) * (thickness/2)
        density = predicted_weight / volume if volume > 0 else 1.0
        
        # Evaluar confianza basada en densidad esperada del cacao (0.8-1.4 g/cm³)
        density_confidence = 1.0
        if density < 0.6 or density > 1.6:
            density_confidence = max(0.0, 1.0 - abs(density - 1.0) / 1.0)
        
        overall_confidence = min(test_r2, density_confidence)
        
        return {
            'overall_confidence': overall_confidence,
            'model_r2': test_r2,
            'expected_mae': test_mae,
            'estimated_density': density,
            'density_confidence': density_confidence,
            'confidence_level': self._classify_confidence(overall_confidence)
        }
    
    def _calculate_combined_confidence(self, 
                                     vision_result: Dict, 
                                     regression_result: Dict) -> Dict[str, Any]:
        """Calcula confianza combinada de ambos modelos."""
        vision_conf = vision_result.get('confidence', {}).get('overall_confidence', 0.5)
        regression_conf = regression_result.get('confidence', {}).get('overall_confidence', 0.5)
        
        # Promedio ponderado (más peso al modelo de visión)
        combined_confidence = 0.6 * vision_conf + 0.4 * regression_conf
        
        return {
            'combined_confidence': combined_confidence,
            'vision_confidence': vision_conf,
            'regression_confidence': regression_conf,
            'confidence_level': self._classify_confidence(combined_confidence),
            'recommendation': self._get_confidence_recommendation(combined_confidence)
        }
    
    def _classify_confidence(self, confidence: float) -> str:
        """Clasifica el nivel de confianza."""
        if confidence >= 0.9:
            return 'very_high'
        elif confidence >= 0.7:
            return 'high'
        elif confidence >= 0.5:
            return 'medium'
        elif confidence >= 0.3:
            return 'low'
        else:
            return 'very_low'
    
    def _get_confidence_recommendation(self, confidence: float) -> str:
        """Obtiene recomendación basada en confianza."""
        if confidence >= 0.8:
            return "Predicción confiable, se puede usar directamente"
        elif confidence >= 0.6:
            return "Predicción aceptable, verificar manualmente si es crítico"
        elif confidence >= 0.4:
            return "Predicción incierta, verificación manual recomendada"
        else:
            return "Predicción poco confiable, verificación manual necesaria"
    
    def _assess_agreement(self, vision_weight: float, regression_weight: float) -> str:
        """Evalúa el nivel de acuerdo entre ambos métodos."""
        relative_diff = abs(vision_weight - regression_weight) / max(vision_weight, regression_weight)
        
        if relative_diff <= 0.05:
            return 'excellent'
        elif relative_diff <= 0.10:
            return 'good'
        elif relative_diff <= 0.20:
            return 'fair'
        else:
            return 'poor'
    
    def _calculate_derived_metrics(self, 
                                 width: float, height: float, thickness: float, weight: float) -> Dict[str, Any]:
        """Calcula métricas derivadas."""
        # Volumen aproximado (elipsoide)
        volume = (4/3) * np.pi * (width/2) * (height/2) * (thickness/2)
        
        # Densidad aproximada
        density = weight / volume if volume > 0 else 0
        
        # Relación de aspecto
        aspect_ratio = width / height if height > 0 else 0
        
        # Área proyectada
        projected_area = np.pi * (width/2) * (height/2)
        
        return {
            'volume_mm3': volume,
            'density_g_per_cm3': density / 1000,  # Convertir mm³ a cm³
            'aspect_ratio': aspect_ratio,
            'projected_area_mm2': projected_area,
            'shape_factor': thickness / ((width + height) / 2) if (width + height) > 0 else 0
        }
    
    def _get_cache_key(self, image_input: Any, prefix: str) -> str:
        """Genera clave de cache para una entrada."""
        if isinstance(image_input, (str, Path)):
            return f"{prefix}_{hash(str(image_input))}"
        elif isinstance(image_input, bytes):
            return f"{prefix}_{hash(image_input)}"
        else:
            # Para otros tipos, usar timestamp (no cacheable)
            return f"{prefix}_{time.time()}"
    
    def _update_avg_processing_time(self, processing_time: float):
        """Actualiza tiempo promedio de procesamiento."""
        n = self.prediction_stats['total_predictions']
        current_avg = self.prediction_stats['avg_processing_time']
        
        # Media móvil
        self.prediction_stats['avg_processing_time'] = (
            (current_avg * (n - 1) + processing_time) / n
        )
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del servicio."""
        return {
            'prediction_stats': self.prediction_stats.copy(),
            'cache_stats': self._cache_stats.copy(),
            'cache_size': len(self._prediction_cache) if self._prediction_cache else 0,
            'model_manager_stats': model_manager.get_model_stats()
        }
    
    def clear_cache(self):
        """Limpia el cache de predicciones."""
        if self._prediction_cache:
            self._prediction_cache.clear()
            logger.info("Cache de predicciones limpiado")
    
    def warmup_service(self):
        """Precarga modelos para mejor rendimiento."""
        logger.info("Precargando modelos...")
        
        try:
            vision_model = get_vision_model(device=self.device)
            regression_model = get_regression_model()
            
            if vision_model and regression_model:
                logger.info("✓ Servicio de predicción listo")
                return True
            else:
                logger.warning("✗ Algunos modelos no están disponibles")
                return False
                
        except Exception as e:
            logger.error(f"Error en precarga: {e}")
            return False


# Instancia global del servicio
prediction_service = CacaoPredictionService()


def predict_from_image(image_input: Any, **kwargs) -> Dict[str, Any]:
    """
    Función de conveniencia para predicción desde imagen.
    
    Args:
        image_input: Imagen de entrada
        **kwargs: Argumentos adicionales
        
    Returns:
        Dict: Predicciones de características físicas
    """
    return prediction_service.predict_from_image(image_input, **kwargs)


def predict_weight_from_dimensions(width: float, height: float, thickness: float, **kwargs) -> Dict[str, Any]:
    """
    Función de conveniencia para predicción de peso.
    
    Args:
        width (float): Ancho en mm
        height (float): Alto en mm  
        thickness (float): Grosor en mm
        **kwargs: Argumentos adicionales
        
    Returns:
        Dict: Predicción de peso
    """
    return prediction_service.predict_weight_from_dimensions(width, height, thickness, **kwargs)


def predict_complete_analysis(image_input: Any, **kwargs) -> Dict[str, Any]:
    """
    Función de conveniencia para análisis completo.
    
    Args:
        image_input: Imagen de entrada
        **kwargs: Argumentos adicionales
        
    Returns:
        Dict: Análisis completo con todas las predicciones
    """
    return prediction_service.predict_complete_analysis(image_input, **kwargs)


def warmup_prediction_service() -> bool:
    """
    Precarga el servicio de predicción.
    
    Returns:
        bool: True si la precarga fue exitosa
    """
    return prediction_service.warmup_service()


def get_prediction_service_stats() -> Dict[str, Any]:
    """
    Obtiene estadísticas del servicio de predicción.
    
    Returns:
        Dict: Estadísticas completas
    """
    return prediction_service.get_service_stats()


if __name__ == "__main__":
    # Ejemplo de uso
    print("Inicializando servicio de predicción...")
    
    # Verificar estado
    if warmup_prediction_service():
        print("✓ Servicio listo para usar")
    else:
        print("✗ Algunos modelos no están disponibles")
    
    # Mostrar estadísticas
    stats = get_prediction_service_stats()
    print(f"Predicciones realizadas: {stats['prediction_stats']['total_predictions']}")
    print(f"Modelos cargados: {len(stats['model_manager_stats']['loaded_models'])}")
    
    print("\nEjemplo de uso:")
    print("1. predict_from_image('path/to/image.jpg')")
    print("2. predict_weight_from_dimensions(12.5, 8.3, 4.2)")
    print("3. predict_complete_analysis('path/to/image.jpg')")
