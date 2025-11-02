"""
Vistas para gestiÃ³n de notificaciones en CacaoScan.
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

try:
    from notifications.models import Notification
except ImportError:
    Notification = None
from .serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationStatsSerializer,
    ErrorResponseSerializer
)

logger = logging.getLogger("cacaoscan.api")


class NotificationListCreateView(APIView):
    """
    Vista para listar y crear notificaciones.
    GET: Lista notificaciones del usuario
    POST: Crea nueva notificaciÃ³n (solo admin)
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Lista todas las notificaciones del usuario autenticado",
        operation_summary="Listar notificaciones",
        manual_parameters=[
            openapi.Parameter('tipo', openapi.IN_QUERY, description="Filtrar por tipo", type=openapi.TYPE_STRING),
            openapi.Parameter('leida', openapi.IN_QUERY, description="Filtrar por estado leÃ­do", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="BÃºsqueda por tÃ­tulo", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="NÃºmero de pÃ¡gina", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="TamaÃ±o de pÃ¡gina", type=openapi.TYPE_INTEGER),
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
                # Si el modelo no estÃ¡ disponible, retornar vacÃ­o
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
            
            # PaginaciÃ³n
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # Serializar datos
            serializer = NotificationListSerializer(page_obj.object_list, many=True)
            
            return Response({
                'results': serializer.data,
                'count': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'next': page_obj.next_page_number() if page_obj.has_next() else None,
                'previous': page_obj.previous_page_number() if page_obj.has_previous() else None,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error listando notificaciones para usuario {request.user.username}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationDetailView(APIView):
    """
    Vista para obtener detalles de una notificaciÃ³n especÃ­fica.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los detalles de una notificaciÃ³n especÃ­fica",
        operation_summary="Detalles de notificaciÃ³n",
        responses={
            200: openapi.Response(description="Detalles de notificaciÃ³n obtenidos exitosamente"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def get(self, request, notification_id):
        """Obtener detalles de notificaciÃ³n."""
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Notification.DoesNotExist:
            return Response({
                'error': 'NotificaciÃ³n no encontrada',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error obteniendo detalles de notificaciÃ³n {notification_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationMarkReadView(APIView):
    """
    Vista para marcar una notificaciÃ³n como leÃ­da.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Marca una notificaciÃ³n como leÃ­da",
        operation_summary="Marcar notificaciÃ³n como leÃ­da",
        responses={
            200: openapi.Response(description="NotificaciÃ³n marcada como leÃ­da exitosamente"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def post(self, request, notification_id):
        """Marcar notificaciÃ³n como leÃ­da."""
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            
            notification.mark_as_read()
            
            logger.info(f"NotificaciÃ³n {notification_id} marcada como leÃ­da por usuario {request.user.username}")
            
            return Response({
                'message': 'NotificaciÃ³n marcada como leÃ­da',
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Notification.DoesNotExist:
            return Response({
                'error': 'NotificaciÃ³n no encontrada',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error marcando notificaciÃ³n {notification_id} como leÃ­da: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationMarkAllReadView(APIView):
    """
    Vista para marcar todas las notificaciones como leÃ­das.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Marca todas las notificaciones del usuario como leÃ­das",
        operation_summary="Marcar todas las notificaciones como leÃ­das",
        responses={
            200: openapi.Response(description="Todas las notificaciones marcadas como leÃ­das exitosamente"),
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def post(self, request):
        """Marcar todas las notificaciones como leÃ­das."""
        try:
            Notification.mark_all_as_read(request.user)
            
            logger.info(f"Todas las notificaciones marcadas como leÃ­das por usuario {request.user.username}")
            
            return Response({
                'message': 'Todas las notificaciones han sido marcadas como leÃ­das',
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error marcando todas las notificaciones como leÃ­das: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationUnreadCountView(APIView):
    """
    Vista para obtener el contador de notificaciones no leÃ­das.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene el nÃºmero de notificaciones no leÃ­das del usuario",
        operation_summary="Contador de notificaciones no leÃ­das",
        responses={
            200: openapi.Response(description="Contador obtenido exitosamente"),
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def get(self, request):
        """Obtener contador de notificaciones no leÃ­das."""
        try:
            unread_count = Notification.get_unread_count(request.user)
            
            return Response({
                'unread_count': unread_count,
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo contador de notificaciones no leÃ­das: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationStatsView(APIView):
    """
    Vista para obtener estadÃ­sticas de notificaciones del usuario.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadÃ­sticas de notificaciones del usuario",
        operation_summary="EstadÃ­sticas de notificaciones",
        responses={
            200: openapi.Response(description="EstadÃ­sticas obtenidas exitosamente"),
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def get(self, request):
        """Obtener estadÃ­sticas de notificaciones."""
        try:
            # EstadÃ­sticas bÃ¡sicas
            total_notifications = Notification.objects.filter(user=request.user).count()
            unread_count = Notification.get_unread_count(request.user)
            
            # Notificaciones por tipo
            notifications_by_type = dict(
                Notification.objects.filter(user=request.user)
                .values('tipo')
                .annotate(count=Count('id'))
                .values_list('tipo', 'count')
            )
            
            # Notificaciones recientes (Ãºltimas 5)
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
            logger.error(f"Error obteniendo estadÃ­sticas de notificaciones: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationCreateView(APIView):
    """
    Vista para crear notificaciones (solo administradores).
    """
    permission_classes = [IsAuthenticated]
    
    def _is_admin_user(self, user):
        """Verificar si el usuario es administrador."""
        return user.is_superuser or user.is_staff
    
    @swagger_auto_schema(
        operation_description="Crea una nueva notificaciÃ³n (solo administradores)",
        operation_summary="Crear notificaciÃ³n",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del usuario destinatario"),
                'tipo': openapi.Schema(type=openapi.TYPE_STRING, description="Tipo de notificaciÃ³n"),
                'titulo': openapi.Schema(type=openapi.TYPE_STRING, description="TÃ­tulo de la notificaciÃ³n"),
                'mensaje': openapi.Schema(type=openapi.TYPE_STRING, description="Mensaje de la notificaciÃ³n"),
                'datos_extra': openapi.Schema(type=openapi.TYPE_OBJECT, description="Datos adicionales"),
            },
            required=['user', 'tipo', 'titulo', 'mensaje']
        ),
        responses={
            201: openapi.Response(description="NotificaciÃ³n creada exitosamente"),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Notificaciones']
    )
    def post(self, request):
        """Crear nueva notificaciÃ³n."""
        try:
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para crear notificaciones',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            serializer = NotificationCreateSerializer(data=request.data)
            
            if serializer.is_valid():
                notification = serializer.save()
                
                logger.info(f"NotificaciÃ³n '{notification.titulo}' creada por admin {request.user.username}")
                
                response_serializer = NotificationSerializer(notification)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': 'Datos de entrada invÃ¡lidos',
                    'details': serializer.errors,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creando notificaciÃ³n: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


