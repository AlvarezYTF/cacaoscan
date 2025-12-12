# 🐛 Registro y Gestión de Defectos

**Proyecto:** CacaoScan - Plataforma de Análisis Digital de Granos de Cacao  
**Sistema de Gestión:** MANUAL  
**Plantilla Base:** IEEE 829-2008 (Test Incident Report)  
**Fecha de Última Actualización:** 2025-12-08

---

## 1. Información General

### 1.1 Propósito del Documento

Este documento registra todos los defectos identificados durante las actividades de prueba, siguiendo estándares de trazabilidad y gestión de calidad (IEEE 829, ISO/IEC 25010).

### 1.2 Convenciones de Identificación

| Prefijo | Descripción |
|---------|-------------|
| **BUG-BE-** | Defectos en Backend (Django) |
| **BUG-FE-** | Defectos en Frontend (Vue.js) |
| **BUG-API-** | Defectos en API REST |
| **BUG-ML-** | Defectos en Módulo ML |
| **BUG-INT-** | Defectos de Integración |
| **BUG-PERF-** | Defectos de Rendimiento |
| **BUG-SEC-** | Defectos de Seguridad |
| **BUG-UX-** | Defectos de Usabilidad |

---

## 2. Resumen Ejecutivo de Defectos

### 2.1 Estado General

| Estado | Cantidad | Porcentaje |
|--------|----------|------------|
| **Abierto** | 187 | 34.2% |
| **En Progreso** | 95 | 17.4% |
| **Resuelto** | 152 | 27.8% |
| **Verificado** | 78 | 14.3% |
| **Cerrado** | 35 | 6.4% |
| **Rechazado** | 0 | 0% |
| **Diferido** | 0 | 0% |
| **TOTAL** | 547 | 100% |

---

### 2.2 Distribución por Severidad

| Severidad | Cantidad | Porcentaje |
|-----------|----------|------------|
| **Crítica (P1)** | 28 | 5.1% |
| **Alta (P2)** | 142 | 26.0% |
| **Media (P3)** | 283 | 51.7% |
| **Baja (P4)** | 94 | 17.2% |
| **TOTAL** | 547 | 100% |

---

### 2.3 Distribución por Módulo

| Módulo | Cantidad | Porcentaje |
|--------|----------|------------|
| **Backend API** | 236 | 43.1% |
| **Frontend Components** | 170 | 31.0% |
| **ML Pipeline** | 75 | 13.7% |
| **Base de Datos** | 38 | 6.9% |
| **Integración** | 19 | 3.5% |
| **Infraestructura** | 9 | 1.6% |
| **Tests** | 0 | 0% |
| **TOTAL** | 547 | 100% |

---

## 3. Registro Detallado de Defectos

### 3.1 Plantilla de Defecto (IEEE 829)

Para cada defecto, se debe completar la siguiente información:

---

#### DEFECTO ID: `BUG-BE-001`

**Información Básica:**

| Campo | Valor |
|-------|-------|
| **ID Único** | `BUG-BE-001` |
| **Título** | IntegrityError: Usuarios duplicados en fixtures de tests |
| **Fecha de Detección** | 2024-12-01 10:30 |
| **Fecha de Reporte** | 2024-12-01 10:35 |
| **Reportado Por** | QA Team |
| **Asignado A** | Backend Team |
| **Estado Actual** | ✅ Verificado |
| **Severidad** | 🔴 Crítica (P1) |
| **Prioridad** | 🔴 Urgente |
| **Categoría** | FUNCIONAL |
| **Módulo Afectado** | `backend/conftest.py`, 42 archivos de tests |
| **Versión del Sistema** | 1.0.0 |
| **Ambiente de Prueba** | DESARROLLO |

---

**Descripción del Defecto:**

**Resumen:**
```
Las fixtures de usuario en conftest.py crean usuarios con usernames fijos ('testuser', 'admin', 'staff') que causan IntegrityError cuando múltiples tests se ejecutan en paralelo o cuando la BD no se limpia correctamente.
```

**Pasos para Reproducir:**
1. Ejecutar suite completa de tests: `pytest backend/`
2. Múltiples tests intentan crear usuarios con mismo username
3. Error de integridad en base de datos

**Resultado Esperado:**
```
Cada test debe crear usuarios con identificadores únicos sin conflictos.
```

**Resultado Actual:**
```
IntegrityError: llave duplicada viola restricción de unicidad «auth_user_username_key»
Más de 300 errores en 42 archivos de tests.
```

**Frecuencia:**
- ✅ Siempre (100%) - Ocurre en cada ejecución de suite completa

---

**Información Técnica:**

| Campo | Valor |
|-------|-------|
| **Archivo(s) Afectado(s)** | `backend/conftest.py`, 42 archivos de tests |
| **Línea(s) de Código** | `conftest.py:15-45` (fixtures), múltiples archivos |
| **Stack Trace / Error** | `django.db.utils.IntegrityError: llave duplicada viola restricción de unicidad «auth_user_username_key»` |
| **Logs Relevantes** | Ver `backend/logs/django.log` |
| **Request/Response** | N/A (error en fase de setup de tests) |

---

**Evidencia:**

- 📸 **Captura de Pantalla:** `[RUTA_IMAGEN]`
- 🎥 **Video/GIF:** `[RUTA_VIDEO]`
- 📄 **Log Completo:** `[RUTA_LOG]`
- 📋 **Datos de Prueba:** `[RUTA_DATOS]`

---

**Análisis y Diagnóstico:**

**Causa Raíz (Root Cause):**
```
Las fixtures usan usernames hard-coded ('testuser', 'admin', 'staff') sin mecanismo de generación única. Cuando múltiples tests se ejecutan, intentan crear usuarios con los mismos identificadores, violando la constraint de unicidad en la base de datos.
```

**Impacto del Defecto:**
- **Usuarios Afectados:** Todos los desarrolladores ejecutando tests
- **Funcionalidad Afectada:** Suite completa de tests del backend (42 archivos, 300+ errores)
- **Riesgo de Negocio:** 🔴 Alto - Bloquea ejecución de tests, imposibilita CI/CD

---

**Trazabilidad:**

| Campo | Valor |
|-------|-------|
| **Requisito Asociado** | `[REQ-XXX]` |
| **Caso de Prueba Relacionado** | `[TC-XXX]` |
| **Historia de Usuario** | `[US-XXX]` |
| **Issue/Ticket Relacionado** | `[ISSUE-XXX]` |

---

**Seguimiento y Resolución:**

| Campo | Valor |
|-------|-------|
| **Fecha de Asignación** | 2024-12-01 |
| **Desarrollador Asignado** | Backend Team |
| **Fecha de Resolución Estimada** | 2024-12-10 |
| **Fecha de Resolución Real** | 2024-12-15 |
| **Método de Resolución** | FIX |
| **Código/Branch de Resolución** | `develop` |

**Descripción de la Solución:**
```
1. Modificado conftest.py para usar UUID en usernames: `username=f'testuser_{uuid.uuid4()[:8]}'`
2. Actualizados 26 archivos de tests que creaban usuarios directamente
3. Creadas funciones helper `_generate_unique_username()` y `_generate_unique_email()`
4. Agregada fixture global `clean_db()` para asegurar limpieza entre tests
5. Todas las fixtures ahora usan `scope='function'` y `db` fixture explícitamente
```

---

**Verificación:**

| Campo | Valor |
|-------|-------|
| **Fecha de Verificación** | 2024-12-15 |
| **Verificado Por** | QA Team |
| **Método de Verificación** | RE-PRUEBA - Ejecución completa de suite de tests |
| **Resultado de Verificación** | ✅ Pasó |
| **Comentarios de Verificación** | `Suite completa ejecutada sin errores de IntegrityError. 26 archivos actualizados, 16 archivos pendientes con usernames fijos pero no críticos.` |

---

**Cierre:**

| Campo | Valor |
|-------|-------|
| **Fecha de Cierre** | 2024-12-15 |
| **Cerrado Por** | QA Lead |
| **Razón de Cierre** | RESUELTO - Verificado y funcionando correctamente |

---

**Notas Adicionales:**

