# Flujo Completo: Crear un Lote (Modelo → Frontend)

## Resumen del Flujo

```
Frontend (Vue.js)
  ↓
LoteForm.vue (Componente)
  ↓
useLotes.js (Composable)
  ↓
lotesApi.js (Service API)
  ↓ HTTP POST /api/v1/lotes/
Backend (Django REST Framework)
  ↓
LoteListCreateView (Controller/View)
  ↓
LoteSerializer (Validación)
  ↓
LoteService (Lógica de Negocio)
  ↓
Lote Model (Base de Datos)
  ↓
PostgreSQL
```

---

## 1. FRONTEND - Componente Vue

### `frontend/src/components/LoteForm.vue`

**Responsabilidad**: Formulario de creación/edición de lotes

**Flujo**:
1. Usuario llena el formulario con datos del lote
2. Al hacer submit, se ejecuta `handleSubmit()`
3. Se formatean los datos del formulario
4. Se llama a `createLote()` del composable `useLotes`

```javascript
// Fragmento del flujo en LoteForm.vue
const { createLote, updateLote, loading, error } = useLotes()

const handleSubmit = async () => {
  try {
    const formattedData = {
      finca: props.fincaId,
      nombre: form.nombre,
      variedad: form.variedad,
      fecha_plantacion: form.fecha_plantacion,
      area_hectareas: form.area_hectareas,
      // ... otros campos
    }
    
    await createLote(formattedData)
    // Manejo de éxito (redirección, notificación, etc.)
  } catch (error) {
    // Manejo de errores
  }
}
```

**Archivos relacionados**:
- `frontend/src/views/FincaLotesView.vue` - Vista que contiene el formulario
- `frontend/src/views/FincaDetailView.vue` - Vista de detalle que puede crear lotes

---

## 2. FRONTEND - Composable (Lógica Reactiva)

### `frontend/src/composables/useLotes.js`

**Responsabilidad**: Lógica reactiva y estado para gestión de lotes

**Flujo**:
1. Recibe los datos del formulario
2. Formatea los datos según el formato esperado por la API
3. Llama al servicio API `lotesApi.createLote()`
4. Maneja estados de loading y error
5. Retorna el resultado

```javascript
// Fragmento del flujo en useLotes.js
import { lotesApi } from '@/services/lotesApi'
import { ref } from 'vue'

export function useLotes() {
  const loading = ref(false)
  const error = ref(null)
  
  const createLote = async (loteData) => {
    loading.value = true
    error.value = null
    
    try {
      // Formatear datos si es necesario
      const formatted = {
        ...loteData,
        fecha_plantacion: formatDate(loteData.fecha_plantacion),
        // ... otros formatos
      }
      
      // Llamar al servicio API
      const result = await lotesApi.createLote(formatted)
      
      // Actualizar estado si es necesario
      // Emitir eventos si es necesario
      
      return result
    } catch (err) {
      error.value = err
      throw err
    } finally {
      loading.value = false
    }
  }
  
  return {
    createLote,
    loading,
    error
  }
}
```

---

## 3. FRONTEND - Servicio API

### `frontend/src/services/lotesApi.js`

**Responsabilidad**: Cliente HTTP para comunicación con el backend

**Flujo**:
1. Recibe los datos del lote
2. Construye la petición HTTP POST
3. Envía la petición a `/api/v1/lotes/`
4. Maneja la respuesta y errores
5. Retorna los datos del lote creado

```javascript
// Fragmento del flujo en lotesApi.js
import api from './api'

export async function createLote(loteData) {
  try {
    const response = await api.post('/api/v1/lotes/', loteData)
    return response.data
  } catch (error) {
    // Manejo de errores HTTP
    throw handleApiError(error)
  }
}
```

**Configuración**:
- Base URL: Configurada en `api.js` o `apiClient.js`
- Headers: JWT token incluido automáticamente
- Interceptores: Manejo de errores y autenticación

---

## 4. BACKEND - Routing

### `backend/fincas_app/urls.py` o `backend/api/urls.py`

**Responsabilidad**: Enrutar la petición HTTP a la vista correcta

**Flujo**:
```python
# URLs configuradas
urlpatterns = [
    path('lotes/', LoteListCreateView.as_view(), name='lote-list-create'),
    # ...
]
```

**Endpoint**: `POST /api/v1/lotes/`

---

## 5. BACKEND - Vista/Controller

### `backend/fincas_app/views/finca/lote_views.py`

**Clase**: `LoteListCreateView`

**Responsabilidad**: 
- Recibir la petición HTTP
- Validar permisos del usuario
- Deserializar y validar datos
- Llamar al servicio de negocio
- Retornar respuesta HTTP

