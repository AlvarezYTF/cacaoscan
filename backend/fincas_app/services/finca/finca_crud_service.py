"""
CRUD service for finca management.
Handles create, read, update, and delete operations for fincas.
"""
import logging
from typing import Dict, Any
from django.db.models import Q
from django.contrib.auth.models import User

from api.services.base import BaseService, ServiceResult, ValidationServiceError
from api.utils.model_imports import get_models_safely
from .finca_validation_service import FincaValidationService

# Import models safely
models = get_models_safely({
    'Finca': 'fincas_app.models.Finca'
})
Finca = models['Finca']

logger = logging.getLogger("cacaoscan.services.fincas.crud")

# Error message constants
ERROR_FINCA_NOT_FOUND = "Finca no encontrada"


class FincaCRUDService(BaseService):
    """
    Service for handling finca CRUD operations.
    """
    
    def __init__(self):
        super().__init__()
        self.validation_service = FincaValidationService()
        from fincas_app.services.lote_service import LoteService
        self.lote_service = LoteService()
    
    def create_finca(self, finca_data: Dict[str, Any], user: User) -> ServiceResult:
        """
        Creates a new finca.
        
        Args:
            finca_data: Finca data
            user: User creating the finca
            
        Returns:
            ServiceResult with created finca data
        """
        try:
            # Validate using validation service
            validation_result = self.validation_service.validate_finca_data(finca_data, is_create=True)
            if not validation_result['valid']:
                return ServiceResult.validation_error(
                    validation_result['error'],
                    details=validation_result.get('details', {})
                )
            
            # Handle area_total and propietario for backward compatibility
            hectareas = finca_data.get('hectareas') or finca_data.get('area_total')
            agricultor = finca_data.get('propietario') or user
            
            # Validate hectareas/area_total
            if hectareas is None:
                return ServiceResult.validation_error(
                    "Las hectáreas (area_total) son requeridas",
                    details={"field": "hectareas"}
                )
            
            from decimal import Decimal
            try:
                hectareas = Decimal(str(hectareas))
                if hectareas < 0:
                    return ServiceResult.validation_error(
                        "Las hectáreas deben ser mayores o iguales a 0",
                        details={"field": "hectareas"}
                    )
            except (ValueError, TypeError):
                return ServiceResult.validation_error(
                    "Las hectáreas deben ser un número válido",
                    details={"field": "hectareas"}
                )
            
            # Create finca
            finca = Finca(
                nombre=finca_data['nombre'],
                ubicacion=finca_data.get('ubicacion', ''),
                municipio=finca_data.get('municipio', ''),
                departamento=finca_data.get('departamento', ''),
                hectareas=hectareas,
                agricultor=agricultor,
                activa=finca_data.get('activa', True),
                descripcion=finca_data.get('descripcion', ''),
                coordenadas_lat=finca_data.get('coordenadas_lat'),
                coordenadas_lng=finca_data.get('coordenadas_lng'),
                clima=finca_data.get('clima', ''),
                tipo_suelo=finca_data.get('tipo_suelo', ''),
                altitud=finca_data.get('altitud', 0),
                precipitacion_anual=finca_data.get('precipitacion_anual', 0),
                temperatura_promedio=finca_data.get('temperatura_promedio', 0)
            )
            
            finca.save()
            
            # Create audit log
            self.create_audit_log(
                user=user,
                action="finca_created",
                resource_type="finca",
                resource_id=finca.id,
                details={
                    'nombre': finca.nombre,
                    'hectareas': finca.hectareas,
                    'municipio': finca.municipio,
                    'departamento': finca.departamento
                }
            )
            
            self.log_info(f"Finca {finca.id} creada por usuario {user.username}")
            
            return ServiceResult.success(
                data=self._serialize_finca(finca),
                message="Finca creada exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error creando finca: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno creando finca", details={"original_error": str(e)})
            )
    
    def get_user_fincas(self, user: User, page: int = 1, page_size: int = 20, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Gets fincas for a user.
        
        Args:
            user: User
            page: Page number
            page_size: Page size
            filters: Additional filters
            
        Returns:
            ServiceResult with paginated fincas
        """
        try:
            # Build queryset
            if user.is_superuser or user.is_staff:
                queryset = Finca.objects.all().select_related('agricultor').prefetch_related('lotes')
            else:
                queryset = Finca.objects.filter(agricultor=user).select_related('agricultor').prefetch_related('lotes')
            
            # Apply filters
            if filters:
                if 'activa' in filters:
                    queryset = queryset.filter(activa=filters['activa'])
                if 'departamento' in filters:
                    queryset = queryset.filter(departamento__icontains=filters['departamento'])
                if 'municipio' in filters:
                    queryset = queryset.filter(municipio__icontains=filters['municipio'])
                if 'search' in filters:
                    search_term = filters['search']
                    queryset = queryset.filter(
                        Q(nombre__icontains=search_term) |
                        Q(ubicacion__icontains=search_term) |
                        Q(municipio__icontains=search_term) |
                        Q(departamento__icontains=search_term)
                    )
            
            queryset = queryset.order_by('-created_at')
            
            # Paginate results
            paginated_data = self.paginate_results(queryset, page, page_size)
            
            # Format data
            fincas = []
            for finca in paginated_data['results']:
                fincas.append(self._serialize_finca(finca))
            
            return ServiceResult.success(
                data={
                    'fincas': fincas,
                    'pagination': paginated_data['pagination']
                },
                message="Fincas obtenidas exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo fincas: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo fincas", details={"original_error": str(e)})
            )
    
    def get_finca_details(self, finca_id: int, user: User) -> ServiceResult:
        """
        Gets details of a specific finca.
        
        Args:
            finca_id: Finca ID
            user: User
            
        Returns:
            ServiceResult with finca details
        """
        try:
            try:
                if user.is_superuser or user.is_staff:
                    finca = Finca.objects.select_related('agricultor').prefetch_related('lotes').get(id=finca_id)
                else:
                    finca = Finca.objects.select_related('agricultor').prefetch_related('lotes').get(
                        id=finca_id, agricultor=user
                    )
            except Finca.DoesNotExist:
                return ServiceResult.not_found_error(ERROR_FINCA_NOT_FOUND)
            
            # Get lote statistics using LoteService
            lotes_stats_result = self.lote_service.get_finca_lotes_stats(finca_id, user)
            if lotes_stats_result.success:
                lotes_stats = lotes_stats_result.data['lotes_stats']
                lotes_data = lotes_stats_result.data['lotes_recientes']
            else:
                lotes_stats = {}
                lotes_data = []
            
            finca_data = self._serialize_finca(finca)
            finca_data.update({
                'lotes_stats': lotes_stats,
                'lotes_recientes': lotes_data,
                'agricultor': {
                    'id': finca.agricultor.id,
                    'username': finca.agricultor.username,
                    'email': finca.agricultor.email,
                    'first_name': finca.agricultor.first_name,
                    'last_name': finca.agricultor.last_name
                }
            })
            
            return ServiceResult.success(
                data=finca_data,
                message="Detalles de finca obtenidos exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo detalles: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo detalles", details={"original_error": str(e)})
            )
    
    def update_finca(self, finca_id: int, user: User, finca_data: Dict[str, Any]) -> ServiceResult:
        """
        Updates a finca.
        
        Args:
            finca_id: Finca ID
            user: User
            finca_data: Data to update
            
        Returns:
            ServiceResult with updated finca
        """
        try:
            try:
                if user.is_superuser or user.is_staff:
                    finca = Finca.objects.select_related('agricultor').get(id=finca_id)
                else:
                    finca = Finca.objects.select_related('agricultor').get(id=finca_id, agricultor=user)
            except Finca.DoesNotExist:
                return ServiceResult.not_found_error(ERROR_FINCA_NOT_FOUND)
            
            # Validate using validation service
            validation_result = self.validation_service.validate_finca_data(finca_data, is_create=False)
            if not validation_result['valid']:
                return ServiceResult.validation_error(
                    validation_result['error'],
                    details=validation_result.get('details', {})
                )
            
            # Handle area_total and propietario for backward compatibility
            if 'area_total' in finca_data:
                finca_data['hectareas'] = finca_data.pop('area_total')
            if 'propietario' in finca_data:
                finca_data['agricultor'] = finca_data.pop('propietario')
            
            # Save original data for log
            original_data = {
                'nombre': finca.nombre,
                'ubicacion': finca.ubicacion,
                'municipio': finca.municipio,
                'departamento': finca.departamento,
                'hectareas': finca.hectareas,
                'activa': finca.activa
            }
            
            # Update fields
            for field, value in finca_data.items():
                if hasattr(finca, field):
                    setattr(finca, field, value)
            
            finca.save()
            
            # Create audit log
            self.create_audit_log(
                user=user,
                action="finca_updated",
                resource_type="finca",
                resource_id=finca_id,
                details={
                    'original_data': original_data,
                    'updated_fields': list(finca_data.keys())
                }
            )
            
            self.log_info(f"Finca {finca_id} actualizada por usuario {user.username}")
            
            return ServiceResult.success(
                data=self._serialize_finca(finca),
                message="Finca actualizada exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error actualizando finca: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno actualizando finca", details={"original_error": str(e)})
            )
    
    def delete_finca(self, finca_id: int, user: User) -> ServiceResult:
        """
        Deletes a finca.
        
        Args:
            finca_id: Finca ID
            user: User
            
        Returns:
            ServiceResult with deletion result
        """
        try:
            try:
                if user.is_superuser or user.is_staff:
                    finca = Finca.objects.select_related('agricultor').get(id=finca_id)
                else:
                    finca = Finca.objects.select_related('agricultor').get(id=finca_id, agricultor=user)
            except Finca.DoesNotExist:
                return ServiceResult.not_found_error(ERROR_FINCA_NOT_FOUND)
            
            # Verify if it has associated lotes using LoteService
            lotes_count = self.lote_service.count_finca_lotes(finca_id)
            if lotes_count > 0:
                return ServiceResult.validation_error(
                    f"No se puede eliminar la finca porque tiene {lotes_count} lotes asociados",
                    details={"lotes_count": lotes_count}
                )
            
            # Create audit log before deleting
            self.create_audit_log(
                user=user,
                action="finca_deleted",
                resource_type="finca",
                resource_id=finca_id,
                details={
                    'nombre': finca.nombre,
                    'municipio': finca.municipio,
                    'departamento': finca.departamento,
                    'hectareas': finca.hectareas
                }
            )
            
            # Delete finca
            finca.delete()
            
            self.log_info(f"Finca {finca_id} eliminada por usuario {user.username}")
            
            return ServiceResult.success(
                message="Finca eliminada exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error eliminando finca: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno eliminando finca", details={"original_error": str(e)})
            )
    
    def _serialize_finca(self, finca: Finca) -> Dict[str, Any]:
        """
        Serializes a finca to dictionary.
        
        Args:
            finca: Finca instance
            
        Returns:
            Dictionary with finca data
        """
        return {
            'id': finca.id,
            'nombre': finca.nombre,
            'ubicacion': finca.ubicacion,
            'area_total': finca.hectareas,  # Alias for backward compatibility
            'propietario': finca.agricultor.id if finca.agricultor else None,  # Alias for backward compatibility
            'municipio': finca.municipio,
            'departamento': finca.departamento,
            'hectareas': finca.hectareas,
            'activa': finca.activa,
            'descripcion': finca.descripcion,
            'coordenadas_lat': float(finca.coordenadas_lat) if finca.coordenadas_lat else None,
            'coordenadas_lng': float(finca.coordenadas_lng) if finca.coordenadas_lng else None,
            'clima': finca.clima,
            'tipo_suelo': finca.tipo_suelo,
            'altitud': finca.altitud,
            'precipitacion_anual': float(finca.precipitacion_anual) if finca.precipitacion_anual else 0,
            'temperatura_promedio': float(finca.temperatura_promedio) if finca.temperatura_promedio else 0,
            'created_at': finca.created_at.isoformat(),
            'updated_at': finca.updated_at.isoformat(),
            'lotes_count': self.lote_service.count_finca_lotes(finca.id)
        }