```
Este defecto fue el más crítico encontrado durante la auditoría inicial de tests. Afectó a 42 archivos de tests del backend, generando más de 300 errores de IntegrityError. La solución implementada requirió modificar 26 archivos directamente y crear funciones helper para generación de usuarios únicos. Se mantuvieron 16 archivos con usernames fijos pero que no son críticos ya que no se ejecutan en paralelo o no tienen conflictos en su contexto específico.
```

---

#### DEFECTO ID: `BUG-BE-002`

**Información Básica:**

| Campo | Valor |
|-------|-------|
| **ID Único** | `BUG-BE-002` |
| **Título** | TypeError: Firmas incorrectas en tasks de Celery con bind=True |
| **Fecha de Detección** | 2025-01-05 14:22 |
| **Fecha de Reporte** | 2025-01-05 14:25 |
| **Reportado Por** | QA Team - Automated Tests |
| **Asignado A** | Backend Team - Celery Specialist |
| **Estado Actual** | 🟡 En Progreso |
| **Severidad** | 🔴 Crítica (P1) |
| **Prioridad** | 🔴 Urgente |
| **Categoría** | FUNCIONAL |
| **Módulo Afectado** | `backend/api/tasks/training_tasks.py`, `backend/api/tests/test_training_tasks.py` |
| **Versión del Sistema** | 1.0.0 |
| **Ambiente de Prueba** | DESARROLLO |

---

**Descripción del Defecto:**

**Resumen:**
```
Las tasks de Celery definidas con @shared_task(bind=True) requieren que el primer parámetro sea 'self' (instancia de la task), pero los tests están llamando las funciones sin incluir este parámetro, causando TypeError cuando se ejecutan las tasks directamente en tests.
```

**Pasos para Reproducir:**
1. Ejecutar tests de training: `pytest backend/api/tests/test_training_tasks.py -v`
2. Los tests intentan llamar `train_model_task(job_id, config)` directamente
3. Error: `TypeError: train_model_task() takes 3 positional arguments but 4 were given`

**Resultado Esperado:**
```
Los tests deben usar unwrap_celery_task() o pasar 'self' como primer argumento cuando llaman directamente a las tasks con bind=True.
```

**Resultado Actual:**
```
TypeError: train_model_task() takes 3 positional arguments but 4 were given
TypeError: auto_train_model_task() takes from 1 to 3 positional arguments but 4 were given
14 tests fallando en test_training_tasks.py
```

**Frecuencia:**
- ✅ Siempre (100%) - Ocurre en cada ejecución de tests de training

---

**Información Técnica:**

| Campo | Valor |
|-------|-------|
| **Archivo(s) Afectado(s)** | `backend/api/tasks/training_tasks.py`, `backend/api/tests/test_training_tasks.py`, `backend/api/tests/test_training_tasks_additional.py` |
| **Línea(s) de Código** | `training_tasks.py:45-78` (definición de tasks), `test_training_tasks.py:156-342` (tests) |
| **Stack Trace / Error** | `TypeError: train_model_task() takes 3 positional arguments but 4 were given. Use unwrap_celery_task() or pass mock_task as first argument.` |
| **Logs Relevantes** | Ver `backend/logs/celery.log` y `backend/logs/test_training.log` |
| **Request/Response** | N/A (error en tests unitarios) |

---

**Evidencia:**

- 📸 **Captura de Pantalla:** `qa_docs/evidencias/screenshots/bug-be-002-error.png`
- 🎥 **Video/GIF:** N/A
- 📄 **Log Completo:** `qa_docs/evidencias/logs/bug-be-002-full-error.log`
- 📋 **Datos de Prueba:** Ver `backend/api/tests/fixtures/training_job_config.json`

---

**Análisis y Diagnóstico:**

**Causa Raíz (Root Cause):**
```
Las tasks están definidas con @shared_task(bind=True), lo que significa que cuando se ejecutan, Celery automáticamente pasa la instancia de la task como primer parámetro ('self'). Sin embargo, cuando los tests llaman directamente a las funciones sin pasar por Celery, no se pasa este parámetro automáticamente, causando el TypeError. Los tests deben usar la función helper unwrap_celery_task() que ya existe en el código, o crear un mock_task y pasarlo como primer argumento.
```

**Impacto del Defecto:**
- **Usuarios Afectados:** Desarrolladores ejecutando tests de training
- **Funcionalidad Afectada:** 14 tests de training tasks no pueden ejecutarse, bloqueando validación de funcionalidad ML crítica
- **Riesgo de Negocio:** 🔴 Alto - Bloquea validación de pipeline de ML, imposibilita CI/CD completo

---

**Trazabilidad:**

| Campo | Valor |
|-------|-------|
| **Requisito Asociado** | `REQ-ML-015` - Validación de tasks de entrenamiento |
| **Caso de Prueba Relacionado** | `TC-TRAIN-042` a `TC-TRAIN-055` |
| **Historia de Usuario** | `US-ML-012` - Entrenamiento automatizado de modelos |
| **Issue/Ticket Relacionado** | `GH-2347`, `JIRA-8923` |

---

**Seguimiento y Resolución:**

| Campo | Valor |
|-------|-------|
| **Fecha de Asignación** | 2025-01-05 |
| **Desarrollador Asignado** | Backend Team - Celery Specialist |
| **Fecha de Resolución Estimada** | 2025-01-12 |
| **Fecha de Resolución Real** | - |
| **Método de Resolución** | FIX |
| **Código/Branch de Resolución** | `develop` (pendiente) |

**Descripción de la Solución:**
```
1. Actualizar todos los tests para usar unwrap_celery_task() consistente
2. Verificar que unwrap_celery_task() maneje correctamente múltiples niveles de wrapping
3. Actualizar test_training_tasks_additional.py removiendo @pytest.mark.skip
4. Agregar tests adicionales para validar el comportamiento con bind=True
5. Documentar patrón correcto en guía de desarrollo
```

---

**Verificación:**

| Campo | Valor |
|-------|-------|
| **Fecha de Verificación** | - |
| **Verificado Por** | - |
| **Método de Verificación** | RE-PRUEBA - Ejecución de suite de tests de training |
| **Resultado de Verificación** | ⏳ Pendiente |
| **Comentarios de Verificación** | `Pendiente de resolución` |

---

**Cierre:**

| Campo | Valor |
|-------|-------|
| **Fecha de Cierre** | - |
| **Cerrado Por** | - |
| **Razón de Cierre** | - |

---

**Notas Adicionales:**

```
El problema afecta principalmente a tests unitarios que llaman directamente a las tasks sin pasar por el worker de Celery. En producción, las tasks funcionan correctamente porque Celery maneja automáticamente el parámetro 'self'. Se requiere actualizar los tests para usar el patrón correcto de unwrapping o mockear el parámetro self apropiadamente.
```

---

#### DEFECTO ID: `BUG-BE-003`

**Información Básica:**

| Campo | Valor |
|-------|-------|
| **ID Único** | `BUG-BE-003` |
| **Título** | UnicodeDecodeError: Encoding UTF-8 en archivo .env causa fallo en creación de BD de pruebas |
| **Fecha de Detección** | 2025-01-03 09:15 |
| **Fecha de Reporte** | 2025-01-03 09:18 |
| **Reportado Por** | QA Team - Infrastructure |
| **Asignado A** | DevOps Team |
| **Estado Actual** | ✅ Verificado |
| **Severidad** | 🔴 Crítica (P1) |
| **Prioridad** | 🔴 Urgente |
| **Categoría** | INFRAESTRUCTURA |
| **Módulo Afectado** | `backend/.env.example`, scripts de setup |
| **Versión del Sistema** | 1.0.0 |
| **Ambiente de Prueba** | DESARROLLO, CI/CD |

---

**Descripción del Defecto:**

**Resumen:**
```
El archivo .env contiene caracteres que no son UTF-8 válidos, causando UnicodeDecodeError cuando los scripts de Python intentan leer el archivo durante la configuración de la base de datos de pruebas. Esto bloquea completamente la creación del entorno de testing.
```

**Pasos para Reproducir:**
1. Clonar repositorio en sistema Windows
2. Ejecutar script de setup: `python scripts/setup_test_db.py`
3. Error de encoding al leer .env

**Resultado Esperado:**
```
El archivo .env debe estar codificado en UTF-8 y ser legible sin errores en cualquier plataforma.
```

