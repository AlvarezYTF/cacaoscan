# Flujo Completo: Crear Finca (Frontend → Backend)

## Resumen del Flujo

```
Frontend (Vue.js)
  ↓
FincaForm.vue (Componente)
  ↓
useFincas.js (Composable)
  ↓
fincasApi.js (Service API)
  ↓ HTTP POST /api/v1/fincas/
Backend (Django REST Framework)
  ↓
FincaListCreateView.post() (Controller/View)
  ↓
FincaSerializer (Validación)
  ↓
FincaService (Lógica de Negocio)
  ↓
Finca Model (Base de Datos)
  ↓
PostgreSQL
```

---

## 1. FRONTEND - Componente Vue

### `frontend/src/components/common/FincasViewComponents/FincaForm.vue`

**Responsabilidad**: Formulario de creación/edición de fincas

**Flujo**:
1. Usuario llena el formulario con datos de la finca
2. Al hacer submit, se ejecuta `handleSubmit()`
3. Se formatean los datos del formulario
4. Se llama a `createFinca()` del composable `useFincas`

**Código clave:**
```347:507:frontend/src/components/common/FincasViewComponents/FincaForm.vue
<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import fincasApi, { getAgricultores } from '@/services/fincasApi'
import { useFincasStore } from '@/stores/fincas'
import { useAuthStore } from '@/stores/auth'
import { useFormValidation } from '@/composables/useFormValidation'
import { useNotifications } from '@/composables/useNotifications'
import { useFincas } from '@/composables/useFincas'

const props = defineProps({
  finca: {
    type: Object,
    default: null
  },
  isEditing: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'saved'])

const fincasStore = useFincasStore()
const authStore = useAuthStore()
const { errors, mapServerErrors, scrollToFirstError } = useFormValidation()
const { showSuccess, showError } = useNotifications()
const { create: createFincaComposable, update: updateFincaComposable, isLoading: isFincasLoading } = useFincas({
  onFincaCreate: () => {
    showSuccess('La finca se creó correctamente.')
  },
  onFincaUpdate: () => {
    showSuccess('La finca se actualizó correctamente.')
  }
})

// ... código del formulario ...

const saveFinca = async (formattedData) => {
  if (props.isEditing) {
    await fincasStore.update(props.finca.id, formattedData)
    return 'Finca actualizada'
  }
  await fincasStore.create(formattedData)
  return 'Finca creada'
}
```

**Archivos relacionados**:
- `frontend/src/views/common/FincasView.vue` - Vista que contiene el formulario
- `frontend/src/components/common/FincasViewComponents/FincaList.vue` - Lista de fincas

---

## 2. FRONTEND - Composable (Lógica Reactiva)

### `frontend/src/composables/useFincas.js`

**Responsabilidad**: Lógica reactiva y estado para gestión de fincas

**Flujo**:
1. Recibe los datos del formulario
2. Formatea los datos según el formato esperado por la API
3. Llama al servicio API `fincasApi.createFinca()`
4. Maneja estados de loading y error
5. Retorna el resultado

---

## 3. FRONTEND - Servicio API

### `frontend/src/services/fincasApi.js`

**Responsabilidad**: Cliente HTTP para comunicación con el backend

**Flujo**:
1. Recibe los datos de la finca
2. Construye la petición HTTP POST
3. Envía la petición a `/api/v1/fincas/`
4. Maneja la respuesta y errores
5. Retorna los datos de la finca creada

---

## 4. BACKEND - Routing

### `backend/fincas_app/urls.py` o `backend/api/urls.py`

**Responsabilidad**: Enrutar la petición HTTP a la vista correcta

**Endpoint**: `POST /api/v1/fincas/`

---

## 5. BACKEND - Vista/Controller

### `backend/fincas_app/views/finca/finca_views.py`

**Clase**: `FincaListCreateView`

**Responsabilidad**: 
- Recibir la petición HTTP
- Validar permisos del usuario
- Deserializar y validar datos
- Llamar al servicio de negocio
- Retornar respuesta HTTP

**Flujo**:
```174:211:backend/fincas_app/views/finca/finca_views.py
    def post(self, request):
        """Crear nueva finca."""
        try:
            import traceback
            import sys
            
            # Obtener el agricultor desde request.data si está presente, sino usar request.user
            agricultor = request.user
            if 'agricultor' in request.data:
                from django.contrib.auth.models import User
                try:
                    agricultor = User.objects.get(id=request.data['agricultor'])
                except User.DoesNotExist:
                    return Response({
                        'error': 'Agricultor no encontrado',
                        'details': 'El ID de agricultor proporcionado no existe'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Creando finca con datos: {request.data}, agricultor: {agricultor.id}")
            
            serializer = FincaSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                # Si ya está el agricultor en request.data, usar el que vino en el serializer validado
                # sino, usar el agricultor extraído
                finca = serializer.save(agricultor=agricultor)
                
                logger.info(f"Finca '{finca.nombre}' creada por usuario {request.user.username} para agricultor {agricultor.id}")
                
                return self.create_finca_response(finca)
            else:
                logger.error(f"Errores de validación: {serializer.errors}")
                return self.handle_validation_error(serializer.errors)
                
        except Exception as e:
            logger.error(f"Error creando finca para usuario {request.user.username}: {e}")
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            return self.handle_finca_error(e, "creando finca")
```

