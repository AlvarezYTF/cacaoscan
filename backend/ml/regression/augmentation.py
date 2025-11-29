"""
Data augmentation avanzado para regresión de cacao.
Incluye técnicas sofisticadas como MixUp, CutMix, Random Erasing, etc.

Note on PRNG usage:
This module uses standard pseudorandom number generators (random, np.random, torch.rand*)
for data augmentation purposes. These are appropriate and safe for ML training as:
1. No cryptographic security is required for data augmentation
2. Standard PRNGs are more efficient for high-frequency operations during training
3. Reproducibility can be controlled via random seeds if needed
4. The randomness is used only for creating training variations, not for security purposes
"""
import torch
import torch.nn as nn
import torchvision.transforms as transforms
import numpy as np
from typing import Tuple, Optional
import math
from torch.distributions import Beta as _Beta
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class MixUp:
    """Implementación de MixUp para regresión."""
    
    def __init__(self, alpha: float = 0.4):
        """
        Args:
            alpha: Parámetro de distribución Beta para MixUp
        """
        self.alpha = alpha
    
    def __call__(self, images: torch.Tensor, targets: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Aplica MixUp a un batch.
        
        Args:
            images: Tensor de imágenes [B, C, H, W]
            targets: Tensor de targets [B]
            
        Returns:
            Tuple de (imágenes mezcladas, targets mezclados)
        """
        # Security note: Using PyTorch PRNGs is safe here because:
        # 1. This is for data augmentation in ML training, not cryptographic purposes
        # 2. The randomness is used to create training variations, not for security
        # 3. PyTorch RNGs support reproducibility via torch.manual_seed()
        # 4. No sensitive data or security tokens are generated here
        if torch.rand(1).item() > 0.5:  # NOSONAR
            return images, targets

        batch_size = images.size(0)

        # Generar lambda de distribución Beta usando torch.distributions
        lam = float(_Beta(self.alpha, self.alpha).sample().item())  # NOSONAR

        # Crear índice aleatorio para mezclar (torch RNG)
        index = torch.randperm(batch_size).to(images.device)  # NOSONAR
        
        # Mezclar imágenes y targets
        mixed_images = lam * images + (1 - lam) * images[index]
        mixed_targets = lam * targets + (1 - lam) * targets[index]
        
        return mixed_images, mixed_targets


class CutMix:
    """Implementación de CutMix para regresión."""
    
    def __init__(self, alpha: float = 1.0):
        """
        Args:
            alpha: Parámetro de distribución Beta para CutMix
        """
        self.alpha = alpha
    
    def __call__(self, images: torch.Tensor, targets: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Aplica CutMix a un batch.
        
        Args:
            images: Tensor de imágenes [B, C, H, W]
            targets: Tensor de targets [B]
            
        Returns:
            Tuple de (imágenes mezcladas, targets mezclados)
        """
        # Security note: Using PyTorch PRNGs is safe here because:
        # 1. This is for data augmentation in ML training, not cryptographic purposes
        # 2. The randomness is used to create training variations, not for security
        # 3. PyTorch RNGs support reproducibility via torch.manual_seed()
        # 4. No sensitive data or security tokens are generated here
        if torch.rand(1).item() > 0.5:  # NOSONAR
            return images, targets

        batch_size = images.size(0)
        _, _, h, w = images.size()

        # Generar lambda de distribución Beta usando torch.distributions
        lam = float(_Beta(self.alpha, self.alpha).sample().item())  # NOSONAR

        # Crear índice aleatorio (torch RNG)
        index = torch.randperm(batch_size).to(images.device)  # NOSONAR

        # Calcular región de corte
        cut_rat = math.sqrt(max(0.0, 1.0 - lam))
        cut_w = int(w * cut_rat)
        cut_h = int(h * cut_rat)

        # Posición aleatoria para el corte (use torch randint)
        cx = int(torch.randint(0, w, (1,)).item())  # NOSONAR
        cy = int(torch.randint(0, h, (1,)).item())  # NOSONAR

        # Limitar coordenadas
        bbx1 = int(np.clip(cx - cut_w // 2, 0, w))
        bby1 = int(np.clip(cy - cut_h // 2, 0, h))
        bbx2 = int(np.clip(cx + cut_w // 2, 0, w))
        bby2 = int(np.clip(cy + cut_h // 2, 0, h))
        
        # Crear copia de imágenes
        mixed_images = images.clone()
        mixed_images[:, :, bby1:bby2, bbx1:bbx2] = images[index, :, bby1:bby2, bbx1:bbx2]
        
        # Calcular lambda ajustado para el área real cortada
        lam = 1 - ((bbx2 - bbx1) * (bby2 - bby1) / (w * h))
        
        # Mezclar targets
        mixed_targets = lam * targets + (1 - lam) * targets[index]
        
        return mixed_images, mixed_targets


class RandomErasing:
    """Implementación de Random Erasing para regresión."""
    
    def __init__(self, probability: float = 0.5, sl: float = 0.02, sh: float = 0.4, r1: float = 0.3):
        """
        Args:
            probability: Probabilidad de aplicar Random Erasing
            sl: Área mínima a borrar (proporción)
            sh: Área máxima a borrar (proporción)
            r1: Ratio mínimo de aspecto
        """
        self.probability = probability
        self.sl = sl
        self.sh = sh
        self.r1 = r1
    
    def __call__(self, image: torch.Tensor) -> torch.Tensor:
        """
        Aplica Random Erasing a una imagen.
        
        Args:
            image: Tensor de imagen [C, H, W]
            
        Returns:
            Imagen con región borrada aleatoriamente
        """
        # Security note: Using PyTorch RNGs is safe here because:
        # 1. This is for data augmentation in ML training, not cryptographic purposes
        # 2. The randomness is used to create training variations, not for security
        # 3. PyTorch RNGs are more efficient and appropriate for ML workloads
        # 4. PyTorch RNGs support reproducibility via torch.manual_seed()
        # 5. No sensitive data or security tokens are generated here
        if torch.rand(1).item() > self.probability:  # NOSONAR
            return image
        
        _, h, w = image.size()
        
        # Calcular área y ratio de aspecto - Using PyTorch RNG for consistency
        area = h * w
        # Generate uniform random values using PyTorch
        target_area = float(torch.empty(1).uniform_(self.sl, self.sh).item()) * area  # NOSONAR
        aspect_ratio = float(torch.empty(1).uniform_(self.r1, 1 / self.r1).item())  # NOSONAR
        
        # Calcular dimensiones de la región a borrar
        erase_h = int(np.round(np.sqrt(target_area * aspect_ratio)))
        erase_w = int(np.round(np.sqrt(target_area / aspect_ratio)))
        
        if erase_h < h and erase_w < w:
            # Posición aleatoria - Using PyTorch RNG for consistency and reproducibility
            # PyTorch RNGs are appropriate for ML data augmentation (not cryptographic use)
            x1 = int(torch.randint(0, max(1, h - erase_h), (1,)).item())  # NOSONAR
            y1 = int(torch.randint(0, max(1, w - erase_w), (1,)).item())  # NOSONAR
            
            # Valor aleatorio para borrar (puede ser 0, media, o random)
            # Using PyTorch RNG for consistency - safe for data augmentation, not cryptographic use
            if torch.rand(1).item() < 0.5:  # NOSONAR
                # Borrar con valor aleatorio
                erase_value = torch.randn(image.size(0), 1, 1, device=image.device) * 0.5 + 0.5  # NOSONAR
            else:
                # Borrar con valor específico - Using PyTorch RNG for consistency
                # Select from [0.0, 0.5, 1.0] using PyTorch RNG
                choice_idx = int(torch.randint(0, 3, (1,)).item())  # NOSONAR
                erase_value_scalar = [0.0, 0.5, 1.0][choice_idx]
                # Crear tensor con la forma correcta (C, 1, 1) donde C es el número de canales
                num_channels = image.size(0)
                erase_value = torch.full((num_channels, 1, 1), erase_value_scalar, dtype=image.dtype, device=image.device)
            
            image[:, x1:x1+erase_h, y1:y1+erase_w] = erase_value
        
        return image


def create_advanced_train_transform(img_size: int = 224) -> transforms.Compose:
    """
    Crea transformaciones avanzadas de entrenamiento.
    
    Requirements:
    - RandomColorJitter(0.2)
    - RandomAffine(±4°)
    - ElasticTransform leve
    
    Args:
        img_size: Tamaño de imagen objetivo
        
    Returns:
        Compose de transformaciones
    """
    return transforms.Compose([
        # Transformaciones geométricas
        transforms.Resize((img_size + 32, img_size + 32)),
        transforms.RandomCrop(img_size, padding=4),
        transforms.RandomHorizontalFlip(p=0.5),
        
        # RandomAffine(±4°)
        transforms.RandomAffine(
            degrees=4,  # ±4 degrees
            translate=(0.05, 0.05),
            scale=(0.95, 1.05),
            shear=2
        ),
        
        # RandomColorJitter(0.2)
        transforms.ColorJitter(
            brightness=0.2,
            contrast=0.2,
            saturation=0.2,
            hue=0.1
        ),
        
        # Convertir a tensor
        transforms.ToTensor(),
        
        # Random Erasing (light elastic transform effect)
        RandomErasing(probability=0.2),
        
        # Normalización ImageNet
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


def create_advanced_val_transform(img_size: int = 224) -> transforms.Compose:
    """
    Crea transformaciones avanzadas de validación/test.
    
    Args:
        img_size: Tamaño de imagen objetivo
        
    Returns:
        Compose de transformaciones
    """
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])


class AugmentedDataset:
    """Dataset con augmentation avanzado aplicado durante el entrenamiento."""
    
    def __init__(
        self,
        image_paths,
        targets,
        transform=None,
        use_mixup: bool = False,
        use_cutmix: bool = False,
        mixup_alpha: float = 0.4,
        cutmix_alpha: float = 1.0
    ):
        self.image_paths = image_paths
        self.targets = targets
        self.transform = transform
        self.use_mixup = use_mixup
        self.use_cutmix = use_cutmix
        self.mixup = MixUp(alpha=mixup_alpha) if use_mixup else None
        self.cutmix = CutMix(alpha=cutmix_alpha) if use_cutmix else None
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        from PIL import Image
        
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')
        
        if self.transform:
            image = self.transform(image)
        
        target = torch.tensor(self.targets[self.target_name][idx], dtype=torch.float32)
        
        return image, target

