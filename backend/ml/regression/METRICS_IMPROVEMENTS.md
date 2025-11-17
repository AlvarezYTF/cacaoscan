# Mejoras en el Cálculo de Métricas - CacaoScan

## Problemas Identificados

### 1. R² Calculado sobre Valores Normalizados
**Problema:** El R² se calculaba sobre valores normalizados, lo que produce valores extremadamente negativos.

**Solución:** Desnormalizar predicciones y targets ANTES de calcular R².

### 2. Falta de Validación
**Problema:** No se validaban dimensiones, NaN/Inf, o alineación entre predicciones y targets.

**Solución:** Validaciones exhaustivas antes de calcular métricas.

### 3. Cálculo de R² No Robusto
**Problema:** El cálculo de R² no manejaba casos edge (ss_tot muy pequeño, valores constantes, etc.).

**Solución:** Función `robust_r2_score()` que maneja todos los casos edge.

### 4. Falta de R² Promedio
**Problema:** Solo se calculaba R² individual por target, no había un promedio.

**Solución:** Cálculo de R² promedio sobre todos los targets.

## Implementación

### Nuevo Módulo: `backend/ml/regression/metrics.py`

#### 1. `robust_r2_score()`

Función robusta para calcular R² con validaciones exhaustivas:

```python
from ml.regression.metrics import robust_r2_score

r2 = robust_r2_score(
    y_true=targets_desnormalizados,
    y_pred=predicciones_desnormalizadas,
    target_name="alto",
    verbose=True
)
```

**Características:**
- ✅ Valida dimensiones
- ✅ Filtra NaN/Inf automáticamente
- ✅ Maneja ss_tot muy pequeño
- ✅ Detecta R² extremadamente negativo y loggea detalles
- ✅ Logs detallados opcionales

#### 2. `calculate_metrics_per_target()`

Calcula MAE, RMSE y R² para cada target individualmente:

```python
from ml.regression.metrics import calculate_metrics_per_target

metrics = calculate_metrics_per_target(
    predictions={target: array for target in TARGETS},
    targets={target: array for target in TARGETS},
    verbose=True
)
```

**Retorna:**
```python
{
    'alto': {'mae': 1.23, 'rmse': 2.45, 'r2': 0.85, 'n_samples': 100},
    'ancho': {'mae': 0.98, 'rmse': 1.76, 'r2': 0.78, 'n_samples': 100},
    ...
}
```

#### 3. `denormalize_and_calculate_metrics()`

Desnormaliza y calcula métricas en una sola función:

```python
from ml.regression.metrics import denormalize_and_calculate_metrics

metrics, avg_r2 = denormalize_and_calculate_metrics(
    predictions_norm=predicciones_normalizadas,
    targets_norm=targets_normalizados,
    scalers=cacao_scalers,
    verbose=True
)
```

**Características:**
- ✅ Desnormaliza automáticamente
- ✅ Calcula métricas por target
- ✅ Calcula R² promedio
- ✅ Maneja errores de desnormalización

#### 4. `validate_predictions_targets_alignment()`

Valida que predicciones y targets estén alineados:

```python
from ml.regression.metrics import validate_predictions_targets_alignment

is_aligned = validate_predictions_targets_alignment(
    predictions=pred_dict,
    targets=targ_dict
)
```

## Uso en el Loop de Validación

### Para Modelos Individuales (`RegressionTrainer`)

**Antes:**
```python
# ❌ R² calculado sobre valores normalizados
r2 = 1 - (ss_res / (ss_tot + 1e-8))
```

**Después:**
```python
# ✅ Desnormalizar primero
pred_dict_norm = {self.target: all_predictions}
targ_dict_norm = {self.target: all_targets}
pred_dict_denorm = self.scalers.inverse_transform(pred_dict_norm)
targ_dict_denorm = self.scalers.inverse_transform(targ_dict_norm)

# ✅ Usar función robusta
from .metrics import robust_r2_score
r2 = robust_r2_score(
    targ_dict_denorm[self.target],
    pred_dict_denorm[self.target],
    target_name=self.target
)
```

### Para Modelos Multi-Head (`train_multi_head_model`)

**Antes:**
```python
# ❌ Cálculo manual, no robusto
ss_res = np.sum((targets - preds) ** 2)
ss_tot = np.sum((targets - np.mean(targets)) ** 2)
r2 = 1 - (ss_res / ss_tot)
```

**Después:**
```python
# ✅ Usar función robusta con desnormalización automática
from .metrics import (
    denormalize_and_calculate_metrics,
    validate_predictions_targets_alignment
)

# Validar alineación
validate_predictions_targets_alignment(pred_dict_norm, targ_dict_norm)

# Desnormalizar y calcular métricas
metrics_per_target, avg_r2 = denormalize_and_calculate_metrics(
    predictions_norm=pred_dict_norm,
    targets_norm=targ_dict_norm,
    scalers=scalers,
    verbose=False
)

# Guardar en history
for target in TARGETS:
    history[f'val_r2_{target}'].append(metrics_per_target[target]['r2'])
history['val_r2_avg'].append(avg_r2)  # R² promedio
```

## Logs Mejorados

### Logs por Época

**Antes:**
```
Epoch 1/50 - Train Loss: 0.1234, Val Loss: 0.2345, alto R²: -1234.5678
```

