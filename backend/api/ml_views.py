"""
Vistas para el módulo de ML (entrenamiento, métricas, promoción).
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import ErrorResponseSerializer, AutoTrainConfigSerializer
from .models import ModelMetrics, TrainingJob

logger = logging.getLogger("cacaoscan.api.ml_views")


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
    def get(self, request):
        """
        Obtiene las últimas métricas de todos los targets.
        """
        try:
            # Obtener las últimas métricas por target
            targets = ['alto', 'ancho', 'grosor', 'peso']
            latest_metrics = {}
            
            for target in targets:
                latest = ModelMetrics.objects.filter(
                    target=target,
                    metric_type='validation'
                ).order_by('-created_at').first()
                
                if latest:
                    from .serializers import ModelMetricsListSerializer
                    latest_metrics[target] = ModelMetricsListSerializer(latest).data
            
            return Response({
                'message': 'Últimas métricas obtenidas exitosamente',
                'metrics': latest_metrics
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo últimas métricas: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PromoteModelView(APIView):
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
    def post(self, request, version):
        """
        Promueve una versión específica de modelo a producción.
        """
        try:
            # Verificar permisos de administrador
            if not request.user.is_superuser and not request.user.is_staff:
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
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
            
            from .serializers import ModelMetricsListSerializer
            serializer = ModelMetricsListSerializer(model_metric)
            
            logger.info(f"Modelo {model_name} v{version} para {target} promovido a producción por {request.user.username}")
            
            return Response({
                'message': f'Modelo {model_name} v{version} para {target} promovido a producción exitosamente',
                'model': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error promoviendo modelo: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MLTrainView(APIView):
    """
    Endpoint para iniciar entrenamiento (alias para TrainingJobCreateView).
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Redirige a TrainingJobCreateView para mantener compatibilidad.
        """
        from .views.training_views import TrainingJobCreateView
        view = TrainingJobCreateView()
        return view.post(request)


class AutoTrainView(APIView):
    """
    Inicia un trabajo de entrenamiento de modelos de forma síncrona.
    ACTUALIZADO: Eliminada la dependencia de Celery.
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AutoTrainConfigSerializer

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

            logger = get_ml_logger("cacaoscan.api.AutoTrainView")

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

            logger.info(f"Iniciando entrenamiento síncrono (sin Celery) con config: {pipeline_config}")

            success = run_training_pipeline(**pipeline_config)

            if success:
                logger.info("Entrenamiento síncrono completado exitosamente.")
                return Response(
                    {"status": "completed", "message": "Entrenamiento síncrono completado exitosamente."},
                    status=status.HTTP_200_OK
                )

            logger.error("Entrenamiento síncrono falló.")
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

