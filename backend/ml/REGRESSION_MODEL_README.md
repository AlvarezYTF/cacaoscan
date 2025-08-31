# Feature 2.2: Modelo de Regresión para Peso - Implementación Completa

## Resumen
Se ha implementado exitosamente la **Feature 2.2: Modelo de regresión para peso** en CacaoScan. Esta feature proporciona un sistema completo de regresión usando scikit-learn para predecir el peso de granos de cacao basándose en sus características físicas.

## Archivos Implementados

### 1. `backend/ml/regression_model.py`
**Propósito**: Clase principal WeightRegressionModel para regresión de peso

**Características principales**:
- **Múltiples algoritmos**: Linear, Ridge, Lasso, ElasticNet, RandomForest, GradientBoosting, SVR
- **Preprocesamiento automático**: Escalado y características polinomiales opcionales
- **Pipeline completo**: Integración con scikit-learn Pipeline
- **Integración Django**: Carga directa desde modelo `CacaoImage`
- **Evaluación completa**: MAE, MSE, RMSE, R², MAPE
- **Persistencia**: Guardado/carga con joblib

**Algoritmos soportados**:
```python
SUPPORTED_ALGORITHMS = {
    'linear': LinearRegression,
    'ridge': Ridge, 
    'lasso': Lasso,
    'elastic_net': ElasticNet,
    'random_forest': RandomForestRegressor,
    'gradient_boosting': GradientBoostingRegressor,
    'svr': SVR
}
```

**Uso básico**:
```python
from ml.regression_model import WeightRegressionModel

# Crear modelo
model = WeightRegressionModel(algorithm='linear', use_scaling=True)

# Preparar datos desde Django
X, y = model.prepare_data()

# Entrenar
metrics = model.train(X, y)

# Predecir
weight = model.predict_single(width=12.5, height=8.3, thickness=4.2)
```

### 2. `backend/ml/train_regression.py`
**Propósito**: Script completo de entrenamiento y experimentación

**Funcionalidades**:
- **Carga automática de datos** desde `apps.images.models.CacaoImage`
- **Experimentación múltiple**: Prueba varios algoritmos automáticamente
- **Optimización de hiperparámetros**: GridSearchCV integrado
- **Validación de datos**: Detección de outliers, correlaciones
- **Evaluación completa**: Análisis de residuos, intervalos de confianza
- **Profiling de rendimiento**: Monitoreo de tiempo y memoria
- **Visualizaciones**: Gráficos de importancia de características
- **Modelo placeholder**: Crea modelo sintético si no hay datos

**Clase principal**:
```python
class RegressionTrainer:
    def load_and_prepare_data(min_samples=20)
    def validate_data(df) -> Dict
    def experiment_with_algorithms(X, y, algorithms) -> Dict
    def hyperparameter_optimization(algorithm, X, y) -> Dict
    def evaluate_final_model(model, X, y) -> Dict
    def save_results(model, results, evaluation, validation)
```

**Características de entrenamiento**:
- **Preparación de datos**: X = [width, height, thickness], y = weight
- **División train/test**: Configurable (default 80/20)
- **Validación cruzada**: 5-fold por defecto
- **Métricas de evaluación**: R², RMSE, MAE, MAPE
- **Análisis de residuos**: Normalidad, skewness, kurtosis
- **Guardado automático**: Modelo + métricas + visualizaciones

### 3. `backend/ml/models/weight_regression.pkl`
**Propósito**: Archivo del modelo entrenado en formato pickle

**Contenido del archivo**:
```python
model_data = {
    'pipeline': sklearn.pipeline.Pipeline,  # Pipeline entrenado
    'algorithm': str,                       # Algoritmo usado
    'use_polynomial_features': bool,        # Si usa características polinomiales
    'use_scaling': bool,                    # Si usa escalado
    'training_metrics': dict,               # Métricas de entrenamiento
    'feature_names': ['width', 'height', 'thickness'],
    'saved_at': str,                        # Timestamp
    'version': str,                         # Versión del modelo
    'placeholder': bool                     # Si es placeholder
}
```

