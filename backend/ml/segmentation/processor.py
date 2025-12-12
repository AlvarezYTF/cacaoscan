"""
Módulo de procesamiento de segmentación para granos de cacao.

REFACTORIZADO: Aplicando principios SOLID
- Funciones auxiliares extraídas para mejorar SRP
- Mejores docstrings y type hints
- Separación de responsabilidades mejorada
"""
import os
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional, Dict, Any, List
from PIL import Image
import io
try:
    import cv2.ximgproc as ximgproc  # type: ignore[import-untyped] # Opcional: guidedFilter
    _HAS_XIMGPROC = True
except ImportError:
    _HAS_XIMGPROC = False
import cv2
import numpy as np

from ml.data.transforms import remove_background_ai
from ..utils.logs import get_ml_logger

try:
    # Opcional: modelo U2Net a través de rembg para recorte de alta calidad
    from rembg import remove as rembg_remove
    _HAS_REMBG = True
except Exception:
    _HAS_REMBG = False

# YOLO para validación rápida de detección de granos
try:
    from .infer_yolo_seg import create_yolo_inference
    _HAS_YOLO = True
    _yolo_validator = None  # Se inicializa lazy
except Exception:
    _HAS_YOLO = False
    _yolo_validator = None

logger = get_ml_logger("cacaoscan.ml.segmentation.processor")


class SegmentationError(Exception):
    """Excepción personalizada para errores de segmentación."""
    pass