---

## 6. BACKEND - Serializer

### `backend/fincas_app/serializers/finca_serializers.py`

**Clase**: `FincaSerializer`

**Responsabilidad**:
- Validar datos de entrada
- Validar campos requeridos
- Validar tipos de datos
- Validar reglas de negocio (nombre único por agricultor, hectáreas positivas, etc.)

---

## 7. BACKEND - Modelo

### `backend/fincas_app/models/finca_models.py`

**Clase**: `Finca`

**Responsabilidad**:
- Representar la entidad Finca en la base de datos
- Definir campos y relaciones
- Implementar métodos del modelo

---

## Endpoint de la API

**URL:** `POST /api/v1/fincas/`

**Autenticación:** Requerida (IsAuthenticated)

**Content-Type:** `application/json`

**Parámetros:**
- `nombre`: Nombre de la finca (requerido)
- `ubicacion`: Ubicación/dirección (requerido)
- `municipio`: Municipio (requerido)
- `departamento`: Departamento (requerido)
- `hectareas`: Hectáreas (requerido, número positivo)
- `coordenadas_lat`: Latitud GPS (opcional)
- `coordenadas_lng`: Longitud GPS (opcional)
- `descripcion`: Descripción adicional (opcional)
- `agricultor`: ID del agricultor (opcional, por defecto usuario actual)

**Respuesta exitosa (201 Created):**
```json
{
  "id": 1,
  "nombre": "Finca El Paraíso",
  "ubicacion": "Vereda La Esperanza",
  "municipio": "San José",
  "departamento": "Cundinamarca",
  "hectareas": 5.5,
  "coordenadas_lat": 4.6097,
  "coordenadas_lng": -74.0817,
  "descripcion": "Finca dedicada al cultivo de cacao",
  "agricultor": 1,
  "activa": true,
  "created_at": "2024-12-19T10:00:00Z",
  "updated_at": "2024-12-19T10:00:00Z"
}
```

**Respuesta con errores (400 Bad Request):**
```json
{
  "error": "Error de validación",
  "details": {
    "nombre": ["Este campo es requerido"],
    "hectareas": ["Debe ser un número positivo"]
  }
}
```

---

## Comandos de Test

### Configuración Inicial

**Desde el directorio `backend/`:**

```bash
# Asegúrate de estar en el directorio backend/
cd backend

# Activar entorno virtual (si no está activo)
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### Tests de Vistas (Crear Finca)

**Archivo:** `backend/fincas_app/tests/test_finca_views.py` (si existe)

#### Ejecutar todos los tests de creación de fincas:

```bash
# Desde backend/
pytest fincas_app/tests/test_finca_views.py::TestFincaListCreateView -v
```

#### Tests específicos:

```bash
# Test: Crear finca exitosa
pytest fincas_app/tests/test_finca_views.py::TestFincaListCreateView::test_post_success -v

# Test: Campos requeridos faltantes
pytest fincas_app/tests/test_finca_views.py::TestFincaListCreateView::test_post_missing_fields -v

# Test: Nombre duplicado para el mismo agricultor
pytest fincas_app/tests/test_finca_views.py::TestFincaListCreateView::test_post_duplicate_name -v

# Test: Hectáreas negativas
pytest fincas_app/tests/test_finca_views.py::TestFincaListCreateView::test_post_negative_hectareas -v

# Test: Coordenadas GPS inválidas
pytest fincas_app/tests/test_finca_views.py::TestFincaListCreateView::test_post_invalid_coordinates -v

# Test: Sin autenticación
pytest fincas_app/tests/test_finca_views.py::TestFincaListCreateView::test_post_unauthenticated -v
```

### Tests de Serializers

**Archivo:** `backend/fincas_app/tests/test_finca_serializers.py` (si existe)

```bash
# Test: Validación de FincaSerializer
pytest fincas_app/tests/test_finca_serializers.py::TestFincaSerializer -v

# Test: Validación de campos requeridos
pytest fincas_app/tests/test_finca_serializers.py::TestFincaSerializer::test_required_fields -v