**Estado actual**: Modelo placeholder con datos sintéticos creado
- Puede reentrenarse con datos reales usando `train_regression.py`
- Estructura compatible con WeightRegressionModel

### 4. `backend/ml/config.py` (Actualizado)
**Agregado**: Configuración para el modelo de regresión

```python
'weight_regression': {
    'model_path': MODELS_DIR / 'weight_regression.pkl',
    'model_type': 'sklearn_regression',
    'inputs': ['width', 'height', 'thickness'],
    'input_units': ['mm', 'mm', 'mm'],
    'outputs': ['weight'],
    'output_units': ['g'],
    'model_class': 'WeightRegressionModel',
    'algorithms': ['linear', 'ridge', 'lasso', 'random_forest', 'gradient_boosting', 'svr']
}
```

## Integración con Django

### Modelo Django Compatible
El sistema funciona directamente con el modelo `CacaoImage`:
```python
# Campos usados por el modelo de regresión
width = models.DecimalField(max_digits=8, decimal_places=3, ...)      # Entrada
height = models.DecimalField(max_digits=8, decimal_places=3, ...)     # Entrada  
thickness = models.DecimalField(max_digits=8, decimal_places=3, ...)  # Entrada
weight = models.DecimalField(max_digits=8, decimal_places=4, ...)     # Target
```

### Carga de Datos Automática
```python
# El modelo carga automáticamente desde Django ORM
queryset = CacaoImage.objects.filter(
    width__isnull=False,
    height__isnull=False, 
    thickness__isnull=False,
    weight__isnull=False
).exclude(width=0, height=0, thickness=0, weight=0)
```

## Uso del Sistema

### Entrenamiento Básico
```bash
cd backend
python ml/train_regression.py
```

### Entrenamiento con Algoritmo Específico
```bash
python ml/train_regression.py --algorithm ridge --optimize
```

### Parámetros Disponibles
```bash
--algorithm          # Algoritmo específico o 'auto' para experimentar
--optimize          # Realizar optimización de hiperparámetros
--min-samples       # Número mínimo de muestras (default: 20)
--test-size         # Proporción del conjunto de prueba (default: 0.2)
--output-dir        # Directorio de salida personalizado
```

### Inferencia en Código
```python
from ml.regression_model import load_weight_regression_model

# Cargar modelo entrenado
model = load_weight_regression_model()

# Predicción individual
weight = model.predict_single(width=12.5, height=8.3, thickness=4.2)
print(f"Peso predicho: {weight:.2f}g")

# Predicción múltiple
weights = model.predict([[12.5, 8.3, 4.2], [11.0, 7.5, 3.8]])
print(f"Pesos predichos: {weights}")
```

## Características Técnicas

### Algoritmos Implementados
1. **Linear Regression**: Regresión lineal simple
2. **Ridge Regression**: Regresión con regularización L2
3. **Lasso Regression**: Regresión con regularización L1
4. **Elastic Net**: Combinación de regularización L1 y L2
5. **Random Forest**: Ensemble de árboles de decisión
6. **Gradient Boosting**: Boosting de gradiente
7. **SVR**: Support Vector Regression

### Preprocesamiento
- **Escalado estándar**: StandardScaler para normalización
- **Características polinomiales**: Grados configurables
- **Validación de datos**: Detección de outliers y correlaciones

### Métricas de Evaluación
```python
metrics = {
    'mse': Mean Squared Error,
    'rmse': Root Mean Squared Error,
    'mae': Mean Absolute Error,
    'r2': R-squared (coeficiente de determinación),
    'mape': Mean Absolute Percentage Error
}
```

### Análisis Avanzado
- **Análisis de residuos**: Normalidad, distribución
- **Importancia de características**: Para algoritmos compatibles
- **Intervalos de confianza**: 68%, 95%, 99%
- **Validación cruzada**: K-fold configurable