**Después:**
```
Epoch 1/50 - Train Loss: 0.1234, Val Loss: 0.2345, alto R²: 0.1234, ancho R²: 0.2345, grosor R²: 0.3456, peso R²: 0.4567 | Avg R²: 0.2901
```

### Logs Detallados (cada 5 épocas o si R² < -100)

```
=== Métricas detalladas por componente ===
ALTO: MAE=1.2345, RMSE=2.3456, R²=0.1234, n=100
ANCHO: MAE=0.9876, RMSE=1.8765, R²=0.2345, n=100
GROSOR: MAE=0.7654, RMSE=1.5432, R²=0.3456, n=100
PESO: MAE=0.1234, RMSE=0.2345, R²=0.4567, n=100
R² Promedio: 0.2901
==========================================
```

### Logs de Advertencia

Si R² es extremadamente negativo:
```
ERROR: alto: R² extremadamente negativo (-1234.5678). Esto indica un problema serio:
  - Preds range: [-5.1234, 5.5678]
  - Targets range: [10.2345, 25.6789]
  - Preds mean: 0.1234, std: 2.3456
  - Targets mean: 18.4567, std: 5.6789
  - ss_res: 12345.67, ss_tot: 123.45
```

## Validaciones Implementadas

### 1. Dimensiones
- ✅ Verifica que `y_true.shape == y_pred.shape`
- ✅ Aplana automáticamente si es necesario
- ✅ Error si no se pueden igualar dimensiones

### 2. NaN/Inf
- ✅ Filtra valores NaN/Inf automáticamente
- ✅ Loggea cuántos valores se filtraron
- ✅ Retorna 0.0 si no hay valores válidos

### 3. Variación en Targets
- ✅ Verifica que `std(targets) > 1e-8`
- ✅ Retorna 0.0 si no hay variación (targets constantes)

### 4. ss_tot
- ✅ Verifica que `ss_tot > 1e-8`
- ✅ Retorna 0.0 si ss_tot es muy pequeño

### 5. R² Extremadamente Negativo
- ✅ Detecta R² < -1000 (error crítico)
- ✅ Detecta R² < -100 (advertencia)
- ✅ Loggea detalles completos para debugging

## Ejemplo Completo de Uso

```python
import numpy as np
from ml.regression.metrics import (
    robust_r2_score,
    calculate_metrics_per_target,
    denormalize_and_calculate_metrics,
    validate_predictions_targets_alignment
)

# 1. Datos normalizados (del modelo)
predictions_norm = {
    'alto': np.array([0.1, 0.2, 0.3]),
    'ancho': np.array([-0.1, 0.0, 0.1]),
    'grosor': np.array([0.05, 0.15, 0.25]),
    'peso': np.array([-0.2, 0.0, 0.2])
}

targets_norm = {
    'alto': np.array([0.12, 0.22, 0.32]),
    'ancho': np.array([-0.08, 0.02, 0.12]),
    'grosor': np.array([0.06, 0.16, 0.26]),
    'peso': np.array([-0.18, 0.02, 0.22])
}

# 2. Validar alineación
is_aligned = validate_predictions_targets_alignment(
    predictions_norm,
    targets_norm
)
print(f"Alineación correcta: {is_aligned}")

# 3. Desnormalizar y calcular métricas
metrics, avg_r2 = denormalize_and_calculate_metrics(
    predictions_norm=predictions_norm,
    targets_norm=targets_norm,
    scalers=scalers,  # Objeto CacaoScalers
    verbose=True
)

# 4. Resultados
print(f"R² promedio: {avg_r2:.4f}")
for target, m in metrics.items():
    print(f"{target}: MAE={m['mae']:.4f}, RMSE={m['rmse']:.4f}, R²={m['r2']:.4f}")
```

## Beneficios

1. **R² Correcto:** Siempre calculado sobre valores desnormalizados
2. **Robustez:** Maneja todos los casos edge (NaN, Inf, dimensiones, etc.)
3. **Debugging:** Logs detallados cuando hay problemas
4. **R² Promedio:** Métrica agregada útil para monitoreo
5. **Validación:** Detecta problemas de alineación temprano

## Checklist de Verificación

Antes de calcular R², verificar:

- [x] Predicciones y targets están desnormalizados
- [x] Dimensiones coinciden
- [x] No hay NaN/Inf
- [x] Targets tienen variación (no son constantes)
- [x] ss_tot > 1e-8
- [x] R² se calcula con función robusta
- [x] R² promedio se calcula y guarda
- [x] Logs detallados se muestran periódicamente

## Troubleshooting

### R² Extremadamente Negativo

**Causas posibles:**
1. Predicciones y targets en diferentes escalas (no desnormalizados)
2. Targets desordenados (no alineados)
3. Modelo prediciendo valores constantes muy diferentes a la media

**Solución:**
1. Verificar que se desnormalice correctamente
2. Usar `validate_predictions_targets_alignment()`
3. Revisar logs detallados para ver rangos de predicciones y targets

### R² = 0.0

**Causas posibles:**
1. ss_tot muy pequeño (targets casi constantes)
2. No hay valores válidos después de filtrar NaN/Inf
3. Desviación estándar de targets muy pequeña

**Solución:**
1. Verificar que los targets tengan variación
2. Revisar logs para ver cuántos valores se filtraron
3. Verificar que los datos sean correctos

