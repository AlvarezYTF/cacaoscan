"""
Base classes para servicios en CacaoScan.
"""
import logging
from typing import Dict, Any, Optional, List, Union
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.contrib.auth.models import User
from django.utils import timezone

logger = logging.getLogger("cacaoscan.services")


class ServiceError(Exception):
    """Excepción base para errores de servicios."""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationServiceError(ServiceError):
    """Error de validación en servicios."""
    pass


class PermissionServiceError(ServiceError):
    """Error de permisos en servicios."""
    pass


class NotFoundServiceError(ServiceError):
    """Error de recurso no encontrado en servicios."""
    pass


class BaseService:
    """
    Clase base para todos los servicios.
    Proporciona funcionalidades comunes como logging, manejo de errores y transacciones.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"cacaoscan.services.{self.__class__.__name__}")
    
    def log_info(self, message: str, **kwargs):
        """Log de información."""
        self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log de advertencia."""
        self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log de error."""
        self.logger.error(message, extra=kwargs)
    
    def validate_user_permission(self, user: User, permission: str, resource: Any = None) -> bool:
        """
        Valida permisos de usuario.
        
        Args:
            user: Usuario a validar
            permission: Permiso requerido
            resource: Recurso específico (opcional)
            
        Returns:
            True si tiene permisos, False en caso contrario
        """
        if user.is_superuser or user.is_staff:
            return True
        
        # Implementar lógica específica de permisos según el servicio
        return False
    
    def check_user_permission(self, user: User, permission: str, resource: Any = None):
        """
        Verifica permisos de usuario y lanza excepción si no los tiene.
        
        Args:
            user: Usuario a validar
            permission: Permiso requerido
            resource: Recurso específico (opcional)
            
        Raises:
            PermissionServiceError: Si no tiene permisos
        """
        if not self.validate_user_permission(user, permission, resource):
            raise PermissionServiceError(
                f"Usuario {user.username} no tiene permisos para {permission}",
                error_code="permission_denied"
            )
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]):
        """
        Valida que los campos requeridos estén presentes.
        
        Args:
            data: Datos a validar
            required_fields: Lista de campos requeridos
            
        Raises:
            ValidationServiceError: Si faltan campos requeridos
        """
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            raise ValidationServiceError(
                f"Campos requeridos faltantes: {', '.join(missing_fields)}",
                error_code="missing_required_fields",
                details={"missing_fields": missing_fields}
            )
    
    def validate_field_values(self, data: Dict[str, Any], validations: Dict[str, Any]):
        """
        Valida valores de campos específicos.
        
        Args:
            data: Datos a validar
            validations: Diccionario con validaciones por campo
            
        Raises:
            ValidationServiceError: Si las validaciones fallan
        """
        for field, validation in validations.items():
            if field in data:
                value = data[field]
                
                # Validación de tipo
                if 'type' in validation:
                    expected_type = validation['type']
                    if not isinstance(value, expected_type):
                        raise ValidationServiceError(
                            f"Campo '{field}' debe ser de tipo {expected_type.__name__}",
                            error_code="invalid_field_type",
                            details={"field": field, "expected_type": expected_type.__name__, "actual_type": type(value).__name__}
                        )
                
                # Validación de rango
                if 'min' in validation and value < validation['min']:
                    raise ValidationServiceError(
                        f"Campo '{field}' debe ser mayor o igual a {validation['min']}",
                        error_code="field_value_too_small",
                        details={"field": field, "min": validation['min'], "actual": value}
                    )
                
                if 'max' in validation and value > validation['max']:
                    raise ValidationServiceError(
                        f"Campo '{field}' debe ser menor o igual a {validation['max']}",
                        error_code="field_value_too_large",
                        details={"field": field, "max": validation['max'], "actual": value}
                    )
                
                # Validación de longitud
                if 'min_length' in validation and len(str(value)) < validation['min_length']:
                    raise ValidationServiceError(
                        f"Campo '{field}' debe tener al menos {validation['min_length']} caracteres",
                        error_code="field_too_short",
                        details={"field": field, "min_length": validation['min_length'], "actual_length": len(str(value))}
                    )
                
                if 'max_length' in validation and len(str(value)) > validation['max_length']:
                    raise ValidationServiceError(
                        f"Campo '{field}' debe tener máximo {validation['max_length']} caracteres",
                        error_code="field_too_long",
                        details={"field": field, "max_length": validation['max_length'], "actual_length": len(str(value))}
                    )
    
    def execute_with_transaction(self, func, *args, **kwargs):
        """
        Ejecuta una función dentro de una transacción de base de datos.
        
        Args:
            func: Función a ejecutar
            *args: Argumentos de la función
            **kwargs: Argumentos con nombre de la función
            
        Returns:
            Resultado de la función
            
        Raises:
            ServiceError: Si ocurre un error durante la transacción
        """
        try:
            with transaction.atomic():
                return func(*args, **kwargs)
        except Exception as e:
            self.log_error(f"Error en transacción: {str(e)}")
            raise ServiceError(
                f"Error en operación de base de datos: {str(e)}",
                error_code="transaction_error",
                details={"original_error": str(e)}
            )
    
    def paginate_results(self, queryset, page: int = 1, page_size: int = 20):
        """
        Pagina resultados de un queryset.
        
        Args:
            queryset: QuerySet a paginar
            page: Número de página (empezando en 1)
            page_size: Tamaño de página
            
        Returns:
            Diccionario con datos paginados
        """
        from django.core.paginator import Paginator
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)
        
        return {
            'results': list(page_obj.object_list),
            'pagination': {
                'page': page_obj.number,
                'pages': paginator.num_pages,
                'per_page': page_size,
                'total': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None
            }
        }
    
    def create_audit_log(self, user: User, action: str, resource_type: str, resource_id: Any = None, details: Dict[str, Any] = None):
        """
        Crea un log de auditoría.
        
        Args:
            user: Usuario que realiza la acción
            action: Acción realizada
            resource_type: Tipo de recurso
            resource_id: ID del recurso (opcional)
            details: Detalles adicionales (opcional)
        """
        try:
            try:
                from audit.models import ActivityLog
            except ImportError:
                ActivityLog = None
            
            if ActivityLog is None:
                self.log_debug("Servicio de auditoría no disponible; se omite creación de log")
                return
            
            ActivityLog.objects.create(
                user=user,
                action=action,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else None,
                details=details or {},
                timestamp=timezone.now()
            )
        except Exception as e:
            self.log_warning(f"Error creando log de auditoría: {str(e)}")


class ServiceResult:
    """
    Clase para encapsular resultados de servicios.
    """
    
    def __init__(self, success: bool = True, data: Any = None, message: str = None, error: ServiceError = None):
        self.success = success
        self.data = data
        self.message = message
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        result = {
            'success': self.success,
            'data': self.data,
            'message': self.message
        }
        
        if self.error:
            result['error'] = {
                'message': self.error.message,
                'code': self.error.error_code,
                'details': self.error.details
            }
        
        return result
    
    @classmethod
    def success(cls, data: Any = None, message: str = None):
        """Crea un resultado exitoso."""
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def error(cls, error: ServiceError, message: str = None):
        """Crea un resultado de error."""
        return cls(success=False, error=error, message=message)
    
    @classmethod
    def validation_error(cls, message: str, details: Dict[str, Any] = None):
        """Crea un resultado de error de validación."""
        error = ValidationServiceError(message, details=details)
        return cls(success=False, error=error)
    
    @classmethod
    def permission_error(cls, message: str):
        """Crea un resultado de error de permisos."""
        error = PermissionServiceError(message)
        return cls(success=False, error=error)
    
    @classmethod
    def not_found_error(cls, message: str):
        """Crea un resultado de error de recurso no encontrado."""
        error = NotFoundServiceError(message)
        return cls(success=False, error=error)