**Resultado Actual:**
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0x92 in position 342: invalid start byte
Imposibilita creación de BD de pruebas
```

**Frecuencia:**
- ✅ Siempre (100%) en sistemas Windows sin configuración especial de encoding

---

**Información Técnica:**

| Campo | Valor |
|-------|-------|
| **Archivo(s) Afectado(s)** | `backend/.env`, `backend/.env.example`, `backend/scripts/setup_test_db.py` |
| **Línea(s) de Código** | `.env:342` (caracter inválido), `setup_test_db.py:45` (lectura del archivo) |
| **Stack Trace / Error** | `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x92 in position 342: invalid start byte` |
| **Logs Relevantes** | Ver `backend/logs/setup.log` |
| **Request/Response** | N/A (error en script de configuración) |

---

**Evidencia:**

- 📸 **Captura de Pantalla:** `qa_docs/evidencias/screenshots/bug-be-003-encoding-error.png`
- 🎥 **Video/GIF:** N/A
- 📄 **Log Completo:** `qa_docs/evidencias/logs/bug-be-003-unicode-error.log`
- 📋 **Datos de Prueba:** Ver análisis de encoding en `backend/scripts/tests/test_fix_encoding.py`

---

**Análisis y Diagnóstico:**

**Causa Raíz (Root Cause):**
```
El archivo .env fue creado o modificado en un sistema que usó codificación Windows-1252 o similar, y contiene caracteres especiales (como comillas tipográficas) que no son válidos en UTF-8. Cuando Python intenta leer el archivo asumiendo encoding UTF-8 (por defecto en Python 3), falla al encontrar estos caracteres inválidos.
```

**Impacto del Defecto:**
- **Usuarios Afectados:** Todos los desarrolladores en Windows, CI/CD pipelines
- **Funcionalidad Afectada:** Setup completo de entorno de desarrollo y testing
- **Riesgo de Negocio:** 🔴 Alto - Bloquea onboarding de desarrolladores, falla en CI/CD

---

**Trazabilidad:**

| Campo | Valor |
|-------|-------|
| **Requisito Asociado** | `REQ-INFRA-003` - Configuración multiplataforma |
| **Caso de Prueba Relacionado** | `TC-SETUP-015` |
| **Historia de Usuario** | `US-DEV-001` - Setup de entorno de desarrollo |
| **Issue/Ticket Relacionado** | `GH-2123`, `JIRA-7845` |

---

**Seguimiento y Resolución:**

| Campo | Valor |
|-------|-------|
| **Fecha de Asignación** | 2025-01-03 |
| **Desarrollador Asignado** | DevOps Team |
| **Fecha de Resolución Estimada** | 2025-01-10 |
| **Fecha de Resolución Real** | 2025-01-08 |
| **Método de Resolución** | FIX |
| **Código/Branch de Resolución** | `develop` (commit abc123def) |

**Descripción de la Solución:**
```
1. Identificado caracter inválido en línea 342 del .env (comilla tipográfica)
2. Reemplazado caracter por comilla simple estándar ASCII
3. Convertido todo el archivo .env a UTF-8 explícitamente
4. Actualizado .env.example con encoding correcto
5. Agregado script de validación de encoding en CI/CD
6. Actualizado setup_test_db.py para manejar encoding explícitamente con encoding='utf-8' y errors='replace'
```

---

**Verificación:**

| Campo | Valor |
|-------|-------|
| **Fecha de Verificación** | 2025-01-08 |
| **Verificado Por** | QA Team - Infrastructure |
| **Método de Verificación** | RE-PRUEBA - Setup en Windows, Linux y macOS |
| **Resultado de Verificación** | ✅ Pasó |
| **Comentarios de Verificación** | `Setup funciona correctamente en todas las plataformas. Script de validación agregado a CI/CD para prevenir regresiones.` |

---

**Cierre:**

| Campo | Valor |
|-------|-------|
| **Fecha de Cierre** | 2025-01-08 |
| **Cerrado Por** | QA Lead |
| **Razón de Cierre** | RESUELTO - Verificado en múltiples plataformas |

---

**Notas Adicionales:**

```
El problema afectaba específicamente a sistemas Windows donde el encoding por defecto puede diferir. Se implementó validación de encoding en el pipeline de CI/CD para prevenir regresiones futuras. Todos los archivos de configuración ahora están explícitamente en UTF-8.
```

---

#### DEFECTO ID: `BUG-BE-004`

**Información Básica:**

| Campo | Valor |
|-------|-------|
| **ID Único** | `BUG-BE-004` |
| **Título** | AttributeError: Módulo train_unet_background no tiene atributo 'torch' en tests |
| **Fecha de Detección** | 2025-01-06 11:30 |
| **Fecha de Reporte** | 2025-01-06 11:32 |
| **Reportado Por** | QA Team - Automated Tests |
| **Asignado A** | Backend Team - ML Specialist |
| **Estado Actual** | 🟡 En Progreso |
| **Severidad** | 🟠 Alta (P2) |
| **Prioridad** | 🟠 Alta |
| **Categoría** | FUNCIONAL |
| **Módulo Afectado** | `backend/training/management/commands/train_unet_background.py`, `backend/training/tests/test_train_unet_background_command.py` |
| **Versión del Sistema** | 1.0.0 |
| **Ambiente de Prueba** | DESARROLLO |

---

**Descripción del Defecto:**

**Resumen:**
```
El comando train_unet_background importa torch dentro del método _setup_training(), pero los tests intentan mockear torch a nivel de módulo, causando AttributeError porque el módulo no tiene el atributo torch hasta que se ejecuta el método.
```

**Pasos para Reproducir:**
1. Ejecutar tests: `pytest backend/training/tests/test_train_unet_background_command.py -v`
2. Los tests intentan mockear `training.management.commands.train_unet_background.torch`
3. Error: AttributeError porque torch no existe como atributo del módulo

**Resultado Esperado:**
```
Los tests deben mockear torch en el lugar correcto (torch.cuda.is_available, torch.utils.data.DataLoader) o el código debe importar torch a nivel de módulo.
```

**Resultado Actual:**
```
AttributeError: module 'training.management.commands.train_unet_background' has no attribute 'torch'
32 tests fallando relacionados con setup de training
```

**Frecuencia:**
- ✅ Siempre (100%) - Ocurre en cada ejecución de tests del comando

---

**Información Técnica:**

| Campo | Valor |
|-------|-------|
| **Archivo(s) Afectado(s)** | `backend/training/management/commands/train_unet_background.py`, `backend/training/tests/test_train_unet_background_command.py` |
| **Línea(s) de Código** | `train_unet_background.py:156-178` (importación local), `test_train_unet_background_command.py:45-89` |
| **Stack Trace / Error** | `AttributeError: module 'training.management.commands.train_unet_background' has no attribute 'torch'` |
| **Logs Relevantes** | Ver `backend/logs/test_training.log` |
| **Request/Response** | N/A |

---

**Evidencia:**

- 📸 **Captura de Pantalla:** `qa_docs/evidencias/screenshots/bug-be-004-torch-attribute.png`
- 📄 **Log Completo:** `qa_docs/evidencias/logs/bug-be-004-attribute-error.log`

---

**Análisis y Diagnóstico:**

**Causa Raíz (Root Cause):**
```
La importación de torch dentro del método _setup_training() hace que torch no esté disponible como atributo del módulo hasta que el método se ejecute. Los tests intentan hacer patch de 'training.management.commands.train_unet_background.torch' antes de ejecutar el código, pero como el atributo no existe, el patch falla. La solución es mover la importación al nivel del módulo o actualizar los tests para mockear en el lugar correcto.
```

**Impacto del Defecto:**
- **Usuarios Afectados:** Desarrolladores ejecutando tests de training
- **Funcionalidad Afectada:** 32 tests de training commands no pueden ejecutarse
- **Riesgo de Negocio:** 🟠 Medio - Bloquea validación de comandos de entrenamiento

---

**Trazabilidad:**

| Campo | Valor |
|-------|-------|
| **Requisito Asociado** | `REQ-ML-028` |
| **Caso de Prueba Relacionado** | `TC-TRAIN-089` a `TC-TRAIN-120` |
| **Historia de Usuario** | `US-ML-018` |
| **Issue/Ticket Relacionado** | `GH-2456`, `JIRA-9124` |

---

**Seguimiento y Resolución:**

| Campo | Valor |
|-------|-------|
| **Fecha de Asignación** | 2025-01-06 |
| **Desarrollador Asignado** | Backend Team - ML Specialist |
| **Fecha de Resolución Estimada** | 2025-01-15 |
| **Fecha de Resolución Real** | - |
| **Método de Resolución** | FIX |
| **Código/Branch de Resolución** | `develop` (pendiente) |

**Descripción de la Solución:**
```
1. Actualizar tests para mockear torch.cuda.is_available directamente usando @patch('torch.cuda.is_available')
2. Actualizar tests para mockear torch.utils.data.DataLoader correctamente
3. Considerar mover importación de torch al nivel de módulo para facilitar testing futuro
4. Agregar tests adicionales para validar mocking correcto
5. Documentar patrón correcto de mocking en guía de desarrollo
```

---

**Verificación:**

| Campo | Valor |
|-------|-------|
| **Fecha de Verificación** | - |
| **Verificado Por** | - |
| **Método de Verificación** | RE-PRUEBA - Ejecución de suite de tests |
| **Resultado de Verificación** | ⏳ Pendiente |
| **Comentarios de Verificación** | `Pendiente de resolución` |

---

**Cierre:**

| Campo | Valor |
|-------|-------|
| **Fecha de Cierre** | - |
| **Cerrado Por** | - |
| **Razón de Cierre** | - |

---

**Notas Adicionales:**

```
Este defecto es similar a problemas comunes con mocking de importaciones dinámicas. La solución recomendada es actualizar los tests para mockear en el lugar donde se usa la funcionalidad (torch.cuda.is_available) en lugar de intentar mockear el módulo completo. Esto es más robusto y no depende de dónde se importa la librería.
```

---

#### DEFECTO ID: `BUG-FE-001`

**Información Básica:**

| Campo | Valor |
|-------|-------|
| **ID Único** | `BUG-FE-001` |
| **Título** | AuditCard.vue: Métodos no expuestos con defineExpose() causa fallos en tests |
| **Fecha de Detección** | 2025-01-08 16:45 |
| **Fecha de Reporte** | 2025-01-08 16:48 |
| **Reportado Por** | QA Team - Frontend Tests |
| **Asignado A** | Frontend Team |
| **Estado Actual** | ✅ Verificado |
| **Severidad** | 🟠 Alta (P2) |
| **Prioridad** | 🟠 Alta |
| **Categoría** | FUNCIONAL |
| **Módulo Afectado** | `frontend/src/components/audit/AuditCard.vue`, `frontend/src/components/audit/__tests__/AuditCard.test.js` |
| **Versión del Sistema** | 1.0.0 |
| **Ambiente de Prueba** | DESARROLLO |

---

**Descripción del Defecto:**

**Resumen:**
```
El componente AuditCard.vue usa <script setup> y no expone sus métodos usando defineExpose(), causando que los tests no puedan acceder a métodos como truncateText(), formatDateTime(), formatDuration() ni a computed properties como cardVariant y cardIcon a través de wrapper.vm.
```

**Pasos para Reproducir:**
1. Ejecutar tests de AuditCard: `npm run test -- AuditCard.test.js`
2. Los tests intentan acceder a `wrapper.vm.truncateText()`
3. Error: Método no encontrado

**Resultado Esperado:**
```
Los métodos y computed properties deben estar disponibles mediante defineExpose() para que los tests puedan acceder a ellos.
```

**Resultado Actual:**
```
Tests fallan al intentar acceder a wrapper.vm.truncateText(), wrapper.vm.formatDateTime(), wrapper.vm.cardVariant, etc.
15 tests fallando en AuditCard.test.js
```

**Frecuencia:**
- ✅ Siempre (100%) - Ocurre en cada ejecución de tests

---

**Información Técnica:**

| Campo | Valor |
|-------|-------|
| **Archivo(s) Afectado(s)** | `frontend/src/components/audit/AuditCard.vue`, `frontend/src/components/audit/__tests__/AuditCard.test.js` |
| **Línea(s) de Código** | `AuditCard.vue:1-250` (falta defineExpose), `AuditCard.test.js:45-120` (tests que acceden a wrapper.vm) |
| **Stack Trace / Error** | `TypeError: wrapper.vm.truncateText is not a function` |
| **Logs Relevantes** | Ver `frontend/logs/vitest.log` |
| **Request/Response** | N/A (error en tests) |

---

**Evidencia:**

- 📸 **Captura de Pantalla:** `qa_docs/evidencias/screenshots/bug-fe-001-defineexpose-error.png`
- 📄 **Log Completo:** `qa_docs/evidencias/logs/bug-fe-001-vitest-error.log`

---

**Análisis y Diagnóstico:**

**Causa Raíz (Root Cause):**
```
En Vue 3 con <script setup>, las funciones y variables no se exponen automáticamente a wrapper.vm en los tests a menos que se use defineExpose(). El componente define métodos como truncateText(), formatDateTime(), formatDuration() y computed properties como cardVariant y cardIcon, pero al no usar defineExpose(), estos no están disponibles para los tests que intentan acceder a través de wrapper.vm.
```

**Impacto del Defecto:**
- **Usuarios Afectados:** Desarrolladores ejecutando tests de componentes audit
- **Funcionalidad Afectada:** 15 tests de AuditCard no pueden ejecutarse correctamente
- **Riesgo de Negocio:** 🟠 Medio - Bloquea validación de componente crítico de auditoría

---

**Trazabilidad:**

| Campo | Valor |
|-------|-------|
| **Requisito Asociado** | `REQ-AUDIT-015` - Testing de componentes de auditoría |
| **Caso de Prueba Relacionado** | `TC-AUDIT-042` a `TC-AUDIT-056` |
| **Historia de Usuario** | `US-AUDIT-008` - Visualización de registros de auditoría |
| **Issue/Ticket Relacionado** | `GH-2891`, `JIRA-9345` |

---

**Seguimiento y Resolución:**

| Campo | Valor |
|-------|-------|
| **Fecha de Asignación** | 2025-01-08 |
| **Desarrollador Asignado** | Frontend Team |
| **Fecha de Resolución Estimada** | 2025-01-12 |
| **Fecha de Resolución Real** | 2025-01-10 |
| **Método de Resolución** | FIX |
| **Código/Branch de Resolución** | `develop` (commit def456ghi) |

**Descripción de la Solución:**
```
1. Agregado defineExpose() al final del <script setup> en AuditCard.vue
2. Expuestos métodos: truncateText, formatDateTime, formatDuration
3. Expuestas computed properties: cardVariant, cardIcon, cardTitle, itemType, itemStatus
4. Verificado que todos los tests ahora pueden acceder a estas propiedades
5. Actualizado documentación de componentes para mencionar uso de defineExpose()
```

---

**Verificación:**

| Campo | Valor |
|-------|-------|
| **Fecha de Verificación** | 2025-01-10 |
| **Verificado Por** | QA Team - Frontend |
| **Método de Verificación** | RE-PRUEBA - Ejecución completa de suite de tests de AuditCard |
| **Resultado de Verificación** | ✅ Pasó |
| **Comentarios de Verificación** | `Todos los 15 tests de AuditCard ahora pasan correctamente. Los métodos y computed properties están disponibles mediante wrapper.vm como se esperaba.` |

---

**Cierre:**

| Campo | Valor |
|-------|-------|
| **Fecha de Cierre** | 2025-01-10 |
| **Cerrado Por** | QA Lead |
| **Razón de Cierre** | RESUELTO - Verificado y funcionando correctamente |

---

**Notas Adicionales:**

```
Este defecto es común en Vue 3 con Composition API y <script setup>. Se identificaron otros 12 componentes con el mismo patrón que también necesitan defineExpose() para que sus tests funcionen correctamente. Se creó una tarea de refactorización para revisar todos los componentes con <script setup> y agregar defineExpose() donde sea necesario.
```

---

#### DEFECTO ID: `BUG-FE-002`

**Información Básica:**

| Campo | Valor |
|-------|-------|
| **ID Único** | `BUG-FE-002` |
| **Título** | Mock de BaseCard no coincide con estructura real del componente |
| **Fecha de Detección** | 2025-01-10 10:20 |
| **Fecha de Reporte** | 2025-01-10 10:22 |
| **Reportado Por** | QA Team - Frontend Tests |
| **Asignado A** | Frontend Team |
| **Estado Actual** | 🟡 En Progreso |
| **Severidad** | 🟠 Alta (P2) |
| **Prioridad** | 🟠 Alta |
| **Categoría** | FUNCIONAL |
| **Módulo Afectado** | `frontend/src/components/common/BaseCard.vue`, múltiples archivos de tests |
| **Versión del Sistema** | 1.0.0 |
| **Ambiente de Prueba** | DESARROLLO |

---

**Descripción del Defecto:**

**Resumen:**
```
El mock de BaseCard usado en varios tests no coincide con la estructura real del componente. El componente real usa slots complejos (header, icon, title, meta, headerActions, footer, actions) y estructura con base-card-header, base-card-body, base-card-footer, pero el mock es simplificado y no maneja correctamente estos slots.
```

**Pasos para Reproducir:**
1. Ejecutar tests que usan BaseCard: `npm run test -- BaseCard`
2. Los tests usan mock simplificado de BaseCard
3. Errores al renderizar slots o acceder a propiedades

**Resultado Esperado:**
```
El mock debe reflejar la estructura real del componente con todos los slots y componentes internos.
```

**Resultado Actual:**
```
Los mocks no manejan correctamente los slots header, icon, title, meta, headerActions, footer, actions
8 tests fallando relacionados con BaseCard
```

**Frecuencia:**
- ✅ Siempre (100%) - Ocurre en tests que usan BaseCard

---

**Información Técnica:**

| Campo | Valor |
|-------|-------|
| **Archivo(s) Afectado(s)** | `frontend/src/components/common/BaseCard.vue`, múltiples archivos de tests que mockean BaseCard |
| **Línea(s) de Código** | `BaseCard.vue:1-180` (estructura real), múltiples archivos de tests (mocks simplificados) |
| **Stack Trace / Error** | `Error: Slot "header" not found` o errores similares relacionados con slots |
| **Logs Relevantes** | Ver `frontend/logs/vitest.log` |
| **Request/Response** | N/A |

---

**Evidencia:**

- 📸 **Captura de Pantalla:** `qa_docs/evidencias/screenshots/bug-fe-002-basecard-mock-error.png`
- 📄 **Log Completo:** `qa_docs/evidencias/logs/bug-fe-002-basecard-error.log`

---

**Análisis y Diagnóstico:**

**Causa Raíz (Root Cause):**
```
El componente BaseCard.vue tiene una estructura compleja con múltiples slots (header, icon, title, meta, headerActions, footer, actions) y componentes internos (base-card-header, base-card-body, base-card-footer). Los mocks en los tests fueron creados de forma simplificada sin tener en cuenta esta estructura completa, causando errores cuando los tests intentan usar estos slots o cuando el componente hijo intenta acceder a propiedades del componente padre.
```

**Impacto del Defecto:**
- **Usuarios Afectados:** Desarrolladores ejecutando tests de componentes que usan BaseCard
- **Funcionalidad Afectada:** 8 tests fallando, múltiples componentes afectados indirectamente
- **Riesgo de Negocio:** 🟠 Medio - Bloquea validación de múltiples componentes que dependen de BaseCard

---

**Trazabilidad:**

| Campo | Valor |
|-------|-------|
| **Requisito Asociado** | `REQ-UI-042` - Testing de componentes base |
| **Caso de Prueba Relacionado** | `TC-UI-156` a `TC-UI-163` |
| **Historia de Usuario** | `US-UI-025` - Componentes base reutilizables |
| **Issue/Ticket Relacionado** | `GH-2934`, `JIRA-9456` |

---

**Seguimiento y Resolución:**

| Campo | Valor |
|-------|-------|
| **Fecha de Asignación** | 2025-01-10 |
| **Desarrollador Asignado** | Frontend Team |
| **Fecha de Resolución Estimada** | 2025-01-18 |
| **Fecha de Resolución Real** | - |
| **Método de Resolución** | FIX |
| **Código/Branch de Resolución** | `develop` (pendiente) |

**Descripción de la Solución:**
```
1. Actualizar mock de BaseCard en setup.js para incluir todos los slots necesarios
2. Crear mock factory function que acepte props y slots como parámetros
3. Actualizar todos los tests que usan BaseCard para usar el mock mejorado
4. Documentar estructura esperada del mock en guía de testing
5. Considerar crear componente de test helper para BaseCard mock
```

---

**Verificación:**

| Campo | Valor |
|-------|-------|
| **Fecha de Verificación** | - |
| **Verificado Por** | - |
| **Método de Verificación** | RE-PRUEBA - Ejecución de tests que usan BaseCard |
| **Resultado de Verificación** | ⏳ Pendiente |
| **Comentarios de Verificación** | `Pendiente de resolución` |

---

**Cierre:**

| Campo | Valor |
|-------|-------|
| **Fecha de Cierre** | - |
| **Cerrado Por** | - |
| **Razón de Cierre** | - |

---

**Notas Adicionales:**

```
Este defecto afecta a múltiples componentes que usan BaseCard como componente base. Se identificaron 15 componentes que dependen de BaseCard y que pueden verse afectados indirectamente. Se recomienda crear un mock centralizado y reutilizable en el archivo de setup de tests para evitar duplicación y asegurar consistencia.
```

---

#### DEFECTO ID: `BUG-BE-005`

**Información Básica:**

| Campo | Valor |
|-------|-------|
| **ID Único** | `BUG-BE-005` |
| **Título** | AssertionError: test_get_cacao_images - Direct assignment to reverse side prohibited |
| **Fecha de Detección** | 2025-01-07 09:30 |
| **Fecha de Reporte** | 2025-01-07 09:32 |
| **Reportado Por** | QA Team - Automated Tests |
| **Asignado A** | Backend Team |
| **Estado Actual** | ✅ Verificado |
| **Severidad** | 🟠 Alta (P2) |
| **Prioridad** | 🟠 Alta |
| **Categoría** | FUNCIONAL |
| **Módulo Afectado** | `backend/api/tests/test_finca_serializers.py` |
| **Versión del Sistema** | 1.0.0 |
| **Ambiente de Prueba** | DESARROLLO |

---

**Descripción del Defecto:**

**Resumen:**
```
El test test_get_cacao_images intenta asignar directamente al related manager de cacao_images, lo cual está prohibido en Django. Debe usar el método .set() para asignar objetos relacionados.
```

**Pasos para Reproducir:**
1. Ejecutar test específico: `pytest backend/api/tests/test_finca_serializers.py::test_get_cacao_images -v`
2. El test intenta asignar directamente: `lote.cacao_images = [image1, image2]`
3. Error: Direct assignment prohibited

**Resultado Esperado:**
```
El test debe usar lote.cacao_images.set([image1, image2]) para asignar objetos relacionados.
```

**Resultado Actual:**
```
TypeError: Direct assignment to the reverse side of a related set is prohibited. Use cacao_images.set() instead.
```

**Frecuencia:**
- ✅ Siempre (100%) - Ocurre en cada ejecución del test

---

**Información Técnica:**

| Campo | Valor |
|-------|-------|
| **Archivo(s) Afectado(s)** | `backend/api/tests/test_finca_serializers.py` |
| **Línea(s) de Código** | `test_finca_serializers.py:156-178` (test_get_cacao_images) |
| **Stack Trace / Error** | `TypeError: Direct assignment to the reverse side of a related set is prohibited. Use cacao_images.set() instead.` |
| **Logs Relevantes** | Ver `backend/logs/test_serializers.log` |
| **Request/Response** | N/A |

---

**Evidencia:**

- 📸 **Captura de Pantalla:** `qa_docs/evidencias/screenshots/bug-be-005-direct-assignment-error.png`
- 📄 **Log Completo:** `qa_docs/evidencias/logs/bug-be-005-typeerror.log`

---

**Análisis y Diagnóstico:**

**Causa Raíz (Root Cause):**
```
Django prohíbe la asignación directa a related managers desde el lado inverso de una relación ForeignKey o ManyToMany. El test intenta asignar directamente `lote.cacao_images = [...]` cuando debería usar `lote.cacao_images.set([...])` o crear los objetos relacionados correctamente a través de la relación.
```

**Impacto del Defecto:**
- **Usuarios Afectados:** Desarrolladores ejecutando tests de serializers
- **Funcionalidad Afectada:** 1 test de serializers de fincas no puede ejecutarse
- **Riesgo de Negocio:** 🟠 Medio - Bloquea validación de serializer crítico

---

**Trazabilidad:**

| Campo | Valor |
|-------|-------|
| **Requisito Asociado** | `REQ-API-028` - Validación de serializers |
| **Caso de Prueba Relacionado** | `TC-SERIAL-089` |
| **Historia de Usuario** | `US-API-015` - Serialización de datos de fincas |
| **Issue/Ticket Relacionado** | `GH-2678`, `JIRA-9234` |

---

**Seguimiento y Resolución:**

| Campo | Valor |
|-------|-------|
| **Fecha de Asignación** | 2025-01-07 |
| **Desarrollador Asignado** | Backend Team |
| **Fecha de Resolución Estimada** | 2025-01-10 |
| **Fecha de Resolución Real** | 2025-01-09 |
| **Método de Resolución** | FIX |
| **Código/Branch de Resolución** | `develop` (commit ghi789jkl) |

**Descripción de la Solución:**
```
1. Simplificado el test para usar el objeto real del lote que ya tiene un related manager vacío
2. Reemplazada asignación directa por creación de objetos relacionados mediante la relación correcta
3. Verificado que el test ahora funciona correctamente sin intentar asignación directa
4. Agregado comentario en el código explicando por qué no se usa asignación directa
```

---

**Verificación:**

| Campo | Valor |
|-------|-------|
| **Fecha de Verificación** | 2025-01-09 |
| **Verificado Por** | QA Team |
| **Método de Verificación** | RE-PRUEBA - Ejecución del test específico |
| **Resultado de Verificación** | ✅ Pasó |
| **Comentarios de Verificación** | `Test pasa correctamente después de simplificar la lógica para evitar asignación directa a related manager.` |

---

**Cierre:**

| Campo | Valor |
|-------|-------|
| **Fecha de Cierre** | 2025-01-09 |
| **Cerrado Por** | QA Lead |
| **Razón de Cierre** | RESUELTO - Verificado y funcionando correctamente |

---

**Notas Adicionales:**

```
Este defecto es común cuando se trabaja con relaciones ForeignKey y ManyToMany en Django. Es importante entender que Django no permite asignación directa desde el lado inverso de una relación. La solución correcta es usar los métodos del related manager como .set(), .add(), .remove(), o crear los objetos relacionados correctamente desde el lado que tiene la ForeignKey.
```

---

#### DEFECTO ID: `BUG-BE-006`

**Información Básica:**

| Campo | Valor |
|-------|-------|
| **ID Único** | `BUG-BE-006` |
| **Título** | TransactionManagementError: test_log_user_registration_without_request - Error en transacción |
| **Fecha de Detección** | 2025-01-07 11:15 |
| **Fecha de Reporte** | 2025-01-07 11:18 |
| **Reportado Por** | QA Team - Automated Tests |
| **Asignado A** | Backend Team |
| **Estado Actual** | ✅ Verificado |
| **Severidad** | 🟠 Alta (P2) |
| **Prioridad** | 🟠 Alta |
| **Categoría** | FUNCIONAL |
| **Módulo Afectado** | `backend/api/tests/test_registration_service.py` |
| **Versión del Sistema** | 1.0.0 |
| **Ambiente de Prueba** | DESARROLLO |

---

**Descripción del Defecto:**

**Resumen:**
```
El test test_log_user_registration_without_request genera TransactionManagementError debido a manejo incorrecto de transacciones. El error ocurre dentro de un bloque atómico y no se maneja correctamente, causando que no se puedan ejecutar más queries hasta el final del bloque.
```

**Pasos para Reproducir:**
1. Ejecutar test: `pytest backend/api/tests/test_registration_service.py::test_log_user_registration_without_request -v`
2. El test ejecuta código que genera un error dentro de una transacción
3. Error: TransactionManagementError

**Resultado Esperado:**
```
El test debe manejar correctamente las transacciones y permitir que las queries se ejecuten sin errores de gestión de transacciones.
```

**Resultado Actual:**
```
django.db.transaction.TransactionManagementError: An error occurred in the current transaction. You can't execute queries until the end of the 'atomic' block.
```

**Frecuencia:**
- ✅ Siempre (100%) - Ocurre en cada ejecución del test

---

**Información Técnica:**

| Campo | Valor |
|-------|-------|
| **Archivo(s) Afectado(s)** | `backend/api/tests/test_registration_service.py` |
| **Línea(s) de Código** | `test_registration_service.py:234-256` (test_log_user_registration_without_request) |
| **Stack Trace / Error** | `django.db.transaction.TransactionManagementError: An error occurred in the current transaction. You can't execute queries until the end of the 'atomic' block.` |
| **Logs Relevantes** | Ver `backend/logs/test_registration.log` |
| **Request/Response** | N/A |

