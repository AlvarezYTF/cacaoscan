# Diagnóstico Completo de la Suite de Tests

## Resumen Ejecutivo

Este documento identifica los problemas reales en la suite de tests del proyecto CacaoScan, ordenados por prioridad y categoría. Se han detectado más de 300 errores relacionados con usuarios duplicados, firmas incorrectas en tasks de Celery, comandos sin mocks adecuados, y problemas de diseño que afectan los tests.

---

## 1. PROBLEMA CRÍTICO: Usuarios Duplicados (IntegrityError)

### Origen del Problema

**Archivo principal:** `backend/conftest.py`

Las fixtures de usuario están creando usuarios con usernames **fijos** que no se limpian entre tests:

```python
@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',  # ❌ Fijo - causa duplicados
        email='test@example.com',
        password=TEST_USER_PASSWORD
    )

@pytest.fixture
def admin_user():
    return User.objects.create_superuser(
        username='admin',  # ❌ Fijo - causa duplicados
        email='admin@example.com',
        password=TEST_ADMIN_PASSWORD
    )

@pytest.fixture
def staff_user():
    user = User.objects.create_user(
        username='staff',  # ❌ Fijo - causa duplicados
        email='staff@example.com',
        password=TEST_STAFF_PASSWORD
    )
```

### Impacto

- **Más de 300 errores** de `IntegrityError: llave duplicada viola restricción de unicidad «auth_user_username_key»`
- Los tests fallan cuando se ejecutan en paralelo o cuando la BD no se limpia correctamente
- 42 archivos de tests crean usuarios con estos mismos usernames fijos

### Archivos Afectados

1. `backend/conftest.py` - Fixtures principales
2. `backend/api/tests/test_realtime_middleware.py` - Crea `testuser` directamente
3. `backend/fincas_app/tests/test_finca_crud_service.py` - Crea `testuser` directamente
4. `backend/fincas_app/tests/test_finca_views.py` - Crea `testuser` directamente
5. Y 38 archivos más que usan estos usernames fijos

### Solución Requerida

1. **Modificar `conftest.py`** para usar usernames únicos (UUID o timestamp)
2. **Buscar y reemplazar** todos los usernames fijos en los 42 archivos afectados
3. **Asegurar limpieza** de BD entre tests (usar `@pytest.mark.django_db` correctamente)

---

## 2. PROBLEMA CRÍTICO: Firmas Incorrectas en Tasks de Celery

### Origen del Problema

**Archivo:** `backend/api/tasks/training_tasks.py`

Las tasks están definidas con `@shared_task(bind=True)`, lo que significa que el primer parámetro es `self` (la instancia de la task):

```python
@shared_task(bind=True, name='api.tasks.train_model')
def train_model_task(self, job_id: str, config: dict) -> Dict[str, Any]:
    # self es el primer parámetro cuando bind=True
    pass

@shared_task(bind=True, name='api.tasks.auto_train_model')
def auto_train_model_task(self, force: bool = False, config: Optional[dict] = None) -> Dict[str, Any]:
    # self es el primer parámetro cuando bind=True
    pass
```

### Errores Detectados

1. **`train_model_task() takes 3 positional arguments but 4 were given`**
   - Los tests están llamando: `train_model_task(job_id, config)` 
   - Pero debería ser: `train_model_task(self, job_id, config)`

2. **`auto_train_model_task() takes from 1 to 3 positional arguments but 4 were given`**
   - Similar problema con la firma

### Archivos Afectados

1. `backend/api/tests/test_training_tasks.py` - Usa `unwrap_celery_task()` pero algunos tests pueden estar llamando incorrectamente
2. `backend/api/tests/test_training_tasks_additional.py` - Tests marcados como `@pytest.mark.skip` por problemas de binding
3. `backend/api/tests/test_training_views.py` - Puede estar llamando tasks incorrectamente

### Solución Requerida

1. **Verificar** que todos los tests usen `unwrap_celery_task()` o llamen correctamente con `self`
2. **Revisar** tests que llaman directamente a las tasks sin considerar `bind=True`
3. **Actualizar** `test_training_tasks_additional.py` para usar el mismo patrón que `test_training_tasks.py`

---