def _validate_with_yolo_fast(image_path: str, min_confidence: float = 0.75) -> bool:
    """
    Valida OBLIGATORIAMENTE con YOLO si hay un grano de cacao en la imagen.
    YOLO ES OBLIGATORIO: Si YOLO falla, no detecta nada, o detecta una clase incorrecta,
    se lanza SegmentationError y se detiene el proceso. NO se permite continuar con OpenCV.
    
    VALIDACIONES ESTRICTAS PARA ELIMINAR FALSOS POSITIVOS:
    - Confianza mínima: 0.75 (75%) - muy estricto
    - Área mínima: 0.5% de la imagen (mínimo absoluto 2000 píxeles)
    - Área máxima: 40% de la imagen (para evitar objetos gigantes como dunas)
    - Proporción del objeto: entre 0.5% y 40% de la imagen
    - Aspect ratio: entre 0.2 y 4.0
    - Clase obligatoria: debe ser "cacao", "cacao_grain", "cocoa", o "cocoa_bean"
    
    Args:
        image_path: Ruta a la imagen
        min_confidence: Confianza mínima requerida (0.75 = 75% por defecto, estricto)
        
    Returns:
        True si YOLO detecta un grano válido
        
    Raises:
        SegmentationError: Si YOLO no detecta un grano válido, falla, o detecta clase incorrecta
    """
    global _yolo_validator
    
    # YOLO ES OBLIGATORIO: Si no está disponible, lanzar error
    if not _HAS_YOLO:
        logger.error("YOLO no disponible - YOLO es obligatorio para validación de granos de cacao")
        raise SegmentationError(
            "No se puede validar la imagen: YOLO no está disponible. "
            "YOLO es obligatorio para garantizar que solo se procesen granos de cacao válidos."
        )
    
    # Lista de clases válidas de cacao
    VALID_CACAO_CLASSES = ["cacao", "cacao_grain", "cocoa", "cocoa_bean"]
    
    try:
        # Inicializar YOLO lazy (solo una vez)
        if _yolo_validator is None:
            logger.info("Inicializando YOLO para validación obligatoria...")
            _yolo_validator = create_yolo_inference(confidence_threshold=min_confidence)
        
        # VALIDACIÓN OBLIGATORIA: Solo una predicción directa
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
        
        # Leer dimensiones de la imagen para validaciones relativas
        from PIL import Image as PILImage
        with PILImage.open(image_path) as img:
            img_width, img_height = img.size
            total_pixels = img_width * img_height
        
        logger.info(
            f"[YOLO OBLIGATORIO] Validando: imagen={image_path_obj.name}, "
            f"dimensiones={img_width}x{img_height}, total_pixels={total_pixels}, "
            f"min_confidence={min_confidence:.2f}"
        )
        
        # Predicción con umbral estricto
        results = _yolo_validator.model(
            str(image_path),
            conf=min_confidence,  # Umbral estricto (0.75 = 75%)
            imgsz=320,  # Resolución más baja para validación rápida
            verbose=False,  # Sin logs verbosos
            max_det=1,  # Solo necesitamos 1 detección para validar
            iou=0.5  # NMS estándar
        )
        
        # Procesar resultados
        predictions = _yolo_validator._process_yolo_results(results, min_confidence=min_confidence)
        
        if not predictions:
            # YOLO no detectó nada - OBLIGATORIO rechazar
            logger.error(
                f"[YOLO OBLIGATORIO] No detectó ningún objeto en {image_path_obj.name} "
                f"(confianza mínima={min_confidence:.2f})"
            )
            raise SegmentationError(
                "No se detectó un grano de cacao en la imagen. "
                "El modelo de detección YOLO no encontró ningún grano válido. "
                "YOLO es obligatorio para garantizar que solo se procesen granos de cacao."
            )
        
        # Verificar que la mejor predicción tenga confianza suficiente
        best_prediction = max(predictions, key=lambda p: p['confidence'])
        
        # Log detallado de la mejor predicción
        logger.info(
            f"[YOLO] Detectó objeto: confidence={best_prediction['confidence']:.3f}, "
            f"area={best_prediction['area']}, class_name={best_prediction.get('class_name', 'unknown')}"
        )
        
        # VALIDACIÓN 1: Confianza mínima estricta (0.75)
        if best_prediction['confidence'] < min_confidence:
            logger.error(
                f"[YOLO OBLIGATORIO] Confianza insuficiente: {best_prediction['confidence']:.3f} < {min_confidence:.3f} "
                f"en {image_path_obj.name}"
            )
            raise SegmentationError(
                f"No se detectó un grano de cacao válido en la imagen. "
                f"Confianza de detección: {best_prediction['confidence']*100:.1f}% "
                f"(mínimo requerido: {min_confidence*100:.0f}%)."
            )
        
        # VALIDACIÓN 2: Área mínima y máxima RELATIVA al tamaño de imagen
        object_ratio = best_prediction['area'] / total_pixels if total_pixels > 0 else 0
        min_area_ratio = 0.005  # 0.5% de la imagen (mínimo)
        max_area_ratio = 0.40  # 40% de la imagen (máximo - para evitar objetos gigantes como dunas)
        min_area = max(2000, int(min_area_ratio * total_pixels))  # Mínimo absoluto de 2000 píxeles
        
        if best_prediction['area'] < min_area:
            logger.error(
                f"[YOLO OBLIGATORIO] Área muy pequeña: {best_prediction['area']} < {min_area} "
                f"({object_ratio*100:.2f}% < {min_area_ratio*100:.2f}%) en {image_path_obj.name}"
            )
            raise SegmentationError(
                f"No se detectó un grano de cacao válido en la imagen. "
                f"El área detectada es muy pequeña: {best_prediction['area']} píxeles "
                f"({object_ratio*100:.2f}% de la imagen, "
                f"mínimo requerido: {min_area} píxeles o {min_area_ratio*100:.2f}%)."
            )
        
        # VALIDACIÓN 3: Proporción del objeto respecto a la imagen (mínimo y máximo)
        if object_ratio < min_area_ratio:
            logger.error(
                f"[YOLO OBLIGATORIO] Proporción muy pequeña: {object_ratio*100:.2f}% < {min_area_ratio*100:.2f}% "
                f"en {image_path_obj.name}"
            )
            raise SegmentationError(
                f"No se detectó un grano de cacao válido en la imagen. "
                f"El objeto detectado ocupa solo el {object_ratio*100:.2f}% de la imagen "
                f"(mínimo requerido: {min_area_ratio*100:.2f}%)."
            )
        
        if object_ratio > max_area_ratio:
            logger.error(
                f"[YOLO OBLIGATORIO] Proporción muy grande (posible objeto gigante como dunas): "
                f"{object_ratio*100:.2f}% > {max_area_ratio*100:.0f}% en {image_path_obj.name}"
            )
            raise SegmentationError(
                f"No se detectó un grano de cacao válido en la imagen. "
                f"El objeto detectado ocupa el {object_ratio*100:.2f}% de la imagen "
                f"(máximo permitido: {max_area_ratio*100:.0f}%). "
                f"Esto sugiere que no es un grano de cacao (posiblemente un objeto gigante como dunas)."
            )
        
        # VALIDACIÓN 4: Aspect ratio del bounding box
        bbox = best_prediction.get('bbox', [])
        aspect_ratio = None
        if len(bbox) >= 4:
            bbox_width = bbox[2] - bbox[0]
            bbox_height = bbox[3] - bbox[1]
            if bbox_height > 0:
                aspect_ratio = bbox_width / bbox_height
                min_aspect_ratio = 0.2
                max_aspect_ratio = 4.0
                if not (min_aspect_ratio <= aspect_ratio <= max_aspect_ratio):
                    logger.error(
                        f"[YOLO OBLIGATORIO] Aspect ratio fuera de rango: {aspect_ratio:.2f} "
                        f"(esperado entre {min_aspect_ratio:.2f} y {max_aspect_ratio:.2f}) "
                        f"en {image_path_obj.name}"
                    )
                    raise SegmentationError(
                        f"No se detectó un grano de cacao válido en la imagen. "
                        f"El objeto detectado tiene un aspect ratio inusual ({aspect_ratio:.2f}), "
                        f"lo que sugiere que no es un grano de cacao."
                    )
        
        # VALIDACIÓN 5: Clase OBLIGATORIA - debe ser cacao o variantes
        class_name = best_prediction.get('class_name', '').lower().strip()
        is_valid_class = False
        
        # Si no hay class_name, rechazar (no podemos confirmar que sea cacao)
        if not class_name:
            logger.error(
                f"[YOLO OBLIGATORIO] No se detectó nombre de clase (class_name vacío) "
                f"en {image_path_obj.name}. Se requiere una clase válida de cacao."
            )
            raise SegmentationError(
                f"No se detectó un grano de cacao válido en la imagen. "
                f"El modelo no devolvió un nombre de clase válido. "
                f"Clases válidas requeridas: {', '.join(VALID_CACAO_CLASSES)}."
            )
        
        # Verificar si la clase contiene alguna de las clases válidas
        is_valid_class = any(valid_class in class_name for valid_class in VALID_CACAO_CLASSES)
        
        # También verificar si es exactamente una de las clases válidas
        if not is_valid_class:
            is_valid_class = class_name in VALID_CACAO_CLASSES
        
        if not is_valid_class:
            logger.error(
                f"[YOLO OBLIGATORIO] Clase inválida detectada: '{class_name}' "
                f"(clases válidas: {VALID_CACAO_CLASSES}) en {image_path_obj.name}"
            )
            raise SegmentationError(
                f"No se detectó un grano de cacao válido en la imagen. "
                f"El modelo detectó un objeto de clase '{class_name}', no un grano de cacao. "
                f"Clases válidas requeridas: {', '.join(VALID_CACAO_CLASSES)}. "
                f"Si detectó 'seed', 'bean', 'object', etc., se rechaza automáticamente."
            )
        
        # Log de validación exitosa con todas las métricas
        aspect_ratio_str = f"{aspect_ratio:.2f}" if aspect_ratio is not None else "N/A"
        logger.info(
            f"[YOLO OBLIGATORIO] ✅ Validación exitosa: "
            f"confidence={best_prediction['confidence']:.3f}, "
            f"area={best_prediction['area']} píxeles, "
            f"object_ratio={object_ratio*100:.2f}% (rango: {min_area_ratio*100:.2f}%-{max_area_ratio*100:.0f}%), "
            f"aspect_ratio={aspect_ratio_str}, "
            f"class_name='{class_name}' en {image_path_obj.name}"
        )
        return True
        
    except SegmentationError:
        # Propagar SegmentationError inmediatamente - NO permitir continuar
        raise
    except Exception as e:
        # Si hay error con YOLO, OBLIGATORIO lanzar error - NO permitir continuar con OpenCV
        logger.error(
            f"[YOLO OBLIGATORIO] Error en validación YOLO: {e} "
            f"en {image_path_obj.name if 'image_path_obj' in locals() else image_path}"
        )
        raise SegmentationError(
            f"No se puede validar la imagen: Error en YOLO: {str(e)}. "
            "YOLO es obligatorio para garantizar que solo se procesen granos de cacao válidos."
        ) from e