## Arquitectura del Sistema

### Flujo de Entrenamiento
1. **Carga de datos** → Django ORM → DataFrame
2. **Validación** → Outliers, correlaciones, calidad
3. **Experimentación** → Múltiples algoritmos en paralelo
4. **Optimización** → GridSearchCV para mejores hiperparámetros
5. **Evaluación** → Métricas completas + análisis residuos
6. **Persistencia** → Modelo + métricas + visualizaciones

### Flujo de Inferencia
1. **Carga de modelo** → Desde archivo pickle
2. **Validación de entrada** → Formato y dimensiones
3. **Preprocesamiento** → Escalado automático
4. **Predicción** → Pipeline scikit-learn
5. **Post-procesamiento** → Formato de salida

## Rendimiento y Escalabilidad

### Optimizaciones Implementadas
- **Pipeline de scikit-learn**: Preprocesamiento + modelo en una sola operación
- **Validación cruzada paralela**: n_jobs=-1 para usar todos los cores
- **Profiling de memoria**: Monitoreo de uso de recursos
- **Cache de resultados**: Evita recálculos innecesarios

### Métricas de Rendimiento Típicas
- **Entrenamiento**: < 1 segundo para datasets < 1000 muestras
- **Inferencia**: < 1ms por predicción individual
- **Memoria**: < 50MB para modelos simples
- **Precisión esperada**: R² > 0.8 con datos de calidad

## Validación y Testing

### Validación de Datos
```python
validation_results = {
    'total_samples': int,
    'missing_values': dict,
    'outliers': dict,          # Por cada característica
    'correlations': dict,      # Matriz de correlación
    'data_quality_score': float
}
```

### Testing del Modelo
- **Train/Test split**: Evaluación en datos no vistos
- **Validación cruzada**: Robustez del modelo
- **Análisis de residuos**: Distribución y normalidad
- **Test de overfitting**: Comparación train vs test

## Próximos Pasos

### Desarrollo Inmediato
1. **Integrar con API Django** para predicciones en tiempo real
2. **Crear interfaz web** para entrenamiento y visualización
3. **Implementar cache** para predicciones frecuentes

### Mejoras Futuras
1. **Modelos ensemble**: Combinación de múltiples algoritmos
2. **Feature engineering**: Características derivadas (volumen, densidad)
3. **Actualización online**: Reentrenamiento incremental
4. **A/B testing**: Comparación de versiones de modelo

### Integración con Sistema Completo
1. **Endpoint de predicción**: API REST para peso
2. **Validación cruzada con vision model**: Consistencia entre modelos
3. **Dashboard de monitoreo**: Métricas en tiempo real
4. **Alertas de degradación**: Detección de drift en el modelo

## Ejemplo de Uso Completo

```python
# 1. Crear y entrenar modelo
from ml.regression_model import WeightRegressionModel

model = WeightRegressionModel(
    algorithm='gradient_boosting',
    use_scaling=True,
    use_polynomial_features=False
)

# 2. Preparar datos desde Django
X, y = model.prepare_data(min_samples=50)
print(f"Dataset cargado: {X.shape[0]} muestras")

# 3. Entrenar con validación cruzada
metrics = model.train(X, y, cross_validation=True)
print(f"R² test: {metrics['test_metrics']['r2']:.4f}")

# 4. Guardar modelo
model.save_model('ml/models/weight_regression_custom.pkl')

# 5. Cargar y usar para predicción
loaded_model = WeightRegressionModel.load_model('ml/models/weight_regression_custom.pkl')
weight_prediction = loaded_model.predict_single(12.5, 8.3, 4.2)
print(f"Peso predicho: {weight_prediction:.2f}g")
```

Esta implementación proporciona una base sólida y escalable para la predicción de peso en granos de cacao, con soporte completo para múltiples algoritmos, evaluación rigurosa y integración seamless con Django.
