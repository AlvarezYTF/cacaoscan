# Guía Rápida: Modelos Optimizados de Regresión

## Problema Identificado

El modelo original producía R² extremadamente negativos debido a:
1. ❌ Falta de Batch Normalization
2. ❌ Inicialización de pesos inadecuada
3. ❌ Learning rate demasiado alto
4. ❌ MSELoss muy sensible a outliers
5. ❌ Scheduler no adaptativo

## Solución Implementada

### ✅ Modelos Optimizados

1. **SimpleCacaoRegression** (Recomendado para empezar)
   - ResNet18 + Head simple optimizada
   - BatchNorm en todas las capas
   - Inicialización de pesos adecuada

2. **OptimizedResNet18Regression**
   - Similar a Simple pero con más capas
   - Mejor para datasets más grandes

3. **OptimizedHybridRegression**
   - ResNet18 + Pixel Features
   - Simplificado (sin ConvNeXt)

### ✅ Configuración Mejorada

- **Loss:** SmoothL1Loss (más robusta que MSE)
- **Optimizer:** AdamW con LR validado (max 5e-4)
- **Scheduler:** ReduceLROnPlateau (adaptativo)
- **BatchNorm:** En todas las capas FC
- **Inicialización:** Xavier Uniform

## Uso Rápido

### Opción 1: Usar modelo optimizado directamente

```python
from ml.regression.optimized_models import SimpleCacaoRegression

model = SimpleCacaoRegression(
    num_outputs=4,  # [alto, ancho, grosor, peso]
    pretrained=True,
    dropout_rate=0.25
)
```

### Opción 2: Usar create_model (automático)

El código ya está actualizado para usar modelos optimizados automáticamente:

```python
from ml.regression.models import create_model

# Esto usará el modelo optimizado automáticamente
model = create_model(
    model_type='resnet18',
    num_outputs=4,
    pretrained=True,
    dropout_rate=0.3,
    use_optimized=True  # Por defecto True
)
```

### Opción 3: Comando de entrenamiento

```bash
docker compose exec backend python manage.py train_cacao_models \
  --hybrid \
  --use-pixel-features \
  --epochs 50 \
  --batch-size 32 \
  --learning-rate 1e-4 \
  --loss-type smooth_l1 \
  --scheduler-type reduce_on_plateau \
  --segmentation-backend opencv
```

## Configuración Recomendada

```python
config = {
    'model_type': 'resnet18',  # o 'simple' para empezar
    'learning_rate': 1e-4,  # Conservador, validado automáticamente
    'loss_type': 'smooth_l1',  # Más robusta que MSE
    'scheduler_type': 'reduce_on_plateau',  # Adaptativo
    'epochs': 50,
    'batch_size': 32,
    'dropout_rate': 0.25,  # Para Simple, 0.3 para otros
    'weight_decay': 1e-4,
    'max_grad_norm': 1.0,
    'early_stopping_patience': 10
}
```

## Verificación de Salida

El modelo **SIEMPRE** debe devolver 4 valores en este orden:

```python
[alto, ancho, grosor, peso]
```

**Test rápido:**
```python
model.eval()
dummy = torch.randn(1, 3, 224, 224)
output = model(dummy)

if isinstance(output, dict):
    assert output['alto'].shape[1] == 1
    assert output['ancho'].shape[1] == 1
    assert output['grosor'].shape[1] == 1
    assert output['peso'].shape[1] == 1
    print("✅ Formato correcto")
elif isinstance(output, torch.Tensor):
    assert output.shape[1] == 4
    print(f"✅ Tensor correcto: shape={output.shape}")
```

## Qué Esperar

### Antes (Modelo Original)
- R²: -1000 a -10000 (extremadamente negativo)
- Loss: 100000+ (muy alto)
- Predicciones: Valores constantes o sin sentido

### Después (Modelo Optimizado)
- R²: Debe mejorar gradualmente (empezar cerca de 0, mejorar hacia positivo)
- Loss: Debe disminuir durante el entrenamiento
- Predicciones: Deben variar según la imagen

## Troubleshooting

### Si R² sigue siendo negativo:

1. **Verificar normalización de targets:**
   ```python
   # Targets deben estar normalizados con StandardScaler
   # R² debe calcularse sobre valores DESNORMALIZADOS
   ```

2. **Reducir learning rate:**
   ```python
   learning_rate = 5e-5  # Más conservador
   ```

3. **Usar modelo Simple:**
   ```python
   model_type = 'simple'  # Más simple = más fácil de entrenar
   ```

4. **Verificar datos:**
   - Imágenes en RGB
   - Targets en orden correcto
   - No hay NaN o Inf

### Si Loss no disminuye:

1. Verificar que targets estén normalizados
2. Reducir learning rate
3. Aumentar batch size si es muy pequeño (< 16)
4. Verificar que el modelo no esté congelado

## Próximos Pasos

1. **Empezar simple:**
   - Usar `SimpleCacaoRegression`
   - Configuración conservadora (LR=1e-4, SmoothL1Loss)
   - 50 épocas

2. **Si funciona:**
   - Aumentar complejidad gradualmente
   - Probar con pixel_features si están disponibles

3. **Monitorear:**
   - Train Loss debe disminuir
   - Val Loss debe disminuir (puede tener ruido)
   - R² debe mejorar (no ser extremadamente negativo)

