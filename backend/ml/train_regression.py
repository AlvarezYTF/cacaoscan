"""
Script de entrenamiento para el modelo de regresión de peso de granos de cacao.

Este script entrena modelos de regresión de scikit-learn para predecir el peso
de granos de cacao basándose en sus características físicas (width, height, thickness).
Incluye experimentación con múltiples algoritmos y optimización de hiperparámetros.
"""

import os
import sys
import logging
import argparse
import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configurar Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.images.models import CacaoImage
from .regression_model import WeightRegressionModel, create_weight_regression_model
from .config import MODELS_DIR, TRAINING_CONFIG, get_training_config_for_dataset_size
from .ml_utils_extended import dataset_validator, performance_profiler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('regression_training.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ml')


class RegressionTrainer:
    """
    Entrenador principal para modelos de regresión de peso.
    
    Maneja la experimentación con múltiples algoritmos, optimización de
    hiperparámetros, evaluación y guardado de modelos.
    """
    
    def __init__(self, output_dir: str = None):
        """
        Inicializa el entrenador de regresión.
        
        Args:
            output_dir (str): Directorio para guardar resultados
        """
        self.output_dir = Path(output_dir) if output_dir else MODELS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar directorio de experimentos
        self.experiments_dir = self.output_dir / 'regression_experiments'
        self.experiments_dir.mkdir(exist_ok=True)
        
        # Almacenar resultados
        self.experiment_results = {}
        self.best_model = None
        self.best_score = float('-inf')
        
        logger.info(f"RegressionTrainer inicializado. Output: {self.output_dir}")
    
    def load_and_prepare_data(self, min_samples: int = 20) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
        """
        Carga y prepara los datos desde la base de datos.
        
        Args:
            min_samples (int): Número mínimo de muestras requeridas
            
        Returns:
            Tuple: X, y, DataFrame original
        """
        logger.info("Cargando datos desde la base de datos...")
        
        # Obtener datos desde Django ORM
        queryset = CacaoImage.objects.filter(
            width__isnull=False,
            height__isnull=False,
            thickness__isnull=False,
            weight__isnull=False
        ).exclude(
            width=0,
            height=0,
            thickness=0,
            weight=0
        )
        
        # Convertir a DataFrame
        data = []
        for obj in queryset:
            data.append({
                'id': obj.id,
                'width': float(obj.width),
                'height': float(obj.height),
                'thickness': float(obj.thickness),
                'weight': float(obj.weight),
                'batch_number': obj.batch_number,
                'quality': obj.predicted_quality,
                'created_at': obj.created_at
            })
        
        if len(data) < min_samples:
            raise ValueError(f"Datos insuficientes: {len(data)} < {min_samples}")
        
        df = pd.DataFrame(data)
        
        # Preparar X (características) y y (target)
        feature_columns = ['width', 'height', 'thickness']
        X = df[feature_columns].values
        y = df['weight'].values
        
        logger.info(f"Datos cargados: {len(df)} muestras")
        
        # Mostrar estadísticas básicas
        self._log_data_statistics(df)
        
        return X, y, df
    
    def _log_data_statistics(self, df: pd.DataFrame):
        """
        Muestra estadísticas descriptivas de los datos.
        
        Args:
            df (pd.DataFrame): DataFrame con los datos
        """
        logger.info("Estadísticas de los datos:")
        for col in ['width', 'height', 'thickness', 'weight']:
            stats = df[col].describe()
            logger.info(f"  {col}: mean={stats['mean']:.3f}, std={stats['std']:.3f}, "
                       f"min={stats['min']:.3f}, max={stats['max']:.3f}")
    
    def validate_data(self, df: pd.DataFrame) -> Dict:
        """
        Valida la calidad de los datos.
        
        Args:
            df (pd.DataFrame): DataFrame con los datos
            
        Returns:
            Dict: Resultado de la validación
        """
        logger.info("Validando calidad de los datos...")
        
        validation_results = {
            'total_samples': len(df),
            'missing_values': df.isnull().sum().to_dict(),
            'outliers': {},
            'correlations': {},
            'data_quality_score': 1.0
        }
        
        # Detectar outliers usando IQR
        numeric_cols = ['width', 'height', 'thickness', 'weight']
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
            validation_results['outliers'][col] = {
                'count': len(outliers),
                'percentage': len(outliers) / len(df) * 100,
                'bounds': {'lower': lower_bound, 'upper': upper_bound}
            }
        
        # Calcular correlaciones
        corr_matrix = df[numeric_cols].corr()
        validation_results['correlations'] = corr_matrix.to_dict()
        
        # Correlación peso con otras características
        weight_correlations = corr_matrix['weight'].drop('weight').to_dict()
        logger.info("Correlaciones con peso:")
        for feature, corr in weight_correlations.items():
            logger.info(f"  {feature}: {corr:.3f}")
        
        return validation_results
    
    def experiment_with_algorithms(self, 
                                 X: np.ndarray, 
                                 y: np.ndarray,
                                 algorithms: List[str] = None,
                                 test_size: float = 0.2) -> Dict:
        """
        Experimenta con múltiples algoritmos de regresión.
        
        Args:
            X (np.ndarray): Características
            y (np.ndarray): Target
            algorithms (List[str]): Algoritmos a probar
            test_size (float): Proporción del conjunto de prueba
            
        Returns:
            Dict: Resultados de todos los experimentos
        """
        if algorithms is None:
            algorithms = ['linear', 'ridge', 'lasso', 'random_forest', 'gradient_boosting']
        
        logger.info(f"Experimentando con algoritmos: {algorithms}")
        
        results = {}
        
        for algorithm in algorithms:
            logger.info(f"Entrenando modelo: {algorithm}")
            
            try:
                # Crear y entrenar modelo
                model = create_weight_regression_model(
                    algorithm=algorithm,
                    use_polynomial_features=(algorithm in ['linear', 'ridge', 'lasso']),
                    use_scaling=True
                )
                
                # Entrenar con profiling de rendimiento
                @performance_profiler.profile_function(f"train_{algorithm}")
                def train_model():
                    return model.train(X, y, test_size=test_size)
                
                metrics = train_model()
                
                # Guardar resultados
                results[algorithm] = {
                    'model': model,
                    'metrics': metrics,
                    'test_r2': metrics['test_metrics']['r2'],
                    'test_rmse': metrics['test_metrics']['rmse'],
                    'test_mae': metrics['test_metrics']['mae']
                }
                
                logger.info(f"  {algorithm} - R²: {metrics['test_metrics']['r2']:.4f}, "
                           f"RMSE: {metrics['test_metrics']['rmse']:.4f}")
                
                # Actualizar mejor modelo
                test_r2 = metrics['test_metrics']['r2']
                if test_r2 > self.best_score:
                    self.best_score = test_r2
                    self.best_model = model
                    logger.info(f"  Nuevo mejor modelo: {algorithm} (R² = {test_r2:.4f})")
                
            except Exception as e:
                logger.error(f"Error entrenando {algorithm}: {e}")
                results[algorithm] = {'error': str(e)}
        
        self.experiment_results = results
        return results
    
    def hyperparameter_optimization(self, 
                                   algorithm: str,
                                   X: np.ndarray,
                                   y: np.ndarray,
                                   param_grid: Dict = None) -> Dict:
        """
        Optimiza hiperparámetros para un algoritmo específico.
        
        Args:
            algorithm (str): Algoritmo a optimizar
            X (np.ndarray): Características
            y (np.ndarray): Target
            param_grid (Dict): Grid de parámetros
            
        Returns:
            Dict: Resultado de la optimización
        """
        from sklearn.model_selection import GridSearchCV
        from sklearn.metrics import make_scorer
        
        logger.info(f"Optimizando hiperparámetros para: {algorithm}")
        
        # Grid de parámetros por defecto
        if param_grid is None:
            param_grids = {
                'ridge': {
                    'regressor__alpha': [0.1, 1.0, 10.0, 100.0]
                },
                'lasso': {
                    'regressor__alpha': [0.01, 0.1, 1.0, 10.0]
                },
                'random_forest': {
                    'regressor__n_estimators': [50, 100, 200],
                    'regressor__max_depth': [None, 10, 20],
                    'regressor__min_samples_split': [2, 5, 10]
                },
                'gradient_boosting': {
                    'regressor__n_estimators': [50, 100, 200],
                    'regressor__learning_rate': [0.01, 0.1, 0.2],
                    'regressor__max_depth': [3, 5, 7]
                }
            }
            param_grid = param_grids.get(algorithm, {})
        
        if not param_grid:
            logger.warning(f"No hay grid de parámetros para {algorithm}")
            return {}
        
        # Crear modelo base
        base_model = create_weight_regression_model(
            algorithm=algorithm,
            use_polynomial_features=(algorithm in ['linear', 'ridge', 'lasso']),
            use_scaling=True
        )
        
        # Grid search
        grid_search = GridSearchCV(
            base_model.pipeline,
            param_grid,
            cv=5,
            scoring='r2',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X, y)
        
        # Resultados
        optimization_results = {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'best_estimator': grid_search.best_estimator_,
            'cv_results': grid_search.cv_results_
        }
        
        logger.info(f"  Mejores parámetros: {grid_search.best_params_}")
        logger.info(f"  Mejor puntuación CV: {grid_search.best_score_:.4f}")
        
        return optimization_results
    
    def evaluate_final_model(self, 
                           model: WeightRegressionModel,
                           X: np.ndarray,
                           y: np.ndarray) -> Dict:
        """
        Evaluación completa del modelo final.
        
        Args:
            model (WeightRegressionModel): Modelo a evaluar
            X (np.ndarray): Características
            y (np.ndarray): Target
            
        Returns:
            Dict: Resultados de evaluación
        """
        logger.info("Evaluación completa del modelo final...")
        
        # Métricas básicas
        evaluation = model.evaluate_model(X, y)
        
        # Predicciones
        y_pred = model.predict(X)
        
        # Análisis de residuos detallado
        residuals = y - y_pred
        evaluation.update({
            'residuals_analysis': {
                'mean': float(np.mean(residuals)),
                'std': float(np.std(residuals)),
                'skewness': float(self._calculate_skewness(residuals)),
                'kurtosis': float(self._calculate_kurtosis(residuals)),
                'normality_test': self._test_residuals_normality(residuals)
            }
        })
        
        # Intervalos de confianza para predicciones
        evaluation['prediction_intervals'] = self._calculate_prediction_intervals(y, y_pred)
        
        # Análisis de características
        feature_importance = model.get_feature_importance()
        if feature_importance:
            evaluation['feature_importance'] = feature_importance
        
        return evaluation
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calcula la asimetría de los datos."""
        n = len(data)
        mean = np.mean(data)
        std = np.std(data)
        return (1/n) * np.sum(((data - mean) / std) ** 3)
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calcula la curtosis de los datos."""
        n = len(data)
        mean = np.mean(data)
        std = np.std(data)
        return (1/n) * np.sum(((data - mean) / std) ** 4) - 3
    
    def _test_residuals_normality(self, residuals: np.ndarray) -> Dict:
        """Test de normalidad de residuos."""
        try:
            from scipy import stats
            statistic, p_value = stats.shapiro(residuals[:5000])  # Límite para Shapiro-Wilk
            return {
                'test': 'shapiro-wilk',
                'statistic': float(statistic),
                'p_value': float(p_value),
                'is_normal': p_value > 0.05
            }
        except ImportError:
            return {'test': 'not_available', 'reason': 'scipy not installed'}
    
    def _calculate_prediction_intervals(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """Calcula intervalos de confianza para predicciones."""
        residuals = y_true - y_pred
        rmse = np.sqrt(np.mean(residuals ** 2))
        
        # Intervalos de confianza aproximados (asumiendo distribución normal)
        confidence_levels = [0.68, 0.95, 0.99]
        intervals = {}
        
        for level in confidence_levels:
            z_score = {0.68: 1.0, 0.95: 1.96, 0.99: 2.576}[level]
            margin = z_score * rmse
            
            intervals[f'{int(level*100)}%'] = {
                'margin': float(margin),
                'lower_bound': (y_pred - margin).tolist(),
                'upper_bound': (y_pred + margin).tolist()
            }
        
        return intervals
    
    def save_results(self, 
                    model: WeightRegressionModel,
                    experiment_results: Dict,
                    evaluation: Dict,
                    validation_results: Dict):
        """
        Guarda todos los resultados del entrenamiento.
        
        Args:
            model: Modelo final
            experiment_results: Resultados de experimentos
            evaluation: Evaluación del modelo
            validation_results: Validación de datos
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar modelo principal
        model_path = self.output_dir / 'weight_regression.pkl'
        model.save_model(model_path)
        logger.info(f"Modelo guardado en: {model_path}")
        
        # Guardar modelo con timestamp
        timestamped_model_path = self.experiments_dir / f'weight_regression_{timestamp}.pkl'
        model.save_model(timestamped_model_path)
        
        # Preparar resumen de resultados
        results_summary = {
            'timestamp': timestamp,
            'best_algorithm': model.algorithm,
            'final_metrics': evaluation,
            'data_validation': validation_results,
            'model_info': model.get_model_info(),
            'performance_stats': performance_profiler.get_stats()
        }
        
        # Agregar resultados de experimentos (sin modelos para evitar archivos grandes)
        experiment_summary = {}
        for alg, result in experiment_results.items():
            if 'model' in result:
                experiment_summary[alg] = {
                    k: v for k, v in result.items() if k != 'model'
                }
            else:
                experiment_summary[alg] = result
        
        results_summary['experiment_results'] = experiment_summary
        
        # Guardar resumen en JSON
        results_path = self.experiments_dir / f'training_results_{timestamp}.json'
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(results_summary, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"Resultados guardados en: {results_path}")
        
        # Crear visualizaciones
        self._create_visualizations(model, evaluation, timestamp)
    
    def _create_visualizations(self, 
                              model: WeightRegressionModel,
                              evaluation: Dict,
                              timestamp: str):
        """
        Crea visualizaciones de los resultados.
        
        Args:
            model: Modelo entrenado
            evaluation: Evaluación del modelo  
            timestamp: Timestamp para nombres de archivo
        """
        try:
            # Configurar matplotlib
            plt.style.use('default')
            fig_dir = self.experiments_dir / 'figures'
            fig_dir.mkdir(exist_ok=True)
            
            # Gráfico de importancia de características
            feature_importance = model.get_feature_importance()
            if feature_importance:
                plt.figure(figsize=(10, 6))
                features = list(feature_importance.keys())
                importances = list(feature_importance.values())
                
                plt.barh(features, importances)
                plt.title('Importancia de Características')
                plt.xlabel('Importancia')
                plt.tight_layout()
                plt.savefig(fig_dir / f'feature_importance_{timestamp}.png', dpi=300, bbox_inches='tight')
                plt.close()
            
            logger.info(f"Visualizaciones guardadas en: {fig_dir}")
            
        except ImportError:
            logger.warning("Matplotlib no disponible para crear visualizaciones")
        except Exception as e:
            logger.error(f"Error creando visualizaciones: {e}")


def main():
    """Función principal del script de entrenamiento."""
    parser = argparse.ArgumentParser(description='Entrenar modelo de regresión de peso')
    parser.add_argument('--algorithm', type=str, default='auto', 
                       help='Algoritmo específico o "auto" para experimentar')
    parser.add_argument('--optimize', action='store_true',
                       help='Realizar optimización de hiperparámetros')
    parser.add_argument('--min-samples', type=int, default=20,
                       help='Número mínimo de muestras requeridas')
    parser.add_argument('--test-size', type=float, default=0.2,
                       help='Proporción del conjunto de prueba')
    parser.add_argument('--output-dir', type=str, default=None,
                       help='Directorio de salida')
    
    args = parser.parse_args()
    
    # Crear entrenador
    trainer = RegressionTrainer(output_dir=args.output_dir)
    
    try:
        # Cargar y validar datos
        X, y, df = trainer.load_and_prepare_data(min_samples=args.min_samples)
        validation_results = trainer.validate_data(df)
        
        if args.algorithm == 'auto':
            # Experimentar con múltiples algoritmos
            experiment_results = trainer.experiment_with_algorithms(
                X, y, test_size=args.test_size
            )
            
            if trainer.best_model is None:
                logger.error("No se pudo entrenar ningún modelo exitosamente")
                return
            
            final_model = trainer.best_model
            
        else:
            # Entrenar algoritmo específico
            logger.info(f"Entrenando algoritmo específico: {args.algorithm}")
            final_model = create_weight_regression_model(
                algorithm=args.algorithm,
                use_polynomial_features=(args.algorithm in ['linear', 'ridge', 'lasso']),
                use_scaling=True
            )
            
            metrics = final_model.train(X, y, test_size=args.test_size)
            experiment_results = {args.algorithm: {'model': final_model, 'metrics': metrics}}
        
        # Optimización de hiperparámetros si se solicita
        if args.optimize and final_model:
            logger.info("Iniciando optimización de hiperparámetros...")
            optimization_results = trainer.hyperparameter_optimization(
                final_model.algorithm, X, y
            )
            
            if optimization_results and 'best_estimator' in optimization_results:
                # Crear modelo optimizado
                optimized_model = create_weight_regression_model(
                    algorithm=final_model.algorithm,
                    use_polynomial_features=final_model.use_polynomial_features,
                    use_scaling=final_model.use_scaling
                )
                optimized_model.pipeline = optimization_results['best_estimator']
                optimized_model.is_trained = True
                final_model = optimized_model
        
        # Evaluación final
        evaluation = trainer.evaluate_final_model(final_model, X, y)
        
        # Guardar resultados
        trainer.save_results(final_model, experiment_results, evaluation, validation_results)
        
        # Resumen final
        logger.info("=" * 60)
        logger.info("ENTRENAMIENTO COMPLETADO")
        logger.info("=" * 60)
        logger.info(f"Mejor algoritmo: {final_model.algorithm}")
        logger.info(f"R² final: {evaluation['r2']:.4f}")
        logger.info(f"RMSE final: {evaluation['rmse']:.4f}")
        logger.info(f"MAE final: {evaluation['mae']:.4f}")
        
        if 'feature_importance' in evaluation:
            logger.info("Importancia de características:")
            for feature, importance in evaluation['feature_importance'].items():
                logger.info(f"  {feature}: {importance:.4f}")
        
        logger.info("Modelo guardado exitosamente!")
        
    except ValueError as e:
        logger.error(f"Error de datos: {e}")
        logger.info("Creando modelo placeholder...")
        create_placeholder_model()
    except Exception as e:
        logger.error(f"Error durante el entrenamiento: {e}")
        raise


def create_placeholder_model():
    """Crea un modelo placeholder cuando no hay datos suficientes."""
    logger.info("Creando modelo placeholder...")
    
    # Crear modelo con datos sintéticos
    model = create_weight_regression_model(algorithm='linear')
    
    # Datos sintéticos básicos
    np.random.seed(42)
    X_synthetic = np.random.uniform(low=[8, 6, 3], high=[15, 12, 6], size=(50, 3))
    
    # Relación aproximada: peso ≈ volumen * densidad
    # Aproximar volumen como elipsoide: V = (4/3) * π * a * b * c
    volumes = (4/3) * np.pi * (X_synthetic[:, 0]/2) * (X_synthetic[:, 1]/2) * (X_synthetic[:, 2]/2)
    densities = np.random.uniform(0.8, 1.2, size=50)  # Densidad aproximada del cacao
    y_synthetic = volumes * densities + np.random.normal(0, 0.1, size=50)
    
    # Entrenar con datos sintéticos
    model.train(X_synthetic, y_synthetic)
    
    # Guardar modelo placeholder
    placeholder_path = MODELS_DIR / 'weight_regression.pkl'
    model.save_model(placeholder_path)
    
    logger.info(f"Modelo placeholder guardado en: {placeholder_path}")
    logger.info("El modelo puede reentrenarse cuando haya datos reales disponibles.")


if __name__ == "__main__":
    main()