# Alias para compatibilidad
_validate_with_yolo = _validate_with_yolo_fast


def _estimar_color_fondo(rgb: np.ndarray, bg_mask: np.ndarray) -> np.ndarray:
    """Estima el color de fondo usando la mediana de píxeles de fondo."""
    bg_pixels = rgb[bg_mask]
    return np.median(bg_pixels.reshape(-1, 3), axis=0).astype(np.uint8)


def _calcular_delta_color(rgb_lab: np.ndarray, bg_lab: np.ndarray) -> np.ndarray:
    """Calcula la diferencia de color en espacio LAB."""
    dl = (rgb_lab[:, :, 0] - bg_lab[0]).astype(np.float32)
    da = (rgb_lab[:, :, 1] - bg_lab[1]).astype(np.float32)
    db = (rgb_lab[:, :, 2] - bg_lab[2]).astype(np.float32)
    return cv2.magnitude(dl, cv2.magnitude(da, db))


def _calcular_gradiente_imagen(rgb: np.ndarray) -> np.ndarray:
    """Calcula el gradiente de la imagen para detectar bordes."""
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    return cv2.magnitude(gx, gy)


def _aplicar_limpieza_morfologica(alpha: np.ndarray) -> np.ndarray:
    """Aplica limpieza morfológica y suavizado al canal alpha."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    new_alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel, iterations=1)
    return cv2.GaussianBlur(new_alpha, (5, 5), 0)


def _normalizar_mascara_binaria(mask: np.ndarray) -> np.ndarray:
    """Normaliza una máscara a formato binario uint8."""
    if mask.max() <= 1.0 and mask.dtype != np.uint8:
        return (mask * 255).astype(np.uint8)
    return np.uint8(mask)


def _calcular_area_minima(h: int, w: int, min_area_ratio: float) -> int:
    """Calcula el área mínima basada en la proporción de la imagen."""
    return max(16, int(min_area_ratio * h * w))


def _obtener_componente_mayor(cnts: list, min_area: int) -> Optional[np.ndarray]:
    """Obtiene el contorno del componente mayor que cumple el área mínima."""
    cnts_filtrados = [c for c in cnts if cv2.contourArea(c) >= float(min_area)]
    if not cnts_filtrados:
        return None
    return max(cnts_filtrados, key=cv2.contourArea)


def _aplicar_refinamiento_guided(rgb: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """Aplica refinamiento guiado usando guidedFilter o bilateralFilter."""
    if _HAS_XIMGPROC:
        try:
            guide = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            guide = cv2.blur(guide, (3, 3))
            a32 = (alpha.astype(np.float32) / 255.0)
            refined = ximgproc.guidedFilter(guide=guide, src=a32, radius=8, eps=1e-3)
            return (np.clip(refined, 0.0, 1.0) * 255.0).astype(np.uint8)
        except Exception:
            pass
    return cv2.bilateralFilter(alpha, d=0, sigmaColor=35, sigmaSpace=9)


def _calcular_padding_recorte(x1: int, x2: int, y1: int, y2: int) -> Tuple[int, int, int, int]:
    """Calcula el padding para el recorte tight."""
    pad_x = max(10, int(0.08 * (x2 - x1 + 1)))
    pad_y = max(10, int(0.08 * (y2 - y1 + 1)))
    return pad_x, pad_y


def _aplicar_padding_coordenadas(x1: int, y1: int, x2: int, y2: int, w: int, h: int, pad_x: int, pad_y: int) -> Tuple[int, int, int, int]:
    """Aplica padding a las coordenadas del recorte respetando los límites de la imagen."""
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w - 1, x2 + pad_x)
    y2 = min(h - 1, y2 + pad_y)
    return x1, y1, x2, y2

def _deshadow_alpha(rgb: np.ndarray, alpha: np.ndarray, max_dist: int = 35) -> np.ndarray:
    """
    Elimina sombras adyacentes al objeto sin perder borde real.
    
    Args:
        rgb: Imagen RGB
        alpha: Canal alpha
        max_dist: Distancia máxima al borde para considerar sombra
        
    Returns:
        Canal alpha sin sombras
    """
    bg_mask = alpha == 0
    if not np.any(bg_mask):
        return alpha

    # Estimar color de fondo
    bg_color = _estimar_color_fondo(rgb, bg_mask)

    # Convertir a Lab y calcular delta de color
    rgb_lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.int16)
    bg_lab = cv2.cvtColor(np.uint8([[bg_color]]), cv2.COLOR_RGB2LAB)[0, 0].astype(np.int16)
    delta = _calcular_delta_color(rgb_lab, bg_lab)

    # Gradiente para evitar comer borde de alto contraste
    grad = _calcular_gradiente_imagen(rgb)

    # Distancia al fondo para limitar a una franja alrededor del objeto
    dist_to_bg = cv2.distanceTransform((alpha > 0).astype(np.uint8), cv2.DIST_L2, 5)

    shadow_like = (
        (alpha > 0) &
        (delta < 12.0) &               # parecido al fondo
        (grad < 20.0) &                # bajo contraste
        (dist_to_bg < float(max_dist)) # pegado al borde
    )

    new_alpha = alpha.copy()
    new_alpha[shadow_like] = 0

    # Limpieza morfológica ligera + feather
    return _aplicar_limpieza_morfologica(new_alpha)


def _clean_components(mask: np.ndarray, min_area_ratio: float = 0.002) -> np.ndarray:
    """
    Conserva el componente mayor, elimina ruido y rellena huecos.
    
    Args:
        mask: Máscara binaria
        min_area_ratio: Proporción mínima del área de la imagen para considerar componente
        
    Returns:
        Máscara limpia con solo el componente mayor
    """
    h, w = mask.shape
    min_area = _calcular_area_minima(h, w, min_area_ratio)
    
    # Normalizar máscara a binaria uint8
    mask_bin = _normalizar_mascara_binaria(mask)

    cnts, _ = cv2.findContours(mask_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    out = np.zeros_like(mask_bin)
    if not cnts:
        return mask

    # Obtener componente mayor
    largest = _obtener_componente_mayor(cnts, min_area)
    if largest is None:
        return mask_bin

    cv2.drawContours(out, [largest], -1, 255, thickness=cv2.FILLED)
    
    # Rellenar huecos internos
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    out = cv2.morphologyEx(out, cv2.MORPH_CLOSE, kernel, iterations=2)
    return out


def _guided_refine(rgb: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """
    Refina alpha guiado por bordes de la imagen para un recorte más nítido.
    
    Args:
        rgb: Imagen RGB
        alpha: Canal alpha a refinar
        
    Returns:
        Canal alpha refinado
    """
    return _aplicar_refinamiento_guided(rgb, alpha)


def _remove_background_opencv(image_path: str) -> Image.Image:
    """
    Elimina fondo con OpenCV con mejores resultados y devuelve un PNG RGBA listo para recortar.
    
    Args:
        image_path: Ruta a la imagen original
        
    Returns:
        Imagen PIL RGBA con fondo transparente
        
    Raises:
        FileNotFoundError: Si no se puede leer la imagen
    """
    bgr = cv2.imread(image_path)
    if bgr is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {image_path}")

    h, w = bgr.shape[:2]
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

    # 1) Mapa inicial de foreground con Otsu sobre luminancia
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    if np.mean(otsu) > 127:
        initial = 255 - otsu
    else:
        initial = otsu

    # Morfología para consolidar regiones
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    initial = cv2.morphologyEx(initial, cv2.MORPH_OPEN, kernel, iterations=1)
    initial = cv2.morphologyEx(initial, cv2.MORPH_CLOSE, kernel, iterations=2)

    # 2) GrabCut con máscara inicial
    gc_mask = np.full((h, w), cv2.GC_PR_BGD, np.uint8)
    gc_mask[initial > 0] = cv2.GC_PR_FGD
    bgd = np.zeros((1, 65), np.float64)
    fgd = np.zeros((1, 65), np.float64)
    try:
        cv2.grabCut(bgr, gc_mask, None, bgd, fgd, 5, cv2.GC_INIT_WITH_MASK)
    except Exception:
        rect = (10, 10, max(1, w - 20), max(1, h - 20))
        gc_mask = np.zeros((h, w), np.uint8)
        cv2.grabCut(bgr, gc_mask, rect, bgd, fgd, 5, cv2.GC_INIT_WITH_RECT)

    bin_mask = np.where((gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
    bin_mask = _clean_components(bin_mask)

    # VALIDACIÓN TEMPRANA: Verificar rápidamente si hay suficiente área antes de procesar más
    total_pixels = h * w
    foreground_pixels = np.sum(bin_mask > 0)
    foreground_ratio = foreground_pixels / total_pixels if total_pixels > 0 else 0
    
    logger.info(
        f"OpenCV segmentación: dimensiones={w}x{h}, total_pixels={total_pixels}, "
        f"foreground_pixels={foreground_pixels}, foreground_ratio={foreground_ratio*100:.2f}%"
    )
    
    # AJUSTE: Área mínima reducida de 2% a 0.8% (más permisivo para reducir falsos negativos)
    min_foreground_ratio = 0.008  # Mínimo 0.8% de la imagen debe ser foreground (antes 2%)
    min_foreground_pixels = max(3000, int(min_foreground_ratio * total_pixels))  # Mínimo absoluto de 3000 píxeles
    
    if foreground_pixels < min_foreground_pixels or foreground_ratio < min_foreground_ratio:
        logger.warning(
            f"OpenCV detectó área insuficiente: {foreground_pixels} píxeles ({foreground_ratio*100:.2f}%) "
            f"< {min_foreground_pixels} píxeles o {min_foreground_ratio*100:.2f}%"
        )
        raise SegmentationError(
            f"No se detectó un grano de cacao en la imagen. "
            f"El área detectada ocupa solo el {foreground_ratio*100:.2f}% de la imagen "
            f"({foreground_pixels} píxeles, mínimo requerido: {min_foreground_ratio*100:.2f}% o {min_foreground_pixels} píxeles)."
        )
    
    # 3) Mantener solo el mayor contorno
    cnts, _ = cv2.findContours(bin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if cnts:
        largest = max(cnts, key=cv2.contourArea)
        largest_area = cv2.contourArea(largest)
        
        # VALIDACIÓN TEMPRANA: Verificar que el contorno más grande tenga área suficiente (relativa)
        # AJUSTE: Área mínima ahora relativa (0.4% de la imagen) con mínimo absoluto de 3000 píxeles
        min_contour_area_ratio = 0.004  # 0.4% de la imagen (antes era 5000 píxeles fijos)
        min_contour_area = max(3000, int(min_contour_area_ratio * total_pixels))
        
        logger.info(
            f"OpenCV contorno mayor: area={largest_area:.0f} píxeles "
            f"({largest_area/total_pixels*100:.2f}% de imagen), "
            f"min_requerido={min_contour_area} píxeles ({min_contour_area_ratio*100:.2f}%)"
        )
        
        if largest_area < min_contour_area:
            logger.warning(
                f"OpenCV contorno mayor con área insuficiente: {largest_area:.0f} < {min_contour_area} "
                f"({largest_area/total_pixels*100:.2f}% < {min_contour_area_ratio*100:.2f}%)"
            )
            raise SegmentationError(
                f"No se detectó un grano de cacao en la imagen. "
                f"El área del objeto detectado es de {largest_area:.0f} píxeles "
                f"({largest_area/total_pixels*100:.2f}% de la imagen, "
                f"mínimo requerido: {min_contour_area} píxeles o {min_contour_area_ratio*100:.2f}%)."
            )
        
        clean = np.zeros_like(bin_mask)
        cv2.drawContours(clean, [largest], -1, 255, thickness=cv2.FILLED)
        hull = cv2.convexHull(largest)
        hull_mask = np.zeros_like(bin_mask)
        cv2.drawContours(hull_mask, [hull], -1, 255, thickness=cv2.FILLED)
        clean = cv2.bitwise_and(clean, hull_mask)
    else:
        # No hay contornos, definitivamente no hay grano
        raise SegmentationError(
            "No se detectó un grano de cacao en la imagen. No se encontraron objetos válidos en la segmentación."
        )

    # 4) Feather del borde para alpha suave
    edge = cv2.Canny(clean, 50, 150)
    feather = cv2.GaussianBlur(edge, (21, 21), 0)
    alpha = np.clip(clean.astype(np.float32) + feather.astype(np.float32), 0, 255).astype(np.uint8)
    alpha = _deshadow_alpha(rgb, alpha)
    alpha = _guided_refine(rgb, alpha)

    # 5) Recorte tight con padding
    ys, xs = np.nonzero(alpha > 0)
    if len(xs) == 0 or len(ys) == 0:
        # VALIDACIÓN TEMPRANA: Si no hay píxeles no transparentes, no hay grano
        raise SegmentationError(
            "No se detectó un grano de cacao en la imagen. No se encontraron píxeles válidos después de la segmentación."
        )

    x1, x2 = xs.min(), xs.max()
    y1, y2 = ys.min(), ys.max()
    
    # VALIDACIÓN TEMPRANA: Verificar dimensiones del bounding box antes de recortar (relativas)
    bbox_width = x2 - x1 + 1
    bbox_height = y2 - y1 + 1
    bbox_area = bbox_width * bbox_height
    
    # AJUSTE: Dimensiones mínimas ahora relativas al tamaño de imagen
    # Mínimo 2% del ancho/alto de la imagen, con mínimo absoluto de 40 píxeles
    min_bbox_dimension_ratio = 0.02  # 2% de la dimensión de la imagen
    min_bbox_dimension = max(40, int(min(min_bbox_dimension_ratio * w, min_bbox_dimension_ratio * h)))
    min_bbox_area_ratio = 0.003  # 0.3% del área total (antes 2500 píxeles fijos)
    min_bbox_area = max(2000, int(min_bbox_area_ratio * total_pixels))
    
    logger.info(
        f"OpenCV bbox: dimensiones={bbox_width}x{bbox_height}, area={bbox_area} píxeles² "
        f"({bbox_area/total_pixels*100:.2f}% de imagen), "
        f"min_dimension={min_bbox_dimension}, min_area={min_bbox_area}"
    )
    
    if bbox_width < min_bbox_dimension or bbox_height < min_bbox_dimension:
        logger.warning(
            f"OpenCV bbox con dimensiones insuficientes: {bbox_width}x{bbox_height} < {min_bbox_dimension}x{min_bbox_dimension}"
        )
        raise SegmentationError(
            f"No se detectó un grano de cacao en la imagen. "
            f"Dimensiones del objeto detectado: {bbox_width}x{bbox_height} píxeles "
            f"(mínimo requerido: {min_bbox_dimension}x{min_bbox_dimension}, "
            f"equivalente a {min_bbox_dimension_ratio*100:.0f}% de la imagen)."
        )
    
    if bbox_area < min_bbox_area:
        logger.warning(
            f"OpenCV bbox con área insuficiente: {bbox_area} < {min_bbox_area} "
            f"({bbox_area/total_pixels*100:.2f}% < {min_bbox_area_ratio*100:.2f}%)"
        )
        raise SegmentationError(
            f"No se detectó un grano de cacao en la imagen. "
            f"Área del objeto detectado: {bbox_area} píxeles cuadrados "
            f"({bbox_area/total_pixels*100:.2f}% de la imagen, "
            f"mínimo requerido: {min_bbox_area} píxeles cuadrados o {min_bbox_area_ratio*100:.2f}%)."
        )
    
    pad_x, pad_y = _calcular_padding_recorte(x1, x2, y1, y2)
    x1, y1, x2, y2 = _aplicar_padding_coordenadas(x1, y1, x2, y2, w, h, pad_x, pad_y)

    crop_rgb = rgb[y1:y2 + 1, x1:x2 + 1]
    crop_a = alpha[y1:y2 + 1, x1:x2 + 1]

    smooth_a = _guided_refine(crop_rgb, _deshadow_alpha(crop_rgb, crop_a))
    rgba = np.dstack([crop_rgb, smooth_a])
    return Image.fromarray(rgba, "RGBA")


def _remove_background_rembg(image_path: str) -> Image.Image:
    """
    Usa rembg (U2Net) para un recorte de alta calidad (si está disponible).
    
    Args:
        image_path: Ruta a la imagen original
        
    Returns:
        Imagen PIL RGBA con fondo transparente
        
    Raises:
        RuntimeError: Si rembg no está disponible
    """
    if not _HAS_REMBG:
        raise RuntimeError("rembg no disponible")
    with open(image_path, 'rb') as f:
        data = f.read()
    out = rembg_remove(data)
    return Image.open(io.BytesIO(out)).convert("RGBA")


def _processed_dir_for_today() -> Path:
    """
    Obtiene el directorio de procesados para el día actual.
    
    Returns:
        Path al directorio YYYY/MM/DD
    """
    today = datetime.now()
    output_dir = Path("media") / "cacao_images" / "processed" / f"{today.year}" / f"{today.month:02d}" / f"{today.day:02d}"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def save_processed_png(pil_png: Image.Image, out_name: str) -> Path:
    """
    Guarda un PNG RGBA en media/cacao_images/processed/YYYY/MM/DD y retorna su Path.
    
    Args:
        pil_png: Imagen PIL RGBA
        out_name: Nombre del archivo de salida
        
    Returns:
        Path al archivo guardado
    """
    output_dir = _processed_dir_for_today()
    out_path = output_dir / out_name
    pil_png.convert("RGBA").save(out_path)
    return out_path


def _process_with_opencv(image_path: str, filename: str) -> Image.Image:
    """
    Procesa imagen usando OpenCV directamente.
    VALIDACIÓN PREVIA: Usa YOLO para validar que hay un grano antes de procesar.
    
    Args:
        image_path: Ruta a la imagen
        filename: Nombre del archivo para logging
        
    Returns:
        Imagen PIL RGBA procesada
        
    Raises:
        SegmentationError: Si YOLO no detecta un grano o si OpenCV no detecta un grano válido
        FileNotFoundError: Si no se puede procesar la imagen
    """
    logger.debug("Segmentación solicitada con backend OpenCV (modo directo)")
    try:
        # YOLO ES OBLIGATORIO: Debe validar antes de procesar con OpenCV
        # Si YOLO falla, NO se permite continuar con OpenCV
        logger.info("[YOLO OBLIGATORIO] Validando con YOLO antes de procesar con OpenCV...")
        _validate_with_yolo_fast(image_path, min_confidence=0.75)  # Umbral estricto (75%)
        logger.info("[YOLO OBLIGATORIO] YOLO validó detección, procesando con OpenCV...")
        
        return _remove_background_opencv(image_path)
    except SegmentationError:
        # Propagar SegmentationError inmediatamente (detección temprana de "no hay grano")
        raise
    except Exception as e_opencv:
        logger.error(f"OpenCV directo falló para {filename}: {e_opencv}")
        raise FileNotFoundError(f"No se pudo procesar la imagen {filename} con OpenCV: {e_opencv}")


def _process_with_priority_chain(image_path: str, filename: str) -> Image.Image:
    """
    Procesa imagen usando cadena de prioridad: YOLO (obligatorio) -> AI -> rembg -> OpenCV.
    
    YOLO ES OBLIGATORIO: Debe validar antes de cualquier método de segmentación.
    Si YOLO falla, NO se permite continuar con ningún método.
    
    Args:
        image_path: Ruta a la imagen
        filename: Nombre del archivo para logging
        
    Returns:
        Imagen PIL RGBA procesada
        
    Raises:
        SegmentationError: Si YOLO no detecta un grano válido o si ningún método detecta un grano válido
        FileNotFoundError: Si todos los métodos fallan
    """
    # YOLO ES OBLIGATORIO: Validar primero antes de cualquier segmentación
    logger.info("[YOLO OBLIGATORIO] Validando con YOLO antes de segmentación...")
    _validate_with_yolo_fast(image_path, min_confidence=0.75)  # Umbral estricto (75%)
    logger.info("[YOLO OBLIGATORIO] YOLO validó detección, procediendo con segmentación...")
    
    try:
        logger.debug("Prioridad 1: Intentando U-Net (remove_background_ai)...")
        return remove_background_ai(image_path)
    except SegmentationError:
        # Propagar SegmentationError inmediatamente (detección temprana de "no hay grano")
        raise
    except Exception as e_ai:
        logger.warning(f"U-Net (Prioridad 1) falló: {e_ai}. Intentando rembg...")
        return _try_rembg_then_opencv(image_path, filename)


def _try_rembg_then_opencv(image_path: str, filename: str) -> Image.Image:
    """
    Intenta rembg, fallback a OpenCV si falla.
    
    NOTA: YOLO ya fue validado en _process_with_priority_chain, así que OpenCV puede ejecutarse
    solo si YOLO ya confirmó que hay un grano válido.
    
    Args:
        image_path: Ruta a la imagen
        filename: Nombre del archivo para logging
        
    Returns:
        Imagen PIL RGBA procesada
        
    Raises:
        SegmentationError: Si no se detecta un grano válido (propagado inmediatamente)
    """
    try:
        if _HAS_REMBG:
            logger.debug("Prioridad 2: Intentando rembg...")
            return _remove_background_rembg(image_path)
        raise RuntimeError("rembg no disponible, saltando a OpenCV")
    except SegmentationError:
        # Propagar SegmentationError inmediatamente (detección temprana de "no hay grano")
        raise
    except Exception as e_rembg:
        logger.warning(f"rembg (Prioridad 2) falló: {e_rembg}. Usando OpenCV como último recurso...")
        # YOLO ya fue validado, así que OpenCV puede ejecutarse
        return _try_opencv_fallback(image_path, filename)


def _try_opencv_fallback(image_path: str, filename: str) -> Image.Image:
    """
    Intenta OpenCV como último recurso.
    VALIDACIÓN PREVIA: Usa YOLO para validar que hay un grano antes de procesar.
    
    Args:
        image_path: Ruta a la imagen
        filename: Nombre del archivo para logging
        
    Returns:
        Imagen PIL RGBA procesada
        
    Raises:
        SegmentationError: Si YOLO no detecta un grano o si OpenCV no detecta un grano válido
        FileNotFoundError: Si OpenCV falla por otros motivos
    """
    try:
        logger.info("[YOLO OBLIGATORIO] Prioridad 3: Validando con YOLO antes de OpenCV...")
        
        # YOLO ES OBLIGATORIO: Debe validar antes de procesar con OpenCV
        # Si YOLO falla, NO se permite continuar con OpenCV
        _validate_with_yolo_fast(image_path, min_confidence=0.75)  # Umbral estricto (75%)
        logger.info("[YOLO OBLIGATORIO] YOLO validó detección, procesando con OpenCV...")
        
        return _remove_background_opencv(image_path)
    except SegmentationError:
        # Propagar SegmentationError inmediatamente (detección temprana de "no hay grano")
        raise
    except Exception as e_opencv:
        logger.error(f"Todos los métodos de segmentación fallaron para {filename}: {e_opencv}")
        raise FileNotFoundError(f"No se pudo procesar la imagen {filename} con ningún método.")


def segment_and_crop_cacao_bean(image_path: str, method: str = "yolo") -> str:
    """
    Segmenta (elimina fondo) y recorta una imagen de cacao usando YOLO-Seg.
    
    VALIDACIÓN EN DOS ETAPAS:
    1. Clasificador binario (si está disponible): Valida usando imágenes de ejemplo
    2. YOLO-Seg: Validación y segmentación final
    
    YOLO-Seg es OBLIGATORIO: No hay fallbacks. Si YOLO-Seg falla, se lanza SegmentationError.
    
    Migrado a YOLO-Seg para segmentación más precisa y reducción de falsos positivos.

    Args:
        image_path (str): Ruta de la imagen original.
        method (str): Método de segmentación (solo "yolo" es válido, otros valores se ignoran).

    Returns:
        str: Ruta absoluta del archivo PNG generado con fondo transparente.
        
    Raises:
        SegmentationError: Si el clasificador o YOLO-Seg no detecta un grano válido
        FileNotFoundError: Si la imagen no existe
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"La imagen '{image_path}' no existe")

    filename = os.path.basename(image_path)
    logger.info(f"[Validación] Iniciando validación y segmentación para: {filename}")

    # ETAPA 1: Validación con clasificador binario (OBLIGATORIA si está disponible)
    try:
        from ..classification import get_cacao_classifier
        
        classifier = get_cacao_classifier()
        if classifier is not None:
            logger.info(f"[Clasificador] Validando imagen con clasificador binario (OBLIGATORIO)...")
            try:
                is_cacao, confidence, details = classifier.classify(image_path)
                
                # El método classify() ya lanza SegmentationError si no es cacao
                # Si llegamos aquí, la validación pasó
                logger.info(
                    f"[Clasificador] ✅ Validación exitosa: confianza={confidence:.3f}, "
                    f"prob_cacao={details.get('cacao_probability', 0)*100:.1f}%, "
                    f"prob_no_cacao={details.get('not_cacao_probability', 0)*100:.1f}%"
                )
            except SegmentationError as seg_err:
                # El clasificador rechazó la imagen - OBLIGATORIO rechazar
                logger.error(f"[Clasificador] ❌ Imagen rechazada: {seg_err}")
                raise
        else:
            logger.warning(
                "[Clasificador] ⚠️ Clasificador no disponible. "
                "Se recomienda entrenar el clasificador para mejor validación. "
                "Usando solo YOLO..."
            )
    except SegmentationError:
        # Propagar error del clasificador inmediatamente - NO continuar
        raise
    except Exception as e:
        # Si el clasificador falla por otros motivos (error técnico), 
        # OBLIGATORIO rechazar para evitar falsos positivos
        logger.error(
            f"[Clasificador] ❌ Error técnico en clasificación: {e}. "
            "Rechazando imagen por seguridad (evitar falsos positivos)."
        )
        raise SegmentationError(
            f"No se pudo validar la imagen con el clasificador: {str(e)}. "
            "La imagen fue rechazada por seguridad para evitar falsos positivos."
        ) from e

    # ETAPA 2: Validación y segmentación con YOLO-Seg
    try:
        from .cacao_segmentation_model import CacaoSegmentationModel
        
        # Inicializar modelo (se carga lazy, solo una vez)
        if not hasattr(segment_and_crop_cacao_bean, '_seg_model'):
            segment_and_crop_cacao_bean._seg_model = CacaoSegmentationModel(
                confidence_threshold=0.75
            )
        
        seg_model = segment_and_crop_cacao_bean._seg_model
        
        # Segmentar y guardar
        crop_image, output_path = seg_model.segment_and_save(image_path)
        
        logger.info(f"[YOLO-Seg] ✅ Imagen procesada y guardada en: {output_path}")
        return str(output_path)
        
    except SegmentationError:
        # Propagar SegmentationError inmediatamente
        raise
    except Exception as e:
        logger.error(f"[YOLO-Seg] ❌ Error en segmentación: {e}", exc_info=True)
        raise SegmentationError(
            f"No se pudo segmentar la imagen: {str(e)}. "
            "YOLO-Seg es obligatorio y no se permiten fallbacks."
        ) from e