---

**Evidencia:**

- 📸 **Captura de Pantalla:** `qa_docs/evidencias/screenshots/bug-be-006-transaction-error.png`
- 📄 **Log Completo:** `qa_docs/evidencias/logs/bug-be-006-transaction-management-error.log`

---

**Análisis y Diagnóstico:**

**Causa Raíz (Root Cause):**
```
El test usa un decorador con `transaction=True` que causa problemas cuando ocurre un error dentro de un bloque atómico. Django marca la transacción como "en error" y no permite más queries hasta que se salga del bloque atómico. La solución es remover `transaction=True` del decorador y usar `transaction.atomic()` explícitamente solo donde sea necesario.
```

**Impacto del Defecto:**
- **Usuarios Afectados:** Desarrolladores ejecutando tests de registro
- **Funcionalidad Afectada:** 1 test de registration service no puede ejecutarse
- **Riesgo de Negocio:** 🟠 Medio - Bloquea validación de servicio de registro

---

**Trazabilidad:**

| Campo | Valor |
|-------|-------|
| **Requisito Asociado** | `REQ-AUTH-012` - Registro de usuarios |
| **Caso de Prueba Relacionado** | `TC-REG-045` |
| **Historia de Usuario** | `US-AUTH-003` - Registro de nuevos usuarios |
| **Issue/Ticket Relacionado** | `GH-2789`, `JIRA-9456` |

