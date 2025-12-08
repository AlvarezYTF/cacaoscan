"""
User management views for CacaoScan API.
"""
import logging
from datetime import timedelta, datetime
from typing import Tuple, Optional
from django.db.models import Q, Count, Avg, Min, Max, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.views.mixins import PaginationMixin, AdminPermissionMixin
from api.serializers import UserSerializer, ErrorResponseSerializer
from api.utils.decorators import handle_api_errors

User = get_user_model()

logger = logging.getLogger("cacaoscan.api.auth.users")

# Error message constants
ERROR_USER_NOT_FOUND = 'Usuario no encontrado'


class UserListView(PaginationMixin, AdminPermissionMixin, APIView):
    """
    Endpoint para listar usuarios con filtros y paginación (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la lista de usuarios con filtros y paginación (solo admins)",
        operation_summary="Lista de usuarios",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página (máximo 100)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('role', openapi.IN_QUERY, description="Filtrar por rol (admin, analyst, farmer)", type=openapi.TYPE_STRING),
            openapi.Parameter('is_active', openapi.IN_QUERY, description="Filtrar por estado activo", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('is_verified', openapi.IN_QUERY, description="Filtrar por estado de verificación", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Buscar en username, email, nombre", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Fecha de registro desde (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Fecha de registro hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Lista de usuarios obtenida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Usuarios']
    )
    @handle_api_errors(
        error_message="Error obteniendo lista de usuarios",
        log_message="Error obteniendo lista de usuarios"
    )
    def get(self, request):
        """
        Obtiene la lista de usuarios con filtros y paginación.
        Solo accesible para administradores.
        """
        # Verificar permisos de administrador
        if not self.is_admin_user(request.user):
            return self.admin_permission_denied()
        
        # Obtener parámetros de consulta (paginación se maneja en el mixin)
        role = request.GET.get('role')
        is_active = request.GET.get('is_active')
        is_verified = request.GET.get('is_verified')
        search = request.GET.get('search')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        # Construir queryset base (evitar select_related/prefetch a relaciones no garantizadas)
        queryset = User.objects.all().prefetch_related('groups')
        
        # Aplicar filtros
        if role:
            if role == 'admin':
                queryset = queryset.filter(Q(is_superuser=True) | Q(is_staff=True))
            elif role == 'analyst':
                queryset = queryset.filter(groups__name='analyst')
            elif role == 'farmer':
                queryset = queryset.filter(
                    ~Q(is_superuser=True),
                    ~Q(is_staff=True),
                    ~Q(groups__name='analyst')
                )
        
        if is_active is not None:
            active_bool = is_active.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_active=active_bool)
        
        if is_verified is not None:
            verified_bool = is_verified.lower() in ['true', '1', 'yes']
            if verified_bool:
                queryset = queryset.filter(auth_email_token__is_verified=True)
            else:
                queryset = queryset.filter(
                    Q(auth_email_token__is_verified=False) | 
                    Q(auth_email_token__isnull=True)
                )
        
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        if date_from:
            queryset = queryset.filter(date_joined__date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(date_joined__date__lte=date_to)
        
        # Ordenar por fecha de registro (más recientes primero)
        queryset = queryset.order_by('-date_joined')
        
        # Paginar usando el mixin
        return self.paginate_queryset(
            request,
            queryset,
            UserSerializer
        )


class UserUpdateView(AdminPermissionMixin, APIView):
    """
    Endpoint para actualizar información de un usuario (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Actualiza la información de un usuario específico (solo admins)",
        operation_summary="Actualizar usuario",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'is_staff': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'groups': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
            }
        ),
        responses={
            200: openapi.Response(
                description="Usuario actualizado exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Usuarios']
    )
    def _get_user_or_404(self, user_id: int) -> Tuple[User, Optional[Response]]:
        """Obtiene un usuario o retorna respuesta 404."""
        try:
            user = User.objects.get(id=user_id)
            return user, None
        except User.DoesNotExist:
            return None, Response({
                'error': ERROR_USER_NOT_FOUND,
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def _validate_self_deactivation(self, user: User, request_user, is_active: Optional[bool]) -> Optional[Response]:
        """Valida que un usuario no se pueda desactivar a sí mismo."""
        if user == request_user and is_active is False:
            return Response({
                'error': 'No puedes desactivar tu propia cuenta',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        return None
    
    def _update_basic_fields(self, user: User, request_data: dict, user_id: int) -> Optional[Response]:
        """Actualiza los campos básicos del usuario."""
        if 'first_name' in request_data:
            user.first_name = request_data['first_name']
        
        if 'last_name' in request_data:
            user.last_name = request_data['last_name']
        
        if 'email' in request_data:
            if User.objects.filter(email=request_data['email']).exclude(id=user_id).exists():
                return Response({
                    'error': 'Este email ya está en uso por otro usuario',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.email = request_data['email']
            user.username = request_data['email']
        
        if 'is_active' in request_data:
            user.is_active = request_data['is_active']
        
        if 'is_staff' in request_data:
            user.is_staff = request_data['is_staff']
        
        return None
    
    def _update_user_groups(self, user: User, group_names: list) -> None:
        """Actualiza los grupos del usuario."""
        user.groups.clear()
        for group_name in group_names:
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                logger.warning(f"Grupo '{group_name}' no encontrado")
    
    def patch(self, request, user_id):
        """
        Actualiza la información de un usuario específico.
        Solo accesible para administradores.
        """
        if not self.is_admin_user(request.user):
            return self.admin_permission_denied()
        
        user, error_response = self._get_user_or_404(user_id)
        if error_response:
            return error_response
        
        validation_error = self._validate_self_deactivation(
            user, request.user, request.data.get('is_active')
        )
        if validation_error:
            return validation_error
        
        update_error = self._update_basic_fields(user, request.data, user_id)
        if update_error:
            return update_error
        
        user.save()
        
        if 'groups' in request.data:
            self._update_user_groups(user, request.data['groups'])
        
        serializer = UserSerializer(user)
        return Response({
            'message': 'Usuario actualizado exitosamente',
            'user': serializer.data
        }, status=status.HTTP_200_OK)


class UserDeleteView(AdminPermissionMixin, APIView):
    """
    Endpoint para eliminar un usuario (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Elimina un usuario del sistema (solo admins)",
        operation_summary="Eliminar usuario",
        responses={
            200: openapi.Response(
                description="Usuario eliminado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'deleted_user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Usuarios']
    )
    def delete(self, request, user_id):
        """
        Elimina un usuario del sistema.
        Solo accesible para administradores.
        """
        # Verificar permisos de administrador
        if not self.is_admin_user(request.user):
            return self.admin_permission_denied()
        
        # Obtener usuario
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                'error': ERROR_USER_NOT_FOUND,
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validaciones de seguridad
        if user == request.user:
            return Response({
                'error': 'No puedes eliminar tu propia cuenta',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if user.is_superuser and not request.user.is_superuser:
            return Response({
                'error': 'No tienes permisos para eliminar superusuarios',
                'status': 'error'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Guardar información del usuario antes de eliminarlo
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser
        }
        
        # Eliminar usuario (esto también eliminará el perfil y tokens relacionados)
        user.delete()
        
        logger.info(f"Usuario {user_data['username']} eliminado por admin {request.user.username}")
        
        return Response({
            'message': 'Usuario eliminado exitosamente',
            'deleted_user': user_data
        }, status=status.HTTP_200_OK)


class UserStatsView(AdminPermissionMixin, APIView):
    """
    Endpoint para obtener estadísticas de usuarios (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas de usuarios del sistema (solo admins)",
        operation_summary="Estadísticas de usuarios",
        responses={
            200: openapi.Response(
                description="Estadísticas obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
        },
        tags=['Usuarios']
    )
    def get(self, request):
        """
        Obtiene estadísticas de usuarios.
        Solo accesible para administradores.
        """
        # Verificar permisos de administrador
        if not self.is_admin_user(request.user):
            return self.admin_permission_denied()
        
        # Estadísticas generales
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = total_users - active_users
        
        # Usuarios registrados hoy
        today = timezone.now().date()
        users_today = User.objects.filter(date_joined__date=today).count()
        
        # Usuarios en línea (últimos 5 minutos)
        five_minutes_ago = timezone.now() - timedelta(minutes=5)
        online_users = User.objects.filter(last_login__gte=five_minutes_ago).count()
        
        # Usuarios por rol
        admin_users = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True)).count()
        analyst_users = User.objects.filter(groups__name='analyst').distinct().count()
        farmer_users = User.objects.filter(
            ~Q(is_superuser=True),
            ~Q(is_staff=True),
            ~Q(groups__name='analyst')
        ).count()
        
        # Usuarios por estado de verificación
        verified_users = User.objects.filter(
            auth_email_token__is_verified=True
        ).count()
        
        # Usuarios nuevos esta semana
        this_week_start = today - timedelta(days=today.weekday())
        users_this_week = User.objects.filter(date_joined__date__gte=this_week_start).count()
        
        # Usuarios nuevos este mes
        this_month_start = today.replace(day=1)
        users_this_month = User.objects.filter(date_joined__date__gte=this_month_start).count()
        
        # Preparar respuesta
        stats = {
            'total': total_users,
            'active': active_users,
            'inactive': inactive_users,
            'online': online_users,
            'new_today': users_today,
            'new_this_week': users_this_week,
            'new_this_month': users_this_month,
            'by_role': {
                'admin': admin_users,
                'analyst': analyst_users,
                'farmer': farmer_users
            },
            'verified': verified_users,
            'generated_at': timezone.now().isoformat()
        }
        
        return Response(stats, status=status.HTTP_200_OK)


# Temporarily disable cache to debug 500 error
# @method_decorator(cache_page(60 * 10, cache='api_cache'), name='get')
class AdminStatsView(AdminPermissionMixin, APIView):
    """
    Endpoint para obtener estadísticas globales del sistema (Admin only).
    
    CACHED: Este endpoint está cacheado por 10 minutos porque:
    - Calcular estadísticas globales requiere múltiples agregaciones SQL pesadas
    - Las estadísticas no cambian frecuentemente en tiempo real
    - Reduce significativamente la carga en la base de datos
    - El cache se invalida automáticamente cuando hay cambios relevantes (nuevos usuarios, imágenes, etc.)
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas globales del sistema (solo admins)",
        operation_summary="Estadísticas del sistema",
        responses={
            200: openapi.Response(
                description="Estadísticas obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
        },
        tags=['Usuarios']
    )
    def get(self, request):
        """
        Obtiene estadísticas globales del sistema.
        Solo accesible para administradores.
        
        Retorna las estadísticas directamente de forma síncrona.
        Siempre devuelve una respuesta válida, incluso si hay errores.
        """
        logger.info(f"[AdminStatsView] Iniciando get() para usuario: {request.user.username if request.user.is_authenticated else 'Anonymous'}")
        
        # Default empty stats response
        default_empty_response = {
            'users': {'total': 0, 'active': 0, 'staff': 0, 'superusers': 0, 'analysts': 0, 'farmers': 0, 'verified': 0, 'this_week': 0, 'this_month': 0},
            'fincas': {'total': 0, 'this_week': 0, 'this_month': 0},
            'images': {'total': 0, 'processed': 0, 'unprocessed': 0, 'this_week': 0, 'this_month': 0, 'processing_rate': 0},
            'predictions': {'total': 0, 'average_dimensions': {'alto_mm': 0, 'ancho_mm': 0, 'grosor_mm': 0, 'peso_g': 0}, 'average_confidence': 0, 'average_processing_time_ms': 0},
            'top_regions': [],
            'top_fincas': [],
            'activity_by_day': {'labels': [], 'data': []},
            'quality_distribution': {'excelente': 0, 'buena': 0, 'regular': 0, 'baja': 0},
            'generated_at': None
        }
        
        try:
            # Verificar permisos de administrador
            try:
                if not self.is_admin_user(request.user):
                    return self.admin_permission_denied()
            except Exception as perm_error:
                logger.error(f"Error verificando permisos: {perm_error}", exc_info=True)
                # Si falla la verificación de permisos, asumir que no es admin y denegar acceso
                return Response({
                    'error': 'Permiso denegado',
                    'details': 'No tienes permisos para acceder a esta funcionalidad'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Calcular estadísticas directamente (síncrono)
            try:
                from api.services.stats import StatsService
                stats_service = StatsService()
            except Exception as import_error:
                logger.error(f"Error importando StatsService: {import_error}", exc_info=True)
                return Response(default_empty_response, status=status.HTTP_200_OK)
            
            try:
                stats = stats_service.get_all_stats()
                logger.info(f"Admin stats calculated successfully - Users: {stats.get('users', {}).get('total', 0)}, Fincas: {stats.get('fincas', {}).get('total', 0)}")
                return Response(stats, status=status.HTTP_200_OK)
            except Exception as stats_error:
                logger.error(f"Error calculando estadísticas en StatsService: {stats_error}", exc_info=True)
                # Intentar obtener estadísticas básicas aunque falle alguna parte
                try:
                    # Obtener al menos estadísticas de usuarios que son críticas
                    user_stats = stats_service.get_user_stats()
                    finca_stats = stats_service.get_finca_stats()
                    image_stats = stats_service.get_image_stats()
                    
                    stats = {
                        'users': user_stats,
                        'fincas': finca_stats,
                        'images': image_stats,
                        'predictions': {'average_confidence': 0},
                        'activity_by_day': {'labels': [], 'data': []},
                        'quality_distribution': {'excelente': 0, 'buena': 0, 'regular': 0, 'baja': 0}
                    }
                    logger.warning(f"Stats parciales generadas después de error: {stats_error}")
                    return Response(stats, status=status.HTTP_200_OK)
                except Exception as fallback_error:
                    logger.error(f"Error incluso en fallback de estadísticas: {fallback_error}", exc_info=True)
                    # Último recurso: datos vacíos
                    try:
                        return Response(stats_service.get_empty_stats(), status=status.HTTP_200_OK)
                    except Exception:
                        return Response(default_empty_response, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error general en AdminStatsView: {e}", exc_info=True)
            # Retornar datos vacíos en lugar de 500
            return Response(default_empty_response, status=status.HTTP_200_OK)


class UserDetailView(AdminPermissionMixin, APIView):
    """
    Endpoint para obtener detalles de un usuario específico (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los detalles completos de un usuario específico (solo admins)",
        operation_summary="Detalles de usuario",
        responses={
            200: openapi.Response(
                description="Detalles de usuario obtenidos exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Usuarios']
    )
    def get(self, request, user_id):
        """
        Obtiene los detalles completos de un usuario específico.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            # Obtener usuario con optimizaciones para evitar N+1 queries
            try:
                user = User.objects.select_related(
                    'api_profile', 
                    'api_email_token'
                ).prefetch_related(
                    'groups',
                    'api_cacao_images',
                    'images_app_cacao_images',
                    'images_app_cacao_images__prediction',
                    'images_app_cacao_images__finca',
                    'images_app_cacao_images__lote'
                ).get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'error': ERROR_USER_NOT_FOUND,
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Serializar usuario con información extendida
            serializer = UserSerializer(user)
            user_data = serializer.data
            
            # Agregar estadísticas adicionales
            try:
                cacao_images_manager = getattr(user, 'cacao_images', None) or getattr(user, 'api_cacao_images', None) or getattr(user, 'images_app_cacao_images', None)
                total_images = cacao_images_manager.count() if cacao_images_manager is not None else 0
                processed_images = cacao_images_manager.filter(processed=True).count() if cacao_images_manager is not None else 0
            except Exception:
                total_images = 0
                processed_images = 0

            user_data['stats'] = {
                'total_images': total_images,
                'processed_images': processed_images,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'days_since_registration': (timezone.now().date() - user.date_joined.date()).days,
                'has_profile': hasattr(user, 'profile') or hasattr(user, 'api_profile'),
                'groups': [group.name for group in user.groups.all()]
            }

            # Incluir datos de persona (si existe) usando serializers de la app personas
            try:
                from personas.models import Persona
                from personas.serializers import PersonaSerializer
                persona = Persona.objects.select_related('user', 'tipo_documento', 'genero', 'departamento', 'municipio').filter(user=user).first()
                user_data['persona'] = PersonaSerializer(persona).data if persona else None
            except Exception:
                user_data['persona'] = None
            
            return Response(user_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo detalles de usuario {user_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

