"""
Inferencia con YOLOv8-seg para segmentación de granos de cacao.
"""
import numpy as np
import cv2
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import logging

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None
    logging.warning("Ultralytics no está instalado. La funcionalidad de segmentación no estará disponible.")

from ..utils.paths import get_yolo_artifacts_dir, ensure_dir_exists
from ..utils.logs import get_ml_logger


logger = get_ml_logger("cacaoscan.ml.segmentation")


class YOLOSegmentationInference:
    """Clase para inferencia de segmentación con YOLOv8-seg."""
    
    def __init__(self, model_path: Optional[Path] = None, confidence_threshold: float = 0.5):
        """
        Inicializa el modelo de segmentación.
        
        Args:
            model_path: Ruta al modelo personalizado. Si es None, usa el modelo base.
            confidence_threshold: Umbral de confianza para las predicciones
        """
        if YOLO is None:
            raise ImportError("Ultralytics no está instalado. Instalar con: pip install ultralytics")
        
        self.confidence_threshold = confidence_threshold
        self.model = None
        
        # Asegurar que el directorio de artefactos existe
        ensure_dir_exists(get_yolo_artifacts_dir())
        
        # Cargar modelo
        self._load_model(model_path)
    
    def _load_model(self, model_path: Optional[Path] = None):
        """Carga el modelo YOLO."""
        try:
            if model_path and model_path.exists():
                logger.info(f"Cargando modelo personalizado desde {model_path}")
                self.model = YOLO(str(model_path))
            else:
                logger.info("Cargando modelo base YOLOv8s-seg")
                self.model = YOLO('yolov8s-seg.pt')
            
            logger.info("Modelo YOLOv8-seg cargado exitosamente")
            
        except Exception as e:
            logger.error(f"Error al cargar el modelo YOLO: {e}")
            raise
    
    def predict(self, image_path: Path) -> List[Dict[str, Any]]:
        """
        Realiza predicción de segmentación en una imagen.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Lista de predicciones con información de detección y segmentación
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
        
        try:
            # Realizar predicción
            results = self.model(str(image_path), conf=self.confidence_threshold)
            
            predictions = []
            
            for result in results:
                if result.masks is not None and len(result.masks) > 0:
                    # Obtener información de las detecciones
                    boxes = result.boxes
                    masks = result.masks
                    
                    for i in range(len(boxes)):
                        # Información de la caja delimitadora
                        box = boxes[i]
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])
                        
                        # Información de la máscara
                        mask = masks[i]
                        mask_data = mask.data[0].cpu().numpy()
                        
                        prediction = {
                            'confidence': conf,
                            'class_id': cls,
                            'class_name': self.model.names[cls],
                            'bbox': box.xyxy[0].cpu().numpy().tolist(),  # [x1, y1, x2, y2]
                            'mask': mask_data,
                            'area': np.sum(mask_data > 0.5),
                            'center': self._calculate_mask_center(mask_data)
                        }
                        
                        predictions.append(prediction)
            
            # Ordenar por confianza descendente
            predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            logger.debug(f"Encontradas {len(predictions)} detecciones en {image_path.name}")
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error en la predicción para {image_path}: {e}")
            return []
    
    def _calculate_mask_center(self, mask: np.ndarray) -> Tuple[int, int]:
        """Calcula el centro de masa de una máscara."""
        moments = cv2.moments(mask.astype(np.uint8))
        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])
            return (cx, cy)
        else:
            # Fallback: centro geométrico
            h, w = mask.shape
            return (w // 2, h // 2)
    
    def get_best_prediction(self, image_path: Path) -> Optional[Dict[str, Any]]:
        """
        Obtiene la mejor predicción (mayor confianza) para una imagen.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Mejor predicción o None si no hay detecciones
        """
        predictions = self.predict(image_path)
        return predictions[0] if predictions else None
    
    def filter_predictions_by_class(
        self,
        predictions: List[Dict[str, Any]],
        target_classes: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filtra predicciones por clase específica.
        
        Args:
            predictions: Lista de predicciones
            target_classes: Lista de nombres de clases objetivo
            
        Returns:
            Predicciones filtradas
        """
        if target_classes is None:
            return predictions
        
        filtered = []
        for pred in predictions:
            if pred['class_name'] in target_classes:
                filtered.append(pred)
        
        return filtered
    
    def validate_prediction_quality(self, prediction: Dict[str, Any]) -> bool:
        """
        Valida la calidad de una predicción.
        
        Args:
            prediction: Predicción a validar
            
        Returns:
            True si la predicción es de buena calidad
        """
        if not prediction:
            return False
        
        # Verificar confianza mínima
        if prediction['confidence'] < self.confidence_threshold:
            return False
        
        # Verificar área mínima de la máscara
        min_area = 100  # píxeles
        if prediction['area'] < min_area:
            return False
        
        # Verificar que la máscara no esté vacía
        mask = prediction['mask']
        if np.sum(mask > 0.5) == 0:
            return False
        
        return True
    
    def save_prediction_debug(
        self,
        image_path: Path,
        prediction: Dict[str, Any],
        output_dir: Path
    ) -> None:
        """
        Guarda información de debug de una predicción.
        
        Args:
            image_path: Ruta a la imagen original
            prediction: Predicción a guardar
            output_dir: Directorio de salida
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar máscara
        mask = prediction['mask']
        mask_normalized = (mask * 255).astype(np.uint8)
        mask_path = output_dir / f"{image_path.stem}_mask.png"
        cv2.imwrite(str(mask_path), mask_normalized)
        
        # Guardar imagen con bounding box
        image = cv2.imread(str(image_path))
        bbox = prediction['bbox']
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Añadir texto con confianza
        conf_text = f"Conf: {prediction['confidence']:.3f}"
        cv2.putText(image, conf_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        debug_path = output_dir / f"{image_path.stem}_debug.jpg"
        cv2.imwrite(str(debug_path), image)
        
        logger.debug(f"Guardado debug para {image_path.name} en {output_dir}")


def create_yolo_inference(
    model_path: Optional[Path] = None,
    confidence_threshold: float = 0.5
) -> YOLOSegmentationInference:
    """
    Función de conveniencia para crear una instancia de inferencia YOLO.
    
    Args:
        model_path: Ruta al modelo personalizado
        confidence_threshold: Umbral de confianza
        
    Returns:
        Instancia de YOLOSegmentationInference
    """
    return YOLOSegmentationInference(model_path, confidence_threshold)