**Flujo**:
```python
class LoteListCreateView(PaginationMixin, LotePermissionMixin, APIView):
    """
    Vista para listar y crear lotes.
    GET: Lista lotes (con paginación)
    POST: Crea un nuevo lote
    """
    
    def post(self, request, *args, **kwargs):
        # 1. Validar permisos (LotePermissionMixin)
        # 2. Deserializar datos con LoteSerializer
        serializer = LoteSerializer(data=request.data)
        
        # 3. Validar datos
        if not serializer.is_valid():
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 4. Obtener usuario autenticado
        user = request.user
        
        # 5. Llamar al servicio de negocio
        lote_service = LoteService()
        result = lote_service.create_lote(
            user=user,
            validated_data=serializer.validated_data
        )
        
        # 6. Verificar resultado del servicio
        if not result.success:
            return Response(
                result.to_dict(),
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 7. Serializar respuesta
        response_serializer = LoteDetailSerializer(result.data)
        
        # 8. Retornar respuesta HTTP
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
```

**Mixins utilizados**:
- `LotePermissionMixin`: Valida permisos del usuario
- `PaginationMixin`: Agrega funcionalidad de paginación

---

## 6. BACKEND - Serializer (Validación)

### `backend/api/serializers/finca_serializers.py`

**Clase**: `LoteSerializer`

**Responsabilidad**:
- Validar estructura de datos
- Validar tipos de datos
- Validar reglas de negocio básicas
- Convertir datos de entrada a formato del modelo

**Flujo**:
```python
class LoteSerializer(serializers.ModelSerializer):
    """
    Serializer para crear y actualizar lotes.
    """
    
    class Meta:
        model = Lote
        fields = [
            'id',
            'finca',
            'identificador',
            'nombre',
            'variedad',
            'fecha_plantacion',
            'fecha_cosecha',
            'area_hectareas',
            'estado',
            'descripcion',
            'coordenadas_lat',
            'coordenadas_lng',
            'activo',
            # ... otros campos
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validaciones personalizadas:
        - Fecha de cosecha debe ser >= fecha de plantación
        - Área debe ser positiva
        - Identificador único por finca
        """
        # Validaciones aquí
        return data
    
    def validate_area_hectareas(self, value):
        """Validar que el área sea positiva."""
        if value <= 0:
            raise serializers.ValidationError(
                "El área debe ser mayor a cero"
            )
        return value
```

**Validaciones realizadas**:
- Campos requeridos
- Tipos de datos correctos
- Reglas de negocio (fechas, áreas, etc.)
- Relaciones (finca existe, usuario tiene permisos)

---

## 7. BACKEND - Servicio de Negocio

### `backend/fincas_app/services/lote_service.py`

**Clase**: `LoteService`

**Responsabilidad**:
- Lógica de negocio para crear lotes
- Validaciones de negocio adicionales
- Transacciones de base de datos
- Auditoría y logging
- Manejo de errores

**Flujo**:
```python
class LoteService(BaseService):
    """
    Servicio para gestión de lotes.
    """
    
    def create_lote(
        self, 
        user: User, 
        validated_data: dict
    ) -> ServiceResult:
        """
        Crea un nuevo lote.
        
        Args:
            user: Usuario que crea el lote
            validated_data: Datos validados del serializer
            
        Returns:
            ServiceResult con el lote creado o error
        """
        try:
            # 1. Validar permisos del usuario
            finca = validated_data.get('finca')
            if not self._can_user_manage_finca(user, finca):
                return ServiceResult.permission_error(
                    "No tiene permisos para crear lotes en esta finca"
                )
            
            # 2. Validaciones de negocio adicionales
            if not self._validate_lote_business_rules(validated_data):
                return ServiceResult.validation_error(
                    "No se cumplen las reglas de negocio"
                )
            
            # 3. Ejecutar en transacción
            with transaction.atomic():
                # 4. Crear el lote
                lote = Lote.objects.create(
                    finca=finca,
                    nombre=validated_data['nombre'],
                    variedad=validated_data['variedad'],
                    fecha_plantacion=validated_data['fecha_plantacion'],
                    fecha_cosecha=validated_data.get('fecha_cosecha'),
                    area_hectareas=validated_data['area_hectareas'],
                    estado=validated_data.get('estado', 'activo'),
                    descripcion=validated_data.get('descripcion', ''),
                    # ... otros campos
                )
                
                # 5. Crear log de auditoría
                self.create_audit_log(
                    user=user,
                    action='create_lote',
                    resource_type='Lote',
                    resource_id=lote.id,
                    details={'finca_id': finca.id}
                )
                
                # 6. Log de información
                self.log_info(
                    f"Lote {lote.id} creado por {user.username}"
                )
            
            # 7. Retornar resultado exitoso
            return ServiceResult.success(
                data=lote,
                message="Lote creado exitosamente"
            )
            
        except ValidationError as e:
            return ServiceResult.validation_error(
                str(e),
                details={'errors': e.message_dict}
            )
        except Exception as e:
            self.log_error(f"Error creando lote: {str(e)}")
            return ServiceResult.error(
                ServiceError(f"Error al crear lote: {str(e)}")
            )
```

