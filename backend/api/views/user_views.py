"""
User management views for CacaoScan API.
"""
import logging
from datetime import timedelta, datetime
from django.db.models import Q, Count, Avg, Min, Max, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..views.mixins import PaginationMixin, AdminPermissionMixin
from ..serializers import UserSerializer, ErrorResponseSerializer
from ..utils.decorators import handle_api_errors

User = get_user_model()

from ..utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage',
    'CacaoPrediction': 'images_app.models.CacaoPrediction',
    'Finca': 'fincas_app.models.Finca'
})
CacaoImage = models['CacaoImage']
CacaoPrediction = models['CacaoPrediction']
Finca = models['Finca']

logger = logging.getLogger("cacaoscan.api.users")


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
    def patch(self, request, user_id):
        """
        Actualiza la información de un usuario específico.
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
                'error': 'Usuario no encontrado',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Validar que no se puede desactivar a sí mismo
        if user == request.user and request.data.get('is_active') is False:
            return Response({
                'error': 'No puedes desactivar tu propia cuenta',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Actualizar campos básicos
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        
        if 'email' in request.data:
            # Verificar que el email no esté en uso por otro usuario
            if User.objects.filter(email=request.data['email']).exclude(id=user_id).exists():
                return Response({
                    'error': 'Este email ya está en uso por otro usuario',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            user.email = request.data['email']
            user.username = request.data['email']  # Mantener username = email
        
        if 'is_active' in request.data:
            user.is_active = request.data['is_active']
        
        if 'is_staff' in request.data:
            user.is_staff = request.data['is_staff']
        
        # Guardar cambios
        user.save()
        
        # Actualizar grupos si se proporcionan
        if 'groups' in request.data:
            group_names = request.data['groups']
            
            # Limpiar grupos existentes
            user.groups.clear()
            
            # Agregar nuevos grupos
            for group_name in group_names:
                try:
                    group = Group.objects.get(name=group_name)
                    user.groups.add(group)
                except Group.DoesNotExist:
                    logger.warning(f"Grupo '{group_name}' no encontrado")
        
        # Serializar usuario actualizado
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
                'error': 'Usuario no encontrado',
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


class AdminStatsView(AdminPermissionMixin, APIView):
    """
    Endpoint para obtener estadísticas globales del sistema (Admin only).
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
        """
        try:
            # Verificar permisos de administrador
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            # Estadísticas de usuarios
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            staff_users = User.objects.filter(is_staff=True).count()
            superusers = User.objects.filter(is_superuser=True).count()
            
            logger.info(f"[AdminStatsView] Usuarios - Total: {total_users}, Activos: {active_users}, Staff: {staff_users}, Superusers: {superusers}")
            
            # Usuarios por rol
            analyst_users = User.objects.filter(groups__name='analyst').distinct().count()
            farmer_users = User.objects.filter(
                ~Q(is_superuser=True),
                ~Q(is_staff=True),
                ~Q(groups__name='analyst')
            ).count()
            
            # Usuarios verificados - usar auth_email_token (related_name correcto)
            try:
                verified_users = User.objects.filter(
                    auth_email_token__is_verified=True
                ).count()
            except Exception:
                # Si no existe el campo, contar solo usuarios activos
                verified_users = User.objects.filter(is_active=True).count()
            
            # Estadísticas de imágenes
            total_images = 0
            processed_images = 0
            unprocessed_images = 0
            if CacaoImage is not None:
                total_images = CacaoImage.objects.count()
                processed_images = CacaoImage.objects.filter(processed=True).count()
                unprocessed_images = total_images - processed_images
            logger.info(f"[AdminStatsView] Imágenes - Total: {total_images}, Procesadas: {processed_images}, Sin procesar: {unprocessed_images}")
            
            # Estadísticas por fecha
            today = timezone.now().date()
            this_week = today - timedelta(days=7)
            this_month = today - timedelta(days=30)
            
            users_this_week = User.objects.filter(date_joined__date__gte=this_week).count()
            users_this_month = User.objects.filter(date_joined__date__gte=this_month).count()
            
            images_this_week = 0
            images_this_month = 0
            if CacaoImage is not None:
                images_this_week = CacaoImage.objects.filter(created_at__date__gte=this_week).count()
                images_this_month = CacaoImage.objects.filter(created_at__date__gte=this_month).count()
            
            # Datos de actividad por día para gráficos
            max_days_to_check = 30
            
            # Obtener conteos de imágenes por fecha usando agregación (más eficiente)
            images_by_date = {}
            if CacaoImage is not None:
                images_by_date = dict(
                    CacaoImage.objects
                    .filter(created_at__date__gte=today - timedelta(days=max_days_to_check))
                    .annotate(date=TruncDate('created_at'))
                    .values('date')
                    .annotate(count=Count('id'))
                    .values_list('date', 'count')
                )
            
            # Usuarios por día (últimos 30 días)
            users_by_date = dict(
                User.objects
                .filter(date_joined__date__gte=today - timedelta(days=max_days_to_check))
                .annotate(date=TruncDate('date_joined'))
                .values('date')
                .annotate(count=Count('id'))
                .values_list('date', 'count')
            )
            
            # Predicciones por día (últimos 30 días)
            predictions_by_date = {}
            if CacaoPrediction is not None:
                predictions_by_date = dict(
                    CacaoPrediction.objects
                    .filter(created_at__date__gte=today - timedelta(days=max_days_to_check))
                    .annotate(date=TruncDate('created_at'))
                    .values('date')
                    .annotate(count=Count('id'))
                    .values_list('date', 'count')
                )
            
            # Contar días únicos con actividad
            all_dates_with_activity = set()
            all_dates_with_activity.update(images_by_date.keys())
            all_dates_with_activity.update(users_by_date.keys())
            all_dates_with_activity.update(predictions_by_date.keys())
            
            days_with_activity_count = len(all_dates_with_activity)
            
            # Determinar cuántos días mostrar
            if days_with_activity_count > 10:
                days_to_show = max_days_to_check  # Mostrar últimos 30 días
                logger.info(f"[AdminStatsView] Más de 10 días con actividad ({days_with_activity_count}), mostrando últimos {days_to_show} días")
            else:
                days_to_show = 7
                logger.info(f"[AdminStatsView] {days_with_activity_count} días con actividad, mostrando últimos 7 días")
            
            activity_by_day = []
            activity_labels = []
            
            for i in range(days_to_show - 1, -1, -1):  # Desde hace N días hasta hoy
                date = today - timedelta(days=i)
                
                # Obtener conteos del diccionario (más eficiente que queries individuales)
                images_count = images_by_date.get(date, 0)
                users_count = users_by_date.get(date, 0)
                predictions_count = predictions_by_date.get(date, 0)
                
                total_activity = images_count + users_count + predictions_count
                
                activity_by_day.append(total_activity)
                
                # Formato de labels: "Hoy", "Ayer", o fecha
                if i == 0:
                    activity_labels.append('Hoy')
                elif i == 1:
                    activity_labels.append('Ayer')
                else:
                    # Para muchos días, usar formato más compacto
                    if days_to_show > 14:
                        activity_labels.append(date.strftime('%d/%m'))
                    else:
                        # Para pocos días, incluir día de la semana
                        day_names = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
                        day_name = day_names[date.weekday()]
                        activity_labels.append(f"{day_name} {date.strftime('%d/%m')}")
            
            logger.info(f"[AdminStatsView] Actividad por día: {activity_by_day} ({len(activity_by_day)} días mostrados)")
            
            # Estadísticas de fincas
            total_fincas = 0
            fincas_this_week = 0
            fincas_this_month = 0
            if Finca is not None:
                total_fincas = Finca.objects.count()
                fincas_this_week = Finca.objects.filter(fecha_registro__date__gte=this_week).count()
                fincas_this_month = Finca.objects.filter(fecha_registro__date__gte=this_month).count()
                logger.info(f"[AdminStatsView] Fincas - Total: {total_fincas}, Esta semana: {fincas_this_week}, Este mes: {fincas_this_month}")
            else:
                logger.warning("[WARNING] [AdminStatsView] Finca model no está disponible")
            
            # Estadísticas de predicciones
            total_predictions = 0
            avg_dimensions = {}
            avg_confidence = 0
            if CacaoPrediction is not None:
                total_predictions = CacaoPrediction.objects.count()
                
                # Estadísticas de dimensiones promedio
                avg_dimensions = CacaoPrediction.objects.aggregate(
                    avg_alto=Avg('alto_mm'),
                    avg_ancho=Avg('ancho_mm'),
                    avg_grosor=Avg('grosor_mm'),
                    avg_peso=Avg('peso_g'),
                    avg_processing_time=Avg('processing_time_ms')
                )
                
                # Calcular promedio de confidence manualmente
                if CacaoPrediction.objects.exists():
                    confidences = []
                    for pred in CacaoPrediction.objects.all():
                        confidences.append(float(pred.average_confidence))
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Estadísticas por región
            region_stats = []
            if CacaoImage is not None:
                region_stats = list(CacaoImage.objects.values('region').annotate(
                    count=Count('id'),
                    processed_count=Count('id', filter=Q(processed=True))
                ).order_by('-count')[:10])
            
            # Estadísticas por finca
            finca_stats = []
            if CacaoImage is not None:
                finca_stats = list(CacaoImage.objects.values('finca').annotate(
                    count=Count('id'),
                    processed_count=Count('id', filter=Q(processed=True))
                ).order_by('-count')[:10])
            
            # Distribución de calidad para gráfico de dona
            quality_distribution = {
                'excelente': 0,  # >= 0.8
                'buena': 0,      # 0.6 - 0.79
                'regular': 0,    # 0.4 - 0.59
                'baja': 0        # < 0.4
            }
            
            if CacaoPrediction is not None and CacaoPrediction.objects.exists():
                for pred in CacaoPrediction.objects.all():
                    conf = float(pred.average_confidence)
                    if conf >= 0.8:
                        quality_distribution['excelente'] += 1
                    elif conf >= 0.6:
                        quality_distribution['buena'] += 1
                    elif conf >= 0.4:
                        quality_distribution['regular'] += 1
                    else:
                        quality_distribution['baja'] += 1
            
            logger.info(f"[AdminStatsView] Distribución de calidad: {quality_distribution}")
            
            # Preparar respuesta
            stats = {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'staff': staff_users,
                    'superusers': superusers,
                    'analysts': analyst_users,
                    'farmers': farmer_users,
                    'verified': verified_users,
                    'this_week': users_this_week,
                    'this_month': users_this_month
                },
                'images': {
                    'total': total_images,
                    'processed': processed_images,
                    'unprocessed': unprocessed_images,
                    'this_week': images_this_week,
                    'this_month': images_this_month,
                    'processing_rate': round((processed_images / total_images * 100), 2) if total_images > 0 else 0
                },
                'fincas': {
                    'total': total_fincas,
                    'this_week': fincas_this_week,
                    'this_month': fincas_this_month
                },
                'predictions': {
                    'total': total_predictions,
                    'average_dimensions': {
                        'alto_mm': round(float(avg_dimensions.get('avg_alto', 0) or 0), 2),
                        'ancho_mm': round(float(avg_dimensions.get('avg_ancho', 0) or 0), 2),
                        'grosor_mm': round(float(avg_dimensions.get('avg_grosor', 0) or 0), 2),
                        'peso_g': round(float(avg_dimensions.get('avg_peso', 0) or 0), 2)
                    },
                    'average_confidence': round(float(avg_confidence), 3),
                    'average_processing_time_ms': round(float(avg_dimensions.get('avg_processing_time', 0) or 0), 0)
                },
                'top_regions': region_stats,
                'top_fincas': finca_stats,
                'activity_by_day': {
                    'labels': activity_labels,
                    'data': activity_by_day
                },
                'quality_distribution': quality_distribution,
                'generated_at': timezone.now().isoformat()
            }
            
            logger.info(f"[INFO] [AdminStatsView] Estadísticas generadas - Users: {stats['users']['total']}, Fincas: {stats['fincas']['total']}, Images: {stats['images']['total']}, Quality: {stats['predictions']['average_confidence']}")
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.warning(f"[WARNING] Error obteniendo estadísticas del sistema: {e}")
            # Retornar datos vacíos en lugar de 500
            return Response({
                'users': {
                    'total': 0,
                    'active': 0,
                    'staff': 0,
                    'superusers': 0,
                    'analysts': 0,
                    'farmers': 0,
                    'verified': 0,
                    'this_week': 0,
                    'this_month': 0
                },
                'images': {
                    'total': 0,
                    'processed': 0,
                    'unprocessed': 0,
                    'this_week': 0,
                    'this_month': 0,
                    'processing_rate': 0
                },
                'predictions': {
                    'total': 0,
                    'average_dimensions': {
                        'alto_mm': 0,
                        'ancho_mm': 0,
                        'grosor_mm': 0,
                        'peso_g': 0
                    },
                    'average_confidence': 0,
                    'average_processing_time_ms': 0
                },
                'top_regions': [],
                'top_fincas': [],
                'generated_at': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)


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
            
            # Obtener usuario
            try:
                user = User.objects.select_related('api_profile', 'api_email_token').prefetch_related('groups', 'api_cacao_images', 'images_app_cacao_images').get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'error': 'Usuario no encontrado',
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

