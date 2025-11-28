"""
Admin image CRUD views for CacaoScan API.
"""
import logging
import os
from datetime import datetime
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.views.mixins import AdminPermissionMixin
from api.serializers import (
    ErrorResponseSerializer,
    CacaoImageDetailSerializer
)
from api.utils.model_imports import get_models_safely

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
                    'error': ERROR_IMAGE_NOT_FOUND,
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
                    'error': ERROR_INTERNAL_SERVER,
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
            
            # Obtener imagen (optimizado para evitar N+1 queries)
            try:
                image = CacaoImage.objects.select_related(
                    'user',
                    'finca',
                    'finca__agricultor',
                    'lote',
                    'lote__finca',
                    'lote__finca__agricultor'
                ).prefetch_related(
                    'prediction',
                    'user__groups'
                ).get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': ERROR_IMAGE_NOT_FOUND,
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
                    'error': ERROR_INTERNAL_SERVER,
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
                    'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