**Validaciones de negocio**:
- Usuario tiene permisos sobre la finca
- Finca existe y está activa
- Identificador único por finca (si se proporciona)
- Fechas válidas
- Área válida

---

## 8. BACKEND - Modelo (ORM)

### `backend/fincas_app/models.py`

**Clase**: `Lote`

**Responsabilidad**:
- Definir estructura de datos en base de datos
- Validaciones a nivel de modelo
- Métodos y propiedades del modelo
- Relaciones con otros modelos

**Flujo**:
```python
class Lote(TimeStampedModel):
    """
    Modelo para gestionar lotes de cacao dentro de fincas.
    """
    
    finca = models.ForeignKey(
        Finca, 
        on_delete=models.CASCADE, 
        related_name='lotes'
    )
    nombre = models.CharField(max_length=200)
    variedad = models.CharField(max_length=100)
    fecha_plantacion = models.DateField()
    fecha_cosecha = models.DateField(null=True, blank=True)
    area_hectareas = models.DecimalField(
        max_digits=8, 
        decimal_places=2
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    # ... otros campos
    
    class Meta:
        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=models.Q(area_hectareas__gt=0),
                name='fincas_app_lote_area_positiva'
            ),
            models.CheckConstraint(
                check=models.Q(fecha_cosecha__isnull=True) | 
                       models.Q(fecha_cosecha__gte=models.F('fecha_plantacion')),
                name='fincas_app_lote_fecha_cosecha_valida'
            ),
        ]
    
    def clean(self):
        """Validaciones a nivel de modelo."""
        # Validaciones adicionales
        pass
    
    def save(self, *args, **kwargs):
        """Sobrescribir save para ejecutar validaciones."""
        self.full_clean()
        super().save(*args, **kwargs)
```

**Cuando se ejecuta `Lote.objects.create()`**:
1. Django ORM valida los datos
2. Ejecuta `clean()` si está definido
3. Ejecuta validaciones de constraints
4. Inserta el registro en PostgreSQL
5. Retorna la instancia creada

---

## 9. BASE DE DATOS

### PostgreSQL

**Tabla**: `fincas_app_lote` (o nombre configurado en Meta.db_table)

**Flujo**:
1. Django ORM genera SQL INSERT
2. Se ejecuta la transacción
3. Se inserta el registro
4. Se retorna el ID generado
5. Se confirma la transacción

---

## 10. RESPUESTA (Camino de Vuelta)

### Flujo de Respuesta

```
PostgreSQL
  ↓
Lote Model (instancia creada)
  ↓
LoteService (ServiceResult.success con data=lote)
  ↓
LoteDetailSerializer (serializa el lote)
  ↓
LoteListCreateView (Response HTTP 201)
  ↓ HTTP Response JSON
lotesApi.js (retorna response.data)
  ↓
useLotes.js (retorna resultado)
  ↓
LoteForm.vue (maneja respuesta)
  ↓
UI Actualizada (notificación, redirección, etc.)
```

**Estructura de respuesta JSON**:
```json
{
  "id": 1,
  "finca": 5,
  "nombre": "Lote Norte",
  "variedad": "Criollo",
  "fecha_plantacion": "2023-01-15",
  "area_hectareas": "2.50",
  "estado": "activo",
  "created_at": "2024-01-20T10:30:00Z",
  "updated_at": "2024-01-20T10:30:00Z"
}
```

---

## 11. MANEJO DE ERRORES

### Puntos de Validación y Error

1. **Frontend (LoteForm.vue)**:
   - Validación de campos requeridos
   - Validación de formato de fechas
   - Validación de tipos de datos

2. **Serializer (LoteSerializer)**:
   - Validación de estructura
   - Validación de tipos
   - Validación de reglas básicas

3. **Servicio (LoteService)**:
   - Validación de permisos
   - Validación de reglas de negocio
   - Validación de integridad referencial

4. **Modelo (Lote)**:
   - Validación de constraints de base de datos
   - Validación de integridad referencial (foreign keys)

5. **Base de Datos**:
   - Constraints de base de datos
   - Validación de tipos SQL
   - Validación de unicidad

### Propagación de Errores

