"""
Servicio de gestión de imágenes para CacaoScan.
"""
import logging
from typing import Dict, Any, Optional, List
from django.core.files.uploadedfile import UploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Q, Count, Avg, Min, Max
from PIL import Image
import io
import os

from .base import BaseService, ServiceResult, ValidationServiceError, PermissionServiceError, NotFoundServiceError
try:
    from images_app.models import CacaoImage
except ImportError:
    CacaoImage = None

from django.contrib.auth.models import User

logger = logging.getLogger("cacaoscan.services.images")


class ImageManagementService(BaseService):
    """
    Servicio para manejar gestión de imágenes de cacao.
    """
    
    def __init__(self):
        super().__init__()
        self.allowed_image_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp']
        self.max_file_size = 20 * 1024 * 1024  # 20MB
    
    def upload_image(self, image_file: UploadedFile, user: User, metadata: Dict[str, Any] = None) -> ServiceResult:
        """
        Sube una nueva imagen de cacao.
        
        Args:
            image_file: Archivo de imagen
            user: Usuario que sube la imagen
            metadata: Metadatos adicionales
            
        Returns:
            ServiceResult con datos de la imagen subida
        """
        try:
            # Validar archivo
            validation_result = self._validate_image_file(image_file)
            if not validation_result.success:
                return validation_result
            
            # Crear imagen
            cacao_image = CacaoImage(
                user=user,
                image=image_file,
                file_name=image_file.name,
                file_size=image_file.size,
                file_type=image_file.content_type,
                processed=False
            )
            
            # Agregar metadatos si se proporcionan
            if metadata:
                cacao_image.metadata = metadata
            
            cacao_image.save()
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="image_uploaded",
                resource_type="cacao_image",
                resource_id=cacao_image.id,
                details={
                    'file_name': image_file.name,
                    'file_size': image_file.size,
                    'file_type': image_file.content_type
                }
            )
            
            self.log_info(f"Imagen {cacao_image.id} subida por usuario {user.username}")
            
            return ServiceResult.success(
                data={
                    'id': cacao_image.id,
                    'file_name': cacao_image.file_name,
                    'file_size': cacao_image.file_size,
                    'file_type': cacao_image.file_type,
                    'processed': cacao_image.processed,
                    'created_at': cacao_image.created_at.isoformat(),
                    'image_url': cacao_image.image.url if cacao_image.image else None,
                    'metadata': cacao_image.metadata
                },
                message="Imagen subida exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error subiendo imagen: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno subiendo imagen", details={"original_error": str(e)})
            )
    
    def get_user_images(self, user: User, page: int = 1, page_size: int = 20, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Obtiene imágenes de un usuario.
        
        Args:
            user: Usuario
            page: Número de página
            page_size: Tamaño de página
            filters: Filtros adicionales
            
        Returns:
            ServiceResult con imágenes paginadas
        """
        try:
            # Construir queryset
            queryset = CacaoImage.objects.filter(user=user).order_by('-created_at')
            
            # Aplicar filtros
            if filters:
                if 'processed' in filters:
                    queryset = queryset.filter(processed=filters['processed'])
                if 'file_type' in filters:
                    queryset = queryset.filter(file_type=filters['file_type'])
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
                if 'search' in filters:
                    search_term = filters['search']
                    queryset = queryset.filter(
                        Q(file_name__icontains=search_term) |
                        Q(metadata__icontains=search_term)
                    )
            
            # Paginar resultados
            paginated_data = self.paginate_results(queryset, page, page_size)
            
            # Formatear datos
            images = []
            for image in paginated_data['results']:
                images.append({
                    'id': image.id,
                    'file_name': image.file_name,
                    'file_size': image.file_size,
                    'file_type': image.file_type,
                    'processed': image.processed,
                    'created_at': image.created_at.isoformat(),
                    'updated_at': image.updated_at.isoformat(),
                    'image_url': image.image.url if image.image else None,
                    'metadata': image.metadata
                })
            
            return ServiceResult.success(
                data={
                    'images': images,
                    'pagination': paginated_data['pagination']
                },
                message="Imágenes obtenidas exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo imágenes: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo imágenes", details={"original_error": str(e)})
            )
    
    def get_image_details(self, image_id: int, user: User) -> ServiceResult:
        """
        Obtiene detalles de una imagen específica.
        
        Args:
            image_id: ID de la imagen
            user: Usuario
            
        Returns:
            ServiceResult con detalles de la imagen
        """
        try:
            try:
                image = CacaoImage.objects.get(id=image_id, user=user)
            except CacaoImage.DoesNotExist:
                return ServiceResult.not_found_error("Imagen no encontrada")
            
            # Obtener predicciones asociadas
            predictions = image.predictions.all().order_by('-created_at')
            prediction_data = []
            
            for prediction in predictions:
                prediction_data.append({
                    'id': prediction.id,
                    'alto_mm': prediction.alto_mm,
                    'ancho_mm': prediction.ancho_mm,
                    'grosor_mm': prediction.grosor_mm,
                    'peso_g': prediction.peso_g,
                    'average_confidence': prediction.average_confidence,
                    'processing_time_ms': prediction.processing_time_ms,
                    'created_at': prediction.created_at.isoformat(),
                    'crop_url': getattr(prediction, 'crop_url', None)
                })
            
            image_data = {
                'id': image.id,
                'file_name': image.file_name,
                'file_size': image.file_size,
                'file_type': image.file_type,
                'processed': image.processed,
                'created_at': image.created_at.isoformat(),
                'updated_at': image.updated_at.isoformat(),
                'image_url': image.image.url if image.image else None,
                'metadata': image.metadata,
                'predictions': prediction_data,
                'predictions_count': len(prediction_data)
            }
            
            return ServiceResult.success(
                data=image_data,
                message="Detalles de imagen obtenidos exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo detalles: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo detalles", details={"original_error": str(e)})
            )
    
    def update_image_metadata(self, image_id: int, user: User, metadata: Dict[str, Any]) -> ServiceResult:
        """
        Actualiza metadatos de una imagen.
        
        Args:
            image_id: ID de la imagen
            user: Usuario
            metadata: Nuevos metadatos
            
        Returns:
            ServiceResult con imagen actualizada
        """
        try:
            try:
                image = CacaoImage.objects.get(id=image_id, user=user)
            except CacaoImage.DoesNotExist:
                return ServiceResult.not_found_error("Imagen no encontrada")
            
            # Actualizar metadatos
            old_metadata = image.metadata.copy() if image.metadata else {}
            image.metadata = metadata
            image.save()
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="image_metadata_updated",
                resource_type="cacao_image",
                resource_id=image_id,
                details={
                    'old_metadata': old_metadata,
                    'new_metadata': metadata
                }
            )
            
            self.log_info(f"Metadatos de imagen {image_id} actualizados por usuario {user.username}")
            
            return ServiceResult.success(
                data={
                    'id': image.id,
                    'file_name': image.file_name,
                    'metadata': image.metadata,
                    'updated_at': image.updated_at.isoformat()
                },
                message="Metadatos actualizados exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error actualizando metadatos: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno actualizando metadatos", details={"original_error": str(e)})
            )
    
    def delete_image(self, image_id: int, user: User) -> ServiceResult:
        """
        Elimina una imagen y sus predicciones asociadas.
        
        Args:
            image_id: ID de la imagen
            user: Usuario
            
        Returns:
            ServiceResult con resultado de la eliminación
        """
        try:
            try:
                image = CacaoImage.objects.get(id=image_id, user=user)
            except CacaoImage.DoesNotExist:
                return ServiceResult.not_found_error("Imagen no encontrada")
            
            # Obtener información para el log
            predictions_count = image.predictions.count()
            
            # Crear log de auditoría antes de eliminar
            self.create_audit_log(
                user=user,
                action="image_deleted",
                resource_type="cacao_image",
                resource_id=image_id,
                details={
                    'file_name': image.file_name,
                    'file_size': image.file_size,
                    'predictions_count': predictions_count
                }
            )
            
            # Eliminar imagen (esto también eliminará las predicciones por CASCADE)
            image.delete()
            
            self.log_info(f"Imagen {image_id} eliminada por usuario {user.username}")
            
            return ServiceResult.success(
                message="Imagen eliminada exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error eliminando imagen: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno eliminando imagen", details={"original_error": str(e)})
            )
    
    def get_image_statistics(self, user: User, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Obtiene estadísticas de imágenes de un usuario.
        
        Args:
            user: Usuario
            filters: Filtros adicionales
            
        Returns:
            ServiceResult con estadísticas
        """
        try:
            # Construir queryset base
            queryset = CacaoImage.objects.filter(user=user)
            
            # Aplicar filtros
            if filters:
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
            
            # Calcular estadísticas
            stats = {
                'total_images': queryset.count(),
                'processed_images': queryset.filter(processed=True).count(),
                'unprocessed_images': queryset.filter(processed=False).count(),
                'total_size_bytes': queryset.aggregate(total=Sum('file_size'))['total'] or 0,
                'average_size_bytes': queryset.aggregate(avg=Avg('file_size'))['avg'] or 0,
                'file_types': dict(queryset.values('file_type').annotate(count=Count('id')).values_list('file_type', 'count')),
                'processing_rate': 0,
                'size_distribution': {
                    'small': queryset.filter(file_size__lt=1024*1024).count(),  # < 1MB
                    'medium': queryset.filter(file_size__gte=1024*1024, file_size__lt=5*1024*1024).count(),  # 1-5MB
                    'large': queryset.filter(file_size__gte=5*1024*1024).count()  # > 5MB
                },
                'recent_uploads': queryset.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
            }
            
            # Calcular tasa de procesamiento
            if stats['total_images'] > 0:
                stats['processing_rate'] = stats['processed_images'] / stats['total_images']
            
            return ServiceResult.success(
                data=stats,
                message="Estadísticas obtenidas exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo estadísticas: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo estadísticas", details={"original_error": str(e)})
            )
    
    def bulk_delete_images(self, image_ids: List[int], user: User) -> ServiceResult:
        """
        Elimina múltiples imágenes.
        
        Args:
            image_ids: Lista de IDs de imágenes
            user: Usuario
            
        Returns:
            ServiceResult con resultado de la eliminación masiva
        """
        try:
            if not image_ids:
                return ServiceResult.validation_error("Lista de IDs de imágenes vacía")
            
            # Verificar que todas las imágenes pertenezcan al usuario
            images = CacaoImage.objects.filter(id__in=image_ids, user=user)
            
            if len(images) != len(image_ids):
                return ServiceResult.validation_error(
                    "Algunas imágenes no existen o no pertenecen al usuario",
                    details={"requested_count": len(image_ids), "found_count": len(images)}
                )
            
            # Crear log de auditoría
            self.create_audit_log(
                user=user,
                action="bulk_image_delete",
                resource_type="cacao_image",
                resource_id=None,
                details={
                    'image_ids': image_ids,
                    'count': len(image_ids)
                }
            )
            
            # Eliminar imágenes
            deleted_count = images.count()
            images.delete()
            
            self.log_info(f"{deleted_count} imágenes eliminadas por usuario {user.username}")
            
            return ServiceResult.success(
                data={'deleted_count': deleted_count},
                message=f"{deleted_count} imágenes eliminadas exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error eliminando imágenes masivamente: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno eliminando imágenes", details={"original_error": str(e)})
            )
    
    def _validate_image_file(self, image_file: UploadedFile) -> ServiceResult:
        """
        Valida un archivo de imagen.
        
        Args:
            image_file: Archivo de imagen
            
        Returns:
            ServiceResult con resultado de validación
        """
        try:
            # Validar tipo de archivo
            if image_file.content_type not in self.allowed_image_types:
                return ServiceResult.validation_error(
                    f"Tipo de archivo no válido. Tipos permitidos: {', '.join(self.allowed_image_types)}",
                    details={"field": "content_type", "allowed_types": self.allowed_image_types}
                )
            
            # Validar tamaño del archivo
            if image_file.size > self.max_file_size:
                return ServiceResult.validation_error(
                    f"Archivo demasiado grande. Máximo {self.max_file_size // (1024*1024)}MB permitido",
                    details={"field": "file_size", "max_size": self.max_file_size, "actual_size": image_file.size}
                )
            
            # Validar que sea una imagen válida
            try:
                image_data = image_file.read()
                image_file.seek(0)  # Resetear posición del archivo
                Image.open(io.BytesIO(image_data))
            except Exception as e:
                return ServiceResult.validation_error(
                    "Archivo de imagen inválido o corrupto",
                    details={"field": "image_validity", "error": str(e)}
                )
            
            return ServiceResult.success(message="Archivo de imagen válido")
            
        except Exception as e:
            self.log_error(f"Error validando imagen: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno validando imagen", details={"original_error": str(e)})
            )
