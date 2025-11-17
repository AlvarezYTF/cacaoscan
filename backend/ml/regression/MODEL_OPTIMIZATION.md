# Optimización de Modelos de Regresión - CacaoScan

## Análisis de Problemas en la Arquitectura Actual

### Problemas Identificados

1. **Falta de Batch Normalization**: Las capas fully connected no tenían BatchNorm, causando problemas de entrenamiento
2. **Inicialización de pesos**: No había inicialización explícita, causando que las capas nuevas empezaran con valores problemáticos
3. **Arquitectura demasiado compleja**: El modelo híbrido original era muy complejo (ResNet18 + ConvNeXt + Píxeles)
4. **Learning rate inadecuado**: Podía ser demasiado alto, causando inestabilidad
5. **Loss function**: MSELoss puede ser muy sensible a outliers
6. **Scheduler**: CosineAnnealingLR puede no ser el mejor para regresión

## Mejoras Implementadas

### 1. Batch Normalization

✅ **Agregado en todas las capas fully connected**
- Mejora la estabilidad del entrenamiento
- Permite learning rates más altos
- Reduce la dependencia de la inicialización

**Antes:**
```python
nn.Linear(512, 256),
nn.ReLU(inplace=True),
nn.Dropout(0.2)
```

**Después:**
```python
nn.Linear(512, 256),
nn.BatchNorm1d(256),
nn.ReLU(inplace=True),
nn.Dropout(0.3)
```

### 2. Inicialización de Pesos

✅ **Xavier Uniform para capas Linear**
✅ **Constante para BatchNorm**

```python
def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.xavier_uniform_(m.weight)
        if m.bias is not None:
            nn.init.constant_(m.bias, 0.0)
    elif isinstance(m, nn.BatchNorm1d):
        nn.init.constant_(m.weight, 1.0)
        nn.init.constant_(m.bias, 0.0)
```

### 3. Arquitectura Optimizada

#### SimpleCacaoRegression (Recomendado para empezar)

```python
ResNet18 Backbone (512 features)
    ↓
Linear(512 → 256) + BatchNorm + ReLU + Dropout
    ↓
Linear(256 → 128) + BatchNorm + ReLU + Dropout
    ↓
Linear(128 → 4)  # [alto, ancho, grosor, peso]
```

**Ventajas:**
- Simple y eficiente
- Fácil de entrenar
- Menos parámetros = menos overfitting

#### OptimizedResNet18Regression

Similar a Simple pero con más capas intermedias para mayor capacidad.

#### OptimizedHybridRegression

ResNet18 + Pixel Features (sin ConvNeXt para simplificar)

### 4. Loss Function Mejorada

**Antes:** `nn.MSELoss()` (muy sensible a outliers)

**Después:** `nn.SmoothL1Loss()` (más robusta)

```python
# SmoothL1Loss es más robusta que MSE
# L(x) = 0.5 * x^2 si |x| < 1
#      = |x| - 0.5 si |x| >= 1
criterion = nn.SmoothL1Loss()
```

**Alternativas disponibles:**
- `mse`: MSELoss (más sensible)
- `smooth_l1`: SmoothL1Loss (recomendado, default)
- `huber`: HuberLoss (muy robusta)

### 5. Optimizer Mejorado

**Configuración optimizada:**
```python
optimizer = optim.AdamW(
    model.parameters(),
    lr=1e-4,  # Más conservador
    weight_decay=1e-4,
    betas=(0.9, 0.999),
    eps=1e-8
)
```

**Validación de learning rate:**
- Si LR > 5e-4, se reduce automáticamente a 5e-4
- Previene inestabilidad en el entrenamiento

### 6. Scheduler Mejorado

**ReduceLROnPlateau (Recomendado para regresión):**
```python
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode='min',
    factor=0.5,  # Reduce LR a la mitad
    patience=5,  # Espera 5 épocas sin mejora
    verbose=True,
    min_lr=1e-7
)
```

**Ventajas:**
- Se adapta automáticamente al progreso del entrenamiento
- Reduce LR solo cuando es necesario
- Más robusto que CosineAnnealing para regresión

## Modelos Disponibles

### 1. SimpleCacaoRegression (Recomendado)

**Uso:**
```python
from ml.regression.optimized_models import SimpleCacaoRegression

model = SimpleCacaoRegression(
    num_outputs=4,  # [alto, ancho, grosor, peso]
    pretrained=True,
    dropout_rate=0.25
)
```

**Características:**
- ResNet18 backbone
- Head simple: 512 → 256 → 128 → 4
- BatchNorm en todas las capas
- Inicialización de pesos adecuada

### 2. OptimizedResNet18Regression

**Uso:**
```python
from ml.regression.optimized_models import OptimizedResNet18Regression

model = OptimizedResNet18Regression(
    num_outputs=4,
    pretrained=True,
    dropout_rate=0.3,
    freeze_backbone=False  # True para fine-tuning
)
```

**Características:**
- Más capas intermedias que Simple
- Opción de congelar backbone
- Mejor para datasets más grandes

### 3. OptimizedHybridRegression

**Uso:**
```python
from ml.regression.optimized_models import OptimizedHybridRegression

model = OptimizedHybridRegression(
    num_outputs=4,
    pretrained=True,
    dropout_rate=0.3,
    num_pixel_features=12,  # 12 extendidos o 5 básicos
    use_pixel_features=True
)
```