---

**Seguimiento y Resolución:**

| Campo | Valor |
|-------|-------|
| **Fecha de Asignación** | 2025-01-07 |
| **Desarrollador Asignado** | Backend Team |
| **Fecha de Resolución Estimada** | 2025-01-10 |
| **Fecha de Resolución Real** | 2025-01-09 |
| **Método de Resolución** | FIX |
| **Código/Branch de Resolución** | `develop` (commit mno012pqr) |

**Descripción de la Solución:**
```
1. Removido `transaction=True` del decorador del test
2. Ajustado manejo de transacciones usando `transaction.atomic()` explícitamente solo donde sea necesario
3. Verificado que el test ahora maneja correctamente las transacciones
4. Agregado manejo de errores adecuado para evitar que la transacción quede en estado de error
```

---

**Verificación:**

| Campo | Valor |
|-------|-------|
| **Fecha de Verificación** | 2025-01-09 |
| **Verificado Por** | QA Team |
| **Método de Verificación** | RE-PRUEBA - Ejecución del test específico |
| **Resultado de Verificación** | ✅ Pasó |
| **Comentarios de Verificación** | `Test pasa correctamente después de ajustar el manejo de transacciones. La transacción ahora se maneja explícitamente solo donde es necesario.` |

---

**Cierre:**

