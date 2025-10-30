"""
Vistas para gestión de lotes en CacaoScan.
"""
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

try:
    from fincas_app.models import Lote, Finca
except ImportError:
    Lote = None
    Finca = None
from .serializers import (
    LoteSerializer,
    LoteListSerializer,
    LoteDetailSerializer,
    LoteStatsSerializer,
    ErrorResponseSerializer
)

logger = logging.getLogger("cacaoscan.api")


class LotePermissionMixin:
    """
    Mixin para permisos de lotes.
    Los agricultores solo pueden ver/editar lotes de sus fincas.
    Los administradores pueden ver/editar todos los lotes.
    """
    
    def get_queryset(self):
        """Obtener queryset filtrado por permisos."""
        user = self.request.user
        
        if user.is_superuser or user.is_staff:
            # Admin puede ver todos los lotes
            return Lote.objects.all().select_related('finca', 'finca__agricultor')
        else:
            # Agricultor solo ve lotes de sus fincas
            return Lote.objects.filter(
                finca__agricultor=user
            ).select_related('finca', 'finca__agricultor')
    
    def perform_create(self, serializer):
        """Validar que la finca pertenezca al usuario."""
        finca_id = self.request.data.get('finca')
        if finca_id:
            try:
                finca = Finca.objects.get(id=finca_id)
                if not (self.request.user.is_superuser or self.request.user.is_staff):
                    if finca.agricultor != self.request.user:
                        raise ValueError("No tienes permisos para crear lotes en esta finca.")
                serializer.save()
            except Finca.DoesNotExist:
                raise ValueError("Finca no encontrada.")


