"""
Entrenador para modelos de segmentación de fondo.

Este módulo maneja el entrenamiento de modelos U-Net,
siguiendo el principio de Responsabilidad Única.
"""
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms as T

from ....utils.logs import get_ml_logger
from ..models import UNet
from ..datasets import CacaoDataset

logger = get_ml_logger("cacaoscan.ml.data.transforms.trainers")


def train_background_ai(
    image_dir: str = "ml/data/dataset/images",
    mask_dir: str = "ml/data/dataset/masks",
    epochs: int = 10
) -> None:
    """
    Función de conveniencia para entrenar modelo U-Net.
    
    Args:
        image_dir: Directorio con imágenes de entrenamiento
        mask_dir: Directorio con máscaras de entrenamiento
        epochs: Número de épocas de entrenamiento
    """
    trainer = BackgroundTrainer(image_dir, mask_dir)
    trainer.train(epochs=epochs)


class BackgroundTrainer:
    """
    Entrenador para modelos de segmentación de fondo.
    
    Esta clase es responsable de:
    - Configurar el entrenamiento
    - Ejecutar el bucle de entrenamiento
    - Guardar el modelo entrenado
    
    Siguiendo el principio de Responsabilidad Única.
    """
    
    def __init__(
        self,
        image_dir: str = "ml/data/dataset/images",
        mask_dir: str = "ml/data/dataset/masks",
        model_save_path: str = "ml/segmentation/cacao_unet.pth"
    ):
        """
        Inicializa el entrenador.
        
        Args:
            image_dir: Directorio con imágenes de entrenamiento
            mask_dir: Directorio con máscaras de entrenamiento
            model_save_path: Ruta para guardar el modelo entrenado
        """
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.model_save_path = model_save_path
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"BackgroundTrainer inicializado (device={self.device})")
    
    def train(self, epochs: int = 10, batch_size: int = 4) -> None:
        """
        Entrena modelo U-Net para remoción de fondo.
        
        Args:
            epochs: Número de épocas de entrenamiento
            batch_size: Tamaño del lote
        """
        transform = T.Compose([
            T.Resize((256, 256)),
            T.ToTensor(),
        ])

        dataset = CacaoDataset(
            self.image_dir, 
            self.mask_dir, 
            transform, 
            auto_generate=True
        )
        loader = DataLoader(
            dataset, 
            batch_size=batch_size, 
            shuffle=True, 
            num_workers=0
        )

        model = UNet().to(self.device)
        criterion = nn.BCELoss()
        optimizer = optim.Adam(
            model.parameters(), 
            lr=1e-4, 
            weight_decay=1e-4
        )

        for epoch in range(epochs):
            for imgs, masks in loader:
                imgs, masks = imgs.to(self.device), masks.to(self.device)
                preds = model(imgs)
                loss = criterion(preds, masks)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            logger.info(f"Época {epoch+1}/{epochs} | Pérdida: {loss.item():.4f}")

        os.makedirs(os.path.dirname(self.model_save_path), exist_ok=True)
        torch.save(model.state_dict(), self.model_save_path)
        logger.info(f"Modelo entrenado y guardado en {self.model_save_path}")

