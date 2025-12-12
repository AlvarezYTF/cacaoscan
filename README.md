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
| Node.js | 20.19.0 o superior (22.12.0+) |
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
py -3.12 -m venv venv

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
| **@tailwindcss/postcss** | ^4.1.11 | Plugin PostCSS para TailwindCSS | ✅ Sí |
| **vitest** | ^2.1.8 | Framework de testing | ⚠️ Opcional |
| **@vitest/coverage-v8** | ^2.1.8 | Cobertura de código para Vitest | ⚠️ Opcional |
| **@vue/test-utils** | ^2.4.6 | Utilidades para testing Vue | ⚠️ Opcional |
| **eslint** | ^9.31.0 | Linter de código | ⚠️ Opcional |
| **@eslint/js** | ^9.31.0 | Configuración base de ESLint | ⚠️ Opcional |
| **eslint-plugin-vue** | ~10.3.0 | Plugin ESLint para Vue | ⚠️ Opcional |
| **@vue/eslint-config-prettier** | ^10.2.0 | Configuración Prettier para Vue | ⚠️ Opcional |
| **prettier** | 3.6.2 | Formateador de código | ⚠️ Opcional |
| **globals** | ^16.3.0 | Variables globales para ESLint | ⚠️ Opcional |
| **jsdom** | ^25.0.1 | Entorno DOM para testing | ⚠️ Opcional |
| **vite-plugin-vue-devtools** | ^8.0.0 | DevTools para Vue en desarrollo | ⚠️ Opcional |
| **start-server-and-test** | ^2.0.12 | Utilidad para testing con servidor | ⚠️ Opcional |

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

#### Tabla Completa de Dependencias (requirements.txt)

Esta tabla incluye todas las dependencias listadas en `backend/requirements.txt`:

