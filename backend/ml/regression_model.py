"""
Modelo de regresión para predicción de peso de granos de cacao.

Este módulo contiene la clase WeightRegressionModel que utiliza algoritmos
de regresión de scikit-learn para predecir el peso de granos de cacao
basándose en sus características físicas (ancho, alto, grosor).
"""

import os
import logging
import numpy as np
import pandas as pd
from typing import Union, List, Tuple, Optional, Dict, Any
from pathlib import Path
import joblib
from datetime import datetime

# Imports de scikit-learn
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline

# Configurar Django si no está configurado
import django
if not django.apps.apps.ready:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from apps.images.models import CacaoImage
from .config import MODELS_DIR, get_config_value, EVALUATION_METRICS

# Configurar logging
logger = logging.getLogger('ml')


class WeightRegressionModel:
    """
    Clase principal para el modelo de regresión de peso de granos de cacao.
    
    Utiliza características físicas (width, height, thickness) para predecir
    el peso del grano usando algoritmos de regresión de scikit-learn.
    """
    
    SUPPORTED_ALGORITHMS = {
        'linear': LinearRegression,
        'ridge': Ridge,
        'lasso': Lasso,
        'elastic_net': ElasticNet,
        'random_forest': RandomForestRegressor,
        'gradient_boosting': GradientBoostingRegressor,
        'svr': SVR
    }
    
    def __init__(self, 
                 algorithm: str = 'linear',
                 use_polynomial_features: bool = False,
                 polynomial_degree: int = 2,
                 use_scaling: bool = True,
                 **model_params):
        """
        Inicializa el modelo de regresión.
        
        Args:
            algorithm (str): Algoritmo de regresión a usar
            use_polynomial_features (bool): Si usar características polinomiales
            polynomial_degree (int): Grado de las características polinomiales
            use_scaling (bool): Si usar escalado de características
            **model_params: Parámetros específicos del modelo
        """
        self.algorithm = algorithm
        self.use_polynomial_features = use_polynomial_features
        self.polynomial_degree = polynomial_degree
        self.use_scaling = use_scaling
        self.model_params = model_params
        
        # Componentes del pipeline
        self.scaler = StandardScaler() if use_scaling else None
        self.poly_features = PolynomialFeatures(
            degree=polynomial_degree, 
            include_bias=False
        ) if use_polynomial_features else None
        
        # Modelo principal
        self.model = self._create_model()
        
        # Pipeline completo
        self.pipeline = self._create_pipeline()
        
        # Métricas de entrenamiento
        self.training_metrics = {}
        self.feature_names = ['width', 'height', 'thickness']
        self.is_trained = False
        
        logger.info(f"WeightRegressionModel inicializado con algoritmo: {algorithm}")
    
    def _create_model(self):
        """
        Crea el modelo de regresión basado en el algoritmo especificado.
        
        Returns:
            Modelo de scikit-learn
        """
        if self.algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(f"Algoritmo no soportado: {self.algorithm}")
        
        model_class = self.SUPPORTED_ALGORITHMS[self.algorithm]
        
        # Parámetros por defecto para cada algoritmo
        default_params = {
            'linear': {},
            'ridge': {'alpha': 1.0},
            'lasso': {'alpha': 1.0},
            'elastic_net': {'alpha': 1.0, 'l1_ratio': 0.5},
            'random_forest': {'n_estimators': 100, 'random_state': 42},
            'gradient_boosting': {'n_estimators': 100, 'random_state': 42},
            'svr': {'kernel': 'rbf', 'C': 1.0}
        }
        
        # Combinar parámetros por defecto con los proporcionados
        params = default_params.get(self.algorithm, {})
        params.update(self.model_params)
        
        return model_class(**params)
    
    def _create_pipeline(self) -> Pipeline:
        """
        Crea el pipeline de procesamiento completo.
        
        Returns:
            Pipeline de scikit-learn
        """
        steps = []
        
        # Paso 1: Escalado (opcional)
        if self.scaler is not None:
            steps.append(('scaler', self.scaler))
        
        # Paso 2: Características polinomiales (opcional)
        if self.poly_features is not None:
            steps.append(('poly_features', self.poly_features))
        
        # Paso 3: Modelo de regresión
        steps.append(('regressor', self.model))
        
        return Pipeline(steps)
    
    def prepare_data(self, 
                    queryset: Optional[Any] = None,
                    min_samples: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara los datos desde la base de datos Django.
        
        Args:
            queryset: QuerySet de Django con objetos CacaoImage
            min_samples: Número mínimo de muestras requeridas
            
        Returns:
            Tuple[np.ndarray, np.ndarray]: X (características), y (peso)
        """
        if queryset is None:
            # Obtener todos los registros con datos completos
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
        
        # Convertir a DataFrame para facilitar el manejo
        data = []
        for obj in queryset:
            data.append({
                'width': float(obj.width),
                'height': float(obj.height),
                'thickness': float(obj.thickness),
                'weight': float(obj.weight)
            })
        
        if len(data) < min_samples:
            raise ValueError(f"Datos insuficientes: {len(data)} < {min_samples}")
        
        df = pd.DataFrame(data)
        
        # Características (X) y target (y)
        X = df[self.feature_names].values
        y = df['weight'].values
        
        logger.info(f"Datos preparados: {X.shape[0]} muestras, {X.shape[1]} características")
        
        return X, y
    
    def train(self, 
              X: np.ndarray, 
              y: np.ndarray,
              test_size: float = 0.2,
              random_state: int = 42,
              cross_validation: bool = True,
              cv_folds: int = 5) -> Dict[str, Any]:
        """
        Entrena el modelo de regresión.
        
        Args:
            X (np.ndarray): Características de entrada
            y (np.ndarray): Valores objetivo (peso)
            test_size (float): Proporción para conjunto de prueba
            random_state (int): Semilla para reproducibilidad
            cross_validation (bool): Si realizar validación cruzada
            cv_folds (int): Número de folds para CV
            
        Returns:
            Dict[str, Any]: Métricas de entrenamiento
        """
        logger.info("Iniciando entrenamiento del modelo de regresión")
        
        # Dividir datos en entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Entrenar el modelo
        self.pipeline.fit(X_train, y_train)
        
        # Predicciones
        y_train_pred = self.pipeline.predict(X_train)
        y_test_pred = self.pipeline.predict(X_test)
        
        # Calcular métricas
        metrics = {
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'train_metrics': self._calculate_metrics(y_train, y_train_pred),
            'test_metrics': self._calculate_metrics(y_test, y_test_pred),
            'algorithm': self.algorithm,
            'use_polynomial_features': self.use_polynomial_features,
            'use_scaling': self.use_scaling,
            'model_params': self.model_params
        }
        
        # Validación cruzada
        if cross_validation:
            cv_scores = cross_val_score(
                self.pipeline, X_train, y_train, 
                cv=cv_folds, scoring='r2'
            )
            metrics['cross_validation'] = {
                'mean_r2': float(np.mean(cv_scores)),
                'std_r2': float(np.std(cv_scores)),
                'scores': cv_scores.tolist()
            }
        
        # Guardar métricas y marcar como entrenado
        self.training_metrics = metrics
        self.is_trained = True
        
        logger.info(f"Entrenamiento completado. R² test: {metrics['test_metrics']['r2']:.4f}")
        
        return metrics
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calcula métricas de evaluación.
        
        Args:
            y_true (np.ndarray): Valores reales
            y_pred (np.ndarray): Valores predichos
            
        Returns:
            Dict[str, float]: Métricas calculadas
        """
        return {
            'mse': float(mean_squared_error(y_true, y_pred)),
            'rmse': float(np.sqrt(mean_squared_error(y_true, y_pred))),
            'mae': float(mean_absolute_error(y_true, y_pred)),
            'r2': float(r2_score(y_true, y_pred)),
            'mape': float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100)
        }
    
    def predict(self, 
                X: Union[np.ndarray, List[List[float]], Tuple[float, float, float]]) -> np.ndarray:
        """
        Realiza predicciones con el modelo entrenado.
        
        Args:
            X: Características de entrada (width, height, thickness)
            
        Returns:
            np.ndarray: Predicciones de peso
        """
        if not self.is_trained:
            raise ValueError("El modelo debe ser entrenado antes de hacer predicciones")
        
        # Convertir entrada a formato correcto
        if isinstance(X, (list, tuple)):
            if len(X) == 3 and isinstance(X[0], (int, float)):
                # Entrada única: (width, height, thickness)
                X = np.array([X])
            else:
                # Lista de muestras
                X = np.array(X)
        elif isinstance(X, np.ndarray):
            if X.ndim == 1:
                X = X.reshape(1, -1)
        
        # Validar dimensiones
        if X.shape[1] != 3:
            raise ValueError(f"Se esperan 3 características, recibido: {X.shape[1]}")
        
        # Realizar predicción
        predictions = self.pipeline.predict(X)
        
        return predictions
    
    def predict_single(self, width: float, height: float, thickness: float) -> float:
        """
        Predice el peso para un grano individual.
        
        Args:
            width (float): Ancho en mm
            height (float): Alto en mm
            thickness (float): Grosor en mm
            
        Returns:
            float: Peso predicho en gramos
        """
        prediction = self.predict([(width, height, thickness)])
        return float(prediction[0])
    
    def evaluate_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
        """
        Evalúa el modelo en un conjunto de datos.
        
        Args:
            X (np.ndarray): Características
            y (np.ndarray): Valores objetivo
            
        Returns:
            Dict[str, Any]: Métricas de evaluación
        """
        if not self.is_trained:
            raise ValueError("El modelo debe ser entrenado antes de evaluar")
        
        y_pred = self.predict(X)
        metrics = self._calculate_metrics(y, y_pred)
        
        # Análisis de residuos
        residuals = y - y_pred
        metrics.update({
            'residuals_mean': float(np.mean(residuals)),
            'residuals_std': float(np.std(residuals)),
            'residuals_range': {
                'min': float(np.min(residuals)),
                'max': float(np.max(residuals))
            }
        })
        
        return metrics
    
    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Obtiene la importancia de las características (si está disponible).
        
        Returns:
            Optional[Dict[str, float]]: Importancia de características
        """
        if not self.is_trained:
            return None
        
        model = self.pipeline.named_steps['regressor']
        
        if hasattr(model, 'feature_importances_'):
            # Para Random Forest, Gradient Boosting
            importances = model.feature_importances_
            
            # Ajustar nombres si se usan características polinomiales
            if self.use_polynomial_features:
                poly_feature_names = self.poly_features.get_feature_names_out(self.feature_names)
                feature_names = poly_feature_names
            else:
                feature_names = self.feature_names
            
            return dict(zip(feature_names, importances))
        
        elif hasattr(model, 'coef_'):
            # Para modelos lineales
            coefficients = model.coef_
            
            if self.use_polynomial_features:
                poly_feature_names = self.poly_features.get_feature_names_out(self.feature_names)
                feature_names = poly_feature_names
            else:
                feature_names = self.feature_names
            
            return dict(zip(feature_names, np.abs(coefficients)))
        
        return None
    
    def save_model(self, file_path: Union[str, Path]):
        """
        Guarda el modelo entrenado en un archivo.
        
        Args:
            file_path (Union[str, Path]): Ruta del archivo
        """
        if not self.is_trained:
            raise ValueError("El modelo debe ser entrenado antes de guardar")
        
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Datos a guardar
        model_data = {
            'pipeline': self.pipeline,
            'algorithm': self.algorithm,
            'use_polynomial_features': self.use_polynomial_features,
            'polynomial_degree': self.polynomial_degree,
            'use_scaling': self.use_scaling,
            'model_params': self.model_params,
            'training_metrics': self.training_metrics,
            'feature_names': self.feature_names,
            'saved_at': datetime.now().isoformat(),
            'version': '1.0.0'
        }
        
        # Guardar usando joblib
        joblib.dump(model_data, file_path)
        logger.info(f"Modelo guardado en: {file_path}")
    
    @classmethod
    def load_model(cls, file_path: Union[str, Path]) -> 'WeightRegressionModel':
        """
        Carga un modelo entrenado desde archivo.
        
        Args:
            file_path (Union[str, Path]): Ruta del archivo
            
        Returns:
            WeightRegressionModel: Modelo cargado
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Archivo de modelo no encontrado: {file_path}")
        
        # Cargar datos del modelo
        model_data = joblib.load(file_path)
        
        # Crear instancia
        instance = cls(
            algorithm=model_data['algorithm'],
            use_polynomial_features=model_data['use_polynomial_features'],
            polynomial_degree=model_data.get('polynomial_degree', 2),
            use_scaling=model_data['use_scaling'],
            **model_data['model_params']
        )
        
        # Restaurar pipeline entrenado
        instance.pipeline = model_data['pipeline']
        instance.training_metrics = model_data['training_metrics']
        instance.feature_names = model_data['feature_names']
        instance.is_trained = True
        
        logger.info(f"Modelo cargado desde: {file_path}")
        
        return instance
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información completa del modelo.
        
        Returns:
            Dict[str, Any]: Información del modelo
        """
        info = {
            'algorithm': self.algorithm,
            'use_polynomial_features': self.use_polynomial_features,
            'polynomial_degree': self.polynomial_degree,
            'use_scaling': self.use_scaling,
            'model_params': self.model_params,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        if self.is_trained:
            info['training_metrics'] = self.training_metrics
            
            # Información del pipeline
            info['pipeline_steps'] = [step[0] for step in self.pipeline.steps]
            
            # Importancia de características
            feature_importance = self.get_feature_importance()
            if feature_importance:
                info['feature_importance'] = feature_importance
        
        return info


def create_weight_regression_model(algorithm: str = 'linear', **kwargs) -> WeightRegressionModel:
    """
    Función de conveniencia para crear un modelo de regresión.
    
    Args:
        algorithm (str): Algoritmo de regresión
        **kwargs: Argumentos adicionales
        
    Returns:
        WeightRegressionModel: Instancia del modelo
    """
    return WeightRegressionModel(algorithm=algorithm, **kwargs)


def load_weight_regression_model(model_name: str = 'weight_regression') -> WeightRegressionModel:
    """
    Carga el modelo de regresión desde el directorio de modelos.
    
    Args:
        model_name (str): Nombre del modelo
        
    Returns:
        WeightRegressionModel: Modelo cargado
    """
    model_path = MODELS_DIR / f"{model_name}.pkl"
    return WeightRegressionModel.load_model(model_path)


if __name__ == "__main__":
    # Ejemplo de uso
    print("Creando modelo de regresión de peso...")
    
    # Crear modelo
    model = create_weight_regression_model(
        algorithm='linear',
        use_polynomial_features=True,
        polynomial_degree=2
    )
    
    print(f"Modelo creado: {model.algorithm}")
    print(f"Información del modelo: {model.get_model_info()}")
    
    try:
        # Preparar datos
        X, y = model.prepare_data()
        print(f"Datos preparados: {X.shape[0]} muestras")
        
        # Entrenar modelo
        metrics = model.train(X, y)
        print(f"Entrenamiento completado. R²: {metrics['test_metrics']['r2']:.4f}")
        
        # Ejemplo de predicción
        prediction = model.predict_single(12.5, 8.3, 4.2)
        print(f"Predicción ejemplo: {prediction:.3f}g")
        
    except ValueError as e:
        print(f"Error: {e}")
        print("El modelo puede entrenarse cuando haya datos suficientes disponibles.")

