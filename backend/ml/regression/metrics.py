"""
Métricas robustas para regresión de cacao.

Implementa cálculo robusto de R² y otras métricas con:
- Validación de dimensiones
- Manejo de NaN/Inf
- Desnormalización correcta
- Logs detallados por componente
"""
import numpy as np
from typing import Dict, Tuple, Optional, List
import logging

from ..utils.logs import get_ml_logger

logger = get_ml_logger("cacaoscan.ml.regression.metrics")

# Orden estándar de targets
TARGETS = ['alto', 'ancho', 'grosor', 'peso']


def robust_r2_score(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    target_name: str = "unknown",
    verbose: bool = False
) -> float:
    """
    Calcula R² de forma robusta con validaciones exhaustivas.
    
    Args:
        y_true: Valores reales (desnormalizados)
        y_pred: Valores predichos (desnormalizados)
        target_name: Nombre del target para logging
        verbose: Si mostrar logs detallados
        
    Returns:
        R² score (puede ser negativo si el modelo es peor que la media)
    """
    # Validar que no estén vacíos
    if len(y_true) == 0 or len(y_pred) == 0:
        logger.warning(f"{target_name}: Arrays vacíos, R²=0")
        return 0.0
    
    # Validar dimensiones
    if y_true.shape != y_pred.shape:
        logger.error(
            f"{target_name}: Dimensiones no coinciden - "
            f"y_true.shape={y_true.shape}, y_pred.shape={y_pred.shape}"
        )
        # Intentar aplanar
        y_true = y_true.flatten()
        y_pred = y_pred.flatten()
        if y_true.shape != y_pred.shape:
            logger.error(f"{target_name}: No se pudieron igualar dimensiones")
            return 0.0
    
    # Aplanar para asegurar 1D
    y_true = y_true.flatten()
    y_pred = y_pred.flatten()
    
    # Filtrar NaN e Inf
    valid_mask = np.isfinite(y_true) & np.isfinite(y_pred)
    n_valid = np.sum(valid_mask)
    n_total = len(y_true)
    
    if n_valid == 0:
        logger.error(f"{target_name}: No hay valores válidos después de filtrar NaN/Inf")
        return 0.0
    
    if n_valid < n_total:
        logger.warning(
            f"{target_name}: {n_total - n_valid} valores NaN/Inf filtrados "
            f"({n_valid}/{n_total} válidos)"
        )
        y_true = y_true[valid_mask]
        y_pred = y_pred[valid_mask]
    
    # Validar que haya suficiente variación en targets
    y_true_mean = np.mean(y_true)
    y_true_std = np.std(y_true)
    
    if y_true_std < 1e-8:
        logger.warning(
            f"{target_name}: Desviación estándar de targets muy pequeña "
            f"({y_true_std:.2e}), R²=0"
        )
        return 0.0
    
    # Calcular R²
    ss_res = np.sum((y_true - y_pred) ** 2)  # Suma de cuadrados residual
    ss_tot = np.sum((y_true - y_true_mean) ** 2)  # Suma de cuadrados total
    
    if ss_tot < 1e-8:
        logger.warning(
            f"{target_name}: ss_tot muy pequeño ({ss_tot:.2e}), R²=0"
        )
        return 0.0
    
    r2 = 1.0 - (ss_res / ss_tot)
    
    # Validar R² razonable
    if r2 < -1000:
        logger.error(
            f"{target_name}: R² extremadamente negativo ({r2:.4f}). "
            f"Esto indica un problema serio:\n"
            f"  - Preds range: [{y_pred.min():.4f}, {y_pred.max():.4f}]\n"
            f"  - Targets range: [{y_true.min():.4f}, {y_true.max():.4f}]\n"
            f"  - Preds mean: {y_pred.mean():.4f}, std: {y_pred.std():.4f}\n"
            f"  - Targets mean: {y_true_mean:.4f}, std: {y_true_std:.4f}\n"
            f"  - ss_res: {ss_res:.4f}, ss_tot: {ss_tot:.4f}"
        )
    elif r2 < -100:
        logger.warning(
            f"{target_name}: R² muy negativo ({r2:.4f}). "
            f"Preds: [{y_pred.min():.2f}, {y_pred.max():.2f}], "
            f"Targets: [{y_true.min():.2f}, {y_true.max():.2f}]"
        )
    
    if verbose:
        logger.info(
            f"{target_name} R²: {r2:.4f} | "
            f"MAE: {np.mean(np.abs(y_true - y_pred)):.4f} | "
            f"RMSE: {np.sqrt(np.mean((y_true - y_pred) ** 2)):.4f} | "
            f"Preds: [{y_pred.min():.2f}, {y_pred.max():.2f}] | "
            f"Targets: [{y_true.min():.2f}, {y_true.max():.2f}]"
        )
    
    return float(r2)