| Dependencia | Versión | Categoría | Descripción |
|-------------|---------|-----------|-------------|
| **albucore** | 0.0.24 | ML - Data augmentation | Biblioteca core para transformaciones de imágenes de albumentations |
| **albumentations** | 2.0.8 | ML - Data augmentation | Biblioteca rápida de aumento de datos para aprendizaje profundo |
| **amqp** | 5.3.1 | Async - Message queue | Biblioteca cliente del protocolo avanzado de cola de mensajes |
| **annotated-types** | 0.7.0 | Utilidad - Type hints | Validación en tiempo de ejecución para anotaciones de tipo |
| **asgiref** | 3.11.0 | Framework - Django ASGI | Implementación de referencia de la especificación ASGI para Django |
| **billiard** | 4.2.4 | Async - Celery multiprocessing | Implementación de pool de multiprocesamiento para Celery |
| **celery** | 5.6.0 | Async - Task queue | Cola de tareas distribuida para procesamiento asíncrono de trabajos |
| **certifi** | 2025.11.12 | Utilidad - SSL certificates | Paquete de certificados SSL para Python |
| **channels** | 4.3.2 | Async - WebSockets | Soporte de WebSocket y protocolos asíncronos para Django |
| **channels_redis** | 4.3.0 | Async - Redis backend | Backend de capa de canales Redis para Django Channels |
| **charset-normalizer** | 3.4.4 | Utilidad - Encoding | Detección y normalización de codificación de caracteres |
| **click** | 8.3.0 | Utilidad - CLI framework | Framework para crear interfaces de línea de comandos |
| **click-didyoumean** | 0.3.1 | Utilidad - CLI suggestions | Sugerencias de errores tipográficos para comandos Click |
| **click-plugins** | 1.1.1.2 | Utilidad - CLI plugins | Sistema de plugins para el framework CLI Click |
| **click-repl** | 0.3.0 | Utilidad - CLI REPL | Soporte REPL para aplicaciones Click |
| **colorama** | 0.4.6 | Utilidad - Terminal colors | Texto de terminal con colores multiplataforma |
| **contourpy** | 1.3.3 | Visualización - Matplotlib | Algoritmo rápido de contornos para Matplotlib |
| **coverage** | 7.12.0 | Testing - Code coverage | Herramienta de medición de cobertura de código |
| **cycler** | 1.2.1 | Visualización - Matplotlib | Ciclos de estilo componibles para Matplotlib |
| **Django** | 5.2.9 | Framework - Web framework | Framework web de alto nivel para Python |
| **django-cors-headers** | 4.9.0 | Framework - CORS handling | Encabezados de intercambio de recursos de origen cruzado para Django |
| **django-filter** | 25.2 | Framework - Query filtering | Filtrado avanzado para Django REST Framework |
| **django-redis** | 6.0.0 | Framework - Redis cache | Backend de caché Redis para Django |
| **django-storages** | 1.14.2 | Framework - Cloud storage | Backends de almacenamiento personalizados para Django (S3, Azure, etc.) |
| **djangorestframework** | 3.16.1 | Framework - REST API | Kit de herramientas potente para construir APIs web |
| **djangorestframework_simplejwt** | 5.5.1 | Framework - JWT auth | Autenticación JWT para Django REST Framework |
| **drf-yasg** | 1.21.7 | Framework - API docs | Documentación Swagger/OpenAPI para Django REST Framework |
| **et_xmlfile** | 2.0.0 | Utilidad - Excel support | Lector de archivos XML de bajo nivel para openpyxl |
| **exceptiongroup** | 1.3.1 | Utilidad - Exception handling | Grupos de excepciones y soporte de sintaxis except* |
| **execnet** | 2.1.2 | Testing - Parallel execution | Ejecución y pruebas distribuidas entre procesos |
| **filelock** | 3.20.0 | Utilidad - File locking | Bloqueo de archivos independiente de plataforma |
| **fonttools** | 4.60.1 | Visualización - Font handling | Biblioteca de manipulación y conversión de fuentes |
| **fsspec** | 2025.10.0 | Utilidad - File system | Interfaz unificada para sistemas de archivos locales y remotos |
| **gunicorn** | 23.0.0 | Servidor - WSGI server | Servidor HTTP WSGI de Python para producción |
| **huggingface-hub** | 0.36.0 | ML - Model hub | Biblioteca cliente para el repositorio de modelos Hugging Face |
| **idna** | 3.11 | Utilidad - IDN support | Soporte de nombres de dominio internacionalizados |
| **ImageIO** | 2.37.2 | Utilidad - Image I/O | Biblioteca para leer y escribir datos de imagen |
| **inflection** | 0.5.1 | Utilidad - String inflection | Biblioteca de transformación de cadenas (pluralizar, singularizar, etc.) |
| **iniconfig** | 2.3.0 | Testing - Config parser | Analizador de archivos INI para configuración de pytest |
| **intel-openmp** | 2021.4.0 | ML - Intel optimizations | Biblioteca de tiempo de ejecución Intel OpenMP para computación paralela |
| **Jinja2** | 3.1.6 | Utilidad - Template engine | Motor de plantillas moderno para Python |
| **joblib** | 1.5.2 | ML - Parallel processing | Pipeline ligero para computación paralela |
| **kiwisolver** | 1.4.9 | Visualización - Layout solver | Solucionador rápido de restricciones para problemas de diseño |
| **kombu** | 5.6.1 | Async - Celery messaging | Biblioteca de mensajería para la cola de tareas Celery |
| **lazy_loader** | 0.4 | Utilidad - Lazy imports | Utilidades de importación diferida para paquetes grandes |
| **MarkupSafe** | 3.0.3 | Utilidad - Safe strings | Renderizar de forma segura cadenas XML/HTML no confiables |
| **matplotlib** | 3.10.7 | Visualización - Plotting | Biblioteca completa de gráficos para Python |
| **mkl** | 2021.4.0 | ML - Intel Math Kernel | Biblioteca Intel Math Kernel para operaciones matemáticas optimizadas |
| **mpmath** | 1.3.0 | Utilidad - Arbitrary precision | Aritmética de punto flotante de precisión arbitraria |
| **msgpack** | 1.1.2 | Utilidad - Serialization | Formato de serialización binaria rápida |
| **networkx** | 3.6 | Utilidad - Graph algorithms | Biblioteca de análisis de grafos y redes |
| **numpy** | 2.1.3 | ML - Numerical computing | Paquete fundamental para computación científica |
| **opencv-python** | 4.12.0.88 | ML - Computer vision | Biblioteca OpenCV para tareas de visión por computadora |
| **opencv-python-headless** | 4.12.0.88 | ML - OpenCV headless | OpenCV sin dependencias de GUI (uso en servidor) |
| **openpyxl** | 3.1.5 | Utilidad - Excel files | Biblioteca para leer/escribir archivos Excel |
| **packaging** | 25.0 | Utilidad - Package metadata | Utilidades principales para paquetes de Python |
| **pandas** | 2.3.3 | Utilidad - Data analysis | Biblioteca de manipulación y análisis de datos |
| **pillow** | 12.0.0 | Utilidad - Image processing | Fork de Python Imaging Library para procesamiento de imágenes |
| **pluggy** | 1.6.0 | Testing - Plugin system | Mecanismo de llamada de plugins y hooks |
| **polars** | 1.35.2 | Utilidad - Fast dataframes | Biblioteca DataFrame rápida multi-hilo |
| **polars-runtime-32** | 1.35.2 | Utilidad - Polars runtime | Componentes de tiempo de ejecución para la biblioteca Polars |
| **prompt_toolkit** | 3.0.52 | Utilidad - CLI interface | Construcción de líneas de comando interactivas potentes |
| **psutil** | 7.1.3 | Utilidad - System info | Utilidades multiplataforma de sistema y procesos |
| **psycopg2-binary** | 2.9.11 | Base de datos - PostgreSQL | Adaptador de PostgreSQL para Python |
| **py-cpuinfo** | 9.0.0 | Utilidad - CPU information | Biblioteca de recopilación de información de CPU |
| **pydantic** | 2.12.5 | Utilidad - Data validation | Validación de datos usando anotaciones de tipo de Python |
| **pydantic_core** | 2.41.5 | Utilidad - Pydantic core | Motor de validación core para Pydantic |
| **Pygments** | 2.19.2 | Utilidad - Syntax highlighting | Biblioteca de resaltado de sintaxis |
| **PyJWT** | 2.10.1 | Framework - JWT tokens | Implementación de JSON Web Token |
| **pyparsing** | 3.2.5 | Utilidad - Parsing | Framework de análisis general |
| **pytest** | 9.0.1 | Testing - Test framework | Framework de pruebas para Python |
| **pytest-cov** | 7.0.0 | Testing - Coverage plugin | Plugin de cobertura para pytest |
| **pytest-django** | 4.11.1 | Testing - Django plugin | Plugin de Django para pytest |
| **pytest-xdist** | 3.8.0 | Testing - Parallel tests | Ejecución de pruebas en paralelo para pytest |
| **python-dateutil** | 2.9.0.post0 | Utilidad - Date parsing | Extensiones al módulo datetime estándar |
| **python-dotenv** | 1.2.1 | Utilidad - Environment vars | Cargar variables de entorno desde archivo .env |
| **python-http-client** | 3.3.7 | Utilidad - HTTP client | Biblioteca cliente HTTP para SendGrid |
| **pytz** | 2025.2 | Utilidad - Timezone handling | Definiciones y cálculos de zonas horarias mundiales |
| **PyYAML** | 6.0.3 | Utilidad - YAML parser | Analizador y emisor YAML para Python |
| **qudida** | 0.0.4 | ML - Data augmentation | Aumento de datos que preserva la calidad |
| **redis** | 7.1.0 | Base de datos - Redis client | Cliente Python para la base de datos Redis |
| **reportlab** | 4.0.4 | Utilidad - PDF generation | Biblioteca de generación de PDF |
| **requests** | 2.32.5 | Utilidad - HTTP library | Biblioteca HTTP para realizar solicitudes |
| **safetensors** | 0.7.0 | ML - Safe tensor storage | Formato de almacenamiento de tensores seguro y rápido |
| **scikit-image** | 0.25.2 | ML - Image processing | Algoritmos de procesamiento de imágenes para Python |
| **scikit-learn** | 1.7.2 | ML - Machine learning | Biblioteca de aprendizaje automático para Python |
| **scipy** | 1.16.2 | ML - Scientific computing | Biblioteca de computación científica |
| **seaborn** | 0.13.2 | Visualización - Statistical plots | Biblioteca de visualización de datos estadísticos |
| **sendgrid** | 6.11.0 | Utilidad - Email service | Cliente API de SendGrid para entrega de correo electrónico |
| **setuptools** | 80.9.0 | Utilidad - Package setup | Herramienta de empaquetado y distribución de Python |
| **simsimd** | 6.5.3 | ML - SIMD optimizations | Búsqueda de similitud acelerada por SIMD |
| **six** | 1.17.0 | Utilidad - Python 2/3 compat | Utilidades de compatibilidad entre Python 2 y 3 |
| **sqlparse** | 0.5.3 | Framework - SQL parsing | Analizador SQL no validante para Django |
| **starkbank-ecdsa** | 2.2.0 | Utilidad - Cryptography | Biblioteca criptográfica ECDSA |
| **stringzilla** | 4.4.0 | Utilidad - String operations | Biblioteca de operaciones de cadenas rápida |
| **sympy** | 1.13.1 | Utilidad - Symbolic math | Biblioteca de matemáticas simbólicas |
| **tbb** | 2021.13.1 | ML - Threading library | Intel Threading Building Blocks |
| **threadpoolctl** | 3.6.0 | ML - Thread pool control | Control del tamaño del pool de hilos para bibliotecas nativas |
| **tifffile** | 2025.10.16 | Utilidad - TIFF file support | Leer y escribir archivos TIFF |
| **timm** | 0.9.12 | ML - Pre-trained models | Modelos de imagen PyTorch y pesos preentrenados |
| **torch** | 2.5.1 | ML - PyTorch framework | Framework de aprendizaje profundo |
| **torchvision** | 0.20.1 | ML - Vision utilities | Conjuntos de datos, transformaciones y modelos para visión por computadora |
| **tqdm** | 4.67.1 | Utilidad - Progress bars | Biblioteca de barras de progreso rápida y extensible |
| **typing-inspection** | 0.4.2 | Utilidad - Type inspection | Utilidades de inspección de tipos en tiempo de ejecución |
| **typing_extensions** | 4.15.0 | Utilidad - Type hints | Anotaciones de tipo retrocompatibles para versiones anteriores de Python |
| **tzdata** | 2025.2 | Utilidad - Timezone data | Base de datos de zonas horarias |
| **tzlocal** | 5.3.1 | Utilidad - Local timezone | Información de zona horaria local |
| **ultralytics** | 8.3.234 | ML - YOLO models | Detección de objetos y segmentación YOLOv8 |
| **ultralytics-thop** | 2.0.18 | ML - Model profiling | Herramienta de perfilado de modelos para Ultralytics |
| **uritemplate** | 4.2.0 | Utilidad - URI templates | Análisis y expansión de plantillas URI |
| **urllib3** | 2.2.3 | Utilidad - HTTP client | Biblioteca cliente HTTP con agrupación de conexiones |
| **vine** | 5.1.0 | Async - Celery dependency | Biblioteca de promesas para Celery |
| **wcwidth** | 0.2.14 | Utilidad - Character width | Determinar el ancho imprimible de caracteres anchos |
| **whitenoise** | 6.8.2 | Servidor - Static files | Servicio de archivos estáticos para Django |
| **XlsxWriter** | 3.1.9 | Utilidad - Excel writer | Escribir archivos Excel con formato |