**Características:**
- ResNet18 + Pixel Features
- Más simple que el híbrido original (sin ConvNeXt)
- Mejor para cuando se tienen features de píxeles

## Configuración de Entrenamiento Recomendada

### Para empezar (SimpleCacaoRegression)

```python
config = {
    'model_type': 'simple',  # Usar modelo simple
    'learning_rate': 1e-4,  # Conservador
    'loss_type': 'smooth_l1',  # Más robusta que MSE
    'scheduler_type': 'reduce_on_plateau',  # Adaptativo
    'epochs': 50,
    'batch_size': 32,
    'dropout_rate': 0.25,
    'weight_decay': 1e-4,
    'max_grad_norm': 1.0,
    'early_stopping_patience': 10
}
```

### Para modelo híbrido

```python
config = {
    'model_type': 'hybrid',
    'hybrid': True,
    'use_pixel_features': True,
    'learning_rate': 5e-5,  # Más bajo para modelo más complejo
    'loss_type': 'smooth_l1',
    'scheduler_type': 'reduce_on_plateau',
    'epochs': 50,
    'batch_size': 32,
    'dropout_rate': 0.3,
    'weight_decay': 1e-4
}
```

## Uso en el Pipeline

### Opción 1: Usar modelos optimizados directamente

```python
from ml.regression.optimized_models import create_optimized_model

model = create_optimized_model(
    model_type='simple',  # o 'resnet18', 'hybrid'
    num_outputs=4,
    pretrained=True,
    dropout_rate=0.25
)
```

### Opción 2: Actualizar create_model existente

El código existente en `models.py` ya está optimizado con BatchNorm e inicialización de pesos.

## Verificación de Salida

**IMPORTANTE:** El modelo siempre debe devolver 4 valores en este orden:
```python
[alto, ancho, grosor, peso]
```

**Verificación:**
```python
# Test forward pass
model.eval()
with torch.no_grad():
    dummy_input = torch.randn(1, 3, 224, 224)
    output = model(dummy_input)
    
    if isinstance(output, dict):
        assert 'alto' in output
        assert 'ancho' in output
        assert 'grosor' in output
        assert 'peso' in output
        print("✅ Formato de salida correcto")
    elif isinstance(output, torch.Tensor):
        assert output.shape[1] == 4
        print(f"✅ Tensor de salida correcto: shape={output.shape}")
```

## Comparación de Arquitecturas

| Modelo | Parámetros | Complejidad | Recomendado para |
|--------|-----------|-------------|------------------|
| SimpleCacaoRegression | ~11M | Baja | Empezar, datasets pequeños |
| OptimizedResNet18Regression | ~11M | Media | Datasets medianos |
| OptimizedHybridRegression | ~12M | Media-Alta | Cuando hay pixel_features |
| HybridCacaoRegression (original) | ~25M | Alta | Solo si Simple no funciona |

## Checklist de Verificación

Antes de entrenar, verificar:

- [ ] Modelo tiene BatchNorm en capas FC
- [ ] Pesos inicializados correctamente
- [ ] Salida es exactamente 4 valores: [alto, ancho, grosor, peso]
- [ ] Loss function es SmoothL1Loss o HuberLoss (no MSE puro)
- [ ] Learning rate <= 5e-4
- [ ] Scheduler es ReduceLROnPlateau o similar
- [ ] Targets están normalizados (StandardScaler)
- [ ] R² se calcula sobre valores desnormalizados

## Próximos Pasos

1. **Empezar con SimpleCacaoRegression**
   ```bash
   docker compose exec backend python manage.py train_cacao_models \
     --model-type resnet18 \
     --epochs 50 \
     --batch-size 32 \
     --learning-rate 1e-4 \
     --loss-type smooth_l1 \
     --scheduler-type reduce_on_plateau
   ```

2. **Si Simple funciona pero R² es bajo:**
   - Aumentar epochs
   - Reducir learning rate a 5e-5
   - Usar OptimizedResNet18Regression

3. **Si tienes pixel_calibration.json:**
   - Usar OptimizedHybridRegression
   - Asegurar que use_pixel_features=True

4. **Monitorear:**
   - Train Loss debe disminuir
   - Val Loss debe disminuir (puede tener ruido)
   - R² debe mejorar gradualmente (no ser extremadamente negativo)

## Troubleshooting

### R² extremadamente negativo

**Causas posibles:**
1. Targets no normalizados → Normalizar con StandardScaler
2. R² calculado sobre valores normalizados → Desnormalizar antes
3. Modelo prediciendo valores constantes → Verificar inicialización
4. Learning rate muy alto → Reducir a 1e-4 o menos

### Loss no disminuye

**Soluciones:**
1. Reducir learning rate
2. Verificar que targets estén normalizados
3. Usar SmoothL1Loss en lugar de MSELoss
4. Aumentar batch size si es muy pequeño

### Modelo predice valores constantes

**Soluciones:**
1. Verificar inicialización de pesos (debe estar implementada)
2. Reducir dropout (puede estar muy alto)
3. Verificar que el modelo no esté congelado
4. Usar learning rate más alto (pero <= 5e-4)

