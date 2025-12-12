"""
Uncertainty-based multi-task loss weighting (Kendall et al.).
"""
import torch
import torch.nn as nn
from typing import Dict
import numpy as np

from .logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.utils.losses")


def _normalizar_tensor_a_2d(tensor: torch.Tensor) -> torch.Tensor:
    """Normaliza un tensor a 2D (batch, features)."""
    if tensor.ndim == 1:
        return tensor.unsqueeze(0)
    return tensor


def _cortar_tensor_a_num_targets(tensor: torch.Tensor, num_targets: int) -> torch.Tensor:
    """Corta un tensor a num_targets columnas si tiene más."""
    if tensor.shape[1] > num_targets:
        logger.warning(f"Tensor tiene {tensor.shape[1]} columnas, cortando a {num_targets}")
        return tensor[:, :num_targets]
    return tensor


def _aplanar_log_sigmas(log_sigmas: torch.Tensor) -> torch.Tensor:
    """Aplana log_sigmas a 1D si es necesario."""
    if log_sigmas.ndim > 1:
        return log_sigmas.flatten()
    return log_sigmas


def _calcular_loss_incertidumbre(
    base_loss: torch.Tensor,
    log_sigma: torch.Tensor,
    epsilon: float = 1e-8
) -> torch.Tensor:
    """
    Calcula la pérdida ponderada por incertidumbre.
    
    Fórmula: L_i_weighted = (1 / (2 * σ_i²)) * L_i + log(σ_i)
    """
    sigma = torch.exp(log_sigma)
    sigma_sq = sigma ** 2
    return (1.0 / (2.0 * sigma_sq + epsilon)) * base_loss + log_sigma


class UncertaintyWeightedLoss(nn.Module):
    """
    Multi-task loss with learnable uncertainty weights.
    
    Formula: L_total = Σ [ (1 / (2 * σ_i²)) * L_i + log σ_i ]
    
    Each output (alto, ancho, grosor, peso) has its own learnable σ_i.
    """
    
    TARGETS = ["alto", "ancho", "grosor", "peso"]
    
    def __init__(self, initial_sigma: float = 0.3):
        """
        Initialize uncertainty-weighted loss.
        
        Args:
            initial_sigma: Initial value for σ_i (default: 0.3)
        """
        super(UncertaintyWeightedLoss, self).__init__()
        
        # CRÍTICO: Crear 4 parámetros INDEPENDIENTES (uno por cada target)
        # Inicializar con pequeñas variaciones para que el optimizador pueda diferenciarlos
        # Usamos log(σ_i) para asegurar que σ_i > 0
        num_targets = len(self.TARGETS)
        initial_log_sigma = np.log(initial_sigma)
        
        # Inicializar cada sigma con una pequeña variación aleatoria
        # Esto ayuda a que el optimizador pueda diferenciarlos desde el inicio
        # Use fixed seed for reproducibility in parameter initialization
        rng = np.random.default_rng(seed=42)
        initial_values = torch.tensor([
            initial_log_sigma + rng.uniform(-0.05, 0.05)  # ±5% variación
            for _ in range(num_targets)
        ], dtype=torch.float32)
        
        # Crear parámetros independientes (uno por target)
        self.log_sigmas = nn.Parameter(initial_values)
        
        # Verificar que son parámetros independientes
        assert len(self.log_sigmas) == num_targets, \
            f"Se esperaban {num_targets} parámetros independientes, se obtuvieron {len(self.log_sigmas)}"
        
        # Base loss: SmoothL1Loss
        self.base_criterion = nn.SmoothL1Loss(reduction='none')
        
        logger.info(
            f"UncertaintyWeightedLoss initialized with initial_sigma={initial_sigma}"
        )
        logger.info(
            "Uncertainty-based loss formula: L_total = Σ [ (1 / (2 * σ_i²)) * L_i + log σ_i ]"
        )
        logger.info(f"Learnable sigmas for targets: {self.TARGETS}")
        logger.info(f"Initial log_sigmas (4 parámetros independientes): {self.log_sigmas.data.cpu().numpy()}")
        logger.info(f"Initial sigmas (exp): {torch.exp(self.log_sigmas).data.cpu().numpy()}")
    
    def forward(self, predictions, targets):
        """
        Devuelve SOLO un escalar. Nada de tuples.
        """
        
        # Log inmediatamente shapes
        print("DEBUG Loss: preds:", predictions.shape, "targets:", targets.shape)
        
        # 1) Normalizar pred/target a 2D
        predictions = _normalizar_tensor_a_2d(predictions)
        targets = _normalizar_tensor_a_2d(targets)
        
        # Forzar tamaño correcto (cortar a 4 dimensiones si hay más)
        num_targets = len(self.log_sigmas)
        predictions = _cortar_tensor_a_num_targets(predictions, num_targets)
        targets = _cortar_tensor_a_num_targets(targets, num_targets)
        
        # 2) Sanity check
        assert predictions.shape == targets.shape, \
            f"Mismatch shapes in loss: preds={predictions.shape}, targets={targets.shape}"
        
        total_loss = 0.0
        
        # Asegurar que log_sigmas es 1D (4 parámetros independientes)
        log_sigmas_flat = _aplanar_log_sigmas(self.log_sigmas)
        
        # Para cada target i (usar min para evitar index out of bounds)
        _, C = predictions.shape
        C = min(predictions.shape[1], targets.shape[1], len(log_sigmas_flat))
        
        for i in range(C):
            pi = predictions[:, i]
            ti = targets[:, i]
            
            li = self.base_criterion(pi, ti)  # [batch]
            
            # Obtener el log_sigma INDEPENDIENTE para esta tarea específica
            log_sigma_i = log_sigmas_flat[i]
            
            # Loss incertidumbre según Kendall et al.
            li_weighted = _calcular_loss_incertidumbre(li, log_sigma_i)  # [batch]
            
            total_loss = total_loss + li_weighted  # [batch]
        
        # Promediar sobre el batch para obtener escalar
        total_loss = total_loss.mean()
        
        # IMPORTANTE: devolver SOLO el escalar
        return total_loss
    
    def get_sigmas(self) -> Dict[str, float]:
        """
        Get current sigma values.
        
        Returns:
            Dictionary of sigma values per target
        """
        # Asegurar que log_sigmas es un tensor 1D con 4 elementos
        log_sigmas_flat = _aplanar_log_sigmas(self.log_sigmas)
        
        # Verificar que tenemos exactamente 4 valores
        if len(log_sigmas_flat) != len(self.TARGETS):
            logger.warning(
                f"Mismatch: log_sigmas tiene {len(log_sigmas_flat)} valores, "
                f"pero hay {len(self.TARGETS)} targets"
            )
        
        sigmas = torch.exp(log_sigmas_flat).detach().cpu().numpy()
        return {target: float(sigmas[i]) for i, target in enumerate(self.TARGETS)}
