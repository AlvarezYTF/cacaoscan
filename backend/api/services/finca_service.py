"""
Servicio de gestión de fincas y lotes para CacaoScan.
"""
import logging
from typing import Dict, Any, Optional, List
from django.db.models import Q, Count, Avg, Sum, Prefetch
from django.utils import timezone
from datetime import timedelta

from .base import BaseService, ServiceResult, ValidationServiceError, PermissionServiceError, NotFoundServiceError
try:
    from fincas_app.models import Finca, Lote
except ImportError:
    Finca = None
    Lote = None

from django.contrib.auth.models import User

logger = logging.getLogger("cacaoscan.services.fincas")


class FincaService(BaseService):
    """
    Servicio para manejar gestión de fincas.
    """
    
    def __init__(self):
        super().__init__()
    
    def create_finca(self, finca_data: Dict[str, Any], user: User) -> ServiceResult:
        """
        Crea una nueva finca.
        
        Args:
            finca_data: Datos de la finca
            user: Usuario que crea la finca
            
        Returns:
            ServiceResult con datos de la finca creada
        """
        try:
            # Validar campos requeridos
            required_fields = ['nombre', 'ubicacion', 'municipio', 'departamento', 'hectareas']
            self.validate_required_fields(finca_data, required_fields)
            
            # Validar valores
            validations = {
                'nombre': {'min_length': 2, 'max_length': 200},
                'ubicacion': {'min_length': 5, 'max_length': 300},
                'municipio': {'min_length': 2, 'max_length': 100},
                'departamento': {'min_length': 2, 'max_length': 100},
                'hectareas': {'type': (int, float), 'min': 0.01}
            }
            self.validate_field_values(finca_data, validations)
            
            # Crear finca
            finca = Finca(
                nombre=finca_data['nombre'],
                ubicacion=finca_data['ubicacion'],
                municipio=finca_data['municipio'],
                departamento=finca_data['departamento'],
                hectareas=finca_data['hectareas'],
                agricultor=user,
                activa=finca_data.get('activa', True),
                descripcion=finca_data.get('descripcion', ''),
                coordenadas=finca_data.get('coordenadas', {}),
                clima=finca_data.get('clima', ''),
                tipo_suelo=finca_data.get('tipo_suelo', ''),
                altitud=finca_data.get('altitud', 0),
                precipitacion_anual=finca_data.get('precipitacion_anual', 0),
                temperatura_promedio=finca_data.get('temperatura_promedio', 0)
            )
            
            finca.save()
            
            # Crear log de auditoría
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
        Obtiene fincas de un usuario.
        
        Args:
            user: Usuario
            page: Número de página
            page_size: Tamaño de página
            filters: Filtros adicionales
            
        Returns:
            ServiceResult con fincas paginadas
        """
        try:
            # Construir queryset
            if user.is_superuser or user.is_staff:
                queryset = Finca.objects.all().select_related('agricultor').prefetch_related('lotes')
            else:
                queryset = Finca.objects.filter(agricultor=user).select_related('agricultor').prefetch_related('lotes')
            
            # Aplicar filtros
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
            
            # Paginar resultados
            paginated_data = self.paginate_results(queryset, page, page_size)
            
            # Formatear datos
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
        Obtiene detalles de una finca específica.
        
        Args:
            finca_id: ID de la finca
            user: Usuario
            
        Returns:
            ServiceResult con detalles de la finca
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
                return ServiceResult.not_found_error("Finca no encontrada")
            
            # Obtener estadísticas de lotes
            lotes_stats = finca.lotes.aggregate(
                total_lotes=Count('id'),
                hectareas_cultivadas=Sum('hectareas'),
                promedio_edad=Avg('edad_plantas')
            )
            
            # Obtener lotes recientes
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
        Actualiza una finca.
        
        Args:
            finca_id: ID de la finca
            user: Usuario
            finca_data: Datos a actualizar
            
        Returns:
            ServiceResult con finca actualizada
        """
        try:
            try:
                if user.is_superuser or user.is_staff:
                    finca = Finca.objects.get(id=finca_id)
                else:
                    finca = Finca.objects.get(id=finca_id, agricultor=user)
            except Finca.DoesNotExist:
                return ServiceResult.not_found_error("Finca no encontrada")
            
            # Validar campos si se proporcionan
            if 'nombre' in finca_data:
                if len(finca_data['nombre']) < 2 or len(finca_data['nombre']) > 200:
                    return ServiceResult.validation_error(
                        "El nombre debe tener entre 2 y 200 caracteres",
                        details={"field": "nombre"}
                    )
            
            if 'hectareas' in finca_data:
                if finca_data['hectareas'] < 0.01:
                    return ServiceResult.validation_error(
                        "Las hectáreas deben ser mayor a 0.01",
                        details={"field": "hectareas"}
                    )
            
            # Guardar datos originales para el log
            original_data = {
                'nombre': finca.nombre,
                'ubicacion': finca.ubicacion,
                'municipio': finca.municipio,
                'departamento': finca.departamento,
                'hectareas': finca.hectareas,
                'activa': finca.activa
            }
            
            # Actualizar campos
            for field, value in finca_data.items():
                if hasattr(finca, field):
                    setattr(finca, field, value)
            
            finca.save()
            
            # Crear log de auditoría
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
        Elimina una finca.
        
        Args:
            finca_id: ID de la finca
            user: Usuario
            
        Returns:
            ServiceResult con resultado de la eliminación
        """
        try:
            try:
                if user.is_superuser or user.is_staff:
                    finca = Finca.objects.get(id=finca_id)
                else:
                    finca = Finca.objects.get(id=finca_id, agricultor=user)
            except Finca.DoesNotExist:
                return ServiceResult.not_found_error("Finca no encontrada")
            
            # Verificar si tiene lotes asociados
            lotes_count = finca.lotes.count()
            if lotes_count > 0:
                return ServiceResult.validation_error(
                    f"No se puede eliminar la finca porque tiene {lotes_count} lotes asociados",
                    details={"lotes_count": lotes_count}
                )
            
            # Crear log de auditoría antes de eliminar
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
            
            # Eliminar finca
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
    
    def get_finca_statistics(self, user: User, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Obtiene estadísticas de fincas de un usuario.
        
        Args:
            user: Usuario
            filters: Filtros adicionales
            
        Returns:
            ServiceResult con estadísticas
        """
        try:
            # Construir queryset base
            if user.is_superuser or user.is_staff:
                queryset = Finca.objects.all()
            else:
                queryset = Finca.objects.filter(agricultor=user)
            
            # Aplicar filtros
            if filters:
                if 'departamento' in filters:
                    queryset = queryset.filter(departamento=filters['departamento'])
                if 'activa' in filters:
                    queryset = queryset.filter(activa=filters['activa'])
            
            # Calcular estadísticas
            stats = {
                'total_fincas': queryset.count(),
                'fincas_activas': queryset.filter(activa=True).count(),
                'fincas_inactivas': queryset.filter(activa=False).count(),
                'total_hectareas': queryset.aggregate(total=Sum('hectareas'))['total'] or 0,
                'promedio_hectareas': queryset.aggregate(avg=Avg('hectareas'))['avg'] or 0,
                'departamentos': dict(queryset.values('departamento').annotate(count=Count('id')).values_list('departamento', 'count')),
                'municipios': dict(queryset.values('municipio').annotate(count=Count('id')).values_list('municipio', 'count')),
                'recent_fincas': queryset.filter(created_at__gte=timezone.now() - timedelta(days=30)).count(),
                'hectareas_distribution': {
                    'small': queryset.filter(hectareas__lt=5).count(),  # < 5 ha
                    'medium': queryset.filter(hectareas__gte=5, hectareas__lt=20).count(),  # 5-20 ha
                    'large': queryset.filter(hectareas__gte=20).count()  # > 20 ha
                }
            }
            
            return ServiceResult.success(
                data=stats,
                message="Estadísticas obtenidas exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo estadísticas: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo estadísticas", details={"original_error": str(e)})
            )
    
    def _serialize_finca(self, finca: Finca) -> Dict[str, Any]:
        """
        Serializa una finca a diccionario.
        
        Args:
            finca: Instancia de Finca
            
        Returns:
            Diccionario con datos de la finca
        """
        return {
            'id': finca.id,
            'nombre': finca.nombre,
            'ubicacion': finca.ubicacion,
            'municipio': finca.municipio,
            'departamento': finca.departamento,
            'hectareas': finca.hectareas,
            'activa': finca.activa,
            'descripcion': finca.descripcion,
            'coordenadas': finca.coordenadas,
            'clima': finca.clima,
            'tipo_suelo': finca.tipo_suelo,
            'altitud': finca.altitud,
            'precipitacion_anual': finca.precipitacion_anual,
            'temperatura_promedio': finca.temperatura_promedio,
            'created_at': finca.created_at.isoformat(),
            'updated_at': finca.updated_at.isoformat(),
            'lotes_count': finca.lotes.count()
        }


