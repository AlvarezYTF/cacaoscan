# 🔍 Diagnóstico: R² Negativo en 'grosor' y Sigmas Fijos

## 📊 Resumen Ejecutivo

**Problema Principal:** Los sigmas (σ_i) de la función de pérdida basada en incertidumbre están fijos en 0.2999 y no se están aprendiendo.

**Causa Raíz:** Los parámetros `log_sigmas` de `UncertaintyWeightedLoss` NO estaban incluidos en el optimizador, por lo que nunca se actualizaban.

**Impacto:** Sin sigmas aprendibles, la función de pérdida no puede balancear automáticamente las diferentes tareas, resultando en:
- R² negativo en 'grosor' (la tarea más difícil)
- Val Loss alto a pesar de que otras tareas aprenden bien
- Modelo incapaz de adaptar el peso de cada tarea durante el entrenamiento

---

## 🔬 Análisis Detallado

### 1. Función de Pérdida (Loss Function)

**Ubicación:** `backend/ml/utils/losses.py`

**Estado Actual:**
- ✅ `log_sigmas` está definido como `nn.Parameter` (línea 36-38)
- ✅ La fórmula de la pérdida es correcta: `L_i_weighted = (1 / (2 * σ_i²)) * L_i + log(σ_i)`
- ❌ **PROBLEMA:** Los parámetros no se estaban pasando al optimizador

**Código Original (PROBLEMÁTICO):**
```python
optimizer = optim.AdamW(
    model.parameters(),  # ❌ Solo incluye parámetros del modelo
    lr=learning_rate,
    ...
)
```

**Código Corregido:**
```python
if use_uncertainty_loss and hasattr(criterion, 'parameters'):
    optimizer = optim.AdamW(
        list(model.parameters()) + list(criterion.parameters()),  # ✅ Incluye log_sigmas
        lr=learning_rate,
        ...
    )
```

### 2. Optimizador y Bucle de Entrenamiento

**Ubicación:** `backend/ml/regression/train_improved.py`

**Problemas Identificados:**
1. ❌ Los `log_sigmas` no estaban en el optimizador → nunca se actualizaban
2. ✅ El Val Loss se calcula correctamente como la suma de pérdidas individuales
3. ✅ El backward pass se ejecuta correctamente

**Solución Aplicada:**
- Incluir `criterion.parameters()` en el optimizador
- Agregar logging para verificar que los sigmas cambian durante el entrenamiento
- Mostrar el cambio porcentual de sigmas desde el inicio

### 3. Análisis de Datos (Dataset y Normalización)

**Ubicación:** `backend/ml/regression/scalers.py`

**Estado Actual:**
- ✅ Log-transform aplicado a 'grosor' y 'peso' (log1p)
- ✅ StandardScaler usado para normalización
- ⚠️ **Posible problema:** Grosor puede tener outliers extremos que afectan el R²

**Recomendaciones:**
1. Verificar distribución de 'grosor' en los datos
2. Considerar usar RobustScaler en vez de StandardScaler para 'grosor'
3. Aplicar clipping de outliers si es necesario

---

## ✅ Soluciones Implementadas

### 1. Incluir Parámetros de la Loss en el Optimizador

**Archivo:** `backend/ml/regression/train_improved.py` (líneas 162-187)

```python
# CRÍTICO: Incluir parámetros del modelo Y de la loss (log_sigmas) en el optimizador
if use_uncertainty_loss and hasattr(criterion, 'parameters'):
    optimizer = optim.AdamW(
        list(model.parameters()) + list(criterion.parameters()),
        lr=learning_rate,
        weight_decay=config.get('weight_decay', 1e-4),
        betas=(0.9, 0.999),
        eps=1e-8
    )
    logger.info("✔ Optimizador incluye parámetros del modelo Y de la loss (log_sigmas)")
```

### 2. Mejorar Fórmula de la Loss (Estabilidad Numérica)

**Archivo:** `backend/ml/utils/losses.py` (líneas 94-102)

```python
# Fórmula mejorada con epsilon para evitar división por cero
sigma_sq = sigma_i ** 2
epsilon = 1e-8
Li_weighted = (1.0 / (2.0 * sigma_sq + epsilon)) * Li + self.log_sigmas[i]
```

### 3. Logging Mejorado de Sigmas

**Archivo:** `backend/ml/regression/train_improved.py` (líneas 661-673)

