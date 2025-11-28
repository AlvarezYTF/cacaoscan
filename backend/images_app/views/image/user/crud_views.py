"""
User image CRUD views for CacaoScan API.
"""
import logging
import os
from datetime import datetime
from django.http import FileResponse, HttpResponseRedirect
from django.utils.encoding import escape_uri_path
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers import (
    ErrorResponseSerializer,
    CacaoImageSerializer,
    CacaoImageDetailSerializer
)
from api.utils.decorators import handle_api_errors
from api.utils.model_imports import get_models_safely
from ..mixins import ImagePermissionMixin

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage',
    'CacaoPrediction': 'images_app.models.CacaoPrediction'
})
CacaoImage = models['CacaoImage']
CacaoPrediction = models['CacaoPrediction']

logger = logging.getLogger("cacaoscan.api.images")

# Error message constants
ERROR_IMAGE_NOT_FOUND = 'Imagen no encontrada'
ERROR_INTERNAL_SERVER = 'Error interno del servidor'


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
                'error': ERROR_IMAGE_NOT_FOUND,
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
                    'error': ERROR_IMAGE_NOT_FOUND,
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
                    'error': ERROR_INTERNAL_SERVER,
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
                    'error': ERROR_IMAGE_NOT_FOUND,
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
                    'error': ERROR_INTERNAL_SERVER,
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
                    'error': ERROR_IMAGE_NOT_FOUND,
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
                    'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

