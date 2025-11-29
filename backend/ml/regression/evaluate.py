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
from ..utils.paths import get_regressors_artifacts_dir, get_artifacts_dir
from ..utils.io import save_json
from .models import TARGETS, TARGET_NAMES
from .scalers import load_scalers


logger = get_ml_logger("cacaoscan.ml.regression")


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
        mae = mean_absolute_error(all_targets, all_predictions)
        mse = mean_squared_error(all_targets, all_predictions)
        rmse = np.sqrt(mse)
        r2 = r2_score(all_targets, all_predictions)
        
        # MAPE (Mean Absolute Percentage Error)
        mape = mean_absolute_percentage_error(all_targets, all_predictions) * 100
        
        # Error relativo medio
        relative_error = np.mean(np.abs((all_targets - all_predictions) / all_targets)) * 100
        
        metrics = {
            'mae': float(mae),
            'mse': float(mse),
            'rmse': float(rmse),
            'r2': float(r2),
            'mape': float(mape),
            'relative_error': float(relative_error),
            'n_samples': len(all_predictions)
        }
        
        # Guardar predicciones y targets
        self.predictions[target] = all_predictions
        self.targets[target] = all_targets
        self.results[target] = metrics
        
        logger.info(f"Métricas para {target}: MAE={mae:.4f}, RMSE={rmse:.4f}, R²={r2:.4f}")
        
        return metrics
    
    def evaluate_multi_head_model(
        self,
        denormalize: bool = True
    ) -> Dict[str, Dict[str, float]]:
        """
        Evalúa un modelo multi-head.
        
        Args:
            denormalize: Si desnormalizar las predicciones
            
        Returns:
            Diccionario con métricas por target
        """
        logger.info("Evaluando modelo multi-head/híbrido")
        
        self.model.eval()
        all_predictions = {target: [] for target in TARGETS}
        all_targets = {target: [] for target in TARGETS}
        
        # Determinar si el modelo es híbrido (basado en el tipo de modelo)
        is_hybrid = "Hybrid" in type(self.model).__name__
        
        with torch.no_grad():
            # --- INICIO DE CORRECCIÓN ---
            # El loader puede devolver 2 o 3 items
            for batch_data in self.test_loader:
                images, targets_dict, pixel_features = None, None, None
                
                # Desempaquetar datos basado en si es híbrido o no
                if len(batch_data) == 3:
                    images, targets_dict, pixel_features = batch_data
                    if is_hybrid:
                        pixel_features = pixel_features.to(self.device)
                elif len(batch_data) == 2:
                     images, targets_dict = batch_data
                else:
                    logger.error(f"Batch de datos inesperado. Se esperaban 2 o 3 tensores, se obtuvieron {len(batch_data)}")
                    continue
                
                images = images.to(self.device)
                
                # Forward pass
                if is_hybrid and pixel_features is not None:
                    outputs = self.model(images, pixel_features)
                else:
                    outputs = self.model(images)
                # --- FIN DE CORRECCIÓN ---
                
                # Manejar targets: puede ser tensor 2D [batch_size, 4] o diccionario
                if isinstance(targets_dict, dict):
                    # Si es diccionario, usar directamente
                    targets_by_key = targets_dict
                else:
                    # Si es tensor 2D, extraer columnas según el orden: [alto, ancho, grosor, peso]
                    # targets_dict tiene forma [batch_size, 4]
                    targets_by_key = {
                        'alto': targets_dict[:, 0],
                        'ancho': targets_dict[:, 1],
                        'grosor': targets_dict[:, 2],
                        'peso': targets_dict[:, 3]
                    }
                
                for target in TARGETS:
                    # Obtener predicciones y targets
                    predictions_batch = outputs[target].cpu().numpy().flatten()
                    targets_batch = targets_by_key[target].cpu().numpy().flatten()
                    
                    all_predictions[target].extend(predictions_batch)
                    all_targets[target].extend(targets_batch)
        
        # Convertir a arrays numpy
        for target in TARGETS:
            all_predictions[target] = np.array(all_predictions[target])
            all_targets[target] = np.array(all_targets[target])
        
        # Desnormalizar si se especifica
        if denormalize and self.scalers is not None:
            try:
                # Usar .transform(dict) y .inverse_transform(dict)
                
                # Preparar dict para desnormalización
                pred_dict_norm = {t: all_predictions[t] for t in TARGETS}
                targ_dict_norm = {t: all_targets[t] for t in TARGETS}

                denorm_pred = self.scalers.inverse_transform(pred_dict_norm)
                denorm_targets = self.scalers.inverse_transform(targ_dict_norm)
                
                all_predictions = denorm_pred
                all_targets = denorm_targets
                
                logger.info("Predicciones desnormalizadas para modelo multi-head")
            except Exception as e:
                logger.warning(f"Error desnormalizando modelo multi-head: {e}", exc_info=True)
        
        # Calcular métricas para cada target
        results = {}
        for target in TARGETS:
            predictions = all_predictions[target]
            targets = all_targets[target]
            
            # Asegurarse de que no estén vacíos
            if len(targets) == 0 or len(predictions) == 0:
                logger.warning(f"No hay datos para evaluar el target {target}")
                continue

            mae = mean_absolute_error(targets, predictions)
            mse = mean_squared_error(targets, predictions)
            rmse = np.sqrt(mse)
            r2 = r2_score(targets, predictions)
            
            # Calcular MAPE de forma segura (evitar división por cero)
            non_zero_mask = targets != 0
            if np.any(non_zero_mask):
                mape = mean_absolute_percentage_error(targets[non_zero_mask], predictions[non_zero_mask]) * 100
                relative_error = np.mean(np.abs((targets[non_zero_mask] - predictions[non_zero_mask]) / targets[non_zero_mask])) * 100
            else:
                mape = 0.0
                relative_error = 0.0

            
            results[target] = {
                'mae': float(mae),
                'mse': float(mse),
                'rmse': float(rmse),
                'r2': float(r2),
                'mape': float(mape),
                'relative_error': float(relative_error),
                'n_samples': len(predictions)
            }
            
            logger.info(f"{target}: MAE={mae:.4f}, RMSE={rmse:.4f}, R²={r2:.4f}")
        
        # Guardar predicciones y targets
        self.predictions = all_predictions
        self.targets = all_targets
        self.results = results
        
        return results
    
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
        
        # Importacin perezosa de matplotlib/seaborn (lazy import) para evitar MemoryError en Windows con multiprocessing
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Configurar estilo
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Crear figura
        n_targets = len(self.results)
        _, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
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
            props = {'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.8}
            ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', bbox=props)
        
        # Ocultar subplots no utilizados
        for idx in range(n_targets, 4):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        
        # Guardar si se especifica
        if save_path:
            ensure_dir_exists(save_path.parent)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Gráficos de paridad guardados en {save_path}")
        
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
        
        # Importacin perezosa de matplotlib/seaborn (lazy import) para evitar MemoryError en Windows con multiprocessing
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Configurar estilo
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Crear figura
        n_targets = len(self.results)
        _, axes = plt.subplots(2, 2, figsize=figsize)
        axes = axes.flatten()
        
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
            props = {'boxstyle': 'round', 'facecolor': 'wheat', 'alpha': 0.8}
            ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=10,
                   verticalalignment='top', bbox=props)
        
        # Ocultar subplots no utilizados
        for idx in range(n_targets, 4):
            axes[idx].set_visible(False)
        
        plt.tight_layout()
        
        # Guardar si se especifica
        if save_path:
            ensure_dir_exists(save_path.parent)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Gráficos de residuos guardados en {save_path}")
        
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
    Carga un modelo para evaluación.
    
    Args:
        model_path: Ruta al archivo del modelo
        model_class: Clase del modelo
        device: Dispositivo para cargar el modelo
        
    Returns:
        Modelo cargado
    """
    # Safe loading: restrict pickle module to prevent untrusted code execution
    import pickle
    class RestrictedUnpickler(pickle.Unpickler):
        def find_class(self, module, name):
            # Only allow safe modules
            if module == "collections" and name == "OrderedDict":
                return super().find_class(module, name)
            if module == "torch._utils" and name == "_rebuild_tensor_v2":
                return super().find_class(module, name)
            if module == "torch.storage" and name == "_load_from_bytes":
                return super().find_class(module, name)
            raise pickle.UnpicklingError(f"global '{module}.{name}' is forbidden")

    def restricted_load(f):
        return RestrictedUnpickler(f).load()

    with open(model_path, "rb") as f:
        checkpoint = torch.load(f, map_location=device, pickle_module=pickle, pickle_loader=restricted_load)
    
    if 'model_state_dict' in checkpoint:
        model = model_class()
        model.load_state_dict(checkpoint['model_state_dict'])
    else:
        model = checkpoint
    
    model.eval()
    logger.info(f"Modelo cargado desde {model_path}")
    
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