class LoteService(BaseService):
    """
    Servicio para manejar gestión de lotes.
    """
    
    def __init__(self):
        super().__init__()
    
    def create_lote(self, lote_data: Dict[str, Any], user: User) -> ServiceResult:
        """
        Crea un nuevo lote.
        
        Args:
            lote_data: Datos del lote
            user: Usuario que crea el lote
            
        Returns:
            ServiceResult con datos del lote creado
        """
        try:
            # Validar campos requeridos
            required_fields = ['finca', 'identificador', 'variedad', 'fecha_plantacion', 'hectareas']
            self.validate_required_fields(lote_data, required_fields)
            
            # Validar que la finca pertenezca al usuario
            try:
                if user.is_superuser or user.is_staff:
                    finca = Finca.objects.get(id=lote_data['finca'])
                else:
                    finca = Finca.objects.get(id=lote_data['finca'], agricultor=user)
            except Finca.DoesNotExist:
                return ServiceResult.not_found_error("Finca no encontrada")
            
            # Validar identificador único en la finca
            if Lote.objects.filter(finca=finca, identificador=lote_data['identificador']).exists():
                return ServiceResult.validation_error(
                    "Ya existe un lote con este identificador en la finca",
                    details={"field": "identificador"}
                )
            
            # Validar valores
            validations = {
                'identificador': {'min_length': 1, 'max_length': 50},
                'variedad': {'min_length': 2, 'max_length': 100},
                'hectareas': {'type': (int, float), 'min': 0.01}
            }
            self.validate_field_values(lote_data, validations)
            
            # Crear lote
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
            
            # Crear log de auditoría
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
            
            self.log_info(f"Lote {lote.id} creado por usuario {user.username}")
            
            return ServiceResult.success(
                data=self._serialize_lote(lote),
                message="Lote creado exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error creando lote: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno creando lote", details={"original_error": str(e)})
            )
    
    def get_finca_lotes(self, finca_id: int, user: User, page: int = 1, page_size: int = 20, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Obtiene lotes de una finca específica.
        
        Args:
            finca_id: ID de la finca
            user: Usuario
            page: Número de página
            page_size: Tamaño de página
            filters: Filtros adicionales
            
        Returns:
            ServiceResult con lotes paginados
        """
        try:
            # Verificar que la finca pertenezca al usuario
            try:
                if user.is_superuser or user.is_staff:
                    finca = Finca.objects.get(id=finca_id)
                else:
                    finca = Finca.objects.get(id=finca_id, agricultor=user)
            except Finca.DoesNotExist:
                return ServiceResult.not_found_error("Finca no encontrada")
            
            # Construir queryset
            queryset = Lote.objects.filter(finca=finca).order_by('-created_at')
            
            # Aplicar filtros
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
            
            # Paginar resultados
            paginated_data = self.paginate_results(queryset, page, page_size)
            
            # Formatear datos
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
                message="Lotes obtenidos exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo lotes: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo lotes", details={"original_error": str(e)})
            )
    
    def get_lote_details(self, lote_id: int, user: User) -> ServiceResult:
        """
        Obtiene detalles de un lote específico.
        
        Args:
            lote_id: ID del lote
            user: Usuario
            
        Returns:
            ServiceResult con detalles del lote
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
                return ServiceResult.not_found_error("Lote no encontrado")
            
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
                message="Detalles de lote obtenidos exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo detalles: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo detalles", details={"original_error": str(e)})
            )
    
    def update_lote(self, lote_id: int, user: User, lote_data: Dict[str, Any]) -> ServiceResult:
        """
        Actualiza un lote.
        
        Args:
            lote_id: ID del lote
            user: Usuario
            lote_data: Datos a actualizar
            
        Returns:
            ServiceResult con lote actualizado
        """
        try:
            try:
                if user.is_superuser or user.is_staff:
                    lote = Lote.objects.get(id=lote_id)
                else:
                    lote = Lote.objects.get(id=lote_id, finca__agricultor=user)
            except Lote.DoesNotExist:
                return ServiceResult.not_found_error("Lote no encontrado")
            
            # Validar identificador único si se está cambiando
            if 'identificador' in lote_data and lote_data['identificador'] != lote.identificador:
                if Lote.objects.filter(finca=lote.finca, identificador=lote_data['identificador']).exists():
                    return ServiceResult.validation_error(
                        "Ya existe un lote con este identificador en la finca",
                        details={"field": "identificador"}
                    )
            
            # Guardar datos originales para el log
            original_data = {
                'identificador': lote.identificador,
                'variedad': lote.variedad,
                'hectareas': lote.hectareas,
                'estado': lote.estado
            }
            
            # Actualizar campos
            for field, value in lote_data.items():
                if hasattr(lote, field):
                    setattr(lote, field, value)
            
            lote.save()
            
            # Crear log de auditoría
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
            
            self.log_info(f"Lote {lote_id} actualizado por usuario {user.username}")
            
            return ServiceResult.success(
                data=self._serialize_lote(lote),
                message="Lote actualizado exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error actualizando lote: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno actualizando lote", details={"original_error": str(e)})
            )
    
    def delete_lote(self, lote_id: int, user: User) -> ServiceResult:
        """
        Elimina un lote.
        
        Args:
            lote_id: ID del lote
            user: Usuario
            
        Returns:
            ServiceResult con resultado de la eliminación
        """
        try:
            try:
                if user.is_superuser or user.is_staff:
                    lote = Lote.objects.get(id=lote_id)
                else:
                    lote = Lote.objects.get(id=lote_id, finca__agricultor=user)
            except Lote.DoesNotExist:
                return ServiceResult.not_found_error("Lote no encontrado")
            
            # Crear log de auditoría antes de eliminar
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
            
            # Eliminar lote
            lote.delete()
            
            self.log_info(f"Lote {lote_id} eliminado por usuario {user.username}")
            
            return ServiceResult.success(
                message="Lote eliminado exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error eliminando lote: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno eliminando lote", details={"original_error": str(e)})
            )
    
    def get_lote_statistics(self, user: User, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Obtiene estadísticas de lotes de un usuario.
        
        Args:
            user: Usuario
            filters: Filtros adicionales
            
        Returns:
            ServiceResult con estadísticas
        """
        try:
            # Construir queryset base
            if user.is_superuser or user.is_staff:
                queryset = Lote.objects.all()
            else:
                queryset = Lote.objects.filter(finca__agricultor=user)
            
            # Aplicar filtros
            if filters:
                if 'finca_id' in filters:
                    queryset = queryset.filter(finca_id=filters['finca_id'])
                if 'estado' in filters:
                    queryset = queryset.filter(estado=filters['estado'])
                if 'variedad' in filters:
                    queryset = queryset.filter(variedad=filters['variedad'])
            
            # Calcular estadísticas
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
                message="Estadísticas obtenidas exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo estadísticas: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo estadísticas", details={"original_error": str(e)})
            )
    
    def _serialize_lote(self, lote: Lote) -> Dict[str, Any]:
        """
        Serializa un lote a diccionario.
        
        Args:
            lote: Instancia de Lote
            
        Returns:
            Diccionario con datos del lote
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