```
Error en Base de Datos
  ↓
Modelo lanza excepción
  ↓
Servicio captura y retorna ServiceResult.error
  ↓
Vista retorna Response HTTP 400/500
  ↓
API Service lanza excepción
  ↓
Composable propaga error
  ↓
Componente muestra mensaje de error al usuario
```

---

## 12. FLUJO COMPLETO CON DIAGRAMA

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (Vue.js)                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │ LoteForm.vue │───▶│ useLotes.js  │───▶│ lotesApi.js  │ │
│  │ (Componente) │    │ (Composable) │    │ (API Client) │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                               │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            │ HTTP POST /api/v1/lotes/
                            │ { finca, nombre, variedad, ... }
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  BACKEND (Django REST)                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐                                       │
│  │ URLs (routing)   │                                       │
│  └────────┬─────────┘                                       │
│           │                                                   │
│           ▼                                                   │
│  ┌──────────────────┐                                       │
│  │LoteListCreateView│                                       │
│  │  (Controller)    │                                       │
│  └────────┬─────────┘                                       │
│           │                                                   │
│           ▼                                                   │
│  ┌──────────────────┐                                       │
│  │LoteSerializer    │                                       │
│  │  (Validación)    │                                       │
│  └────────┬─────────┘                                       │
│           │                                                   │
│           ▼                                                   │
│  ┌──────────────────┐                                       │
│  │  LoteService     │                                       │
│  │ (Lógica Negocio) │                                       │
│  └────────┬─────────┘                                       │
│           │                                                   │
│           ▼                                                   │
│  ┌──────────────────┐                                       │
│  │   Lote Model     │                                       │
│  │     (ORM)        │                                       │
│  └────────┬─────────┘                                       │
│           │                                                   │
└───────────┼───────────────────────────────────────────────────┘
            │
            │ SQL INSERT
            ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL                                │
│                                                               │
│  INSERT INTO fincas_app_lote (...)                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 13. PUNTOS CLAVE DEL FLUJO

### Separación de Responsabilidades

1. **Frontend**: Presentación y experiencia de usuario
2. **Composable**: Lógica reactiva y estado
3. **API Service**: Comunicación HTTP
4. **Controller/View**: Recepción de peticiones HTTP
5. **Serializer**: Validación y transformación de datos
6. **Service**: Lógica de negocio
7. **Model**: Estructura de datos y validaciones básicas
8. **Database**: Persistencia

### Validaciones en Cada Capa

- **Frontend**: UX y formato básico
- **Serializer**: Estructura y tipos
- **Service**: Reglas de negocio
- **Model**: Constraints de base de datos

### Manejo de Transacciones

- Las transacciones se manejan en el **Service** usando `transaction.atomic()`
- Garantiza consistencia de datos
- Permite rollback en caso de error

### Auditoría

- Se crea log de auditoría en el **Service** después de crear el lote
- Registra quién, qué, cuándo y detalles adicionales

---

## 14. TESTS PARA CREAR LOTE

### Backend - Tests del Servicio

**Archivo**: `backend/fincas_app/tests/test_lote_service.py`

#### Test de Creación Exitosa

```python
import pytest
from decimal import Decimal
from datetime import date
from django.contrib.auth.models import User
from fincas_app.services.lote_service import LoteService
from fincas_app.models import Finca, Lote

@pytest.mark.django_db
class TestLoteService:
    """Tests for LoteService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance."""
        return LoteService()
    
    @pytest.fixture
    def user(self, db):
        """Create test user."""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return User.objects.create_user(
            username=f'testuser_{unique_id}',
            email=f'test_{unique_id}@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def finca(self, user):
        """Create test finca."""
        return Finca.objects.create(
            agricultor=user,
            nombre='Test Finca',
            hectareas=Decimal('10.0'),
            municipio='Test Municipio',
            departamento='Test Departamento'
        )
    
    def test_create_lote_success(self, service, user, finca):
        """Test creating lote successfully."""
        lote_data = {
            'finca_id': finca.id,
            'area_hectareas': 5.0,
            'nombre': 'Test Lote',
            'identificador': 'LOTE-001',
            'variedad': 'Criollo',
            'estado': 'activo',
            'fecha_plantacion': date.today()
        }
        
        result = service.create_lote(lote_data, user)
        
        assert result.success
        assert result.data['identificador'] == 'LOTE-001'
        assert Lote.objects.filter(identificador='LOTE-001').exists()
```

#### Tests de Validación