def convert_bmp_to_jpg(bmp_path: Path) -> Tuple[Optional[Image.Image], Dict[str, Any]]:
    """
    Convierte una imagen BMP a JPG (en memoria).
    
    Args:
        bmp_path: Ruta al archivo BMP
        
    Returns:
        Tupla de (imagen JPG o None, diccionario con resultado)
    """
    try:
        img = Image.open(bmp_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Guardar en buffer de bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG', quality=90)
        img_byte_arr.seek(0)
        
        # Recargar desde buffer para asegurar formato JPG
        jpg_img = Image.open(img_byte_arr)
        
        return jpg_img, {"success": True, "format": "JPEG"}
    except Exception as e:
        logger.error(f"Error convirtiendo BMP a JPG: {bmp_path.name}: {e}")
        return None, {"success": False, "error": str(e)}


# ============================================================================
# FUNCIÓN DE DEBUG PARA CALIBRAR UMBRALES
# ============================================================================

def debug_validate_thresholds(
    image_paths: List[str],
    min_confidence: float = 0.75,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Función de debug para calibrar umbrales de validación sobre un conjunto de imágenes de prueba.
    
    Esta función ejecuta las validaciones YOLO y post-segmentación sobre múltiples imágenes
    y retorna métricas detalladas para ajustar los umbrales y reducir falsos negativos.
    
    Args:
        image_paths: Lista de rutas a imágenes de prueba
        min_confidence: Confianza mínima para YOLO (por defecto 0.75 - estricto)
        verbose: Si True, imprime métricas detalladas por imagen
        
    Returns:
        Diccionario con estadísticas agregadas y métricas por imagen
    """
    results = {
        'total_images': len(image_paths),
        'yolo_validations': [],
        'post_segmentation_validations': [],
        'summary': {
            'yolo_passed': 0,
            'yolo_failed': 0,
            'segmentation_passed': 0,
            'segmentation_failed': 0
        }
    }
    
    for image_path in image_paths:
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            logger.warning(f"Imagen no encontrada: {image_path}")
            continue
        
        # Leer dimensiones de la imagen
        from PIL import Image as PILImage
        with PILImage.open(image_path) as img:
            img_width, img_height = img.size
            total_pixels = img_width * img_height
        
        # 1. Validación YOLO
        yolo_result = {
            'image_path': str(image_path),
            'image_size': f"{img_width}x{img_height}",
            'total_pixels': total_pixels,
            'passed': False,
            'error': None,
            'metrics': {}
        }
        
        try:
            if _HAS_YOLO:
                global _yolo_validator
                if _yolo_validator is None:
                    _yolo_validator = create_yolo_inference(confidence_threshold=min_confidence)
                
                results_yolo = _yolo_validator.model(
                    str(image_path),
                    conf=min_confidence,
                    imgsz=320,
                    verbose=False,
                    max_det=1,
                    iou=0.5
                )
                
                predictions = _yolo_validator._process_yolo_results(results_yolo, min_confidence=min_confidence)
                
                if predictions:
                    best_pred = max(predictions, key=lambda p: p['confidence'])
                    bbox = best_pred.get('bbox', [])
                    
                    bbox_width = bbox[2] - bbox[0] if len(bbox) >= 4 else 0
                    bbox_height = bbox[3] - bbox[1] if len(bbox) >= 4 else 0
                    aspect_ratio = bbox_width / bbox_height if bbox_height > 0 else 0
                    object_ratio = best_pred['area'] / total_pixels if total_pixels > 0 else 0
                    
                    yolo_result['metrics'] = {
                        'confidence': best_pred['confidence'],
                        'area': best_pred['area'],
                        'object_ratio': object_ratio,
                        'aspect_ratio': aspect_ratio,
                        'class_name': best_pred.get('class_name', 'unknown'),
                        'bbox_width': bbox_width,
                        'bbox_height': bbox_height
                    }
                    
                    # Intentar validación completa
                    try:
                        _validate_with_yolo_fast(image_path, min_confidence=min_confidence)
                        yolo_result['passed'] = True
                        results['summary']['yolo_passed'] += 1
                    except SegmentationError as e:
                        yolo_result['passed'] = False
                        yolo_result['error'] = str(e)
                        results['summary']['yolo_failed'] += 1
                else:
                    yolo_result['passed'] = False
                    yolo_result['error'] = "YOLO no detectó ningún objeto"
                    results['summary']['yolo_failed'] += 1
            else:
                yolo_result['error'] = "YOLO no disponible"
        except Exception as e:
            yolo_result['passed'] = False
            yolo_result['error'] = str(e)
            results['summary']['yolo_failed'] += 1
        
        results['yolo_validations'].append(yolo_result)
        
        # 2. Validación post-segmentación (simular)
        seg_result = {
            'image_path': str(image_path),
            'passed': False,
            'error': None,
            'metrics': {}
        }
        
        try:
            # Intentar segmentación completa
            segment_and_crop_cacao_bean(image_path, method="ai")
            seg_result['passed'] = True
            results['summary']['segmentation_passed'] += 1
            
            # Si pasó, intentar cargar el crop para obtener métricas
            # (esto requiere acceso al crop generado, simplificado aquí)
            seg_result['metrics'] = {
                'status': 'segmentation_successful',
                'note': 'Crop generado exitosamente'
            }
        except SegmentationError as e:
            seg_result['passed'] = False
            seg_result['error'] = str(e)
            results['summary']['segmentation_failed'] += 1
        except Exception as e:
            seg_result['passed'] = False
            seg_result['error'] = f"Error inesperado: {str(e)}"
            results['summary']['segmentation_failed'] += 1
        
        results['post_segmentation_validations'].append(seg_result)
        
        # Imprimir métricas si verbose
        if verbose:
            print(f"\n{'='*80}")
            print(f"Imagen: {image_path_obj.name}")
            print(f"Tamaño: {img_width}x{img_height} ({total_pixels} píxeles)")
            print(f"\nYOLO Validation:")
            print(f"  Passed: {yolo_result['passed']}")
            if yolo_result['metrics']:
                print(f"  Confidence: {yolo_result['metrics'].get('confidence', 0):.3f}")
                print(f"  Area: {yolo_result['metrics'].get('area', 0)} píxeles")
                print(f"  Object Ratio: {yolo_result['metrics'].get('object_ratio', 0)*100:.2f}%")
                print(f"  Aspect Ratio: {yolo_result['metrics'].get('aspect_ratio', 0):.2f}")
                print(f"  Class: {yolo_result['metrics'].get('class_name', 'unknown')}")
            if yolo_result['error']:
                print(f"  Error: {yolo_result['error']}")
            print(f"\nPost-Segmentation Validation:")
            print(f"  Passed: {seg_result['passed']}")
            if seg_result['error']:
                print(f"  Error: {seg_result['error']}")
    
    # Resumen final
    if verbose:
        print(f"\n{'='*80}")
        print("RESUMEN:")
        print(f"Total imágenes: {results['total_images']}")
        print(f"YOLO: {results['summary']['yolo_passed']} pasaron, {results['summary']['yolo_failed']} fallaron")
        print(f"Segmentación: {results['summary']['segmentation_passed']} pasaron, {results['summary']['segmentation_failed']} fallaron")
        print(f"{'='*80}\n")
    
    return results