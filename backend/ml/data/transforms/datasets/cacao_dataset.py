"""
Dataset para entrenamiento de segmentación con generación automática de máscaras.

Este módulo maneja la carga de datos para entrenamiento,
siguiendo el principio de Responsabilidad Única.
"""
import os
import cv2
import numpy as np
from typing import Optional
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms as T

from ....utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.data.transforms.datasets")


class CacaoDataset(Dataset):
    """
    Dataset para entrenamiento de segmentación con generación automática de máscaras.
    
    Esta clase es responsable de:
    - Cargar imágenes y máscaras
    - Generar máscaras automáticamente si faltan
    - Aplicar transformaciones
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    def __init__(
        self,
        img_dir: str,
        mask_dir: str,
        transform: Optional[T.Compose] = None,
        auto_generate: bool = False
    ):
        """
        Inicializa dataset de segmentación.
        
        Args:
            img_dir: Directorio con imágenes
            mask_dir: Directorio con máscaras
            transform: Transformaciones de imagen
            auto_generate: Si es True, genera máscaras automáticamente si faltan
        """
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
                    logger.info(f"Máscara creada: {mask_path}")

    def _auto_mask(self, image_path: str) -> np.ndarray:
        """
        Usa OpenCV (grabCut) para generar máscara base automáticamente.
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            Máscara generada
        """
        img = cv2.imread(image_path)
        mask = np.zeros(img.shape[:2], np.uint8)
        rect = (10, 10, img.shape[1]-20, img.shape[0]-20)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        cv2.grabCut(img, mask, rect, bgd_model, fgd_model, 10, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8') * 255
        return mask2

    def __len__(self) -> int:
        """
        Retorna el tamaño del dataset.
        
        Returns:
            Número de imágenes
        """
        return len(self.images)

    def __getitem__(self, idx: int) -> tuple:
        """
        Obtiene un elemento del dataset.
        
        Args:
            idx: Índice del elemento
            
        Returns:
            Tupla (imagen, máscara)
        """
        img_path = os.path.join(self.img_dir, self.images[idx])
        mask_path = os.path.join(self.mask_dir, self.images[idx].replace(".jpg", ".png"))
        image = Image.open(img_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")

        if self.transform:
            image = self.transform(image)
            mask = self.transform(mask)

        return image, mask

