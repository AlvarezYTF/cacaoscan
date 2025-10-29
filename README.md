# 🌱 CacaoScan - Sistema de Control de Calidad del Cacao

Plataforma completa para el análisis y gestión de calidad de granos de cacao mediante inteligencia artificial.

## 🎯 Características

- **Análisis Automatizado**: Medición precisa de dimensiones (alto, ancho, grosor, peso) de granos de cacao
- **Machine Learning**: Modelos de visión computacional (YOLOv8) y regresión para predicciones precisas
- **Gestión de Fincas**: Control de fincas, lotes y cosechas
- **Reportes Avanzados**: Generación de reportes en PDF y Excel
- **Tiempo Real**: Notificaciones y actualizaciones en vivo
- **API REST**: Documentación completa con Swagger

## 🏗️ Arquitectura

### Frontend
- Vue.js 3 con Composition API
- Vite como bundler
- Tailwind CSS para estilos
- Pinia para gestión de estado

### Backend
- Django REST Framework
- PostgreSQL
- Machine Learning con PyTorch
- WebSockets con Django Channels

## 📁 Estructura del Proyecto

```
cacaoscan/
├── frontend/          # Aplicación Vue.js
├── backend/           # API Django
│   ├── core/         # App core con utilidades
│   ├── auth_app/     # Autenticación
│   ├── fincas_app/   # Gestión de fincas
│   ├── images_app/   # Análisis de imágenes
│   ├── notifications/# Sistema de notificaciones
│   ├── audit/        # Auditoría y logs
│   ├── training/     # Entrenamiento de modelos ML
│   ├── reports/      # Generación de reportes
│   └── ml/           # Módulo de Machine Learning
└── docs/             # Documentación
```

## 🚀 Instalación

### Requisitos
- Python 3.9+
- Node.js 16+
- PostgreSQL 13+
- pip y npm

### Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## 🧪 Modelos de Machine Learning

El sistema utiliza dos tipos de modelos:

1. **YOLOv8 Seg**: Segmentación de granos de cacao en imágenes
2. **Regresión**: Predicción de dimensiones físicas (alto, ancho, grosor, peso)

Los modelos se almacenan en `backend/ml/artifacts/` y se cargan automáticamente al iniciar el servidor.

## 📊 API Endpoints Principales

- `POST /api/v1/scan/measure/` - Analizar imagen de grano
- `GET /api/v1/images/` - Listar imágenes analizadas
- `GET /api/v1/fincas/` - Gestión de fincas
- `GET /api/v1/lotes/` - Gestión de lotes
- `GET /api/v1/reports/` - Generar reportes
- `GET /api/docs/` - Documentación Swagger

## 🔧 Configuración

1. Copiar `backend/env.example` a `backend/.env`
2. Configurar variables de entorno (base de datos, email, etc.)
3. Ejecutar migraciones
4. Ejecutar comandos de management para entrenar modelos iniciales

## 🧪 Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

## 📝 Variables de Entorno

Configurar en `backend/.env`:
```env
DB_NAME=cacaoscan_db
DB_USER=postgres
DB_PASSWORD=your_password
SECRET_KEY=your_secret_key
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es propiedad privada.

## 👥 Equipo

Desarrollado con ❤️ para el sector cacaotero.

