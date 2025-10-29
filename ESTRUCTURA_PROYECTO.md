# 📁 Estructura Actual del Proyecto CacaoScan

## 🎯 Resumen del Proyecto

**CacaoScan** es un sistema completo para análisis y gestión de calidad de granos de cacao mediante inteligencia artificial.

---

## 📂 Estructura de Directorios

### Backend (Django)

#### Apps Principales (Modularizadas)
```
backend/
├── core/                  ✅ App core con utilidades compartidas
│   ├── models.py          # SystemSettings, TimeStampedModel
│   ├── utils/             # Utilidades de respuestas
│   └── middleware/        # Middleware de manejo de errores
│
├── auth_app/              ✅ App de autenticación
│   ├── models.py          # EmailVerificationToken, UserProfile
│   ├── views.py
│   └── serializers.py
│
├── fincas_app/            ✅ App de fincas y lotes
│   ├── models.py          # Finca, Lote
│   ├── views.py
│   └── serializers.py
│
├── images_app/            ✅ App de imágenes y predicciones
│   ├── models.py          # CacaoImage, CacaoPrediction
│   ├── views.py
│   └── serializers.py
│
├── notifications/         ✅ App de notificaciones
├── audit/                 ✅ App de auditoría
├── training/              ✅ App de entrenamiento ML
├── reports/               ✅ App de reportes
├── users/                 ✅ App de usuarios
│
└── api/                   ⚠️ App monolítica (temporal, migrando)
    ├── models.py          # Todos los modelos (en migración)
    ├── views.py
    ├── fincas_views.py
    ├── lotes_views.py
    ├── notifications_views.py
    ├── audit_views.py
    ├── config_views.py
    ├── services/          # Servicios organizados
    └── serializers.py     # Todos los serializers
```

#### Módulo de Machine Learning
```
backend/ml/
├── data/              # Carga de datasets
├── segmentation/      # Segmentación YOLO
├── regression/        # Modelos de regresión
├── prediction/        # Predicciones
├── pipeline/          # Pipeline de entrenamiento
├── measurement/       # Calibración
└── utils/            # Utilidades ML
```

#### Otras Carpetas
```
backend/
├── management/commands/    # Comandos Django personalizados
│   ├── train_cacao_models.py
│   ├── train_yolo_model.py
│   └── init_api.py
│
├── tests/                  # Tests globales
├── media/                  # Archivos multimedia
├── logs/                   # Logs del sistema
└── venv/                   # Entorno virtual Python
```

---

### Frontend (Vue.js 3)

#### Estructura Principal
```
frontend/src/
├── components/           # Componentes Vue
│   ├── admin/           # Componentes de administrador
│   ├── agricultor/      # Componentes de agricultor
│   ├── analysis/        # Componentes de análisis
│   ├── auth/            # Componentes de autenticación
│   ├── charts/          # Gráficos y visualizaciones
│   ├── common/          # Componentes comunes
│   ├── fincas/          # Componentes de fincas
│   ├── notifications/   # Componentes de notificaciones
│   ├── reportes/        # Componentes de reportes
│   └── training/        # Componentes de entrenamiento
│
├── views/               # Vistas/Páginas
│   ├── Admin/           # Vistas de admin
│   ├── Agricultor/      # Vistas de agricultor
│   ├── Auth/            # Vistas de autenticación
│   ├── common/          # Vistas comunes
│   └── *.vue            # Otras vistas
│
├── services/            # Servicios API
│   ├── api.js           # Cliente base
│   ├── authApi.js       # API de autenticación
│   ├── predictionApi.js # API de predicciones
│   ├── fincasApi.js     # API de fincas
│   └── ...              # Otros servicios
│
├── stores/              # Pinia stores
│   ├── auth.js          # Estado de autenticación
│   ├── analysis.js      # Estado de análisis
│   ├── fincas.js        # Estado de fincas
│   └── ...              # Otros stores
│
├── composables/         # Composable functions
├── router/              # Configuración de rutas
└── utils/               # Utilidades
```

