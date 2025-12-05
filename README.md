# 🌱 CacaoScan — Plataforma de Análisis Digital de Granos de Cacao

**CacaoScan** es un sistema web desarrollado por aprendices del **SENA (Tecnólogo ADSO)** que permite registrar, analizar y gestionar información de productores de cacao mediante **visión por computadora, aprendizaje automático (PyTorch, YOLOv8)** y un panel administrativo interactivo.

---

## 🚀 Tecnologías Principales

| Componente | Tecnología | Descripción |
|-------------|-------------|-------------|
| **Backend** | Django 4.2 + Django REST Framework | API REST principal y gestión de modelos ML |
| **Base de Datos** | PostgreSQL 15 | Base de datos relacional |
| **Frontend** | Vue.js 3 + Vite + Pinia + TailwindCSS + Flowbite | Interfaz web moderna y responsive |
| **ML/IA** | PyTorch, scikit-learn, YOLOv8, OpenCV | Procesamiento de imágenes y predicción de peso y dimensiones |
| **Autenticación** | JWT (JSON Web Tokens) | Inicio de sesión seguro con roles y permisos |
| **Despliegue** | Render / Railway / Docker (opcional) | Listo para producción |

---

## 🧠 Funcionalidades Clave

- 🔐 Registro, autenticación y roles de usuario (admin, agricultor, técnico)
- 🌾 Gestión de fincas y lotes agrícolas
- 📷 Escaneo y análisis de granos de cacao con IA
- 📊 Reportes descargables en Excel (agricultores, usuarios, métricas)
- 🧾 Sistema de auditoría y notificaciones
- ⚙️ Configuración y calibración de modelos ML desde panel administrativo

---

## 🖥️ Requisitos Previos

Asegúrate de tener instalados:

| Requisito | Versión recomendada |
|------------|--------------------|
| Python | 3.12 o superior |
| Node.js | 18 o superior |
| PostgreSQL | 15 o superior |
| Git | Última versión estable |
| PowerShell o Bash | (para comandos de terminal) |

---

## ⚙️ Instalación del Proyecto

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/tu_usuario/cacaoscan.git
cd cacaoscan
```

### 2️⃣ Configurar el Backend (Django)

⚠️ **Asegúrate de tener instalado Python 3.12** (no versiones anteriores ni posteriores, para evitar incompatibilidades con dependencias del proyecto).

Si tienes varias versiones instaladas, usa siempre el comando `python3.12`.  
Puedes verificar tu versión con:

```bash
python3.12 --version
```

Si necesitas instalar Python 3.12, revisa la documentación oficial según tu sistema operativo: https://www.python.org/downloads/release/python-3120/


```bash
cd backend
python -3.12 -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
# source venv/bin/activate

pip install -r requirements.txt
```

Crea el archivo `.env` en la carpeta `backend/` con el siguiente contenido:

```env
DEBUG=True
SECRET_KEY=tu_clave_segura
ALLOWED_HOSTS=127.0.0.1,localhost
DB_NAME=cacaoscan_db
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```

Aplica las migraciones:

```bash
  python manage.py makemigrations
