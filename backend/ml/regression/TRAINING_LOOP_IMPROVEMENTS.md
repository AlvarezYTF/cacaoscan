# Mejoras en el Training Loop - CacaoScan

## Problemas Identificados

### 1. Pérdidas Enormes
- Train Loss: 1580141
- Val Loss: 46024
- **Causa:** Targets no normalizados o normalización incorrecta

### 2. R² Extremadamente Negativos
- alto R²: -1306
- ancho R²: -25495
- **Causa:** R² calculado sobre valores normalizados o desnormalización incorrecta

### 3. Falta de Validación
- No se validaba normalización antes de entrenar
- No se validaba pérdida inicial
- No había checkpoints automáticos

### 4. Logging Insuficiente
- No mostraba pérdida por batch
- No mostraba tiempo por epoch
- No mostraba R² por variable claramente

## Soluciones Implementadas

### 1. Validación de Normalización

**Antes:** No se validaba si los targets estaban normalizados.

**Después:**
```python
# Validar normalización ANTES de entrenar
validate_targets_normalization(train_targets_dict, scalers, verbose=True)
```

**Valida:**
- ✅ Que no haya NaN/Inf
- ✅ Que los valores estén en rango razonable (mean ~0, std ~1 para StandardScaler)
- ✅ Que todos los targets estén presentes

### 2. Validación de Pérdida Inicial

**Antes:** No se validaba la pérdida inicial.

**Después:**
```python
# Validar pérdida inicial (primeros 5 batches)
initial_val_loss = validate_initial_loss(model, val_loader, criterion)

if initial_val_loss > 1000:
    logger.error("PÉRDIDA INICIAL EXTREMADAMENTE ALTA")
    # Sugiere problemas en normalización, inicialización, o LR
```

**Detecta:**
- ✅ Pérdidas extremadamente altas (>1000)
- ✅ Pérdidas altas (>100)
- ✅ Sugiere causas posibles

### 3. Checkpoints Automáticos

**Antes:** No se guardaban checkpoints automáticamente.

**Después:**
```python
# Guardar checkpoint cuando mejora val_loss
if avg_val_loss < best_val_loss - improvement_threshold:
    checkpoint_path = checkpoint_dir / f"best_model_epoch_{epoch+1}.pt"
    torch.save({
        'epoch': epoch + 1,
        'model_state_dict': best_model_state,
        'optimizer_state_dict': optimizer.state_dict(),
        'scheduler_state_dict': scheduler.state_dict(),
        'val_loss': best_val_loss,
        'metrics': metrics_per_target,
        'avg_r2': avg_r2,
        'config': config
    }, checkpoint_path)
```

**Guarda:**
- ✅ Modelo con mejor val_loss
- ✅ Estado del optimizador y scheduler
- ✅ Métricas completas
- ✅ Configuración usada

### 4. Logging Mejorado

**Antes:**
```
Epoch 4/50 - Train Loss: 1580141.7857, Val Loss: 46024.7196
```

**Después:**
```
Epoch 4/50 | Train Loss: 0.1234 | Val Loss: 0.2345 | LR: 1.00e-04 | Time: 12.34s | alto R²: 0.1234 | ancho R²: 0.2345 | grosor R²: 0.3456 | peso R²: 0.4567 | Avg R²: 0.2901

=== Métricas detalladas por componente ===
ALTO: MAE=1.2345, RMSE=2.3456, R²=0.1234, n=100
ANCHO: MAE=0.9876, RMSE=1.8765, R²=0.2345, n=100
GROSOR: MAE=0.7654, RMSE=1.5432, R²=0.3456, n=100
PESO: MAE=0.1234, RMSE=0.2345, R²=0.4567, n=100
R² Promedio: 0.2901
Tiempo total: 123.45s
==========================================
```

**Muestra:**
- ✅ Pérdida por batch (cada 10% de batches)
- ✅ Pérdida total por epoch
- ✅ R² por variable
- ✅ Tiempo por epoch
- ✅ Learning rate actual
- ✅ Métricas detalladas cada 5 épocas

### 5. Early Stopping Mejorado

**Antes:** Early stopping básico.

**Después:**
```python
# Early stopping con mejor tracking
if avg_val_loss < best_val_loss - improvement_threshold:
    best_val_loss = avg_val_loss
    best_epoch = epoch + 1
    patience_counter = 0
    best_model_state = model.state_dict().copy()
    # Guardar checkpoint
else:
    patience_counter += 1

if patience_counter >= early_stopping_patience:
    logger.info(f"Early stopping en época {epoch+1} (mejor época: {best_epoch})")
```

