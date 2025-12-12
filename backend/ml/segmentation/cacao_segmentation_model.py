"""
Modelo de segmentación YOLO-Seg para granos de cacao.

Este módulo implementa una clase dedicada para segmentación usando YOLOv8-Seg o YOLOv10-Seg,
reemplazando completamente la cascada anterior (U-Net -> rembg -> OpenCV).

Migrado a YOLO-Seg para segmentación más precisa y reducción de falsos positivos.
"""
import numpy as np
import cv2
from pathlib import Path
from typing import Tuple, Optional, Dict, Any
from PIL import Image
import uuid
import tempfile
import os
from datetime import datetime

try:
    from ultralytics import YOLO
    _HAS_YOLO = True
except ImportError:
    YOLO = None
    _HAS_YOLO = False

from ..utils.paths import get_yolo_artifacts_dir, ensure_dir_exists, get_media_root
from ..utils.logs import get_ml_logger
from .processor import SegmentationError

logger = get_ml_logger("cacaoscan.ml.segmentation.yolo_seg")


class CacaoSegmentationModel:
    """
    Modelo de segmentación YOLO-Seg para granos de cacao.
    
    Esta clase maneja:
    - Carga del modelo YOLO-Seg
    - Predicción segmentada
    - Extracción de bounding box
    - Extracción de máscara
    - Recorte exacto con fondo transparente
    - Exportación PNG con fondo transparente
    """
    
    # Clases válidas de cacao
    VALID_CACAO_CLASSES = ["cacao", "cacao_grain", "cocoa", "cocoa_bean"]
    
    # Umbrales de validación
    MIN_CONFIDENCE = 0.75
    MIN_AREA_PIXELS = 2000
    MIN_ASPECT_RATIO = 0.2
    MAX_ASPECT_RATIO = 4.0
    
    def __init__(self, model_path: Optional[Path] = None, confidence_threshold: float = 0.75):
        """
        Inicializa el modelo de segmentación YOLO-Seg.
        
        Args:
            model_path: Ruta al modelo personalizado. Si es None, busca automáticamente.
            confidence_threshold: Umbral de confianza mínimo (por defecto 0.75)
        """
        if not _HAS_YOLO:
            raise ImportError(
                "Ultralytics no está instalado. YOLO-Seg es obligatorio. "
                "Instalar con: pip install ultralytics"
            )
        
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.is_custom_model = False
        
        # Asegurar que el directorio de artefactos existe
        ensure_dir_exists(get_yolo_artifacts_dir())
        
        # Cargar modelo
        self._load_model(model_path)
    
    def _load_model(self, model_path: Optional[Path] = None) -> None:
        """
        Carga el modelo YOLO-Seg.
        
        Args:
            model_path: Ruta al modelo personalizado. Si es None, busca automáticamente.
        """
        try:
            if model_path and model_path.exists():
                logger.info(f"Cargando modelo YOLO-Seg personalizado desde {model_path}")
                self.model = YOLO(str(model_path))
                self.is_custom_model = True
            else:
                # Buscar modelo personalizado entrenado automáticamente
                custom_model_path = self._find_custom_model()
                if custom_model_path:
                    logger.info(f"Cargando modelo YOLO-Seg personalizado desde {custom_model_path}")
                    self.model = YOLO(str(custom_model_path))
                    self.is_custom_model = True
                else:
                    logger.warning("No se encontró modelo personalizado. Usando modelo base YOLOv8s-seg")
                    logger.warning("El modelo base puede no clasificar correctamente granos de cacao")
                    self.model = YOLO('yolov8s-seg.pt')
                    self.is_custom_model = False
            
            logger.info("✅ Modelo YOLO-Seg cargado exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error al cargar el modelo YOLO-Seg: {e}")
            raise SegmentationError(
                f"No se puede cargar el modelo YOLO-Seg: {str(e)}. "
                "YOLO-Seg es obligatorio para segmentación de granos de cacao."
            ) from e
    
    def _find_custom_model(self) -> Optional[Path]:
        """
        Busca automáticamente un modelo personalizado entrenado.
        
        Busca en: ml/artifacts/yolov8-seg/models/cacao_seg_YYYYMMDD_HHMMSS/weights/best.pt
        
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
                        # Si no se puede parsear, usar timestamp de modificación
                        timestamp = best_model.stat().st_mtime
                        best_models.append((str(timestamp), best_model))
        
        if best_models:
            # Ordenar por timestamp (más reciente primero)
            best_models.sort(reverse=True)
            return best_models[0][1]
        
        return None
    
    def predict(self, image_path: str) -> Dict[str, Any]:
        """
        Realiza predicción segmentada con YOLO-Seg.
        
        VALIDACIÓN ESTRICTA: Solo acepta detecciones con confianza >= 0.75 y clase válida.
        No se permiten umbrales bajos para evitar falsos positivos.
        
        Args:
            image_path: Ruta a la imagen a segmentar
            
        Returns:
            Diccionario con resultados de la predicción:
            - confidence: Confianza de la detección
            - class_name: Nombre de la clase detectada
            - bbox: Bounding box [x1, y1, x2, y2]
            - mask: Máscara de segmentación (numpy array)
            - area: Área de la máscara en píxeles
            
        Raises:
            SegmentationError: Si no se detecta un grano válido
        """
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
        
        # Solo intentar con el umbral estricto (0.75)
        # NO permitir umbrales bajos para evitar falsos positivos
        threshold = self.confidence_threshold
        results = self._try_predict_with_threshold(image_path, threshold)
        
        if results is None:
            raise SegmentationError(
                "No se detectó un grano de cacao en la imagen. "
                f"YOLO-Seg no encontró ningún objeto válido con confianza >= {threshold*100:.0f}%. "
                "Solo se aceptan detecciones con alta confianza para garantizar que sea un grano de cacao."
            )
        
        return results
    
    def _try_predict_with_threshold(self, image_path: str, threshold: float) -> Optional[Dict[str, Any]]:
        """
        Intenta realizar una predicción con un umbral específico.
        
        Args:
            image_path: Ruta a la imagen
            threshold: Umbral de confianza
            
        Returns:
            Diccionario con resultados o None si no hay detecciones válidas
        """
        try:
            # Realizar predicción con YOLO
            results = self.model(
                image_path,
                conf=threshold,
                imgsz=640,  # Resolución estándar para mejor precisión
                verbose=False,
                max_det=1,  # Solo necesitamos 1 detección
                iou=0.5
            )
            
            if not results or len(results) == 0:
                return None
            
            result = results[0]
            
            # Verificar que hay detecciones
            if result.boxes is None or len(result.boxes) == 0:
                return None
            
            # Verificar que hay máscaras
            if result.masks is None or len(result.masks) == 0:
                return None
            
            # Obtener la mejor detección (primera, ya que están ordenadas por confianza)
            box = result.boxes[0]
            mask = result.masks[0]
            
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = result.names[class_id].lower().strip()
            bbox = box.xyxy[0].cpu().numpy().tolist()
            
            # Convertir máscara a numpy array
            mask_data = mask.data[0].cpu().numpy()
            mask_resized = mask.data[0].cpu().numpy()
            
            # Obtener dimensiones de la imagen original
            from PIL import Image as PILImage
            with PILImage.open(image_path) as img:
                img_width, img_height = img.size
            
            # Redimensionar máscara a tamaño original si es necesario
            if mask_resized.shape != (img_height, img_width):
                mask_resized = cv2.resize(
                    mask_resized,
                    (img_width, img_height),
                    interpolation=cv2.INTER_NEAREST
                )
            
            # Convertir máscara a binaria (0 o 255)
            mask_binary = (mask_resized > 0.5).astype(np.uint8) * 255
            area = int(np.sum(mask_binary > 0))
            
            # Validar detección con umbral estricto (0.75) - NO se permiten excepciones
            # Siempre usar MIN_CONFIDENCE (0.75) para evitar falsos positivos
            min_confidence_for_validation = self.MIN_CONFIDENCE
            
            # Validar detección con umbral estricto
            try:
                self._validate_detection_with_threshold(
                    confidence, class_name, area, bbox, image_path, min_confidence_for_validation
                )
            except SegmentationError:
                return None
            
            logger.info(
                f"[YOLO-Seg] Detección válida: confidence={confidence:.3f}, "
                f"class_name='{class_name}', area={area} píxeles, "
                f"bbox={[int(x) for x in bbox]}"
            )
            
            return {
                'confidence': confidence,
                'class_name': class_name,
                'class_id': class_id,
                'bbox': bbox,
                'mask': mask_binary,
                'area': area,
                'image_size': (img_width, img_height)
            }
        except Exception as e:
            logger.debug(f"Error en predicción con threshold {threshold}: {e}")
            return None
    
    def _validate_detection(
        self,
        confidence: float,
        class_name: str,
        area: int,
        bbox: list,
        image_path: str
    ) -> None:
        """
        Valida que la detección cumple con los requisitos para un grano de cacao.
        
        Args:
            confidence: Confianza de la detección
            class_name: Nombre de la clase detectada
            area: Área de la máscara en píxeles
            bbox: Bounding box [x1, y1, x2, y2]
            image_path: Ruta a la imagen (para logging)
            
        Raises:
            SegmentationError: Si la detección no es válida
        """
        self._validate_detection_with_threshold(
            confidence, class_name, area, bbox, image_path, self.MIN_CONFIDENCE
        )
    
    def _validate_detection_with_threshold(
        self,
        confidence: float,
        class_name: str,
        area: int,
        bbox: list,
        image_path: str,
        min_confidence: float
    ) -> None:
        """
        Valida que la detección cumple con los requisitos para un grano de cacao.
        
        Args:
            confidence: Confianza de la detección
            class_name: Nombre de la clase detectada
            area: Área de la máscara en píxeles
            bbox: Bounding box [x1, y1, x2, y2]
            image_path: Ruta a la imagen (para logging)
            min_confidence: Umbral de confianza mínimo a usar
            
        Raises:
            SegmentationError: Si la detección no es válida
        """
        filename = Path(image_path).name
        
        # Validación 1: Confianza mínima
        if confidence < min_confidence:
            logger.error(
                f"[YOLO-Seg] Confianza insuficiente: {confidence:.3f} < {min_confidence:.3f} "
                f"en {filename}"
            )
            raise SegmentationError(
                f"No se detectó un grano de cacao válido en la imagen. "
                f"Confianza de detección: {confidence*100:.1f}% "
                f"(mínimo requerido: {min_confidence*100:.0f}%)."
            )
        
        # Validación 2: Clase válida OBLIGATORIA - NO se permiten excepciones
        is_valid_class = False
        if class_name:
            is_valid_class = any(valid_class in class_name for valid_class in self.VALID_CACAO_CLASSES)
            if not is_valid_class:
                is_valid_class = class_name in self.VALID_CACAO_CLASSES
        
        # OBLIGATORIO: La clase debe ser válida, sin excepciones
        # NO se permite continuar con clases inválidas, incluso con buena confianza
        if not is_valid_class:
            logger.error(
                f"[YOLO-Seg] Clase inválida detectada: '{class_name}' "
                f"(clases válidas: {self.VALID_CACAO_CLASSES}) en {filename}. "
                f"Confianza: {confidence:.3f}, Área: {area} píxeles. "
                f"Se rechaza porque no es una clase válida de cacao."
            )
            raise SegmentationError(
                f"No se detectó un grano de cacao válido en la imagen. "
                f"El modelo detectó un objeto de clase '{class_name}', no un grano de cacao. "
                f"Clases válidas requeridas: {', '.join(self.VALID_CACAO_CLASSES)}. "
                f"Si detectó 'seed', 'bean', 'object', u otra clase, se rechaza automáticamente."
            )
        
        # Validación 3: Área mínima
        if area < self.MIN_AREA_PIXELS:
            logger.error(
                f"[YOLO-Seg] Área insuficiente: {area} < {self.MIN_AREA_PIXELS} píxeles "
                f"en {filename}"
            )
            raise SegmentationError(
                f"No se detectó un grano de cacao válido en la imagen. "
                f"Área detectada: {area} píxeles "
                f"(mínimo requerido: {self.MIN_AREA_PIXELS} píxeles)."
            )
        
        # Validación 4: Aspect ratio
        if len(bbox) >= 4:
            bbox_width = bbox[2] - bbox[0]
            bbox_height = bbox[3] - bbox[1]
            if bbox_height > 0:
                aspect_ratio = bbox_width / bbox_height
                if not (self.MIN_ASPECT_RATIO <= aspect_ratio <= self.MAX_ASPECT_RATIO):
                    logger.error(
                        f"[YOLO-Seg] Aspect ratio fuera de rango: {aspect_ratio:.2f} "
                        f"(esperado entre {self.MIN_ASPECT_RATIO:.2f} y {self.MAX_ASPECT_RATIO:.2f}) "
                        f"en {filename}"
                    )
                    raise SegmentationError(
                        f"No se detectó un grano de cacao válido en la imagen. "
                        f"El objeto detectado tiene un aspect ratio inusual ({aspect_ratio:.2f}), "
                        f"lo que sugiere que no es un grano de cacao."
                    )
    
    def apply_mask_and_crop(
        self,
        image_path: str,
        prediction: Dict[str, Any],
        padding: int = 10
    ) -> Image.Image:
        """
        Aplica la máscara a la imagen y recorta el grano con fondo transparente.
        
        Args:
            image_path: Ruta a la imagen original
            prediction: Resultado de la predicción (del método predict)
            padding: Padding alrededor del bounding box
            
        Returns:
            Imagen PIL RGBA con fondo transparente y recorte ajustado a la máscara
        """
        # Cargar imagen original
        image_rgb = np.array(Image.open(image_path).convert('RGB'))
        mask = prediction['mask']
        bbox = prediction['bbox']
        
        # Asegurar que la máscara tiene el mismo tamaño que la imagen
        img_height, img_width = image_rgb.shape[:2]
        if mask.shape != (img_height, img_width):
            mask = cv2.resize(
                mask,
                (img_width, img_height),
                interpolation=cv2.INTER_NEAREST
            )
        
        # Aplicar máscara a la imagen RGB
        mask_3d = np.stack([mask, mask, mask], axis=2) / 255.0
        masked_rgb = (image_rgb * mask_3d).astype(np.uint8)
        
        # Encontrar bounding box ajustado a la máscara (no al bbox de YOLO)
        y_coords, x_coords = np.nonzero(mask > 0)
        if len(x_coords) == 0 or len(y_coords) == 0:
            raise SegmentationError(
                "No se pudo recortar el grano: la máscara no contiene píxeles válidos."
            )
        
        x1 = max(0, int(x_coords.min()) - padding)
        y1 = max(0, int(y_coords.min()) - padding)
        x2 = min(img_width - 1, int(x_coords.max()) + 1 + padding)
        y2 = min(img_height - 1, int(y_coords.max()) + 1 + padding)
        
        # Recortar imagen y máscara
        crop_rgb = masked_rgb[y1:y2, x1:x2]
        crop_mask = mask[y1:y2, x1:x2]
        
        # Crear imagen RGBA
        crop_alpha = crop_mask.astype(np.uint8)
        crop_rgba = np.dstack([crop_rgb, crop_alpha])
        
        return Image.fromarray(crop_rgba, "RGBA")
    
    def segment(self, image: Image.Image) -> Dict[str, Any]:
        """
        Ejecuta segmentación sobre una imagen PIL y retorna metadata completa.
        
        Args:
            image: Imagen PIL a segmentar
            
        Returns:
            Diccionario con:
            - mask: Máscara binaria (np.ndarray, 0 o 255)
            - bbox: Bounding box [x1, y1, x2, y2]
            - class_name: Nombre de la clase detectada
            - confidence: Confianza de detección
            - area_pixels: Área de la máscara en píxeles
            - aspect_ratio: Aspect ratio del bounding box
            - image_width: Ancho de la imagen original
            - image_height: Alto de la imagen original
            
        Raises:
            SegmentationError: Si no se detecta un grano válido
        """
        # Guardar temporalmente la imagen para YOLO (YOLO requiere ruta de archivo)
        temp_file = None
        try:
            # Convertir a RGB si es necesario (YOLO espera RGB)
            if image.mode != 'RGB':
                image_rgb = image.convert('RGB')
            else:
                image_rgb = image
            
            # Guardar en archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                temp_file = tmp.name
                image_rgb.save(temp_file, format='JPEG', quality=95)
            
            # Realizar predicción
            prediction = self.predict(temp_file)
            
            # Calcular aspect ratio
            bbox = prediction['bbox']
            bbox_width = bbox[2] - bbox[0]
            bbox_height = bbox[3] - bbox[1]
            aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 0.0
            
            # Retornar metadata completa
            return {
                'mask': prediction['mask'],
                'bbox': prediction['bbox'],
                'class_name': prediction['class_name'],
                'confidence': prediction['confidence'],
                'area_pixels': prediction['area'],
                'aspect_ratio': aspect_ratio,
                'image_width': prediction['image_size'][0],
                'image_height': prediction['image_size'][1],
                'class_id': prediction.get('class_id', -1)
            }
        finally:
            # Limpiar archivo temporal
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def segment_and_crop(self, image: Image.Image) -> Tuple[Image.Image, Dict[str, Any]]:
        """
        Retorna imagen recortada con fondo transparente y metadata completa.
        
        Args:
            image: Imagen PIL a segmentar y recortar
            
        Returns:
            Tupla de:
            - crop_image: Imagen RGBA del grano con fondo transparente
            - metadata: Diccionario con info de máscara, bbox, métricas, etc.
            
        Raises:
            SegmentationError: Si no se detecta un grano válido
        """
        # Guardar temporalmente la imagen para YOLO
        temp_file = None
        try:
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image_rgb = image.convert('RGB')
            else:
                image_rgb = image
            
            # Guardar en archivo temporal
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                temp_file = tmp.name
                image_rgb.save(temp_file, format='JPEG', quality=95)
            
            # Realizar predicción
            prediction = self.predict(temp_file)
            
            # Aplicar máscara y recortar
            crop_image = self.apply_mask_and_crop(temp_file, prediction)
            
            # Calcular aspect ratio y otras métricas
            bbox = prediction['bbox']
            bbox_width = bbox[2] - bbox[0]
            bbox_height = bbox[3] - bbox[1]
            aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 0.0
            
            # Preparar metadata completa
            metadata = {
                'mask': prediction['mask'],
                'bbox': prediction['bbox'],
                'class_name': prediction['class_name'],
                'confidence': prediction['confidence'],
                'area_pixels': prediction['area'],
                'aspect_ratio': aspect_ratio,
                'image_width': prediction['image_size'][0],
                'image_height': prediction['image_size'][1],
                'crop_width': crop_image.width,
                'crop_height': crop_image.height,
                'class_id': prediction.get('class_id', -1)
            }
            
            logger.info(
                f"[YOLO-Seg] Segmentación completada: "
                f"confidence={metadata['confidence']:.3f}, "
                f"area={metadata['area_pixels']} píxeles, "
                f"aspect_ratio={metadata['aspect_ratio']:.2f}, "
                f"crop_size={metadata['crop_width']}x{metadata['crop_height']}"
            )
            
            return crop_image, metadata
            
        finally:
            # Limpiar archivo temporal
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def segment_and_save(
        self,
        image_path: str,
        output_dir: Optional[Path] = None
    ) -> Tuple[Image.Image, Path]:
        """
        Segmenta una imagen y guarda el resultado como PNG con fondo transparente.
        
        Args:
            image_path: Ruta a la imagen original
            output_dir: Directorio de salida. Si es None, usa el directorio por defecto.
            
        Returns:
            Tupla de (imagen PIL RGBA, Path al archivo guardado)
        """
        # Realizar predicción
        prediction = self.predict(image_path)
        
        # Aplicar máscara y recortar
        crop_image = self.apply_mask_and_crop(image_path, prediction)
        
        # Determinar directorio de salida
        if output_dir is None:
            today = datetime.now()
            media_root = get_media_root()
            output_dir = media_root / "cacao_images" / "processed" / \
                         f"{today.year}" / f"{today.month:02d}" / f"{today.day:02d}"
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo único
        output_filename = f"cacao_{uuid.uuid4().hex}.png"
        output_path = output_dir / output_filename
        
        # Guardar imagen
        crop_image.save(output_path, format='PNG')
        
        logger.info(f"[YOLO-Seg] ✅ Imagen segmentada guardada en: {output_path}")
        
        return crop_image, output_path

