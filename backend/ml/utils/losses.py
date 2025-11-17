"""
Uncertainty-based multi-task loss weighting (Kendall et al.).
"""
import torch
import torch.nn as nn
from typing import Dict
import numpy as np

from .logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.utils.losses")


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
        initial_values = torch.tensor([
            initial_log_sigma + np.random.uniform(-0.05, 0.05)  # ±5% variación
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
            f"Uncertainty-based loss formula: L_total = Σ [ (1 / (2 * σ_i²)) * L_i + log σ_i ]"
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
        if predictions.ndim == 1:
            predictions = predictions.unsqueeze(0)
        if targets.ndim == 1:
            targets = targets.unsqueeze(0)
        
        # Forzar tamaño correcto (cortar a 4 dimensiones si hay más)
        num_targets = len(self.log_sigmas)
        if predictions.shape[1] > num_targets:
            logger.warning(f"Predictions tiene {predictions.shape[1]} columnas, cortando a {num_targets}")
            predictions = predictions[:, :num_targets]
        if targets.shape[1] > num_targets:
            logger.warning(f"Targets tiene {targets.shape[1]} columnas, cortando a {num_targets}")
            targets = targets[:, :num_targets]
        
        # 2) Sanity check
        assert predictions.shape == targets.shape, \
            f"Mismatch shapes in loss: preds={predictions.shape}, targets={targets.shape}"
        
        total_loss = 0.0
        
        # Smooth L1 base loss
        base_loss_fn = self.base_criterion
        
        # Asegurar que log_sigmas es 1D (4 parámetros independientes)
        if self.log_sigmas.ndim > 1:
            log_sigmas_flat = self.log_sigmas.flatten()
        else:
            log_sigmas_flat = self.log_sigmas
        
        # Para cada target i (usar min para evitar index out of bounds)
        B, C = predictions.shape
        C = min(predictions.shape[1], targets.shape[1], len(log_sigmas_flat))
        
        for i in range(C):
            pi = predictions[:, i]
            ti = targets[:, i]
            
            Li = base_loss_fn(pi, ti)  # [batch]
            
            # Obtener el log_sigma INDEPENDIENTE para esta tarea específica
            log_sigma_i = log_sigmas_flat[i]
            sigma_i = torch.exp(log_sigma_i)
            
            # Loss incertidumbre según Kendall et al.
            # Fórmula: L_i_weighted = (1 / (2 * σ_i²)) * L_i + log(σ_i)
            # Nota: Usamos log(σ_i) en vez de log(σ_i²) para estabilidad numérica
            # Si σ_i es muy pequeño, log(σ_i) puede ser muy negativo, pero eso está bien
            # porque el término (1/(2*σ_i²)) * L_i compensa
            sigma_sq = sigma_i ** 2
            # Evitar división por cero (aunque sigma_i > 0 por construcción)
            epsilon = 1e-8
            Li_weighted = (1.0 / (2.0 * sigma_sq + epsilon)) * Li + log_sigma_i  # [batch]
            
            total_loss = total_loss + Li_weighted  # [batch]
        
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
        if self.log_sigmas.ndim > 1:
            log_sigmas_flat = self.log_sigmas.flatten()
        else:
            log_sigmas_flat = self.log_sigmas
        
        # Verificar que tenemos exactamente 4 valores
        if len(log_sigmas_flat) != len(self.TARGETS):
            logger.warning(
                f"Mismatch: log_sigmas tiene {len(log_sigmas_flat)} valores, "
                f"pero hay {len(self.TARGETS)} targets"
            )
        
        sigmas = torch.exp(log_sigmas_flat).detach().cpu().numpy()
        return {target: float(sigmas[i]) for i, target in enumerate(self.TARGETS)}
