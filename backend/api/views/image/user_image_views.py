"""
User image views for CacaoScan API.
"""
import logging
import os
from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.http import FileResponse, HttpResponseRedirect
from django.utils.encoding import escape_uri_path
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..mixins import PaginationMixin
from ...serializers import (
    ScanMeasureResponseSerializer,
    ErrorResponseSerializer,
    CacaoImageSerializer,
    CacaoImageDetailSerializer
)
from ...utils.decorators import handle_api_errors
from ...services.analysis_service import AnalysisService
from ...utils.model_imports import get_models_safely
from .mixins import ImagePermissionMixin

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage',
    'CacaoPrediction': 'images_app.models.CacaoPrediction'
})
CacaoImage = models['CacaoImage']
CacaoPrediction = models['CacaoPrediction']

try:
    from django.contrib.auth.models import User
except ImportError:
    from django.contrib.auth import get_user_model
    User = get_user_model()

logger = logging.getLogger("cacaoscan.api.images")


class ScanMeasureView(APIView):
    """
    Endpoint para medición de granos de cacao.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    @swagger_auto_schema(
        operation_description="Procesa una imagen de grano de cacao y devuelve predicciones de dimensiones y peso",
        operation_summary="Medir grano de cacao",
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="Imagen del grano de cacao (JPG, PNG, BMP)",
                type=openapi.TYPE_FILE,
                required=True
            ),
        ],
        responses={
            200: ScanMeasureResponseSerializer,
            400: ErrorResponseSerializer,
            413: ErrorResponseSerializer,
            503: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['Medición']
    )
    def post(self, request):
        """
        Procesa una imagen y devuelve mediciones del grano.
        
        Request:
            - multipart/form-data con campo 'image' (jpg/png/bmp)
            - Límite de tamaño: 8MB
        
        Response:
            - JSON con predicciones de dimensiones y peso
        """
        # Validar que existe el archivo
        if 'image' not in request.FILES:
            return Response({
                'error': 'Campo "image" requerido',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        
        # Usar servicio de análisis para procesar imagen completa
        analysis_service = AnalysisService()
        result = analysis_service.process_image_with_segmentation(image_file, request.user)
        
        if result.success:
            # Validar respuesta con serializer
            serializer = ScanMeasureResponseSerializer(data=result.data)
            if serializer.is_valid():
                # Enviar email de análisis completado (opcional, no crítico)
                try:
                    from ...email_service import send_email_notification
                    
                    response_data = result.data
                    avg_confidence = sum(response_data['confidences'].values()) / len(response_data['confidences'])
                    
                    if avg_confidence >= 0.8:
                        confidence_level = 'high'
                    elif avg_confidence >= 0.6:
                        confidence_level = 'medium'
                    else:
                        confidence_level = 'low'
                    
                    email_context = {
                        'user_name': request.user.get_full_name() or request.user.username,
                        'user_email': request.user.email,
                        'analysis_id': response_data.get('prediction_id', 'N/A'),
                        'confidence': round(avg_confidence * 100, 1),
                        'confidence_level': confidence_level,
                        'alto_mm': response_data['alto_mm'],
                        'ancho_mm': response_data['ancho_mm'],
                        'grosor_mm': response_data['grosor_mm'],
                        'peso_g': response_data['peso_g'],
                        'confidence_alto': round(response_data['confidences']['alto'] * 100, 1),
                        'confidence_ancho': round(response_data['confidences']['ancho'] * 100, 1),
                        'confidence_grosor': round(response_data['confidences']['grosor'] * 100, 1),
                        'confidence_peso': round(response_data['confidences']['peso'] * 100, 1),
                        'model_version': response_data.get('debug', {}).get('model_version', 'v1.0'),
                        'analysis_date': timezone.now().strftime('%d/%m/%Y %H:%M'),
                        'crop_url': response_data.get('crop_url'),
                        'defects_detected': []
                    }
                    
                    email_result = send_email_notification(
                        user_email=request.user.email,
                        notification_type='analysis_complete',
                        context=email_context
                    )
                    
                    if email_result.get('success'):
                        logger.info(f"Email de análisis completado enviado a {request.user.email}")
                    else:
                        logger.warning(f"Error enviando email de análisis: {email_result.get('error')}")
                except Exception as e:
                    logger.warning(f"Error en envío de email de análisis: {e}")
                
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                logger.error(f"Error de serialización: {serializer.errors}")
                return Response({
                    'error': 'Error interno de serialización',
                    'status': 'error',
                    'details': serializer.errors
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Mapear errores del servicio a códigos HTTP
            if result.error.error_code == 'validation_error':
                status_code = status.HTTP_400_BAD_REQUEST
                if 'file_size' in str(result.error.details.get('field', '')):
                    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            elif 'not_available' in result.error.message.lower() or 'no disponible' in result.error.message.lower():
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            return Response({
                'error': result.error.message,
                'status': 'error',
                'details': result.error.details
            }, status=status_code)


class ImagesListView(PaginationMixin, APIView, ImagePermissionMixin):
    """
    Endpoint para listar imágenes procesadas con paginación y filtros.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la lista de imágenes procesadas por el usuario con paginación y filtros",
        operation_summary="Lista de imágenes",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página (máximo 100)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('region', openapi.IN_QUERY, description="Filtrar por región", type=openapi.TYPE_STRING),
            openapi.Parameter('finca', openapi.IN_QUERY, description="Filtrar por finca", type=openapi.TYPE_STRING),
            openapi.Parameter('processed', openapi.IN_QUERY, description="Filtrar por estado de procesamiento", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Buscar en notas y metadatos", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Fecha desde (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Fecha hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Lista de imágenes obtenida exitosamente",
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
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    @handle_api_errors(
        error_message="Error obteniendo lista de imágenes",
        log_message="Error obteniendo lista de imágenes"
    )
    def get(self, request):
        """
        Obtiene la lista de imágenes procesadas con paginación y filtros.
        """
        # Obtener parámetros de consulta (paginación se maneja en el mixin)
        region = request.GET.get('region')
        finca = request.GET.get('finca')
        processed = request.GET.get('processed')
        search = request.GET.get('search')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        # Construir queryset base según permisos
        queryset = self.get_user_images_queryset(request.user)
        
        # Aplicar filtros
        if region:
            queryset = queryset.filter(region__icontains=region)
        
        if finca:
            queryset = queryset.filter(finca__icontains=finca)
        
        if processed is not None:
            processed_bool = processed.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(processed=processed_bool)
        
        if search:
            queryset = queryset.filter(
                Q(notas__icontains=search) |
                Q(finca__icontains=search) |
                Q(region__icontains=search) |
                Q(lote_id__icontains=search) |
                Q(variedad__icontains=search)
            )
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Ordenar por fecha de creación (más recientes primero)
        queryset = queryset.order_by('-created_at')
        
        # Paginar usando el mixin
        return self.paginate_queryset(
            request,
            queryset,
            CacaoImageSerializer
        )


class ImageDetailView(APIView, ImagePermissionMixin):
    """
    Endpoint para obtener detalles de una imagen específica con acceso por owner/admin.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los detalles completos de una imagen específica incluyendo predicción",
        operation_summary="Detalles de imagen",
        responses={
            200: openapi.Response(
                description="Detalles de imagen obtenidos exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    @handle_api_errors(
        error_message="Error obteniendo detalles de imagen",
        log_message="Error obteniendo detalles de imagen"
    )
    def get(self, request, image_id):
        """
        Obtiene los detalles completos de una imagen específica.
        Solo el propietario o un admin pueden acceder.
        """
        # Obtener imagen (optimizado con select_related y prefetch_related)
        try:
            image = CacaoImage.objects.select_related(
                'user',
                'finca',
                'finca__agricultor',
                'lote',
                'lote__finca',
                'lote__finca__agricultor'
            ).prefetch_related('prediction').get(id=image_id)
        except CacaoImage.DoesNotExist:
            return Response({
                'error': 'Imagen no encontrada',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar permisos de acceso
        if not self.can_access_image(request.user, image):
            return Response({
                'error': 'No tienes permisos para acceder a esta imagen',
                'status': 'error'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Serializar imagen con predicción
        serializer = CacaoImageDetailSerializer(image, context={'request': request})
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class ImagesStatsView(APIView, ImagePermissionMixin):
    """
    Endpoint para obtener estadísticas detalladas de imágenes procesadas.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas detalladas de imágenes procesadas por el usuario",
        operation_summary="Estadísticas de imágenes",
        responses={
            200: openapi.Response(
                description="Estadísticas obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            401: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def get(self, request):
        """
        Obtiene estadísticas detalladas de imágenes procesadas.
        """
        try:
            # Obtener queryset base según permisos
            user_images = self.get_user_images_queryset(request.user)
            
            # Estadísticas básicas
            total_images = user_images.count()
            processed_images = user_images.filter(processed=True).count()
            unprocessed_images = total_images - processed_images
            
            # Estadísticas por fecha
            today = timezone.now().date()
            this_week = today - timedelta(days=7)
            this_month = today - timedelta(days=30)
            
            processed_today = user_images.filter(
                created_at__date=today, 
                processed=True
            ).count()
            
            processed_this_week = user_images.filter(
                created_at__date__gte=this_week,
                processed=True
            ).count()
            
            processed_this_month = user_images.filter(
                created_at__date__gte=this_month,
                processed=True
            ).count()
            
            # Estadísticas de predicciones
            # Use SQL aggregation to calculate average_confidence
            # average_confidence = (confidence_alto + confidence_ancho + confidence_grosor + confidence_peso) / 4
            from django.db.models import F
            
            avg_confidence_expr = (
                F('confidence_alto') + F('confidence_ancho') + 
                F('confidence_grosor') + F('confidence_peso')
            ) / 4
            
            predictions = CacaoPrediction.objects.filter(image__user_id=request.user.id)
            
            prediction_stats = predictions.aggregate(
                avg_confidence=Avg(avg_confidence_expr),
                avg_time=Avg('processing_time_ms')
            )
            
            avg_confidence = float(prediction_stats.get('avg_confidence', 0) or 0)
            avg_processing_time = float(prediction_stats.get('avg_time', 0) or 0)
            
            # Estadísticas por región
            region_stats = user_images.values('region').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True))
            ).order_by('-count')
            
            # Estadísticas por finca
            finca_stats = user_images.values('finca').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True))
            ).order_by('-count')[:10]  # Top 10 fincas
            
            # Estadísticas de dimensiones promedio
            avg_dimensions = predictions.aggregate(
                avg_alto=Avg('alto_mm'),
                avg_ancho=Avg('ancho_mm'),
                avg_grosor=Avg('grosor_mm'),
                avg_peso=Avg('peso_g')
            )
            
            # Preparar respuesta
            stats = {
                'total_images': total_images,
                'processed_images': processed_images,
                'unprocessed_images': unprocessed_images,
                'processed_today': processed_today,
                'processed_this_week': processed_this_week,
                'processed_this_month': processed_this_month,
                'average_confidence': round(float(avg_confidence), 3),
                'average_processing_time_ms': round(float(avg_processing_time), 0),
                'region_stats': list(region_stats),
                'top_fincas': list(finca_stats),
                'average_dimensions': {
                    'alto_mm': round(float(avg_dimensions['avg_alto'] or 0), 2),
                    'ancho_mm': round(float(avg_dimensions['avg_ancho'] or 0), 2),
                    'grosor_mm': round(float(avg_dimensions['avg_grosor'] or 0), 2),
                    'peso_g': round(float(avg_dimensions['avg_peso'] or 0), 2)
                }
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.warning(f"[WARNING] Error obteniendo estadísticas de imágenes: {e}")
            # Retornar datos vacíos en lugar de 500
            return Response({
                'total_images': 0,
                'processed_images': 0,
                'unprocessed_images': 0,
                'processed_today': 0,
                'processed_this_week': 0,
                'processed_this_month': 0,
                'average_confidence': 0,
                'average_processing_time_ms': 0,
                'region_stats': [],
                'top_fincas': [],
                'average_dimensions': {
                    'alto_mm': 0,
                    'ancho_mm': 0,
                    'grosor_mm': 0,
                    'peso_g': 0
                }
            }, status=status.HTTP_200_OK)


class ImageUpdateView(APIView, ImagePermissionMixin):
    """
    Endpoint para actualizar metadatos de una imagen específica.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Actualiza los metadatos de una imagen específica",
        operation_summary="Actualizar imagen",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'finca': openapi.Schema(type=openapi.TYPE_STRING),
                'region': openapi.Schema(type=openapi.TYPE_STRING),
                'lote_id': openapi.Schema(type=openapi.TYPE_STRING),
                'variedad': openapi.Schema(type=openapi.TYPE_STRING),
                'fecha_cosecha': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'notas': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(
                description="Imagen actualizada exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def patch(self, request, image_id):
        """
        Actualiza los metadatos de una imagen específica.
        Solo el propietario o un admin pueden actualizar.
        """
        try:
            # Obtener imagen (optimizado)
            try:
                image = CacaoImage.objects.select_related(
                    'user',
                    'finca',
                    'finca__agricultor',
                    'lote',
                    'lote__finca',
                    'lote__finca__agricultor'
                ).prefetch_related('prediction').get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar permisos de acceso
            if not self.can_access_image(request.user, image):
                return Response({
                    'error': 'No tienes permisos para actualizar esta imagen',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Actualizar campos permitidos
            allowed_fields = ['finca', 'region', 'lote_id', 'variedad', 'fecha_cosecha', 'notas']
            updated_fields = []
            
            for field in allowed_fields:
                if field in request.data:
                    setattr(image, field, request.data[field])
                    updated_fields.append(field)
            
            # Validar fecha_cosecha si se proporciona
            if 'fecha_cosecha' in request.data and request.data['fecha_cosecha']:
                try:
                    fecha_cosecha = datetime.strptime(request.data['fecha_cosecha'], '%Y-%m-%d').date()
                    image.fecha_cosecha = fecha_cosecha
                except ValueError:
                    return Response({
                        'error': 'Formato de fecha inválido. Use YYYY-MM-DD',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Guardar cambios
            image.save()
            
            # Serializar imagen actualizada
            serializer = CacaoImageSerializer(image, context={'request': request})
            
            logger.info(f"Imagen {image_id} actualizada por usuario {request.user.username}. Campos: {updated_fields}")
            
            return Response({
                'message': 'Imagen actualizada exitosamente',
                'updated_fields': updated_fields,
                'image': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error actualizando imagen {image_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImageDeleteView(APIView, ImagePermissionMixin):
    """
    Endpoint para eliminar una imagen y su predicción asociada.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Elimina una imagen y su predicción asociada del sistema",
        operation_summary="Eliminar imagen",
        responses={
            200: openapi.Response(
                description="Imagen eliminada exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'deleted_image': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def delete(self, request, image_id):
        """
        Elimina una imagen y su predicción asociada.
        Solo el propietario o un admin pueden eliminar.
        """
        try:
            # Obtener imagen con predicción (optimizado)
            try:
                image = CacaoImage.objects.select_related(
                    'user',
                    'finca',
                    'finca__agricultor',
                    'lote',
                    'lote__finca',
                    'lote__finca__agricultor'
                ).prefetch_related('prediction').get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar permisos de acceso
            if not self.can_access_image(request.user, image):
                return Response({
                    'error': 'No tienes permisos para eliminar esta imagen',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Guardar información de la imagen antes de eliminarla
            image_data = {
                'id': image.id,
                'file_name': image.file_name,
                'file_size_mb': image.file_size_mb,
                'finca': image.finca,
                'region': image.region,
                'lote_id': image.lote_id,
                'variedad': image.variedad,
                'fecha_cosecha': image.fecha_cosecha.isoformat() if image.fecha_cosecha else None,
                'processed': image.processed,
                'created_at': image.created_at.isoformat(),
                'user': image.user.username
            }
            
            # Información de la predicción si existe
            prediction_data = None
            if hasattr(image, 'prediction') and image.prediction:
                prediction_data = {
                    'id': image.prediction.id,
                    'alto_mm': float(image.prediction.alto_mm),
                    'ancho_mm': float(image.prediction.ancho_mm),
                    'grosor_mm': float(image.prediction.grosor_mm),
                    'peso_g': float(image.prediction.peso_g),
                    'average_confidence': float(image.prediction.average_confidence),
                    'model_version': image.prediction.model_version,
                    'created_at': image.prediction.created_at.isoformat()
                }
            
            # Eliminar imagen (esto también eliminará la predicción por CASCADE)
            image.delete()
            
            logger.info(f"Imagen {image_id} eliminada por usuario {request.user.username}")
            
            return Response({
                'message': 'Imagen eliminada exitosamente',
                'deleted_image': image_data,
                'deleted_prediction': prediction_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error eliminando imagen {image_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImageDownloadView(APIView, ImagePermissionMixin):
    """
    Endpoint para descargar imágenes originales o procesadas.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Descarga una imagen original o procesada",
        operation_summary="Descargar imagen",
        manual_parameters=[
            openapi.Parameter('type', openapi.IN_QUERY, description="Tipo de imagen: 'original' o 'processed'", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Archivo de imagen descargado",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def get(self, request, image_id):
        """
        Descarga una imagen original o procesada.
        Solo el propietario o un admin pueden descargar.
        """
        try:
            # Obtener imagen (optimizado)
            try:
                image = CacaoImage.objects.select_related(
                    'user',
                    'finca',
                    'finca__agricultor',
                    'lote',
                    'lote__finca',
                    'lote__finca__agricultor'
                ).prefetch_related('prediction').get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar permisos de acceso
            if not self.can_access_image(request.user, image):
                return Response({
                    'error': 'No tienes permisos para descargar esta imagen',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener tipo de descarga
            download_type = request.GET.get('type', 'original').lower()
            
            if download_type == 'original':
                # Descargar imagen original
                if not image.image:
                    return Response({
                        'error': 'Imagen original no disponible',
                        'status': 'error'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                file_path = image.image.path
                file_name = image.file_name or f"image_{image_id}.jpg"
                
            elif download_type == 'processed':
                # Descargar imagen procesada (crop)
                if not hasattr(image, 'prediction') or not image.prediction:
                    return Response({
                        'error': 'No hay imagen procesada disponible para esta imagen',
                        'status': 'error'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                crop_url = image.prediction.crop_url
                if not crop_url:
                    return Response({
                        'error': 'URL de imagen procesada no disponible',
                        'status': 'error'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Para imágenes procesadas, redirigir a la URL del crop
                return HttpResponseRedirect(crop_url)
                
            else:
                return Response({
                    'error': 'Tipo de descarga inválido. Use "original" o "processed"',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que el archivo existe
            if not os.path.exists(file_path):
                return Response({
                    'error': 'Archivo de imagen no encontrado en el servidor',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Determinar content type
            if file_name.lower().endswith('.png'):
                content_type = 'image/png'
            elif file_name.lower().endswith('.jpg') or file_name.lower().endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file_name.lower().endswith('.bmp'):
                content_type = 'image/bmp'
            else:
                content_type = 'application/octet-stream'
            
            # Crear respuesta de archivo
            response = FileResponse(
                open(file_path, 'rb'),
                content_type=content_type,
                as_attachment=True,
                filename=escape_uri_path(file_name)
            )
            
            # Agregar headers adicionales
            response['Content-Disposition'] = f'attachment; filename="{escape_uri_path(file_name)}"'
            response['Content-Length'] = os.path.getsize(file_path)
            
            logger.info(f"Imagen {image_id} ({download_type}) descargada por usuario {request.user.username}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error descargando imagen {image_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

