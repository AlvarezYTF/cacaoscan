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
                self.is_custom_model = True
            else:
                # Buscar modelo personalizado entrenado automáticamente
                custom_model_path = self._find_custom_model()
                if custom_model_path:
                    logger.info(f"Cargando modelo personalizado entrenado desde {custom_model_path}")
                    self.model = YOLO(str(custom_model_path))
                    self.is_custom_model = True
                else:
                    logger.info("Cargando modelo base YOLOv8s-seg (no se encontró modelo personalizado)")
                    logger.warning("El modelo base está entrenado en COCO y puede clasificar incorrectamente los granos de cacao")
                    logger.warning("Se recomienda entrenar un modelo personalizado para mejor precisión")
                    self.model = YOLO('yolov8s-seg.pt')
                    self.is_custom_model = False
            
            logger.info("Modelo YOLOv8-seg cargado exitosamente")
            
        except Exception as e:
            logger.error(f"Error al cargar el modelo YOLO: {e}")
            raise
    
    def _find_custom_model(self) -> Optional[Path]:
        """
        Busca automáticamente un modelo personalizado entrenado.
        
        Returns:
            Ruta al modelo personalizado si existe, None en caso contrario
        """
        artifacts_dir = get_yolo_artifacts_dir()
        models_dir = artifacts_dir / "models"
        
        if not models_dir.exists():
            return None
        
        # Buscar el mejor modelo en subdirectorios de entrenamiento
        # Los modelos se guardan en: models/cacao_seg_YYYYMMDD_HHMMSS/weights/best.pt
        best_models = []
        for train_dir in models_dir.iterdir():
            if train_dir.is_dir():
                weights_dir = train_dir / "weights"
                best_model = weights_dir / "best.pt"
                if best_model.exists():
                    # Obtener timestamp del directorio para ordenar
                    try:
                        timestamp = train_dir.name.split("_")[-2:]  # Obtener fecha y hora
                        timestamp_str = "_".join(timestamp)
                        best_models.append((timestamp_str, best_model))
                    except Exception:
                        best_models.append((train_dir.name, best_model))
        
        if best_models:
            # Ordenar por timestamp (más reciente primero)
            best_models.sort(reverse=True)
            return best_models[0][1]
        
        return None
    
    def predict(self, image_path: Path, conf_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Realiza predicción de segmentación en una imagen.
        
        Args:
            image_path: Ruta a la imagen
            conf_threshold: Umbral de confianza (usa self.confidence_threshold si es None)
            
        Returns:
            Lista de predicciones con información de detección y segmentación
        """
        # Asegurar que trabajamos siempre con Path
        if not isinstance(image_path, Path):
            image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
        
        try:
            # Usar threshold proporcionado o el predeterminado
            threshold = conf_threshold if conf_threshold is not None else self.confidence_threshold
            
            # Realizar predicción con umbral inicial
            results = self.model(str(image_path), conf=threshold)
            predictions = self._process_yolo_results(results)
            
            # Si no hay detecciones, intentar con umbrales más bajos
            if not predictions:
                lower_thresholds = [0.4, 0.3, 0.25, 0.2, 0.15, 0.1]
                predictions = self._try_lower_thresholds(image_path, lower_thresholds, min_confidence_ratio=0.8)
            
            # Si aún no hay detecciones y el umbral inicial era alto, intentar con umbrales más bajos
            if not predictions and threshold > 0.25:
                logger.debug(f"No se encontraron detecciones con conf={threshold:.2f}, intentando con umbral más bajo...")
                fallback_thresholds = [0.4, 0.3, 0.25]
                predictions = self._try_lower_thresholds(image_path, fallback_thresholds, min_confidence_ratio=1.0)
            
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
    
    def _process_yolo_results(self, results: Any, min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Processes YOLO results and extracts predictions."""
        predictions = []
        
        for result in results:
            if result.masks is None or len(result.masks) == 0:
                continue
                
            boxes = result.boxes
            masks = result.masks
            
            for i in range(len(boxes)):
                box = boxes[i]
                conf = float(box.conf[0])
                
                if conf < min_confidence:
                    continue
                
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
        
        return predictions
    
    def _try_lower_thresholds(
        self,
        image_path: Path,
        thresholds: List[float],
        min_confidence_ratio: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Tries prediction with progressively lower thresholds."""
        for lower_threshold in thresholds:
            logger.debug(f"Intentando detección con umbral {lower_threshold}...")
            results = self.model(str(image_path), conf=lower_threshold)
            predictions = self._process_yolo_results(
                results,
                min_confidence=lower_threshold * min_confidence_ratio
            )
            
            if predictions:
                return predictions
        
        return []
    
    def get_best_prediction(self, image_path: Path) -> Optional[Dict[str, Any]]:
        """
        Obtiene la mejor predicción (mayor confianza) para una imagen.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Mejor predicción o None si no hay detecciones
        """
        # Asegurar siempre un Path para logging y acceso a disco
        if not isinstance(image_path, Path):
            image_path = Path(image_path)

        predictions = self.predict(image_path)
        if not predictions:
            return None
        
        # Si es modelo personalizado, usar la primera (ya ordenada por confianza)
        if hasattr(self, 'is_custom_model') and self.is_custom_model:
            return predictions[0]
        
        # Para modelo base, ignorar la clase y seleccionar por mejor combinación de área y confianza
        # Priorizar predicciones con mayor área y confianza razonable
        best_pred = None
        best_score = 0
        
        for pred in predictions:
            # Score combinado: área * confianza
            # Esto prioriza máscaras grandes con buena confianza
            area = pred.get('area', 0)
            confidence = pred.get('confidence', 0)
            score = area * confidence
            
            if score > best_score:
                best_score = score
                best_pred = pred
        
        if best_pred:
            # Log informativo sobre la clase detectada (pero no afecta la selección)
            class_name = best_pred.get('class_name', 'unknown')
            if class_name not in ['cacao_grain', 'cacao']:
                logger.debug(
                    "Modelo base detectó clase '%s' en %s. Usando máscara con área=%s y confianza=%.2f",
                    class_name,
                    image_path.name,
                    best_pred.get('area', 0),
                    best_pred.get('confidence', 0.0),
                )
        
        return best_pred
    
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