## 3. PROBLEMA: Comando train_unet_background sin Mocks Adecuados

### Origen del Problema

**Archivo:** `backend/training/management/commands/train_unet_background.py`

El comando importa `torch` directamente en el método `_setup_training()`:

```python
def _setup_training(self, ...):
    import torch  # ❌ Importación directa sin mock
    from torch.utils.data import DataLoader
    from torch import nn, optim
    
    # Usa torch.cuda.is_available(), torch.cuda.get_device_name(), etc.
```

### Error Detectado

**`module 'training.management.commands.train_unet_background' has no attribute 'torch'`**

Los tests intentan mockear `torch` pero el módulo no tiene el atributo porque se importa dentro del método.

### Archivo Afectado

1. `backend/training/tests/test_train_unet_background_command.py` - Tests que intentan mockear `torch`

### Solución Requerida

1. **Mover** la importación de `torch` al nivel del módulo o usar `patch` en el lugar correcto
2. **Actualizar** los tests para mockear `torch` correctamente usando `patch('torch.cuda.is_available')` o similar
3. **Considerar** hacer la importación condicional o usar un patrón de inyección de dependencias

---

## 4. PROBLEMA: Tests que Esperan Logs y No se Ejecutan

### Origen del Problema

**Archivos afectados:** Varios tests esperan que se llamen métodos de logging pero los mocks no están configurados correctamente.

### Errores Detectados

**`AssertionError: Expected 'info' to have been called once. Called 0 times.`**

### Archivos Afectados

1. `backend/reports/tests/test_views.py` - Líneas 164, 183, 494
   - `mock_logger.info.assert_called_once()`
   - `mock_logger.error.assert_called_once()`

### Solución Requerida

1. **Verificar** que los mocks de logger estén configurados antes de ejecutar el código
2. **Asegurar** que el código bajo prueba realmente llame a los métodos de logging
3. **Revisar** que los patches estén aplicados en el orden correcto

---

## 5. PROBLEMA: Errores de StopIteration

### Origen del Problema

Probablemente relacionado con iteradores en tests o código que usa `next()` sin manejar `StopIteration`.

### Archivos Afectados

1. `backend/api/utils/pagination.py` - Puede tener problemas con iteradores
2. Tests que usan `next()` o `iter()` sin manejo adecuado

### Solución Requerida

1. **Buscar** usos de `next()` sin try/except
2. **Revisar** iteradores en código de paginación
3. **Asegurar** manejo adecuado de `StopIteration`

---

## 6. PROBLEMA: Errores de Regex

### Origen del Problema

Aunque ya se corrigieron algunos problemas de ReDoS en el frontend, pueden existir problemas similares en el backend o tests que usan regex incorrectamente.

### Archivos Afectados

- Tests que usan `match=` en `pytest.raises()` con patrones regex que no coinciden

### Solución Requerida

1. **Revisar** todos los `pytest.raises(..., match=...)` para asegurar que los patrones regex coincidan
2. **Verificar** que los mensajes de error coincidan con los patrones esperados

---

## 7. PROBLEMA: Errores de Paginación

### Origen del Problema

**Archivo:** `backend/api/utils/pagination.py`

El código tiene lógica compleja para manejar mocks y querysets reales, lo que puede causar problemas en tests.

### Archivos Afectados

1. `backend/api/tests/test_pagination.py` - Tests de paginación
2. Cualquier test que use `paginate_queryset()` con mocks

### Solución Requerida

1. **Revisar** la lógica de detección de mocks en `_is_mock_queryset()`
2. **Asegurar** que los tests usen querysets reales cuando sea posible
3. **Verificar** que los mocks tengan todos los atributos necesarios

---

## TODOs ORDENADOS POR PRIORIDAD

### PRIORIDAD CRÍTICA (Resolver primero)

#### 1. Fixtures - Usuarios Duplicados

**Archivo:** `backend/conftest.py`

**Cambios requeridos:**
- [ ] Modificar fixture `user()` para usar username único (UUID o timestamp)
- [ ] Modificar fixture `admin_user()` para usar username único
- [ ] Modificar fixture `staff_user()` para usar username único
- [ ] Asegurar que las fixtures usen `@pytest.fixture(scope='function')` explícitamente