python manage.py migrate
```

Aplica los seeders

```bash
python manage.py init_catalogos
python manage.py seed_colombia
```

Crea el superusuario:

```bash
python manage.py createsuperuser
```

Inicia el servidor:

```bash
python manage.py runserver
```

✅ El backend estará disponible en: **http://127.0.0.1:8000**

### 3️⃣ Configurar el Frontend (Vue)

```bash
cd ../frontend
pnpm install
pnpm dev
```

✅ El frontend estará disponible en: **http://127.0.0.1:5173**

---

## 📦 Dependencias del Proyecto

Esta sección documenta todas las dependencias utilizadas en CacaoScan, sus versiones, propósitos y cómo gestionarlas.

### 🎨 Dependencias del Frontend (Vue.js)

El frontend utiliza **pnpm** como gestor de paquetes. Las dependencias están definidas en `frontend/package.json`.

#### Dependencias Principales (Producción)

| Dependencia | Versión | Propósito | Obligatoria |
|-------------|---------|-----------|-------------|
| **vue** | ^3.5.18 | Framework principal de Vue.js 3 | ✅ Sí |
| **vue-router** | ^4.5.1 | Enrutamiento y navegación SPA | ✅ Sí |
| **pinia** | ^3.0.3 | Gestión de estado global | ✅ Sí |
| **axios** | ^1.12.2 | Cliente HTTP para comunicación con API | ✅ Sí |
| **tailwindcss** | ^4.1.11 | Framework CSS utility-first | ✅ Sí |
| **@tailwindcss/vite** | ^4.1.11 | Plugin de TailwindCSS para Vite | ✅ Sí |
| **chart.js** | ^4.5.0 | Gráficos y visualización de datos | ⚠️ Opcional |
| **leaflet** | ^1.9.4 | Mapas interactivos | ⚠️ Opcional |
| **sweetalert2** | ^11.26.3 | Alertas y modales elegantes | ⚠️ Opcional |
| **ionicons** | ^8.0.13 | Iconos vectoriales | ⚠️ Opcional |

#### Dependencias de Desarrollo

| Dependencia | Versión | Propósito | Obligatoria |
|-------------|---------|-----------|-------------|
| **vite** | ^7.0.6 | Build tool y servidor de desarrollo | ✅ Sí |
| **@vitejs/plugin-vue** | ^6.0.1 | Plugin Vue para Vite | ✅ Sí |
| **vitest** | ^2.1.8 | Framework de testing | ⚠️ Opcional |
| **@vue/test-utils** | ^2.4.6 | Utilidades para testing Vue | ⚠️ Opcional |
| **eslint** | ^9.31.0 | Linter de código | ⚠️ Opcional |
| **prettier** | 3.6.2 | Formateador de código | ⚠️ Opcional |

#### Instalación de Dependencias Frontend

```bash
cd frontend
pnpm install
```

#### Actualización de Dependencias Frontend

```bash
# Actualizar todas las dependencias
pnpm update

# Actualizar una dependencia específica
pnpm update vue@latest

