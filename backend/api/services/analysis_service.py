"""
Servicio de anÃ¡lisis para CacaoScan.
"""
import logging
import time
from typing import Dict, Any, Optional, List
from django.core.files.uploadedfile import UploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import io
import os

from .base import BaseService, ServiceResult, ValidationServiceError, PermissionServiceError
try:
    from images_app.models import CacaoImage, CacaoPrediction
except ImportError:
    CacaoImage = None
    CacaoPrediction = None

from django.contrib.auth.models import User
from ml.prediction.predict import get_predictor, load_artifacts

logger = logging.getLogger("cacaoscan.services.analysis")


class AnalysisService(BaseService):
    """
    Servicio para manejar anÃ¡lisis de granos de cacao.
    """
    
    def __init__(self):
        super().__init__()
        self.allowed_image_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp']
        self.max_file_size = 20 * 1024 * 1024  # 20MB
    
    def analyze_cacao_grain(self, image_file: UploadedFile, user: User) -> ServiceResult:
        """
        Analiza un grano de cacao desde una imagen.
        
        Args:
            image_file: Archivo de imagen subido
            user: Usuario que realiza el anÃ¡lisis
            
        Returns:
            ServiceResult con resultados del anÃ¡lisis
        """
        try:
            # Validar archivo
            validation_result = self._validate_image_file(image_file)
            if not validation_result.success:
                return validation_result
            
            start_time = time.time()
            
            # Guardar imagen
            save_result = self._save_uploaded_image(image_file, user)
            if not save_result.success:
                return save_result
            
            cacao_image = save_result.data
            
            # Cargar imagen para procesamiento
            image_data = image_file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Obtener predictor
            predictor_result = self._get_predictor()
            if not predictor_result.success:
                return predictor_result
            
            predictor = predictor_result.data
            
            # Realizar predicciÃ³n
            prediction_start = time.time()
            result = predictor.predict(image)
            prediction_time_ms = int((time.time() - prediction_start) * 1000)
            
            # Guardar predicciÃ³n
            prediction_result = self._save_prediction(cacao_image, result, prediction_time_ms)
            if not prediction_result.success:
                self.log_warning(f"Error guardando predicciÃ³n: {prediction_result.error.message}")
            
            cacao_prediction = prediction_result.data if prediction_result.success else None
            
            # Preparar respuesta
            response_data = {
                'alto_mm': result['alto_mm'],
                'ancho_mm': result['ancho_mm'],
                'grosor_mm': result['grosor_mm'],
                'peso_g': result['peso_g'],
                'confidences': result['confidences'],
                'crop_url': result['crop_url'],
                'debug': result['debug'],
                'image_id': cacao_image.id,
                'prediction_id': cacao_prediction.id if cacao_prediction else None,
                'saved_to_database': prediction_result.success
            }
            
            # Crear log de auditorÃ­a
            self.create_audit_log(
                user=user,
                action="analysis_performed",
                resource_type="cacao_analysis",
                resource_id=cacao_prediction.id if cacao_prediction else None,
                details={
                    'image_id': cacao_image.id,
                    'processing_time_ms': prediction_time_ms,
                    'confidence_scores': result['confidences']
                }
            )
            
            total_time = time.time() - start_time
            self.log_info(f"AnÃ¡lisis completado en {total_time:.2f}s para usuario {user.username}")
            
            return ServiceResult.success(
                data=response_data,
                message="AnÃ¡lisis completado exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error en anÃ¡lisis: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante el anÃ¡lisis", details={"original_error": str(e)})
            )
    
    def get_analysis_history(self, user: User, page: int = 1, page_size: int = 20, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Obtiene el historial de anÃ¡lisis de un usuario.
        
        Args:
            user: Usuario
            page: NÃºmero de pÃ¡gina
            page_size: TamaÃ±o de pÃ¡gina
            filters: Filtros adicionales
            
        Returns:
            ServiceResult con historial paginado
        """
        try:
            # Construir queryset
            queryset = CacaoPrediction.objects.filter(
                image__user=user
            ).select_related('image').order_by('-created_at')
            
            # Aplicar filtros
            if filters:
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
                if 'min_confidence' in filters:
                    queryset = queryset.filter(average_confidence__gte=filters['min_confidence'])
                if 'max_confidence' in filters:
                    queryset = queryset.filter(average_confidence__lte=filters['max_confidence'])
            
            # Paginar resultados
            paginated_data = self.paginate_results(queryset, page, page_size)
            
            # Formatear datos
            analyses = []
            for prediction in paginated_data['results']:
                analyses.append({
                    'id': prediction.id,
                    'image_id': prediction.image.id,
                    'alto_mm': prediction.alto_mm,
                    'ancho_mm': prediction.ancho_mm,
                    'grosor_mm': prediction.grosor_mm,
                    'peso_g': prediction.peso_g,
                    'average_confidence': prediction.average_confidence,
                    'processing_time_ms': prediction.processing_time_ms,
                    'created_at': prediction.created_at.isoformat(),
                    'image_url': prediction.image.image.url if prediction.image.image else None,
                    'crop_url': getattr(prediction, 'crop_url', None)
                })
            
            return ServiceResult.success(
                data={
                    'analyses': analyses,
                    'pagination': paginated_data['pagination']
                },
                message="Historial de anÃ¡lisis obtenido exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo historial: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo historial", details={"original_error": str(e)})
            )
    
    def get_analysis_details(self, analysis_id: int, user: User) -> ServiceResult:
        """
        Obtiene detalles de un anÃ¡lisis especÃ­fico.
        
        Args:
            analysis_id: ID del anÃ¡lisis
            user: Usuario
            
        Returns:
            ServiceResult con detalles del anÃ¡lisis
        """
        try:
            try:
                prediction = CacaoPrediction.objects.select_related('image').get(
                    id=analysis_id,
                    image__user=user
                )
            except CacaoPrediction.DoesNotExist:
                return ServiceResult.not_found_error("AnÃ¡lisis no encontrado")
            
            analysis_data = {
                'id': prediction.id,
                'image_id': prediction.image.id,
                'alto_mm': prediction.alto_mm,
                'ancho_mm': prediction.ancho_mm,
                'grosor_mm': prediction.grosor_mm,
                'peso_g': prediction.peso_g,
                'average_confidence': prediction.average_confidence,
                'processing_time_ms': prediction.processing_time_ms,
                'created_at': prediction.created_at.isoformat(),
                'updated_at': prediction.updated_at.isoformat(),
                'image': {
                    'id': prediction.image.id,
                    'file_name': prediction.image.file_name,
                    'file_size': prediction.image.file_size,
                    'file_type': prediction.image.file_type,
                    'image_url': prediction.image.image.url if prediction.image.image else None,
                    'processed': prediction.image.processed
                },
                'crop_url': getattr(prediction, 'crop_url', None),
                'debug_info': getattr(prediction, 'debug_info', {})
            }
            
            return ServiceResult.success(
                data=analysis_data,
                message="Detalles del anÃ¡lisis obtenidos exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo detalles: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo detalles", details={"original_error": str(e)})
            )
    
    def delete_analysis(self, analysis_id: int, user: User) -> ServiceResult:
        """
        Elimina un anÃ¡lisis.
        
        Args:
            analysis_id: ID del anÃ¡lisis
            user: Usuario
            
        Returns:
            ServiceResult con resultado de la eliminaciÃ³n
        """
        try:
            try:
                prediction = CacaoPrediction.objects.select_related('image').get(
                    id=analysis_id,
                    image__user=user
                )
            except CacaoPrediction.DoesNotExist:
                return ServiceResult.not_found_error("AnÃ¡lisis no encontrado")
            
            # Crear log de auditorÃ­a antes de eliminar
            self.create_audit_log(
                user=user,
                action="analysis_deleted",
                resource_type="cacao_analysis",
                resource_id=analysis_id,
                details={
                    'image_id': prediction.image.id,
                    'analysis_data': {
                        'alto_mm': prediction.alto_mm,
                        'ancho_mm': prediction.ancho_mm,
                        'grosor_mm': prediction.grosor_mm,
                        'peso_g': prediction.peso_g
                    }
                }
            )
            
            # Eliminar anÃ¡lisis
            prediction.delete()
            
            self.log_info(f"AnÃ¡lisis {analysis_id} eliminado por usuario {user.username}")
            
            return ServiceResult.success(
                message="AnÃ¡lisis eliminado exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error eliminando anÃ¡lisis: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno eliminando anÃ¡lisis", details={"original_error": str(e)})
            )
    
    def get_analysis_statistics(self, user: User, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Obtiene estadÃ­sticas de anÃ¡lisis de un usuario.
        
        Args:
            user: Usuario
            filters: Filtros adicionales
            
        Returns:
            ServiceResult con estadÃ­sticas
        """
        try:
            # Construir queryset base
            queryset = CacaoPrediction.objects.filter(image__user=user)
            
            # Aplicar filtros
            if filters:
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
            
            # Calcular estadÃ­sticas
            stats = {
                'total_analyses': queryset.count(),
                'average_dimensions': {
                    'alto_mm': float(queryset.aggregate(avg=Avg('alto_mm'))['avg'] or 0),
                    'ancho_mm': float(queryset.aggregate(avg=Avg('ancho_mm'))['avg'] or 0),
                    'grosor_mm': float(queryset.aggregate(avg=Avg('grosor_mm'))['avg'] or 0),
                    'peso_g': float(queryset.aggregate(avg=Avg('peso_g'))['avg'] or 0)
                },
                'average_confidence': float(queryset.aggregate(avg=Avg('average_confidence'))['avg'] or 0),
                'average_processing_time_ms': float(queryset.aggregate(avg=Avg('processing_time_ms'))['avg'] or 0),
                'confidence_distribution': {
                    'high': queryset.filter(average_confidence__gte=0.8).count(),
                    'medium': queryset.filter(average_confidence__gte=0.6, average_confidence__lt=0.8).count(),
                    'low': queryset.filter(average_confidence__lt=0.6).count()
                },
                'dimension_ranges': {
                    'alto_mm': {
                        'min': float(queryset.aggregate(min=Min('alto_mm'))['min'] or 0),
                        'max': float(queryset.aggregate(max=Max('alto_mm'))['max'] or 0)
                    },
                    'ancho_mm': {
                        'min': float(queryset.aggregate(min=Min('ancho_mm'))['min'] or 0),
                        'max': float(queryset.aggregate(max=Max('ancho_mm'))['max'] or 0)
                    },
                    'grosor_mm': {
                        'min': float(queryset.aggregate(min=Min('grosor_mm'))['min'] or 0),
                        'max': float(queryset.aggregate(max=Max('grosor_mm'))['max'] or 0)
                    },
                    'peso_g': {
                        'min': float(queryset.aggregate(min=Min('peso_g'))['min'] or 0),
                        'max': float(queryset.aggregate(max=Max('peso_g'))['max'] or 0)
                    }
                }
            }
            
            return ServiceResult.success(
                data=stats,
                message="EstadÃ­sticas obtenidas exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo estadÃ­sticas: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo estadÃ­sticas", details={"original_error": str(e)})
            )
    
    def _validate_image_file(self, image_file: UploadedFile) -> ServiceResult:
        """
        Valida un archivo de imagen.
        
        Args:
            image_file: Archivo de imagen
            
        Returns:
            ServiceResult con resultado de validaciÃ³n
        """
        try:
            # Validar tipo de archivo
            if image_file.content_type not in self.allowed_image_types:
                return ServiceResult.validation_error(
                    f"Tipo de archivo no vÃ¡lido. Tipos permitidos: {', '.join(self.allowed_image_types)}",
                    details={"field": "content_type", "allowed_types": self.allowed_image_types}
                )
            
            # Validar tamaÃ±o del archivo
            if image_file.size > self.max_file_size:
                return ServiceResult.validation_error(
                    f"Archivo demasiado grande. MÃ¡ximo {self.max_file_size // (1024*1024)}MB permitido",
                    details={"field": "file_size", "max_size": self.max_file_size, "actual_size": image_file.size}
                )
            
            # Validar que sea una imagen vÃ¡lida
            try:
                image_data = image_file.read()
                image_file.seek(0)  # Resetear posiciÃ³n del archivo
                Image.open(io.BytesIO(image_data))
            except Exception as e:
                return ServiceResult.validation_error(
                    "Archivo de imagen invÃ¡lido o corrupto",
                    details={"field": "image_validity", "error": str(e)}
                )
            
            return ServiceResult.success(message="Archivo de imagen vÃ¡lido")
            
        except Exception as e:
            self.log_error(f"Error validando imagen: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno validando imagen", details={"original_error": str(e)})
            )
    
    def _save_uploaded_image(self, image_file: UploadedFile, user: User) -> ServiceResult:
        """
        Guarda una imagen subida en el sistema.
        
        Args:
            image_file: Archivo de imagen
            user: Usuario
            
        Returns:
            ServiceResult con datos de la imagen guardada
        """
        try:
            cacao_image = CacaoImage(
                user=user,
                image=image_file,
                file_name=image_file.name,
                file_size=image_file.size,
                file_type=image_file.content_type,
                processed=False
            )
            
            cacao_image.save()
            
            self.log_info(f"Imagen guardada con ID {cacao_image.id} para usuario {user.username}")
            
            return ServiceResult.success(
                data=cacao_image,
                message="Imagen guardada exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error guardando imagen: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno guardando imagen", details={"original_error": str(e)})
            )
    
    def _save_prediction(self, cacao_image: CacaoImage, result: Dict[str, Any], processing_time_ms: int) -> ServiceResult:
        """
        Guarda una predicciÃ³n en la base de datos.
        
        Args:
            cacao_image: Imagen de cacao
            result: Resultado de la predicciÃ³n
            processing_time_ms: Tiempo de procesamiento en milisegundos
            
        Returns:
            ServiceResult con datos de la predicciÃ³n guardada
        """
        try:
            # Calcular confianza promedio
            confidences = result['confidences']
            avg_confidence = sum(confidences.values()) / len(confidences)
            
            prediction = CacaoPrediction(
                image=cacao_image,
                alto_mm=result['alto_mm'],
                ancho_mm=result['ancho_mm'],
                grosor_mm=result['grosor_mm'],
                peso_g=result['peso_g'],
                average_confidence=avg_confidence,
                processing_time_ms=processing_time_ms,
                crop_url=result.get('crop_url', ''),
                debug_info=result.get('debug', {})
            )
            
            prediction.save()
            
            # Marcar imagen como procesada
            cacao_image.processed = True
            cacao_image.save()
            
            self.log_info(f"PredicciÃ³n guardada con ID {prediction.id}")
            
            return ServiceResult.success(
                data=prediction,
                message="PredicciÃ³n guardada exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error guardando predicciÃ³n: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno guardando predicciÃ³n", details={"original_error": str(e)})
            )
    
    def _get_predictor(self) -> ServiceResult:
        """
        Obtiene el predictor de modelos.
        
        Returns:
            ServiceResult con predictor
        """
        try:
            predictor = get_predictor()
            
            if not predictor.models_loaded:
                # Intentar cargar modelos automÃ¡ticamente
                self.log_info("Modelos no cargados. Intentando carga automÃ¡tica...")
                success = load_artifacts()
                
                if not success:
                    return ServiceResult.error(
                        ValidationServiceError(
                            "Modelos no disponibles. Ejecutar inicializaciÃ³n automÃ¡tica primero.",
                            details={"suggestion": "POST /api/v1/auto-initialize/ para inicializar el sistema"}
                        )
                    )
                
                # Reintentar obtener predictor
                predictor = get_predictor()
                
                if not predictor.models_loaded:
                    return ServiceResult.error(
                        ValidationServiceError("Error cargando modelos despuÃ©s de intento automÃ¡tico.")
                    )
            
            return ServiceResult.success(
                data=predictor,
                message="Predictor obtenido exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo predictor: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo predictor", details={"original_error": str(e)})
            )


