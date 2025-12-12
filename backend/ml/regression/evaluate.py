"""
Script de evaluación para modelos de regresión de dimensiones de cacao.
"""
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
# Importacin perezosa de matplotlib/seaborn para evitar MemoryError en Windows con multiprocessing
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import json
import logging
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import mean_absolute_percentage_error

from ..utils.logs import get_ml_logger
from ..utils.paths import (
    get_regressors_artifacts_dir,
    get_artifacts_dir,
    ensure_dir_exists,
)
from ..utils.io import save_json
from .models import TARGETS, TARGET_NAMES
from .scalers import load_scalers


logger = get_ml_logger("cacaoscan.ml.regression")

TargetArrayDict = Dict[str, np.ndarray]
TargetListDict = Dict[str, List[float]]
TargetMetricsDict = Dict[str, Dict[str, float]]
BatchTargets = Union[Dict[str, torch.Tensor], torch.Tensor]
BatchData = Union[Tuple[torch.Tensor, ...], List[torch.Tensor]]


def compute_regression_metrics(
    targets: np.ndarray,
    predictions: np.ndarray
) -> Dict[str, float]:
    """
    Calcula métricas de regresión comunes.
    
    Args:
        targets: Valores reales
        predictions: Predicciones del modelo
        
    Returns:
        Diccionario con métricas: mae, mse, rmse, r2, mape, relative_error
    """
    mae = mean_absolute_error(targets, predictions)
    mse = mean_squared_error(targets, predictions)
    rmse = np.sqrt(mse)
    r2 = r2_score(targets, predictions)
    
    # MAPE y error relativo (solo si hay valores no cero)
    non_zero_mask = targets != 0
    if np.any(non_zero_mask):
        mape = mean_absolute_percentage_error(
            targets[non_zero_mask],
            predictions[non_zero_mask]
        ) * 100
        relative_error = np.mean(
            np.abs((targets[non_zero_mask] - predictions[non_zero_mask]) / targets[non_zero_mask])
        ) * 100
    else:
        # If all targets are zero, mape and relative_error are 0.0
        mape = 0.0
        relative_error = 0.0
    
    return {
        'mae': float(mae),
        'mse': float(mse),
        'rmse': float(rmse),
        'r2': float(r2),
        'mape': float(mape),
        'relative_error': float(relative_error)
    }