# Verificar dependencias desactualizadas
pnpm outdated
```

#### Restricciones y Compatibilidades Frontend

- **Node.js**: Requiere Node.js `^20.19.0` o `>=22.12.0` (verificado en `engines`)
- **pnpm**: Se recomienda usar pnpm en lugar de npm o yarn para consistencia
- **Vue 3**: El proyecto utiliza Composition API y requiere Vue 3.5+

---

### 🐍 Dependencias del Backend (Django/Python)

El backend utiliza **pip** y **requirements.txt** para gestionar dependencias. Requiere **Python 3.12**.

#### Dependencias Principales (Producción)

##### Framework y API

| Dependencia | Versión | Propósito | Obligatoria |
|-------------|---------|-----------|-------------|
| **Django** | 5.2.9 | Framework web principal | ✅ Sí |
| **djangorestframework** | 3.16.1 | Framework para APIs REST | ✅ Sí |
| **djangorestframework_simplejwt** | 5.5.1 | Autenticación JWT | ✅ Sí |
| **django-cors-headers** | 4.9.0 | Manejo de CORS | ✅ Sí |
| **django-filter** | 25.2 | Filtrado avanzado de querysets | ⚠️ Opcional |
| **drf-yasg** | 1.21.7 | Documentación Swagger/OpenAPI | ⚠️ Opcional |

##### Base de Datos

| Dependencia | Versión | Propósito | Obligatoria |
|-------------|---------|-----------|-------------|
| **psycopg2-binary** | 2.9.11 | Adaptador PostgreSQL | ✅ Sí |
| **django-redis** | 6.0.0 | Cache con Redis | ⚠️ Opcional |
| **redis** | 7.1.0 | Cliente Redis | ⚠️ Opcional |

##### Machine Learning y Visión por Computadora

| Dependencia | Versión | Propósito | Obligatoria |
|-------------|---------|-----------|-------------|
| **torch** | 2.5.1 | PyTorch - Framework de deep learning | ✅ Sí |
| **torchvision** | 0.20.1 | Utilidades de visión para PyTorch | ✅ Sí |
| **ultralytics** | 8.3.234 | YOLOv8 para detección de objetos | ✅ Sí |
| **opencv-python** | 4.12.0.88 | Procesamiento de imágenes | ✅ Sí |
| **opencv-python-headless** | 4.12.0.88 | OpenCV sin GUI (para servidores) | ✅ Sí |
| **scikit-learn** | 1.7.2 | Machine learning tradicional | ✅ Sí |
| **scikit-image** | 0.25.2 | Procesamiento de imágenes | ✅ Sí |
| **albumentations** | 2.0.8 | Data augmentation para imágenes | ⚠️ Opcional |
| **timm** | 0.9.12 | Modelos pre-entrenados | ⚠️ Opcional |

##### Procesamiento de Datos

| Dependencia | Versión | Propósito | Obligatoria |
|-------------|---------|-----------|-------------|
| **numpy** | 2.1.3 | Computación numérica | ✅ Sí |
| **pandas** | 2.3.3 | Manipulación de datos | ✅ Sí |
| **polars** | 1.35.2 | Procesamiento de datos rápido | ⚠️ Opcional |
| **scipy** | 1.16.2 | Computación científica | ⚠️ Opcional |

##### Visualización y Reportes

| Dependencia | Versión | Propósito | Obligatoria |
|-------------|---------|-----------|-------------|
| **matplotlib** | 3.10.7 | Visualización de datos | ⚠️ Opcional |
| **seaborn** | 0.13.2 | Visualización estadística | ⚠️ Opcional |
| **openpyxl** | 3.1.5 | Generación de archivos Excel | ✅ Sí |
| **XlsxWriter** | 3.1.9 | Escritura avanzada de Excel | ⚠️ Opcional |
| **reportlab** | 4.0.4 | Generación de PDFs | ⚠️ Opcional |

##### Tareas Asíncronas y WebSockets

| Dependencia | Versión | Propósito | Obligatoria |
|-------------|---------|-----------|-------------|
| **celery** | 5.6.0 | Tareas asíncronas en background | ⚠️ Opcional |
| **channels** | 4.3.2 | WebSockets y protocolos asíncronos | ⚠️ Opcional |
| **channels_redis** | 4.3.0 | Backend Redis para Channels | ⚠️ Opcional |

##### Servidor y Despliegue

| Dependencia | Versión | Propósito | Obligatoria |
|-------------|---------|-----------|-------------|
| **gunicorn** | 23.0.0 | Servidor WSGI para producción | ✅ Sí (producción) |
| **whitenoise** | 6.8.2 | Servir archivos estáticos | ⚠️ Opcional |
| **django-storages** | 1.14.2 | Almacenamiento en cloud (S3, etc.) | ⚠️ Opcional |

##### Utilidades y Otros

| Dependencia | Versión | Propósito | Obligatoria |
|-------------|---------|-----------|-------------|
| **python-dotenv** | 1.2.1 | Gestión de variables de entorno | ✅ Sí |
| **pillow** | 12.0.0 | Procesamiento de imágenes | ✅ Sí |
| **requests** | 2.32.5 | Cliente HTTP | ⚠️ Opcional |
| **sendgrid** | 6.11.0 | Envío de emails | ⚠️ Opcional |
| **pydantic** | 2.12.5 | Validación de datos | ⚠️ Opcional |

##### Testing

| Dependencia | Versión | Propósito | Obligatoria |
|-------------|---------|-----------|-------------|
| **pytest** | 9.0.1 | Framework de testing | ⚠️ Opcional |
| **pytest-django** | 4.11.1 | Plugin pytest para Django | ⚠️ Opcional |
| **pytest-cov** | 7.0.0 | Cobertura de código | ⚠️ Opcional |
| **pytest-xdist** | 3.8.0 | Testing paralelo | ⚠️ Opcional |
| **coverage** | 7.12.0 | Análisis de cobertura | ⚠️ Opcional |

#### Instalación de Dependencias Backend

```bash
cd backend
python3.12 -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

#### Actualización de Dependencias Backend

```bash
# Actualizar todas las dependencias
pip install --upgrade -r requirements.txt

# Actualizar una dependencia específica
pip install --upgrade Django==5.2.10

# Generar nuevo requirements.txt con versiones actualizadas
pip freeze > requirements.txt

# Verificar dependencias desactualizadas
pip list --outdated
```

#### Restricciones y Compatibilidades Backend

