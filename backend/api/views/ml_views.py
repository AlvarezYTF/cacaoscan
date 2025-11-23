"""
ML views for CacaoScan API.
"""
import logging
import time
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..views.mixins import AdminPermissionMixin
from ..serializers import (
    ModelsStatusSerializer,
    LoadModelsResponseSerializer,
    ErrorResponseSerializer,
    AutoTrainConfigSerializer
)
from ..utils.decorators import handle_api_errors
from ..services.analysis_service import AnalysisService

from ..utils.model_imports import get_model_safely, get_models_safely

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
    'ModelMetrics': 'api.models.ModelMetrics',
    'TrainingJob': 'training.models.TrainingJob'
})
ModelMetrics = models['ModelMetrics']
TrainingJob = models['TrainingJob']

logger = logging.getLogger("cacaoscan.api.ml_views")


class ModelsStatusView(APIView):
    """
    Endpoint para consultar el estado de los modelos.
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
        if get_predictor is None:
            return Response({
                'error': 'Sistema de predicción no disponible',
                'status': 'error'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        predictor = get_predictor()
        model_info = predictor.get_model_info()
        
        response_data = {
            'status': model_info.get('status', 'not_loaded'),
            'device': model_info.get('device', 'unknown'),
            'model': model_info.get('model', 'HybridCacaoRegression'),
            'model_details': model_info.get('model_details', {}),
            'scalers': model_info.get('scalers', 'not_loaded'),
        }

        serializer = ModelsStatusSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class DatasetValidationView(APIView):
    """
    Endpoint para validar el dataset.
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
        Valida el dataset y devuelve estadísticas.
        """
        if CacaoDatasetLoader is None:
            return Response({
                'valid': False,
                'error': 'Cargador de dataset no disponible',
                'status': 'error'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        loader = CacaoDatasetLoader()
        stats = loader.get_dataset_stats()
        
        return Response({
            'valid': len(stats.get('missing_images', [])) == 0,
            'stats': stats,
            'status': 'success'
        })


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
        """
        if load_artifacts is None:
            return Response({
                'error': 'Sistema de carga de modelos no disponible',
                'status': 'error'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        success = load_artifacts()
        
        if success:
            return Response({
                'message': 'Modelos cargados exitosamente',
                'status': 'success'
            })
        else:
            return Response({
                'error': 'Error cargando modelos',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class LatestMetricsView(APIView):
    """
    Endpoint para obtener las últimas métricas de todos los targets.
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
                from ..serializers import ModelMetricsListSerializer
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
        
        from ..serializers import ModelMetricsListSerializer
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

