# Feature 2.1: Modelo de Visión Artificial - Implementación Completa

## Resumen
Se ha implementado exitosamente la Feature 2.1: Modelo de visión artificial dentro del proyecto CacaoScan. Esta implementación proporciona una CNN completa en PyTorch que puede predecir las características físicas de granos de cacao a partir de imágenes.

## Archivos Implementados

### 1. `backend/ml/vision_model.py`
**Propósito**: Definición de la arquitectura CNN principal
**Características**:
- Clase `CacaoVisionModel` que hereda de `torch.nn.Module`
- Arquitectura CNN con 5 bloques convolucionales + BatchNorm + ReLU
- Predice 4 salidas numéricas: width, height, thickness, weight
- Incluye pooling adaptativo para manejar diferentes tamaños de entrada
- Funciones de utilidad para carga, guardado e inferencia
- Inicialización de pesos Kaiming/Xavier
- Regularización con Dropout

**Estructura del modelo**:
```
Entrada: (batch_size, 3, H, W) -> RGB images
├── Conv Block 1: 3 -> 32 channels (7x7 kernel, stride=2)
├── Conv Block 2: 32 -> 64 channels (5x5 kernel)
├── Conv Block 3: 64 -> 128 channels (3x3 kernel)
├── Conv Block 4: 128 -> 256 channels (3x3 kernel)
├── Conv Block 5: 256 -> 512 channels (3x3 kernel)
├── Adaptive Pooling: -> (batch_size, 512, 4, 4)
└── FC Layers: 8192 -> 1024 -> 512 -> 128 -> 4
Salida: (batch_size, 4) -> [width, height, thickness, weight]
```

### 2. `backend/ml/data_preprocessing.py`
**Propósito**: Funciones de preprocesamiento y carga de datos
**Características**:
- Clase `CacaoImageTransforms` para transformaciones de imagen
- Clase `CacaoDataset` que hereda de `torch.utils.data.Dataset`
- Integración completa con el modelo Django `CacaoImage`
- Soporte para augmentación de datos en entrenamiento
- Carga de imágenes desde `media/` con validación de formatos
- División automática de dataset en train/validation
- Cálculo de estadísticas del dataset
- Manejo robusto de errores de carga

**Transformaciones incluidas**:
- Resize a tamaño objetivo (default: 224x224)
- Normalización con estadísticas ImageNet
- Augmentación: rotación, flip horizontal, color jitter, crop aleatorio
- Conversión a tensor PyTorch

### 3. `backend/ml/train_vision.py`
**Propósito**: Script completo de entrenamiento
**Características**:
- Clase `CacaoTrainer` para manejo del entrenamiento
- Soporte para múltiples optimizadores (Adam, AdamW, SGD)
- Schedulers de learning rate (ReduceLROnPlateau, Cosine, Step)
- Múltiples funciones de pérdida (MSE, MAE, Huber, Weighted MSE)
- Early stopping automático
- Guardado de checkpoints periódicos
- Logging con TensorBoard
- Cálculo de métricas detalladas (MAE, MSE, RMSE, MAPE por característica)
- Integración directa con Django ORM

**Métricas de evaluación**:
- MAE, MSE, RMSE globales y por característica
- MAPE (Mean Absolute Percentage Error) para interpretabilidad
- Logging en tiempo real y guardado de historial

### 4. `backend/ml/models/vision_model.pth`
**Propósito**: Archivo placeholder del modelo entrenado
**Contenido**:
- Estructura de checkpoint PyTorch
- Metadatos del modelo y configuración
- Marcado como placeholder para entrenamiento futuro

### 5. `backend/ml/config.py` (Actualizado)
**Agregado**: Configuración para el nuevo modelo de visión
```python
'vision_model': {
    'model_path': MODELS_DIR / 'vision_model.pth',
    'model_type': 'pytorch_vision',
    'input_shape': (3, 224, 224),
    'outputs': ['width', 'height', 'thickness', 'weight'],
    'output_units': ['mm', 'mm', 'mm', 'g'],
    'model_class': 'CacaoVisionModel'
}
```

