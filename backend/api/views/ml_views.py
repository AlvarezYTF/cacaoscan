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

# ML related imports
try:
    from ml.data.dataset_loader import CacaoDatasetLoader
    from ml.prediction.predict import get_predictor, load_artifacts
except ImportError:
    CacaoDatasetLoader = None
    get_predictor = None
    load_artifacts = None

# Importar modelos
try:
    from ..models import ModelMetrics, TrainingJob
except ImportError:
    ModelMetrics = None
    TrainingJob = None

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
        start_time = time.time()
        steps_completed = []
        
        logger.info("[INICIO] Iniciando inicialización automática completa del sistema")
        
        # Paso 1: Validar dataset
        logger.info("Paso 1: Validando dataset...")
        if CacaoDatasetLoader is None:
            return Response({
                'error': 'Cargador de dataset no disponible',
                'status': 'error'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        try:
            loader = CacaoDatasetLoader()
            stats = loader.get_dataset_stats()
            
            if stats['valid_records'] == 0:
                return Response({
                    'error': 'No hay registros válidos en el dataset. Verificar CSV e imágenes.',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            steps_completed.append("[OK] Dataset validado")
            logger.info(f"Dataset validado: {stats['valid_records']} registros válidos")
            
        except Exception as e:
            logger.error(f"Error validando dataset: {e}")
            return Response({
                'error': f'Error validando dataset: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Paso 2: Generar crops (si no existen)
        logger.info("Paso 2: Verificando crops...")
        try:
            from ml.utils.paths import get_crops_dir
            crops_dir = get_crops_dir()
            
            if not crops_dir.exists() or len(list(crops_dir.glob("*.png"))) == 0:
                logger.info("Generando crops automáticamente...")
                from management.commands.make_cacao_crops import Command as CropCommand
                
                # Simular comando de crops
                crop_command = CropCommand()
                crop_command.handle(
                    conf=0.5,
                    limit=0,
                    overwrite=False
                )
                
                steps_completed.append("[OK] Crops generados")
                logger.info("Crops generados exitosamente")
            else:
                steps_completed.append("[OK] Crops ya existen")
                logger.info("Crops ya existen, saltando generación")
                
        except Exception as e:
            logger.warning(f"Advertencia en generación de crops: {e}")
            steps_completed.append("[WARNING] Crops con advertencias")
        
        # Paso 3: Verificar/Entrenar modelos
        logger.info("Paso 3: Verificando modelos...")
        try:
            from ml.utils.paths import get_regressors_artifacts_dir
            artifacts_dir = get_regressors_artifacts_dir()
            
            models_exist = all(
                (artifacts_dir / f"{target}.pt").exists() 
                for target in ['alto', 'ancho', 'grosor', 'peso']
            )
            
            if not models_exist:
                logger.info("Entrenando modelos automáticamente...")
                from ml.pipeline.train_all import run_training_pipeline
                
                # Configuración de entrenamiento automático
                success = run_training_pipeline(
                    epochs=20,  # Menos epochs para inicialización rápida
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
                    logger.info("Modelos entrenados exitosamente")
                else:
                    return Response({
                        'error': 'Error en entrenamiento de modelos',
                        'status': 'error'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                steps_completed.append("[OK] Modelos ya existen")
                logger.info("Modelos ya existen, saltando entrenamiento")
                
        except Exception as e:
            logger.error(f"Error en entrenamiento de modelos: {e}")
            return Response({
                'error': f'Error entrenando modelos: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Paso 4: Cargar modelos
        logger.info("Paso 4: Cargando modelos...")
        if load_artifacts is None:
            return Response({
                'error': 'Sistema de carga de modelos no disponible',
                'status': 'error'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        try:
            success = load_artifacts()
            
            if success:
                steps_completed.append("[OK] Modelos cargados")
                logger.info("Modelos cargados exitosamente")
            else:
                return Response({
                    'error': 'Error cargando modelos',
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
            return Response({
                'error': f'Error cargando modelos: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Paso 5: Sistema listo
        total_time = time.time() - start_time
        steps_completed.append("[OK] Sistema listo para predicciones")
        
        logger.info(f"[OK] Inicialización automática completada en {total_time:.2f}s")
        
        return Response({
            'message': 'Sistema inicializado automáticamente y listo para predicciones',
            'status': 'success',
            'steps_completed': steps_completed,
            'total_time_seconds': round(total_time, 2),
            'ready_for_predictions': True
        })


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
            ).order_by('-created_at').first()
            
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
        try:
            model_metric = ModelMetrics.objects.get(
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