```python
    def test_validate_lote_required_fields_missing_finca(self, service):
        """Test validating lote with missing finca."""
        result = service._validate_lote_required_fields(
            None, 5.0, 'Test', 'LOTE-001'
        )
        
        assert result is not None
        assert not result.success
    
    def test_validate_lote_area_negative(self, service, finca):
        """Test validating negative area."""
        result = service._validate_lote_area(-1, finca)
        
        assert result is not None
        assert not result.success
    
    def test_validate_lote_area_exceeds_finca(self, service, finca):
        """Test validating area that exceeds finca area."""
        # Finca tiene 10 hectáreas
        result = service._validate_lote_area(20.0, finca)
        
        assert result is not None
        assert not result.success
    
    def test_validate_lote_text_fields_duplicate_identifier(self, service, finca):
        """Test validating duplicate identifier."""
        from datetime import date
        # Crear lote existente
        Lote.objects.create(
            finca=finca,
            nombre='Test Lote',
            identificador='LOTE-001',
            variedad='Criollo',
            area_hectareas=Decimal('1.0'),
            fecha_plantacion=date.today()
        )
        
        # Intentar crear otro con mismo identificador
        result = service._validate_lote_text_fields(
            'Test', 'LOTE-001', 'Criollo', finca
        )
        
        assert result is not None
        assert not result.success
```

#### Ejecutar Tests del Backend

**IMPORTANTE**: Ejecutar desde el directorio `backend/`

```bash
# Desde el directorio backend/
cd backend

# Ejecutar todos los tests del servicio de lotes
pytest fincas_app/tests/test_lote_service.py -v

# Ejecutar un test específico
pytest fincas_app/tests/test_lote_service.py::TestLoteService::test_create_lote_success -v

# Ejecutar con cobertura
pytest fincas_app/tests/test_lote_service.py --cov=fincas_app.services.lote_service --cov-report=html

# Ejecutar todos los tests de fincas_app
pytest fincas_app/tests/ -v
```

---

### Backend - Tests de la Vista/Controller

**Nota**: Actualmente no hay tests específicos para `LoteListCreateView` en el proyecto. Los tests de vistas están en `test_finca_views.py` pero solo cubren vistas de fincas. 

**Para crear tests de vistas de lotes**, crear un nuevo archivo o agregar a `test_finca_views.py`:

**Archivo sugerido**: `backend/fincas_app/tests/test_lote_views.py` (crear nuevo archivo)

#### Test de POST Request

```python
import pytest
from decimal import Decimal
from datetime import date
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from fincas_app.models import Finca

@pytest.mark.django_db
class TestLoteListCreateView:
    """Tests for LoteListCreateView."""
    
    @pytest.fixture
    def client(self):
        """Create API client."""
        return APIClient()
    
    @pytest.fixture
    def user(self, db):
        """Create test user."""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def finca(self, user):
        """Create test finca."""
        return Finca.objects.create(
            agricultor=user,
            nombre='Test Finca',
            hectareas=Decimal('10.0'),
            municipio='Test Municipio',
            departamento='Test Departamento'
        )
    
    def test_create_lote_success(self, client, user, finca):
        """Test POST request to create lote."""
        # Autenticar usuario
        client.force_authenticate(user=user)
        
        # Datos del lote
        lote_data = {
            'finca': finca.id,
            'nombre': 'Test Lote',
            'identificador': 'LOTE-001',
            'variedad': 'Criollo',
            'fecha_plantacion': '2024-01-15',
            'area_hectareas': '5.0',
            'estado': 'activo'
        }
        
        # Hacer petición POST
        url = reverse('lote-list-create')
        response = client.post(url, lote_data, format='json')
        
        # Verificar respuesta
        assert response.status_code == 201
        assert response.data['identificador'] == 'LOTE-001'
        assert response.data['nombre'] == 'Test Lote'
    
    def test_create_lote_unauthorized(self, client, finca):
        """Test creating lote without authentication."""
        lote_data = {
            'finca': finca.id,
            'nombre': 'Test Lote',
            'variedad': 'Criollo',
            'fecha_plantacion': '2024-01-15',
            'area_hectareas': '5.0'
        }
        
        url = reverse('lote-list-create')
        response = client.post(url, lote_data, format='json')
        
        assert response.status_code == 401  # Unauthorized
    
    def test_create_lote_invalid_data(self, client, user, finca):
        """Test creating lote with invalid data."""
        client.force_authenticate(user=user)
        
        # Datos inválidos (área negativa)
        lote_data = {
            'finca': finca.id,
            'nombre': 'Test Lote',
            'variedad': 'Criollo',
            'fecha_plantacion': '2024-01-15',
            'area_hectareas': '-5.0'  # Inválido
        }
        
        url = reverse('lote-list-create')
        response = client.post(url, lote_data, format='json')
        
        assert response.status_code == 400  # Bad Request
        assert 'area_hectareas' in response.data
```

