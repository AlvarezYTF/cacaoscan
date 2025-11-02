"""
Inferencia con YOLOv8-seg para segmentaciÃ³n de granos de cacao.
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
    logging.warning("Ultralytics no estÃ¡ instalado. La funcionalidad de segmentaciÃ³n no estarÃ¡ disponible.")

from ..utils.paths import get_yolo_artifacts_dir, ensure_dir_exists
from ..utils.logs import get_ml_logger


logger = get_ml_logger("cacaoscan.ml.segmentation")


class YOLOSegmentationInference:
    """Clase para inferencia de segmentaciÃ³n con YOLOv8-seg."""
    
    def __init__(self, model_path: Optional[Path] = None, confidence_threshold: float = 0.5):
        """
        Inicializa el modelo de segmentaciÃ³n.
        
        Args:
            model_path: Ruta al modelo personalizado. Si es None, usa el modelo base.
            confidence_threshold: Umbral de confianza para las predicciones
        """
        if YOLO is None:
            raise ImportError("Ultralytics no estÃ¡ instalado. Instalar con: pip install ultralytics")
        
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
    
    def predict(self, image_path: Path, conf_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Realiza predicciÃ³n de segmentaciÃ³n en una imagen.
        
        Args:
            image_path: Ruta a la imagen
            conf_threshold: Umbral de confianza (usa self.confidence_threshold si es None)
            
        Returns:
            Lista de predicciones con informaciÃ³n de detecciÃ³n y segmentaciÃ³n
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
        
        try:
            # Usar threshold proporcionado o el predeterminado
            threshold = conf_threshold if conf_threshold is not None else self.confidence_threshold
            
            # Realizar predicción con umbral inicial
            results = self.model(str(image_path), conf=threshold)
            
            predictions = []
            
            for result in results:
                if result.masks is not None and len(result.masks) > 0:
                    # Obtener informaciÃ³n de las detecciones
                    boxes = result.boxes
                    masks = result.masks
                    
                    for i in range(len(boxes)):
                        # InformaciÃ³n de la caja delimitadora
                        box = boxes[i]
                        conf = float(box.conf[0])
                        cls = int(box.cls[0])
                        
                        # InformaciÃ³n de la mÃ¡scara
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
            
            # Si no hay detecciones con el umbral inicial, intentar con umbrales más bajos progresivamente
            if not predictions:
                lower_thresholds = [0.4, 0.3, 0.25, 0.2, 0.15, 0.1]  # Más intentos con umbrales progresivamente más bajos
                for lower_threshold in lower_thresholds:
                    logger.debug(f"Intentando detección con umbral {lower_threshold}...")
                    results = self.model(str(image_path), conf=lower_threshold)
                    
                    for result in results:
                        if result.masks is not None and len(result.masks) > 0:
                            boxes = result.boxes
                            masks = result.masks
                            
                            # Filtrar solo las detecciones más confiables de cada intento
                            for i in range(len(boxes)):
                                box = boxes[i]
                                conf = float(box.conf[0])
                                
                                # Solo aceptar si la confianza es razonable
                                if conf >= lower_threshold * 0.8:  # Al menos 80% del umbral usado
                                    mask = masks[i]
                                    mask_data = mask.data[0].cpu().numpy()
                                    
                                    prediction = {
                                        'confidence': conf,
                                        'class_id': int(box.cls[0]),
                                        'class_name': self.model.names[int(box.cls[0])],
                                        'bbox': box.xyxy[0].cpu().numpy().tolist(),
                                        'mask': mask_data,
                                        'area': np.sum(mask_data > 0.5),
                                        'center': self._calculate_mask_center(mask_data)
                                    }
                                    
                                    predictions.append(prediction)
                            
                            # Si encontramos detecciones, detener búsqueda
                            if predictions:
                                break
                    
                    if predictions:
                        break
            
            # Si aún no hay detecciones, usar el último intento con umbral muy bajo
            if not predictions and threshold > 0.25:
                logger.debug(f"No se encontraron detecciones con conf={threshold:.2f}, intentando con umbral más bajo...")
                # Intentar con umbrales progresivamente más bajos
                for lower_threshold in [0.4, 0.3, 0.25]:
                    results = self.model(str(image_path), conf=lower_threshold)
                    for result in results:
                        if result.masks is not None and len(result.masks) > 0:
                            boxes = result.boxes
                            masks = result.masks
                            for i in range(len(boxes)):
                                box = boxes[i]
                                conf = float(box.conf[0])
                                if conf >= 0.25:  # Aceptar si confianza >= 0.25
                                    cls = int(box.cls[0])
                                    mask = masks[i]
                                    mask_data = mask.data[0].cpu().numpy()
                                    prediction = {
                                        'confidence': conf,
                                        'class_id': cls,
                                        'class_name': self.model.names[cls],
                                        'bbox': box.xyxy[0].cpu().numpy().tolist(),
                                        'mask': mask_data,
                                        'area': np.sum(mask_data > 0.5),
                                        'center': self._calculate_mask_center(mask_data)
                                    }
                                    predictions.append(prediction)
                    if predictions:
                        logger.debug(f"Encontradas {len(predictions)} detecciones con conf={lower_threshold:.2f}")
                        break
            
            # Ordenar por confianza descendente
            predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            logger.debug(f"Encontradas {len(predictions)} detecciones en {image_path.name}")
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error en la predicciÃ³n para {image_path}: {e}")
            return []
    
    def _calculate_mask_center(self, mask: np.ndarray) -> Tuple[int, int]:
        """Calcula el centro de masa de una mÃ¡scara."""
        moments = cv2.moments(mask.astype(np.uint8))
        if moments['m00'] != 0:
            cx = int(moments['m10'] / moments['m00'])
            cy = int(moments['m01'] / moments['m00'])
            return (cx, cy)
        else:
            # Fallback: centro geomÃ©trico
            h, w = mask.shape
            return (w // 2, h // 2)
    
    def get_best_prediction(self, image_path: Path) -> Optional[Dict[str, Any]]:
        """
        Obtiene la mejor predicciÃ³n (mayor confianza) para una imagen.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Mejor predicciÃ³n o None si no hay detecciones
        """
        predictions = self.predict(image_path)
        return predictions[0] if predictions else None
    
    def filter_predictions_by_class(
        self,
        predictions: List[Dict[str, Any]],
        target_classes: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Filtra predicciones por clase especÃ­fica.
        
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
        Valida la calidad de una predicciÃ³n.
        
        Args:
            prediction: PredicciÃ³n a validar
            
        Returns:
            True si la predicciÃ³n es de buena calidad
        """
        if not prediction:
            return False
        
        # Verificar confianza mÃ­nima
        if prediction['confidence'] < self.confidence_threshold:
            return False
        
        # Verificar Ã¡rea mÃ­nima de la mÃ¡scara
        min_area = 100  # pÃ­xeles
        if prediction['area'] < min_area:
            return False
        
        # Verificar que la mÃ¡scara no estÃ© vacÃ­a
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
        Guarda informaciÃ³n de debug de una predicciÃ³n.
        
        Args:
            image_path: Ruta a la imagen original
            prediction: PredicciÃ³n a guardar
            output_dir: Directorio de salida
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar mÃ¡scara
        mask = prediction['mask']
        mask_normalized = (mask * 255).astype(np.uint8)
        mask_path = output_dir / f"{image_path.stem}_mask.png"
        cv2.imwrite(str(mask_path), mask_normalized)
        
        # Guardar imagen con bounding box
        image = cv2.imread(str(image_path))
        bbox = prediction['bbox']
        x1, y1, x2, y2 = map(int, bbox)
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # AÃ±adir texto con confianza
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
    FunciÃ³n de conveniencia para crear una instancia de inferencia YOLO.
    
    Args:
        model_path: Ruta al modelo personalizado
        confidence_threshold: Umbral de confianza
        
    Returns:
        Instancia de YOLOSegmentationInference
    """
    return YOLOSegmentationInference(model_path, confidence_threshold)