#### Tests Frontend
```
frontend/
├── cypress/             # Tests E2E
│   ├── e2e/            # Tests por módulo
│   │   ├── auth/
│   │   ├── fincas/
│   │   ├── images/
│   │   └── navigation/
│   └── fixtures/       # Datos de prueba
│
└── vitest.config.js     # Configuración de tests unitarios
```

---

## 📊 Estadísticas del Proyecto

### Backend
- **Apps Django**: 10 apps (4 nuevas + 6 existentes)
- **Modelos de BD**: ~14**
- **Servicios**: 6 servicios organizados
- **Tests**: 11 archivos de test
- **Lenguaje**: Python 3.9+
- **Framework**: Django + Django REST Framework

### Frontend
- **Componentes Vue**: ~135 componentes
- **Vistas**: ~35 vistas
- **Servicios API**: 20 servicios
- **Stores Pinia**: 9 stores
- **Tests E2E**: 20 tests Cypress
- **Framework**: Vue.js 3 + Vite
- **UI**: Tailwind CSS

---

## 🔧 Tecnologías Utilizadas

### Backend
- Django 4.x
- Django REST Framework
- PostgreSQL
- PyTorch (Machine Learning)
- YOLOv8 (Visión computacional)
- Django Channels (WebSockets)
- JWT (Autenticación)

### Frontend
- Vue.js 3 (Composition API)
- Vite
- Pinia (State Management)
- Vue Router
- Tailwind CSS
- Chart.js / Recharts
- Axios

### Testing
- Pytest (Backend)
- Cypress (E2E Frontend)
- Vitest (Unit Tests Frontend)

---

## 🎯 Funcionalidades Principales

### 1. Análisis de Granos
- Subida de imágenes
- Segmentación automática (YOLO)
- Predicción de dimensiones (ML)
- Historial de análisis

### 2. Gestión de Fincas
- CRUD de fincas
- Gestión de lotes
- Ubicación GPS
- Estadísticas por finca

### 3. Machine Learning
- Entrenamiento de modelos
- Predicciones en tiempo real
- Calibración de modelos
- Métricas de rendimiento

### 4. Reportes
- Generación de PDF/Excel
- Estadísticas detalladas
- Exportación de datos
- Historial de reportes

### 5. Sistema de Usuarios
- Autenticación con JWT
- Roles (Admin/Agricultor)
- Perfiles de usuario
- Recuperación de contraseña

### 6. Auditoría
- Logs de actividad
- Historial de logins
- Trazabilidad de acciones

### 7. Notificaciones
- Tiempo real (WebSockets)
- Notificaciones por email
- Centro de notificaciones

---

## 📈 Estado de Modularización

### ✅ Completado
- [x] Creación de apps nuevas (core, auth, fincas, images)
- [x] Modelos migrados a apps correspondientes
- [x] Configuración en settings.py
- [x] Utilidades movidas a core/
- [x] Middleware organizado

### ⏳ Pendiente
- [ ] Completar migración de modelos restantes
- [ ] Mover vistas a sus apps
- [ ] Crear serializers por app
- [ ] Crear URLs por app
- [ ] Generar migraciones
- [ ] Actualizar imports
- [ ] Testing completo
- [ ] Eliminar app api/ cuando todo esté migrado

---

## 🚀 Comandos Útiles

### Backend
```bash
cd backend

# Activar entorno virtual
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Migraciones
python manage.py makemigrations
python manage.py migrate

# Servidor
python manage.py runserver

# Tests
pytest
```

### Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Servidor desarrollo
npm run dev

# Build producción
npm run build

# Tests
npm run test
npm run test:e2e
```

---

## 📝 Archivos de Configuración

- `requirements.txt` - Dependencias Python
- `package.json` - Dependencias Node.js
- `env.example` - Variables de entorno (ejemplo)
- `pytest.ini` - Configuración tests backend
- `cypress.config.js` - Configuración Cypress
- `vite.config.js` - Configuración Vite

---

## 🎯 Próximos Pasos

1. Completar modularización del backend
2. Generar migraciones para nuevas apps
3. Mover vistas y servicios a apps
4. Actualizar URLs y imports
5. Testing completo
6. Documentar APIs
7. Optimización de rendimiento

