"""
Módulo de predicción unificada para CacaoScan.
Integra segmentación YOLOv8-seg con modelos de regresión.
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

logger = get_ml_logger("cacaoscan.ml.prediction")


class CacaoPredictor:
    """Predictor unificado para granos de cacao."""
    
    def __init__(self, confidence_threshold: float = 0.5):
        """
        Inicializa el predictor.
        
        Args:
            confidence_threshold: Umbral de confianza para YOLO
        """
        self.confidence_threshold = confidence_threshold
        self.yolo_cropper = None
        self.regression_models = {}
        self.scalers = None
        self.device = self._get_device()
        self.models_loaded = False
        
        # Crear directorio para crops de runtime
        self.runtime_crops_dir = Path("media/cacao_images/crops_runtime")
        ensure_dir_exists(self.runtime_crops_dir)
        
        logger.info(f"Predictor inicializado con threshold {confidence_threshold}")
    
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
        Si no existen, entrena automáticamente los modelos.
        
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
                logger.warning("Modelos o escaladores no encontrados. Iniciando entrenamiento automático...")
                if not self._auto_train_models():
                    logger.error("Error en entrenamiento automático")
                    return False
            
            # 3. Cargar escaladores
            try:
                self.scalers = load_scalers()
                logger.info("Escaladores cargados exitosamente")
            except Exception as e:
                logger.error(f"Error cargando escaladores: {e}")
                return False
            
            # 4. Cargar modelos de regresión
            self.regression_models = {}
            
            for target in TARGETS:
                model_path = get_regressors_artifacts_dir() / f"{target}.pt"
                
                if not model_path.exists():
                    logger.error(f"Modelo no encontrado para {target}: {model_path}")
                    return False
                
                try:
                    # Crear modelo
                    model = create_model(
                        model_type="resnet18",  # Por defecto ResNet18
                        num_outputs=1,
                        pretrained=False,
                        dropout_rate=0.2,
                        multi_head=False
                    )
                    
                    # Cargar pesos
                    checkpoint = torch.load(model_path, map_location=self.device)
                    model.load_state_dict(checkpoint['model_state_dict'])
                    model.to(self.device)
                    model.eval()
                    
                    self.regression_models[target] = model
                    logger.info(f"Modelo cargado para {target}")
                    
                except Exception as e:
                    logger.error(f"Error cargando modelo para {target}: {e}")
                    return False
            
            self.models_loaded = True
            load_time = time.time() - start_time
            logger.info(f"Todos los artefactos cargados exitosamente en {load_time:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"Error general cargando artefactos: {e}")
            return False
    
    def _auto_train_models(self) -> bool:
        """
        Entrena automáticamente los modelos si no existen.
        
        Returns:
            True si el entrenamiento fue exitoso, False en caso contrario
        """
        try:
            logger.info("🚀 Iniciando entrenamiento automático de modelos...")
            
            # Importar funciones de entrenamiento
            from ..pipeline.train_all import run_training_pipeline
            
            # Configuración de entrenamiento automático
            config = {
                'epochs': 30,  # Menos epochs para entrenamiento rápido
                'batch_size': 16,  # Batch size más pequeño para memoria
                'learning_rate': 0.001,
                'multi_head': False,  # 4 modelos independientes
                'model_type': 'resnet18',
                'img_size': 224,
                'early_stopping_patience': 10,
                'save_best_only': True
            }
            
            logger.info(f"Configuración de entrenamiento automático: {config}")
            
            # Ejecutar pipeline de entrenamiento
            success = run_training_pipeline(
                epochs=config['epochs'],
                batch_size=config['batch_size'],
                learning_rate=config['learning_rate'],
                multi_head=config['multi_head'],
                model_type=config['model_type'],
                img_size=config['img_size'],
                early_stopping_patience=config['early_stopping_patience'],
                save_best_only=config['save_best_only']
            )
            
            if success:
                logger.info("✅ Entrenamiento automático completado exitosamente")
                return True
            else:
                logger.error("❌ Error en entrenamiento automático")
                return False
                
        except Exception as e:
            logger.error(f"Error en entrenamiento automático: {e}")
            return False
    
    def _preprocess_image(self, image: Image.Image) -> torch.Tensor:
        """
        Preprocesa una imagen para los modelos de regresión.
        
        Args:
            image: Imagen PIL
            
        Returns:
            Tensor preprocesado
        """
        import torchvision.transforms as transforms
        
        # Transformaciones estándar para ImageNet
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Aplicar transformaciones
        tensor = transform(image)
        
        # Añadir dimensión de batch
        tensor = tensor.unsqueeze(0)
        
        return tensor.to(self.device)
    
    def _predict_single_target(self, image_tensor: torch.Tensor, target: str) -> Tuple[float, float]:
        """
        Predice un target específico.
        
        Args:
            image_tensor: Imagen preprocesada
            target: Target a predecir
            
        Returns:
            Tuple con (valor_predicho, confianza)
        """
        model = self.regression_models[target]
        
        with torch.no_grad():
            # Predicción
            prediction = model(image_tensor)
            prediction_value = prediction.cpu().numpy().flatten()[0]
            
            # Desnormalizar
            if self.scalers:
                try:
                    denorm_data = self.scalers.inverse_transform({target: np.array([prediction_value])})
                    prediction_value = denorm_data[target][0]
                except Exception as e:
                    logger.warning(f"Error desnormalizando {target}: {e}")
            
            # Calcular confianza (proxy basado en varianza del modelo)
            # Usar dropout para estimar incertidumbre si está disponible
            confidence = self._estimate_confidence(model, image_tensor, target)
            
            return float(prediction_value), float(confidence)
    
    def _estimate_confidence(self, model: torch.nn.Module, image_tensor: torch.Tensor, target: str) -> float:
        """
        Estima la confianza de la predicción.
        
        Args:
            model: Modelo de regresión
            image_tensor: Imagen preprocesada
            target: Target predicho
            
        Returns:
            Confianza estimada (0-1)
        """
        try:
            # Intentar usar dropout para estimar incertidumbre
            model.train()  # Activar dropout
            
            predictions = []
            n_samples = 5  # Número de muestras para estimar varianza
            
            for _ in range(n_samples):
                with torch.no_grad():
                    pred = model(image_tensor)
                    predictions.append(pred.cpu().numpy().flatten()[0])
            
            model.eval()  # Volver a modo eval
            
            # Calcular varianza
            predictions = np.array(predictions)
            variance = np.var(predictions)
            
            # Convertir varianza a confianza (menor varianza = mayor confianza)
            # Usar función sigmoide para mapear a [0, 1]
            confidence = 1.0 / (1.0 + variance * 10)  # Factor de escala ajustable
            
            return min(max(confidence, 0.0), 1.0)  # Clamp a [0, 1]
            
        except Exception as e:
            logger.warning(f"Error estimando confianza para {target}: {e}")
            # Fallback: confianza basada en rangos típicos
            return self._get_proxy_confidence(target)
    
    def _get_proxy_confidence(self, target: str) -> float:
        """
        Obtiene una confianza proxy basada en estadísticas del target.
        
        Args:
            target: Target predicho
            
        Returns:
            Confianza proxy (0-1)
        """
        # Confianzas proxy basadas en la dificultad típica de cada target
        proxy_confidences = {
            'alto': 0.85,
            'ancho': 0.80,
            'grosor': 0.75,
            'peso': 0.70
        }
        
        return proxy_confidences.get(target, 0.75)
    
    def predict(self, image: Image.Image) -> Dict[str, Any]:
        """
        Predice dimensiones y peso de un grano de cacao.
        
        Args:
            image: Imagen PIL del grano
            
        Returns:
            Diccionario con predicciones y metadatos
        """
        if not self.models_loaded:
            raise RuntimeError("Los artefactos no han sido cargados. Llamar load_artifacts() primero.")
        
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
            
            # 4. Preparar resultado
            total_time = time.time() - start_time
            latency_ms = int(total_time * 1000)
            
            result = {
                'alto_mm': predictions['alto'],
                'ancho_mm': predictions['ancho'],
                'grosor_mm': predictions['grosor'],
                'peso_g': predictions['peso'],
                'confidences': confidences,
                'crop_url': f"/media/cacao_images/crops_runtime/{crop_uuid}.png",
                'debug': {
                    'segmented': True,
                    'yolo_conf': float(yolo_confidence),
                    'latency_ms': latency_ms,
                    'models_version': 'v1',
                    'device': str(self.device),
                    'total_time_s': total_time
                }
            }
            
            logger.info(f"Predicción completada en {total_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            raise
    
    def predict_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Predice desde bytes de imagen.
        
        Args:
            image_bytes: Bytes de la imagen
            
        Returns:
            Diccionario con predicciones
        """
        try:
            # Convertir bytes a imagen PIL
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            return self.predict(image)
            
        except Exception as e:
            logger.error(f"Error procesando imagen desde bytes: {e}")
            raise ValueError(f"Error procesando imagen: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre los modelos cargados.
        
        Returns:
            Diccionario con información de los modelos
        """
        if not self.models_loaded:
            return {'status': 'not_loaded'}
        
        info = {
            'status': 'loaded',
            'device': str(self.device),
            'models': {},
            'scalers': 'loaded' if self.scalers else 'not_loaded',
            'yolo_cropper': 'loaded' if self.yolo_cropper else 'not_loaded'
        }
        
        for target, model in self.regression_models.items():
            info['models'][target] = {
                'type': type(model).__name__,
                'parameters': sum(p.numel() for p in model.parameters())
            }
        
        return info


# Instancia global del predictor
_predictor_instance: Optional[CacaoPredictor] = None


def get_predictor() -> CacaoPredictor:
    """
    Obtiene la instancia global del predictor.
    
    Returns:
        Instancia del predictor
    """
    global _predictor_instance
    
    if _predictor_instance is None:
        _predictor_instance = CacaoPredictor()
        
        # Intentar cargar artefactos automáticamente
        if not _predictor_instance.load_artifacts():
            logger.warning("No se pudieron cargar todos los artefactos automáticamente")
    
    return _predictor_instance


def load_artifacts() -> bool:
    """
    Función de conveniencia para cargar artefactos.
    
    Returns:
        True si se cargaron exitosamente
    """
    predictor = get_predictor()
    return predictor.load_artifacts()


def predict_image(image: Image.Image) -> Dict[str, Any]:
    """
    Función de conveniencia para predecir una imagen.
    
    Args:
        image: Imagen PIL
        
    Returns:
        Diccionario con predicciones
    """
    predictor = get_predictor()
    return predictor.predict(image)


def predict_image_bytes(image_bytes: bytes) -> Dict[str, Any]:
    """
    Función de conveniencia para predecir desde bytes.
    
    Args:
        image_bytes: Bytes de la imagen
        
    Returns:
        Diccionario con predicciones
    """
    predictor = get_predictor()
    return predictor.predict_from_bytes(image_bytes)
