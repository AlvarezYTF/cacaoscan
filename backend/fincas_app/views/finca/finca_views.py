"""
Vistas para gestión de fincas en CacaoScan.
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

from api.views.mixins import PaginationMixin, AdminPermissionMixin

from api.utils.model_imports import get_model_safely

Finca = get_model_safely('fincas_app.models.Finca')
from api.serializers import (
    FincaSerializer,
    FincaListSerializer,
    FincaDetailSerializer,
    FincaStatsSerializer,
    ErrorResponseSerializer
)

logger = logging.getLogger("cacaoscan.api")

# Error message constants
ERROR_INTERNAL_SERVER = 'Error interno del servidor'
ERROR_INVALID_INPUT = 'Datos de entrada inválidos'
ERROR_FINCA_NOT_FOUND = 'Finca no encontrada'


class FincaPermissionMixin(AdminPermissionMixin):
    """
    Mixin para permisos de fincas.
    Los agricultores solo pueden ver/editar sus propias fincas.
    Los administradores pueden ver/editar todas las fincas.
    """
    
    def get_queryset(self):
        """Obtener queryset filtrado por permisos (optimizado con select_related)."""
        user = self.request.user
        
        base_queryset = Finca.objects.select_related('agricultor')
        
        if self.is_admin_user(user):
            # Admin puede ver todas las fincas (activas e inactivas)
            return base_queryset
        else:
            # Agricultor solo ve sus fincas ACTIVAS (soft delete)
            return base_queryset.filter(agricultor=user, activa=True)
    
    def perform_create(self, serializer):
        """Asignar automáticamente el agricultor al crear finca."""
        serializer.save(agricultor=self.request.user)


class FincaListCreateView(PaginationMixin, FincaPermissionMixin, APIView):
    """
    Vista para listar y crear fincas.
    GET: Lista fincas del usuario (o todas si es admin)
    POST: Crea nueva finca
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Lista todas las fincas del usuario autenticado",
        operation_summary="Listar fincas",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Búsqueda por nombre", type=openapi.TYPE_STRING),
            openapi.Parameter('municipio', openapi.IN_QUERY, description="Filtrar por municipio", type=openapi.TYPE_STRING),
            openapi.Parameter('departamento', openapi.IN_QUERY, description="Filtrar por departamento", type=openapi.TYPE_STRING),
            openapi.Parameter('activa', openapi.IN_QUERY, description="Filtrar por estado activo", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(description="Lista de fincas obtenida exitosamente"),
            401: ErrorResponseSerializer,
        },
        tags=['Fincas']
    )
    def get(self, request):
        """Listar fincas con filtros optimizados."""
        try:
            # Optimización: obtener solo los campos necesarios
            queryset = self.get_queryset().only(
                'id', 'nombre', 'municipio', 'departamento', 'hectareas', 
                'ubicacion', 'activa', 'fecha_registro'
            )
            
            # Aplicar filtros
            search = request.GET.get('search', '').strip()
            if search:
                queryset = queryset.filter(
                    Q(nombre__icontains=search) |
                    Q(municipio__icontains=search) |
                    Q(departamento__icontains=search)
                )
            
            municipio = request.GET.get('municipio', '').strip()
            if municipio:
                queryset = queryset.filter(municipio__icontains=municipio)
            
            departamento = request.GET.get('departamento', '').strip()
            if departamento:
                queryset = queryset.filter(departamento__icontains=departamento)
            
            # Filtro por estado activo (solo admins pueden ver inactivas)
            activa = request.GET.get('activa')
            if activa is not None and self.is_admin_user(request.user):
                activa_bool = activa.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(activa=activa_bool)
            
            # Filtrar por agricultor si se proporciona el parámetro (optimizado para el frontend)
            agricultor_id = request.GET.get('agricultor')
            if agricultor_id:
                try:
                    queryset = queryset.filter(agricultor_id=int(agricultor_id))
                except (ValueError, TypeError):
                    logger.warning(f"ID de agricultor inválido: {agricultor_id}")
            
            # Para consultas con agricultor, no paginar (solo para el frontend)
            if agricultor_id:
                # Retornar todas las fincas del agricultor sin paginación (más rápido)
                serializer = FincaListSerializer(queryset[:100], many=True)  # Máximo 100 para evitar sobrecarga
                return Response({
                    'results': serializer.data,
                    'count': queryset.count(),
                    'page': 1,
                    'page_size': len(serializer.data),
                    'total_pages': 1,
                    'next': None,
                    'previous': None,
                }, status=status.HTTP_200_OK)
            
            # Paginación solo para listados generales usando el mixin
            return self.paginate_queryset(
                request,
                queryset,
                FincaListSerializer
            )
            
        except Exception as e:
            logger.error(f"Error listando fincas para usuario {request.user.username}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Crea una nueva finca para el usuario autenticado",
        operation_summary="Crear finca",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nombre': openapi.Schema(type=openapi.TYPE_STRING, description="Nombre de la finca"),
                'ubicacion': openapi.Schema(type=openapi.TYPE_STRING, description="Ubicación de la finca"),
                'municipio': openapi.Schema(type=openapi.TYPE_STRING, description="Municipio"),
                'departamento': openapi.Schema(type=openapi.TYPE_STRING, description="Departamento"),
                'hectareas': openapi.Schema(type=openapi.TYPE_NUMBER, description="Hectáreas de la finca"),
                'descripcion': openapi.Schema(type=openapi.TYPE_STRING, description="Descripción adicional"),
                'coordenadas_lat': openapi.Schema(type=openapi.TYPE_NUMBER, description="Latitud GPS"),
                'coordenadas_lng': openapi.Schema(type=openapi.TYPE_NUMBER, description="Longitud GPS"),
            },
            required=['nombre', 'ubicacion', 'municipio', 'departamento', 'hectareas']
        ),
        responses={
            201: openapi.Response(description="Finca creada exitosamente"),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Fincas']
    )
    def post(self, request):
        """Crear nueva finca."""
        try:
            import traceback
            import sys
            
            # Obtener el agricultor desde request.data si está presente, sino usar request.user
            agricultor = request.user
            if 'agricultor' in request.data:
                from django.contrib.auth.models import User
                try:
                    agricultor = User.objects.get(id=request.data['agricultor'])
                except User.DoesNotExist:
                    return Response({
                        'error': 'Agricultor no encontrado',
                        'details': {'agricultor': ['El ID de agricultor proporcionado no existe']},
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Creando finca con datos: {request.data}, agricultor: {agricultor.id}")
            
            serializer = FincaSerializer(data=request.data, context={'request': request})
            
            if serializer.is_valid():
                # Si ya está el agricultor en request.data, usar el que vino en el serializer validado
                # sino, usar el agricultor extraído
                finca = serializer.save(agricultor=agricultor)
                
                logger.info(f"Finca '{finca.nombre}' creada por usuario {request.user.username} para agricultor {agricultor.id}")
                
                # Devolver datos completos
                response_serializer = FincaSerializer(finca, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"Errores de validación: {serializer.errors}")
                return Response({
                    'error': ERROR_INVALID_INPUT,
                    'details': serializer.errors,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creando finca para usuario {request.user.username}: {e}")
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            import traceback
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'error_detail': str(e),
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FincaDetailView(FincaPermissionMixin, APIView):
    """
    Vista para obtener detalles de una finca específica.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los detalles de una finca específica",
        operation_summary="Detalles de finca",
        responses={
            200: openapi.Response(description="Detalles de finca obtenidos exitosamente"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Fincas']
    )
    def get(self, request, finca_id):
        """Obtener detalles de finca."""
        try:
            queryset = self.get_queryset()
            finca = queryset.get(id=finca_id)
            
            serializer = FincaDetailSerializer(finca, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Finca.DoesNotExist:
            return Response({
                'error': ERROR_FINCA_NOT_FOUND,
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error obteniendo detalles de finca {finca_id}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FincaUpdateView(FincaPermissionMixin, APIView):
    """
    Vista para actualizar una finca específica.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Actualiza una finca específica",
        operation_summary="Actualizar finca",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'nombre': openapi.Schema(type=openapi.TYPE_STRING, description="Nombre de la finca"),
                'ubicacion': openapi.Schema(type=openapi.TYPE_STRING, description="Ubicación de la finca"),
                'municipio': openapi.Schema(type=openapi.TYPE_STRING, description="Municipio"),
                'departamento': openapi.Schema(type=openapi.TYPE_STRING, description="Departamento"),
                'hectareas': openapi.Schema(type=openapi.TYPE_NUMBER, description="Hectáreas de la finca"),
                'descripcion': openapi.Schema(type=openapi.TYPE_STRING, description="Descripción adicional"),
                'coordenadas_lat': openapi.Schema(type=openapi.TYPE_NUMBER, description="Latitud GPS"),
                'coordenadas_lng': openapi.Schema(type=openapi.TYPE_NUMBER, description="Longitud GPS"),
                'activa': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Estado activo"),
            }
        ),
        responses={
            200: openapi.Response(description="Finca actualizada exitosamente"),
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Fincas']
    )
    def put(self, request, finca_id):
        """Actualizar finca completa."""
        try:
            queryset = self.get_queryset()
            finca = queryset.get(id=finca_id)
            
            serializer = FincaSerializer(finca, data=request.data, context={'request': request})
            
            if serializer.is_valid():
                finca = serializer.save()
                
                logger.info(f"Finca '{finca.nombre}' actualizada por usuario {request.user.username}")
                
                response_serializer = FincaSerializer(finca, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': ERROR_INVALID_INPUT,
                    'details': serializer.errors,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Finca.DoesNotExist:
            return Response({
                'error': ERROR_FINCA_NOT_FOUND,
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error actualizando finca {finca_id}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request, finca_id):
        """Actualizar finca parcialmente."""
        try:
            queryset = self.get_queryset()
            finca = queryset.get(id=finca_id)
            
            serializer = FincaSerializer(finca, data=request.data, partial=True, context={'request': request})
            
            if serializer.is_valid():
                finca = serializer.save()
                
                logger.info(f"Finca '{finca.nombre}' actualizada parcialmente por usuario {request.user.username}")
                
                response_serializer = FincaSerializer(finca, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': ERROR_INVALID_INPUT,
                    'details': serializer.errors,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Finca.DoesNotExist:
            return Response({
                'error': ERROR_FINCA_NOT_FOUND,
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error actualizando finca {finca_id}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FincaDeleteView(FincaPermissionMixin, APIView):
    """
    Vista para eliminar una finca específica.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Elimina una finca específica",
        operation_summary="Eliminar finca",
        responses={
            204: openapi.Response(description="Finca eliminada exitosamente"),
            400: openapi.Response(description="No se puede eliminar finca con dependencias"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Fincas']
    )
    def delete(self, request, finca_id):
        """Desactivar finca (soft delete)."""
        try:
            # Usar queryset sin filtro de activa para poder desactivar fincas inactivas
            if self.is_admin_user(request.user):
                queryset = Finca.objects.all()
            else:
                queryset = Finca.objects.filter(agricultor=request.user)
            
            finca = queryset.get(id=finca_id)
            
            if not finca.activa:
                return Response({
                    'error': 'La finca ya está desactivada',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            finca_nombre = finca.nombre
            # Soft delete: marcar como inactiva en lugar de eliminar
            finca.activa = False
            finca.save(update_fields=['activa'])
            
            logger.info(f"Finca '{finca_nombre}' desactivada (soft delete) por usuario {request.user.username}")
            
            return Response({
                'message': 'Finca desactivada correctamente',
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Finca.DoesNotExist:
            return Response({
                'error': ERROR_FINCA_NOT_FOUND,
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error desactivando finca {finca_id}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FincaActivateView(FincaPermissionMixin, APIView):
    """
    Vista para reactivar una finca desactivada (soft delete).
    Solo accesible para administradores.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Reactivar una finca desactivada (solo admins)",
        operation_summary="Reactivar finca",
        responses={
            200: openapi.Response(description="Finca reactivada exitosamente"),
            400: openapi.Response(description="La finca ya está activa"),
            403: openapi.Response(description="Permiso denegado"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Fincas']
    )
    def post(self, request, finca_id):
        """Reactivar finca (solo admins)."""
        try:
            # Solo admins pueden reactivar fincas
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied('No tienes permisos para reactivar fincas')
            
            # Obtener la finca sin filtro de activa
            try:
                finca = Finca.objects.get(id=finca_id)
            except Finca.DoesNotExist:
                return Response({
                    'error': ERROR_FINCA_NOT_FOUND,
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            if finca.activa:
                return Response({
                    'error': 'La finca ya está activa',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            finca_nombre = finca.nombre
            finca.activa = True
            finca.save(update_fields=['activa'])
            
            logger.info(f"Finca '{finca_nombre}' reactivada por admin {request.user.username}")
            
            return Response({
                'message': 'Finca reactivada correctamente',
                'status': 'success'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error reactivando finca {finca_id}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FincaStatsView(FincaPermissionMixin, APIView):
    """
    Vista para obtener estadísticas de una finca específica.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas detalladas de una finca",
        operation_summary="Estadísticas de finca",
        responses={
            200: openapi.Response(description="Estadísticas obtenidas exitosamente"),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Fincas']
    )
    def get(self, request, finca_id):
        """Obtener estadísticas de finca."""
        try:
            queryset = self.get_queryset()
            finca = queryset.get(id=finca_id)
            
            stats = finca.get_estadisticas()
            
            # Agregar estadísticas adicionales
            stats.update({
                'finca_nombre': finca.nombre,
                'agricultor_nombre': finca.agricultor.get_full_name(),
                'ubicacion_completa': finca.ubicacion_completa,
            })
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Finca.DoesNotExist:
            return Response({
                'error': ERROR_FINCA_NOT_FOUND,
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de finca {finca_id}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


