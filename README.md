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

```bash
cd backend
python -m venv venv

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