```python
if use_uncertainty_loss:
    sigmas = criterion.get_sigmas()
    if epoch == 0:
        initial_sigmas = sigmas.copy()
        log_str += f" | Sigmas: {sigmas}"
    else:
        # Mostrar cambio porcentual desde el inicio
        sigma_changes = {k: f"{sigmas[k]:.4f} (Δ{...}%)" for k in sigmas}
        log_str += f" | Sigmas: {sigma_changes}"
```

---

## 📈 Resultados Esperados

Después de aplicar estas correcciones, deberías ver:

1. **Sigmas Cambiando Durante el Entrenamiento:**
   ```
   Epoch 1: Sigmas: {'alto': 0.3000, 'ancho': 0.3000, 'grosor': 0.3000, 'peso': 0.3000}
   Epoch 5: Sigmas: {'alto': 0.2850 (Δ-5.0%), 'ancho': 0.2900 (Δ-3.3%), 
                     'grosor': 0.3500 (Δ+16.7%), 'peso': 0.3200 (Δ+6.7%)}
   ```

2. **R² de Grosor Mejorando:**
   - Epoch 1: grosor R²: -0.5 a -1.0 (mejor que antes)
   - Epoch 5: grosor R²: -0.2 a 0.0
   - Epoch 10+: grosor R²: 0.0 a +0.3

3. **Val Loss Más Estable:**
   - Los sigmas se ajustarán automáticamente para balancear las tareas
   - Grosor (tarea difícil) tendrá un sigma más alto → menos peso en la pérdida total
   - Alto/Ancho (tareas fáciles) tendrán sigmas más bajos → más peso

---

## 🔧 Recomendaciones Adicionales

### 1. Análisis de Datos de Grosor

Ejecuta este script para analizar la distribución:

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Cargar datos
df = pd.read_csv('dataset_cacao.clean.csv')

# Analizar grosor
grosor = df['grosor_mm'].values
print(f"Grosor stats:")
print(f"  Mean: {grosor.mean():.2f}")
print(f"  Std: {grosor.std():.2f}")
print(f"  Min: {grosor.min():.2f}")
print(f"  Max: {grosor.max():.2f}")
print(f"  Q1: {np.percentile(grosor, 25):.2f}")
print(f"  Q3: {np.percentile(grosor, 75):.2f}")
print(f"  Outliers (IQR method): {len(grosor[(grosor < Q1 - 1.5*IQR) | (grosor > Q3 + 1.5*IQR)])}")

# Si hay muchos outliers, considerar:
# - Usar RobustScaler en vez de StandardScaler
# - Aplicar clipping: grosor = np.clip(grosor, Q1 - 1.5*IQR, Q3 + 1.5*IQR)
```

### 2. Ajustar Learning Rate para Sigmas

Si los sigmas no cambian lo suficiente, considera usar un learning rate diferente para ellos:

```python
# Separar parámetros del modelo y de la loss
model_params = list(model.parameters())
loss_params = list(criterion.parameters())

optimizer = optim.AdamW([
    {'params': model_params, 'lr': learning_rate},
    {'params': loss_params, 'lr': learning_rate * 10}  # LR más alto para sigmas
], weight_decay=config.get('weight_decay', 1e-4))
```

### 3. Monitorear Gradientes de Sigmas

Agrega logging de gradientes para verificar que se están actualizando:

```python
# Después de backward()
if use_uncertainty_loss:
    for name, param in criterion.named_parameters():
        if param.grad is not None:
            logger.debug(f"Gradiente de {name}: {param.grad.data.mean().item():.6f}")
        else:
            logger.warning(f"⚠ No hay gradiente para {name}")
```

---

## 📝 Checklist de Verificación

- [x] Parámetros de la loss incluidos en el optimizador
- [x] Fórmula de la loss corregida (con epsilon)
- [x] Logging mejorado de sigmas
- [ ] Verificar distribución de datos de grosor
- [ ] Monitorear cambio de sigmas durante entrenamiento
- [ ] Verificar que R² de grosor mejora

---

## 🎯 Conclusión

El problema principal era que los sigmas no se estaban aprendiendo porque no estaban en el optimizador. Con esta corrección, el modelo debería:

1. Aprender sigmas automáticamente para balancear las tareas
2. Asignar un sigma más alto a 'grosor' (tarea difícil) → menos peso en la pérdida
3. Mejorar el R² de grosor gradualmente durante el entrenamiento
4. Lograr un Val Loss más bajo y estable

**Próximos pasos:** Ejecutar el entrenamiento y verificar que los sigmas cambian y que el R² de grosor mejora.