- **Python**: Requiere **Python 3.12** exactamente (no 3.11 ni 3.13)
- **Django**: Compatible con Django 5.2.x
- **PyTorch**: Requiere CUDA 11.8+ para GPU (opcional, funciona con CPU)
- **PostgreSQL**: Requiere PostgreSQL 15 o superior
- **Redis**: Opcional, requerido solo si se usan tareas asíncronas o cache
- **Sistema Operativo**: Compatible con Windows, Linux y macOS

#### Dependencias Opcionales por Funcionalidad

| Funcionalidad | Dependencias Opcionales |
|---------------|------------------------|
| **Mapas interactivos** | `leaflet` (frontend) |
| **Gráficos avanzados** | `chart.js` (frontend) |
| **Tareas asíncronas** | `celery`, `redis` (backend) |
| **WebSockets** | `channels`, `channels_redis` (backend) |
| **Envío de emails** | `sendgrid` (backend) |
| **Almacenamiento cloud** | `django-storages`, `boto3` (backend) |
| **Testing** | `pytest`, `pytest-django`, `vitest` |

---

### 🔄 Gestión de Dependencias

#### Buenas Prácticas

1. **Versionado**: Todas las dependencias están fijadas a versiones específicas para garantizar reproducibilidad
2. **Actualizaciones**: Revisar changelogs antes de actualizar dependencias críticas
3. **Seguridad**: Ejecutar `pip audit` o `pnpm audit` regularmente para detectar vulnerabilidades
4. **Entornos**: Usar entornos virtuales (Python) y lockfiles (pnpm) para aislamiento

#### Comandos Útiles

```bash
# Frontend - Verificar vulnerabilidades
pnpm audit

# Frontend - Actualizar dependencias de forma segura
pnpm update --latest

# Backend - Verificar vulnerabilidades
pip audit

# Backend - Actualizar dependencias de forma segura
pip install --upgrade package-name

# Generar requirements.txt actualizado
pip freeze > requirements.txt
```

#### Notas Importantes

- ⚠️ **No actualizar PyTorch sin verificar compatibilidad con CUDA** si se usa GPU
- ⚠️ **Django 5.2.x** tiene cambios breaking respecto a versiones anteriores
- ⚠️ **Vue 3.5+** requiere Node.js 20.19+ o 22.12+
- ✅ Las dependencias marcadas como "Opcional" pueden eliminarse si no se usan sus funcionalidades

---

## 🐳 Instalación con Docker (Recomendado)

La forma más fácil de ejecutar CacaoScan es usando Docker Compose.

