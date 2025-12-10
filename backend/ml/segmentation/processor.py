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
from typing import Tuple, Optional, Dict, Any
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

logger = get_ml_logger("cacaoscan.ml.segmentation.processor")


class SegmentationError(Exception):
    """Excepción personalizada para errores de segmentación."""
    pass


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

    # 3) Mantener solo el mayor contorno
    cnts, _ = cv2.findContours(bin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if cnts:
        largest = max(cnts, key=cv2.contourArea)
        clean = np.zeros_like(bin_mask)
        cv2.drawContours(clean, [largest], -1, 255, thickness=cv2.FILLED)
        hull = cv2.convexHull(largest)
        hull_mask = np.zeros_like(bin_mask)
        cv2.drawContours(hull_mask, [hull], -1, 255, thickness=cv2.FILLED)
        clean = cv2.bitwise_and(clean, hull_mask)
    else:
        clean = bin_mask

    # 4) Feather del borde para alpha suave
    edge = cv2.Canny(clean, 50, 150)
    feather = cv2.GaussianBlur(edge, (21, 21), 0)
    alpha = np.clip(clean.astype(np.float32) + feather.astype(np.float32), 0, 255).astype(np.uint8)
    alpha = _deshadow_alpha(rgb, alpha)
    alpha = _guided_refine(rgb, alpha)

    # 5) Recorte tight con padding
    ys, xs = np.nonzero(alpha > 0)
    if len(xs) == 0 or len(ys) == 0:
        rgba = np.dstack([rgb, clean])
        return Image.fromarray(rgba, "RGBA")

    x1, x2 = xs.min(), xs.max()
    y1, y2 = ys.min(), ys.max()
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
    
    Args:
        image_path: Ruta a la imagen
        filename: Nombre del archivo para logging
        
    Returns:
        Imagen PIL RGBA procesada
        
    Raises:
        FileNotFoundError: Si no se puede procesar la imagen
    """
    logger.debug("Segmentación solicitada con backend OpenCV (modo directo)")
    try:
        return _remove_background_opencv(image_path)
    except Exception as e_opencv:
        logger.error(f"OpenCV directo falló para {filename}: {e_opencv}")
        raise FileNotFoundError(f"No se pudo procesar la imagen {filename} con OpenCV: {e_opencv}")


def _process_with_priority_chain(image_path: str, filename: str) -> Image.Image:
    """
    Procesa imagen usando cadena de prioridad: AI -> rembg -> OpenCV.
    
    Args:
        image_path: Ruta a la imagen
        filename: Nombre del archivo para logging
        
    Returns:
        Imagen PIL RGBA procesada
        
    Raises:
        FileNotFoundError: Si todos los métodos fallan
    """
    try:
        logger.debug("Prioridad 1: Intentando U-Net (remove_background_ai)...")
        return remove_background_ai(image_path)
    except Exception as e_ai:
        logger.warning(f"U-Net (Prioridad 1) falló: {e_ai}. Intentando rembg...")
        return _try_rembg_then_opencv(image_path, filename)


def _try_rembg_then_opencv(image_path: str, filename: str) -> Image.Image:
    """
    Intenta rembg, fallback a OpenCV si falla.
    
    Args:
        image_path: Ruta a la imagen
        filename: Nombre del archivo para logging
        
    Returns:
        Imagen PIL RGBA procesada
    """
    try:
        if _HAS_REMBG:
            logger.debug("Prioridad 2: Intentando rembg...")
            return _remove_background_rembg(image_path)
        raise RuntimeError("rembg no disponible, saltando a OpenCV")
    except Exception as e_rembg:
        logger.warning(f"rembg (Prioridad 2) falló: {e_rembg}. Usando OpenCV como último recurso...")
        return _try_opencv_fallback(image_path, filename)


def _try_opencv_fallback(image_path: str, filename: str) -> Image.Image:
    """
    Intenta OpenCV como último recurso.
    
    Args:
        image_path: Ruta a la imagen
        filename: Nombre del archivo para logging
        
    Returns:
        Imagen PIL RGBA procesada
        
    Raises:
        FileNotFoundError: Si OpenCV también falla
    """
    try:
        logger.debug("Prioridad 3: Intentando OpenCV...")
        return _remove_background_opencv(image_path)
    except Exception as e_opencv:
        logger.error(f"Todos los métodos de segmentación fallaron para {filename}: {e_opencv}")
        raise FileNotFoundError(f"No se pudo procesar la imagen {filename} con ningún método.")


def segment_and_crop_cacao_bean(image_path: str, method: str = "ai") -> str:
    """
    Segmenta (elimina fondo) y recorta una imagen de cacao.
    
    PRIORIDAD RESTAURADA: 1. U-Net (ai), 2. rembg, 3. OpenCV

    Args:
        image_path (str): Ruta de la imagen original.
        method (str): Método de segmentación ("ai", "opencv", "yolo").

    Returns:
        str: Ruta absoluta del archivo PNG generado con fondo transparente.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"La imagen '{image_path}' no existe")

    filename = os.path.basename(image_path)
    logger.info(f"Iniciando eliminación de fondo para: {filename}")

    method = (method or "ai").lower()
    if method == "opencv":
        processed = _process_with_opencv(image_path, filename)
    else:
        processed = _process_with_priority_chain(image_path, filename)
    
    output_filename = f"cacao_{uuid.uuid4().hex}.png"
    out_path = save_processed_png(processed, output_filename)

    logger.info(f"[OK] Imagen procesada y guardada en: {out_path}")
    return str(out_path)


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