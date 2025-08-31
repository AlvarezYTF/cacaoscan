# Guía de Uso - Permisos y Seguridad CacaoScan

Esta guía práctica muestra cómo usar el sistema de permisos, decoradores y throttling en tus vistas y APIs.

## 🚀 Inicio Rápido

### 1. Usar Permisos en ViewSets

```python
from rest_framework.viewsets import ModelViewSet
from apps.users.permissions import CanUploadImages, IsAdminOrAnalyst

class MiViewSet(ModelViewSet):
    permission_classes = [CanUploadImages]
    
    def get_permissions(self):
        """Permisos específicos por acción."""
        if self.action == 'create':
            self.permission_classes = [CanUploadImages]
        elif self.action == 'list':
            self.permission_classes = [IsAdminOrAnalyst]
        
        return [permission() for permission in self.permission_classes]
```

### 2. Usar Decoradores en Vistas Función

```python
from apps.users.decorators import require_role, require_verified_user, log_api_access

@require_role(['admin', 'analyst'])
@log_api_access
def admin_stats(request):
    # Solo administradores y analistas
    return JsonResponse({'stats': 'data'})

@require_verified_user
@validate_file_upload(['jpg', 'png'])
def upload_image(request):
    # Solo usuarios verificados, validar archivos
    return JsonResponse({'success': True})
```

### 3. Aplicar Throttling

```python
from rest_framework.decorators import throttle_classes
from apps.users.throttling import PredictionThrottle, LoginThrottle

@throttle_classes([PredictionThrottle])
def predict_view(request):
    # Límites específicos para predicciones
    pass

@throttle_classes([LoginThrottle])
def login_view(request):
    # Límites para intentos de login
    pass
```

## 📋 Ejemplos por Caso de Uso

### Caso 1: API de Predicción

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.users.permissions import CanUploadImages
from apps.users.decorators import validate_prediction_data, log_api_access
from apps.users.throttling import PredictionThrottle

class PredictionAPIView(APIView):
    permission_classes = [CanUploadImages]
    throttle_classes = [PredictionThrottle]
    
    @log_api_access
    @validate_prediction_data
    def post(self, request):
        # Lógica de predicción aquí
        return Response({'prediction': 'result'})
```

### Caso 2: Dashboard Administrativo

```python
from rest_framework.decorators import api_view, permission_classes
from apps.users.permissions import IsAdminUser
from apps.users.decorators import admin_management_endpoint

@api_view(['GET'])
@admin_management_endpoint
def admin_dashboard(request):
    # Solo administradores, con logging automático
    return Response({'dashboard': 'data'})
```

### Caso 3: Gestión de Perfil

```python
from rest_framework.viewsets import ModelViewSet
from apps.users.permissions import IsSameUserOrAdmin
from apps.users.models import User

class UserProfileViewSet(ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsSameUserOrAdmin]
    
    def get_queryset(self):
        """Filtrar según permisos del usuario."""
        if self.request.user.role == 'admin':
            return self.queryset
        else:
            return self.queryset.filter(id=self.request.user.id)
```

### Caso 4: Upload de Archivos

```python
from apps.users.decorators import farmer_upload_endpoint

@farmer_upload_endpoint  # Combina múltiples validaciones
def upload_cacao_image(request):
    # Automáticamente valida:
    # - Usuario autenticado
    # - Rol farmer o admin
    # - Usuario verificado
    # - Archivo válido (jpg, png)
    # - Logging de acceso
    
    image = request.FILES['image']
    # Procesar imagen...
    return JsonResponse({'uploaded': True})
```

## 🎯 Permisos por Funcionalidad

### Subida de Imágenes
```python
permission_classes = [CanUploadImages]
# Permite: usuarios verificados con rol farmer/admin
```

### Ver Predicciones
```python
permission_classes = [CanViewPredictions]
# Farmers: solo sus predicciones
# Analysts/Admins: todas las predicciones
```

### Gestionar Dataset
```python
permission_classes = [CanManageDataset]
# Solo analysts y admins
```

### Entrenar Modelos
```python
permission_classes = [CanTrainModels]
# Solo administradores
```

### Administrar Usuarios
```python
permission_classes = [IsAdminUser]
# Solo administradores
```

## 🔄 Throttling por Endpoint

### Configuración Automática

Los siguientes endpoints tienen throttling automático configurado:

```python
# En tu vista, simplemente usa:
throttle_classes = [PredictionThrottle]  # Para predicciones ML
throttle_classes = [UploadThrottle]      # Para uploads
throttle_classes = [LoginThrottle]       # Para login
throttle_classes = [BurstThrottle]       # Para ráfagas
```

### Límites por Rol

El sistema ajusta automáticamente según el rol:

```python
# Agricultores: 30 predicciones/hora
# Analistas: 60 predicciones/hora  
# Administradores: 120 predicciones/hora

class MyAPIView(APIView):
    throttle_classes = [PredictionThrottle]
    # Los límites se aplican automáticamente