**Archivos adicionales a modificar:**
- [ ] Buscar y reemplazar todos los `username='testuser'` en 42 archivos de tests
- [ ] Buscar y reemplazar todos los `username='admin'` en tests
- [ ] Buscar y reemplazar todos los `username='staff'` en tests
- [ ] Crear función helper `generate_unique_username()` para reutilizar

**Comando para buscar:**
```bash
grep -r "username=['\"]testuser['\"]" backend/
grep -r "username=['\"]admin['\"]" backend/
grep -r "username=['\"]staff['\"]" backend/
```

---

#### 2. Tasks - Firmas de Celery

**Archivo:** `backend/api/tasks/training_tasks.py`

**Verificaciones requeridas:**
- [ ] Confirmar que `train_model_task` tiene `bind=True` y acepta `self` como primer parámetro
- [ ] Confirmar que `auto_train_model_task` tiene `bind=True` y acepta `self` como primer parámetro
- [ ] Documentar claramente la firma esperada en docstrings

**Archivos de tests a modificar:**
- [ ] `backend/api/tests/test_training_tasks.py` - Verificar que todos los tests usen `unwrap_celery_task()` correctamente
- [ ] `backend/api/tests/test_training_tasks_additional.py` - Remover `@pytest.mark.skip` y usar patrón correcto
- [ ] `backend/api/tests/test_training_views.py` - Verificar llamadas a tasks

**Cambios específicos:**
- [ ] Asegurar que `unwrap_celery_task()` funcione correctamente con `bind=True`
- [ ] Todos los tests deben pasar `mock_task` como primer argumento cuando llamen directamente
- [ ] Verificar que los tests no asuman que las tasks son funciones normales

---

### PRIORIDAD ALTA

#### 3. Commands - Mocks de torch

**Archivo:** `backend/training/management/commands/train_unet_background.py`

**Cambios requeridos:**
- [ ] Mover importación de `torch` al nivel del módulo (opcional, para facilitar mocking)
- [ ] O mantener importación local pero actualizar tests para mockear correctamente
- [ ] Considerar usar inyección de dependencias para `torch` (opcional, mejora de diseño)

**Archivo de tests:**
- [ ] `backend/training/tests/test_train_unet_background_command.py`
  - [ ] Actualizar `test_setup_training_cpu()` para mockear `torch` correctamente
  - [ ] Actualizar `test_setup_training_gpu()` para mockear `torch` correctamente
  - [ ] Usar `@patch('torch.cuda.is_available')` en lugar de `@patch('builtins.__import__')`
  - [ ] Mockear `torch.utils.data.DataLoader` correctamente
  - [ ] Mockear `torch.nn.BCELoss` y `torch.optim.Adam` correctamente

---

#### 4. Tests - Logs No Llamados

**Archivos afectados:**
- `backend/reports/tests/test_views.py`

**Cambios requeridos:**
- [ ] Verificar que los mocks de logger se configuren antes de ejecutar el código
- [ ] Asegurar que el código bajo prueba realmente llame a los métodos de logging
- [ ] Revisar el orden de los decoradores `@patch` para asegurar que se apliquen correctamente
- [ ] Considerar usar `@patch.object` en lugar de `@patch` si es necesario

**Líneas específicas a revisar:**
- [ ] Línea 164: `mock_logger.info.assert_called_once()`
- [ ] Línea 183: `mock_logger.error.assert_called_once()`
- [ ] Línea 494: `mock_logger.error.assert_called_once()`

---

### PRIORIDAD MEDIA

#### 5. Pagination - Manejo de Mocks

**Archivo:** `backend/api/utils/pagination.py`

**Cambios requeridos:**
- [ ] Revisar función `_is_mock_queryset()` para asegurar detección correcta
- [ ] Asegurar que `_handle_mock_queryset()` retorne estructura válida
- [ ] Verificar que `_handle_real_queryset()` maneje correctamente querysets reales
- [ ] Documentar claramente el comportamiento esperado con mocks vs reales

**Archivo de tests:**
- [ ] `backend/api/tests/test_pagination.py`
  - [ ] Verificar que `test_paginate_queryset_mock_queryset()` funcione correctamente
  - [ ] Asegurar que los mocks tengan todos los atributos necesarios
  - [ ] Considerar usar querysets reales en más tests para evitar problemas de mocks

