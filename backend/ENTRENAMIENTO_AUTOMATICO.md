# Entrenamiento Automático del Modelo

Esta guía explica cómo entrenar el modelo después de hacer `git pull`.

## Comando Existente

Ya existe el comando `train_cacao_models` que puedes usar directamente:

```bash
# Entrenamiento básico (usa parámetros por defecto)
python manage.py train_cacao_models

# Con parámetros optimizados
python manage.py train_cacao_models --epochs=150 --batch-size=16 --learning-rate=0.001

# Solo validar datos sin entrenar
python manage.py train_cacao_models --validate-only
```

## Entrenamiento con Celery

Para ejecutar el entrenamiento de forma asíncrona con Celery:

```bash
# 1. Iniciar worker de Celery
celery -A cacaoscan worker --loglevel=info

# 2. En Python shell o desde código:
from api.tasks import auto_train_model_task
auto_train_model_task.delay()
```

## Configuración Automática con Git Hooks

### Windows

```powershell
# En el directorio raíz del proyecto
cd backend
.\scripts\setup_git_hooks.ps1
```

### Linux/Mac

```bash
# En el directorio raíz del proyecto
cd backend
chmod +x scripts/setup_git_hooks.sh
./scripts/setup_git_hooks.sh
```

Los hooks se ejecutarán automáticamente después de:
- `git pull` - Si hay cambios en datasets o imágenes
- `git checkout` - Para recordarte entrenar si cambias de branch

## Verificación Manual

Verifica si todo está listo para entrenar sin ejecutar el entrenamiento:

```bash
python manage.py train_cacao_models --validate-only
```

## Requisitos Previos

Antes de entrenar, asegúrate de tener:

1. **Dataset preparado:**
   ```bash
   python manage.py prepare_dataset
   ```

2. **Imágenes .bmp en `media/cacao_images/raw/`**
   - El entrenamiento usa específicamente archivos `.bmp`
   - Asegúrate de tener imágenes como `1.bmp`, `2.bmp`, etc.

3. **Redis corriendo (para Celery):**
   ```bash
   # Windows (si tienes Redis instalado)
   redis-server
   
   # O usar Docker
   docker run -d -p 6379:6379 redis
   ```

4. **Worker de Celery activo (si usas Celery):**
   ```bash
   # Windows
   .\start_celery.bat
   
   # Linux/Mac
   ./start_celery.sh
   
   # O manualmente
   celery -A cacaoscan worker --loglevel=info
   ```

## Configuración del Entrenamiento

El entrenamiento automático usa esta configuración por defecto:

- **Epochs:** 150
- **Batch size:** 16
- **Learning rate:** 0.001
- **Model type:** resnet18
- **Early stopping patience:** 25

Para cambiar estos valores, edita `api/tasks.py` en la función `auto_train_model_task`.

## Solución de Problemas

### Error: "Dataset no encontrado"

Ejecuta primero:
```bash
python manage.py prepare_dataset
```

### Error: "No se encontraron imágenes .bmp"

Asegúrate de tener imágenes `.bmp` en:
```
media/cacao_images/raw/*.bmp
```

**Importante:** El entrenamiento usa específicamente archivos `.bmp`, no `.jpg` ni `.png`. El dataset `dataset_cacao.clean.csv` espera que las imágenes tengan la extensión `.bmp`.

### Error: "Celery no está corriendo"

Inicia el worker de Celery:
```bash
celery -A cacaoscan worker --loglevel=info
```

### Ver el progreso del entrenamiento (Celery)

```bash
celery -A cacaoscan inspect active
```

## Integración con CI/CD

Para ejecutar el entrenamiento en pipelines de CI/CD:

```yaml
# Ejemplo para GitHub Actions
- name: Train model
  run: |
    cd backend
    python manage.py train_cacao_models --epochs=150 --batch-size=16
```

## Notas Importantes

- El entrenamiento puede tardar varios minutos dependiendo del tamaño del dataset
- Asegúrate de tener suficiente memoria RAM disponible
- Si usas Celery, el worker debe estar corriendo antes de ejecutar la tarea
- Los modelos entrenados se guardan en `ml/artifacts/`