**Mejoras:**
- ✅ Guarda mejor época
- ✅ Guarda mejor modelo automáticamente
- ✅ Logs más informativos

### 6. Validación de Pérdidas

**Antes:** No se validaba si la pérdida era finita.

**Después:**
```python
# Validar pérdida del batch
if not torch.isfinite(loss):
    logger.error(f"Batch {batch_idx}: Pérdida no finita: {loss.item()}")
    continue
```

**Valida:**
- ✅ Que la pérdida sea finita (no NaN/Inf)
- ✅ Omite batches problemáticos

### 7. Learning Rate Optimizado

**Antes:** LR podía ser muy alto o muy bajo.

**Después:**
```python
# Validar y ajustar LR
if learning_rate > 1e-3:
    logger.warning(f"LR {learning_rate} muy alto. Reduciendo a 1e-3")
    learning_rate = 1e-3
elif learning_rate < 1e-6:
    logger.warning(f"LR {learning_rate} muy bajo. Aumentando a 1e-5")
    learning_rate = 1e-5
```

**Recomendaciones:**
- LR inicial: 1e-4 (conservador)
- LR máximo: 1e-3
- LR mínimo: 1e-6

### 8. Integración con Métricas R² Mejoradas

**Antes:** R² calculado manualmente, podía tener errores.

**Después:**
```python
# Usar función robusta de métricas
from .metrics import denormalize_and_calculate_metrics

metrics_per_target, avg_r2 = denormalize_and_calculate_metrics(
    predictions_norm=pred_dict_norm,
    targets_norm=targ_dict_norm,
    scalers=scalers,
    target_names=TARGETS,
    verbose=False
)
```

**Ventajas:**
- ✅ Desnormalización automática
- ✅ Validación de alineación
- ✅ Manejo robusto de edge cases
- ✅ R² promedio calculado automáticamente

## Uso del Training Loop Mejorado

### Opción 1: Automático (Recomendado)

El training loop mejorado se usa automáticamente cuando se llama a `train_multi_head_model`:

```python
from ml.regression.train import train_multi_head_model

history = train_multi_head_model(
    model=model,
    train_loader=train_loader,
    val_loader=val_loader,
    scalers=scalers,
    config=config,
    device=device,
    use_improved=True  # Por defecto True
)
```

### Opción 2: Directo

```python
from ml.regression.train_improved import train_multi_head_model_improved

history = train_multi_head_model_improved(
    model=model,
    train_loader=train_loader,
    val_loader=val_loader,
    scalers=scalers,
    config=config,
    device=device,
    save_dir=checkpoint_dir
)
```

## Configuración Recomendada

```python
config = {
    'learning_rate': 1e-4,  # Conservador, validado automáticamente
    'loss_type': 'smooth_l1',  # Más robusta que MSE
    'scheduler_type': 'reduce_on_plateau',  # Adaptativo
    'epochs': 50,
    'batch_size': 32,  # Ajustar según GPU
    'dropout_rate': 0.25,
    'weight_decay': 1e-4,
    'max_grad_norm': 1.0,
    'early_stopping_patience': 10,
    'improvement_threshold': 1e-4,
    'min_lr': 1e-7
}
```

## Hiperparámetros Optimizados

### Learning Rate
- **Inicial:** 1e-4 (conservador)
- **Máximo:** 1e-3 (validado automáticamente)
- **Mínimo:** 1e-6 (para fine-tuning)

### Batch Size
- **Recomendado:** 32
- **Si GPU pequeña:** 16
- **Si GPU grande:** 64

### Epochs
- **Inicial:** 50
- **Con early stopping:** Se detiene automáticamente si no mejora

### Scheduler
- **Recomendado:** `reduce_on_plateau` (adaptativo)
- **Alternativas:** `cosine`, `cosine_warmup`

## Logs de Ejemplo

### Inicio de Entrenamiento
```
=== Validando normalización de targets ===
alto: mean=0.0001, std=1.0002, range=[-2.3456, 2.5678]
ancho: mean=-0.0002, std=0.9998, range=[-2.1234, 2.3456]
grosor: mean=0.0000, std=1.0001, range=[-2.2345, 2.4567]
peso: mean=0.0001, std=0.9999, range=[-2.3456, 2.5678]
==========================================

=== Validando pérdida inicial ===
Pérdida inicial (promedio de 5 batches): 0.1234
=================================

=== Iniciando entrenamiento (50 épocas) ===
```