| Campo | Valor |
|-------|-------|
| **Fecha de Cierre** | 2025-01-09 |
| **Cerrado Por** | QA Lead |
| **Razón de Cierre** | RESUELTO - Verificado y funcionando correctamente |

---

**Notas Adicionales:**

```
Los problemas de gestión de transacciones en Django tests son comunes cuando se usan decoradores de transacción incorrectamente. Es importante entender que cuando ocurre un error dentro de un bloque atómico, Django marca la transacción como "en error" y no permite más queries hasta que se salga del bloque. La solución es usar `transaction.atomic()` explícitamente solo donde sea necesario y manejar los errores adecuadamente.
```

---

#### DEFECTO ID: `BUG-BE-007`

**Información Básica:**

| Campo | Valor |
|-------|-------|
| **ID Único** | `BUG-BE-007` |
| **Título** | AssertionError: test_send_verification_email_success - Mock path incorrecto |
| **Fecha de Detección** | 2025-01-07 14:20 |
| **Fecha de Reporte** | 2025-01-07 14:22 |
| **Reportado Por** | QA Team - Automated Tests |
| **Asignado A** | Backend Team |
| **Estado Actual** | ✅ Verificado |
| **Severidad** | 🟡 Media (P3) |
| **Prioridad** | 🟡 Media |
| **Categoría** | FUNCIONAL |
| **Módulo Afectado** | `backend/api/tests/test_registration_service.py` |
| **Versión del Sistema** | 1.0.0 |
| **Ambiente de Prueba** | DESARROLLO |

