# Correcciones Aplicadas a Tests Fallidos

## Resumen
Se han corregido 4 errores críticos. Quedan 70 errores por corregir.

## Correcciones Aplicadas

### 1. `test_get_cacao_images` - Direct assignment to reverse side
**Error**: `TypeError: Direct assignment to the reverse side of a related set is prohibited. Use cacao_images.set() instead.`

**Solución**: Simplificado el test para no intentar asignar directamente al related manager. Ahora simplemente usa el objeto real del lote que ya tiene un related manager vacío.

**Archivo**: `backend/api/tests/test_finca_serializers.py`

### 2. `test_log_user_registration_without_request` - TransactionManagementError
**Error**: `django.db.transaction.TransactionManagementError: An error occurred in the current transaction. You can't execute queries until the end of the 'atomic' block.`

**Solución**: Ajustado el manejo de transacciones, removido `transaction=True` del decorador y usando `transaction.atomic()` explícitamente.

**Archivo**: `backend/api/tests/test_registration_service.py`

### 3. `test_send_verification_email_success` - assert False is True
**Error**: `assert False is True`

**Solución**: Corregido el path del mock de `api.services.auth.registration_service.send_custom_email` a `api.services.email.send_custom_email` ya que la función se importa desde ese módulo.

**Archivo**: `backend/api/tests/test_registration_service.py`

### 4. `test_send_pre_registration_verification_email_*` - assert False is True
**Error**: Similar al anterior, los mocks no estaban funcionando correctamente.

**Solución**: Corregidos los paths de los mocks para usar `api.services.email.send_custom_email`.

**Archivo**: `backend/api/tests/test_registration_service.py`

## Errores Pendientes (70)

### Tests de training_tasks (14 errores)
- Problema: `AttributeError: module does not have the attribute`
- Causa: Los tests están intentando hacer patch de `TrainingJob` que se importa usando `get_model_safely`
- Archivos: `backend/api/tests/test_training_tasks.py`

### Tests de upload_dataset_command (6 errores)
- Problemas:
  - `AssertionError: assert 8 == 4` - El método encuentra más archivos de los esperados
  - `TransactionManagementError` - Problemas con transacciones
- Archivos: `backend/images_app/tests/test_upload_dataset_command.py`

### Tests de vistas (7 errores)
- Problema: `assert 404 in [201, 207]` - Las URLs no están siendo encontradas
- Archivos: `backend/images_app/tests/test_views.py`

### Tests de reports (12 errores)
- Problemas:
  - `AttributeError: module does not have the attribute 'logger'`
  - `AttributeError: module does not have the attribute 'CacaoReport'`
  - `FieldError: Unsupported lookup 'icontains' for ForeignKey`
- Archivos: `backend/reports/tests/test_views.py`, `backend/reports/tests/test_pdf_generator.py`

### Tests de training (varios)
- Múltiples problemas con atributos faltantes y validaciones

## Próximos Pasos

1. Corregir tests de training_tasks - ajustar el patch de TrainingJob
2. Corregir tests de upload_dataset - ajustar conteo de archivos y transacciones
3. Corregir tests de vistas - verificar configuración de URLs
4. Corregir tests de reports - agregar atributos faltantes y corregir lookups