---

#### 6. StopIteration - Manejo de Iteradores

**Archivos a revisar:**
- `backend/api/utils/pagination.py`
- Cualquier código que use `next()` o `iter()`

**Cambios requeridos:**
- [ ] Buscar todos los usos de `next()` sin try/except
- [ ] Asegurar manejo adecuado de `StopIteration`
- [ ] Considerar usar valores por defecto en `next(iterator, default)` cuando sea apropiado

---

#### 7. Regex - Patrones que No Coinciden

**Archivos a revisar:**
- Todos los tests que usan `pytest.raises(..., match=...)`

**Cambios requeridos:**
- [ ] Buscar todos los `pytest.raises(..., match=...)` en tests
- [ ] Verificar que los patrones regex coincidan con los mensajes de error reales
- [ ] Considerar usar strings simples en lugar de regex cuando sea posible
- [ ] Asegurar que los mensajes de error sean consistentes

---

### PRIORIDAD BAJA (Mejoras de Diseño)

#### 8. Services - Revisar Patrones de Testing

**Archivos afectados:**
- Todos los archivos en `backend/*/tests/test_*_service.py`

**Mejoras sugeridas:**
- [ ] Estandarizar el uso de fixtures entre archivos de tests
- [ ] Crear factories reutilizables para modelos comunes
- [ ] Documentar patrones de testing preferidos

---

#### 9. Serializers - Tests de Validación

**Archivos afectados:**
- `backend/api/tests/test_finca_serializers.py`
- `backend/personas/tests/test_personas_serializers.py`
- Otros tests de serializers

**Mejoras sugeridas:**
- [ ] Asegurar que los tests de serializers usen datos únicos
- [ ] Revisar que los mocks de serializers estén configurados correctamente

---

#### 10. Mixins - Tests de Permisos

**Archivos afectados:**
- `backend/images_app/tests/test_image_mixins.py`
- `backend/api/tests/test_owner_mixin.py`

**Mejoras sugeridas:**
- [ ] Asegurar que los tests de mixins usen usuarios únicos
- [ ] Verificar que los mocks de permisos funcionen correctamente

---

## Resumen de Archivos a Modificar

### Archivos Críticos (Modificar primero)
1. `backend/conftest.py` - Fixtures de usuarios
2. `backend/api/tests/test_training_tasks.py` - Tests de tasks
3. `backend/api/tests/test_training_tasks_additional.py` - Tests adicionales de tasks
4. `backend/training/tests/test_train_unet_background_command.py` - Tests de comando
5. `backend/reports/tests/test_views.py` - Tests de logs

### Archivos de Alto Impacto (42 archivos con usernames fijos)
- Todos los archivos que crean usuarios con `username='testuser'`, `'admin'`, o `'staff'`

### Archivos de Soporte
1. `backend/api/utils/pagination.py` - Utilidades de paginación
2. `backend/api/tasks/training_tasks.py` - Tasks de Celery (verificar firmas)
3. `backend/training/management/commands/train_unet_background.py` - Comando (revisar imports)

---

## Estrategia de Implementación Recomendada

1. **Fase 1: Usuarios Duplicados** (Crítico)
   - Modificar `conftest.py`
   - Buscar y reemplazar usernames fijos en batches
   - Ejecutar tests después de cada batch

2. **Fase 2: Tasks de Celery** (Crítico)
   - Verificar firmas de tasks
   - Actualizar tests para usar patrón correcto
   - Remover skips de tests

3. **Fase 3: Comandos y Logs** (Alto)
   - Arreglar mocks de torch
   - Arreglar tests de logs

4. **Fase 4: Paginación y Otros** (Medio)
   - Revisar paginación
   - Arreglar StopIteration
   - Arreglar regex

---

## Notas Finales

- **NO aplicar cambios aún** - Este es solo el diagnóstico
- Todos los cambios deben ser **mínimos y enfocados**
- Respetar el estilo y patrones del código existente
- Usar tipado estricto en todos los cambios
- Asegurar que los tests pasen después de cada cambio

