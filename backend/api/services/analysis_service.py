"""
Servicio de análisis para CacaoScan.
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

try:
    from ml.data.dataset_loader import CacaoDatasetLoader
except ImportError:
    CacaoDatasetLoader = None

logger = logging.getLogger("cacaoscan.services.analysis")


class AnalysisService(BaseService):
    """
    Servicio para manejar análisis de granos de cacao.
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
            user: Usuario que realiza el análisis
            
        Returns:
            ServiceResult con resultados del análisis
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
            
            # Realizar predicción
            prediction_start = time.time()
            result = predictor.predict(image)
            prediction_time_ms = int((time.time() - prediction_start) * 1000)
            
            # Guardar predicción
            prediction_result = self._save_prediction(cacao_image, result, prediction_time_ms)
            if not prediction_result.success:
                self.log_warning(f"Error guardando predicción: {prediction_result.error.message}")
            
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
            
            # Crear log de auditoría
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
            self.log_info(f"Análisis completado en {total_time:.2f}s para usuario {user.username}")
            
            return ServiceResult.success(
                data=response_data,
                message="Análisis completado exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error en análisis: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante el análisis", details={"original_error": str(e)})
            )
    
    def get_analysis_history(self, user: User, page: int = 1, page_size: int = 20, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Obtiene el historial de análisis de un usuario.
        
        Args:
            user: Usuario
            page: Número de página
            page_size: Tamaño de página
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
                message="Historial de análisis obtenido exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo historial: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo historial", details={"original_error": str(e)})
            )
    
    def get_analysis_details(self, analysis_id: int, user: User) -> ServiceResult:
        """
        Obtiene detalles de un análisis específico.
        
        Args:
            analysis_id: ID del análisis
            user: Usuario
            
        Returns:
            ServiceResult con detalles del análisis
        """
        try:
            try:
                prediction = CacaoPrediction.objects.select_related('image').get(
                    id=analysis_id,
                    image__user=user
                )
            except CacaoPrediction.DoesNotExist:
                return ServiceResult.not_found_error("Análisis no encontrado")
            
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
                message="Detalles del análisis obtenidos exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo detalles: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo detalles", details={"original_error": str(e)})
            )
    
    def delete_analysis(self, analysis_id: int, user: User) -> ServiceResult:
        """
        Elimina un análisis.
        
        Args:
            analysis_id: ID del análisis
            user: Usuario
            
        Returns:
            ServiceResult con resultado de la eliminación
        """
        try:
            try:
                prediction = CacaoPrediction.objects.select_related('image').get(
                    id=analysis_id,
                    image__user=user
                )
            except CacaoPrediction.DoesNotExist:
                return ServiceResult.not_found_error("Análisis no encontrado")
            
            # Crear log de auditoría antes de eliminar
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
            
            # Eliminar análisis
            prediction.delete()
            
            self.log_info(f"Análisis {analysis_id} eliminado por usuario {user.username}")
            
            return ServiceResult.success(
                message="Análisis eliminado exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error eliminando análisis: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno eliminando análisis", details={"original_error": str(e)})
            )
    
    def get_analysis_statistics(self, user: User, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Obtiene estadísticas de análisis de un usuario.
        
        Args:
            user: Usuario
            filters: Filtros adicionales
            
        Returns:
            ServiceResult con estadísticas
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
            
            # Calcular estadísticas
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
                message="Estadísticas obtenidas exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo estadísticas: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo estadísticas", details={"original_error": str(e)})
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
        Guarda una predicción en la base de datos.
        
        Args:
            cacao_image: Imagen de cacao
            result: Resultado de la predicción
            processing_time_ms: Tiempo de procesamiento en milisegundos
            
        Returns:
            ServiceResult con datos de la predicción guardada
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
            
            self.log_info(f"Predicción guardada con ID {prediction.id}")
            
            return ServiceResult.success(
                data=prediction,
                message="Predicción guardada exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error guardando predicción: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno guardando predicción", details={"original_error": str(e)})
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
                # Intentar cargar modelos automáticamente
                self.log_info("Modelos no cargados. Intentando carga automática...")
                success = load_artifacts()
                
                if not success:
                    return ServiceResult.error(
                        ValidationServiceError(
                            "Modelos no disponibles. Ejecutar inicialización automática primero.",
                            details={"suggestion": "POST /api/v1/auto-initialize/ para inicializar el sistema"}
                        )
                    )
                
                # Reintentar obtener predictor
                predictor = get_predictor()
                
                if not predictor.models_loaded:
                    return ServiceResult.error(
                        ValidationServiceError("Error cargando modelos después de intento automático.")
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
    
    def process_image_with_segmentation(self, image_file: UploadedFile, user: User) -> ServiceResult:
        """
        Procesa una imagen completa: validación, guardado, segmentación y predicción.
        
        Args:
            image_file: Archivo de imagen subido
            user: Usuario que realiza el análisis
            
        Returns:
            ServiceResult con resultados completos del análisis
        """
        try:
            start_time = time.time()
            
            # 1. Validar archivo
            validation_result = self._validate_image_file_complete(image_file)
            if not validation_result.success:
                return validation_result
            
            # 2. Guardar imagen en BD
            save_result = self._save_uploaded_image_with_segmentation(image_file, user)
            if not save_result.success:
                return save_result
            
            cacao_image = save_result.data['cacao_image']
            processed_png_path = save_result.data.get('processed_png_path')
            
            # 3. Cargar imagen para predicción
            image_data = image_file.read()
            image_file.seek(0)  # Resetear posición
            image = Image.open(io.BytesIO(image_data))
            
            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 4. Obtener predictor
            predictor_result = self._get_predictor()
            if not predictor_result.success:
                return predictor_result
            
            predictor = predictor_result.data
            
            # 5. Realizar predicción
            prediction_start = time.time()
            result = predictor.predict(image)
            prediction_time_ms = int((time.time() - prediction_start) * 1000)
            
            # 6. Guardar predicción
            prediction_result = self._save_prediction(cacao_image, result, prediction_time_ms)
            if not prediction_result.success:
                self.log_warning(f"Error guardando predicción: {prediction_result.error.message}")
            
            cacao_prediction = prediction_result.data if prediction_result.success else None
            
            # 7. Preparar respuesta
            response_data = {
                'alto_mm': result['alto_mm'],
                'ancho_mm': result['ancho_mm'],
                'grosor_mm': result['grosor_mm'],
                'peso_g': result['peso_g'],
                'confidences': result['confidences'],
                'crop_url': result.get('crop_url'),
                'debug': result.get('debug', {}),
                'image_id': cacao_image.id,
                'prediction_id': cacao_prediction.id if cacao_prediction else None,
                'saved_to_database': prediction_result.success,
                'processed_png_path': str(processed_png_path) if processed_png_path else None
            }
            
            # 8. Crear log de auditoría
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
            self.log_info(f"Análisis completado en {total_time:.2f}s para usuario {user.username}")
            
            return ServiceResult.success(
                data=response_data,
                message="Análisis completado exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error en procesamiento completo: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante el procesamiento", details={"original_error": str(e)})
            )
    
    def _validate_image_file_complete(self, image_file: UploadedFile) -> ServiceResult:
        """
        Valida un archivo de imagen de forma completa (tipo, tamaño, dimensiones).
        
        Args:
            image_file: Archivo de imagen
            
        Returns:
            ServiceResult con resultado de validación
        """
        try:
            # Validar tipo de archivo
            if image_file.content_type not in self.allowed_image_types:
                return ServiceResult.validation_error(
                    f"Tipo de archivo no permitido. Tipos válidos: {', '.join(self.allowed_image_types)}",
                    details={"field": "content_type", "allowed_types": self.allowed_image_types}
                )
            
            # Validar tamaño del archivo (8MB máximo para análisis)
            max_size = 8 * 1024 * 1024  # 8MB
            if image_file.size > max_size:
                return ServiceResult.validation_error(
                    f"Imagen demasiado grande. Máximo permitido: 8MB",
                    details={"field": "file_size", "max_size": max_size, "actual_size": image_file.size}
                )
            
            # Validar nombre de archivo
            filename = image_file.name
            if not filename or len(filename) > 255:
                return ServiceResult.validation_error(
                    "Nombre de archivo inválido",
                    details={"field": "filename"}
                )
            
            # Validar que sea una imagen válida y obtener dimensiones
            try:
                image_data = image_file.read()
                image_file.seek(0)  # Resetear posición
                image = Image.open(io.BytesIO(image_data))
                
                # Convertir a RGB si es necesario
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Validar dimensiones mínimas
                if image.width < 50 or image.height < 50:
                    return ServiceResult.validation_error(
                        "Imagen demasiado pequeña. Mínimo: 50x50 píxeles",
                        details={"field": "image_dimensions", "min_width": 50, "min_height": 50,
                                "actual_width": image.width, "actual_height": image.height}
                    )
                
            except Exception as e:
                return ServiceResult.validation_error(
                    f"Error procesando imagen: {str(e)}",
                    details={"field": "image_validity", "error": str(e)}
                )
            
            return ServiceResult.success(message="Archivo de imagen válido")
            
        except Exception as e:
            self.log_error(f"Error validando imagen: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno validando imagen", details={"original_error": str(e)})
            )
    
    def _save_uploaded_image_with_segmentation(self, image_file: UploadedFile, user: User) -> ServiceResult:
        """
        Guarda una imagen subida y realiza segmentación del grano.
        
        Args:
            image_file: Archivo de imagen
            user: Usuario
            
        Returns:
            ServiceResult con datos de la imagen guardada y ruta del PNG segmentado
        """
        try:
            from pathlib import Path
            from ml.segmentation.processor import segment_and_crop_cacao_bean
            
            # Crear imagen
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
            
            # Segmentar y guardar PNG transparente del grano
            processed_png_path = None
            try:
                generated_path = segment_and_crop_cacao_bean(str(cacao_image.image.path), method="opencv")
                if generated_path:
                    processed_png_path = Path(generated_path)
                    self.log_info(f"PNG segmentado guardado en: {processed_png_path.absolute()}")
                else:
                    self.log_warning(f"No se pudo segmentar imagen {cacao_image.id}: retorno vacío")
            except Exception as seg_error:
                self.log_error(f"Error en segmentación de imagen {cacao_image.id}: {seg_error}")
            
            return ServiceResult.success(
                data={
                    'cacao_image': cacao_image,
                    'processed_png_path': processed_png_path
                },
                message="Imagen guardada y segmentada exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error guardando imagen: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno guardando imagen", details={"original_error": str(e)})
            )
    
    def initialize_ml_system(self) -> ServiceResult:
        """
        Inicializa automáticamente el sistema ML completo.
        
        Pasos:
        1. Validar dataset
        2. Generar crops (si no existen)
        3. Entrenar modelos (si no existen)
        4. Cargar modelos
        5. Sistema listo para predicciones
        
        Returns:
            ServiceResult con resultado de la inicialización
        """
        try:
            import time
            from pathlib import Path
            
            start_time = time.time()
            steps_completed = []
            
            self.log_info("[INICIO] Iniciando inicialización automática completa del sistema")
            
            # Paso 1: Validar dataset
            self.log_info("Paso 1: Validando dataset...")
            if CacaoDatasetLoader is None:
                return ServiceResult.error(
                    ValidationServiceError("Cargador de dataset no disponible")
                )
            
            try:
                loader = CacaoDatasetLoader()
                stats = loader.get_dataset_stats()
                
                if stats['valid_records'] == 0:
                    return ServiceResult.validation_error(
                        "No hay registros válidos en el dataset. Verificar CSV e imágenes."
                    )
                
                steps_completed.append("[OK] Dataset validado")
                self.log_info(f"Dataset validado: {stats['valid_records']} registros válidos")
                
            except Exception as e:
                self.log_error(f"Error validando dataset: {e}")
                return ServiceResult.error(
                    ValidationServiceError(f"Error validando dataset: {str(e)}")
                )
            
            # Paso 2: Generar crops (si no existen)
            self.log_info("Paso 2: Verificando crops...")
            try:
                from ml.utils.paths import get_crops_dir
                crops_dir = get_crops_dir()
                
                if not crops_dir.exists() or len(list(crops_dir.glob("*.png"))) == 0:
                    self.log_info("Generando crops automáticamente...")
                    from management.commands.make_cacao_crops import Command as CropCommand
                    
                    crop_command = CropCommand()
                    crop_command.handle(
                        conf=0.5,
                        limit=0,
                        overwrite=False
                    )
                    
                    steps_completed.append("[OK] Crops generados")
                    self.log_info("Crops generados exitosamente")
                else:
                    steps_completed.append("[OK] Crops ya existen")
                    self.log_info("Crops ya existen, saltando generación")
                    
            except Exception as e:
                self.log_warning(f"Advertencia en generación de crops: {e}")
                steps_completed.append("[WARNING] Crops con advertencias")
            
            # Paso 3: Verificar/Entrenar modelos
            self.log_info("Paso 3: Verificando modelos...")
            try:
                from ml.utils.paths import get_regressors_artifacts_dir
                artifacts_dir = get_regressors_artifacts_dir()
                
                models_exist = all(
                    (artifacts_dir / f"{target}.pt").exists() 
                    for target in ['alto', 'ancho', 'grosor', 'peso']
                )
                
                if not models_exist:
                    self.log_info("Entrenando modelos automáticamente...")
                    from ml.pipeline.train_all import run_training_pipeline
                    
                    success = run_training_pipeline(
                        epochs=20,
                        batch_size=16,
                        learning_rate=0.001,
                        multi_head=False,
                        model_type='resnet18',
                        img_size=224,
                        early_stopping_patience=8,
                        save_best_only=True
                    )
                    
                    if success:
                        steps_completed.append("[OK] Modelos entrenados")
                        self.log_info("Modelos entrenados exitosamente")
                    else:
                        return ServiceResult.error(
                            ValidationServiceError("Error en entrenamiento de modelos")
                        )
                else:
                    steps_completed.append("[OK] Modelos ya existen")
                    self.log_info("Modelos ya existen, saltando entrenamiento")
                    
            except Exception as e:
                self.log_error(f"Error en entrenamiento de modelos: {e}")
                return ServiceResult.error(
                    ValidationServiceError(f"Error entrenando modelos: {str(e)}")
                )
            
            # Paso 4: Cargar modelos
            self.log_info("Paso 4: Cargando modelos...")
            if load_artifacts is None:
                return ServiceResult.error(
                    ValidationServiceError("Sistema de carga de modelos no disponible")
                )
            
            try:
                success = load_artifacts()
                
                if success:
                    steps_completed.append("[OK] Modelos cargados")
                    self.log_info("Modelos cargados exitosamente")
                else:
                    return ServiceResult.error(
                        ValidationServiceError("Error cargando modelos")
                    )
                    
            except Exception as e:
                self.log_error(f"Error cargando modelos: {e}")
                return ServiceResult.error(
                    ValidationServiceError(f"Error cargando modelos: {str(e)}")
                )
            
            # Paso 5: Sistema listo
            total_time = time.time() - start_time
            steps_completed.append("[OK] Sistema listo para predicciones")
            
            self.log_info(f"[OK] Inicialización automática completada en {total_time:.2f}s")
            
            return ServiceResult.success(
                data={
                    'steps_completed': steps_completed,
                    'total_time_seconds': round(total_time, 2),
                    'ready_for_predictions': True
                },
                message="Sistema inicializado automáticamente y listo para predicciones"
            )
            
        except Exception as e:
            self.log_error(f"Error en inicialización automática: {e}")
            return ServiceResult.error(
                ValidationServiceError(f"Error en inicialización automática: {str(e)}")
            )