#### Dependencias Frontend (package.json)

Esta tabla incluye todas las dependencias listadas en `frontend/package.json`:

##### Dependencias de Producción

| Dependencia | Versión | Categoría | Descripción |
|-------------|---------|-----------|-------------|
| **@tailwindcss/vite** | ^4.1.11 | Desarrollo - Build tools | Plugin de Vite para Tailwind CSS |
| **axios** | ^1.12.2 | Utilidad - HTTP client | Cliente HTTP basado en promesas para el navegador y Node.js |
| **chart.js** | ^4.5.0 | UI - Gráficos | Biblioteca de gráficos interactivos y responsivos |
| **ionicons** | ^8.0.13 | UI - Iconos | Conjunto de iconos de código abierto optimizados para aplicaciones web |
| **leaflet** | ^1.9.4 | UI - Mapas | Biblioteca de código abierto para mapas interactivos |
| **pinia** | ^3.0.3 | Framework - State management | Store de estado para Vue.js |
| **sweetalert2** | ^11.26.3 | UI - Alertas | Biblioteca de alertas y diálogos modernos y personalizables |
| **tailwindcss** | ^4.1.11 | UI - Styling | Framework CSS utility-first para diseño rápido |
| **vue** | ^3.5.18 | Framework - Vue.js | Framework progresivo de JavaScript para construir interfaces de usuario |
| **vue-router** | ^4.5.1 | Framework - Routing | Router oficial para aplicaciones Vue.js |