### Durante Entrenamiento
```
Epoch 1/50 | Train Loss: 0.1234 | Val Loss: 0.2345 | LR: 1.00e-04 | Time: 12.34s | alto R²: 0.1234 | ancho R²: 0.2345 | grosor R²: 0.3456 | peso R²: 0.4567 | Avg R²: 0.2901
✓ Checkpoint guardado: checkpoints/best_model_epoch_1.pt (Val Loss: 0.2345)

Epoch 2/50 | Train Loss: 0.1123 | Val Loss: 0.2234 | LR: 1.00e-04 | Time: 11.23s | alto R²: 0.2345 | ancho R²: 0.3456 | grosor R²: 0.4567 | peso R²: 0.5678 | Avg R²: 0.4012
✓ Checkpoint guardado: checkpoints/best_model_epoch_2.pt (Val Loss: 0.2234)
```

### Métricas Detalladas (cada 5 épocas)
```
=== Métricas detalladas por componente ===
ALTO: MAE=1.2345, RMSE=2.3456, R²=0.1234, n=100
ANCHO: MAE=0.9876, RMSE=1.8765, R²=0.2345, n=100
GROSOR: MAE=0.7654, RMSE=1.5432, R²=0.3456, n=100
PESO: MAE=0.1234, RMSE=0.2345, R²=0.4567, n=100
R² Promedio: 0.2901
Tiempo total: 123.45s
==========================================
```

### Early Stopping
```
Early stopping en época 25 (mejor época: 20, Val Loss: 0.1234)
Mejor modelo cargado (Época 20, Val Loss: 0.1234)
=== Entrenamiento completado en 234.56s ===
```

## Troubleshooting

### Pérdida Inicial Extremadamente Alta

**Síntoma:**
```
PÉRDIDA INICIAL EXTREMADAMENTE ALTA: 1580141.7857
```

**Soluciones:**
1. Verificar que targets estén normalizados
2. Reducir learning rate a 1e-5
3. Verificar inicialización del modelo
4. Verificar loss function

### R² Extremadamente Negativo

**Síntoma:**
```
alto R²: -1306.3514
```

**Soluciones:**
1. Verificar que se desnormalice antes de calcular R² (ya implementado)
2. Verificar alineación de predicciones y targets
3. Verificar que el modelo esté aprendiendo (loss debe disminuir)

### Pérdida No Finita

**Síntoma:**
```
Batch 5: Pérdida no finita: nan
```

**Soluciones:**
1. Verificar que no haya NaN/Inf en targets
2. Reducir learning rate
3. Aumentar gradient clipping (max_grad_norm)

## Checklist de Verificación

Antes de entrenar, verificar:

- [x] Targets están normalizados (validación automática)
- [x] Pérdida inicial es razonable (<100)
- [x] Learning rate está en rango válido (1e-6 a 1e-3)
- [x] Modelo está en modo train antes de entrenar
- [x] Checkpoints se guardan automáticamente
- [x] R² se calcula sobre valores desnormalizados
- [x] Logs muestran información detallada

## Archivos Creados

1. **`backend/ml/regression/train_improved.py`** (NUEVO)
   - Training loop mejorado completo
   - Validaciones exhaustivas
   - Logging detallado
   - Checkpoints automáticos

2. **`backend/ml/regression/train.py`** (MEJORADO)
   - Integración automática con training loop mejorado
   - Flag `use_improved=True` por defecto

3. **`backend/ml/regression/TRAINING_LOOP_IMPROVEMENTS.md`** (NUEVO)
   - Documentación completa
   - Ejemplos de uso
   - Troubleshooting

## Beneficios Inmediatos

1. **Detección Temprana de Problemas:** Validación antes de entrenar
2. **Pérdidas Razonables:** Validación y ajuste automático de LR
3. **R² Correctos:** Desnormalización automática
4. **Checkpoints Automáticos:** No se pierde el mejor modelo
5. **Logging Detallado:** Fácil debugging y monitoreo
6. **Early Stopping Robusto:** Evita overfitting

El training loop mejorado está listo para usar y debería resolver los problemas de pérdidas enormes y R² extremadamente negativos.

