"""
ML model views for CacaoScan API.
"""
import logging
import time
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ...views.mixins import AdminPermissionMixin
from ...serializers import (
    ModelsStatusSerializer,
    LoadModelsResponseSerializer,
    ErrorResponseSerializer,
    AutoTrainConfigSerializer
)
from ...utils.decorators import handle_api_errors
from ...services.analysis_service import AnalysisService
from training.services import MLService
from core.utils import invalidate_models_status_cache, invalidate_dataset_validation_cache, invalidate_latest_metrics_cache

from ...utils.model_imports import get_model_safely, get_models_safely

# ML related imports (these are functions, not models, but we use the same pattern)
try:
    from ml.data.dataset_loader import CacaoDatasetLoader
    from ml.prediction.predict import get_predictor, load_artifacts
except ImportError:
    CacaoDatasetLoader = None
    get_predictor = None
    load_artifacts = None

# Import models safely
models = get_models_safely({
    'ModelMetrics': 'training.models.ModelMetrics',
    'TrainingJob': 'training.models.TrainingJob'
})
ModelMetrics = models['ModelMetrics']
TrainingJob = models['TrainingJob']

logger = logging.getLogger("cacaoscan.api.ml.model_views")


@method_decorator(cache_page(60 * 5, cache='api_cache'), name='get')
class ModelsStatusView(APIView):
    """
    Endpoint para consultar el estado de los modelos.
    
    CACHED: Este endpoint está cacheado por 5 minutos porque:
    - El estado de los modelos ML no cambia frecuentemente
    - Obtener el estado requiere cargar información del predictor
    - Reduce la carga en el sistema de ML
    - El cache se invalida automáticamente cuando se cargan nuevos modelos
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene el estado de los modelos de ML cargados",
        operation_summary="Estado de modelos",
        responses={
            200: ModelsStatusSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['Modelos']
    )
    @handle_api_errors(
        error_message="Error obteniendo estado de modelos",
        log_message="Error obteniendo estado de modelos"
    )
    def get(self, request):
        """
        Devuelve el estado de los modelos entrenados.
        """
        try:
            ml_service = MLService()
            status_result = ml_service.get_model_status()
            
            if not status_result.success:
                error_msg = status_result.error.message if status_result.error else 'Models not loaded'
                error_details = status_result.error.details if status_result.error and hasattr(status_result.error, 'details') else error_msg
                return Response({
                    'error': error_msg,
                    'details': error_details
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            status_data = status_result.data
            
            response_data = {
                'status': status_data.get('status', 'not_loaded'),
                'device': status_data.get('device', 'unknown'),
                'model': status_data.get('model', 'HybridCacaoRegression'),
                'model_details': status_data.get('model_details', {}),
                'scalers': status_data.get('scalers', 'not_loaded'),
            }

            serializer = ModelsStatusSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error getting models status: {e}")
            return Response({
                'error': 'Error obteniendo estado de modelos',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DatasetValidationView(APIView):
    """
    Endpoint para validar el dataset.
    
    CACHED: Este endpoint usa cache dinámico porque:
    - La validación del dataset puede ser costosa (lee archivos, verifica imágenes)
    - El dataset no cambia frecuentemente, pero puede cambiar cuando se agregan nuevas imágenes
    - El cache se invalida automáticamente cuando se detectan cambios en el dataset
    - El timeout del cache se ajusta dinámicamente según la frecuencia de cambios
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Valida el dataset y devuelve estadísticas",
        operation_summary="Validar dataset",
        responses={
            200: openapi.Response(
                description="Estadísticas del dataset",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'valid': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'stats': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            500: ErrorResponseSerializer,
        },
        tags=['Dataset']
    )
    @handle_api_errors(
        error_message="Error validando dataset",
        log_message="Error validando dataset"
    )
    def get(self, request):
        """
        Valida el dataset y devuelve estadísticas de forma asíncrona.
        
        Si el resultado está en cache, lo retorna inmediatamente.
        Si no, encola una tarea Celery y retorna un task_id.
        """
        from django.core.cache import cache
        from core.utils import get_cache_key
        from ...tasks.ml_tasks import validate_dataset_task
        
        # Cache key basado en el dataset
        cache_key = get_cache_key('dataset_validation', 'stats')
        
        # Intentar obtener del cache
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return Response(cached_result)
        
        # Si no está en cache, encolar tarea asíncrona
        task = validate_dataset_task.delay()
        
        logger.info(f"Dataset validation task enqueued - Task ID: {task.id}")
        
        return Response({
            'task_id': task.id,
            'status': 'processing',
            'message': 'Validación de dataset iniciada. Use el task_id para consultar el estado.'
        }, status=status.HTTP_202_ACCEPTED)