#### Ejecutar Tests de Vista

**IMPORTANTE**: Ejecutar desde el directorio `backend/`

```bash
# Desde el directorio backend/
cd backend

# Ejecutar tests de vistas
pytest fincas_app/tests/test_views.py -v

# Ejecutar con output detallado
pytest fincas_app/tests/test_views.py -v -s

# Ejecutar solo tests relacionados con lotes
pytest fincas_app/tests/test_views.py -k lote -v
```

---

### Frontend - Tests del Servicio API

**Archivo**: `frontend/src/services/__tests__/lotesApi.test.js`

#### Test de createLote

```javascript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import api from '../api'
import { createLote } from '../lotesApi'

vi.mock('../api', () => ({
  default: {
    post: vi.fn()
  }
}))

describe('lotesApi - createLote', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should create lote successfully', async () => {
    const loteData = {
      identificador: 'Lote Nuevo',
      variedad: 'Criollo',
      finca: { id: 1 },
      fecha_plantacion: '2024-01-01',
      area_hectareas: 5.5
    }
    
    const mockResponse = {
      data: {
        id: 3,
        ...loteData
      }
    }
    
    api.post.mockResolvedValue(mockResponse)

    const result = await createLote(loteData)

    expect(api.post).toHaveBeenCalledWith('/lotes/', loteData, {})
    expect(result).toEqual(mockResponse.data)
    expect(result.id).toBe(3)
    expect(result.identificador).toBe('Lote Nuevo')
  })

  it('should handle error when creating lote', async () => {
    const loteData = {
      finca: { id: 1 },
      nombre: 'Test Lote'
    }
    
    const error = new Error('Validation error')
    api.post.mockRejectedValue(error)

    await expect(createLote(loteData)).rejects.toThrow('Validation error')
    expect(api.post).toHaveBeenCalledWith('/lotes/', loteData, {})
  })

  it('should handle network error', async () => {
    const loteData = { finca: { id: 1 } }
    const error = new Error('Network error')
    api.post.mockRejectedValue(error)

    await expect(createLote(loteData)).rejects.toThrow('Network error')
  })
})
```

#### Ejecutar Tests del Servicio

```bash
# Ejecutar tests del servicio
npm run test frontend/src/services/__tests__/lotesApi.test.js

# Ejecutar con watch mode
npm run test:watch frontend/src/services/__tests__/lotesApi.test.js

# Ejecutar con cobertura
npm run test:coverage frontend/src/services/__tests__/lotesApi.test.js
```

---

### Frontend - Tests del Composable

**Archivo**: `frontend/src/composables/__tests__/useLotes.test.js`

#### Test de createLote en Composable

```javascript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useLotes } from '../useLotes.js'
import * as lotesApi from '@/services/lotesApi'

// Mock dependencies
vi.mock('@/services/lotesApi', () => ({
  validateLoteData: vi.fn(),
  formatLoteData: vi.fn(),
  createLote: vi.fn()
}))

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => ({
    user: { id: 1 },
    userRole: 'farmer'
  })
}))

vi.mock('@/stores/notifications', () => ({
  useNotificationStore: () => ({
    addNotification: vi.fn()
  })
}))

describe('useLotes - createLote', () => {
  let lotes

  beforeEach(() => {
    vi.clearAllMocks()
    lotes = useLotes()
  })

  it('should create lote successfully', async () => {
    const loteData = {
      nombre: 'Lote 1',
      finca: 1,
      variedad: 'Criollo',
      fecha_plantacion: '2024-01-15',
      area_hectareas: 5.0
    }
    
    const mockResult = {
      id: 1,
      ...loteData
    }
    
    // Mock validación exitosa
    lotesApi.validateLoteData.mockReturnValue({
      isValid: true,
      errors: []
    })
    
    // Mock formateo
    lotesApi.formatLoteData.mockReturnValue(loteData)
    
    // Mock creación exitosa
    lotesApi.createLote.mockResolvedValue(mockResult)

    const result = await lotes.createLote(loteData)

    // Verificar que se llamaron las funciones correctas
    expect(lotesApi.validateLoteData).toHaveBeenCalledWith(loteData)
    expect(lotesApi.formatLoteData).toHaveBeenCalled()
    expect(lotesApi.createLote).toHaveBeenCalled()
    
    // Verificar resultado
    expect(result).toEqual(mockResult)
    expect(lotes.loading.value).toBe(false)
    expect(lotes.error.value).toBe(null)
  })

  it('should handle validation error', async () => {
    const loteData = {
      nombre: '',  // Inválido
      finca: 1
    }
    
    // Mock validación fallida
    lotesApi.validateLoteData.mockReturnValue({
      isValid: false,
      errors: ['El nombre es requerido']
    })

    await expect(lotes.createLote(loteData)).rejects.toThrow()
    
    expect(lotesApi.createLote).not.toHaveBeenCalled()
    expect(lotes.error.value).toBeTruthy()
  })

  it('should handle create error', async () => {
    const loteData = {
      nombre: 'Lote 1',
      finca: 1
    }
    
    lotesApi.validateLoteData.mockReturnValue({
      isValid: true,
      errors: []
    })
    lotesApi.formatLoteData.mockReturnValue(loteData)
    
    const error = new Error('Create error')
    lotesApi.createLote.mockRejectedValue(error)

    await expect(lotes.createLote(loteData)).rejects.toThrow()
    
    expect(lotes.error.value).toBeTruthy()
    expect(lotes.loading.value).toBe(false)
  })

  it('should set loading state during creation', async () => {
    const loteData = { nombre: 'Lote 1', finca: 1 }
    
    lotesApi.validateLoteData.mockReturnValue({
      isValid: true,
      errors: []
    })
    lotesApi.formatLoteData.mockReturnValue(loteData)
    
    // Crear promesa que no se resuelve inmediatamente
    let resolvePromise
    const promise = new Promise((resolve) => {
      resolvePromise = resolve
    })
    lotesApi.createLote.mockReturnValue(promise)

    // Iniciar creación
    const createPromise = lotes.createLote(loteData)
    
    // Verificar que loading es true
    expect(lotes.loading.value).toBe(true)
    
    // Resolver promesa
    resolvePromise({ id: 1, ...loteData })
    await createPromise
    
    // Verificar que loading es false
    expect(lotes.loading.value).toBe(false)
  })
})
```

