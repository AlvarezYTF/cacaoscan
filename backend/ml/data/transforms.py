import os
import cv2
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms as T
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from typing import Tuple

# Error message constants
ERROR_IMAGE_CANNOT_BE_NONE = "image cannot be None"

# ======================================================
#  MODELO: U-Net ligero para segmentacion de fondo
# ======================================================
class DoubleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, 3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.conv(x)

class UNet(nn.Module):
    def __init__(self, n_channels=3, n_classes=1):
        super().__init__()
        self.down1 = DoubleConv(n_channels, 64)
        self.pool1 = nn.MaxPool2d(2)
        self.down2 = DoubleConv(64, 128)
        self.pool2 = nn.MaxPool2d(2)
        self.bottom = DoubleConv(128, 256)
        self.up1 = nn.ConvTranspose2d(256, 128, 2, stride=2)
        self.conv1 = DoubleConv(256, 128)
        self.up2 = nn.ConvTranspose2d(128, 64, 2, stride=2)
        self.conv2 = DoubleConv(128, 64)
        self.final = nn.Conv2d(64, n_classes, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x1 = self.down1(x)
        x2 = self.pool1(x1)
        x3 = self.down2(x2)
        x4 = self.pool2(x3)
        x5 = self.bottom(x4)
        x = self.up1(x5)
        x = torch.cat([x, x3], dim=1)
        x = self.conv1(x)
        x = self.up2(x)
        x = torch.cat([x, x1], dim=1)
        x = self.conv2(x)
        x = self.final(x)
        return self.sigmoid(x)


# ======================================================
#  DATASET AUTOMATICO (crea mascaras si no existen)
# ======================================================
class CacaoDataset(Dataset):
    def __init__(self, img_dir, mask_dir, transform=None, auto_generate=False):
        self.img_dir = img_dir
        self.mask_dir = mask_dir
        self.transform = transform
        self.images = os.listdir(img_dir)
        self.auto_generate = auto_generate

        if auto_generate:
            os.makedirs(mask_dir, exist_ok=True)
            for img in self.images:
                mask_path = os.path.join(mask_dir, img.replace(".jpg", ".png"))
                if not os.path.exists(mask_path):
                    mask = self._auto_mask(os.path.join(img_dir, img))
                    cv2.imwrite(mask_path, mask)
                    print(f" Mascara creada: {mask_path}")

    def _auto_mask(self, image_path):
        """Usa OpenCV (grabCut) para generar mascara base automatica."""
        img = cv2.imread(image_path)
        mask = np.zeros(img.shape[:2], np.uint8)
        rect = (10, 10, img.shape[1]-20, img.shape[0]-20)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 10, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8') * 255
        return mask2

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = os.path.join(self.img_dir, self.images[idx])
        mask_path = os.path.join(self.mask_dir, self.images[idx].replace(".jpg", ".png"))
        image = Image.open(img_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")

        if self.transform:
            image = self.transform(image)
            mask = self.transform(mask)

        return image, mask


# ======================================================
#  ENTRENAMIENTO DEL MODELO
# ======================================================
def train_background_ai(image_dir="ml/data/dataset/images", mask_dir="ml/data/dataset/masks", epochs=10):
    transform = T.Compose([
        T.Resize((256, 256)),
        T.ToTensor(),
    ])

    dataset = CacaoDataset(image_dir, mask_dir, transform, auto_generate=True)
    loader = DataLoader(dataset, batch_size=4, shuffle=True, num_workers=0)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = UNet().to(device)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4, weight_decay=1e-4)

    for epoch in range(epochs):
        for imgs, masks in loader:
            imgs, masks = imgs.to(device), masks.to(device)
            preds = model(imgs)
            loss = criterion(preds, masks)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch+1}/{epochs} | Loss: {loss.item():.4f}")

    os.makedirs("ml/segmentation", exist_ok=True)
    torch.save(model.state_dict(), "ml/segmentation/cacao_unet.pth")
    print(" Modelo entrenado y guardado en ml/segmentation/cacao_unet.pth")


