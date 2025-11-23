"""
Admin image views for CacaoScan API.
"""
import logging
import os
from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg, Sum, F, Min, Max
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..mixins import PaginationMixin, AdminPermissionMixin
from ...serializers import (
    ErrorResponseSerializer,
    CacaoImageDetailSerializer
)
from ...utils.model_imports import get_models_safely

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
            # Optimizado: select_related para ForeignKeys, prefetch_related para OneToOne reverso
            queryset = CacaoImage.objects.all().select_related(
                'user',
                'finca',
                'finca__agricultor',
                'lote',
                'lote__finca',
                'lote__finca__agricultor'
            ).prefetch_related('prediction')
            
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
            
            # Calcular confidence usando agregaciones SQL
            # average_confidence = (confidence_alto + confidence_ancho + confidence_grosor + confidence_peso) / 4
            avg_confidence_expr = (
                F('confidence_alto') + F('confidence_ancho') + 
                F('confidence_grosor') + F('confidence_peso')
            ) / 4
            
            confidence_stats = CacaoPrediction.objects.aggregate(
                avg_confidence=Avg(avg_confidence_expr),
                min_confidence=Min(avg_confidence_expr),
                max_confidence=Max(avg_confidence_expr)
            )
            
            avg_confidence = float(confidence_stats.get('avg_confidence', 0) or 0)
            min_confidence = float(confidence_stats.get('min_confidence', 0) or 0)
            max_confidence = float(confidence_stats.get('max_confidence', 0) or 0)
            
            # Estadísticas por modelo usando agregaciones SQL
            model_stats = list(
                CacaoPrediction.objects.values('model_version').annotate(
                    count=Count('id'),
                    avg_confidence=Avg(avg_confidence_expr),
                    avg_processing_time=Avg('processing_time_ms')
                ).order_by('-count')
            )
            
            # Convertir a formato esperado
            model_stats = [
                {
                    'model_version': stat['model_version'],
                    'count': stat['count'],
                    'avg_confidence': round(float(stat['avg_confidence'] or 0), 3),
                    'avg_processing_time_ms': round(float(stat['avg_processing_time'] or 0), 0)
                }
                for stat in model_stats
            ]
            
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