#### Ejecutar Tests del Composable

```bash
# Ejecutar tests del composable
npm run test frontend/src/composables/__tests__/useLotes.test.js

# Ejecutar con watch
npm run test:watch frontend/src/composables/__tests__/useLotes.test.js
```

---

### Frontend - Tests del Componente

**Archivo**: `frontend/src/components/__tests__/LoteForm.test.js` (crear si no existe)

#### Test del Componente LoteForm

```javascript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import LoteForm from '../LoteForm.vue'
import { useLotes } from '@/composables/useLotes'

// Mock composable
vi.mock('@/composables/useLotes', () => ({
  useLotes: vi.fn()
}))

describe('LoteForm - Create Lote', () => {
  let wrapper
  let mockCreateLote
  let mockUpdateLote

  beforeEach(() => {
    mockCreateLote = vi.fn()
    mockUpdateLote = vi.fn()
    
    useLotes.mockReturnValue({
      createLote: mockCreateLote,
      updateLote: mockUpdateLote,
      loading: { value: false },
      error: { value: null }
    })
  })

  it('should render create form', () => {
    wrapper = mount(LoteForm, {
      props: {
        fincaId: 1
      }
    })

    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.find('input[name="nombre"]').exists()).toBe(true)
  })

  it('should call createLote on submit', async () => {
    wrapper = mount(LoteForm, {
      props: {
        fincaId: 1
      }
    })

    // Llenar formulario
    await wrapper.find('input[name="nombre"]').setValue('Test Lote')
    await wrapper.find('input[name="variedad"]').setValue('Criollo')
    await wrapper.find('input[name="area_hectareas"]').setValue('5.0')
    await wrapper.find('input[name="fecha_plantacion"]').setValue('2024-01-15')

    // Mock respuesta exitosa
    mockCreateLote.mockResolvedValue({
      id: 1,
      nombre: 'Test Lote',
      finca: 1
    })

    // Submit formulario
    await wrapper.find('form').trigger('submit')

    // Verificar que se llamó createLote
    expect(mockCreateLote).toHaveBeenCalled()
    expect(mockCreateLote).toHaveBeenCalledWith(
      expect.objectContaining({
        finca: 1,
        nombre: 'Test Lote',
        variedad: 'Criollo',
        area_hectareas: 5.0,
        fecha_plantacion: '2024-01-15'
      })
    )
  })

  it('should show error message on create failure', async () => {
    wrapper = mount(LoteForm, {
      props: {
        fincaId: 1
      }
    })

    // Mock error
    const error = new Error('Validation error')
    mockCreateLote.mockRejectedValue(error)

    // Actualizar error en composable
    useLotes.mockReturnValue({
      createLote: mockCreateLote,
      updateLote: mockUpdateLote,
      loading: { value: false },
      error: { value: error }
    })

    await wrapper.find('form').trigger('submit')

    // Verificar que se muestra el error
    expect(wrapper.text()).toContain('error')
  })

  it('should disable submit button when loading', () => {
    useLotes.mockReturnValue({
      createLote: mockCreateLote,
      updateLote: mockUpdateLote,
      loading: { value: true },
      error: { value: null }
    })

    wrapper = mount(LoteForm, {
      props: {
        fincaId: 1
      }
    })

    const submitButton = wrapper.find('button[type="submit"]')
    expect(submitButton.attributes('disabled')).toBeDefined()
  })
})
```