class LoteListCreateView(LotePermissionMixin, APIView):
    """
    Vista para listar y crear lotes.
    GET: Lista lotes del usuario (o todos si es admin)
    POST: Crea nuevo lote
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Lista todos los lotes del usuario autenticado",
        operation_summary="Listar lotes",
        manual_parameters=[
            openapi.Parameter('finca', openapi.IN_QUERY, description="Filtrar por finca", type=openapi.TYPE_INTEGER),
            openapi.Parameter('variedad', openapi.IN_QUERY, description="Filtrar por variedad", type=openapi.TYPE_STRING),
            openapi.Parameter('estado', openapi.IN_QUERY, description="Filtrar por estado", type=openapi.TYPE_STRING),
            openapi.Parameter('activo', openapi.IN_QUERY, description="Filtrar por estado activo", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Búsqueda por identificador o variedad", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description="Lista de lotes obtenida exitosamente"),
            401: ErrorResponseSerializer,
        },
        tags=['Lotes']
    )
    def get(self, request):
        """Listar lotes con filtros."""
        try:
            queryset = self.get_queryset()
            
            # Aplicar filtros
            finca_id = request.GET.get('finca')
            if finca_id:
                queryset = queryset.filter(finca_id=finca_id)
            
            variedad = request.GET.get('variedad', '').strip()
            if variedad:
                queryset = queryset.filter(variedad__icontains=variedad)
            
            estado = request.GET.get('estado', '').strip()
            if estado:
                queryset = queryset.filter(estado=estado)
            
            activa = request.GET.get('activa')
            if activa is not None:
                activa_bool = activa.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(activo=activa_bool)
            
            search = request.GET.get('search', '').strip()
            if search:
                queryset = queryset.filter(
                    Q(identificador__icontains=search) |
                    Q(variedad__icontains=search) |
                    Q(finca__nombre__icontains=search)
                )
            
            # Paginación
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))
            
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            # Serializar datos
            serializer = LoteListSerializer(page_obj.object_list, many=True)
            
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
            logger.error(f"Error listando lotes para usuario {request.user.username}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Crea un nuevo lote para el usuario autenticado",
        operation_summary="Crear lote",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'finca': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID de la finca"),
                'identificador': openapi.Schema(type=openapi.TYPE_STRING, description="Identificador del lote"),
                'variedad': openapi.Schema(type=openapi.TYPE_STRING, description="Variedad de cacao"),
                'fecha_plantacion': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha de plantación"),
                'fecha_cosecha': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha de cosecha"),
                'area_hectareas': openapi.Schema(type=openapi.TYPE_NUMBER, description="Área en hectáreas"),
                'estado': openapi.Schema(type=openapi.TYPE_STRING, description="Estado del lote"),
                'descripcion': openapi.Schema(type=openapi.TYPE_STRING, description="Descripción adicional"),
                'coordenadas_lat': openapi.Schema(type=openapi.TYPE_NUMBER, description="Latitud GPS"),
                'coordenadas_lng': openapi.Schema(type=openapi.TYPE_NUMBER, description="Longitud GPS"),
            },
            required=['finca', 'identificador', 'variedad', 'fecha_plantacion', 'area_hectareas']
        ),
        responses={
            201: openapi.Response(description="Lote creado exitosamente"),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Lotes']
    )
    def post(self, request):
        """Crear nuevo lote."""
        try:
            # Validar que la finca existe y pertenece al usuario
            finca_id = request.data.get('finca')
            if not finca_id:
                return Response({
                    'error': 'La finca es requerida',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                finca = Finca.objects.get(id=finca_id)
                if not (request.user.is_superuser or request.user.is_staff):
                    if finca.agricultor != request.user:
                        return Response({
                            'error': 'No tienes permisos para crear lotes en esta finca',
                            'status': 'error'
                        }, status=status.HTTP_403_FORBIDDEN)
            except Finca.DoesNotExist:
                return Response({
                    'error': 'Finca no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = LoteSerializer(
                data=request.data, 
                context={'request': request, 'finca': finca}
            )
            
            if serializer.is_valid():
                lote = serializer.save()
                
                logger.info(f"Lote '{lote.identificador}' creado por usuario {request.user.username}")
                
                # Devolver datos completos
                response_serializer = LoteSerializer(lote, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': 'Datos de entrada inválidos',
                    'details': serializer.errors,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creando lote para usuario {request.user.username}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoteDetailView(LotePermissionMixin, APIView):
    """
    Vista para obtener detalles de un lote específico.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los detalles de un lote específico",
        operation_summary="Detalles de lote",
        responses={
            200: openapi.Response(description="Detalles de lote obtenidos exitosamente"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Lotes']
    )
    def get(self, request, lote_id):
        """Obtener detalles de lote."""
        try:
            queryset = self.get_queryset()
            lote = queryset.get(id=lote_id)
            
            serializer = LoteDetailSerializer(lote, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Lote.DoesNotExist:
            return Response({
                'error': 'Lote no encontrado',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error obteniendo detalles de lote {lote_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoteUpdateView(LotePermissionMixin, APIView):
    """
    Vista para actualizar un lote específico.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Actualiza un lote específico",
        operation_summary="Actualizar lote",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'identificador': openapi.Schema(type=openapi.TYPE_STRING, description="Identificador del lote"),
                'variedad': openapi.Schema(type=openapi.TYPE_STRING, description="Variedad de cacao"),
                'fecha_plantacion': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha de plantación"),
                'fecha_cosecha': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha de cosecha"),
                'area_hectareas': openapi.Schema(type=openapi.TYPE_NUMBER, description="Área en hectáreas"),
                'estado': openapi.Schema(type=openapi.TYPE_STRING, description="Estado del lote"),
                'descripcion': openapi.Schema(type=openapi.TYPE_STRING, description="Descripción adicional"),
                'coordenadas_lat': openapi.Schema(type=openapi.TYPE_NUMBER, description="Latitud GPS"),
                'coordenadas_lng': openapi.Schema(type=openapi.TYPE_NUMBER, description="Longitud GPS"),
                'activo': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Estado activo"),
            }
        ),
        responses={
            200: openapi.Response(description="Lote actualizado exitosamente"),
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Lotes']
    )
    def put(self, request, lote_id):
        """Actualizar lote completo."""
        try:
            queryset = self.get_queryset()
            lote = queryset.get(id=lote_id)
            
            serializer = LoteSerializer(
                lote, 
                data=request.data, 
                context={'request': request, 'finca': lote.finca}
            )
            
            if serializer.is_valid():
                lote = serializer.save()
                
                logger.info(f"Lote '{lote.identificador}' actualizado por usuario {request.user.username}")
                
                response_serializer = LoteSerializer(lote, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Datos de entrada inválidos',
                    'details': serializer.errors,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Lote.DoesNotExist:
            return Response({
                'error': 'Lote no encontrado',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error actualizando lote {lote_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, lote_id):
        """Actualizar lote parcialmente."""
        try:
            queryset = self.get_queryset()
            lote = queryset.get(id=lote_id)
            
            serializer = LoteSerializer(
                lote, 
                data=request.data, 
                partial=True, 
                context={'request': request, 'finca': lote.finca}
            )
            
            if serializer.is_valid():
                lote = serializer.save()
                
                logger.info(f"Lote '{lote.identificador}' actualizado parcialmente por usuario {request.user.username}")
                
                response_serializer = LoteSerializer(lote, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Datos de entrada inválidos',
                    'details': serializer.errors,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Lote.DoesNotExist:
            return Response({
                'error': 'Lote no encontrado',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error actualizando lote {lote_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoteDeleteView(LotePermissionMixin, APIView):
    """
    Vista para eliminar un lote específico.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Elimina un lote específico",
        operation_summary="Eliminar lote",
        responses={
            204: openapi.Response(description="Lote eliminado exitosamente"),
            400: openapi.Response(description="No se puede eliminar lote con dependencias"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Lotes']
    )
    def delete(self, request, lote_id):
        """Eliminar lote."""
        try:
            queryset = self.get_queryset()
            lote = queryset.get(id=lote_id)
            
            # Verificar si tiene análisis asociados
            if lote.cacao_images.exists():
                return Response({
                    'error': 'No se puede eliminar el lote porque tiene análisis asociados',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            lote_identificador = lote.identificador
            lote.delete()
            
            logger.info(f"Lote '{lote_identificador}' eliminado por usuario {request.user.username}")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Lote.DoesNotExist:
            return Response({
                'error': 'Lote no encontrado',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error eliminando lote {lote_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoteStatsView(LotePermissionMixin, APIView):
    """
    Vista para obtener estadísticas de un lote específico.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas detalladas de un lote",
        operation_summary="Estadísticas de lote",
        responses={
            200: openapi.Response(description="Estadísticas obtenidas exitosamente"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Lotes']
    )
    def get(self, request, lote_id):
        """Obtener estadísticas de lote."""
        try:
            queryset = self.get_queryset()
            lote = queryset.get(id=lote_id)
            
            stats = lote.get_estadisticas()
            
            # Agregar estadísticas adicionales
            stats.update({
                'lote_identificador': lote.identificador,
                'finca_nombre': lote.finca.nombre,
                'agricultor_nombre': lote.finca.agricultor.get_full_name(),
                'ubicacion_completa': lote.ubicacion_completa,
            })
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Lote.DoesNotExist:
            return Response({
                'error': 'Lote no encontrado',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de lote {lote_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LotesPorFincaView(LotePermissionMixin, APIView):
    """
    Vista para obtener lotes de una finca específica.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene todos los lotes de una finca específica",
        operation_summary="Lotes por finca",
        responses={
            200: openapi.Response(description="Lotes obtenidos exitosamente"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Lotes']
    )
    def get(self, request, finca_id):
        """Obtener lotes de una finca."""
        try:
            # Verificar que la finca existe y pertenece al usuario
            if request.user.is_superuser or request.user.is_staff:
                finca = Finca.objects.get(id=finca_id)
            else:
                finca = Finca.objects.get(id=finca_id, agricultor=request.user)
            
            lotes = Lote.objects.filter(finca=finca).select_related('finca', 'finca__agricultor')
            
            serializer = LoteListSerializer(lotes, many=True)
            
            return Response({
                'finca': {
                    'id': finca.id,
                    'nombre': finca.nombre,
                    'ubicacion': finca.ubicacion_completa
                },
                'lotes': serializer.data,
                'total': lotes.count()
            }, status=status.HTTP_200_OK)
            
        except Finca.DoesNotExist:
            return Response({
                'error': 'Finca no encontrada',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error obteniendo lotes de finca {finca_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