## Integración con Django

### Modelo Django Compatible
El sistema está diseñado para trabajar directamente con el modelo `CacaoImage` existente:
```python
# Campos que el modelo predice
width = models.DecimalField(max_digits=8, decimal_places=3, ...)
height = models.DecimalField(max_digits=8, decimal_places=3, ...)
thickness = models.DecimalField(max_digits=8, decimal_places=3, ...)
weight = models.DecimalField(max_digits=8, decimal_places=4, ...)
```

### Carga de Datos
- Las imágenes se cargan desde `settings.MEDIA_ROOT`
- Filtrado automático de registros con medidas completas
- Soporte para metadatos adicionales (batch_number, quality, etc.)

## Uso del Sistema

### Entrenamiento
```bash
cd backend
python ml/train_vision.py --epochs 100 --batch-size 16 --learning-rate 1e-3
```

**Parámetros disponibles**:
- `--epochs`: Número de épocas (default: 100)
- `--batch-size`: Tamaño del batch (default: 16)
- `--learning-rate`: Tasa de aprendizaje (default: 1e-3)
- `--optimizer`: adam/adamw/sgd (default: adam)
- `--scheduler`: reduce_on_plateau/cosine/step
- `--loss`: mse/mae/huber/weighted_mse
- `--augment`: Activar augmentación de datos
- `--device`: auto/cpu/cuda

### Inferencia
```python
from ml.vision_model import load_model, CacaoVisionModel
from ml.data_preprocessing import preprocess_single_image

# Cargar modelo entrenado
model = load_model('ml/models/vision_model.pth')

# Preprocesar imagen
image_tensor = preprocess_single_image('path/to/image.jpg')

# Predicción
predictions = model.predict_measurements(image_tensor)
# Resultado: {'width': 12.5, 'height': 8.3, 'thickness': 4.2, 'weight': 0.85}
```

## Arquitectura y Rendimiento

### Parámetros del Modelo
- **Total de parámetros**: ~11.2M (calculado automáticamente)
- **Tamaño del modelo**: ~45MB (float32)
- **Memoria GPU requerida**: ~2-4GB para entrenamiento (batch_size=16)

### Optimizaciones Incluidas
- Gradient clipping para estabilidad
- Dropout para regularización
- BatchNorm para normalización
- Pooling adaptativo para flexibilidad de entrada
- Inicialización inteligente de pesos

## Próximos Pasos

### Para Entrenamiento Real
1. **Preparar datos**: Asegurar que existan imágenes con medidas ground truth en la DB
2. **Configurar GPU**: Instalar CUDA si está disponible
3. **Ajustar hiperparámetros**: Basado en el tamaño del dataset
4. **Monitoreo**: Usar TensorBoard para tracking (`tensorboard --logdir checkpoints/tensorboard`)

### Para Producción
1. **Validación**: Evaluar modelo en conjunto de prueba independiente
2. **Optimización**: Considerar quantization o pruning para deployment
3. **API Integration**: Integrar predicciones en las vistas Django
4. **Caching**: Implementar cache de predicciones para eficiencia

## Dependencias
El sistema requiere las siguientes librerías (ya incluidas en requirements.txt):
- PyTorch >= 2.4.0
- torchvision >= 0.19.0
- scikit-learn >= 1.5.1
- opencv-python >= 4.10.0
- Pillow >= 10.4.0
- numpy >= 1.26.4

## Notas Técnicas

### Robustez
- Manejo de errores en carga de imágenes
- Validación de formatos soportados
- Fallbacks para imágenes corruptas
- Logging detallado de errores

### Escalabilidad
- Soporte para datasets grandes con DataLoader
- Paralelización de carga de datos
- Checkpointing para entrenamientos largos
- Early stopping para eficiencia

### Flexibilidad
- Configuración modular en config.py
- Múltiples opciones de optimización
- Transformaciones customizables
- Métricas extensibles

Esta implementación proporciona una base sólida y completa para el análisis de características físicas de granos de cacao mediante visión artificial.
