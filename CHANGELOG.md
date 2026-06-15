# Changelog

## [1.4.0] - 2026-06-15

### Nuevas funcionalidades
- **Infra AWS**: Terraform mínimo viable (S3 + ECR), GitHub Actions CI/CD para deploy automático a ECS en push a `main`
- **MinIO local**: Configuración dual S3/MinIO via `AWS_S3_ENDPOINT_URL` — mismo código corre local y en producción
- **Throttling ML**: `ScopedRateThrottle` en `/scan/` con límite de 30/min configurable via `DRF_THROTTLE_ANALYSIS`
- **Notebook Colab**: Pipeline de entrenamiento completo ejecutable desde Google Colab con sync a S3

### Correcciones
- **Mock silencioso eliminado**: El predictor ML ya no retorna datos falsos (`quality_score: 85.5`) cuando el modelo no carga — ahora lanza `RuntimeError` explícito para evitar análisis inválidos en producción
- `csv_path` movido al `csv_loader` interno donde corresponde (no en `CacaoDatasetLoader`)
- `handle()` en management commands ya no retorna `bool` a Django

### Mejoras de código
- Thresholds ML externalizados a `settings.py` como variables de entorno (`ML_CLASSIFIER_MIN_CONFIDENCE`, `ML_YOLO_VALIDATOR_MIN_CONFIDENCE`, etc.)
- Validación de rango [0, 100] en resultado del predictor antes de persistir en DB
- `float()` para thresholds ML ahora usa fallback con `warnings.warn` en lugar de crash al arrancar

### Frontend — sistema de diseño
- **PRODUCT.md y DESIGN.md**: Contexto de producto y sistema visual documentados para uso con Impeccable
- Eliminados side-tab borders (`border-left: 4px solid`) en `BaseCard`, `DashboardWidget`, notificaciones y recomendaciones — reemplazados por full-border + background tint semántico
- Gradiente text (`background-clip: text`) eliminado de `KPICards`
- Glassmorphism y ghost-card (`border + box-shadow ≥16px`) corregidos en formulario de auth
- Colores no-marca (azul `#3b82f6`, `#3498db`, morado, naranja) migrados a verde primario `#10b981` en CSS globales y componentes
- ARIA: `role="dialog"` + `aria-modal` en `BaseModal`; `aria-invalid` + `aria-describedby` en `BaseInputField` y `BaseFormField`; `role="alert"` en `BaseAlert`; `aria-label` en `BaseSearchBar`
- Motion: tokens de easing (`--ease-out-expo`, `--ease-out-quart`) en `:root`; `@media (prefers-reduced-motion)` global; `transition: all` reemplazado por propiedades específicas en 8 componentes
- CTA "Nuevo Análisis" visible sin scroll en dashboard del agricultor

### Limpieza
- Eliminados exports Figma (CSS/HTML) del repositorio
- Eliminados JSONs de resultados de entrenamiento antiguos (20+ archivos)
- Scripts de sync/upload de modelos a S3 añadidos en `scripts/`
