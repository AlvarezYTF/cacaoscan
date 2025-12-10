# 📦 Guía del Diagrama de Componentes UML - CacaoScan

Este documento explica el diagrama de componentes UML de CacaoScan siguiendo las convenciones estándar de UML 2.0.

---

## 🎯 Convenciones UML Utilizadas

### 1. Componentes
Los componentes se representan con la notación:
```
<<Component>>
Nombre del Componente
```

**Significado**: Representan módulos de clases que son sistemas o subsistemas independientes con capacidad de interfaz con el resto del sistema.

### 2. Interfaces
Las interfaces se representan con:
```
«interface»
INombreInterface
+method1()
+method2()
```

**Tipos de interfaces**:
- **Provided Interfaces** (Interfaces Proporcionadas): El componente ofrece estos servicios a otros componentes
- **Required Interfaces** (Interfaces Requeridas): El componente necesita estos servicios de otros componentes

### 3. Nodos
Los nodos se representan con:
```
<<Node>>
Nombre del Nodo
```

**Significado**: Representan recursos computacionales hardware o software de nivel superior a los componentes (servidores, bases de datos, servicios externos).

### 4. Paquetes
Los paquetes agrupan componentes relacionados:
```
<<Package>>
Nombre del Paquete
```

### 5. Dependencias
Las dependencias se representan con **líneas punteadas** (dashed lines) que indican que un componente depende de otro o de una interfaz.

---

## 📊 Estructura del Diagrama

### Paquete: Frontend
**Componentes**:
- `Vue.js Application`: Aplicación principal del frontend
- `UI Components`: Componentes de interfaz de usuario
- `Pinia Store`: Gestión de estado
- `API Client`: Cliente HTTP/WebSocket

**Interfaces Proporcionadas**:
- `Routing`, `State Management`, `Forms API`, `Tables API`, etc.

**Interfaces Requeridas**:
- `HTTP Client` requiere interfaces de REST API
- `WebSocket Client` requiere interfaces de WebSocket API

### Paquete: API Gateway
**Componentes**:
- `REST API`: API REST usando Django REST Framework
- `WebSocket API`: API WebSocket usando Django Channels

**Interfaces Proporcionadas**:
- `Authentication API`, `Images API`, `Analysis API`, `Farms API`, `Reports API`
- `Real-time Events` (WebSocket)

### Paquete: Application Services
**Componentes**:
- `Authentication Service`: Servicio de autenticación y autorización
- `Image Management Service`: Gestión de imágenes
- `Analysis Service`: Análisis y predicciones ML
- `Farm Management Service`: Gestión de fincas y lotes
- `Report Service`: Generación de reportes
- `Training Service`: Entrenamiento de modelos ML
- `Profile Service`: Gestión de perfiles de usuario

**Interfaces Proporcionadas**:
- Cada servicio proporciona su interfaz específica (ej: `IAuthentication`, `IImageManagement`)

**Interfaces Requeridas**:
- Los servicios requieren interfaces de repositorios, servicios ML e infraestructura

### Paquete: ML/AI
**Componentes**:
- `ML Models`: Modelos de Machine Learning
- `Prediction Engine`: Motor de predicción
- `Training Pipeline`: Pipeline de entrenamiento
- `Segmentation Service`: Servicio de segmentación de imágenes

**Interfaces Proporcionadas**:
- `IPrediction`, `ITrainingPipeline`, `ISegmentation`, `IMLModels`

### Paquete: Data Access
**Componentes** (Repositorios):
- `User Repository`, `Image Repository`, `Farm Repository`, `Report Repository`, `Training Repository`, `Audit Repository`

**Interfaces Proporcionadas**:
- `IUserRepository`, `IImageRepository`, `IFarmRepository`, etc.

**Interfaces Requeridas**:
- Todos los repositorios requieren la interfaz `IDatabase`

### Paquete: Infrastructure
**Nodos** (recursos de infraestructura):
- `PostgreSQL Database`: Base de datos principal
- `File Storage`: Almacenamiento de archivos (Local/S3)
- `Celery Worker`: Worker de tareas asíncronas
- `Redis`: Cola de mensajes y caché
- `Email Service`: Servicio de correo electrónico

**Interfaces Proporcionadas**:
- `IDatabase`, `IStorage`, `IMessageQueue`, `IEmail`

---

## 🔗 Relaciones y Dependencias

### Dependencias Principales

1. **Frontend → API Gateway**
   - `HTTP Client` depende de interfaces REST API
   - `WebSocket Client` depende de interfaces WebSocket API

2. **API Gateway → Application Services**
   - REST API depende de interfaces de servicios de aplicación
   - WebSocket API depende de interfaces de servicios

3. **Application Services → ML/AI**
   - Servicios de análisis requieren interfaces de ML
   - Servicio de imágenes requiere interfaces de segmentación

4. **Application Services → Data Access**
   - Todos los servicios requieren interfaces de repositorios

5. **Data Access → Infrastructure**
   - Repositorios requieren interfaz de base de datos

6. **Application Services → Infrastructure**
   - Servicios requieren almacenamiento, cola de mensajes y email

7. **ML/AI Internal**
   - Componentes ML requieren la interfaz de modelos ML

---

## 📝 Notas Importantes

### Convenciones de Nomenclatura

1. **Interfaces**: Prefijo `I` seguido del nombre (ej: `IAuthentication`)
2. **Componentes**: Nombre descriptivo sin prefijos (ej: `Authentication Service`)
3. **Nodos**: Nombre del recurso hardware/software (ej: `PostgreSQL Database`)

### Dependencias

- **Líneas punteadas** indican dependencias entre componentes
- Las dependencias muestran **qué interfaces requiere cada componente**
- La dirección de la dependencia va desde el componente que **requiere** hacia el componente que **proporciona**

### Acoplamiento

- El diagrama muestra un diseño **bajo acoplamiento**: los componentes se comunican a través de interfaces bien definidas
- Esto permite **cambios internos** en los componentes sin afectar a otros componentes

---

## 🎨 Símbolos y Colores

- **Componentes** (blanco): Módulos de software principales
- **Interfaces** (azul claro): Contratos entre componentes
- **Nodos** (amarillo): Recursos de infraestructura
- **Paquetes** (gris claro): Agrupaciones lógicas
- **Líneas punteadas**: Dependencias
- **Líneas sólidas**: Relaciones de composición/agregación

---

## 🔍 Cómo Leer el Diagrama

1. **Identifica los componentes principales** en cada paquete
2. **Observa las interfaces** que cada componente proporciona o requiere
3. **Sigue las dependencias** para entender el flujo de comunicación
4. **Identifica los nodos** de infraestructura que soportan el sistema
5. **Entiende las capas**: Frontend → API → Services → ML/Data → Infrastructure

---

## 📚 Beneficios del Diagrama

Este diagrama de componentes ayuda a:

1. **Visualizar la estructura física** del sistema CacaoScan
2. **Entender las dependencias** entre componentes
3. **Identificar interfaces** y contratos entre componentes
4. **Planificar cambios** sin romper el sistema
5. **Documentar la arquitectura** para nuevos desarrolladores
6. **Identificar puntos de extensión** (nuevos servicios pueden implementar interfaces existentes)

---

**Última actualización**: Generado basado en el análisis del código base de CacaoScan

