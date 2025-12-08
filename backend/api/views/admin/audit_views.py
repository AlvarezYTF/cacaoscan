"""
Vistas para auditoría y logs de actividad en CacaoScan.
"""
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..mixins import AdminPermissionMixin, PaginationMixin

from audit.models import LoginHistory
from ...utils.model_imports import get_model_safely

ActivityLog = get_model_safely('audit.models.ActivityLog')
from ...serializers import ErrorResponseSerializer

logger = logging.getLogger("cacaoscan.api")

# Error message constants
ERROR_INVALID_DATE_FORMAT = 'Formato de fecha inválido. Use YYYY-MM-DD'
ERROR_INTERNAL_SERVER = 'Error interno del servidor'


class ActivityLogListView(PaginationMixin, AdminPermissionMixin, APIView):
    """
    Vista para listar logs de actividad (solo administradores).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Lista logs de actividad del sistema (solo administradores)",
        operation_summary="Listar logs de actividad",
        manual_parameters=[
            openapi.Parameter('usuario', openapi.IN_QUERY, description="Filtrar por usuario", type=openapi.TYPE_STRING),
            openapi.Parameter('accion', openapi.IN_QUERY, description="Filtrar por acción", type=openapi.TYPE_STRING),
            openapi.Parameter('modelo', openapi.IN_QUERY, description="Filtrar por modelo", type=openapi.TYPE_STRING),
            openapi.Parameter('ip_address', openapi.IN_QUERY, description="Filtrar por IP", type=openapi.TYPE_STRING),
            openapi.Parameter('fecha_desde', openapi.IN_QUERY, description="Fecha desde (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('fecha_hasta', openapi.IN_QUERY, description="Fecha hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description="Logs de actividad obtenidos exitosamente"),
            403: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Auditoría']
    )
    def _get_empty_response(self):
        """Return empty response when ActivityLog is not available."""
        return Response({
            'results': [],
            'count': 0,
            'page': 1,
            'page_size': 50,
            'total_pages': 0,
            'next': None,
            'previous': None,
        }, status=status.HTTP_200_OK)
    
    def _apply_text_filters(self, queryset, request):
        """Apply text-based filters to queryset."""
        usuario = request.GET.get('usuario', '').strip()
        if usuario:
            queryset = queryset.filter(user__username__icontains=usuario)
        
        accion = request.GET.get('accion', '').strip()
        if accion:
            queryset = queryset.filter(action=accion)
        
        modelo = request.GET.get('modelo', '').strip()
        if modelo:
            queryset = queryset.filter(resource_type__icontains=modelo)
        
        ip_address = request.GET.get('ip_address', '').strip()
        if ip_address:
            queryset = queryset.filter(ip_address__icontains=ip_address)
        
        return queryset
    
    def _apply_date_filters(self, queryset, request):
        """Apply date filters to queryset. Returns (queryset, error_response)."""
        fecha_desde = request.GET.get('fecha_desde')
        if fecha_desde:
            try:
                fecha_desde = timezone.datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__gte=fecha_desde)
            except ValueError:
                return None, Response({
                    'error': ERROR_INVALID_DATE_FORMAT,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        fecha_hasta = request.GET.get('fecha_hasta')
        if fecha_hasta:
            try:
                fecha_hasta = timezone.datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(timestamp__date__lte=fecha_hasta)
            except ValueError:
                return None, Response({
                    'error': ERROR_INVALID_DATE_FORMAT,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return queryset, None
    
    def _serialize_logs(self, logs):
        """Serialize logs for response."""
        return [{
            'id': log.id,
            'usuario': log.user.username if log.user else 'Usuario Anónimo',
            'accion': log.action,
            'accion_display': log.action,
            'modelo': log.resource_type,
            'objeto_id': log.resource_id,
            'descripcion': log.details.get('description', '') if isinstance(log.details, dict) else str(log.details),
            'ip_address': log.ip_address,
            'timestamp': log.timestamp.isoformat(),
            'datos_antes': log.details.get('before', {}) if isinstance(log.details, dict) else {},
            'datos_despues': log.details.get('after', {}) if isinstance(log.details, dict) else {},
        } for log in logs]
    
    def get(self, request):
        """Listar logs de actividad con filtros."""
        try:
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied('No tienes permisos para acceder a los logs de actividad')
            
            if ActivityLog is None:
                return self._get_empty_response()
            
            # Get ordering parameter from request
            ordering = request.GET.get('ordering', '-timestamp')
            # Validate ordering field (security: only allow specific fields)
            allowed_orderings = ['timestamp', '-timestamp', 'action', '-action', 'user__username', '-user__username']
            if ordering not in allowed_orderings:
                ordering = '-timestamp'  # Default to most recent first
            
            queryset = ActivityLog.objects.all().select_related('user').order_by(ordering)
            queryset = self._apply_text_filters(queryset, request)
            
            queryset, error_response = self._apply_date_filters(queryset, request)
            if error_response:
                return error_response
            
            logger.info(f"[ActivityLogListView] Querying {queryset.count()} activity logs")
            
            return self.paginate_queryset(
                request,
                queryset,
                serializer_func=self._serialize_logs,
                extra_data=None
            )
            
        except Exception as e:
            logger.error(f"Error listando logs de actividad: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginHistoryListView(PaginationMixin, AdminPermissionMixin, APIView):
    """
    Vista para listar historial de logins (solo administradores).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Lista historial de logins del sistema (solo administradores)",
        operation_summary="Listar historial de logins",
        manual_parameters=[
            openapi.Parameter('usuario', openapi.IN_QUERY, description="Filtrar por usuario", type=openapi.TYPE_STRING),
            openapi.Parameter('ip_address', openapi.IN_QUERY, description="Filtrar por IP", type=openapi.TYPE_STRING),
            openapi.Parameter('success', openapi.IN_QUERY, description="Filtrar por éxito", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('fecha_desde', openapi.IN_QUERY, description="Fecha desde (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('fecha_hasta', openapi.IN_QUERY, description="Fecha hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description="Historial de logins obtenido exitosamente"),
            403: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Auditoría']
    )
    def _apply_login_text_filters(self, queryset, request):
        """Apply text-based filters to login history queryset."""
        usuario = request.GET.get('usuario', '').strip()
        if usuario:
            queryset = queryset.filter(user__username__icontains=usuario)
        
        ip_address = request.GET.get('ip_address', '').strip()
        if ip_address:
            queryset = queryset.filter(ip_address__icontains=ip_address)
        
        success = request.GET.get('success')
        if success is not None:
            success_bool = success.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(login_successful=success_bool)
        
        return queryset
    
    def _apply_login_date_filters(self, queryset, request):
        """Apply date filters to login history queryset. Returns (queryset, error_response)."""
        fecha_desde = request.GET.get('fecha_desde')
        if fecha_desde:
            try:
                fecha_desde = timezone.datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(login_time__date__gte=fecha_desde)
            except ValueError:
                return None, Response({
                    'error': ERROR_INVALID_DATE_FORMAT,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        fecha_hasta = request.GET.get('fecha_hasta')
        if fecha_hasta:
            try:
                fecha_hasta = timezone.datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(login_time__date__lte=fecha_hasta)
            except ValueError:
                return None, Response({
                    'error': ERROR_INVALID_DATE_FORMAT,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return queryset, None
    
    def _serialize_logins(self, logins):
        """Serialize logins for response."""
        return [{
            'id': login.id,
            'usuario': login.user.username if login.user else 'Usuario Anónimo',
            'ip_address': login.ip_address,
            'user_agent': login.user_agent,
            'login_time': login.login_time.isoformat(),
            'logout_time': login.logout_time.isoformat() if login.logout_time else None,
            'session_duration': str(login.session_duration) if login.session_duration else None,
            'success': login.login_successful,
            'failure_reason': login.failure_reason,
        } for login in logins]
    
    def get(self, request):
        """Listar historial de logins con filtros."""
        try:
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied('No tienes permisos para acceder al historial de logins')
            
            queryset = LoginHistory.objects.all().select_related('user')
            queryset = self._apply_login_text_filters(queryset, request)
            
            queryset, error_response = self._apply_login_date_filters(queryset, request)
            if error_response:
                return error_response
            
            return self.paginate_queryset(
                request,
                queryset,
                serializer_func=self._serialize_logins,
                extra_data=None
            )
            
        except Exception as e:
            logger.error(f"Error listando historial de logins: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AuditStatsView(AdminPermissionMixin, APIView):
    """
    Vista para obtener estadísticas de auditoría (solo administradores).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas de auditoría del sistema (solo administradores)",
        operation_summary="Estadísticas de auditoría",
        responses={
            200: openapi.Response(description="Estadísticas obtenidas exitosamente"),
            403: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Auditoría']
    )
    def get(self, request):
        """Obtener estadísticas de auditoría."""
        try:
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied('No tienes permisos para acceder a las estadísticas de auditoría')
            
            # Check if models are available
            if ActivityLog is None:
                return Response({
                    'error': 'Modelo ActivityLog no disponible',
                    'status': 'error'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Estadísticas de ActivityLog
            total_activities = ActivityLog.objects.count()
            activities_today = ActivityLog.objects.filter(
                timestamp__date=timezone.now().date()
            ).count()
            
            activities_by_action = dict(
                ActivityLog.objects.values('action')
                .annotate(count=Count('id'))
                .values_list('action', 'count')
            )
            
            activities_by_model = dict(
                ActivityLog.objects.values('resource_type')
                .annotate(count=Count('id'))
                .values_list('resource_type', 'count')
            )
            
            # Top usuarios más activos
            top_active_users = list(
                ActivityLog.objects.values('user__username')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
            
            # Estadísticas de LoginHistory
            total_logins = LoginHistory.objects.count()
            successful_logins = LoginHistory.objects.filter(login_successful=True).count()
            failed_logins = LoginHistory.objects.filter(login_successful=False).count()
            
            # Logins por día (últimos 7 días)
            login_stats_by_day = []
            for i in range(7):
                date = timezone.now().date() - timedelta(days=i)
                day_logins = LoginHistory.objects.filter(login_time__date=date).count()
                login_stats_by_day.append({
                    'date': date.isoformat(),
                    'count': day_logins
                })
            
            # IPs más frecuentes
            top_ips = list(
                LoginHistory.objects.values('ip_address')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
            
            # Duración promedio de sesión
            avg_session_duration = LoginHistory.objects.filter(
                session_duration__isnull=False
            ).aggregate(avg_duration=Avg('session_duration'))['avg_duration']
            
            stats = {
                'activity_log': {
                    'total_activities': total_activities,
                    'activities_today': activities_today,
                    'activities_by_action': activities_by_action,
                    'activities_by_model': activities_by_model,
                    'top_active_users': top_active_users,
                },
                'login_history': {
                    'total_logins': total_logins,
                    'successful_logins': successful_logins,
                    'failed_logins': failed_logins,
                    'success_rate': (successful_logins / total_logins * 100) if total_logins > 0 else 0,
                    'login_stats_by_day': login_stats_by_day,
                    'top_ips': top_ips,
                    'avg_session_duration_minutes': avg_session_duration.total_seconds() / 60 if avg_session_duration else 0,
                },
                'generated_at': timezone.now().isoformat(),
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de auditoría: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


