"""
Image views for CacaoScan API.
"""
import time
import logging
import os
import io
import csv
from pathlib import Path
from datetime import datetime, timedelta
from django.db import transaction
from django.db.models import Q, Count, Avg, Min, Max, Sum
from django.utils import timezone
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.utils.encoding import escape_uri_path
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from PIL import Image
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..views.mixins import PaginationMixin, AdminPermissionMixin
from ..serializers import (
    ScanMeasureResponseSerializer,
    ErrorResponseSerializer,
    CacaoImageSerializer,
    CacaoImageDetailSerializer
)
from ..utils.decorators import handle_api_errors
from ..services.analysis_service import AnalysisService

try:
    from images_app.models import CacaoImage, CacaoPrediction
except ImportError:
    CacaoImage = None
    CacaoPrediction = None

try:
    from django.contrib.auth.models import User
except ImportError:
    from django.contrib.auth import get_user_model
    User = get_user_model()

logger = logging.getLogger("cacaoscan.api.images")


class ImagePermissionMixin(AdminPermissionMixin):
    """
    Mixin para manejar permisos de acceso a imágenes.
    """
    
    def can_access_image(self, user, image):
        """
        Verificar si el usuario puede acceder a la imagen.
        
        Args:
            user: Usuario autenticado
            image: Objeto CacaoImage
            
        Returns:
            bool: True si puede acceder, False en caso contrario
        """
        # El propietario siempre puede acceder
        if image.user == user:
            return True
        
        # Los admins pueden acceder a cualquier imagen
        if self.is_admin_user(user):
            return True
        
        # Los analistas pueden acceder a imágenes de todos los usuarios
        if user.groups.filter(name='analyst').exists():
            return True
        
        return False
    
    def get_user_images_queryset(self, user):
        """
        Obtener queryset de imágenes según permisos del usuario.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            QuerySet: Queryset filtrado según permisos
        """
        if self.is_admin_user(user):
            # Admins pueden ver todas las imágenes
            return CacaoImage.objects.all().select_related('user')
        elif user.groups.filter(name='analyst').exists():
            # Analistas pueden ver todas las imágenes
            return CacaoImage.objects.all().select_related('user')
        else:
            # Agricultores solo ven sus propias imágenes
            return CacaoImage.objects.filter(user=user).select_related('user')


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
                    from ..email_service import send_email_notification
                    
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
        # Obtener imagen
        try:
            image = CacaoImage.objects.select_related('user', 'prediction').get(id=image_id)
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
            predictions = CacaoPrediction.objects.filter(image__user_id=request.user.id)
            
            # Calcular promedio de confidence manualmente ya que es una propiedad
            avg_confidence = 0
            if predictions.exists():
                confidences = []
                for pred in predictions:
                    confidences.append(float(pred.average_confidence))
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            avg_processing_time = predictions.aggregate(
                avg_time=Avg('processing_time_ms')
            )['avg_time'] or 0
            
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
            # Obtener imagen
            try:
                image = CacaoImage.objects.get(id=image_id)
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
            # Obtener imagen con predicción
            try:
                image = CacaoImage.objects.select_related('prediction').get(id=image_id)
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
            # Obtener imagen
            try:
                image = CacaoImage.objects.get(id=image_id)
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


