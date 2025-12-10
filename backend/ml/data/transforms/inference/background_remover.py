"""
Removedor de fondo usando modelos de IA entrenados.

Este módulo maneja la inferencia para remoción de fondo,
siguiendo el principio de Responsabilidad Única.
"""
import os
import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms as T

from ....utils.logs import get_ml_logger
from ..models import UNet
from ..mask_refinement import refine_mask_opencv_precise

logger = get_ml_logger("cacaoscan.ml.data.transforms.inference")


class BackgroundRemover:
    """
    Removedor de fondo usando modelo de IA entrenado (U-Net) con refinamiento OpenCV.
    
    Esta clase es responsable de:
    - Cargar modelo entrenado
    - Generar máscaras de segmentación
    - Refinar máscaras con OpenCV
    - Remover fondo y recortar grano
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    def __init__(
        self,
        model_path: str = "ml/segmentation/cacao_unet.pth"
    ):
        """
        Inicializa el removedor de fondo.
        
        Args:
            model_path: Ruta al modelo entrenado
        """
        self.model_path = model_path
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model: UNet | None = None
        
        logger.info(f"BackgroundRemover inicializado (device={self.device})")
    
    def _load_model(self) -> None:
        """
        Carga el modelo entrenado.
        
        Raises:
            FileNotFoundError: Si el modelo no existe
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"[ERROR] Modelo entrenado no encontrado: {self.model_path}. "
                f"Ejecuta train_background_ai() primero."
            )
        
        if self.model is None:
            self.model = UNet().to(self.device)
            self.model.load_state_dict(
                torch.load(self.model_path, map_location=self.device, weights_only=True)
            )
            self.model.eval()
            logger.info(f"Modelo cargado desde {self.model_path}")
    
    def remove_background(self, image_path: str) -> Image.Image:
        """
        Remueve fondo usando modelo de IA entrenado (U-Net) con refinamiento OpenCV.
        Remueve bordes blancos, recorta el grano ajustadamente y detecta cada píxel de cacao precisamente.
        
        Args:
            image_path: Ruta a la imagen de entrada
            
        Returns:
            Imagen RGBA con fondo transparente
        """
        self._load_model()
        
        # Cargar imagen original
        img = Image.open(image_path).convert("RGB")
        img_array = np.array(img)
        h, w = img_array.shape[:2]
        original_size = (w, h)  # (width, height)
        
        # Preprocesar para el modelo
        transform = T.Compose([
            T.Resize((256, 256)),
            T.ToTensor()
        ])
        tensor = transform(img).unsqueeze(0).to(self.device)

        # Obtener máscara del modelo U-Net
        with torch.no_grad():
            mask_pred = self.model(tensor)[0][0].cpu().numpy()

        # Normalizar máscara
        mask_pred = (mask_pred - mask_pred.min()) / (mask_pred.max() - mask_pred.min() + 1e-8)
        
        # Redimensionar máscara al tamaño original
        mask = cv2.resize(mask_pred, original_size, interpolation=cv2.INTER_LINEAR)
        mask = (mask * 255).astype(np.uint8)
        
        # REFINAMIENTO PRECISO CON OPENCV
        mask_refined = refine_mask_opencv_precise(img_array, mask)
        
        # Importar funciones de refinamiento del procesador
        from ...segmentation.processor import _deshadow_alpha, _guided_refine, _clean_components
        
        # Aplicar refinamiento adicional (igual que OpenCV)
        alpha = _deshadow_alpha(img_array, mask_refined)
        alpha = _guided_refine(img_array, alpha)
        
        # Limpiar componentes (solo el más grande)
        alpha = _clean_components(alpha)
        
        # RECORTE AJUSTADO: encontrar bounding box del grano
        ys, xs = np.nonzero(alpha > 0)
        if len(xs) == 0 or len(ys) == 0:
            # Si no hay píxeles válidos, retornar imagen completa con máscara
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
        
        # Refinar máscara en el recorte (más preciso)
        crop_alpha = _deshadow_alpha(crop_rgb, crop_alpha)
        crop_alpha = _guided_refine(crop_rgb, crop_alpha)
        
        # Remover píxeles blancos residuales en el recorte
        gray_crop = cv2.cvtColor(crop_rgb, cv2.COLOR_RGB2GRAY)
        white_threshold = 220
        is_white = gray_crop > white_threshold
        
        # Remover píxeles blancos en el borde de la máscara
        kernel = np.ones((5, 5), np.uint8)
        alpha_dilated = cv2.dilate(crop_alpha, kernel, iterations=1)
        border_region = (alpha_dilated > 0) & (crop_alpha == 0)
        
        # Remover píxeles blancos en el borde
        crop_alpha = np.where(border_region & is_white, 0, crop_alpha).astype(np.uint8)
        
        # También remover píxeles blancos dentro del objeto si están muy cerca del borde
        dist_to_edge = cv2.distanceTransform(
            (crop_alpha > 0).astype(np.uint8), cv2.DIST_L2, 5
        )
        edge_region = dist_to_edge < 15  # 15 píxeles del borde
        crop_alpha = np.where(
            edge_region & is_white & (crop_alpha > 0), 0, crop_alpha
        ).astype(np.uint8)
        
        # Limpieza final
        crop_alpha = _clean_components(crop_alpha)
        
        # Crear imagen RGBA recortada
        rgba = np.dstack([crop_rgb, crop_alpha])
        
        return Image.fromarray(rgba, "RGBA")


def remove_background_ai(image_path: str) -> Image.Image:
    """
    Función de conveniencia para remover fondo.
    
    Args:
        image_path: Ruta a la imagen de entrada
        
    Returns:
        Imagen RGBA con fondo transparente
    """
    remover = BackgroundRemover()
    return remover.remove_background(image_path)