# Test: Validación de hectáreas positivas
pytest fincas_app/tests/test_finca_serializers.py::TestFincaSerializer::test_hectareas_positive -v
```

### Ejecutar Todos los Tests de Fincas

```bash
# Desde backend/
pytest fincas_app/tests/ -v -k finca
```

### Ejecutar con Cobertura

```bash
# Desde backend/
pytest fincas_app/tests/test_finca_views.py --cov=fincas_app.views.finca.finca_views --cov-report=html
```

---

## Flujo Completo Paso a Paso

### 1. Usuario completa formulario en el frontend
- Validación inicial en el cliente (campos requeridos, tipos de datos)
- Preparación de datos para envío

### 2. Petición HTTP POST al backend
- Endpoint: `/api/v1/fincas/`
- Headers: `Content-Type: application/json`, `Authorization: Bearer <token>`
- Body: Datos de la finca en JSON

### 3. Backend procesa la petición
- **Validación de autenticación:** Verifica que el usuario esté autenticado
- **Validación de permisos:** Verifica que el usuario tenga rol de Agricultor o Administrador
- **Deserialización:** `FincaSerializer` valida y deserializa los datos
- **Validación de negocio:** Verifica nombre único por agricultor, hectáreas positivas, etc.
- **Creación:** Crea el registro de Finca en la base de datos
- **Asociación:** Asocia la finca al agricultor (usuario actual o especificado)
- **Auditoría:** Registra el evento de creación

### 4. Respuesta al frontend
- **201 Created:** Finca creada exitosamente con datos completos
- **400 Bad Request:** Errores de validación
- **401 Unauthorized:** Usuario no autenticado

### 5. Frontend procesa la respuesta
- Muestra mensaje de éxito
- Actualiza la lista de fincas
- Cierra el modal de formulario
- O muestra errores de validación específicos

---

## Validaciones Implementadas

### Campos Requeridos
- **Nombre:** Requerido, único por agricultor
- **Ubicación:** Requerido
- **Municipio:** Requerido
- **Departamento:** Requerido
- **Hectáreas:** Requerido, número positivo mayor a cero

### Reglas de Negocio
- **Nombre único:** El nombre debe ser único para cada agricultor
- **Hectáreas positivas:** Debe ser un número mayor a cero
- **Coordenadas GPS:** Opcionales pero deben ser válidas si se proporcionan
- **Agricultor:** Por defecto el usuario actual, o puede especificarse si es admin

---

## Ejemplo de Uso con cURL

```bash
# Crear una finca
curl -X POST http://localhost:8000/api/v1/fincas/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Finca El Paraíso",
    "ubicacion": "Vereda La Esperanza",
    "municipio": "San José",
    "departamento": "Cundinamarca",
    "hectareas": 5.5,
    "coordenadas_lat": 4.6097,
    "coordenadas_lng": -74.0817,
    "descripcion": "Finca dedicada al cultivo de cacao"
  }'
```

---

## Troubleshooting

### Error: "Este campo es requerido"
**Causa:** Faltan campos obligatorios en el formulario.
**Solución:** Completar todos los campos requeridos.

### Error: "Ya existe una finca con este nombre"
**Causa:** El nombre de la finca ya está registrado para el agricultor.
**Solución:** Usar un nombre diferente para la finca.

### Error: "Hectáreas debe ser un número positivo"
**Causa:** El valor de hectáreas es negativo o cero.
**Solución:** Ingresar un valor positivo mayor a cero.

### Error: 401 Unauthorized
**Causa:** El usuario no está autenticado.
**Solución:** Iniciar sesión y obtener un token válido.

### Error: "Agricultor no encontrado"
**Causa:** El ID de agricultor proporcionado no existe.
**Solución:** Verificar que el ID de agricultor sea válido.

---

## Archivos Relacionados

### Backend
- `backend/fincas_app/views/finca/finca_views.py` - Vistas de fincas
- `backend/fincas_app/serializers/finca_serializers.py` - Serializers de fincas
- `backend/fincas_app/models/finca_models.py` - Modelos de fincas
- `backend/fincas_app/urls.py` - URLs de fincas

### Frontend
- `frontend/src/components/common/FincasViewComponents/FincaForm.vue` - Formulario de finca
- `frontend/src/composables/useFincas.js` - Composable de fincas
- `frontend/src/services/fincasApi.js` - Servicio de API de fincas
- `frontend/src/stores/fincas.js` - Store de fincas (Pinia)
- `frontend/src/views/common/FincasView.vue` - Vista principal de fincas

---

## Notas Adicionales

- El nombre de la finca debe ser único por agricultor, pero diferentes agricultores pueden tener fincas con el mismo nombre
- Las coordenadas GPS son opcionales pero se recomienda incluirlas para ubicación geográfica
- Un agricultor puede tener múltiples fincas
- La finca se crea con estado `activa=True` por defecto
- Todos los eventos de creación se registran en auditoría

