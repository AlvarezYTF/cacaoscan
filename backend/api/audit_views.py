"""
Vistas para auditoría y logs de actividad en CacaoScan.
"""
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import LoginHistory
try:
    from audit.models import ActivityLog
except ImportError:
    ActivityLog = None
from .serializers import ErrorResponseSerializer

logger = logging.getLogger("cacaoscan.api")


class ActivityLogListView(APIView):
    """
    Vista para listar logs de actividad (solo administradores).
    """
    permission_classes = [IsAuthenticated]
    
    def _is_admin_user(self, user):
        """Verificar si el usuario es administrador."""
        return user.is_superuser or user.is_staff
    
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
    def get(self, request):
        """Listar logs de actividad con filtros."""
        try:
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a los logs de actividad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            if ActivityLog is None:
                # Si el modelo no está disponible, retornar vacío
                return Response({
                    'results': [],
                    'count': 0,
                    'page': 1,
                    'page_size': 50,
                    'total_pages': 0,
                    'next': None,
                    'previous': None,
                }, status=status.HTTP_200_OK)
            
            queryset = ActivityLog.objects.all().select_related('usuario').order_by('-timestamp')
            
            # Aplicar filtros
            usuario = request.GET.get('usuario', '').strip()
            if usuario:
                queryset = queryset.filter(usuario__username__icontains=usuario)
            
            accion = request.GET.get('accion', '').strip()
            if accion:
                queryset = queryset.filter(accion=accion)
            
            modelo = request.GET.get('modelo', '').strip()
            if modelo:
                queryset = queryset.filter(modelo__icontains=modelo)
            
            ip_address = request.GET.get('ip_address', '').strip()
            if ip_address:
                queryset = queryset.filter(ip_address__icontains=ip_address)
            
            # Filtros de fecha
            fecha_desde = request.GET.get('fecha_desde')
            if fecha_desde:
                try:
                    fecha_desde = timezone.datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                    queryset = queryset.filter(timestamp__date__gte=fecha_desde)
                except ValueError:
                    return Response({
                        'error': 'Formato de fecha inválido. Use YYYY-MM-DD',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            fecha_hasta = request.GET.get('fecha_hasta')
            if fecha_hasta:
                try:
                    fecha_hasta = timezone.datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                    queryset = queryset.filter(timestamp__date__lte=fecha_hasta)
                except ValueError:
                    return Response({
                        'error': 'Formato de fecha inválido. Use YYYY-MM-DD',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Paginación
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 50))
            
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # Serializar datos
            logs_data = []
            for log in page_obj.object_list:
                logs_data.append({
                    'id': log.id,
                    'usuario': log.usuario.username if log.usuario else 'Usuario Anónimo',
                    'accion': log.accion,
                    'accion_display': log.get_accion_display(),
                    'modelo': log.modelo,
                    'objeto_id': log.objeto_id,
                    'descripcion': log.descripcion,
                    'ip_address': log.ip_address,
                    'timestamp': log.timestamp.isoformat(),
                    'datos_antes': log.datos_antes,
                    'datos_despues': log.datos_despues,
                })
            
            return Response({
                'results': logs_data,
                'count': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'next': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listando logs de actividad: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginHistoryListView(APIView):
    """
    Vista para listar historial de logins (solo administradores).
    """
    permission_classes = [IsAuthenticated]
    
    def _is_admin_user(self, user):
        """Verificar si el usuario es administrador."""
        return user.is_superuser or user.is_staff
    
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
    def get(self, request):
        """Listar historial de logins con filtros."""
        try:
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder al historial de logins',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            queryset = LoginHistory.objects.all().select_related('usuario')
            
            # Aplicar filtros
            usuario = request.GET.get('usuario', '').strip()
            if usuario:
                queryset = queryset.filter(usuario__username__icontains=usuario)
            
            ip_address = request.GET.get('ip_address', '').strip()
            if ip_address:
                queryset = queryset.filter(ip_address__icontains=ip_address)
            
            success = request.GET.get('success')
            if success is not None:
                success_bool = success.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(success=success_bool)
            
            # Filtros de fecha
            fecha_desde = request.GET.get('fecha_desde')
            if fecha_desde:
                try:
                    fecha_desde = timezone.datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                    queryset = queryset.filter(login_time__date__gte=fecha_desde)
                except ValueError:
                    return Response({
                        'error': 'Formato de fecha inválido. Use YYYY-MM-DD',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            fecha_hasta = request.GET.get('fecha_hasta')
            if fecha_hasta:
                try:
                    fecha_hasta = timezone.datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                    queryset = queryset.filter(login_time__date__lte=fecha_hasta)
                except ValueError:
                    return Response({
                        'error': 'Formato de fecha inválido. Use YYYY-MM-DD',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Paginación
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 50))
            
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # Serializar datos
            logins_data = []
            for login in page_obj.object_list:
                logins_data.append({
                    'id': login.id,
                    'usuario': login.usuario.username,
                    'ip_address': login.ip_address,
                    'user_agent': login.user_agent,
                    'login_time': login.login_time.isoformat(),
                    'logout_time': login.logout_time.isoformat() if login.logout_time else None,
                    'session_duration': str(login.session_duration) if login.session_duration else None,
                    'success': login.success,
                    'failure_reason': login.failure_reason,
                })
            
            return Response({
                'results': logins_data,
                'count': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'next': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listando historial de logins: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AuditStatsView(APIView):
    """
    Vista para obtener estadísticas de auditoría (solo administradores).
    """
    permission_classes = [IsAuthenticated]
    
    def _is_admin_user(self, user):
        """Verificar si el usuario es administrador."""
        return user.is_superuser or user.is_staff
    
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
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a las estadísticas de auditoría',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Estadísticas de ActivityLog
            total_activities = ActivityLog.objects.count()
            activities_today = ActivityLog.objects.filter(
                timestamp__date=timezone.now().date()
            ).count()
            
            activities_by_action = dict(
                ActivityLog.objects.values('accion')
                .annotate(count=Count('id'))
                .values_list('accion', 'count')
            )
            
            activities_by_model = dict(
                ActivityLog.objects.values('modelo')
                .annotate(count=Count('id'))
                .values_list('modelo', 'count')
            )
            
            # Top usuarios más activos
            top_active_users = list(
                ActivityLog.objects.values('usuario__username')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )
            
            # Estadísticas de LoginHistory
            total_logins = LoginHistory.objects.count()
            successful_logins = LoginHistory.objects.filter(success=True).count()
            failed_logins = LoginHistory.objects.filter(success=False).count()
            
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
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


