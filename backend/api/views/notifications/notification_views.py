"""
Vistas para gestión de notificaciones en CacaoScan.
"""
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import Q, Count
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..mixins import PaginationMixin, AdminPermissionMixin

from ...utils.model_imports import get_model_safely

Notification = get_model_safely('notifications.models.Notification')
from ...serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationStatsSerializer,
    NotificationCreateSerializer,
    ErrorResponseSerializer
)

logger = logging.getLogger("cacaoscan.api")

# Error message constants
ERROR_INTERNAL_SERVER = 'Error interno del servidor'


class NotificationListCreateView(PaginationMixin, APIView):
    """
    Vista para listar y crear notificaciones.
    GET: Lista notificaciones del usuario
    POST: Crea nueva notificación (solo admin)
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Lista todas las notificaciones del usuario autenticado",
        operation_summary="Listar notificaciones",
        manual_parameters=[
            openapi.Parameter('tipo', openapi.IN_QUERY, description="Filtrar por tipo", type=openapi.TYPE_STRING),
            openapi.Parameter('leida', openapi.IN_QUERY, description="Filtrar por estado leído", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Búsqueda por título", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description="Lista de notificaciones obtenida exitosamente"),
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def get(self, request):
        """Listar notificaciones con filtros."""
        try:
            if Notification is None:
                # Si el modelo no está disponible, retornar vacío
                return Response({
                    'results': [],
                    'count': 0,
                    'page': 1,
                    'page_size': 20,
                    'total_pages': 0,
                    'next': None,
                    'previous': None,
                }, status=status.HTTP_200_OK)
            
            queryset = Notification.objects.filter(user=request.user).order_by('-fecha_creacion')
            
            # Aplicar filtros
            tipo = request.GET.get('tipo', '').strip()
            if tipo:
                queryset = queryset.filter(tipo=tipo)
            
            leida = request.GET.get('leida')
            if leida is not None:
                leida_bool = leida.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(leida=leida_bool)
            
            search = request.GET.get('search', '').strip()
            if search:
                queryset = queryset.filter(titulo__icontains=search)
            
            # Paginar usando el mixin
            return self.paginate_queryset(
                request,
                queryset,
                NotificationListSerializer
            )
            
        except Exception as e:
            logger.error(f"Error listando notificaciones para usuario {request.user.username}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationDetailView(APIView):
    """
    Vista para obtener detalles de una notificación específica.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los detalles de una notificación específica",
        operation_summary="Detalles de notificación",
        responses={
            200: openapi.Response(description="Detalles de notificación obtenidos exitosamente"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def get(self, request, notification_id):
        """Obtener detalles de notificación."""
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Notification.DoesNotExist:
            return Response({
                'error': 'Notificación no encontrada',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error obteniendo detalles de notificación {notification_id}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationMarkReadView(APIView):
    """
    Vista para marcar una notificación como leída.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Marca una notificación como leída",
        operation_summary="Marcar notificación como leída",
        responses={
            200: openapi.Response(description="Notificación marcada como leída exitosamente"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def post(self, request, notification_id):
        """Marcar notificación como leída."""
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            
            notification.mark_as_read()
            
            logger.info(f"Notificación {notification_id} marcada como leída por usuario {request.user.username}")
            
            return Response({
                'message': 'Notificación marcada como leída',
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Notification.DoesNotExist:
            return Response({
                'error': 'Notificación no encontrada',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error marcando notificación {notification_id} como leída: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationMarkAllReadView(APIView):
    """
    Vista para marcar todas las notificaciones como leídas.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Marca todas las notificaciones del usuario como leídas",
        operation_summary="Marcar todas las notificaciones como leídas",
        responses={
            200: openapi.Response(description="Todas las notificaciones marcadas como leídas exitosamente"),
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def post(self, request):
        """Marcar todas las notificaciones como leídas."""
        try:
            Notification.mark_all_as_read(request.user)
            
            logger.info(f"Todas las notificaciones marcadas como leídas por usuario {request.user.username}")
            
            return Response({
                'message': 'Todas las notificaciones han sido marcadas como leídas',
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error marcando todas las notificaciones como leídas: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationUnreadCountView(APIView):
    """
    Vista para obtener el contador de notificaciones no leídas.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene el número de notificaciones no leídas del usuario",
        operation_summary="Contador de notificaciones no leídas",
        responses={
            200: openapi.Response(description="Contador obtenido exitosamente"),
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def get(self, request):
        """Obtener contador de notificaciones no leídas."""
        try:
            unread_count = Notification.get_unread_count(request.user)
            
            return Response({
                'unread_count': unread_count,
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo contador de notificaciones no leídas: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationStatsView(APIView):
    """
    Vista para obtener estadísticas de notificaciones del usuario.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas de notificaciones del usuario",
        operation_summary="Estadísticas de notificaciones",
        responses={
            200: openapi.Response(description="Estadísticas obtenidas exitosamente"),
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def get(self, request):
        """Obtener estadísticas de notificaciones."""
        try:
            # Estadísticas básicas
            total_notifications = Notification.objects.filter(user=request.user).count()
            unread_count = Notification.get_unread_count(request.user)
            
            # Notificaciones por tipo
            notifications_by_type = dict(
                Notification.objects.filter(user=request.user)
                .values('tipo')
                .annotate(count=Count('id'))
                .values_list('tipo', 'count')
            )
            
            # Notificaciones recientes (últimas 5)
            recent_notifications = NotificationListSerializer(
                Notification.objects.filter(user=request.user)[:5],
                many=True
            ).data
            
            stats = {
                'total_notifications': total_notifications,
                'unread_count': unread_count,
                'notifications_by_type': notifications_by_type,
                'recent_notifications': recent_notifications,
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de notificaciones: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationCreateView(AdminPermissionMixin, APIView):
    """
    Vista para crear notificaciones (solo administradores).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Crea una nueva notificación (solo administradores)",
        operation_summary="Crear notificación",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del usuario destinatario"),
                'tipo': openapi.Schema(type=openapi.TYPE_STRING, description="Tipo de notificación"),
                'titulo': openapi.Schema(type=openapi.TYPE_STRING, description="Título de la notificación"),
                'mensaje': openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de la notificación"),
                'datos_extra': openapi.Schema(type=openapi.TYPE_OBJECT, description="Datos adicionales"),
            },
            required=['user', 'tipo', 'titulo', 'mensaje']
        ),
        responses={
            201: openapi.Response(description="Notificación creada exitosamente"),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def post(self, request):
        """Crear nueva notificación."""
        try:
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied('No tienes permisos para crear notificaciones')
            
            serializer = NotificationCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                notification = serializer.save()
                
                logger.info(f"Notificación '{notification.titulo}' creada por admin {request.user.username}")
                
                response_serializer = NotificationSerializer(notification)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': 'Datos de entrada inválidos',
                    'details': serializer.errors,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creando notificación: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