class LoadModelsView(APIView):
    """
    Endpoint para cargar modelos manualmente.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Carga los artefactos de ML (modelos y escaladores)",
        operation_summary="Cargar modelos",
        responses={
            200: LoadModelsResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['Modelos']
    )
    @handle_api_errors(
        error_message="Error cargando modelos",
        log_message="Error cargando modelos"
    )
    def post(self, request):
        """
        Carga los artefactos de ML.
        
        Uses MLService to ensure models are loaded only once.
        If models are already loaded, returns success without reloading.
        """
        try:
            ml_service = MLService()
            
            # Check if models are already loaded
            status_result = ml_service.get_model_status()
            if status_result.success:
                status_data = status_result.data
                if status_data.get('models_loaded', False) and status_data.get('load_state') == 'loaded':
                    # Models already loaded
                    invalidate_models_status_cache()
                    return Response({
                        'message': 'Modelos ya están cargados',
                        'status': 'success',
                        'already_loaded': True
                    })
            
            # Load models (will only load if not already loaded)
            load_result = ml_service.load_models(force=False)
            
            if load_result.success:
                # Invalidar cache de estado de modelos cuando se cargan nuevos modelos
                invalidate_models_status_cache()
                logger.info("Cache invalidated for models status after loading new models")
                
                return Response({
                    'message': 'Modelos cargados exitosamente',
                    'status': 'success'
                })
            else:
                error_msg = load_result.error.message if load_result.error else 'Error cargando modelos'
                error_details = load_result.error.details if load_result.error and hasattr(load_result.error, 'details') else error_msg
                return Response({
                    'error': error_msg,
                    'details': error_details
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return Response({
                'error': 'Error cargando modelos',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnloadModelsView(APIView):
    """
    Endpoint para descargar modelos de memoria.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Descarga los modelos de memoria",
        operation_summary="Descargar modelos",
        responses={
            200: openapi.Response(
                description="Modelos descargados exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['ML']
    )
    @handle_api_errors(
        error_message="Error descargando modelos",
        log_message="Error descargando modelos"
    )
    def post(self, request):
        """Descarga los modelos de memoria."""
        try:
            ml_service = MLService()
            # Intentar descargar modelos (si el método existe)
            # Si no existe, simplemente invalidar el cache
            try:
                result = ml_service.unload_models()
                if result and hasattr(result, 'success') and result.success:
                    invalidate_models_status_cache()
                    return Response(
                        {
                            'success': True,
                            'message': 'Modelos descargados exitosamente'
                        },
                        status=status.HTTP_200_OK
                    )
            except AttributeError:
                # Si el método no existe, solo invalidar cache
                pass
            
            invalidate_models_status_cache()
            return Response(
                {
                    'success': True,
                    'message': 'Cache invalidado (método unload no disponible)'
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error descargando modelos: {e}")
            return Response(
                {
                    'success': False,
                    'error': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AutoInitializeView(APIView):
    """
    Endpoint para inicialización automática completa del sistema.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Inicializa automáticamente todo el sistema: dataset → crops → entrenamiento → modelos listos",
        operation_summary="Inicialización automática completa",
        responses={
            200: openapi.Response(
                description="Inicialización completada",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'steps_completed': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING)),
                        'training_metrics': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'total_time_seconds': openapi.Schema(type=openapi.TYPE_NUMBER)
                    }
                )
            ),
            202: openapi.Response(
                description="Inicialización en progreso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'progress': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            500: ErrorResponseSerializer,
        },
        tags=['Inicialización']
    )
    @handle_api_errors(
        error_message="Error en inicialización automática",
        log_message="Error en inicialización automática"
    )
    def post(self, request):
        """
        Inicialización automática completa del sistema.
        
        Pasos:
        1. Validar dataset
        2. Generar crops (si no existen)
        3. Entrenar modelos (si no existen)
        4. Cargar modelos
        5. Sistema listo para predicciones
        """
        # Usar servicio de análisis para inicialización automática
        analysis_service = AnalysisService()
        result = analysis_service.initialize_ml_system()
        
        if result.success:
            return Response({
                'message': result.message,
                'status': 'success',
                **result.data
            }, status=status.HTTP_200_OK)
        else:
            # Mapear errores del servicio a códigos HTTP
            if 'validation_error' in result.error.error_code or 'valid_records' in result.error.message.lower():
                status_code = status.HTTP_400_BAD_REQUEST
            elif 'no disponible' in result.error.message.lower() or 'not available' in result.error.message.lower():
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            return Response({
                'error': result.error.message,
                'status': 'error',
                'details': result.error.details
            }, status=status_code)


@method_decorator(cache_page(60 * 1, cache='api_cache'), name='get')
class LatestMetricsView(APIView):
    """
    Endpoint para obtener las últimas métricas de todos los targets.
    
    CACHED: Este endpoint está cacheado por 1 minuto porque:
    - Las métricas pueden cambiar frecuentemente durante entrenamientos
    - 1 minuto es suficiente para reducir carga sin ocultar cambios importantes
    - El cache se invalida automáticamente cuando se crean nuevas métricas
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene las últimas métricas de todos los targets",
        operation_summary="Últimas métricas de modelos",
        responses={
            200: openapi.Response(
                description="Métricas obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            401: ErrorResponseSerializer,
        },
        tags=['ML']
    )
    @handle_api_errors(
        error_message="Error obteniendo últimas métricas",
        log_message="Error obteniendo últimas métricas"
    )
    def get(self, request):
        """
        Obtiene las últimas métricas de todos los targets.
        """
        if ModelMetrics is None:
            return Response({
                'error': 'Modelo ModelMetrics no disponible',
                'status': 'error'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Obtener las últimas métricas por target
        targets = ['alto', 'ancho', 'grosor', 'peso']
        latest_metrics = {}
        
        for target in targets:
            latest = ModelMetrics.objects.filter(
                target=target,
                metric_type='validation'
            ).select_related('created_by').order_by('-created_at').first()
            
            if latest:
                from ...serializers import ModelMetricsListSerializer
                latest_metrics[target] = ModelMetricsListSerializer(latest).data
        
        return Response({
            'message': 'Últimas métricas obtenidas exitosamente',
            'metrics': latest_metrics
        }, status=status.HTTP_200_OK)


class PromoteModelView(AdminPermissionMixin, APIView):
    """
    Endpoint para promover una versión de modelo a producción.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Promueve una versión de modelo a producción (solo admins)",
        operation_summary="Promover modelo a producción",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'model_name': openapi.Schema(type=openapi.TYPE_STRING),
                'target': openapi.Schema(type=openapi.TYPE_STRING, enum=['alto', 'ancho', 'grosor', 'peso'])
            },
            required=['model_name', 'target']
        ),
        responses={
            200: openapi.Response(
                description="Modelo promovido exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['ML']
    )
    @handle_api_errors(
        error_message="Error promoviendo modelo",
        log_message="Error promoviendo modelo"
    )
    def post(self, request, version):
        """
        Promueve una versión específica de modelo a producción.
        """
        # Verificar permisos de administrador
        if not self.is_admin_user(request.user):
            return self.admin_permission_denied()
        
        if ModelMetrics is None:
            return Response({
                'error': 'Modelo ModelMetrics no disponible',
                'status': 'error'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        model_name = request.data.get('model_name')
        target = request.data.get('target')
        
        if not model_name or not target:
            return Response({
                'error': 'model_name y target son requeridos',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar el modelo por versión, nombre y target
        # Optimizado con select_related para evitar query adicional
        try:
            model_metric = ModelMetrics.objects.select_related('created_by').get(
                version=version,
                model_name=model_name,
                target=target
            )
        except ModelMetrics.DoesNotExist:
            return Response({
                'error': f'Modelo {model_name} versión {version} para target {target} no encontrado',
                'status': 'error'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Promover a producción
        model_metric.mark_as_production()
        
        from ...serializers import ModelMetricsListSerializer
        serializer = ModelMetricsListSerializer(model_metric)
        
        logger.info(f"Modelo {model_name} v{version} para {target} promovido a producción por {request.user.username}")
        
        return Response({
            'message': f'Modelo {model_name} v{version} para {target} promovido a producción exitosamente',
            'model': serializer.data
        }, status=status.HTTP_200_OK)


class AutoTrainView(APIView):
    """
    Inicia un trabajo de entrenamiento de modelos de forma síncrona.
    ACTUALIZADO: Eliminada la dependencia de Celery.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AutoTrainConfigSerializer

    @swagger_auto_schema(
        operation_description="Inicia un entrenamiento síncrono de modelos",
        operation_summary="Entrenamiento automático síncrono",
        request_body=AutoTrainConfigSerializer,
        responses={
            200: openapi.Response(
                description="Entrenamiento completado",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['ML']
    )
    @handle_api_errors(
        error_message="Error en entrenamiento automático",
        log_message="Error en entrenamiento automático"
    )
    def post(self, request, *args, **kwargs):
        serializer = AutoTrainConfigSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Configuración inválida", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        config = serializer.validated_data

        try:
            from ml.pipeline.train_all import run_training_pipeline
            from ml.utils.logs import get_ml_logger

            ml_logger = get_ml_logger("cacaoscan.api.AutoTrainView")

            pipeline_config = {
                'epochs': config.get('epochs', 50),
                'batch_size': config.get('batch_size', 16),
                'learning_rate': config.get('learning_rate', 1e-4),
                'model_type': config.get('model_type', 'hybrid'),
                'hybrid': True,
                'use_pixel_features': True,
                'segmentation_backend': 'opencv',
                'targets': ['alto', 'ancho', 'grosor', 'peso']
            }

            ml_logger.info(f"Iniciando entrenamiento síncrono (sin Celery) con config: {pipeline_config}")

            success = run_training_pipeline(**pipeline_config)

            if success:
                ml_logger.info("Entrenamiento síncrono completado exitosamente.")
                return Response(
                    {"status": "completed", "message": "Entrenamiento síncrono completado exitosamente."},
                    status=status.HTTP_200_OK
                )

            ml_logger.error("Entrenamiento síncrono falló.")
            return Response(
                {"status": "failed", "message": "El entrenamiento síncrono falló."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except ImportError:
            return Response(
                {"error": "Pipeline de entrenamiento no encontrado."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            logger.error(f"Error fatal en entrenamiento síncrono: {e}", exc_info=True)
            return Response(
                {"error": f"Error en entrenamiento: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