```

## 🛠️ Decoradores Útiles

### Validación de Roles
```python
@require_role(['admin'])           # Solo administradores
@require_role(['farmer', 'admin']) # Agricultores y administradores
@require_role(['analyst'])         # Solo analistas
```

### Validación de Estado
```python
@require_verified_user    # Solo usuarios verificados
@log_api_access          # Logging automático
```

### Validación de Archivos
```python
@validate_file_upload(['jpg', 'png'], max_size_mb=5)
# Valida extensión y tamaño

@validate_prediction_data
# Validación específica para predicciones
```

### Validación de Propiedad
```python
def get_image(image_id):
    return CacaoImage.objects.get(id=image_id)

@require_ownership(get_image)
def delete_image(request, image_id):
    # Solo el propietario o admin puede eliminar
    pass
```

### Decoradores Combinados
```python
@farmer_upload_endpoint     # farmer + verificado + archivo válido + logging
@admin_management_endpoint  # admin + logging
@analyst_readonly_endpoint  # analyst/admin + logging
```

## 🔍 Filtrado Automático por Rol

### En ViewSets
```python
def get_queryset(self):
    """El sistema filtra automáticamente según rol."""
    queryset = super().get_queryset()
    
    if self.request.user.role == 'farmer':
        # Agricultores ven solo sus datos
        return queryset.filter(uploaded_by=self.request.user)
    elif self.request.user.role in ['admin', 'analyst']:
        # Admin/analistas ven todo
        return queryset
    else:
        # Por defecto, solo datos propios
        return queryset.filter(uploaded_by=self.request.user)
```

## ⚡ Optimización de Performance

### Cache para Permisos
```python
# Los permisos usan cache automáticamente
# Para operaciones costosas, cachear manualmente:

from django.core.cache import cache

def expensive_permission_check(user):
    cache_key = f"perm_check:{user.id}"
    result = cache.get(cache_key)
    
    if result is None:
        result = perform_expensive_check(user)
        cache.set(cache_key, result, 300)  # 5 minutos
    
    return result
```

### Prefetch para Permisos
```python
# En tus querysets, incluir relaciones necesarias:
queryset = CacaoImage.objects.select_related('uploaded_by').prefetch_related('uploaded_by__profile')
```

## 🚨 Manejo de Errores

### Errores de Permisos
```python
from rest_framework.exceptions import PermissionDenied

def my_view(request):
    if not request.user.has_permission('special'):
        raise PermissionDenied("No tienes permisos especiales")
```

### Errores de Throttling
```python
from rest_framework.exceptions import Throttled

# Los throttles lanzan automáticamente Throttled
# Puedes personalizar el mensaje:

class CustomThrottle(UserRateThrottle):
    def throttle_failure(self):
        raise Throttled(detail="Límite personalizado excedido")
```

## 📊 Monitoreo y Debugging

### Logs de Permisos
```python
# Los logs se generan automáticamente en:
# - backend/logs/django.log (general)
# - backend/logs/ml.log (ML específico)

# Para debugging, usar:
import logging
logger = logging.getLogger(__name__)

logger.info(f"User {request.user.email} accessing {request.path}")
logger.warning(f"Permission denied for {request.user.email}")
```

### Debug de Throttling
```python
# Para ver límites actuales:
from django.core.cache import cache

def check_rate_limit(user):
    cache_key = f"throttle_user_{user.id}"
    current_count = cache.get(cache_key, 0)
    print(f"Usuario {user.email}: {current_count} requests en ventana actual")
```

## 🔧 Configuración Avanzada

### Personalizar Límites
```python
# En settings.py, ajustar:
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'farmer': '60/hour',      # Cambiar límite de agricultores
        'prediction': '50/hour',  # Cambiar límite de predicciones
    }
}
```

### Middleware Personalizado
```python
# Para casos especiales, crear middleware propio:
class CustomSecurityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Tu lógica personalizada aquí
        pass
```

## ✅ Checklist de Implementación

Al crear una nueva vista o endpoint:

- [ ] ✅ Definir `permission_classes` apropiadas
- [ ] ✅ Configurar `throttle_classes` si es necesario
- [ ] ✅ Usar decoradores para validaciones adicionales
- [ ] ✅ Implementar `get_queryset()` con filtros por rol
- [ ] ✅ Agregar logging para operaciones sensibles
- [ ] ✅ Validar archivos si hay uploads
- [ ] ✅ Manejar errores de permisos apropiadamente
- [ ] ✅ Documentar en Swagger con ejemplos
- [ ] ✅ Probar con diferentes roles
- [ ] ✅ Verificar logs de seguridad

## 📚 Referencias Útiles

- **Permisos DRF**: https://www.django-rest-framework.org/api-guide/permissions/
- **Throttling DRF**: https://www.django-rest-framework.org/api-guide/throttling/
- **Django Security**: https://docs.djangoproject.com/en/4.2/topics/security/
- **Middleware Django**: https://docs.djangoproject.com/en/4.2/topics/http/middleware/

---

**💡 Tip**: Para casos complejos, combina múltiples decoradores y permisos. El sistema está diseñado para ser flexible y extensible.