class ImagesExportView(APIView, ImagePermissionMixin):
    """
    Endpoint para exportar resultados de predicciones a CSV.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Exporta los resultados de predicciones a formato CSV",
        operation_summary="Exportar resultados",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'format': openapi.Schema(type=openapi.TYPE_STRING, description="Formato de exportación: 'csv'"),
                'include_images': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Incluir información de imágenes"),
                'include_predictions': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Incluir predicciones"),
                'date_from': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha desde"),
                'date_to': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha hasta"),
                'region': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por región"),
                'finca': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por finca"),
                'processed_only': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Solo imágenes procesadas")
            }
        ),
        responses={
            200: openapi.Response(
                description="Archivo CSV generado exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def post(self, request):
        """
        Exporta los resultados de predicciones a CSV.
        """
        try:
            # Obtener parámetros de exportación
            export_format = request.data.get('format', 'csv').lower()
            include_images = request.data.get('include_images', True)
            include_predictions = request.data.get('include_predictions', True)
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            region = request.data.get('region')
            finca = request.data.get('finca')
            processed_only = request.data.get('processed_only', False)
            
            if export_format != 'csv':
                return Response({
                    'error': 'Formato de exportación no soportado. Solo se admite CSV',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Construir queryset base según permisos
            queryset = self.get_user_images_queryset(request.user)
            
            # Aplicar filtros
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
            
            if region:
                queryset = queryset.filter(region__icontains=region)
            
            if finca:
                queryset = queryset.filter(finca__icontains=finca)
            
            if processed_only:
                queryset = queryset.filter(processed=True)
            
            # Solo incluir imágenes con predicciones si se solicitan predicciones
            if include_predictions:
                queryset = queryset.filter(prediction__isnull=False)
            
            # Ordenar por fecha de creación
            queryset = queryset.order_by('-created_at')
            
            # Crear buffer de memoria
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Escribir encabezados
            headers = []
            if include_images:
                headers.extend([
                    'image_id', 'file_name', 'file_size_mb', 'finca', 'region', 
                    'lote_id', 'variedad', 'fecha_cosecha', 'notas', 'processed',
                    'created_at', 'user'
                ])
            
            if include_predictions:
                headers.extend([
                    'prediction_id', 'alto_mm', 'ancho_mm', 'grosor_mm', 'peso_g',
                    'confidence_alto', 'confidence_ancho', 'confidence_grosor', 
                    'confidence_peso', 'average_confidence', 'volume_cm3', 'density_g_cm3',
                    'processing_time_ms', 'model_version', 'device_used', 'prediction_created_at'
                ])
            
            writer.writerow(headers)
            
            # Escribir datos
            for image in queryset.select_related('user', 'prediction'):
                row = []
                
                if include_images:
                    row.extend([
                        image.id,
                        image.file_name or '',
                        image.file_size_mb or 0,
                        image.finca or '',
                        image.region or '',
                        image.lote_id or '',
                        image.variedad or '',
                        image.fecha_cosecha.isoformat() if image.fecha_cosecha else '',
                        image.notas or '',
                        image.processed,
                        image.created_at.isoformat(),
                        image.user.username
                    ])
                
                if include_predictions and hasattr(image, 'prediction') and image.prediction:
                    prediction = image.prediction
                    row.extend([
                        prediction.id,
                        float(prediction.alto_mm),
                        float(prediction.ancho_mm),
                        float(prediction.grosor_mm),
                        float(prediction.peso_g),
                        float(prediction.confidence_alto),
                        float(prediction.confidence_ancho),
                        float(prediction.confidence_grosor),
                        float(prediction.confidence_peso),
                        float(prediction.average_confidence),
                        float(prediction.volume_cm3),
                        float(prediction.density_g_cm3),
                        prediction.processing_time_ms,
                        prediction.model_version,
                        prediction.device_used,
                        prediction.created_at.isoformat()
                    ])
                elif include_predictions:
                    # Si se incluyen predicciones pero no hay predicción, llenar con vacíos
                    row.extend([''] * 16)
                
                writer.writerow(row)
            
            # Preparar respuesta
            output.seek(0)
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            
            # Generar nombre de archivo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cacao_predictions_export_{timestamp}.csv"
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            logger.info(f"Exportación CSV generada por usuario {request.user.username}. Registros: {queryset.count()}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando exportación CSV: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminImagesListView(PaginationMixin, AdminPermissionMixin, APIView):
    """
    Endpoint para listar todas las imágenes del sistema con filtros avanzados (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la lista completa de imágenes del sistema con filtros avanzados (solo admins)",
        operation_summary="Lista global de imágenes",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página (máximo 100)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('user_id', openapi.IN_QUERY, description="Filtrar por ID de usuario", type=openapi.TYPE_INTEGER),
            openapi.Parameter('username', openapi.IN_QUERY, description="Filtrar por nombre de usuario", type=openapi.TYPE_STRING),
            openapi.Parameter('region', openapi.IN_QUERY, description="Filtrar por región", type=openapi.TYPE_STRING),
            openapi.Parameter('finca', openapi.IN_QUERY, description="Filtrar por finca", type=openapi.TYPE_STRING),
            openapi.Parameter('processed', openapi.IN_QUERY, description="Filtrar por estado de procesamiento", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('has_prediction', openapi.IN_QUERY, description="Filtrar por existencia de predicción", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Buscar en notas y metadatos", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Fecha desde (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Fecha hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('model_version', openapi.IN_QUERY, description="Filtrar por versión del modelo", type=openapi.TYPE_STRING),
            openapi.Parameter('min_confidence', openapi.IN_QUERY, description="Confianza mínima", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_confidence', openapi.IN_QUERY, description="Confianza máxima", type=openapi.TYPE_NUMBER),
        ],
        responses={
            200: openapi.Response(
                description="Lista global de imágenes obtenida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING),
                        'filters_applied': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Admin Dataset']
    )
    def get(self, request):
        """
        Obtiene la lista completa de imágenes del sistema con filtros avanzados.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            # Obtener parámetros de consulta (paginación se maneja en el mixin)
            user_id = request.GET.get('user_id')
            username = request.GET.get('username')
            region = request.GET.get('region')
            finca = request.GET.get('finca')
            processed = request.GET.get('processed')
            has_prediction = request.GET.get('has_prediction')
            search = request.GET.get('search')
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')
            model_version = request.GET.get('model_version')
            min_confidence = request.GET.get('min_confidence')
            max_confidence = request.GET.get('max_confidence')
            
            # Construir queryset base con todas las imágenes
            queryset = CacaoImage.objects.all().select_related('user', 'prediction')
            
            # Aplicar filtros
            filters_applied = {}
            
            if user_id:
                queryset = queryset.filter(user_id=user_id)
                filters_applied['user_id'] = user_id
            
            if username:
                queryset = queryset.filter(user__username__icontains=username)
                filters_applied['username'] = username
            
            if region:
                queryset = queryset.filter(region__icontains=region)
                filters_applied['region'] = region
            
            if finca:
                queryset = queryset.filter(finca__icontains=finca)
                filters_applied['finca'] = finca
            
            if processed is not None:
                processed_bool = processed.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(processed=processed_bool)
                filters_applied['processed'] = processed_bool
            
            if has_prediction is not None:
                has_pred_bool = has_prediction.lower() in ['true', '1', 'yes']
                if has_pred_bool:
                    queryset = queryset.filter(prediction__isnull=False)
                else:
                    queryset = queryset.filter(prediction__isnull=True)
                filters_applied['has_prediction'] = has_pred_bool
            
            if search:
                queryset = queryset.filter(
                    Q(notas__icontains=search) |
                    Q(finca__icontains=search) |
                    Q(region__icontains=search) |
                    Q(lote_id__icontains=search) |
                    Q(variedad__icontains=search) |
                    Q(user__username__icontains=search)
                )
                filters_applied['search'] = search
            
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
                filters_applied['date_from'] = date_from
            
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
                filters_applied['date_to'] = date_to
            
            if model_version:
                queryset = queryset.filter(prediction__model_version=model_version)
                filters_applied['model_version'] = model_version
            
            if min_confidence is not None:
                queryset = queryset.filter(prediction__average_confidence__gte=min_confidence)
                filters_applied['min_confidence'] = float(min_confidence)
            
            if max_confidence is not None:
                queryset = queryset.filter(prediction__average_confidence__lte=max_confidence)
                filters_applied['max_confidence'] = float(max_confidence)
            
            # Ordenar por fecha de creación (más recientes primero)
            queryset = queryset.order_by('-created_at')
            
            # Paginar usando el mixin con datos extra
            return self.paginate_queryset(
                request,
                queryset,
                CacaoImageDetailSerializer,
                extra_data={'filters_applied': filters_applied}
            )
            
        except ValueError as e:
            return Response({
                'error': 'Parámetros de consulta inválidos',
                'status': 'error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error obteniendo lista global de imágenes: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminImageDetailView(AdminPermissionMixin, APIView):
    """
    Endpoint para obtener detalles completos de cualquier imagen del sistema (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los detalles completos de cualquier imagen del sistema (solo admins)",
        operation_summary="Detalles globales de imagen",
        responses={
            200: openapi.Response(
                description="Detalles de imagen obtenidos exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Admin Dataset']
    )
    def get(self, request, image_id):
        """
        Obtiene los detalles completos de cualquier imagen del sistema.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            # Obtener imagen con información completa
            try:
                image = CacaoImage.objects.select_related(
                    'user', 'prediction'
                ).prefetch_related(
                    'user__groups'
                ).get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Serializar imagen con predicción
            serializer = CacaoImageDetailSerializer(image, context={'request': request})
            image_data = serializer.data
            
            # Agregar información administrativa adicional
            image_data['admin_info'] = {
                'owner_info': {
                    'id': image.user.id,
                    'username': image.user.username,
                    'email': image.user.email,
                    'first_name': image.user.first_name,
                    'last_name': image.user.last_name,
                    'is_active': image.user.is_active,
                    'is_staff': image.user.is_staff,
                    'is_superuser': image.user.is_superuser,
                    'date_joined': image.user.date_joined.isoformat(),
                    'last_login': image.user.last_login.isoformat() if image.user.last_login else None,
                    'groups': [group.name for group in image.user.groups.all()]
                },
                'file_info': {
                    'file_path': image.image.path if image.image else None,
                    'file_exists': image.image and os.path.exists(image.image.path) if image.image else False,
                    'storage_backend': str(type(image.image.storage).__name__) if image.image else None
                },
                'processing_info': {
                    'processing_time_ms': image.prediction.processing_time_ms if hasattr(image, 'prediction') and image.prediction else None,
                    'model_version': image.prediction.model_version if hasattr(image, 'prediction') and image.prediction else None,
                    'device_used': image.prediction.device_used if hasattr(image, 'prediction') and image.prediction else None,
                    'crop_url': image.prediction.crop_url if hasattr(image, 'prediction') and image.prediction else None
                },
                'access_info': {
                    'accessed_by_admin': request.user.username,
                    'access_timestamp': timezone.now().isoformat(),
                    'admin_permissions': {
                        'can_edit': True,
                        'can_delete': True,
                        'can_download': True,
                        'can_view_owner_data': True
                    }
                }
            }
            
            return Response(image_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo detalles administrativos de imagen {image_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminImageUpdateView(AdminPermissionMixin, APIView):
    """
    Endpoint para actualizar cualquier imagen del sistema (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Actualiza cualquier imagen del sistema (solo admins)",
        operation_summary="Actualizar imagen global",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'finca': openapi.Schema(type=openapi.TYPE_STRING),
                'region': openapi.Schema(type=openapi.TYPE_STRING),
                'lote_id': openapi.Schema(type=openapi.TYPE_STRING),
                'variedad': openapi.Schema(type=openapi.TYPE_STRING),
                'fecha_cosecha': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'notas': openapi.Schema(type=openapi.TYPE_STRING),
                'processed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'admin_notes': openapi.Schema(type=openapi.TYPE_STRING, description="Notas administrativas")
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
        tags=['Admin Dataset']
    )
    def patch(self, request, image_id):
        """
        Actualiza cualquier imagen del sistema.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            # Obtener imagen
            try:
                image = CacaoImage.objects.get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Actualizar campos permitidos (incluyendo campos administrativos)
            allowed_fields = ['finca', 'region', 'lote_id', 'variedad', 'fecha_cosecha', 'notas', 'processed']
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
            
            # Agregar notas administrativas si se proporcionan
            admin_notes = request.data.get('admin_notes')
            if admin_notes:
                # Agregar timestamp y admin info a las notas administrativas
                admin_entry = f"\n[ADMIN {request.user.username} - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}]: {admin_notes}"
                if image.notas:
                    image.notas += admin_entry
                else:
                    image.notas = admin_entry.strip()
                updated_fields.append('admin_notes')
            
            # Guardar cambios
            image.save()
            
            # Serializar imagen actualizada
            serializer = CacaoImageDetailSerializer(image, context={'request': request})
            
            logger.info(f"Imagen {image_id} actualizada por admin {request.user.username}. Campos: {updated_fields}")
            
            return Response({
                'message': 'Imagen actualizada exitosamente por administrador',
                'updated_fields': updated_fields,
                'updated_by': request.user.username,
                'update_timestamp': timezone.now().isoformat(),
                'image': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error actualizando imagen {image_id} por admin: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminImageDeleteView(AdminPermissionMixin, APIView):
    """
    Endpoint para eliminar cualquier imagen del sistema (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Elimina cualquier imagen del sistema (solo admins)",
        operation_summary="Eliminar imagen global",
        responses={
            200: openapi.Response(
                description="Imagen eliminada exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'deleted_image': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'deleted_by': openapi.Schema(type=openapi.TYPE_STRING),
                        'deletion_timestamp': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Admin Dataset']
    )
    def delete(self, request, image_id):
        """
        Elimina cualquier imagen del sistema.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            # Obtener imagen con predicción
            try:
                image = CacaoImage.objects.select_related('user', 'prediction').get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Guardar información completa antes de eliminar
            image_data = {
                'id': image.id,
                'file_name': image.file_name,
                'file_size_mb': image.file_size_mb,
                'finca': image.finca,
                'region': image.region,
                'lote_id': image.lote_id,
                'variedad': image.variedad,
                'fecha_cosecha': image.fecha_cosecha.isoformat() if image.fecha_cosecha else None,
                'notas': image.notas,
                'processed': image.processed,
                'created_at': image.created_at.isoformat(),
                'owner': {
                    'id': image.user.id,
                    'username': image.user.username,
                    'email': image.user.email,
                    'first_name': image.user.first_name,
                    'last_name': image.user.last_name
                }
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
                    'device_used': image.prediction.device_used,
                    'processing_time_ms': image.prediction.processing_time_ms,
                    'created_at': image.prediction.created_at.isoformat()
                }
            
            # Eliminar imagen (esto también eliminará la predicción por CASCADE)
            image.delete()
            
            logger.info(f"Imagen {image_id} eliminada por admin {request.user.username}. Propietario: {image_data['owner']['username']}")
            
            return Response({
                'message': 'Imagen eliminada exitosamente por administrador',
                'deleted_image': image_data,
                'deleted_prediction': prediction_data,
                'deleted_by': request.user.username,
                'deletion_timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error eliminando imagen {image_id} por admin: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminBulkUpdateView(AdminPermissionMixin, APIView):
    """
    Endpoint para actualizaciones masivas de imágenes (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Realiza actualizaciones masivas en múltiples imágenes (solo admins)",
        operation_summary="Actualización masiva",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'image_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER), description="IDs de imágenes a actualizar"),
                'filters': openapi.Schema(type=openapi.TYPE_OBJECT, description="Filtros para seleccionar imágenes automáticamente"),
                'updates': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'finca': openapi.Schema(type=openapi.TYPE_STRING),
                        'region': openapi.Schema(type=openapi.TYPE_STRING),
                        'lote_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'variedad': openapi.Schema(type=openapi.TYPE_STRING),
                        'fecha_cosecha': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                        'notas': openapi.Schema(type=openapi.TYPE_STRING),
                        'processed': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                    }
                ),
                'admin_notes': openapi.Schema(type=openapi.TYPE_STRING, description="Notas administrativas para la operación masiva")
            }
        ),
        responses={
            200: openapi.Response(
                description="Actualización masiva completada",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Admin Dataset']
    )
    def post(self, request):
        """
        Realiza actualizaciones masivas en múltiples imágenes.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            # Obtener parámetros
            image_ids = request.data.get('image_ids', [])
            filters = request.data.get('filters', {})
            updates = request.data.get('updates', {})
            admin_notes = request.data.get('admin_notes', '')
            
            # Validar que se proporcionen actualizaciones
            if not updates:
                return Response({
                    'error': 'No se proporcionaron campos para actualizar',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Construir queryset base
            queryset = CacaoImage.objects.all()
            
            # Aplicar filtros si se proporcionan
            if filters:
                if 'user_id' in filters:
                    queryset = queryset.filter(user_id=filters['user_id'])
                if 'username' in filters:
                    queryset = queryset.filter(user__username__icontains=filters['username'])
                if 'region' in filters:
                    queryset = queryset.filter(region__icontains=filters['region'])
                if 'finca' in filters:
                    queryset = queryset.filter(finca__icontains=filters['finca'])
                if 'processed' in filters:
                    queryset = queryset.filter(processed=filters['processed'])
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__date__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__date__lte=filters['date_to'])
            
            # Si se proporcionan IDs específicos, filtrar por ellos
            if image_ids:
                queryset = queryset.filter(id__in=image_ids)
            
            # Validar que hay imágenes para actualizar
            total_images = queryset.count()
            if total_images == 0:
                return Response({
                    'error': 'No se encontraron imágenes que coincidan con los criterios',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar fecha_cosecha si se proporciona
            if 'fecha_cosecha' in updates and updates['fecha_cosecha']:
                try:
                    fecha_cosecha = datetime.strptime(updates['fecha_cosecha'], '%Y-%m-%d').date()
                    updates['fecha_cosecha'] = fecha_cosecha
                except ValueError:
                    return Response({
                        'error': 'Formato de fecha inválido. Use YYYY-MM-DD',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Campos permitidos para actualización masiva
            allowed_fields = ['finca', 'region', 'lote_id', 'variedad', 'fecha_cosecha', 'notas', 'processed']
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            # Agregar notas administrativas si se proporcionan
            if admin_notes:
                admin_entry = f"\n[BULK UPDATE {request.user.username} - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}]: {admin_notes}"
                if 'notas' in filtered_updates:
                    filtered_updates['notas'] += admin_entry
                else:
                    filtered_updates['notas'] = admin_entry.strip()
            
            # Realizar actualización masiva
            updated_count = queryset.update(**filtered_updates)
            
            # Obtener información de las imágenes actualizadas
            updated_images = queryset.values('id', 'file_name', 'user__username', 'finca', 'region')
            
            logger.info(f"Actualización masiva realizada por admin {request.user.username}. Imágenes actualizadas: {updated_count}")
            
            return Response({
                'message': 'Actualización masiva completada exitosamente',
                'updated_count': updated_count,
                'total_images_found': total_images,
                'updated_fields': list(filtered_updates.keys()),
                'updated_by': request.user.username,
                'update_timestamp': timezone.now().isoformat(),
                'updated_images_preview': list(updated_images[:10]),  # Solo primeras 10 para preview
                'filters_applied': filters,
                'admin_notes': admin_notes
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en actualización masiva por admin: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminDatasetStatsView(AdminPermissionMixin, APIView):
    """
    Endpoint para obtener estadísticas globales del dataset (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas globales detalladas del dataset (solo admins)",
        operation_summary="Estadísticas globales del dataset",
        responses={
            200: openapi.Response(
                description="Estadísticas globales obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
        },
        tags=['Admin Dataset']
    )
    def get(self, request):
        """
        Obtiene estadísticas globales detalladas del dataset.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            # Estadísticas generales del dataset
            total_images = CacaoImage.objects.count()
            processed_images = CacaoImage.objects.filter(processed=True).count()
            unprocessed_images = total_images - processed_images
            
            # Estadísticas por usuarios
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            users_with_images = User.objects.filter(cacao_images__isnull=False).distinct().count()
            
            # Estadísticas de predicciones
            total_predictions = CacaoPrediction.objects.count()
            
            # Estadísticas por fechas
            today = timezone.now().date()
            this_week = today - timedelta(days=7)
            this_month = today - timedelta(days=30)
            this_year = today - timedelta(days=365)
            
            images_this_week = CacaoImage.objects.filter(created_at__date__gte=this_week).count()
            images_this_month = CacaoImage.objects.filter(created_at__date__gte=this_month).count()
            images_this_year = CacaoImage.objects.filter(created_at__date__gte=this_year).count()
            
            # Estadísticas por región
            region_stats = CacaoImage.objects.values('region').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True)),
                unique_users=Count('user', distinct=True)
            ).order_by('-count')[:20]
            
            # Estadísticas por finca
            finca_stats = CacaoImage.objects.values('finca').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True)),
                unique_users=Count('user', distinct=True)
            ).order_by('-count')[:20]
            
            # Estadísticas por variedad
            variedad_stats = CacaoImage.objects.values('variedad').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True))
            ).order_by('-count')[:15]
            
            # Estadísticas de dimensiones y confianza
            avg_dimensions = CacaoPrediction.objects.aggregate(
                avg_alto=Avg('alto_mm'),
                avg_ancho=Avg('ancho_mm'),
                avg_grosor=Avg('grosor_mm'),
                avg_peso=Avg('peso_g'),
                avg_processing_time=Avg('processing_time_ms')
            )
            
            # Calcular confidence manualmente
            avg_confidence = 0
            min_confidence = 0
            max_confidence = 0
            if CacaoPrediction.objects.exists():
                confidences = []
                for pred in CacaoPrediction.objects.all():
                    conf = float(pred.average_confidence)
                    confidences.append(conf)
                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
                    min_confidence = min(confidences)
                    max_confidence = max(confidences)
            
            # Estadísticas por modelo
            model_stats = []
            for model in CacaoPrediction.objects.values_list('model_version', flat=True).distinct():
                predictions = CacaoPrediction.objects.filter(model_version=model)
                count = predictions.count()
                avg_time = predictions.aggregate(avg=Avg('processing_time_ms'))['avg'] or 0
                model_stats.append({
                    'model_version': model,
                    'count': count,
                    'avg_confidence': avg_confidence,
                    'avg_processing_time_ms': round(float(avg_time), 0)
                })
            model_stats.sort(key=lambda x: x['count'], reverse=True)
            
            # Estadísticas por dispositivo
            device_stats = CacaoPrediction.objects.values('device_used').annotate(
                count=Count('id'),
                avg_processing_time=Avg('processing_time_ms')
            ).order_by('-count')
            
            # Top usuarios por actividad
            top_users = User.objects.annotate(
                image_count=Count('api_cacao_images'),
                processed_count=Count('api_cacao_images', filter=Q(api_cacao_images__processed=True))
            ).order_by('-image_count')[:10]
            
            # Estadísticas de archivos
            total_file_size = CacaoImage.objects.aggregate(
                total_size=Sum('file_size')
            )['total_size'] or 0
            
            avg_file_size = CacaoImage.objects.aggregate(
                avg_size=Avg('file_size')
            )['avg_size'] or 0
            
            # Estadísticas de calidad de datos
            images_with_metadata = CacaoImage.objects.filter(
                Q(finca__isnull=False) & ~Q(finca='') |
                Q(region__isnull=False) & ~Q(region='') |
                Q(variedad__isnull=False) & ~Q(variedad='')
            ).count()
            
            # Preparar respuesta
            stats = {
                'dataset_overview': {
                    'total_images': total_images,
                    'processed_images': processed_images,
                    'unprocessed_images': unprocessed_images,
                    'processing_rate': round((processed_images / total_images * 100), 2) if total_images > 0 else 0,
                    'total_users': total_users,
                    'active_users': active_users,
                    'users_with_images': users_with_images,
                    'total_predictions': total_predictions
                },
                'temporal_stats': {
                    'this_week': images_this_week,
                    'this_month': images_this_month,
                    'this_year': images_this_year,
                    'daily_average_this_month': round(images_this_month / 30, 2),
                    'weekly_average_this_year': round(images_this_year / 52, 2)
                },
                'geographic_stats': {
                    'top_regions': list(region_stats),
                    'top_fincas': list(finca_stats),
                    'unique_regions': CacaoImage.objects.values('region').distinct().count(),
                    'unique_fincas': CacaoImage.objects.values('finca').distinct().count()
                },
                'variety_stats': {
                    'top_varieties': list(variedad_stats),
                    'unique_varieties': CacaoImage.objects.values('variedad').distinct().count()
                },
                'quality_stats': {
                    'average_dimensions': {
                        'alto_mm': round(float(avg_dimensions['avg_alto'] or 0), 2),
                        'ancho_mm': round(float(avg_dimensions['avg_ancho'] or 0), 2),
                        'grosor_mm': round(float(avg_dimensions['avg_grosor'] or 0), 2),
                        'peso_g': round(float(avg_dimensions['avg_peso'] or 0), 2)
                    },
                    'confidence_stats': {
                        'average': round(float(avg_confidence), 3),
                        'minimum': round(float(min_confidence), 3),
                        'maximum': round(float(max_confidence), 3)
                    },
                    'processing_stats': {
                        'average_time_ms': round(float(avg_dimensions['avg_processing_time'] or 0), 0)
                    }
                },
                'model_stats': {
                    'by_version': list(model_stats),
                    'by_device': list(device_stats)
                },
                'user_activity': {
                    'top_users': [
                        {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'image_count': user.image_count,
                            'processed_count': user.processed_count,
                            'processing_rate': round((user.processed_count / user.image_count * 100), 2) if user.image_count > 0 else 0
                        }
                        for user in top_users
                    ]
                },
                'storage_stats': {
                    'total_file_size_mb': round(total_file_size / (1024 * 1024), 2),
                    'average_file_size_mb': round(avg_file_size / (1024 * 1024), 2),
                    'images_with_metadata': images_with_metadata,
                    'metadata_completeness': round((images_with_metadata / total_images * 100), 2) if total_images > 0 else 0
                },
                'generated_at': timezone.now().isoformat(),
                'generated_by': request.user.username
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas globales del dataset: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