#### Ejecutar Tests del Componente

```bash
# Ejecutar tests del componente
npm run test frontend/src/components/__tests__/LoteForm.test.js

# Ejecutar con coverage
npm run test:coverage frontend/src/components/__tests__/LoteForm.test.js
```

---

### Tests de Integración (E2E)

#### Test End-to-End con Cypress

**Archivo**: `frontend/cypress/e2e/lotes.cy.js` (crear si no existe)

```javascript
describe('Create Lote E2E', () => {
  beforeEach(() => {
    // Login
    cy.login('testuser', 'testpass123')
    
    // Visitar página de fincas
    cy.visit('/fincas/1/lotes')
  })

  it('should create a new lote', () => {
    // Click en botón "Nuevo Lote"
    cy.contains('Nuevo Lote').click()

    // Llenar formulario
    cy.get('input[name="nombre"]').type('Lote Test E2E')
    cy.get('input[name="identificador"]').type('LOTE-E2E-001')
    cy.get('input[name="variedad"]').type('Criollo')
    cy.get('input[name="area_hectareas"]').type('5.5')
    cy.get('input[name="fecha_plantacion"]').type('2024-01-15')

    // Submit
    cy.get('button[type="submit"]').click()

    // Verificar que aparece mensaje de éxito
    cy.contains('Lote creado exitosamente').should('be.visible')

    // Verificar que el lote aparece en la lista
    cy.contains('Lote Test E2E').should('be.visible')
    cy.contains('LOTE-E2E-001').should('be.visible')
  })

  it('should show validation errors', () => {
    cy.contains('Nuevo Lote').click()

    // Intentar submit sin llenar campos requeridos
    cy.get('button[type="submit"]').click()

    // Verificar mensajes de error
    cy.contains('El nombre es requerido').should('be.visible')
    cy.contains('La variedad es requerida').should('be.visible')
  })
})
```

#### Ejecutar Tests E2E

```bash
# Ejecutar tests E2E
npm run test:e2e

# Ejecutar en modo interactivo
npm run cypress:open
```

---

### Resumen de Tests por Capa

| Capa | Archivo de Test | Framework | Comando |
|------|----------------|-----------|---------|
| **Modelo** | `test_lote_service.py` | pytest | `pytest fincas_app/tests/test_lote_service.py` |
| **Vista** | `test_lote_views.py` | pytest + DRF | `pytest fincas_app/tests/test_lote_views.py` |
| **API Service** | `lotesApi.test.js` | Vitest | `npm run test lotesApi.test.js` |
| **Composable** | `useLotes.test.js` | Vitest | `npm run test useLotes.test.js` |
| **Componente** | `LoteForm.test.js` | Vitest + Vue Test Utils | `npm run test LoteForm.test.js` |
| **E2E** | `lotes.cy.js` | Cypress | `npm run test:e2e` |

---

### Cobertura de Tests Recomendada

1. **Backend - Servicio (LoteService)**:
   - ✅ Creación exitosa
   - ✅ Validación de campos requeridos
   - ✅ Validación de área negativa
   - ✅ Validación de área que excede finca
   - ✅ Validación de identificador duplicado
   - ✅ Validación de permisos

2. **Backend - Vista (LoteListCreateView)**:
   - ✅ POST exitoso (201)
   - ✅ POST sin autenticación (401)
   - ✅ POST con datos inválidos (400)
   - ✅ POST sin permisos (403)

3. **Frontend - API Service**:
   - ✅ Llamada exitosa
   - ✅ Manejo de errores de red
   - ✅ Manejo de errores de validación

4. **Frontend - Composable**:
   - ✅ Creación exitosa
   - ✅ Validación de datos
   - ✅ Manejo de errores
   - ✅ Estados de loading

5. **Frontend - Componente**:
   - ✅ Renderizado del formulario
   - ✅ Submit exitoso
   - ✅ Manejo de errores
   - ✅ Estados de loading

6. **E2E**:
   - ✅ Flujo completo de creación
   - ✅ Validaciones en UI

---

## FIN DEL FLUJO Y TESTS

Este documento describe el flujo completo desde que el usuario llena el formulario hasta que el lote se guarda en la base de datos, incluyendo todas las capas, validaciones involucradas y cómo testear cada capa del sistema.

