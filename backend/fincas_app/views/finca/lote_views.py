"""
Vistas para gestión de lotes en CacaoScan.
"""
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from django.core.paginator import Paginator
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.views.mixins import PaginationMixin, AdminPermissionMixin

from api.utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'Lote': 'fincas_app.models.Lote',
    'Finca': 'fincas_app.models.Finca'
})
Lote = models['Lote']
Finca = models['Finca']
from api.serializers import (
    LoteSerializer,
    LoteListSerializer,
    LoteDetailSerializer,
    LoteStatsSerializer,
    ErrorResponseSerializer,
    CacaoImageSerializer
)

logger = logging.getLogger("cacaoscan.api")

# Error message constants
ERROR_INTERNAL_SERVER = 'Error interno del servidor'
ERROR_INVALID_INPUT = 'Datos de entrada inválidos'
ERROR_LOTE_NOT_FOUND = 'Lote no encontrado'


def create_error_response(error_message: str, status_code: int) -> Response:
    """
    Crea una respuesta de error estandarizada.
    
    Args:
        error_message: Mensaje de error
        status_code: Código de estado HTTP
        
    Returns:
        Response con formato de error estándar
    """
    return Response({
        'error': error_message,
        'status': 'error'
    }, status=status_code)


def handle_exception(e: Exception, user: str, operation: str, lote_id: int = None) -> Response:
    """
    Maneja excepciones y retorna respuesta de error.
    
    Args:
        e: Excepción capturada
        user: Usuario que realizó la operación
        operation: Descripción de la operación
        lote_id: ID del lote (opcional)
        
    Returns:
        Response con error interno del servidor
    """
    lote_info = f"lote {lote_id}" if lote_id else "lote"
    logger.error(f"Error {operation} {lote_info} para usuario {user}: {e}")
    return create_error_response(ERROR_INTERNAL_SERVER, status.HTTP_500_INTERNAL_SERVER_ERROR)


class LotePermissionMixin(AdminPermissionMixin):
    """
    Mixin para permisos de lotes.
    Los agricultores solo pueden ver/editar lotes de sus fincas.
    Los administradores pueden ver/editar todos los lotes.
    """
    
    def get_queryset(self):
        """Obtener queryset filtrado por permisos."""
        user = self.request.user
        
        if self.is_admin_user(user):
            # Admin puede ver todos los lotes
            return Lote.objects.all().select_related(
                'finca', 
                'finca__agricultor',
                'variedad',
                'estado',
                'finca__municipio',
                'finca__municipio__departamento'
            ).prefetch_related('cacao_images')
        else:
            # Agricultor solo ve lotes de sus fincas
            return Lote.objects.filter(
                finca__agricultor=user
            ).select_related(
                'finca', 
                'finca__agricultor',
                'variedad',
                'estado',
                'finca__municipio',
                'finca__municipio__departamento'
            ).prefetch_related('cacao_images')
    
    def perform_create(self, serializer):
        """Validar que la finca pertenezca al usuario."""
        finca_id = self.request.data.get('finca')
        if finca_id:
            try:
                finca = Finca.objects.get(id=finca_id)
                if not self.is_admin_user(self.request.user):
                    if finca.agricultor != self.request.user:
                        raise ValueError("No tienes permisos para crear lotes en esta finca.")
                serializer.save()
            except Finca.DoesNotExist:
                raise ValueError("Finca no encontrada.")


