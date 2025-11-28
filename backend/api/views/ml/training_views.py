"""
Training views for CacaoScan API.
"""
import logging
import uuid
from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ...views.mixins import PaginationMixin, AdminPermissionMixin
from ...serializers import (
    TrainingJobSerializer,
    TrainingJobCreateSerializer,
    TrainingJobStatusSerializer,
    ErrorResponseSerializer
)
from ...utils.decorators import handle_api_errors

from ...utils.model_imports import get_model_safely

# Import training model safely
TrainingJob = get_model_safely('training.models.TrainingJob')

logger = logging.getLogger("cacaoscan.api.ml.training")

# Error message constants
ERROR_TRAINING_JOB_MODEL_UNAVAILABLE = 'Modelo TrainingJob no disponible'
ERROR_INTERNAL_SERVER = 'Error interno del servidor'


class TrainingJobListView(PaginationMixin, AdminPermissionMixin, APIView):
    """
    Endpoint para listar trabajos de entrenamiento (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la lista de trabajos de entrenamiento (solo admins)",
        operation_summary="Lista de trabajos de entrenamiento",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página (máximo 100)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filtrar por estado", type=openapi.TYPE_STRING),
            openapi.Parameter('job_type', openapi.IN_QUERY, description="Filtrar por tipo", type=openapi.TYPE_STRING),
            openapi.Parameter('created_by', openapi.IN_QUERY, description="Filtrar por creador", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="Lista de trabajos obtenida exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Entrenamiento']
    )
    def get(self, request):
        """
        Obtiene la lista de trabajos de entrenamiento.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            if TrainingJob is None:
                return Response({
                    'error': ERROR_TRAINING_JOB_MODEL_UNAVAILABLE,
                    'status': 'error'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Obtener parámetros de consulta
            status_filter = request.GET.get('status')
            job_type_filter = request.GET.get('job_type')
            created_by_filter = request.GET.get('created_by')
            
            # Construir queryset base
            queryset = TrainingJob.objects.all().select_related('created_by')
            
            # Aplicar filtros
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            if job_type_filter:
                queryset = queryset.filter(job_type=job_type_filter)
            
            if created_by_filter:
                queryset = queryset.filter(created_by_id=created_by_filter)
            
            # Ordenar por fecha de creación (más recientes primero)
            queryset = queryset.order_by('-created_at')
            
            # Paginar usando el mixin
            return self.paginate_queryset(
                request,
                queryset,
                TrainingJobSerializer
            )
            
        except ValueError as e:
            return Response({
                'error': 'Parámetros de consulta inválidos',
                'status': 'error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error obteniendo lista de trabajos de entrenamiento: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TrainingJobCreateView(AdminPermissionMixin, APIView):
    """
    Endpoint para crear trabajos de entrenamiento (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Crea un nuevo trabajo de entrenamiento (solo admins)",
        operation_summary="Crear trabajo de entrenamiento",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'job_type': openapi.Schema(type=openapi.TYPE_STRING, description="Tipo: regression, vision, incremental"),
                'model_name': openapi.Schema(type=openapi.TYPE_STRING, description="Nombre del modelo"),
                'dataset_size': openapi.Schema(type=openapi.TYPE_INTEGER, description="Tamaño del dataset"),
                'epochs': openapi.Schema(type=openapi.TYPE_INTEGER, description="Número de epochs"),
                'batch_size': openapi.Schema(type=openapi.TYPE_INTEGER, description="Tamaño del batch"),
                'learning_rate': openapi.Schema(type=openapi.TYPE_NUMBER, description="Learning rate"),
                'config_params': openapi.Schema(type=openapi.TYPE_OBJECT, description="Parámetros adicionales")
            }
        ),
        responses={
            201: openapi.Response(
                description="Trabajo de entrenamiento creado exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Entrenamiento']
    )
    def post(self, request):
        """
        Crea un nuevo trabajo de entrenamiento.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self.is_admin_user(request.user):
                return self.admin_permission_denied()
            
            if TrainingJob is None:
                return Response({
                    'error': ERROR_TRAINING_JOB_MODEL_UNAVAILABLE,
                    'status': 'error'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Validar datos de entrada
            serializer = TrainingJobCreateSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response({
                    'error': 'Datos de entrada inválidos',
                    'status': 'error',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generar ID único para el trabajo
            job_id = f"job_{uuid.uuid4().hex[:12]}"
            
            # Crear trabajo de entrenamiento
            training_job = TrainingJob.objects.create(
                job_id=job_id,
                created_by=request.user,
                **serializer.validated_data
            )
            
            # Iniciar entrenamiento asíncrono con Celery
            try:
                from api.tasks import train_model_task
                
                config = {
                    'epochs': serializer.validated_data.get('epochs', 30),
                    'batch_size': serializer.validated_data.get('batch_size', 16),
                    'learning_rate': serializer.validated_data.get('learning_rate', 0.001),
                    'multi_head': serializer.validated_data.get('config_params', {}).get('multi_head', False),
                    'model_type': serializer.validated_data.get('config_params', {}).get('model_type', 'resnet18'),
                    'img_size': serializer.validated_data.get('config_params', {}).get('img_size', 224),
                    'early_stopping_patience': serializer.validated_data.get('config_params', {}).get('early_stopping_patience', 10),
                    'save_best_only': serializer.validated_data.get('config_params', {}).get('save_best_only', True)
                }
                
                # Encolar tarea de Celery
                train_model_task.delay(job_id, config)
            except ImportError:
                logger.warning("Celery no disponible, el entrenamiento no se iniciará automáticamente")
            except Exception as e:
                logger.error(f"Error iniciando tarea de entrenamiento: {e}")
            
            # Serializar respuesta
            response_serializer = TrainingJobSerializer(training_job)
            
            logger.info(f"Trabajo de entrenamiento {job_id} creado por admin {request.user.username}")
            
            return Response({
                'message': 'Trabajo de entrenamiento creado exitosamente',
                'job_id': job_id,
                'job': response_serializer.data,
                'status': 'pending'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creando trabajo de entrenamiento: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TrainingJobStatusView(AdminPermissionMixin, APIView):
    """
    Endpoint para obtener el estado de un trabajo de entrenamiento específico.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene el estado actual de un trabajo de entrenamiento",
        operation_summary="Estado del trabajo de entrenamiento",
        responses={
            200: openapi.Response(
                description="Estado del trabajo obtenido exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Entrenamiento']
    )
    def get(self, request, job_id):
        """
        Obtiene el estado actual de un trabajo de entrenamiento.
        """
        try:
            if TrainingJob is None:
                return Response({
                    'error': ERROR_TRAINING_JOB_MODEL_UNAVAILABLE,
                    'status': 'error'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Obtener trabajo de entrenamiento (optimizado con select_related)
            try:
                training_job = TrainingJob.objects.select_related('created_by').get(job_id=job_id)
            except TrainingJob.DoesNotExist:
                return Response({
                    'error': 'Trabajo de entrenamiento no encontrado',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar permisos (solo el creador o admin puede ver)
            if training_job.created_by != request.user and not self.is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para ver este trabajo de entrenamiento',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Serializar estado del trabajo
            serializer = TrainingJobStatusSerializer(training_job)
            
            # Información adicional del estado
            status_info = {
                'job': serializer.data,
                'status_details': {
                    'is_active': training_job.is_active,
                    'can_cancel': training_job.status in ['pending', 'running'],
                    'estimated_completion': self._estimate_completion(training_job),
                    'logs_preview': training_job.logs.split('\n')[-5:] if training_job.logs else []
                }
            }
            
            return Response(status_info, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo estado del trabajo {job_id}: {e}")
            return Response({
                'error': ERROR_INTERNAL_SERVER,
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _estimate_completion(self, training_job):
        """
        Estimar tiempo de finalización basado en el progreso actual.
        """
        if training_job.status == 'completed':
            return "Completado"
        elif training_job.status in ['failed', 'cancelled']:
            return "Finalizado"
        elif training_job.progress_percentage == 0:
            return "No iniciado"
        elif training_job.progress_percentage > 0 and training_job.started_at:
            # Calcular tiempo estimado basado en progreso
            elapsed_time = (timezone.now() - training_job.started_at).total_seconds()
            if training_job.progress_percentage > 0:
                estimated_total = elapsed_time / (training_job.progress_percentage / 100)
                remaining_time = estimated_total - elapsed_time
                
                if remaining_time > 0:
                    hours = int(remaining_time // 3600)
                    minutes = int((remaining_time % 3600) // 60)
                    if hours > 0:
                        return f"Aproximadamente {hours}h {minutes}m restantes"
                    else:
                        return f"Aproximadamente {minutes}m restantes"
        
        return "Calculando..."