# ======================================================
#  USO DEL MODELO PARA QUITAR FONDO
# ======================================================
def remove_background_ai(image_path: str) -> Image.Image:
    """
    Quita el fondo usando el modelo IA entrenado (U-Net) con refinamiento OpenCV.
    Elimina bordes blancos, recorta tight el grano y detecta cada pixel del cacao con precision.
    """
    model_path = "ml/segmentation/cacao_unet.pth"
    if not os.path.exists(model_path):
        raise FileNotFoundError("[ERROR] No se encontr el modelo entrenado. Ejecuta train_background_ai() primero.")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = UNet().to(device)
    # S6985: Use weights_only=True to prevent arbitrary code execution from untrusted model files.
    # This ensures only model weights are loaded, not arbitrary Python objects or code.
    model.load_state_dict(torch.load(model_path, map_location=device, weights_only=True))
    model.eval()

    # Cargar imagen original
    img = Image.open(image_path).convert("RGB")
    img_array = np.array(img)
    h, w = img_array.shape[:2]
    original_size = (w, h)  # (ancho, alto)
    
    # Preprocesar para el modelo
    transform = T.Compose([
        T.Resize((256, 256)),
        T.ToTensor()
    ])
    tensor = transform(img).unsqueeze(0).to(device)

    # Obtener mscara del modelo U-Net
    with torch.no_grad():
        mask_pred = model(tensor)[0][0].cpu().numpy()

    # Normalizar mscara
    mask_pred = (mask_pred - mask_pred.min()) / (mask_pred.max() - mask_pred.min() + 1e-8)
    
    # Redimensionar mscara al tamao original
    mask = cv2.resize(mask_pred, original_size, interpolation=cv2.INTER_LINEAR)
    mask = (mask * 255).astype(np.uint8)
    
    # REFINAMIENTO PRECISO CON OPENCV
    mask_refined = _refine_mask_opencv_precise(img_array, mask)
    
    # Importar funciones de refinamiento de processor.py
    from ml.segmentation.processor import _deshadow_alpha, _guided_refine, _clean_components
    
    # Aplicar refinamiento adicional (igual que OpenCV)
    alpha = _deshadow_alpha(img_array, mask_refined)
    alpha = _guided_refine(img_array, alpha)
    
    # Limpiar componentes (solo el más grande)
    alpha = _clean_components(alpha)
    
    # RECORTE TIGHT: encontrar bounding box del grano
    ys, xs = np.nonzero(alpha > 0)
    if len(xs) == 0 or len(ys) == 0:
        # Si no hay píxeles válidos, devolver imagen completa con máscara
        rgba = np.dstack([img_array, alpha])
        return Image.fromarray(rgba, "RGBA")
    
    x1, x2 = xs.min(), xs.max()
    y1, y2 = ys.min(), ys.max()
    
    # Padding mínimo (8% del tamaño o mínimo 10px)
    pad_x = max(10, int(0.08 * (x2 - x1 + 1)))
    pad_y = max(10, int(0.08 * (y2 - y1 + 1)))
    
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w - 1, x2 + pad_x)
    y2 = min(h - 1, y2 + pad_y)
    
    # Recortar región del grano
    crop_rgb = img_array[y1:y2 + 1, x1:x2 + 1]
    crop_alpha = alpha[y1:y2 + 1, x1:x2 + 1]
    
    # Refinar máscara en el crop (más preciso)
    crop_alpha = _deshadow_alpha(crop_rgb, crop_alpha)
    crop_alpha = _guided_refine(crop_rgb, crop_alpha)
    
    # Eliminar píxeles blancos residuales en el crop
    gray_crop = cv2.cvtColor(crop_rgb, cv2.COLOR_RGB2GRAY)
    white_threshold = 220
    is_white = gray_crop > white_threshold
    
    # Eliminar píxeles blancos que están en el borde de la máscara
    kernel = np.ones((5, 5), np.uint8)
    alpha_dilated = cv2.dilate(crop_alpha, kernel, iterations=1)
    border_region = (alpha_dilated > 0) & (crop_alpha == 0)
    
    # Eliminar píxeles blancos en el borde
    crop_alpha = np.where(border_region & is_white, 0, crop_alpha).astype(np.uint8)
    
    # También eliminar píxeles blancos dentro del objeto si están muy cerca del borde
    dist_to_edge = cv2.distanceTransform((crop_alpha > 0).astype(np.uint8), cv2.DIST_L2, 5)
    edge_region = dist_to_edge < 15  # 15 píxeles del borde
    crop_alpha = np.where(edge_region & is_white & (crop_alpha > 0), 0, crop_alpha).astype(np.uint8)
    
    # Limpieza final
    crop_alpha = _clean_components(crop_alpha)
    
    # Crear imagen RGBA recortada
    rgba = np.dstack([crop_rgb, crop_alpha])
    
    return Image.fromarray(rgba, "RGBA")


