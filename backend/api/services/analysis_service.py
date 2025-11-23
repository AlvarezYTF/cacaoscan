"""
Analysis orchestration service for CacaoScan.
Orchestrates image processing, ML prediction, and storage operations.
"""
import logging
import time
from typing import Dict, Any
from django.core.files.uploadedfile import UploadedFile
from django.contrib.auth.models import User

from .base import BaseService, ServiceResult, ValidationServiceError
from images_app.services import ImageProcessingService, ImageStorageService
from training.services import PredictionService

logger = logging.getLogger("cacaoscan.services.analysis")


class AnalysisService(BaseService):
    """
    Orchestration service for complete image analysis workflow.
    
    This service coordinates:
    - Image validation and processing (ImageProcessingService)
    - ML predictions (PredictionService)
    - Image and prediction storage (ImageStorageService)
    
    Responsibilities:
    - Orchestrating the complete analysis workflow
    - Managing the flow between services
    - Creating audit logs
    """
    
    def __init__(self):
        super().__init__()
        self.processing_service = ImageProcessingService()
        self.storage_service = ImageStorageService()
        self.prediction_service = PredictionService()
    
    def process_image_with_segmentation(self, image_file: UploadedFile, user: User) -> ServiceResult:
        """
        Processes a complete image: validation, storage, segmentation, and prediction.
        
        Args:
            image_file: Uploaded image file
            user: User performing the analysis
            
        Returns:
            ServiceResult with complete analysis results
        """
        try:
            start_time = time.time()
            
            # 1. Validate image file
            validation_result = self.processing_service.validate_image_file_complete(image_file)
            if not validation_result.success:
                return validation_result
            
            # 2. Save image with segmentation
            save_result = self.storage_service.save_uploaded_image_with_segmentation(image_file, user)
            if not save_result.success:
                return save_result
            
            cacao_image = save_result.data['cacao_image']
            processed_png_path = save_result.data.get('processed_png_path')
            
            # 3. Load image for prediction
            load_result = self.processing_service.load_image(image_file)
            if not load_result.success:
                return load_result
            
            image = load_result.data
            
            # 4. Perform prediction
            prediction_result = self.prediction_service.predict(image)
            if not prediction_result.success:
                return prediction_result
            
            result = prediction_result.data
            prediction_time_ms = result.get('processing_time_ms', 0)
            
            # 5. Save prediction
            save_pred_result = self.storage_service.save_prediction(
                cacao_image,
                result,
                prediction_time_ms
            )
            if not save_pred_result.success:
                self.log_warning(f"Error saving prediction: {save_pred_result.error.message}")
            
            cacao_prediction = save_pred_result.data if save_pred_result.success else None
            
            # 6. Prepare response
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
                'saved_to_database': save_pred_result.success,
                'processed_png_path': str(processed_png_path) if processed_png_path else None
            }
            
            # 7. Create audit log
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
            self.log_info(f"Analysis completed in {total_time:.2f}s for user {user.username}")
            
            return ServiceResult.success(
                data=response_data,
                message="Analysis completed successfully"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error in complete processing: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error during processing", details={"original_error": str(e)})
            )
    
    def get_analysis_history(self, user: User, page: int = 1, page_size: int = 20, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Gets analysis history for a user.
        
        Args:
            user: User
            page: Page number
            page_size: Page size
            filters: Additional filters
            
        Returns:
            ServiceResult with paginated history
        """
        try:
            from ...utils.model_imports import get_models_safely
            from django.db.models import Avg
            
            models = get_models_safely({
                'CacaoPrediction': 'images_app.models.CacaoPrediction'
            })
            CacaoPrediction = models['CacaoPrediction']
            
            # Build queryset
            queryset = CacaoPrediction.objects.filter(
                image__user=user
            ).select_related('image').order_by('-created_at')
            
            # Apply filters
            if filters:
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
                if 'min_confidence' in filters:
                    queryset = queryset.filter(average_confidence__gte=filters['min_confidence'])
                if 'max_confidence' in filters:
                    queryset = queryset.filter(average_confidence__lte=filters['max_confidence'])
            
            # Paginate results
            paginated_data = self.paginate_results(queryset, page, page_size)
            
            # Format data
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
                message="Analysis history obtained successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error getting history: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error getting history", details={"original_error": str(e)})
            )
    
    def get_analysis_details(self, analysis_id: int, user: User) -> ServiceResult:
        """
        Gets details of a specific analysis.
        
        Args:
            analysis_id: Analysis ID
            user: User
            
        Returns:
            ServiceResult with analysis details
        """
        try:
            from ...utils.model_imports import get_models_safely
            
            models = get_models_safely({
                'CacaoPrediction': 'images_app.models.CacaoPrediction'
            })
            CacaoPrediction = models['CacaoPrediction']
            
            try:
                prediction = CacaoPrediction.objects.select_related('image').get(
                    id=analysis_id,
                    image__user=user
                )
            except CacaoPrediction.DoesNotExist:
                return ServiceResult.not_found_error("Analysis not found")
            
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
                message="Analysis details obtained successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error getting details: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error getting details", details={"original_error": str(e)})
            )
    
    def delete_analysis(self, analysis_id: int, user: User) -> ServiceResult:
        """
        Deletes an analysis.
        
        Args:
            analysis_id: Analysis ID
            user: User
            
        Returns:
            ServiceResult with deletion result
        """
        try:
            from ...utils.model_imports import get_models_safely
            
            models = get_models_safely({
                'CacaoPrediction': 'images_app.models.CacaoPrediction'
            })
            CacaoPrediction = models['CacaoPrediction']
            
            try:
                prediction = CacaoPrediction.objects.select_related('image').get(
                    id=analysis_id,
                    image__user=user
                )
            except CacaoPrediction.DoesNotExist:
                return ServiceResult.not_found_error("Analysis not found")
            
            # Create audit log before deleting
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
            
            # Delete analysis
            prediction.delete()
            
            self.log_info(f"Analysis {analysis_id} deleted by user {user.username}")
            
            return ServiceResult.success(
                message="Analysis deleted successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error deleting analysis: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error deleting analysis", details={"original_error": str(e)})
            )
    
    def get_analysis_statistics(self, user: User, filters: Dict[str, Any] = None) -> ServiceResult:
        """
        Gets analysis statistics for a user.
        
        Args:
            user: User
            filters: Additional filters
            
        Returns:
            ServiceResult with statistics
        """
        try:
            from ...utils.model_imports import get_models_safely
            from django.db.models import Avg, Min, Max
            
            models = get_models_safely({
                'CacaoPrediction': 'images_app.models.CacaoPrediction'
            })
            CacaoPrediction = models['CacaoPrediction']
            
            # Build base queryset
            queryset = CacaoPrediction.objects.filter(image__user=user)
            
            # Apply filters
            if filters:
                if 'date_from' in filters:
                    queryset = queryset.filter(created_at__gte=filters['date_from'])
                if 'date_to' in filters:
                    queryset = queryset.filter(created_at__lte=filters['date_to'])
            
            # Calculate statistics
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
                message="Statistics obtained successfully"
            )
            
        except Exception as e:
            self.log_error(f"Error getting statistics: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Internal error getting statistics", details={"original_error": str(e)})
            )
    
    def initialize_ml_system(self) -> ServiceResult:
        """
        Automatically initializes the complete ML system.
        
        Steps:
        1. Validate dataset
        2. Generate crops (if they don't exist)
        3. Train models (if they don't exist)
        4. Load models
        5. System ready for predictions
        
        Returns:
            ServiceResult with initialization result
        """
        try:
            import time
            from pathlib import Path
            
            start_time = time.time()
            steps_completed = []
            
            self.log_info("[START] Starting complete automatic system initialization")
            
            # Step 1: Validate dataset
            self.log_info("Step 1: Validating dataset...")
            try:
                from ml.data.dataset_loader import CacaoDatasetLoader
            except ImportError:
                return ServiceResult.error(
                    ValidationServiceError("Dataset loader not available")
                )
            
            try:
                loader = CacaoDatasetLoader()
                stats = loader.get_dataset_stats()
                
                if stats['valid_records'] == 0:
                    return ServiceResult.validation_error(
                        "No valid records in dataset. Verify CSV and images."
                    )
                
                steps_completed.append("[OK] Dataset validated")
                self.log_info(f"Dataset validated: {stats['valid_records']} valid records")
                
            except Exception as e:
                self.log_error(f"Error validating dataset: {e}")
                return ServiceResult.error(
                    ValidationServiceError(f"Error validating dataset: {str(e)}")
                )
            
            # Step 2: Generate crops (if they don't exist)
            self.log_info("Step 2: Checking crops...")
            try:
                from ml.utils.paths import get_crops_dir
                crops_dir = get_crops_dir()
                
                if not crops_dir.exists() or len(list(crops_dir.glob("*.png"))) == 0:
                    self.log_info("Generating crops automatically...")
                    from api.management.commands.make_cacao_crops import Command as CropCommand
                    
                    crop_command = CropCommand()
                    crop_command.handle(
                        conf=0.5,
                        limit=0,
                        overwrite=False
                    )
                    
                    steps_completed.append("[OK] Crops generated")
                    self.log_info("Crops generated successfully")
                else:
                    steps_completed.append("[OK] Crops already exist")
                    self.log_info("Crops already exist, skipping generation")
                    
            except Exception as e:
                self.log_warning(f"Warning in crop generation: {e}")
                steps_completed.append("[WARNING] Crops with warnings")
            
            # Step 3: Verify/Train models
            self.log_info("Step 3: Checking models...")
            try:
                from ml.utils.paths import get_regressors_artifacts_dir
                artifacts_dir = get_regressors_artifacts_dir()
                
                models_exist = all(
                    (artifacts_dir / f"{target}.pt").exists() 
                    for target in ['alto', 'ancho', 'grosor', 'peso']
                )
                
                if not models_exist:
                    self.log_info("Training models automatically...")
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
                        steps_completed.append("[OK] Models trained")
                        self.log_info("Models trained successfully")
                    else:
                        return ServiceResult.error(
                            ValidationServiceError("Error in model training")
                        )
                else:
                    steps_completed.append("[OK] Models already exist")
                    self.log_info("Models already exist, skipping training")
                    
            except Exception as e:
                self.log_error(f"Error in model training: {e}")
                return ServiceResult.error(
                    ValidationServiceError(f"Error training models: {str(e)}")
                )
            
            # Step 4: Load models
            self.log_info("Step 4: Loading models...")
            try:
                from training.services import MLService
                
                ml_service = MLService()
                load_result = ml_service.load_models(force=False)
                
                if load_result.success:
                    steps_completed.append("[OK] Models loaded")
                    self.log_info("Models loaded successfully")
                else:
                    return ServiceResult.error(
                        ValidationServiceError(
                            load_result.error.message,
                            details=load_result.error.details
                        )
                    )
                    
            except Exception as e:
                self.log_error(f"Error loading models: {e}")
                return ServiceResult.error(
                    ValidationServiceError(f"Error loading models: {str(e)}")
                )
            
            # Step 5: System ready
            total_time = time.time() - start_time
            steps_completed.append("[OK] System ready for predictions")
            
            self.log_info(f"[OK] Automatic initialization completed in {total_time:.2f}s")
            
            return ServiceResult.success(
                data={
                    'steps_completed': steps_completed,
                    'total_time_seconds': round(total_time, 2),
                    'ready_for_predictions': True
                },
                message="System automatically initialized and ready for predictions"
            )
            
        except Exception as e:
            self.log_error(f"Error in automatic initialization: {e}")
            return ServiceResult.error(
                ValidationServiceError(f"Error in automatic initialization: {str(e)}")
            )
