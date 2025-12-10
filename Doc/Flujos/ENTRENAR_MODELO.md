# Flujo Completo: Entrenar Modelo (Frontend → Backend)

## Resumen del Flujo

El flujo de entrenamiento de modelos permite a un administrador o técnico iniciar el proceso de entrenamiento automático de los modelos de inteligencia artificial del sistema.

**Endpoint:** `POST /api/v1/ml/auto-train/` o `POST /api/v1/training/train/`

**Autenticación:** Requerida (IsAuthenticated, rol Administrador o Técnico)

**Flujo:**
1. Administrador accede a sección "Entrenamiento de Modelos"
2. Administrador configura parámetros (épocas, batch size, modelo)
3. Frontend envía POST con configuración
4. Backend valida permisos y parámetros
5. Backend valida que el dataset esté disponible
6. Backend crea tarea asíncrona (Celery) para entrenamiento
7. Backend retorna `task_id` para seguimiento
8. Frontend monitorea progreso mediante polling
9. Backend entrena modelo en segundo plano
10. Backend guarda modelo entrenado cuando completa

**Parámetros:**
- `model_type`: Tipo de modelo (unet, regression, hybrid)
- `epochs`: Número de épocas
- `batch_size`: Tamaño de batch
- `use_pixel_features`: Usar características de píxeles (sí/no)
- `dataset_id`: ID del dataset (opcional)

**Respuesta:**
```json
{
  "task_id": "uuid-task-id",
  "status": "pending",
  "message": "Entrenamiento iniciado"
}
```

**Monitoreo:**
- Endpoint: `GET /api/v1/tasks/{task_id}/status/`
- Estados: pending, processing, completed, failed
- Métricas: loss, accuracy, epoch actual

**Tests:**
```bash
pytest api/tests/test_training_views.py::TestTrainingView::test_post_success -v
pytest ml/tests/test_training.py -v
```