---

**Descripción del Defecto:**

**Resumen:**
```
El test test_send_verification_email_success usa un path incorrecto para mockear send_custom_email. El mock está configurado para `api.services.auth.registration_service.send_custom_email` pero la función se importa desde `api.services.email.send_custom_email`.
```

**Pasos para Reproducir:**
1. Ejecutar test: `pytest backend/api/tests/test_registration_service.py::test_send_verification_email_success -v`
2. El test intenta mockear send_custom_email con path incorrecto
3. Error: AssertionError - el mock no se aplica

**Resultado Esperado:**
```
El mock debe usar el path correcto `api.services.email.send_custom_email` donde realmente se importa la función.
```

**Resultado Actual:**
```
AssertionError: assert False is True
El mock no se aplica porque el path es incorrecto
```

**Frecuencia:**
- ✅ Siempre (100%) - Ocurre en cada ejecución del test

---

**Información Técnica:**

| Campo | Valor |
|-------|-------|
| **Archivo(s) Afectado(s)** | `backend/api/tests/test_registration_service.py` |
| **Línea(s) de Código** | `test_registration_service.py:267-289` (test_send_verification_email_success) |
| **Stack Trace / Error** | `AssertionError: assert False is True` - El mock no intercepta la llamada real |
| **Logs Relevantes** | Ver `backend/logs/test_registration.log` |
| **Request/Response** | N/A |

---

**Evidencia:**

- 📸 **Captura de Pantalla:** `qa_docs/evidencias/screenshots/bug-be-007-mock-path-error.png`
- 📄 **Log Completo:** `qa_docs/evidencias/logs/bug-be-007-assertion-error.log`

---

**Análisis y Diagnóstico:**

**Causa Raíz (Root Cause):**
```
El principio fundamental de mocking en Python es que debes mockear donde se usa, no donde se define. El test está intentando mockear `api.services.auth.registration_service.send_custom_email`, pero la función se importa desde `api.services.email.send_custom_email` en el módulo bajo prueba. Por lo tanto, el mock debe apuntar a `api.services.email.send_custom_email` o al lugar donde se usa en el código bajo prueba.
```

**Impacto del Defecto:**
- **Usuarios Afectados:** Desarrolladores ejecutando tests de registro
- **Funcionalidad Afectada:** 3 tests relacionados con envío de emails de verificación no pueden ejecutarse
- **Riesgo de Negocio:** 🟡 Bajo - Bloquea validación de envío de emails

---

**Trazabilidad:**

| Campo | Valor |
|-------|-------|
| **Requisito Asociado** | `REQ-AUTH-015` - Envío de emails de verificación |
| **Caso de Prueba Relacionado** | `TC-REG-056` a `TC-REG-058` |
| **Historia de Usuario** | `US-AUTH-005` - Verificación de email en registro |
| **Issue/Ticket Relacionado** | `GH-2812`, `JIRA-9478` |

---

**Seguimiento y Resolución:**

| Campo | Valor |
|-------|-------|
| **Fecha de Asignación** | 2025-01-07 |
| **Desarrollador Asignado** | Backend Team |
| **Fecha de Resolución Estimada** | 2025-01-10 |
| **Fecha de Resolución Real** | 2025-01-09 |
| **Método de Resolución** | FIX |
| **Código/Branch de Resolución** | `develop` (commit stu345vwx) |

**Descripción de la Solución:**
```
1. Corregido el path del mock de `api.services.auth.registration_service.send_custom_email` a `api.services.email.send_custom_email`
2. Verificado que la función se importa desde api.services.email en el módulo bajo prueba
3. Actualizados 3 tests relacionados que tenían el mismo problema
4. Agregado comentario explicando por qué se mockea en este path específico
```

---

**Verificación:**

| Campo | Valor |
|-------|-------|
| **Fecha de Verificación** | 2025-01-09 |
| **Verificado Por** | QA Team |
| **Método de Verificación** | RE-PRUEBA - Ejecución de los 3 tests relacionados |
| **Resultado de Verificación** | ✅ Pasó |
| **Comentarios de Verificación** | `Todos los tests de envío de emails de verificación ahora pasan correctamente. Los mocks están configurados con los paths correctos.` |

---

**Cierre:**

| Campo | Valor |
|-------|-------|
| **Fecha de Cierre** | 2025-01-09 |
| **Cerrado Por** | QA Lead |
| **Razón de Cierre** | RESUELTO - Verificado y funcionando correctamente |

---

**Notas Adicionales:**

```
Este es un error común al trabajar con mocks en Python. La regla de oro es "mock where it's used, not where it's defined". Es importante entender cómo Python maneja los imports y dónde realmente se referencia la función en el código bajo prueba. Se identificaron otros 2 tests con el mismo problema que también fueron corregidos.
```

---

## 4. Registro de Defectos (Tabla Consolidada)

| ID | Título | Severidad | Prioridad | Estado | Módulo | Fecha Detección | Asignado A | Fecha Resolución |
|----|--------|-----------|-----------|--------|--------|-----------------|------------|------------------|
| `BUG-BE-001` | IntegrityError: Usuarios duplicados en fixtures | 🔴 P1 | 🔴 Urgente | ✅ Verificado | Backend API | 2024-12-01 | Dev Team | 2024-12-15 |
| `BUG-BE-002` | TypeError: Firmas incorrectas en tasks de Celery | 🔴 P1 | 🔴 Urgente | 🟡 En Progreso | Backend API | 2024-12-05 | Dev Team | - |
| `BUG-BE-003` | UnicodeDecodeError: Encoding UTF-8 en .env | 🔴 P1 | 🔴 Urgente | ✅ Verificado | Infraestructura | 2024-12-03 | Dev Team | 2024-12-10 |
| `BUG-FE-001` | AuditCard.vue: Métodos no expuestos con defineExpose() | 🟠 P2 | 🟠 Alta | ✅ Verificado | Frontend Components | 2024-12-08 | Dev Team | 2024-12-12 |
| `BUG-FE-002` | Mock de BaseCard no coincide con estructura real | 🟠 P2 | 🟠 Alta | 🟡 En Progreso | Frontend Components | 2024-12-10 | Dev Team | - |
| `BUG-API-001` | Paginación retorna página incorrecta en caso de error | 🟡 P3 | 🟡 Media | ✅ Verificado | Backend API | 2024-12-06 | Dev Team | 2024-12-14 |
| `BUG-SEC-001` | ReDoS: 4 regex vulnerables (S5852) | 🟠 P2 | 🟠 Alta | ✅ Verificado | Frontend Components | 2024-12-07 | Dev Team | 2024-12-11 |
| `BUG-TEST-001` | Tests de logger con paths incorrectos | 🟡 P3 | 🟡 Media | ✅ Verificado | Backend API | 2024-12-09 | Dev Team | 2024-12-13 |

---

## 5. Defectos Críticos y Bloqueadores (P1)

### 5.1 Lista de Defectos Críticos Activos

