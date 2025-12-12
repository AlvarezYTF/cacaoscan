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
from core.utils import create_error_response, create_success_response
from .mixins.finca_error_mixin import FincaErrorMixin, ERROR_INTERNAL_SERVER, ERROR_INVALID_INPUT, ERROR_FINCA_NOT_FOUND
from .mixins.finca_serializer_mixin import FincaSerializerMixin

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


class FincaPermissionMixin(FincaErrorMixin, FincaSerializerMixin, AdminPermissionMixin):
    """
    Mixin para permisos de fincas.
    Los agricultores solo pueden ver/editar sus propias fincas.
    Los administradores pueden ver/editar todas las fincas.
    """
    
    def get_queryset(self):
        """Obtener queryset filtrado por permisos (optimizado con select_related y prefetch_related)."""
        user = self.request.user
        
        base_queryset = Finca.objects.select_related('agricultor', 'municipio', 'municipio__departamento').prefetch_related('lotes')
        
        if self.is_admin_user(user):
            # Admin puede ver todas las fincas (activas e inactivas)
            return base_queryset
        else:
            # Agricultor ve sus fincas (activas e inactivas)
            # El filtro de activa se aplica en la vista si es necesario
            return base_queryset.filter(agricultor=user)
    
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
            # Obtener queryset base
            queryset = self.get_queryset()
            logger.info(f"Queryset inicial para usuario {request.user.username} (admin: {self.is_admin_user(request.user)}): {queryset.count()} fincas")
            
            # Optimización: obtener solo los campos necesarios
            # Incluir agricultor y municipio con select_related para evitar N+1 queries
            # El departamento se obtiene de municipio.departamento (3NF)
            queryset = queryset.select_related('municipio', 'municipio__departamento', 'agricultor')
            
            # Aplicar filtros
            search = request.GET.get('search', '').strip()
            if search:
                queryset = queryset.filter(
                    Q(nombre__icontains=search) |
                    Q(municipio__nombre__icontains=search) |
                    Q(municipio__departamento__nombre__icontains=search)
                )
            
            municipio = request.GET.get('municipio', '').strip()
            if municipio:
                queryset = queryset.filter(municipio__nombre__icontains=municipio)
            
            departamento = request.GET.get('departamento', '').strip()
            if departamento:
                queryset = queryset.filter(municipio__departamento__nombre__icontains=departamento)
            
            # Filtro por estado activo
            # Por defecto, agricultores solo ven fincas activas, pero pueden filtrar explícitamente
            activa = request.GET.get('activa')
            is_admin = self.is_admin_user(request.user)
            logger.info(f"Filtro activa: {activa}, is_admin: {is_admin}")
            
            if activa is not None:
                activa_bool = activa.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(activa=activa_bool)
                logger.info(f"Aplicando filtro explícito activa={activa_bool}: {queryset.count()} fincas")
            elif not is_admin:
                # Agricultores ven solo fincas activas por defecto
                queryset = queryset.filter(activa=True)
                logger.info(f"Aplicando filtro por defecto activa=True para agricultor: {queryset.count()} fincas")
            else:
                logger.info(f"Admin: sin filtro de activa, mostrando todas: {queryset.count()} fincas")
            
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
            logger.info(f"Antes de paginar: {queryset.count()} fincas en queryset")
            response = self.paginate_queryset(
                request,
                queryset,
                FincaListSerializer
            )
            logger.info(f"Respuesta paginada: {response.data.get('count', 0)} fincas totales, {len(response.data.get('results', []))} en esta página")
            return response
            
        except Exception as e:
            logger.error(f"Error listando fincas para usuario {request.user.username}: {e}", exc_info=True)
            return self.handle_finca_error(e, "listando fincas")
    
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
            
            # Obtener el agricultor desde request.data si está presente y es válido, sino usar request.user
            agricultor = request.user
            # Crear una copia mutable de request.data para modificar
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            
            if 'agricultor' in data:
                agricultor_id = data['agricultor']
                # Validar que el ID no sea vacío, None o cadena vacía
                if agricultor_id and str(agricultor_id).strip():
                    from django.contrib.auth.models import User
                    try:
                        agricultor_id_int = int(agricultor_id)
                        agricultor = User.objects.get(id=agricultor_id_int)
                    except (ValueError, TypeError):
                        return Response({
                            'error': 'ID de agricultor inválido',
                            'details': 'El ID de agricultor debe ser un número válido'
                        }, status=status.HTTP_400_BAD_REQUEST)
                    except User.DoesNotExist:
                        return Response({
                            'error': 'Agricultor no encontrado',
                            'details': 'El ID de agricultor proporcionado no existe'
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # Si agricultor_id está vacío o es None, eliminar del data y usar request.user
                    data.pop('agricultor', None)
            
            logger.info(f"Creando finca con datos: {data}, agricultor: {agricultor.id}")
            
            # Pasar el agricultor al contexto para que la validación del nombre use el agricultor correcto
            serializer = FincaSerializer(data=data, context={'request': request, 'agricultor': agricultor})
            
            if serializer.is_valid():
                # Si ya está el agricultor en request.data, usar el que vino en el serializer validado
                # sino, usar el agricultor extraído
                finca = serializer.save(agricultor=agricultor)
                
                logger.info(f"Finca '{finca.nombre}' creada por usuario {request.user.username} para agricultor {agricultor.id}")
                
                return self.create_finca_response(finca)
            else:
                logger.error(f"Errores de validación: {serializer.errors}")
                return self.handle_validation_error(serializer.errors)
                
        except Exception as e:
            logger.error(f"Error creando finca para usuario {request.user.username}: {e}")
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            return self.handle_finca_error(e, "creando finca")


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
        finca, error_response = self.get_finca_with_error_handling(finca_id)
        if error_response:
            return error_response
        
        return self.serialize_finca_response(finca, serializer_class=FincaDetailSerializer)


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
        finca, error_response = self.get_finca_with_error_handling(finca_id)
        if error_response:
            return error_response
        
        # Pasar el agricultor de la finca al contexto para validación correcta
        serializer = FincaSerializer(finca, data=request.data, context={'request': request, 'agricultor': finca.agricultor})
        
        if serializer.is_valid():
            finca = serializer.save()
            logger.info(f"Finca '{finca.nombre}' actualizada por usuario {request.user.username}")
            return self.update_finca_response(finca)
        else:
            return self.handle_validation_error(serializer.errors)
    
    def patch(self, request, finca_id):
        """Actualizar finca parcialmente."""
        finca, error_response = self.get_finca_with_error_handling(finca_id)
        if error_response:
            return error_response
        
        # Pasar el agricultor de la finca al contexto para validación correcta
        serializer = FincaSerializer(finca, data=request.data, partial=True, context={'request': request, 'agricultor': finca.agricultor})
        
        if serializer.is_valid():
            finca = serializer.save()
            logger.info(f"Finca '{finca.nombre}' actualizada parcialmente por usuario {request.user.username}")
            return self.update_finca_response(finca)
        else:
            return self.handle_validation_error(serializer.errors)


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
                return create_error_response(
                    message='La finca ya está desactivada',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            finca_nombre = finca.nombre
            # Soft delete: marcar como inactiva en lugar de eliminar
            finca.activa = False
            finca.save(update_fields=['activa'])
            
            logger.info(f"Finca '{finca_nombre}' desactivada (soft delete) por usuario {request.user.username}")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Finca.DoesNotExist:
            return self.handle_finca_not_found(finca_id)
        except Exception as e:
            return self.handle_finca_error(e, "desactivando finca", finca_id)


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
                return self.handle_finca_not_found(finca_id)
            
            if finca.activa:
                return create_error_response(
                    message='La finca ya está activa',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            finca_nombre = finca.nombre
            finca.activa = True
            finca.save(update_fields=['activa'])
            
            logger.info(f"Finca '{finca_nombre}' reactivada por admin {request.user.username}")
            
            return create_success_response(message='Finca reactivada correctamente')
            
        except Exception as e:
            return self.handle_finca_error(e, "reactivando finca", finca_id)


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
        finca, error_response = self.get_finca_with_error_handling(finca_id)
        if error_response:
            return error_response
        
        stats = finca.get_estadisticas()
        
        # Agregar estadísticas adicionales
        stats.update({
            'finca_nombre': finca.nombre,
            'agricultor_nombre': finca.agricultor.get_full_name(),
            'ubicacion_completa': finca.ubicacion_completa,
        })
        
        return Response(stats, status=status.HTTP_200_OK)