##### Dependencias de Desarrollo

| Dependencia | Versión | Categoría | Descripción |
|-------------|---------|-----------|-------------|
| **@eslint/js** | ^9.31.0 | Desarrollo - Linting | Configuración base de ESLint en JavaScript |
| **@tailwindcss/postcss** | ^4.1.11 | Desarrollo - Build tools | Plugin de PostCSS para Tailwind CSS |
| **@vitejs/plugin-vue** | ^6.0.1 | Desarrollo - Build tools | Plugin oficial de Vite para soporte de Vue.js |
| **@vitest/coverage-v8** | ^2.1.8 | Testing - Coverage | Plugin de cobertura de código para Vitest usando V8 |
| **@vue/eslint-config-prettier** | ^10.2.0 | Desarrollo - Linting | Configuración de Prettier para ESLint con Vue |
| **@vue/test-utils** | ^2.4.6 | Testing - Test utilities | Utilidades de prueba oficiales para Vue.js |
| **eslint** | ^9.31.0 | Desarrollo - Linting | Linter de JavaScript y JSX pluggeable |
| **eslint-plugin-vue** | ~10.3.0 | Desarrollo - Linting | Plugin de ESLint para Vue.js |
| **globals** | ^16.3.0 | Desarrollo - Linting | Variables globales para ESLint |
| **jsdom** | ^25.0.1 | Testing - DOM simulation | Implementación de DOM pura en JavaScript para Node.js |
| **prettier** | 3.6.2 | Desarrollo - Formatting | Formateador de código opinado |
| **start-server-and-test** | ^2.0.12 | Testing - Test utilities | Iniciar servidor, esperar URL, ejecutar comando de prueba |
| **vite** | ^7.0.6 | Desarrollo - Build tools | Herramienta de construcción frontend rápida y ligera |
| **vite-plugin-vue-devtools** | ^8.0.0 | Desarrollo - DevTools | Plugin de Vite para Vue DevTools |
| **vitest** | ^2.1.8 | Testing - Test framework | Framework de pruebas unitarias rápido y ligero |

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

#### Instalación de Dependencias Frontend

```bash
cd frontend

# Instalar todas las dependencias (producción y desarrollo)
npm install

# O usando pnpm (recomendado)
pnpm install
```

#### Actualización de Dependencias Frontend

```bash
cd frontend

# Verificar dependencias desactualizadas
npm outdated

# Actualizar todas las dependencias
npm update

# Actualizar una dependencia específica
npm install axios@latest

# Actualizar package.json y package-lock.json
npm install --save-dev vitest@latest

# Usando pnpm
pnpm update
pnpm add axios@latest
```

#### Restricciones y Compatibilidades Frontend

- **Node.js**: Requiere **Node.js ^20.19.0 o >=22.12.0**
- **npm/pnpm**: Se recomienda usar pnpm para mejor rendimiento
- **Navegadores**: Compatible con navegadores modernos (Chrome, Firefox, Safari, Edge)
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
cls

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