class LoteListCreateView(PaginationMixin, LotePermissionMixin, APIView):
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
                # Variedad is now a ForeignKey to Parametro, filter by ID or nombre
                try:
                    variedad_id = int(variedad)
                    queryset = queryset.filter(variedad_id=variedad_id)
                except (ValueError, TypeError):
                    queryset = queryset.filter(variedad__nombre__icontains=variedad)
            
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
                    Q(nombre__icontains=search) |
                    Q(variedad__nombre__icontains=search) |
                    Q(finca__nombre__icontains=search)
                )
            
            # Paginar usando el mixin
            return self.paginate_queryset(
                request,
                queryset,
                LoteListSerializer
            )
            
        except Exception as e:
            return handle_exception(e, request.user.username, "listando lotes")
    
    @swagger_auto_schema(
        operation_description="Crea un nuevo lote para el usuario autenticado",
        operation_summary="Crear lote",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'finca': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID de la finca"),
                'identificador': openapi.Schema(type=openapi.TYPE_STRING, description="Identificador del lote (opcional)"),
                'nombre': openapi.Schema(type=openapi.TYPE_STRING, description="Nombre o descripción del bulto (opcional)"),
                'variedad': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del parámetro de variedad de cacao"),
                'peso_kg': openapi.Schema(type=openapi.TYPE_NUMBER, description="Peso del bulto en kilogramos"),
                'fecha_recepcion': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha de recepción del bulto"),
                'fecha_procesamiento': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha de procesamiento (opcional)"),
                'fecha_plantacion': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha de plantación (opcional)"),
                'fecha_cosecha': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha de cosecha (opcional)"),
                'estado': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del parámetro de estado del lote (opcional)"),
                'descripcion': openapi.Schema(type=openapi.TYPE_STRING, description="Descripción adicional (opcional)"),
                'activa': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Estado activo (opcional, default: true)"),
            },
            required=['finca', 'variedad', 'peso_kg', 'fecha_recepcion']
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
            import traceback
            
            # Preparar datos: mapear 'activa' a 'activo' si es necesario
            data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
            if 'activa' in data and 'activo' not in data:
                data['activo'] = data.pop('activa')
            
            # Validar que la finca existe y pertenece al usuario
            finca_id = data.get('finca')
            if not finca_id:
                return Response({
                    'error': 'La finca es requerida',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                finca = Finca.objects.get(id=finca_id)
                if not self.is_admin_user(request.user):
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
            
            logger.info(f"Creando lote con datos: {data}")
            
            serializer = LoteSerializer(
                data=data, 
                context={'request': request, 'finca': finca}
            )
            
            if serializer.is_valid():
                try:
                    lote = serializer.save()
                    
                    logger.info(f"Lote '{lote.identificador or lote.nombre}' creado por usuario {request.user.username}")
                    
                    # Devolver datos completos con formato estándar
                    response_serializer = LoteSerializer(lote, context={'request': request})
                    return Response({
                        'success': True,
                        'lote': response_serializer.data
                    }, status=status.HTTP_201_CREATED)
                except Exception as save_error:
                    logger.error(f"Error guardando lote: {save_error}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
                    return Response({
                        'error': 'Error al guardar el lote',
                        'details': str(save_error),
                        'status': 'error'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                logger.error(f"Errores de validación: {serializer.errors}")
                return Response({
                    'error': ERROR_INVALID_INPUT,
                    'details': serializer.errors,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Error creando lote: {e}")
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            return handle_exception(e, request.user.username, "creando")


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
    def get(self, request, lote_id=None, pk=None):
        """Obtener detalles de lote."""
        try:
            # Support both lote_id and pk parameters for URL compatibility
            lote_id = lote_id or pk
            if not lote_id:
                return create_error_response('ID de lote requerido', status.HTTP_400_BAD_REQUEST)
            
            queryset = self.get_queryset()
            lote = queryset.get(id=lote_id)
            
            serializer = LoteDetailSerializer(lote, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Lote.DoesNotExist:
            return create_error_response(ERROR_LOTE_NOT_FOUND, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e, request.user.username, "obteniendo detalles de", lote_id)


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
    def _update_lote(self, request, lote_id, partial: bool = False):
        """
        Método helper para actualizar un lote (completo o parcial).
        
        Args:
            request: Request HTTP
            lote_id: ID del lote a actualizar
            partial: Si es True, actualización parcial (PATCH), si es False, completa (PUT)
            
        Returns:
            Response con el lote actualizado o error
        """
        try:
            queryset = self.get_queryset()
            lote = queryset.get(id=lote_id)
            
            serializer = LoteSerializer(
                lote, 
                data=request.data, 
                partial=partial, 
                context={'request': request, 'finca': lote.finca}
            )
            
            if serializer.is_valid():
                lote = serializer.save()
                
                update_type = "parcialmente" if partial else ""
                logger.info(f"Lote '{lote.identificador}' actualizado {update_type} por usuario {request.user.username}")
                
                response_serializer = LoteSerializer(lote, context={'request': request})
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': ERROR_INVALID_INPUT,
                    'details': serializer.errors,
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Lote.DoesNotExist:
            return create_error_response(ERROR_LOTE_NOT_FOUND, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e, request.user.username, "actualizando", lote_id)
    
    def put(self, request, lote_id):
        """Actualizar lote completo."""
        return self._update_lote(request, lote_id, partial=False)
    
    def patch(self, request, lote_id):
        """Actualizar lote parcialmente."""
        return self._update_lote(request, lote_id, partial=True)


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
            return create_error_response(ERROR_LOTE_NOT_FOUND, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e, request.user.username, "eliminando", lote_id)


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
            return create_error_response(ERROR_LOTE_NOT_FOUND, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e, request.user.username, "obteniendo estadísticas de", lote_id)


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
            is_admin = self.is_admin_user(request.user)
            logger.info(f"Usuario {request.user.username} (admin: {is_admin}) solicitando lotes de finca {finca_id}")
            
            # Verificar que la finca existe y pertenece al usuario
            if is_admin:
                # Admin puede ver lotes de cualquier finca
                try:
                    finca = Finca.objects.get(id=finca_id)
                    logger.info(f"Admin accediendo a finca {finca_id}: {finca.nombre}")
                except Finca.DoesNotExist:
                    logger.warning(f"Admin intentó acceder a finca inexistente: {finca_id}")
                    return create_error_response('Finca no encontrada', status.HTTP_404_NOT_FOUND)
            else:
                # Agricultor solo puede ver lotes de sus fincas
                try:
                    finca = Finca.objects.get(id=finca_id, agricultor=request.user)
                    logger.info(f"Agricultor {request.user.username} accediendo a su finca {finca_id}: {finca.nombre}")
                except Finca.DoesNotExist:
                    logger.warning(f"Agricultor {request.user.username} intentó acceder a finca {finca_id} que no le pertenece")
                    return create_error_response(
                        'Finca no encontrada o no tienes permisos para acceder a esta finca', 
                        status.HTTP_404_NOT_FOUND
                    )
            
            lotes = Lote.objects.filter(finca=finca).select_related('finca', 'finca__agricultor')
            logger.info(f"Encontrados {lotes.count()} lotes para finca {finca_id}")
            
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
            logger.error(f"Finca {finca_id} no encontrada para usuario {request.user.username}")
            return create_error_response('Finca no encontrada', status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error obteniendo lotes de finca {finca_id} para usuario {request.user.username}: {e}", exc_info=True)
            return handle_exception(e, request.user.username, "obteniendo lotes de finca", finca_id)


class AnalisisSerializer(serializers.Serializer):
    """Serializer for análisis (images) in lote detail view."""
    id = serializers.IntegerField()
    fecha_analisis = serializers.DateTimeField(source='created_at')
    tipo_analisis = serializers.SerializerMethodField()
    calidad = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    prediction = serializers.SerializerMethodField()
    
    def get_tipo_analisis(self, obj):
        return 'Análisis de Imagen'
    
    def get_calidad(self, obj):
        if hasattr(obj, 'prediction') and obj.prediction:
            if obj.prediction.quality_score is not None:
                return float(obj.prediction.quality_score)
            # Calcular calidad basada en confianza promedio si no hay quality_score
            if hasattr(obj.prediction, 'average_confidence'):
                avg_conf = float(obj.prediction.average_confidence)
                return round(avg_conf * 100, 2)
        return 0
    
    def get_image_url(self, obj):
        """Get image URL."""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_prediction(self, obj):
        """Get prediction data if exists."""
        if hasattr(obj, 'prediction') and obj.prediction:
            pred = obj.prediction
            return {
                'id': pred.id,
                'alto_mm': float(pred.alto_mm) if pred.alto_mm else None,
                'ancho_mm': float(pred.ancho_mm) if pred.ancho_mm else None,
                'grosor_mm': float(pred.grosor_mm) if pred.grosor_mm else None,
                'peso_g': float(pred.peso_g) if pred.peso_g else None,
                'confidence_alto': float(pred.confidence_alto) if pred.confidence_alto else None,
                'confidence_ancho': float(pred.confidence_ancho) if pred.confidence_ancho else None,
                'confidence_grosor': float(pred.confidence_grosor) if pred.confidence_grosor else None,
                'confidence_peso': float(pred.confidence_peso) if pred.confidence_peso else None,
                'average_confidence': float(pred.average_confidence) if hasattr(pred, 'average_confidence') and pred.average_confidence else None,
                'processing_time_ms': pred.processing_time_ms,
                'crop_url': pred.crop_url if pred.crop_url else None,
                'model_version': str(pred.model_version) if pred.model_version else None,
                'device_used': str(pred.device_used) if pred.device_used else None,
                'created_at': pred.created_at.isoformat() if pred.created_at else None
            }
        return None
        return None


class LoteAnalisisView(PaginationMixin, LotePermissionMixin, APIView):
    """
    Vista para obtener los análisis (imágenes) de un lote específico.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los análisis (imágenes) de un lote específico con paginación",
        operation_summary="Análisis de lote",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página (máximo 100)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('processed', openapi.IN_QUERY, description="Filtrar por estado de procesamiento", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Fecha desde (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Fecha hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Análisis obtenidos exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING),
                        'page': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            404: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Lotes']
    )
    def get(self, request, lote_id):
        """
        Obtener análisis (imágenes) de un lote específico.
        """
        try:
            # Verificar que el lote existe y el usuario tiene permisos
            queryset = self.get_queryset()
            lote = queryset.get(id=lote_id)
            
            # Obtener imágenes del lote con predicciones (OneToOne relationship)
            images_queryset = lote.cacao_images.all().select_related(
                'user', 'lote', 'file_type', 'prediction'
            ).order_by('-created_at')
            
            # Aplicar filtros opcionales
            processed = request.GET.get('processed')
            if processed is not None:
                processed_bool = processed.lower() in ['true', '1', 'yes']
                images_queryset = images_queryset.filter(processed=processed_bool)
            
            date_from = request.GET.get('date_from')
            if date_from:
                images_queryset = images_queryset.filter(created_at__date__gte=date_from)
            
            date_to = request.GET.get('date_to')
            if date_to:
                images_queryset = images_queryset.filter(created_at__date__lte=date_to)
            
            # Paginar usando el mixin con serializer personalizado
            return self.paginate_queryset(
                request,
                images_queryset,
                AnalisisSerializer
            )
            
        except Lote.DoesNotExist:
            return create_error_response(ERROR_LOTE_NOT_FOUND, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return handle_exception(e, request.user.username, "obteniendo análisis de", lote_id)


