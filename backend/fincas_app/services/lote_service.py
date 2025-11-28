"""
Lote service for CacaoScan.
Handles all lote (plot) management operations.
"""
import logging
from typing import Dict, Any
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta

from api.services.base import BaseService, ServiceResult, ValidationServiceError
from api.utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'Finca': 'fincas_app.models.Finca',
    'Lote': 'fincas_app.models.Lote'
})
Finca = models['Finca']
Lote = models['Lote']

from django.contrib.auth.models import User

logger = logging.getLogger("cacaoscan.services.lotes")

# Error message constants
ERROR_FINCA_NOT_FOUND = "Finca not found"
ERROR_LOTE_NOT_FOUND = "Lote not found"


class LoteService(BaseService):
    """
    Service for handling lote (plot) management.
    
    Responsibilities:
    - Creating, updating, and deleting lotes
    - Retrieving lote information
    - Calculating lote statistics
    - Managing lote-finca relationships
    """
    
    def __init__(self):
        super().__init__()
    
    def create_lote(self, lote_data: Dict[str, Any], user: User) -> ServiceResult:
        """
        Creates a new lote.
        
        Args:
            lote_data: Lote data
            user: User creating the lote
            
        Returns:
            ServiceResult with created lote data
        """
        try:
            # Validate required fields
            required_fields = ['finca', 'identificador', 'variedad', 'fecha_plantacion', 'hectareas']
            self.validate_required_fields(lote_data, required_fields)
            
            # Validate that the finca belongs to the user (optimized)
            try:
                if user.is_superuser or user.is_staff:
                    finca = Finca.objects.select_related('agricultor').get(id=lote_data['finca'])
                else:
                    finca = Finca.objects.select_related('agricultor').get(id=lote_data['finca'], agricultor=user)
            except Finca.DoesNotExist:
                return ServiceResult.not_found_error(ERROR_FINCA_NOT_FOUND)
            
            # Validate unique identifier in the finca
            if Lote.objects.filter(finca=finca, identificador=lote_data['identificador']).exists():
                return ServiceResult.validation_error(
                    "A lote with this identifier already exists in the finca",
                    details={"field": "identificador"}
                )
            
            # Validate values
            validations = {
                'identificador': {'min_length': 1, 'max_length': 50},
                'variedad': {'min_length': 2, 'max_length': 100},
                'hectareas': {'type': (int, float), 'min': 0.01}
            }
            self.validate_field_values(lote_data, validations)
            
            # Create lote
            lote = Lote(
                finca=finca,
                identificador=lote_data['identificador'],
                variedad=lote_data['variedad'],
                fecha_plantacion=lote_data['fecha_plantacion'],
                hectareas=lote_data['hectareas'],
                estado=lote_data.get('estado', 'activo'),
                descripcion=lote_data.get('descripcion', ''),
                coordenadas=lote_data.get('coordenadas', {}),
                tipo_suelo=lote_data.get('tipo_suelo', ''),
                altitud=lote_data.get('altitud', 0),
                precipitacion_anual=lote_data.get('precipitacion_anual', 0),
                temperatura_promedio=lote_data.get('temperatura_promedio', 0),
                rendimiento_esperado=lote_data.get('rendimiento_esperado', 0),
                fecha_cosecha=lote_data.get('fecha_cosecha'),
                rendimiento_real=lote_data.get('rendimiento_real', 0),
                calidad_cacao=lote_data.get('calidad_cacao', ''),
                notas=lote_data.get('notas', '')
            )
            
            lote.save()
            
            # Create audit log
            self.create_audit_log(
                user=user,
                action="lote_created",
                resource_type="lote",
                resource_id=lote.id,
                details={
                    'identificador': lote.identificador,
                    'variedad': lote.variedad,
                    'hectareas': lote.hectareas,
                    'finca_id': finca.id,
                    'finca_nombre': finca.nombre
                }
            )
            
            self.log_info(f"Lote {lote.id} created by user {user.username}")
            
            return ServiceResult.success(
                data=self._serialize_lote(lote),
                message="Lote created successfully"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error creating lote: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error creating lote", details={"original_error": str(e)})
            )
    
    def get_finca_lotes(self, finca_id: int, user: User, page: int = 1, page_size: int = 20, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Gets lotes for a specific finca.
        
        Args:
            finca_id: Finca ID
            user: User
            page: Page number
            page_size: Page size
            filters: Additional filters
            
        Returns:
            ServiceResult with paginated lotes
        """
        try:
            # Verify that the finca belongs to the user
            try:
                if user.is_superuser or user.is_staff:
                    finca = Finca.objects.select_related('agricultor').get(id=finca_id)
                else:
                    finca = Finca.objects.select_related('agricultor').get(id=finca_id, agricultor=user)
            except Finca.DoesNotExist:
                return ServiceResult.not_found_error(ERROR_FINCA_NOT_FOUND)
            
            # Build optimized queryset
            queryset = Lote.objects.filter(finca=finca).select_related(
                'finca',
                'finca__agricultor'
            ).prefetch_related('cacao_images').order_by('-created_at')
            
            # Apply filters
            if filters:
                if 'estado' in filters:
                    queryset = queryset.filter(estado=filters['estado'])
                if 'variedad' in filters:
                    queryset = queryset.filter(variedad__icontains=filters['variedad'])
                if 'search' in filters:
                    search_term = filters['search']
                    queryset = queryset.filter(
                        Q(identificador__icontains=search_term) |
                        Q(variedad__icontains=search_term) |
                        Q(descripcion__icontains=search_term)
                    )
            
            # Paginate results
            paginated_data = self.paginate_results(queryset, page, page_size)
            
            # Format data
            lotes = []
            for lote in paginated_data['results']:
                lotes.append(self._serialize_lote(lote))
            
            return ServiceResult.success(
                data={
                    'lotes': lotes,
                    'pagination': paginated_data['pagination'],
                    'finca': {
                        'id': finca.id,
                        'nombre': finca.nombre,
                        'municipio': finca.municipio,
                        'departamento': finca.departamento
                    }
                },
                message="Lotes obtained successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error getting lotes: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error getting lotes", details={"original_error": str(e)})
            )
    
    def get_lote_details(self, lote_id: int, user: User) -> ServiceResult:
        """
        Gets details of a specific lote.
        
        Args:
            lote_id: Lote ID
            user: User
            
        Returns:
            ServiceResult with lote details
        """
        try:
            try:
                if user.is_superuser or user.is_staff:
                    lote = Lote.objects.select_related('finca', 'finca__agricultor').get(id=lote_id)
                else:
                    lote = Lote.objects.select_related('finca', 'finca__agricultor').get(
                        id=lote_id, finca__agricultor=user
                    )
            except Lote.DoesNotExist:
                return ServiceResult.not_found_error(ERROR_LOTE_NOT_FOUND)
            
            lote_data = self._serialize_lote(lote)
            lote_data.update({
                'finca': {
                    'id': lote.finca.id,
                    'nombre': lote.finca.nombre,
                    'municipio': lote.finca.municipio,
                    'departamento': lote.finca.departamento,
                    'hectareas': lote.finca.hectareas
                },
                'agricultor': {
                    'id': lote.finca.agricultor.id,
                    'username': lote.finca.agricultor.username,
                    'email': lote.finca.agricultor.email,
                    'first_name': lote.finca.agricultor.first_name,
                    'last_name': lote.finca.agricultor.last_name
                }
            })
            
            return ServiceResult.success(
                data=lote_data,
                message="Lote details obtained successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error getting details: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error getting details", details={"original_error": str(e)})
            )
    
    def update_lote(self, lote_id: int, user: User, lote_data: Dict[str, Any]) -> ServiceResult:
        """
        Updates a lote.
        
        Args:
            lote_id: Lote ID
            user: User
            lote_data: Data to update
            
        Returns:
            ServiceResult with updated lote
        """
        try:
            try:
                if user.is_superuser or user.is_staff:
                    lote = Lote.objects.select_related('finca', 'finca__agricultor').get(id=lote_id)
                else:
                    lote = Lote.objects.select_related('finca', 'finca__agricultor').get(id=lote_id, finca__agricultor=user)
            except Lote.DoesNotExist:
                return ServiceResult.not_found_error(ERROR_LOTE_NOT_FOUND)
            
            # Validate unique identifier if changing
            if 'identificador' in lote_data and lote_data['identificador'] != lote.identificador:
                if Lote.objects.filter(finca=lote.finca, identificador=lote_data['identificador']).exists():
                    return ServiceResult.validation_error(
                        "A lote with this identifier already exists in the finca",
                        details={"field": "identificador"}
                    )
            
            # Save original data for log
            original_data = {
                'identificador': lote.identificador,
                'variedad': lote.variedad,
                'hectareas': lote.hectareas,
                'estado': lote.estado
            }
            
            # Update fields
            for field, value in lote_data.items():
                if hasattr(lote, field):
                    setattr(lote, field, value)
            
            lote.save()
            
            # Create audit log
            self.create_audit_log(
                user=user,
                action="lote_updated",
                resource_type="lote",
                resource_id=lote_id,
                details={
                    'original_data': original_data,
                    'updated_fields': list(lote_data.keys()),
                    'finca_id': lote.finca.id
                }
            )
            
            self.log_info(f"Lote {lote_id} updated by user {user.username}")
            
            return ServiceResult.success(
                data=self._serialize_lote(lote),
                message="Lote updated successfully"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error updating lote: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error updating lote", details={"original_error": str(e)})
            )
    
    def delete_lote(self, lote_id: int, user: User) -> ServiceResult:
        """
        Deletes a lote.
        
        Args:
            lote_id: Lote ID
            user: User
            
        Returns:
            ServiceResult with deletion result
        """
        try:
            try:
                if user.is_superuser or user.is_staff:
                    lote = Lote.objects.select_related('finca', 'finca__agricultor').get(id=lote_id)
                else:
                    lote = Lote.objects.select_related('finca', 'finca__agricultor').get(id=lote_id, finca__agricultor=user)
            except Lote.DoesNotExist:
                return ServiceResult.not_found_error(ERROR_LOTE_NOT_FOUND)
            
            # Create audit log before deleting
            self.create_audit_log(
                user=user,
                action="lote_deleted",
                resource_type="lote",
                resource_id=lote_id,
                details={
                    'identificador': lote.identificador,
                    'variedad': lote.variedad,
                    'hectareas': lote.hectareas,
                    'finca_id': lote.finca.id,
                    'finca_nombre': lote.finca.nombre
                }
            )
            
            # Delete lote
            lote.delete()
            
            self.log_info(f"Lote {lote_id} deleted by user {user.username}")
            
            return ServiceResult.success(
                message="Lote deleted successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error deleting lote: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error deleting lote", details={"original_error": str(e)})
            )
    
    def get_lote_statistics(self, user: User, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Gets lote statistics for a user.
        
        Args:
            user: User
            filters: Additional filters
            
        Returns:
            ServiceResult with statistics
        """
        try:
            # Build base queryset (optimized)
            if user.is_superuser or user.is_staff:
                queryset = Lote.objects.all().select_related('finca', 'finca__agricultor')
            else:
                queryset = Lote.objects.filter(finca__agricultor=user).select_related('finca', 'finca__agricultor')
            
            # Apply filters
            if filters:
                if 'finca_id' in filters:
                    queryset = queryset.filter(finca_id=filters['finca_id'])
                if 'estado' in filters:
                    queryset = queryset.filter(estado=filters['estado'])
                if 'variedad' in filters:
                    queryset = queryset.filter(variedad=filters['variedad'])
            
            # Calculate statistics
            stats = {
                'total_lotes': queryset.count(),
                'lotes_activos': queryset.filter(estado='activo').count(),
                'lotes_cosechados': queryset.filter(estado='cosechado').count(),
                'lotes_inactivos': queryset.filter(estado='inactivo').count(),
                'total_hectareas': queryset.aggregate(total=Sum('hectareas'))['total'] or 0,
                'promedio_hectareas': queryset.aggregate(avg=Avg('hectareas'))['avg'] or 0,
                'variedades': dict(queryset.values('variedad').annotate(count=Count('id')).values_list('variedad', 'count')),
                'estados': dict(queryset.values('estado').annotate(count=Count('id')).values_list('estado', 'count')),
                'promedio_edad': queryset.aggregate(avg=Avg('edad_plantas'))['avg'] or 0,
                'rendimiento_promedio': queryset.aggregate(avg=Avg('rendimiento_real'))['avg'] or 0,
                'recent_lotes': queryset.filter(created_at__gte=timezone.now() - timedelta(days=30)).count()
            }
            
            return ServiceResult.success(
                data=stats,
                message="Statistics obtained successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error getting statistics: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error getting statistics", details={"original_error": str(e)})
            )
    
    def get_finca_lotes_stats(self, finca_id: int, user: User) -> ServiceResult:
        """
        Gets lote statistics for a specific finca.
        
        Args:
            finca_id: Finca ID
            user: User
            
        Returns:
            ServiceResult with lote statistics for the finca
        """
        try:
            # Verify that the finca belongs to the user
            try:
                if user.is_superuser or user.is_staff:
                    finca = Finca.objects.select_related('agricultor').get(id=finca_id)
                else:
                    finca = Finca.objects.select_related('agricultor').get(id=finca_id, agricultor=user)
            except Finca.DoesNotExist:
                return ServiceResult.not_found_error(ERROR_FINCA_NOT_FOUND)
            
            # Get lote statistics
            lotes_stats = finca.lotes.aggregate(
                total_lotes=Count('id'),
                hectareas_cultivadas=Sum('hectareas'),
                promedio_edad=Avg('edad_plantas')
            )
            
            # Get recent lotes
            lotes_recientes = finca.lotes.order_by('-created_at')[:5]
            lotes_data = []
            
            for lote in lotes_recientes:
                lotes_data.append({
                    'id': lote.id,
                    'identificador': lote.identificador,
                    'variedad': lote.variedad,
                    'hectareas': lote.hectareas,
                    'fecha_plantacion': lote.fecha_plantacion.isoformat(),
                    'edad_plantas': lote.edad_plantas,
                    'estado': lote.estado
                })
            
            return ServiceResult.success(
                data={
                    'lotes_stats': lotes_stats,
                    'lotes_recientes': lotes_data
                },
                message="Finca lote statistics obtained successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error getting finca lote statistics: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error getting finca lote statistics", details={"original_error": str(e)})
            )
    
    def count_finca_lotes(self, finca_id: int) -> int:
        """
        Counts lotes for a finca.
        
        Args:
            finca_id: Finca ID
            
        Returns:
            Number of lotes
        """
        try:
            return Lote.objects.filter(finca_id=finca_id).count()
        except Exception:
            return 0
    
    def _serialize_lote(self, lote: Lote) -> Dict[str, Any]:
        """
        Serializes a lote to dictionary.
        
        Args:
            lote: Lote instance
            
        Returns:
            Dictionary with lote data
        """
        return {
            'id': lote.id,
            'identificador': lote.identificador,
            'variedad': lote.variedad,
            'fecha_plantacion': lote.fecha_plantacion.isoformat(),
            'hectareas': lote.hectareas,
            'estado': lote.estado,
            'edad_plantas': lote.edad_plantas,
            'descripcion': lote.descripcion,
            'coordenadas': lote.coordenadas,
            'tipo_suelo': lote.tipo_suelo,
            'altitud': lote.altitud,
            'precipitacion_anual': lote.precipitacion_anual,
            'temperatura_promedio': lote.temperatura_promedio,
            'rendimiento_esperado': lote.rendimiento_esperado,
            'fecha_cosecha': lote.fecha_cosecha.isoformat() if lote.fecha_cosecha else None,
            'rendimiento_real': lote.rendimiento_real,
            'calidad_cacao': lote.calidad_cacao,
            'notas': lote.notas,
            'created_at': lote.created_at.isoformat(),
            'updated_at': lote.updated_at.isoformat(),
            'finca_id': lote.finca.id,
            'finca_nombre': lote.finca.nombre
        }