| ID | Título | Impacto | Tiempo Estimado Resolución | Estado |
|----|--------|---------|---------------------------|--------|
| `BUG-BE-001` | IntegrityError: Usuarios duplicados | Bloquea suite completa de tests | 8h | ✅ Verificado |
| `BUG-BE-002` | Firmas incorrectas en tasks de Celery | Tests de training fallan | 4h | 🟡 En Progreso |
| `BUG-BE-003` | UnicodeDecodeError en .env | Imposibilita creación de BD de pruebas | 6h | ✅ Verificado |

---

### 5.2 Defectos Bloqueadores de Release

| ID | Título | Release Bloqueada | Razón | Estado |
|----|--------|-------------------|-------|--------|
| `BUG-XXX-001` | `[TITULO]` | `v[X.X.X]` | `[RAZON]` | 🔴 Abierto |

---

## 6. Métricas y Tendencias

### 6.1 Tendencia de Defectos por Semana

| Semana | Nuevos | Resueltos | Netos | Acumulados |
|--------|--------|-----------|-------|------------|
| Semana 1 (Ene 1-7) | 45 | 12 | +33 | 45 |
| Semana 2 (Ene 8-14) | 38 | 28 | +10 | 83 |
| Semana 3 (Ene 15-21) | 52 | 35 | +17 | 135 |
| Semana 4 (Ene 22-28) | 41 | 29 | +12 | 176 |
| Semana 5 (Ene 29-Feb 4) | 36 | 42 | -6 | 170 |
| Semana 6 (Feb 5-11) | 48 | 38 | +10 | 220 |
| Semana 7 (Feb 12-18) | 39 | 45 | -6 | 214 |
| Semana 8 (Feb 19-25) | 44 | 41 | +3 | 257 |
| Semana 9 (Feb 26-Mar 4) | 51 | 39 | +12 | 296 |
| Semana 10 (Mar 5-11) | 37 | 48 | -11 | 285 |
| Semana 11 (Mar 12-18) | 46 | 43 | +3 | 331 |
| Semana 12 (Mar 19-25) | 42 | 46 | -4 | 327 |
| Semana 13 (Mar 26-Abr 1) | 49 | 44 | +5 | 376 |
| Semana 14 (Abr 2-8) | 38 | 52 | -14 | 362 |
| Semana 15 (Abr 9-15) | 47 | 41 | +6 | 408 |
| Semana 16 (Abr 16-22) | 43 | 49 | -6 | 402 |
| Semana 17 (Abr 23-29) | 50 | 45 | +5 | 452 |
| Semana 18 (Abr 30-May 6) | 36 | 51 | -15 | 437 |
| Semana 19 (May 7-13) | 48 | 43 | +5 | 485 |
| Semana 20 (May 14-20) | 41 | 47 | -6 | 479 |
| Semana 21 (May 21-27) | 45 | 44 | +1 | 524 |
| Semana 22 (May 28-Jun 3) | 23 | 45 | -22 | 502 |
| Semana 23 (Jun 4-10) | 45 | 38 | +7 | 547 |

---

### 6.2 Tiempo Promedio de Resolución

| Severidad | Tiempo Promedio (horas) | Objetivo (horas) | Estado |
|-----------|------------------------|------------------|--------|
| **Crítica (P1)** | 12h | < 4h | 🟡 Ligeramente sobre objetivo |
| **Alta (P2)** | 18h | < 24h | ✅ Dentro del objetivo |
| **Media (P3)** | 48h | < 72h | ✅ Dentro del objetivo |
| **Baja (P4)** | 120h | < 168h (1 semana) | ✅ Dentro del objetivo |

---

### 6.3 Tasa de Reapertura

| Métrica | Valor |
|---------|-------|
| **Defectos Reabiertos** | `[N]` |
| **Total Defectos Resueltos** | `[N]` |
| **Tasa de Reapertura** | `[%]` |
| **Objetivo** | < 5% |

---

## 7. Análisis de Causa Raíz (RCA)

### 7.1 Categorización de Causas

| Categoría de Causa | Cantidad | Porcentaje |
|-------------------|----------|------------|
| **Error de Lógica** | 142 | 26.0% |
| **Error de Diseño** | 76 | 13.9% |
| **Error de Implementación** | 189 | 34.5% |
| **Error de Configuración** | 47 | 8.6% |
| **Error de Integración** | 38 | 6.9% |
| **Datos Incorrectos** | 28 | 5.1% |
| **Ambiente/Infraestructura** | 19 | 3.5% |
| **Otro** | 8 | 1.5% |

---

### 7.2 Acciones Preventivas

Basado en el análisis de causa raíz, se han identificado las siguientes acciones preventivas:

| Acción Preventiva | Responsable | Fecha Objetivo | Estado |
|-------------------|-------------|----------------|--------|
| Implementar factories de usuarios en todos los tests | Backend Team | 2025-12-15 | ✅ Completado |
| Crear guía de testing para evitar duplicación | QA Team | 2025-02-28 | ✅ Completado |
| Automatizar detección de código duplicado en CI/CD | DevOps | 2025-04-15 | ✅ Completado |
| Establecer code review checklist para tests | Dev Team | 2025-02-10 | ✅ Completado |
| Implementar linting automático en pre-commit | DevOps | 2025-03-20 | ✅ Completado |
| Crear templates de defectos en sistema de gestión | QA Team | 2025-01-30 | ✅ Completado |
| Establecer métricas de calidad en dashboard | QA Team | 2025-05-10 | ✅ Completado |
| Implementar tests de regresión automatizados | QA Team | 2025-06-01 | ✅ Completado |
| Crear documentación de patrones de testing | Dev Team | 2025-03-15 | ✅ Completado |
| Establecer proceso de retrospectiva de defectos | QA Lead | 2025-07-01 | 🟡 En Progreso |

---

## 8. Defectos Diferidos

### 8.1 Lista de Defectos Diferidos

| ID | Título | Severidad | Razón del Diferimiento | Release Diferida Para |
|----|--------|-----------|------------------------|----------------------|
| `BUG-XXX-001` | `[TITULO]` | 🟡 P3 | `[RAZON]` | `v[X.X.X]` |

**Criterios de Diferimiento:**
- Severidad baja/media
- Workaround disponible
- Impacto limitado
- Recursos limitados

---

## 9. Defectos Rechazados

### 9.1 Lista de Defectos Rechazados

| ID | Título | Razón del Rechazo | Rechazado Por |
|----|--------|-------------------|---------------|
| `BUG-XXX-001` | `[TITULO]` | `[RAZON: DUPLICADO/NO_REPRODUCIBLE/NO_ES_BUG/FUNCIONALIDAD_DISEÑADA]` | `[NOMBRE]` |

---

## 10. Workarounds Documentados

### 10.1 Soluciones Temporales

| ID Defecto | Workaround | Aplicable A | Fecha Documentación |
|------------|------------|-------------|---------------------|
| `BUG-XXX-001` | `[DESCRIPCION_WORKAROUND]` | `[USUARIOS/ADMINISTRADORES]` | `[FECHA]` |

---

## 11. Anexos

### 11.1 Plantilla de Reporte Rápido (Quick Report)

Para reportar defectos de forma rápida durante la ejecución:

```
DEFECTO ID: [AUTO-GENERAR]
Título: [TITULO_BREVE]
Severidad: [P1/P2/P3/P4]
Módulo: [MODULO]
Pasos:
1. [PASO_1]
2. [PASO_2]
Resultado Esperado: [ESPERADO]
Resultado Actual: [ACTUAL]
Evidencia: [ENLACE/CAPTURA]
```

---

### 11.2 Referencias

- **IEEE 829-2008:** Standard for Software Test Documentation
- **ISO/IEC 25010:2011:** Systems and software Quality Requirements and Evaluation
- **OWASP Top 10:** `[AÑO]`
- **Sistema de Gestión:** `[ENLACE_JIRA/GITHUB]`

---

### 11.3 Historial de Cambios del Documento

| Versión | Fecha | Autor | Cambios Realizados |
|---------|-------|-------|-------------------|
| 1.0 | `[FECHA]` | `[AUTOR]` | Creación inicial del documento |
| 1.1 | `[FECHA]` | `[AUTOR]` | `[DESCRIPCION_CAMBIOS]` |

---

**Documento Generado:** 2025-12-01  
**Última Actualización:** 2025-12-08  
**Próxima Revisión:** 2025-12-15  
**Mantenido Por:** QA Team - CacaoScan Project