### Requisitos
- Docker Desktop instalado ([descargar aquí](https://www.docker.com/products/docker-desktop))
- Docker Compose v3.8 o superior

### Pasos de instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/tu_usuario/cacaoscan.git
cd cacaoscan
```

2. **Configurar variables de entorno**:
```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Edita el archivo .env con tus configuraciones (opcional)
```

3. **Construir y ejecutar los contenedores**:
```bash
docker-compose up -d --build
```

4. **Verificar que todo esté funcionando**:
```bash
docker-compose ps
docker-compose logs -f
```

5. **Acceder a la aplicación**:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/v1/
- **Admin Django**: http://localhost:8000/admin/

### Comandos útiles de Docker

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (⚠️ borra datos)
docker-compose down -v

# Reiniciar un servicio específico
docker-compose restart backend

# Ejecutar comandos Django en el contenedor
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser

# Reconstruir las imágenes
docker-compose build --no-cache


---

#### Pasos adicionales recomendados **antes de ejecutar pipelines de ML/IA**:

### 📸 Preparación previa antes de ejecutar pipelines de ML/IA

#### 1. Preparar datos

**Coloca las imágenes en la carpeta `raw`:**  
Asegúrate de que todas las imágenes estén ubicadas en `backend/media/cacao_images/raw/`.  
Formatos soportados: `.bmp`, `.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`

**Agrega el dataset CSV:**  
Copia el archivo CSV del dataset en `backend/media/datasets/`. Debe tener la siguiente estructura:

```
ID,ALTO,ANCHO,GROSOR,PESO,filename,image_path
510,22.8,16.3,10.2,1.72,510.bmp,cacao_images\raw\510.bmp
```

#### 2. Flujo completo de entrenamiento ML/IA

Ejecuta los siguientes comandos **en orden** para entrenar el sistema completo:

**Paso 1: Entrenar modelo U-Net para segmentación de fondo**

```bash
# Con GPU (recomendado)
docker compose exec backend python manage.py train_unet_background --epochs 20 --batch-size 16

# Sin GPU (usa CPU automáticamente)
docker compose exec backend python manage.py train_unet_background --epochs 20 --batch-size 4
```

**¿Qué hace?**
- Entrena un modelo U-Net para eliminar el fondo de imágenes de granos de cacao
- Genera: `ml/segmentation/cacao_unet.pth`
- **Detección automática**: Usa GPU si está disponible, si no usa CPU
- Tiempo estimado: 
  - Con GPU: ~30-60 minutos
  - Sin GPU: ~2-4 horas (recomendado `--batch-size 4`)

**Paso 2: Generar crops y calibrar píxeles**

```bash
docker compose exec backend python manage.py calibrate_dataset_pixels --segmentation-backend auto
```

**¿Qué hace?**
- Procesa todas las imágenes del dataset
- Usa el U-Net entrenado (si existe) para eliminar el fondo
- Crea crops (imágenes sin fondo) en `backend/media/cacao_images/crops/`
- Mide píxeles y calcula factores de escala (píxel → mm)
- Genera: `backend/media/datasets/pixel_calibration.json`
- Tiempo estimado: ~5-15 minutos

**Paso 3: Entrenar modelos de regresión**

```bash
# Con GPU (recomendado)
docker compose exec backend python manage.py train_cacao_models --hybrid --use-pixel-features --epochs 50 --batch-size 32

# Sin GPU (usa CPU automáticamente)
docker compose exec backend python manage.py train_cacao_models --hybrid --use-pixel-features --epochs 50 --batch-size 8
```

**¿Qué hace?**
- Carga los crops y `pixel_calibration.json` generados en el paso anterior
- Entrena un modelo híbrido (CNN + Pixel Features) para predecir dimensiones y peso
- Genera: `ml/artifacts/regressors/hybrid.pt`
- **Detección automática**: Usa GPU si está disponible, si no usa CPU
- Tiempo estimado: 
  - Con GPU: ~1-3 horas
  - Sin GPU: ~6-12 horas (recomendado `--batch-size 8` o menor)

**Ver todas las opciones disponibles:**

```bash
docker compose exec backend python manage.py train_cacao_models --help
```


```

## 📂 Estructura del Proyecto

```
cacaoscan/
├── backend/
│   ├── api/
│   ├── personas/
│   ├── fincas_app/
│   ├── reports/
│   ├── legal/               # Términos y política de privacidad
│   ├── cacaoscan/settings.py
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   ├── router/
│   │   └── services/
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

## 📦 Scripts Útiles

### Backend

| Comando | Descripción |
|---------|-------------|
| `python manage.py runserver` | Ejecuta el servidor de desarrollo |
| `python manage.py shell` | Abre la consola interactiva Django |
| `python manage.py showmigrations` | Lista migraciones aplicadas |
| `python manage.py createsuperuser` | Crea un administrador |

### Frontend

| Comando | Descripción |
|---------|-------------|
| `pnpm dev` | Inicia el servidor de desarrollo |
| `pnpm build` | Genera la versión de producción |
| `pnpm preview` | Previsualiza el build localmente |

---

## 🧩 Endpoints Principales

| Endpoint | Descripción |
|----------|-------------|
| `/api/v1/auth/login/` | Inicio de sesión (JWT) |
| `/api/v1/fincas/` | Gestión de fincas |
| `/api/v1/lotes/` | Gestión de lotes |
| `/api/v1/reports/agricultores/` | Reporte Excel de agricultores |
| `/api/v1/legal/terms/` | Términos y condiciones |
| `/api/v1/legal/privacy/` | Política de privacidad |

---

## 🧠 Autores

Proyecto desarrollado por aprendices de **Análisis y Desarrollo de Software (ADSO)** — Ficha 2923560, SENA Regional Guaviare

- 👨‍💻 **Camilo Andres Hernández Gonzales**
- 👨‍💻 **Jeferson Alexander Alvarez Rodríguez**
- 👨‍💻 **Cristian Camilo Camacho Morales**

---

## 🪪 Licencia

Este proyecto es de uso académico y no comercial, protegido bajo la licencia MIT.

© 2025 CacaoScan — Todos los derechos reservados.