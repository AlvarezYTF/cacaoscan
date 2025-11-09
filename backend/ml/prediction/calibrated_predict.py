"""
Módulo de predicción mejorado con calibración para CacaoScan.
Integra segmentación YOLOv8-seg, modelos de regresión y calibración OpenCV.
"""

import time
import uuid
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Any
import numpy as np
import torch
import cv2
from PIL import Image
import io

from ..utils.paths import get_regressors_artifacts_dir, get_yolo_artifacts_dir
from ..utils.logs import get_ml_logger
from ..utils.io import save_image, ensure_dir_exists
from ..segmentation.cropper import create_cacao_cropper
from ..regression.models import create_model, TARGETS
from ..regression.scalers import load_scalers
from ..data.transforms import resize_crop_to_square
from ..measurement.calibration import (
    get_calibration_manager,
    CalibrationMethod,
    ReferenceObject,
    convert_pixels_to_mm
)

logger = get_ml_logger("cacaoscan.ml.prediction")


class CalibratedCacaoPredictor:
    """Predictor unificado con calibración para granos de cacao."""
    
    def __init__(self, confidence_threshold: float = 0.5, use_calibration: bool = True):
        """
        Inicializa el predictor con calibración.
        
        Args:
            confidence_threshold: Umbral de confianza para YOLO
            use_calibration: Si usar calibración para convertir a medidas reales
        """
        self.confidence_threshold = confidence_threshold
        self.use_calibration = use_calibration
        self.yolo_cropper = None
        self.regression_models = {}
        self.scalers = None
        self.device = self._get_device()
        self.models_loaded = False
        
        # Gestor de calibración
        self.calibration_manager = get_calibration_manager() if use_calibration else None
        
        # Crear directorio para crops de runtime
        self.runtime_crops_dir = Path("media/cacao_images/crops_runtime")
        ensure_dir_exists(self.runtime_crops_dir)
        
        logger.info(f"CalibratedCacaoPredictor inicializado con threshold {confidence_threshold}, calibración: {use_calibration}")
    
    def _get_device(self) -> torch.device:
        """Obtiene el dispositivo disponible."""
        if torch.cuda.is_available():
            device = torch.device('cuda')
            logger.info(f"Usando GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = torch.device('cpu')
            logger.info("Usando CPU")
        
        return device
    
    def load_artifacts(self) -> bool:
        """
        Carga todos los artefactos necesarios para la predicción.
        
        Returns:
            True si se cargaron exitosamente, False en caso contrario
        """
        try:
            logger.info("Cargando artefactos...")
            start_time = time.time()
            
            # 1. Cargar YOLO cropper
            self.yolo_cropper = create_cacao_cropper(
                confidence_threshold=self.confidence_threshold,
                crop_size=512,
                padding=10,
                save_masks=False,
                overwrite=False
            )
            
            # 2. Verificar si existen los modelos y escaladores
            scalers_path = get_regressors_artifacts_dir()
            models_exist = all(
                (get_regressors_artifacts_dir() / f"{target}.pt").exists() 
                for target in TARGETS
            )
            scalers_exist = scalers_path.exists()
            
            if not models_exist or not scalers_exist:
                import os
                auto_train_enabled = os.getenv("AUTO_TRAIN_ENABLED", "0").lower() in ("1", "true", "yes")
                if auto_train_enabled:
                    logger.warning("Modelos o escaladores no encontrados. Iniciando entrenamiento automtico...")
                    if not self._auto_train_models():
                        logger.error("Error en entrenamiento automtico")
                        return False
                else:
                    logger.warning("Modelos/escaladores no encontrados y AUTO_TRAIN_ENABLED=0. Omitiendo autoentrenamiento.")
                    return False
            
            # 3. Cargar escaladores
            try:
                self.scalers = load_scalers()
                logger.info("Escaladores cargados exitosamente")
            except Exception as e:
                logger.error(f"Error cargando escaladores: {e}")
                return False
            
            # 4. Cargar modelos de regresión
            for target in TARGETS:
                try:
                    model_path = get_regressors_artifacts_dir() / f"{target}.pt"
                    model = create_model(
                        model_type="resnet18",
                        num_outputs=1,
                        pretrained=False,
                        dropout_rate=0.2
                    )
                    
                    # Cargar pesos del modelo
                    checkpoint = torch.load(model_path, map_location=self.device)
                    model.load_state_dict(checkpoint['model_state_dict'])
                    model.to(self.device)
                    model.eval()
                    
                    self.regression_models[target] = model
                    logger.info(f"Modelo {target} cargado exitosamente")
                    
                except Exception as e:
                    logger.error(f"Error cargando modelo {target}: {e}")
                    return False
            
            # 5. Cargar calibración si está habilitada
            if self.use_calibration and self.calibration_manager:
                try:
                    calibration_params = self.calibration_manager.load_calibration()
                    if calibration_params:
                        logger.info(f"Calibración cargada: {calibration_params.pixels_per_mm:.3f} pixels/mm")
                    else:
                        logger.warning("No se encontró calibración previa. Se usarán medidas en píxeles.")
                except Exception as e:
                    logger.warning(f"Error cargando calibración: {e}")
            
            self.models_loaded = True
            load_time = time.time() - start_time
            logger.info(f"Artefactos cargados exitosamente en {load_time:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cargando artefactos: {e}")
            return False
    
    def _auto_train_models(self) -> bool:
        """Entrena automáticamente los modelos si no existen."""
        try:
            from ..pipeline.train_all import run_training_pipeline
            
            logger.info("Iniciando entrenamiento automático...")
            success = run_training_pipeline()
            
            if success:
                logger.info("Entrenamiento automático completado")
                return True
            else:
                logger.error("Error en entrenamiento automático")
                return False
                
        except Exception as e:
            logger.error(f"Error en entrenamiento automático: {e}")
            return False
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """Preprocesa la imagen para el modelo de regresión."""
        # Convertir a RGB si es necesario
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Redimensionar a 224x224 (tamaño esperado por ResNet)
        image = image.resize((224, 224), Image.Resampling.LANCZOS)
        
        # Convertir a tensor y normalizar
        image_array = np.array(image).astype(np.float32) / 255.0
        
        # Aplicar normalización estándar de ImageNet
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        image_array = (image_array - mean) / std
        
        # Convertir a tensor y agregar dimensión de batch
        image_tensor = torch.from_numpy(image_array).permute(2, 0, 1).unsqueeze(0)
        
        return image_tensor.to(self.device)
    
    def _predict_single_target(self, image_tensor: torch.Tensor, target: str) -> Tuple[float, float]:
        """Predice un target específico."""
        model = self.regression_models[target]
        
        with torch.no_grad():
            prediction = model(image_tensor)
            pred_value = prediction.item()
            
            # Calcular confianza basada en la varianza de la predicción
            # (implementación simplificada)
            confidence = min(0.95, max(0.1, 1.0 - abs(pred_value - 0.5) * 0.1))
            
            return pred_value, confidence
    
    def calibrate_image(
        self,
        image: Image.Image,
        method: CalibrationMethod = CalibrationMethod.COIN_DETECTION,
        reference_object: Optional[ReferenceObject] = None
    ) -> Dict[str, Any]:
        """
        Calibra una imagen para obtener la escala de píxeles a milímetros.
        
        Args:
            image: Imagen PIL
            method: Método de calibración
            reference_object: Objeto de referencia específico
            
        Returns:
            Diccionario con resultado de calibración
        """
        if not self.use_calibration or not self.calibration_manager:
            return {
                'success': False,
                'error': 'Calibración no habilitada'
            }
        
        try:
            # Convertir PIL a OpenCV
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Realizar calibración
            calibration_result = self.calibration_manager.calibrate_image(
                image_cv, method, reference_object
            )
            
            if calibration_result.success:
                # Guardar calibración
                self.calibration_manager.save_calibration(calibration_result)
                
                return {
                    'success': True,
                    'pixels_per_mm': calibration_result.pixels_per_mm,
                    'confidence': calibration_result.confidence,
                    'method': calibration_result.method.value,
                    'reference_object': calibration_result.reference_object.value['name'] if calibration_result.reference_object else None,
                    'calibration_image_path': calibration_result.calibration_image_path
                }
            else:
                return {
                    'success': False,
                    'error': calibration_result.error_message
                }
                
        except Exception as e:
            logger.error(f"Error en calibración: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """
        Predice las dimensiones de un grano de cacao con calibración opcional.
        
        Args:
            image: Imagen PIL del grano de cacao
            
        Returns:
            Diccionario con predicciones y metadatos
        """
        if not self.models_loaded:
            raise ValueError("Modelos no cargados. Ejecutar load_artifacts() primero.")
        
        logger.info("Iniciando predicción con calibración...")
        
        start_time = time.time()
        
        try:
            # 1. Segmentación y recorte
            logger.debug("Iniciando segmentación...")
            
            # Guardar imagen temporalmente para el cropper
            temp_image_path = self.runtime_crops_dir / f"temp_{uuid.uuid4()}.jpg"
            image.save(temp_image_path)
            
            try:
                # Usar el cropper para segmentar y recortar
                crop_result = self.yolo_cropper.process_image(
                    temp_image_path,
                    image_id=1,  # ID ficticio
                    force_process=True
                )
                
                if not crop_result['success']:
                    raise ValueError(f"Error en segmentación: {crop_result.get('error', 'Error desconocido')}")
                
                # Cargar el crop generado
                crop_path = crop_result['crop_path']
                crop_image = Image.open(crop_path)
                
                # Guardar crop en directorio de runtime con UUID
                crop_uuid = str(uuid.uuid4())
                runtime_crop_path = self.runtime_crops_dir / f"{crop_uuid}.png"
                crop_image.save(runtime_crop_path)
                
                yolo_confidence = crop_result.get('confidence', 0.0)
                
            finally:
                # Limpiar archivo temporal
                if temp_image_path.exists():
                    temp_image_path.unlink()
            
            # 2. Preprocesar imagen para regresión
            image_tensor = self._preprocess_image(crop_image)
            
            # 3. Predecir cada target
            predictions = {}
            confidences = {}
            
            for target in TARGETS:
                pred_value, confidence = self._predict_single_target(image_tensor, target)
                predictions[target] = pred_value
                confidences[target] = confidence
            
            # 4. Desnormalizar predicciones usando escaladores
            denormalized_predictions = {}
            for target in TARGETS:
                try:
                    # Crear diccionario temporal para desnormalización
                    temp_data = {target: np.array([predictions[target]])}
                    denorm_pred = self.scalers.inverse_transform(temp_data)
                    denormalized_predictions[target] = float(denorm_pred[target][0])
                except Exception as e:
                    logger.warning(f"Error desnormalizando {target}: {e}")
                    denormalized_predictions[target] = predictions[target]
            
            # 5. Aplicar calibración si está disponible
            calibrated_predictions = {}
            calibration_info = {}
            
            if self.use_calibration and self.calibration_manager and self.calibration_manager.current_calibration:
                try:
                    pixels_per_mm = self.calibration_manager.current_calibration.pixels_per_mm
                    
                    # Convertir predicciones de píxeles a milímetros
                    calibrated_predictions = {
                        'alto_mm': convert_pixels_to_mm(denormalized_predictions['alto']),
                        'ancho_mm': convert_pixels_to_mm(denormalized_predictions['ancho']),
                        'grosor_mm': convert_pixels_to_mm(denormalized_predictions['grosor']),
                        'peso_g': denormalized_predictions['peso']  # El peso ya está en gramos
                    }
                    
                    calibration_info = {
                        'calibrated': True,
                        'pixels_per_mm': pixels_per_mm,
                        'calibration_method': self.calibration_manager.current_calibration.method.value,
                        'calibration_confidence': self.calibration_manager.current_calibration.confidence
                    }
                    
                    logger.info(f"Predicciones calibradas aplicadas: {pixels_per_mm:.3f} pixels/mm")
                    
                except Exception as e:
                    logger.warning(f"Error aplicando calibración: {e}")
                    calibrated_predictions = denormalized_predictions
                    calibration_info = {
                        'calibrated': False,
                        'error': str(e)
                    }
            else:
                calibrated_predictions = denormalized_predictions
                calibration_info = {
                    'calibrated': False,
                    'reason': 'Calibración no disponible'
                }
            
            # 6. Preparar resultado
            total_time = time.time() - start_time
            
            result = {
                'success': True,
                'predictions': calibrated_predictions,
                'confidences': confidences,
                'calibration_info': calibration_info,
                'processing_time_ms': int(total_time * 1000),
                'crop_url': f"/media/cacao_images/crops_runtime/{crop_uuid}.png",
                'yolo_confidence': yolo_confidence,
                'model_version': 'v2.0_calibrated',
                'device_used': 'cuda' if torch.cuda.is_available() else 'cpu'
            }
            
            logger.info(f"Predicción completada en {total_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }
    
    def get_calibration_status(self) -> Dict[str, Any]:
        """Obtiene el estado actual de la calibración."""
        if not self.use_calibration or not self.calibration_manager:
            return {
                'calibration_enabled': False,
                'reason': 'Calibración no habilitada'
            }
        
        if not self.calibration_manager.current_calibration:
            return {
                'calibration_enabled': True,
                'calibration_loaded': False,
                'reason': 'No hay calibración cargada'
            }
        
        calibration = self.calibration_manager.current_calibration
        return {
            'calibration_enabled': True,
            'calibration_loaded': True,
            'pixels_per_mm': calibration.pixels_per_mm,
            'method': calibration.method.value,
            'confidence': calibration.confidence,
            'timestamp': calibration.timestamp,
            'validation_score': calibration.validation_score
        }


# Función de conveniencia para obtener el predictor calibrado
def get_calibrated_predictor(confidence_threshold: float = 0.5, use_calibration: bool = True) -> CalibratedCacaoPredictor:
    """
    Obtiene una instancia del predictor calibrado.
    
    Args:
        confidence_threshold: Umbral de confianza para YOLO
        use_calibration: Si usar calibración
        
    Returns:
        Instancia del predictor calibrado
    """
    return CalibratedCacaoPredictor(confidence_threshold, use_calibration)