class RegressionEvaluator:
    """Evaluador para modelos de regresión de cacao."""
    
    def __init__(
        self,
        model: nn.Module,
        test_loader: torch.utils.data.DataLoader,
        scalers: Optional[object] = None,
        device: torch.device = torch.device('cpu')
    ):
        """
        Inicializa el evaluador.
        
        Args:
            model: Modelo a evaluar
            test_loader: DataLoader de test
            scalers: Escaladores para desnormalización (opcional)
            device: Dispositivo para evaluación
        """
        self.model = model.to(device)
        self.test_loader = test_loader
        self.scalers = scalers
        self.device = device
        
        # Resultados de evaluación
        self.results = {}
        self.predictions = {}
        self.targets = {}
        
        logger.info("Evaluador inicializado")
    
    def evaluate_single_model(
        self,
        target: str,
        denormalize: bool = True
    ) -> Dict[str, float]:
        """
        Evalúa un modelo individual.
        
        Args:
            target: Target a evaluar
            denormalize: Si desnormalizar las predicciones
            
        Returns:
            Diccionario con métricas de evaluación
        """
        logger.info(f"Evaluando modelo para target: {target}")
        
        self.model.eval()
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for images, targets_batch in self.test_loader:
                images = images.to(self.device)
                
                # Manejar targets como diccionario o tensor
                if isinstance(targets_batch, dict):
                    # Si es diccionario, extraer el target especfico
                    targets = targets_batch[target].to(self.device)
                else:
                    # Si es tensor, usarlo directamente
                    targets = targets_batch.to(self.device)
                
                outputs = self.model(images)
                
                # Convertir a numpy
                predictions = outputs.cpu().numpy().flatten()
                targets_np = targets.cpu().numpy().flatten()
                
                all_predictions.extend(predictions)
                all_targets.extend(targets_np)
        
        all_predictions = np.array(all_predictions)
        all_targets = np.array(all_targets)
        
        # Desnormalizar si se especifica
        if denormalize and self.scalers is not None:
            try:
                # Crear diccionario temporal para desnormalización
                temp_data = {target: all_predictions}
                denorm_pred = self.scalers.inverse_transform(temp_data)
                all_predictions = denorm_pred[target]
                
                temp_data = {target: all_targets}
                denorm_targets = self.scalers.inverse_transform(temp_data)
                all_targets = denorm_targets[target]
                
                logger.info(f"Predicciones desnormalizadas para {target}")
            except Exception as e:
                logger.warning(f"Error desnormalizando para {target}: {e}")
        
        # Calcular métricas
        metrics = compute_regression_metrics(all_targets, all_predictions)
        metrics['n_samples'] = len(all_predictions)
        
        # Guardar predicciones y targets
        self.predictions[target] = all_predictions
        self.targets[target] = all_targets
        self.results[target] = metrics
        
        logger.info(f"Métricas para {target}: MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}, R²={metrics['r2']:.4f}")
        
        return metrics
    
    def evaluate_multi_head_model(
        self,
        denormalize: bool = True
    ) -> Dict[str, Dict[str, float]]:
        """
        Evalúa un modelo multi-head y devuelve métricas por target.
        """
        logger.info("Evaluando modelo multi-head/híbrido")
        
        self.model.eval()
        is_hybrid = "Hybrid" in type(self.model).__name__
        
        raw_predictions, raw_targets = self._collect_multi_head_batches(is_hybrid)
        all_predictions = self._batch_lists_to_arrays(raw_predictions)
        all_targets = self._batch_lists_to_arrays(raw_targets)
        
        if denormalize and self.scalers is not None:
            all_predictions, all_targets = self._denormalize_multi_head_results(
                all_predictions,
                all_targets
            )
        
        results = self._compute_multi_head_metrics(all_predictions, all_targets)
        
        self.predictions = all_predictions
        self.targets = all_targets
        self.results = results
        
        return results
    def _collect_multi_head_batches(
        self,
        is_hybrid: bool,
    ) -> Tuple[TargetListDict, TargetListDict]:
        predictions: TargetListDict = {target: [] for target in TARGETS}
        targets: TargetListDict = {target: [] for target in TARGETS}
        
        with torch.no_grad():
            for batch_data in self.test_loader:
                unpacked = self._unpack_multi_head_batch(batch_data)
                if unpacked is None:
                    continue
                
                images, targets_data, pixel_features = unpacked
                outputs = self._forward_multi_head(images, pixel_features, is_hybrid)
                targets_by_key = self._normalize_targets_dict(targets_data)
                
                for target in TARGETS:
                    predictions[target].extend(
                        outputs[target].detach().cpu().numpy().flatten()
                    )
                    targets[target].extend(
                        targets_by_key[target].detach().cpu().numpy().flatten()
                    )
        
        return predictions, targets

    def _unpack_multi_head_batch(
        self,
        batch_data: BatchData,
    ) -> Optional[Tuple[torch.Tensor, BatchTargets, Optional[torch.Tensor]]]:
        if not isinstance(batch_data, (list, tuple)):
            logger.error("Batch de datos inesperado (tipo inválido)")
            return None
        
        batch_len = len(batch_data)
        if batch_len == 3:
            images, targets_dict, pixel_features = batch_data
            pixel_tensor = pixel_features.to(self.device) if pixel_features is not None else None
        elif batch_len == 2:
            images, targets_dict = batch_data
            pixel_tensor = None
        else:
            logger.error(
                "Batch de datos inesperado. Se esperaban 2 o 3 tensores, "
                f"se obtuvieron {batch_len}"
            )
            return None
        
        return images.to(self.device), targets_dict, pixel_tensor

    def _forward_multi_head(
        self,
        images: torch.Tensor,
        pixel_features: Optional[torch.Tensor],
        is_hybrid: bool,
    ) -> Dict[str, torch.Tensor]:
        if is_hybrid and pixel_features is not None:
            return self.model(images, pixel_features)
        return self.model(images)

    def _normalize_targets_dict(
        self,
        targets_data: BatchTargets,
    ) -> Dict[str, torch.Tensor]:
        if isinstance(targets_data, dict):
            return {
                target: targets_data[target].to(self.device)
                for target in TARGETS
            }
        
        if targets_data.ndim != 2 or targets_data.shape[1] < len(TARGETS):
            raise ValueError(
                "El tensor de targets debe tener forma [batch_size, 4] con todos los objetivos."
            )
        
        return {
            target: targets_data[:, idx].to(self.device)
            for idx, target in enumerate(TARGETS)
        }

    def _batch_lists_to_arrays(
        self,
        batch_dict: TargetListDict,
    ) -> TargetArrayDict:
        return {
            target: np.array(values, dtype=np.float32) if values else np.array([], dtype=np.float32)
            for target, values in batch_dict.items()
        }

    def _denormalize_multi_head_results(
        self,
        predictions: TargetArrayDict,
        targets: TargetArrayDict,
    ) -> Tuple[TargetArrayDict, TargetArrayDict]:
        try:
            denorm_pred = self.scalers.inverse_transform(predictions)
            denorm_targets = self.scalers.inverse_transform(targets)
            logger.info("Predicciones desnormalizadas para modelo multi-head")
            return denorm_pred, denorm_targets
        except Exception as exc:
            logger.warning(
                f"Error desnormalizando modelo multi-head: {exc}",
                exc_info=True
            )
            return predictions, targets

    def _compute_multi_head_metrics(
        self,
        predictions: TargetArrayDict,
        targets: TargetArrayDict,
    ) -> TargetMetricsDict:
        results: TargetMetricsDict = {}
        
        for target in TARGETS:
            target_preds = predictions[target]
            target_values = targets[target]
            
            if target_preds.size == 0 or target_values.size == 0:
                logger.warning(f"No hay datos para evaluar el target {target}")
                continue
            
            metrics = compute_regression_metrics(target_values, target_preds)
            metrics['n_samples'] = int(target_preds.size)
            results[target] = metrics
            
            logger.info(
                f"{target}: MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}, R²={metrics['r2']:.4f}"
            )
        
        return results
    
    def _setup_plot_style(self) -> None:
        """Configure matplotlib and seaborn style for plots."""
        # Lazy import to avoid MemoryError in Windows with multiprocessing
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        plt.style.use('default')
        sns.set_palette("husl")
    
    def _create_subplots_layout(
        self,
        n_targets: int,
        figsize: Tuple[int, int] = (15, 12)
    ) -> Tuple:
        """Create subplots layout for plotting."""
        import matplotlib.pyplot as plt
        
        _, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
        # Hide unused subplots
        for idx in range(n_targets, 4):
            axes[idx].set_visible(False)
        
        return _, axes
    
    def _add_metrics_text(
        self,
        ax,
        text: str,
        position: Tuple[float, float] = (0.05, 0.95)
    ) -> None:
        """Add text with metrics to plot axis."""
        props = {'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.8}
        ax.text(
            position[0], position[1], text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment='top',
            bbox=props
        )
    
    def _save_plot_if_specified(
        self,
        save_path: Optional[Path],
        plot_type: str
    ) -> None:
        """Save plot to file if save_path is specified."""
        import matplotlib.pyplot as plt
        
        if save_path:
            ensure_dir_exists(save_path.parent)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Gráficos de {plot_type} guardados en {save_path}")
    
    def plot_parity_plots(
        self,
        save_path: Optional[Path] = None,
        figsize: Tuple[int, int] = (15, 12)
    ) -> None:
        """
        Genera gráficos de paridad (predicción vs realidad).
        
        Args:
            save_path: Ruta para guardar los gráficos
            figsize: Tamaño de la figura
        """
        if not self.results:
            logger.warning("No hay resultados para graficar. Ejecutar evaluación primero.")
            return
        
        import matplotlib.pyplot as plt
        
        self._setup_plot_style()
        
        n_targets = len(self.results)
        _, axes = self._create_subplots_layout(n_targets, figsize)
        
        for idx, (target, metrics) in enumerate(self.results.items()):
            if idx >= 4:  # Máximo 4 subplots
                break
            
            ax = axes[idx]
            predictions = self.predictions[target]
            targets = self.targets[target]
            
            # Scatter plot
            ax.scatter(targets, predictions, alpha=0.6, s=20)
            
            # Línea perfecta (y = x)
            min_val = min(targets.min(), predictions.min())
            max_val = max(targets.max(), predictions.max())
            ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Predicción perfecta')
            
            # Configurar gráfico
            ax.set_xlabel(f'Valor Real ({TARGET_NAMES[target]})')
            ax.set_ylabel(f'Predicción ({TARGET_NAMES[target]})')
            ax.set_title(f'{TARGET_NAMES[target]} - R² = {metrics["r2"]:.3f}')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Añadir texto con métricas
            textstr = f'MAE: {metrics["mae"]:.3f}\\nRMSE: {metrics["rmse"]:.3f}\\nMAPE: {metrics["mape"]:.1f}%'
            self._add_metrics_text(ax, textstr)
        
        plt.tight_layout()
        self._save_plot_if_specified(save_path, "paridad")
        plt.show()
    
    def plot_residual_plots(
        self,
        save_path: Optional[Path] = None,
        figsize: Tuple[int, int] = (15, 12)
    ) -> None:
        """
        Genera gráficos de residuos.
        
        Args:
            save_path: Ruta para guardar los gráficos
            figsize: Tamaño de la figura
        """
        if not self.results:
            logger.warning("No hay resultados para graficar. Ejecutar evaluación primero.")
            return
        
        import matplotlib.pyplot as plt
        
        self._setup_plot_style()
        
        n_targets = len(self.results)
        _, axes = self._create_subplots_layout(n_targets, figsize)
        
        for idx, (target, metrics) in enumerate(self.results.items()):
            if idx >= 4:  # Máximo 4 subplots
                break
            
            ax = axes[idx]
            predictions = self.predictions[target]
            targets = self.targets[target]
            residuals = targets - predictions
            
            # Scatter plot de residuos
            ax.scatter(targets, residuals, alpha=0.6, s=20)
            ax.axhline(y=0, color='r', linestyle='--', lw=2)
            
            # Configurar gráfico
            ax.set_xlabel(f'Valor Real ({TARGET_NAMES[target]})')
            ax.set_ylabel(f'Residuos ({TARGET_NAMES[target]})')
            ax.set_title(f'Residuos - {TARGET_NAMES[target]}')
            ax.grid(True, alpha=0.3)
            
            # Añadir texto con estadísticas de residuos
            mean_residual = np.mean(residuals)
            std_residual = np.std(residuals)
            textstr = f'Media: {mean_residual:.3f}\\nStd: {std_residual:.3f}'
            self._add_metrics_text(ax, textstr)
        
        plt.tight_layout()
        self._save_plot_if_specified(save_path, "residuos")
        plt.show()
    
    def generate_report(
        self,
        save_path: Optional[Path] = None
    ) -> Dict[str, Union[Dict, List]]:
        """
        Genera reporte completo de evaluación.
        
        Args:
            save_path: Ruta para guardar el reporte JSON
            
        Returns:
            Diccionario con reporte completo
        """
        if not self.results:
            logger.warning("No hay resultados para reportar. Ejecutar evaluación primero.")
            return {}
        
        # Calcular métricas agregadas
        total_mae = np.mean([metrics['mae'] for metrics in self.results.values()])
        total_rmse = np.mean([metrics['rmse'] for metrics in self.results.values()])
        total_r2 = np.mean([metrics['r2'] for metrics in self.results.values()])
        
        # Crear reporte
        report = {
            'summary': {
                'total_targets': len(self.results),
                'average_mae': float(total_mae),
                'average_rmse': float(total_rmse),
                'average_r2': float(total_r2),
                'evaluation_timestamp': pd.Timestamp.now().isoformat()
            },
            'individual_results': self.results,
            'model_info': {
                'model_type': type(self.model).__name__,
                'device': str(self.device),
                'total_parameters': sum(p.numel() for p in self.model.parameters())
            }
        }
        
        # Guardar reporte
        if save_path:
            ensure_dir_exists(save_path.parent)
            save_json(report, save_path)
            logger.info(f"Reporte de evaluación guardado en {save_path}")
        
        # Log de resumen
        logger.info("=== REPORTE DE EVALUACIÓN ===")
        logger.info(f"Promedio MAE: {total_mae:.4f}")
        logger.info(f"Promedio RMSE: {total_rmse:.4f}")
        logger.info(f"Promedio R²: {total_r2:.4f}")
        
        for target, metrics in self.results.items():
            logger.info(f"{target.upper()}: MAE={metrics['mae']:.4f}, RMSE={metrics['rmse']:.4f}, R²={metrics['r2']:.4f}")
        
        return report


def load_model_for_evaluation(
    model_path: Path,
    model_class: nn.Module,
    device: torch.device
) -> nn.Module:
    """
    Carga un modelo para evaluación de forma segura.
    
    Args:
        model_path: Ruta al archivo del modelo
        model_class: Clase del modelo
        device: Dispositivo para cargar el modelo
        
    Returns:
        Modelo cargado
        
    Raises:
        RuntimeError: Si el modelo no se puede cargar de forma segura
    """
    # SECURITY: Use weights_only=True to prevent arbitrary code execution (S6985)
    # This is the safest way to load PyTorch models (available in PyTorch 2.1+)
    # If weights_only is not available, fall back to loading state_dict only
    try:
        # Try to load with weights_only=True (safest method, PyTorch 2.1+)
        # weights_only evita ejecución de código arbitrario en los checkpoints
        checkpoint = torch.load(model_path, map_location=device, weights_only=True)  # NOSONAR
    except TypeError as exc:
        raise RuntimeError(
            "La versión de PyTorch instalada no soporta weights_only=True. "
            "Actualiza a PyTorch 2.1 o superior para permitir una carga segura "
            f"de modelos (archivo: {model_path})."
        ) from exc
    
    # Load state_dict into model
    if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
        model = model_class()
        model.load_state_dict(checkpoint['model_state_dict'])
    elif isinstance(checkpoint, dict):
        # Assume it's a state_dict
        model = model_class()
        model.load_state_dict(checkpoint)
    else:
        # Last resort: if checkpoint is the model itself (shouldn't happen with weights_only=True)
        raise RuntimeError(
            f"Unexpected checkpoint format from {model_path}. "
            "Expected state_dict or dict with 'model_state_dict'."
        )
    
    model.eval()
    model.to(device)
    logger.info(f"Modelo cargado de forma segura desde {model_path}")
    
    return model


def evaluate_model_from_file(
    model_path: Path,
    model_class: nn.Module,
    test_loader: torch.utils.data.DataLoader,
    scalers: Optional[object] = None,
    device: torch.device = torch.device('cpu'),
    target: Optional[str] = None
) -> Dict[str, Union[Dict, float]]:
    """
    Evalúa un modelo cargado desde archivo.
    
    Args:
        model_path: Ruta al archivo del modelo
        model_class: Clase del modelo
        test_loader: DataLoader de test
        scalers: Escaladores para desnormalización
        device: Dispositivo para evaluación
        target: Target específico (para modelos individuales)
        
    Returns:
        Resultados de evaluación
    """
    model = load_model_for_evaluation(model_path, model_class, device)
    
    evaluator = RegressionEvaluator(
        model=model,
        test_loader=test_loader,
        scalers=scalers,
        device=device
    )
    
    if target:
        results = evaluator.evaluate_single_model(target)
    else:
        results = evaluator.evaluate_multi_head_model()
    
    return results


