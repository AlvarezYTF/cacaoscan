"""
Admin image bulk operations views for CacaoScan API.
"""
import logging
from typing import Optional
from datetime import datetime
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.views.mixins.admin_mixin import AdminPermissionMixin
from api.serializers import ErrorResponseSerializer
from api.utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'CacaoImage': 'images_app.models.CacaoImage',
})
CacaoImage = models['CacaoImage']

logger = logging.getLogger("cacaoscan.api.images")


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
    def _apply_filters(self, queryset, filters: dict):
        """Aplica los filtros al queryset."""
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
        return queryset
    
    def _validate_fecha_cosecha(self, updates: dict) -> Optional[Response]:
        """Valida y parsea la fecha de cosecha."""
        if 'fecha_cosecha' in updates and updates['fecha_cosecha']:
            try:
                fecha_cosecha = datetime.strptime(updates['fecha_cosecha'], '%Y-%m-%d').date()
                updates['fecha_cosecha'] = fecha_cosecha
            except ValueError:
                return Response({
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
        return None
    
    def _filter_allowed_fields(self, updates: dict) -> dict:
        """Filtra solo los campos permitidos para actualización."""
        allowed_fields = ['finca', 'region', 'lote_id', 'variedad', 'fecha_cosecha', 'notas', 'processed']
        return {k: v for k, v in updates.items() if k in allowed_fields}
    
    def _add_admin_notes(self, filtered_updates: dict, admin_notes: str, username: str):
        """Agrega notas administrativas a las actualizaciones."""
        if admin_notes:
            admin_entry = f"\n[BULK UPDATE {username} - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}]: {admin_notes}"
            if 'notas' in filtered_updates:
                filtered_updates['notas'] += admin_entry
            else:
                filtered_updates['notas'] = admin_entry.strip()
    
    def post(self, request):
        """
        Realiza actualizaciones masivas en múltiples imágenes.
        Solo accesible para administradores.
        """
        try:
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            image_ids = request.data.get('image_ids', [])
            filters = request.data.get('filters', {})
            updates = request.data.get('updates', {})
            admin_notes = request.data.get('admin_notes', '')
            
            if not updates:
                return Response({
                    'error': 'No se proporcionaron campos para actualizar',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            queryset = CacaoImage.objects.all()
            
            if filters:
                queryset = self._apply_filters(queryset, filters)
            
            if image_ids:
                queryset = queryset.filter(id__in=image_ids)
            
            total_images = queryset.count()
            if total_images == 0:
                return Response({
                    'error': 'No se encontraron imágenes que coincidan con los criterios',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            error_response = self._validate_fecha_cosecha(updates)
            if error_response:
                return error_response
            
            filtered_updates = self._filter_allowed_fields(updates)
            self._add_admin_notes(filtered_updates, admin_notes, request.user.username)
            
            updated_count = queryset.update(**filtered_updates)
            updated_images = queryset.values('id', 'file_name', 'user__username', 'finca', 'region')
            
            logger.info(f"Actualización masiva realizada por admin {request.user.username}. Imágenes actualizadas: {updated_count}")
            
            return Response({
                'message': 'Actualización masiva completada exitosamente',
                'updated_count': updated_count,
                'total_images_found': total_images,
                'updated_fields': list(filtered_updates.keys()),
                'updated_by': request.user.username,
                'update_timestamp': timezone.now().isoformat(),
                'updated_images_preview': list(updated_images[:10]),
                'filters_applied': filters,
                'admin_notes': admin_notes
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en actualización masiva por admin: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