def calculate_metrics_per_target(
    predictions: Dict[str, np.ndarray],
    targets: Dict[str, np.ndarray],
    target_names: Optional[List[str]] = None,
    verbose: bool = True
) -> Dict[str, Dict[str, float]]:
    """
    Calcula métricas (MAE, RMSE, R²) para cada target individualmente.
    
    Args:
        predictions: Diccionario de predicciones {target: array}
        targets: Diccionario de targets {target: array}
        target_names: Lista de targets a evaluar (default: TARGETS)
        verbose: Si mostrar logs detallados
        
    Returns:
        Diccionario con métricas por target
    """
    if target_names is None:
        target_names = TARGETS
    
    metrics = {}
    
    for target in target_names:
        if target not in predictions:
            logger.warning(f"Target '{target}' no encontrado en predicciones")
            continue
        
        if target not in targets:
            logger.warning(f"Target '{target}' no encontrado en targets")
            continue
        
        preds = predictions[target]
        targs = targets[target]
        
        # Validar dimensiones
        if preds.shape != targs.shape:
            logger.warning(
                f"{target}: Dimensiones no coinciden, aplanando... "
                f"preds.shape={preds.shape}, targs.shape={targs.shape}"
            )
            preds = preds.flatten()
            targs = targs.flatten()
        
        # Filtrar NaN/Inf
        valid_mask = np.isfinite(preds) & np.isfinite(targs)
        if not np.all(valid_mask):
            n_invalid = np.sum(~valid_mask)
            logger.warning(f"{target}: {n_invalid} valores NaN/Inf filtrados")
            preds = preds[valid_mask]
            targs = targs[valid_mask]
        
        if len(preds) == 0:
            logger.warning(f"{target}: No hay datos válidos después de filtrar")
            metrics[target] = {
                'mae': 0.0,
                'rmse': 0.0,
                'r2': 0.0,
                'n_samples': 0
            }
            continue
        
        # Calcular métricas
        mae = float(np.mean(np.abs(targs - preds)))
        rmse = float(np.sqrt(np.mean((targs - preds) ** 2)))
        r2 = robust_r2_score(targs, preds, target_name=target, verbose=verbose)
        
        metrics[target] = {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'n_samples': len(preds)
        }
        
        if verbose:
            logger.info(
                f"{target.upper()}: MAE={mae:.4f}, RMSE={rmse:.4f}, "
                f"R²={r2:.4f}, n={len(preds)}"
            )
    
    return metrics


def calculate_average_r2(
    metrics_per_target: Dict[str, Dict[str, float]]
) -> float:
    """
    Calcula el R² promedio sobre todos los targets.
    
    Args:
        metrics_per_target: Diccionario de métricas por target
        
    Returns:
        R² promedio
    """
    r2_values = [
        metrics['r2']
        for metrics in metrics_per_target.values()
        if 'r2' in metrics and metrics['r2'] is not None
    ]
    
    if len(r2_values) == 0:
        logger.warning("No hay valores de R² para calcular promedio")
        return 0.0
    
    avg_r2 = np.mean(r2_values)
    logger.info(f"R² promedio: {avg_r2:.4f} (sobre {len(r2_values)} targets)")
    
    return float(avg_r2)


def denormalize_and_calculate_metrics(
    predictions_norm: Dict[str, np.ndarray],
    targets_norm: Dict[str, np.ndarray],
    scalers,
    target_names: Optional[List[str]] = None,
    verbose: bool = True
) -> Tuple[Dict[str, Dict[str, float]], float]:
    """
    Desnormaliza predicciones y targets, luego calcula métricas.
    
    Args:
        predictions_norm: Predicciones normalizadas {target: array}
        targets_norm: Targets normalizados {target: array}
        scalers: Objeto CacaoScalers para desnormalizar
        target_names: Lista de targets (default: TARGETS)
        verbose: Si mostrar logs detallados
        
    Returns:
        Tupla (métricas por target, R² promedio)
    """
    if target_names is None:
        target_names = TARGETS
    
    # Desnormalizar
    if scalers is not None and hasattr(scalers, 'is_fitted') and scalers.is_fitted:
        try:
            predictions_denorm = scalers.inverse_transform(predictions_norm)
            targets_denorm = scalers.inverse_transform(targets_norm)
            
            if verbose:
                logger.info("Predicciones y targets desnormalizados correctamente")
        except Exception as e:
            logger.error(f"Error desnormalizando: {e}", exc_info=True)
            logger.warning("Usando valores normalizados (R² puede ser incorrecto)")
            predictions_denorm = predictions_norm
            targets_denorm = targets_norm
    else:
        logger.warning("Scalers no disponibles o no ajustados, usando valores normalizados")
        predictions_denorm = predictions_norm
        targets_denorm = targets_norm
    
    # Calcular métricas
    metrics = calculate_metrics_per_target(
        predictions_denorm,
        targets_denorm,
        target_names=target_names,
        verbose=verbose
    )
    
    # Calcular R² promedio
    avg_r2 = calculate_average_r2(metrics)
    
    return metrics, avg_r2


def validate_predictions_targets_alignment(
    predictions: Dict[str, np.ndarray],
    targets: Dict[str, np.ndarray],
    target_names: Optional[List[str]] = None
) -> bool:
    """
    Valida que predicciones y targets estén alineados correctamente.
    
    Args:
        predictions: Diccionario de predicciones
        targets: Diccionario de targets
        target_names: Lista de targets esperados
        
    Returns:
        True si están alineados, False si hay problemas
    """
    if target_names is None:
        target_names = TARGETS
    
    # Verificar que todos los targets estén presentes
    missing_preds = set(target_names) - set(predictions.keys())
    missing_targets = set(target_names) - set(targets.keys())
    
    if missing_preds:
        logger.error(f"Targets faltantes en predicciones: {missing_preds}")
        return False
    
    if missing_targets:
        logger.error(f"Targets faltantes en targets: {missing_targets}")
        return False
    
    # Verificar que las longitudes coincidan
    lengths = {}
    for target in target_names:
        pred_len = len(predictions[target].flatten())
        targ_len = len(targets[target].flatten())
        lengths[target] = (pred_len, targ_len)
        
        if pred_len != targ_len:
            logger.error(
                f"{target}: Longitudes no coinciden - "
                f"preds: {pred_len}, targets: {targ_len}"
            )
            return False
    
    if len(set(lengths.values())) > 1:
        logger.warning(
            f"Longitudes diferentes entre targets: {lengths}. "
            f"Esto puede indicar un problema de alineación."
        )
    
    return True