def _refine_mask_opencv_precise(rgb: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Refina la mscara usando OpenCV para deteccin precisa de pxeles del cacao.
    Elimina bordes blancos residuales y ajusta pixel por pixel.
    
    Args:
        rgb: Imagen RGB original (H, W, 3)
        mask: Mscara inicial del modelo (H, W) valores 0-255
        
    Returns:
        Mscara refinada (H, W) valores 0-255
    """
    h, w = mask.shape
    
    # 1. Convertir mscara a binaria
    _, mask_binary = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    
    # 2. Eliminar ruido inicial
    kernel_small = np.ones((3, 3), np.uint8)
    mask_clean = cv2.morphologyEx(mask_binary, cv2.MORPH_OPEN, kernel_small, iterations=1)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_CLOSE, kernel_small, iterations=1)
    
    # 3. Detectar y eliminar bordes blancos
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    
    # Identificar pxeles blancos/claros (fondo residual)
    white_threshold = 220
    is_white = gray > white_threshold
    
    # Dilatar mscara para encontrar rea cercana al borde
    kernel_dilate = np.ones((3, 3), np.uint8)
    mask_dilated = cv2.dilate(mask_clean, kernel_dilate, iterations=1)
    border_region = mask_dilated.astype(bool) & ~(mask_clean.astype(bool))
    
    # Eliminar pxeles blancos en la regin del borde
    mask_clean = np.where(border_region & is_white, 0, mask_clean).astype(np.uint8)
    
    # 4. Erosionar ligeramente para eliminar bordes residuales blancos
    kernel_erode = np.ones((3, 3), np.uint8)
    mask_clean = cv2.erode(mask_clean, kernel_erode, iterations=1)
    
    # Eliminar reas blancas dentro del objeto erosionado
    mask_eroded_white = np.where(is_white & (mask_clean > 128), 0, mask_clean).astype(np.uint8)
    
    # 5. Operaciones morfolgicas MINIMALISTAS para evitar halos
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask_clean = cv2.morphologyEx(mask_eroded_white, cv2.MORPH_CLOSE, kernel, iterations=1)
    mask_clean = cv2.morphologyEx(mask_clean, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # 6. Detectar contorno ms grande (el grano de cacao)
    contours, _ = cv2.findContours(mask_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Encontrar el contorno ms grande
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Crear mscara solo del contorno ms grande
        mask_final = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(mask_final, [largest_contour], -1, 255, thickness=-1)
        
        # 7. Usar GrabCut para refinar an ms (mejora precisin pixel por pixel)
        try:
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            
            # Preparar mscara para GrabCut
            gc_mask = np.where(mask_final > 128, cv2.GC_PR_FGD, cv2.GC_PR_BGD).astype(np.uint8)
            
            # Aplicar GrabCut
            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)
            cv2.grabCut(bgr, gc_mask, None, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_MASK)
            
            # Crear mscara final de GrabCut
            mask_grabcut = np.where((gc_mask == cv2.GC_FGD) | (gc_mask == cv2.GC_PR_FGD), 255, 0).astype(np.uint8)
            
            # Combinar: usar GrabCut pero mantener solo el rea del contorno ms grande
            mask_final = cv2.bitwise_and(mask_grabcut, mask_final)
            
        except Exception:
            # Si GrabCut falla, usar solo el contorno
            pass
        
        # 8. Eliminar pequeos artefactos (componentes conectados pequeos)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask_final, connectivity=8)
        if num_labels > 1:
            # Mantener solo el componente ms grande (el grano)
            largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
            mask_final = (labels == largest_label).astype(np.uint8) * 255
        
        # 9. NO suavizar - mantener bordes precisos sin halos
        # mask_final ya est listo
        
    else:
        # Si no hay contornos, usar mscara limpia
        mask_final = mask_clean
    
    return mask_final


def resize_crop_to_square(
    image_rgba: np.ndarray,
    target_size: int = 512,
    fill_color: tuple[int, int, int, int] = (0, 0, 0, 0),
) -> np.ndarray:
    """
    Redimensiona una imagen RGBA manteniendo proporcin y la centra
    en un lienzo cuadrado target_size x target_size con fill_color.
    """
    if image_rgba is None:
        raise ValueError("image_rgba cannot be None")

    h, w = image_rgba.shape[:2]
    scale = min(target_size / w, target_size / h)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    resized = cv2.resize(image_rgba, (new_w, new_h), interpolation=cv2.INTER_AREA)

    canvas = np.zeros((target_size, target_size, 4), dtype=np.uint8)
    canvas[:, :, 0] = fill_color[0]
    canvas[:, :, 1] = fill_color[1]
    canvas[:, :, 2] = fill_color[2]
    canvas[:, :, 3] = fill_color[3]

    y_off = (target_size - new_h) // 2
    x_off = (target_size - new_w) // 2
    canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized
    return canvas


def resize_with_padding(
    image: np.ndarray,
    target_size: tuple[int, int] = (640, 640),
    fill_color: tuple[int, int, int] = (0, 0, 0),
) -> np.ndarray:
    """
    Redimensiona manteniendo proporcin y rellena hasta target_size (alto, ancho).
    Acepta imagen GRAY/RGB/RGBA.
    """
    if image is None:
        raise ValueError(ERROR_IMAGE_CANNOT_BE_NONE)

    h, w = image.shape[:2]
    th, tw = target_size
    scale = min(th / h, tw / w)
    new_h, new_w = int(round(h * scale)), int(round(w * scale))
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)

    if image.ndim == 2:
        canvas = np.full((th, tw), fill_color[0], dtype=resized.dtype)
        y0 = (th - new_h) // 2
        x0 = (tw - new_w) // 2
        canvas[y0:y0+new_h, x0:x0+new_w] = resized
        return canvas

    c = image.shape[2]
    if c == 3:
        canvas = np.zeros((th, tw, 3), dtype=resized.dtype)
        canvas[:, :, 0] = fill_color[0]
        canvas[:, :, 1] = fill_color[1]
        canvas[:, :, 2] = fill_color[2]
    else:
        # RGBA
        canvas = np.zeros((th, tw, 4), dtype=resized.dtype)
        canvas[:, :, 0] = fill_color[0]
        canvas[:, :, 1] = fill_color[1]
        canvas[:, :, 2] = fill_color[2]
        canvas[:, :, 3] = fill_color[3] if len(fill_color) == 4 else 0

    y0 = (th - new_h) // 2
    x0 = (tw - new_w) // 2
    canvas[y0:y0+new_h, x0:x0+new_w] = resized
    return canvas


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normaliza una imagen a rango [0, 1] en float32."""
    if image is None:
        raise ValueError(ERROR_IMAGE_CANNOT_BE_NONE)
    img = image.astype(np.float32)
    if img.max() > 1.0:
        img = img / 255.0
    return img


def denormalize_image(image: np.ndarray) -> np.ndarray:
    """Desnormaliza una imagen de [0, 1] a uint8 [0, 255]."""
    if image is None:
        raise ValueError(ERROR_IMAGE_CANNOT_BE_NONE)
    img = np.clip(image, 0.0, 1.0)
    return (img * 255.0).astype(np.uint8)


def validate_crop_quality(image_rgb: np.ndarray, mask: np.ndarray, min_aspect_ratio: float = 0.1, max_aspect_ratio: float = 10.0, min_area: int = 100) -> bool:
    """
    Valida que el recorte tenga proporciones razonables.
    
    Args:
        image_rgb: Imagen RGB (H, W, 3)
        mask: Mscara binaria (H, W) con valores 0-255
        min_aspect_ratio: Ratio mnimo permitido (ancho/alto) - ms permisivo para granos variados
        max_aspect_ratio: Ratio mximo permitido (ancho/alto) - ms permisivo para granos variados
        min_area: rea mnima en pxeles del objeto detectado
        
    Returns:
        True si el recorte es válido, False en caso contrario
    """
    if image_rgb is None or mask is None:
        return False
    
    # Convertir mscara a binaria si es necesario
    if mask.dtype != np.uint8 or mask.max() > 1:
        mask_binary = (mask > 128).astype(np.uint8)
    else:
        mask_binary = mask
    
    # Encontrar bounding box del objeto
    contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return False
    
    # Usar el contorno ms grande
    largest_contour = max(contours, key=cv2.contourArea)
    _, _, w, h = cv2.boundingRect(largest_contour)
    
    # Validar que el recorte tenga un rea mnima (ms flexible)
    area = w * h
    if area < min_area:
        return False
    
    # Validar dimensiones mnimas (ms flexible)
    if w < 5 or h < 5:
        return False
    
    # Calcular aspect ratio
    aspect_ratio = w / h if h > 0 else 0
    
    # Validar aspect ratio con rangos ms permisivos para granos de cacao
    # Los granos pueden ser redondos (ratio ~1.0) o ms alargados
    if aspect_ratio < min_aspect_ratio or aspect_ratio > max_aspect_ratio:
        # Log para debug (opcional, solo si hay problemas)
        return False
    
    return True


def create_transparent_crop(image_rgb: np.ndarray, mask: np.ndarray, padding: int = 10, crop_only: bool = False) -> np.ndarray:
    """
    Elimina TODO el fondo y deja solo el grano de cacao con bordes suaves y fondo 100% transparente.
    Usa refinamiento OpenCV para detectar cada pxel del cacao con precisin y eliminar bordes blancos.
    """
    if image_rgb is None or mask is None:
        raise ValueError("image_rgb y mask no pueden ser None")

    mask = _align_mask_to_image(mask, image_rgb)
    mask_refined = _refine_mask_opencv_precise(image_rgb, mask)
    contours, _ = cv2.findContours(mask_refined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return np.dstack([image_rgb, mask_refined])

    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = _compute_padded_bbox(largest_contour, padding, image_rgb.shape)
    final_mask = _render_primary_mask(mask_refined, largest_contour)
    
    if not crop_only:
        return _create_refined_rgba(image_rgb, final_mask, x, y, w, h)
    
    adjusted_bbox = _validate_and_adjust_crop_bbox(
        image_rgb=image_rgb,
        final_mask=final_mask,
        bbox=(x, y, w, h),
        padding=padding
    )
    x_adj, y_adj, w_adj, h_adj = adjusted_bbox
    return _create_rgba_from_crop(image_rgb, final_mask, x_adj, y_adj, w_adj, h_adj)


def _align_mask_to_image(mask: np.ndarray, image_rgb: np.ndarray) -> np.ndarray:
    """Resize and normalize mask values to align with the image shape."""
    if mask.shape[:2] != image_rgb.shape[:2]:
        mask = cv2.resize(mask, (image_rgb.shape[1], image_rgb.shape[0]), interpolation=cv2.INTER_LINEAR)
    if mask.max() <= 1.0:
        return (mask * 255).astype(np.uint8)
    return np.clip(mask, 0, 255).astype(np.uint8)


def _compute_padded_bbox(contour: np.ndarray, padding: int, image_shape: Tuple[int, int, int]) -> Tuple[int, int, int, int]:
    """Compute the padded bounding box for the main contour."""
    x, y, w, h = cv2.boundingRect(contour)
    height, width = image_shape[:2]
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(width - x, w + 2 * padding)
    h = min(height - y, h + 2 * padding)
    return x, y, w, h


def _render_primary_mask(mask_refined: np.ndarray, contour: np.ndarray) -> np.ndarray:
    """Render a filled mask for the selected contour."""
    final_mask = np.zeros(mask_refined.shape, dtype=np.uint8)
    cv2.drawContours(final_mask, [contour], -1, 255, thickness=-1)
    return final_mask


def _create_refined_rgba(
    image_rgb: np.ndarray,
    final_mask: np.ndarray,
    x: int,
    y: int,
    w: int,
    h: int
) -> np.ndarray:
    """Generate RGBA crop with additional refinement."""
    region_rgb = image_rgb[y:y+h, x:x+w].copy()
    region_mask = final_mask[y:y+h, x:x+w].copy()
    region_mask_refined = _refine_mask_opencv_precise(region_rgb, region_mask)
    return _stack_rgba(region_rgb, region_mask_refined)


def _validate_and_adjust_crop_bbox(
    *,
    image_rgb: np.ndarray,
    final_mask: np.ndarray,
    bbox: Tuple[int, int, int, int],
    padding: int
) -> Tuple[int, int, int, int]:
    """Validate crop ratios and adjust the bounding box if needed."""
    _, _, w, h = bbox
    original_area = image_rgb.shape[0] * image_rgb.shape[1]
    crop_area = w * h
    if crop_area <= 0:
        return bbox
    
    crop_ratio = crop_area / original_area
    if crop_ratio <= 0.80:
        return bbox
    
    object_area = np.sum(final_mask > 128)
    object_ratio = object_area / original_area
    if object_ratio > 0.80:
        raise ValueError(
            f"El objeto detectado ocupa ms del 80% de la imagen ({object_ratio:.1%}). "
            f"Esto sugiere que no se detect correctamente el grano o la segmentacin fall. "
            f"rea objeto: {object_area}px, rea imagen: {original_area}px"
        )
    
    coords = np.nonzero(final_mask > 128)
    if coords[0].size == 0:
        return bbox
    
    y_min, y_max = coords[0].min(), coords[0].max()
    x_min, x_max = coords[1].min(), coords[1].max()
    width = image_rgb.shape[1]
    height = image_rgb.shape[0]
    x_new = max(0, x_min - padding)
    y_new = max(0, y_min - padding)
    w_new = min(width - x_new, (x_max - x_min) + 2 * padding)
    h_new = min(height - y_new, (y_max - y_min) + 2 * padding)
    return x_new, y_new, w_new, h_new


def _create_rgba_from_crop(
    image_rgb: np.ndarray,
    final_mask: np.ndarray,
    x: int,
    y: int,
    w: int,
    h: int
) -> np.ndarray:
    """Build RGBA tensor from the adjusted crop."""
    crop_rgb = image_rgb[y:y+h, x:x+w].copy()
    crop_alpha = final_mask[y:y+h, x:x+w].copy()
    return _stack_rgba(crop_rgb, crop_alpha)


def _stack_rgba(rgb: np.ndarray, alpha: np.ndarray) -> np.ndarray:
    """Stack RGB data with an alpha channel."""
    rgba = np.zeros((rgb.shape[0], rgb.shape[1], 4), dtype=np.uint8)
    rgba[:, :, :3] = rgb
    rgba[:, :, 3] = alpha
    return rgba
