# Checklist de Verificación - Pipeline Híbrido V2

## ✅ Verificaciones Automáticas en Logs

Cuando ejecutes el entrenamiento, busca estos mensajes en los logs para confirmar que TODO está aplicado:

### A) Auto-weighted Loss (σ_i)

**Buscar en logs:**
```
UncertaintyWeightedLoss initialized with initial_sigma=0.3
Uncertainty-based loss formula: L_total = Σ [ (1 / (2 * σ_i²)) * L_i + log σ_i ]
Learnable sigmas for targets: ['alto', 'ancho', 'grosor', 'peso']
```

**En cada epoch deberías ver:**
```
Sigmas: {'alto': 0.XX, 'ancho': 0.XX, 'grosor': 0.XX, 'peso': 0.XX}
```

**Si NO ves esto:** El auto-loss NO está activo.

### B) Nuevos Pixel Features

**Buscar en logs:**
```
First record pixel features (10 dims): area_mm2=X.XX, perimeter_mm=X.XX, compactness=X.XX, roundness=X.XX
Pixel features dimension: 10 (expected: 10)
```

**Si ves:**
```
Pixel features dimension: 8 (expected: 10)
```
**Entonces:** Los nuevos features NO están aplicados.

### C) Log-transform Selectivo

**Buscar en logs:**
```
Creating target scaler with SELECTIVE LOG-TRANSFORM (grosor, peso only)
LOG_TARGETS (will apply log1p): {'grosor', 'peso'}
Applied log1p transform to grosor
Applied log1p transform to peso
No log transform for alto
No log transform for ancho
```

**Si NO ves estos mensajes:** El log-transform NO está aplicado.

**Verificación adicional:** En epoch 1, si grosor y peso tienen R² cercano a 0 o positivo, el log-transform está funcionando. Si tienen R² muy negativo (< -1), NO está funcionando.

### D) Feature Gating Fusion

**Buscar en logs:**
```
Backbone convnext_tiny has XXX features
HybridRegressor created with FEATURE GATING: ... gating_enabled=True
Model has feature gating: True
```

**En cada epoch deberías ver:**
```
Gating %: XX.XX%
```

**Si ves:**
```
Fused features dim = 640
```
**Sin mencionar gating:** Está usando la fusión antigua (concat simple).

**Si ves:**
```
img_proj=512, pix_proj=256, fusion_dim=768, gating_enabled=True
```
**Entonces:** Feature gating está activo.

## 🔍 Verificación Manual

### 1. Verificar que el modelo retorna gating values

En el código, el modelo debe retornar:
```python
outputs, gating_values = model(images, pixel_features)
```

Si solo retorna `outputs`, el feature gating NO está activo.

### 2. Verificar dimensiones

**Pixel features:** Debe ser 10, no 8.

**Fusion dim:** Debe ser 768 (512 + 256), no 640.

### 3. Verificar R² en epoch 1

**Con log-transform y auto-loss:**
- Grosor R²: ~0.0 a +0.3 (no muy negativo)
- Peso R²: ~0.0 a +0.3 (no muy negativo)

**Sin log-transform:**
- Grosor R²: -0.5 a -2.0 (muy negativo)
- Peso R²: -1.0 a -3.0 (muy negativo)

## 🚨 Problemas Comunes

### Problema: "Fused features dim = 640"
**Causa:** Está usando modelo antiguo sin feature gating.
**Solución:** Verificar que `hybrid_v2_training.py` esté usando `create_hybrid_model` del archivo correcto.

### Problema: "Pixel features dimension: 8"
**Causa:** Dataset no tiene compactness y roundness.
**Solución:** Verificar `cacao_dataset.py` líneas 143-146.

### Problema: "R² muy negativo en epoch 1"
**Causa:** Log-transform no aplicado o auto-loss no activo.
**Solución:** Verificar logs de scaler y trainer initialization.

### Problema: "No veo sigmas en logs"
**Causa:** UncertaintyWeightedLoss no está siendo usado.
**Solución:** Verificar que trainer use `self.criterion` (UncertaintyWeightedLoss).

## ✅ Checklist Final

Antes de reportar que algo no funciona, verifica:

- [ ] Logs muestran "UncertaintyWeightedLoss initialized"
- [ ] Logs muestran "LOG_TARGETS: {'grosor', 'peso'}"
- [ ] Logs muestran "Pixel features dimension: 10"
- [ ] Logs muestran "gating_enabled=True"
- [ ] Logs muestran "Sigmas:" en cada epoch
- [ ] Logs muestran "Gating %:" en cada epoch
- [ ] R² de grosor/peso en epoch 1 no es muy negativo (< -0.5)

Si TODOS estos están presentes, las mejoras están aplicadas correctamente.

