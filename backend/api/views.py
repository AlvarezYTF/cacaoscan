"""
Views para la API de CacaoScan.
"""
import time
import logging
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import login, logout
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Avg, Min, Max, Sum

# Importar vistas de calibración
from .calibration_views import CalibrationStatusView, CalibrationView, CalibratedScanMeasureView

# Importar vistas de emails
# from .email_views import EmailStatusView, SendTestEmailView, SendBulkNotificationView, EmailTemplatePreviewView, EmailLogsView

# Importar vistas de entrenamiento incremental
from .incremental_views import (
    IncrementalTrainingStatusView, 
    IncrementalTrainingView, 
    IncrementalDataUploadView,
    IncrementalModelVersionsView,
    IncrementalDataVersionsView
)

# Importar vistas de métricas de modelos
from .model_metrics_views import (
    ModelMetricsListView,
    ModelMetricsDetailView,
    ModelMetricsCreateView,
    ModelMetricsUpdateView,
    ModelMetricsDeleteView,
    ModelMetricsStatsView,
    ModelPerformanceTrendView,
    ModelComparisonView,
    BestModelsView,
    ProductionModelsView
)

# Importar vistas de análisis batch
from .batch_analysis_views import BatchAnalysisView

# Importar vistas de configuración del sistema
from .config_views import (
    SystemSettingsView,
    SystemGeneralConfigView,
    SystemSecurityConfigView,
    SystemMLConfigView,
    SystemInfoView
)

# Importar vistas OTP
from .otp_views import SendOtpView, VerifyOtpView

from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from PIL import Image
import io
import os

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ml.data.dataset_loader import CacaoDatasetLoader
from ml.prediction.predict import get_predictor, load_artifacts
from .serializers import (
    ScanMeasureResponseSerializer, 
    ErrorResponseSerializer,
    ModelsStatusSerializer,
    LoadModelsResponseSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    CacaoImageSerializer,
    CacaoImageDetailSerializer,
    FincaSerializer,
    FincaListSerializer,
    FincaDetailSerializer,
    FincaStatsSerializer
)
from .utils import create_error_response, create_success_response
# Importar desde apps modulares
try:
    from auth_app.models import EmailVerificationToken
except ImportError:
    EmailVerificationToken = None

try:
    from images_app.models import CacaoImage, CacaoPrediction
except ImportError:
    CacaoImage = None
    CacaoPrediction = None

try:
    from training.models import TrainingJob
except ImportError:
    TrainingJob = None

try:
    from fincas_app.models import Finca, Lote
except ImportError:
    Finca = None
    Lote = None

try:
    from notifications.models import Notification
except ImportError:
    Notification = None

try:
    from audit.models import ActivityLog
except ImportError:
    ActivityLog = None

# Modelos únicos de API
from .models import LoginHistory, ReporteGenerado
from django.db.models import Prefetch
from .fincas_views import (
    FincaListCreateView,
    FincaDetailView,
    FincaUpdateView,
    FincaDeleteView,
    FincaActivateView,
    FincaStatsView
)
from .lotes_views import (
    LoteListCreateView,
    LoteDetailView,
    LoteUpdateView,
    LoteDeleteView,
    LoteStatsView,
    LotesPorFincaView
)
from .notifications_views import (
    NotificationListCreateView,
    NotificationDetailView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    NotificationUnreadCountView,
    NotificationStatsView,
    NotificationCreateView
)
from .audit_views import (
    ActivityLogListView,
    LoginHistoryListView,
    AuditStatsView
)
from .report_views import (
    ReporteListCreateView,
    ReporteDetailView,
    ReporteDownloadView,
    ReporteAgricultoresView,
    ReporteUsuariosView,
    ReporteDeleteView,
    ReporteStatsView,
    ReporteCleanupView
)


logger = logging.getLogger("cacaoscan.api")


class ImagePermissionMixin:
    """
    Mixin para manejar permisos de acceso a imágenes.
    """
    
    def can_access_image(self, user, image):
        """
        Verificar si el usuario puede acceder a la imagen.
        
        Args:
            user: Usuario autenticado
            image: Objeto CacaoImage
            
        Returns:
            bool: True si puede acceder, False en caso contrario
        """
        # El propietario siempre puede acceder
        if image.user == user:
            return True
        
        # Los admins pueden acceder a cualquier imagen
        if user.is_superuser or user.is_staff:
            return True
        
        # Los analistas pueden acceder a imágenes de todos los usuarios
        if user.groups.filter(name='analyst').exists():
            return True
        
        return False
    
    def get_user_images_queryset(self, user):
        """
        Obtener queryset de imágenes según permisos del usuario.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            QuerySet: Queryset filtrado según permisos
        """
        if user.is_superuser or user.is_staff:
            # Admins pueden ver todas las imágenes
            return CacaoImage.objects.all().select_related('user')
        elif user.groups.filter(name='analyst').exists():
            # Analistas pueden ver todas las imágenes
            return CacaoImage.objects.all().select_related('user')
        else:
            # Agricultores solo ven sus propias imágenes
            return CacaoImage.objects.filter(user=user).select_related('user')


class ScanMeasureView(APIView):
    """
    Endpoint para medición de granos de cacao.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def _save_uploaded_image(self, image_file, user):
        """
        Guarda la imagen subida en el sistema de archivos y crea registro en BD.
        
        Args:
            image_file: Archivo de imagen subido
            user: Usuario autenticado
            
        Returns:
            tuple: (cacao_image_obj, success, error_message)
        """
        try:
            # Crear objeto CacaoImage
            cacao_image = CacaoImage(
                user=user,
                image=image_file,
                file_name=image_file.name,
                file_size=image_file.size,
                file_type=image_file.content_type,
                processed=False
            )
            
            # Guardar en BD
            cacao_image.save()
            
            logger.info(f"Imagen guardada con ID {cacao_image.id} para usuario {user.username}")
            return cacao_image, True, None
            
        except Exception as e:
            logger.error(f"Error guardando imagen: {e}")
            return None, False, str(e)
    
    def _save_prediction(self, cacao_image, result, processing_time_ms):
        """
        Guarda los resultados de predicción en BD con transacción.
        
        Args:
            cacao_image: Objeto CacaoImage asociado
            result: Resultados de predicción del modelo
            processing_time_ms: Tiempo de procesamiento en milisegundos
            
        Returns:
            tuple: (cacao_prediction_obj, success, error_message)
        """
        try:
            if not cacao_image:
                return None, False, "No hay imagen asociada para guardar predicción"
            
            # Usar transacción para asegurar integridad
            with transaction.atomic():
                # Crear objeto CacaoPrediction
                cacao_prediction = CacaoPrediction(
                    image=cacao_image,
                    alto_mm=result['alto_mm'],
                    ancho_mm=result['ancho_mm'],
                    grosor_mm=result['grosor_mm'],
                    peso_g=result['peso_g'],
                    confidence_alto=result['confidences']['alto'],
                    confidence_ancho=result['confidences']['ancho'],
                    confidence_grosor=result['confidences']['grosor'],
                    confidence_peso=result['confidences']['peso'],
                    processing_time_ms=processing_time_ms,
                    crop_url=result.get('crop_url'),
                    model_version=result['debug'].get('models_version', 'v1.0'),
                    device_used=result['debug'].get('device', 'cpu')
                )
                
                # Guardar en BD
                cacao_prediction.save()
                
                # Marcar imagen como procesada
                cacao_image.processed = True
                cacao_image.save()
            
            logger.info(f"Predicción guardada con ID {cacao_prediction.id} para imagen {cacao_image.id}")
            return cacao_prediction, True, None
            
        except Exception as e:
            logger.error(f"Error guardando predicción: {e}")
            return None, False, str(e)
    
    @swagger_auto_schema(
        operation_description="Procesa una imagen de grano de cacao y devuelve predicciones de dimensiones y peso",
        operation_summary="Medir grano de cacao",
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="Imagen del grano de cacao (JPG, PNG, BMP)",
                type=openapi.TYPE_FILE,
                required=True
            ),
        ],
        responses={
            200: ScanMeasureResponseSerializer,
            400: ErrorResponseSerializer,
            413: ErrorResponseSerializer,
            503: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['Medición']
    )
    def post(self, request):
        """
        Procesa una imagen y devuelve mediciones del grano.
        
        Request:
            - multipart/form-data con campo 'image' (jpg/png/bmp)
            - Límite de tamaño: 8MB
        
        Response:
            - JSON con predicciones de dimensiones y peso
        """
        start_time = time.time()
        
        try:
            # 1. Validar request
            if 'image' not in request.FILES:
                return Response({
                    'error': 'Campo "image" requerido',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            image_file = request.FILES['image']
            
            # 2. Validar tamaño (8MB máximo)
            max_size = 8 * 1024 * 1024  # 8MB en bytes
            if image_file.size > max_size:
                return Response({
                    'error': f'Imagen demasiado grande. Máximo permitido: 8MB',
                    'status': 'error'
                }, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
            
            # 3. Validar tipo de contenido
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp']
            if image_file.content_type not in allowed_types:
                return Response({
                    'error': f'Tipo de archivo no permitido. Tipos válidos: {", ".join(allowed_types)}',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. Validar nombre de archivo (sanitizar)
            filename = image_file.name
            if not filename or len(filename) > 255:
                return Response({
                    'error': 'Nombre de archivo inválido',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 5. Leer y validar imagen
            try:
                image_bytes = image_file.read()
                image = Image.open(io.BytesIO(image_bytes))
                
                # Convertir a RGB si es necesario
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Validar dimensiones mínimas
                if image.width < 50 or image.height < 50:
                    return Response({
                        'error': 'Imagen demasiado pequeña. Mínimo: 50x50 píxeles',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            except Exception as e:
                return Response({
                    'error': f'Error procesando imagen: {str(e)}',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 6. Guardar imagen en BD
            cacao_image, save_success, save_error = self._save_uploaded_image(image_file, request.user)
            if not save_success:
                logger.warning(f"Error guardando imagen en BD: {save_error}")
                # Continuar con predicción aunque falle el guardado
            
            # 7. Obtener predictor y hacer predicción
            try:
                predictor = get_predictor()
                
                if not predictor.models_loaded:
                    # Intentar cargar modelos automáticamente
                    logger.info("Modelos no cargados. Intentando carga automática...")
                    success = load_artifacts()
                    
                    if not success:
                        return Response({
                            'error': 'Modelos no disponibles. Ejecutar inicialización automática primero.',
                            'status': 'error',
                            'suggestion': 'POST /api/v1/auto-initialize/ para inicializar el sistema'
                        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    
                    # Reintentar obtener predictor
                    predictor = get_predictor()
                    
                    if not predictor.models_loaded:
                        return Response({
                            'error': 'Error cargando modelos después de intento automático.',
                            'status': 'error'
                        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                
                # Realizar predicción
                prediction_start = time.time()
                result = predictor.predict(image)
                prediction_time_ms = int((time.time() - prediction_start) * 1000)
                
                # 8. Guardar predicción en BD
                cacao_prediction, pred_success, pred_error = self._save_prediction(
                    cacao_image, result, prediction_time_ms
                )
                if not pred_success:
                    logger.warning(f"Error guardando predicción en BD: {pred_error}")
                
                # 9. Preparar respuesta
                response_data = {
                    'alto_mm': result['alto_mm'],
                    'ancho_mm': result['ancho_mm'],
                    'grosor_mm': result['grosor_mm'],
                    'peso_g': result['peso_g'],
                    'confidences': result['confidences'],
                    'crop_url': result['crop_url'],
                    'debug': result['debug'],
                    'image_id': cacao_image.id if cacao_image else None,
                    'prediction_id': cacao_prediction.id if cacao_prediction else None,
                    'saved_to_database': save_success and pred_success
                }
                
                # 10. Enviar email de análisis completado
                try:
                    from .email_service import send_email_notification
                    
                    # Determinar nivel de confianza
                    avg_confidence = (result['confidences']['alto'] + result['confidences']['ancho'] + 
                                    result['confidences']['grosor'] + result['confidences']['peso']) / 4
                    
                    if avg_confidence >= 0.8:
                        confidence_level = 'high'
                    elif avg_confidence >= 0.6:
                        confidence_level = 'medium'
                    else:
                        confidence_level = 'low'
                    
                    email_context = {
                        'user_name': request.user.get_full_name() or request.user.username,
                        'user_email': request.user.email,
                        'analysis_id': cacao_prediction.id if cacao_prediction else 'N/A',
                        'confidence': round(avg_confidence * 100, 1),
                        'confidence_level': confidence_level,
                        'alto_mm': result['alto_mm'],
                        'ancho_mm': result['ancho_mm'],
                        'grosor_mm': result['grosor_mm'],
                        'peso_g': result['peso_g'],
                        'confidence_alto': round(result['confidences']['alto'] * 100, 1),
                        'confidence_ancho': round(result['confidences']['ancho'] * 100, 1),
                        'confidence_grosor': round(result['confidences']['grosor'] * 100, 1),
                        'confidence_peso': round(result['confidences']['peso'] * 100, 1),
                        'processing_time_ms': prediction_time_ms,
                        'model_version': result.get('debug', {}).get('model_version', 'v1.0'),
                        'analysis_date': timezone.now().strftime('%d/%m/%Y %H:%M'),
                        'crop_url': result['crop_url'],
                        'defects_detected': []  # TODO: Implementar detección de defectos
                    }
                    
                    email_result = send_email_notification(
                        user_email=request.user.email,
                        notification_type='analysis_complete',
                        context=email_context
                    )
                    
                    if email_result['success']:
                        logger.info(f"Email de análisis completado enviado a {request.user.email}")
                    else:
                        logger.warning(f"Error enviando email de análisis: {email_result.get('error')}")
                        
                except Exception as e:
                    logger.error(f"Error en envío de email de análisis: {e}")
                
                # Validar respuesta con serializer
                serializer = ScanMeasureResponseSerializer(data=response_data)
                if serializer.is_valid():
                    total_time = time.time() - start_time
                    logger.info(f"Predicción completada en {total_time:.2f}s para imagen {filename}")
                    
                    # Log información sobre guardado en BD
                    if save_success and pred_success:
                        logger.info(f"Datos guardados correctamente en BD - Imagen ID: {cacao_image.id}, Predicción ID: {cacao_prediction.id}")
                    else:
                        logger.warning(f"Problemas guardando en BD - Imagen: {save_success}, Predicción: {pred_success}")
                    
                    return Response(serializer.validated_data, status=status.HTTP_200_OK)
                else:
                    logger.error(f"Error de serialización: {serializer.errors}")
                    return Response({
                        'error': 'Error interno de serialización',
                        'status': 'error'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            except Exception as e:
                logger.error(f"Error en predicción: {e}")
                return Response({
                    'error': f'Error en predicción: {str(e)}',
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Error general en endpoint: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    def get(self, request):
        """
        Devuelve el estado de los modelos entrenados.
        """
        try:
            predictor = get_predictor()
            model_info = predictor.get_model_info()
            
            if model_info['status'] == 'loaded':
                return Response({
                    'yolo_segmentation': 'loaded',
                    'regression_models': {
                        target: 'loaded' if target in model_info['models'] else 'not_loaded'
                        for target in ['alto', 'ancho', 'grosor', 'peso']
                    },
                    'device': model_info['device'],
                    'models_info': model_info['models'],
                    'status': 'ready'
                })
            else:
                return Response({
                    'yolo_segmentation': 'not_loaded',
                    'regression_models': {
                        'alto': 'not_loaded',
                        'ancho': 'not_loaded', 
                        'grosor': 'not_loaded',
                        'peso': 'not_loaded'
                    },
                    'status': 'not_loaded'
                })
                
        except Exception as e:
            logger.error(f"Error obteniendo estado de modelos: {e}")
            return Response({
                'error': str(e),
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    def get(self, request):
        """
        Valida el dataset y devuelve estadísticas.
        """
        try:
            loader = CacaoDatasetLoader()
            stats = loader.get_dataset_stats()
            
            return Response({
                'valid': len(stats.get('missing_images', [])) == 0,
                'stats': stats,
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"Error validando dataset: {e}")
            return Response({
                'valid': False,
                'error': str(e),
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    def post(self, request):
        """
        Carga los artefactos de ML.
        """
        try:
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
                
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
            return Response({
                'error': str(e),
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
        
        try:
            logger.info("🚀 Iniciando inicialización automática completa del sistema")
            
            # Paso 1: Validar dataset
            logger.info("Paso 1: Validando dataset...")
            try:
                from ml.data.dataset_loader import CacaoDatasetLoader
                loader = CacaoDatasetLoader()
                stats = loader.get_dataset_stats()
                
                if stats['valid_records'] == 0:
                    return Response({
                        'error': 'No hay registros válidos en el dataset. Verificar CSV e imágenes.',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                steps_completed.append("✅ Dataset validado")
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
                    
                    steps_completed.append("✅ Crops generados")
                    logger.info("Crops generados exitosamente")
                else:
                    steps_completed.append("✅ Crops ya existen")
                    logger.info("Crops ya existen, saltando generación")
                    
            except Exception as e:
                logger.warning(f"Advertencia en generación de crops: {e}")
                steps_completed.append("⚠️ Crops con advertencias")
            
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
                        steps_completed.append("✅ Modelos entrenados")
                        logger.info("Modelos entrenados exitosamente")
                    else:
                        return Response({
                            'error': 'Error en entrenamiento de modelos',
                            'status': 'error'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
                    steps_completed.append("✅ Modelos ya existen")
                    logger.info("Modelos ya existen, saltando entrenamiento")
                    
            except Exception as e:
                logger.error(f"Error en entrenamiento de modelos: {e}")
                return Response({
                    'error': f'Error entrenando modelos: {str(e)}',
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Paso 4: Cargar modelos
            logger.info("Paso 4: Cargando modelos...")
            try:
                success = load_artifacts()
                
                if success:
                    steps_completed.append("✅ Modelos cargados")
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
            steps_completed.append("🎉 Sistema listo para predicciones")
            
            logger.info(f"✅ Inicialización automática completada en {total_time:.2f}s")
            
            return Response({
                'message': 'Sistema inicializado automáticamente y listo para predicciones',
                'status': 'success',
                'steps_completed': steps_completed,
                'total_time_seconds': round(total_time, 2),
                'ready_for_predictions': True
            })
            
        except Exception as e:
            logger.error(f"Error en inicialización automática: {e}")
            return Response({
                'error': f'Error en inicialización automática: {str(e)}',
                'status': 'error',
                'steps_completed': steps_completed
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vistas de autenticación
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

# VISTAS PÚBLICAS (AllowAny): LoginView, RegisterView
# VISTAS PRIVADAS (IsAuthenticated): Todas las demás


class LoginView(APIView):
    """
    Endpoint para login de usuario.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Autentica un usuario y devuelve un token de acceso",
        operation_summary="Login de usuario",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login exitoso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': UserSerializer,
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Autentica un usuario y devuelve tokens JWT.
        """
        try:
            serializer = LoginSerializer(data=request.data)
            
            if serializer.is_valid():
                user = serializer.validated_data['user']
                
                # Generar tokens JWT
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                
                # Login en la sesión
                login(request, user)
                
                return create_success_response(
                    message='Login exitoso',
                    data={
                        'access': str(access_token),
                        'refresh': str(refresh),
                        'user': UserSerializer(user).data,
                        'access_expires_at': access_token['exp'],
                        'refresh_expires_at': refresh['exp']
                    }
                )
            
            return create_error_response(
                message='Credenciales inválidas',
                error_type='invalid_credentials',
                status_code=status.HTTP_401_UNAUTHORIZED,
                details=serializer.errors
            )
        except Exception as e:
            logger.error(f"Error en LoginView: {str(e)}", exc_info=True)
            return create_error_response(
                message='Error interno del servidor',
                error_type='internal_server_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegisterView(APIView):
    """
    Endpoint para registro de usuario.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Registra un nuevo usuario en el sistema",
        operation_summary="Registro de usuario",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Usuario creado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': UserSerializer,
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Registra un nuevo usuario y genera tokens JWT automáticamente.
        """
        # Crear una copia de los datos y eliminar el campo 'role' si viene del frontend
        data = request.data.copy()
        data.pop('role', None)  # Elimina si viene en la solicitud
        
        serializer = RegisterSerializer(data=data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Crear token de verificación de email
            verification_token = EmailVerificationToken.create_for_user(user)
            
            # Enviar email de verificación
            try:
                from django.conf import settings
                from .email_service import send_custom_email
                
                verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token.token}"
                
                # Contenido HTML del email
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4CAF50;">¡Bienvenido a CacaoScan, {user.get_full_name() or user.username}!</h2>
                        <p>Gracias por registrarte en nuestra plataforma. Para completar tu registro, por favor verifica tu dirección de correo electrónico haciendo clic en el siguiente enlace:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Verificar mi correo</a>
                        </div>
                        <p>O copia y pega este enlace en tu navegador:</p>
                        <p style="word-break: break-all; color: #666;">{verification_url}</p>
                        <p style="margin-top: 30px; font-size: 12px; color: #999;">Este enlace expirará en 24 horas.</p>
                        <p style="font-size: 12px; color: #999;">Si no creaste esta cuenta, puedes ignorar este correo.</p>
                    </div>
                </body>
                </html>
                """
                
                # Contenido de texto plano
                text_content = f"""
Bienvenido a CacaoScan, {user.get_full_name() or user.username}!

Gracias por registrarte en nuestra plataforma. Para completar tu registro, por favor verifica tu dirección de correo electrónico visitando el siguiente enlace:

{verification_url}

Este enlace expirará en 24 horas.

Si no creaste esta cuenta, puedes ignorar este correo.
                """
                
                send_custom_email(
                    to_emails=[user.email],
                    subject="Verifica tu correo electrónico - CacaoScan",
                    html_content=html_content,
                    text_content=text_content
                )
                
                logger.info(f"Email de verificación enviado a {user.email}")
            except Exception as e:
                logger.error(f"Error enviando email de verificación: {e}")
                # No fallar el registro si falla el envío de email
            
            # NO hacer auto-login, el usuario debe verificar su email primero
            return create_success_response(
                message='Usuario registrado exitosamente. Por favor verifica tu correo electrónico para activar tu cuenta.',
                data={
                    'user': UserSerializer(user).data,
                    'verification_required': True,
                    'email': user.email,
                    'verification_token': str(verification_token.token) if settings.DEBUG else None  # Solo en desarrollo
                },
                status_code=status.HTTP_201_CREATED
            )
        
        return create_error_response(
            message='Error en los datos proporcionados',
            error_type='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
        )


class LogoutView(APIView):
    """
    Endpoint para logout de usuario.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Cierra la sesión del usuario y elimina el token",
        operation_summary="Logout de usuario",
        responses={
            200: openapi.Response(
                description="Logout exitoso",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Cierra la sesión del usuario y blacklistea el token de refresh.
        """
        try:
            # Obtener el token de refresh del cuerpo de la petición
            refresh_token = request.data.get('refresh')
            
            if refresh_token:
                # Blacklistear el token de refresh
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Logout de la sesión
            logout(request)
            
            return Response({
                'message': 'Logout exitoso'
            })
        except TokenError:
            return Response({
                'error': 'Token inválido',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'Error en logout: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    Endpoint para obtener perfil del usuario actual.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la información del perfil del usuario autenticado",
        operation_summary="Perfil de usuario",
        responses={
            200: UserSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def get(self, request):
        """
        Obtiene el perfil del usuario actual.
        """
        return Response(UserSerializer(request.user).data)


class RefreshTokenView(APIView):
    """
    Endpoint para refrescar token de acceso JWT.
    """
    permission_classes = [AllowAny]  # Cambiar a AllowAny porque necesitamos el refresh token
    
    @swagger_auto_schema(
        operation_description="Refresca el token de acceso usando el token de refresh",
        operation_summary="Refrescar token JWT",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Token de refresh')
            },
            required=['refresh']
        ),
        responses={
            200: openapi.Response(
                description="Token refrescado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        'access_expires_at': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Refresca el token de acceso usando el token de refresh.
        """
        try:
            refresh_token = request.data.get('refresh')
            
            if not refresh_token:
                return create_error_response(
                    message='Token de refresh requerido',
                    error_type='missing_refresh_token',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Crear nuevo token de acceso usando el refresh token
            refresh = RefreshToken(refresh_token)
            new_access_token = refresh.access_token
            
            return create_success_response(
                message='Token refrescado exitosamente',
                data={
                    'access': str(new_access_token),
                    'refresh': str(refresh),
                    'access_expires_at': new_access_token['exp']
                }
            )
            
        except TokenError as e:
            return create_error_response(
                message='Token de refresh inválido o expirado',
                error_type='invalid_refresh_token',
                status_code=status.HTTP_400_BAD_REQUEST,
                details={'error': str(e)}
            )
        except Exception as e:
            return create_error_response(
                message='Error refrescando token',
                error_type='refresh_error',
                status_code=status.HTTP_400_BAD_REQUEST,
                details={'error': str(e)}
            )


class ChangePasswordView(APIView):
    """
    Endpoint para cambiar la contraseña del usuario autenticado.
    Requiere autenticación y validación de la contraseña actual.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Cambiar la contraseña del usuario autenticado.
        
        Requiere:
        - old_password: Contraseña actual
        - new_password: Nueva contraseña (mínimo 8 caracteres, mayúscula, minúscula, número)
        - confirm_password: Confirmación de la nueva contraseña
        """
        from .serializers import ChangePasswordSerializer
        
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            # Verificar que la contraseña actual sea correcta
            if not user.check_password(old_password):
                return create_error_response(
                    message='La contraseña actual es incorrecta',
                    error_type='invalid_old_password',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={'old_password': ['La contraseña actual no es correcta.']}
                )
            
            # Cambiar la contraseña
            try:
                user.set_password(new_password)
                user.save()
                
                # Log de auditoría si está disponible
                try:
                    from audit.models import ActivityLog
                    ActivityLog.objects.create(
                        user=user,
                        action='change_password',
                        resource_type='user',
                        resource_id=str(user.id),
                        details={'timestamp': timezone.now().isoformat()},
                        timestamp=timezone.now()
                    )
                except Exception:
                    pass  # Si no hay módulo de auditoría, continuar
                
                return create_success_response(
                    message='Contraseña cambiada exitosamente',
                    data={'user_id': user.id}
                )
                
            except Exception as e:
                logger.error(f"Error cambiando contraseña para usuario {user.id}: {str(e)}")
                return create_error_response(
                    message='Error al cambiar la contraseña',
                    error_type='password_change_error',
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # Si hay errores de validación, devolverlos
        return create_error_response(
            message='Errores de validación',
            error_type='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
        )


class ImagesListView(APIView, ImagePermissionMixin):
    """
    Endpoint para listar imágenes procesadas con paginación y filtros.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la lista de imágenes procesadas por el usuario con paginación y filtros",
        operation_summary="Lista de imágenes",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página (máximo 100)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('region', openapi.IN_QUERY, description="Filtrar por región", type=openapi.TYPE_STRING),
            openapi.Parameter('finca', openapi.IN_QUERY, description="Filtrar por finca", type=openapi.TYPE_STRING),
            openapi.Parameter('processed', openapi.IN_QUERY, description="Filtrar por estado de procesamiento", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Buscar en notas y metadatos", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Fecha desde (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Fecha hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Lista de imágenes obtenida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING),
                        'page': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def get(self, request):
        """
        Obtiene la lista de imágenes procesadas con paginación y filtros.
        """
        try:
            # Obtener parámetros de consulta
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)  # Máximo 100 por página
            region = request.GET.get('region')
            finca = request.GET.get('finca')
            processed = request.GET.get('processed')
            search = request.GET.get('search')
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')
            
            # Construir queryset base según permisos
            queryset = self.get_user_images_queryset(request.user)
            
            # Aplicar filtros
            if region:
                queryset = queryset.filter(region__icontains=region)
            
            if finca:
                queryset = queryset.filter(finca__icontains=finca)
            
            if processed is not None:
                processed_bool = processed.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(processed=processed_bool)
            
            if search:
                queryset = queryset.filter(
                    Q(notas__icontains=search) |
                    Q(finca__icontains=search) |
                    Q(region__icontains=search) |
                    Q(lote_id__icontains=search) |
                    Q(variedad__icontains=search)
                )
            
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
            
            # Ordenar por fecha de creación (más recientes primero)
            queryset = queryset.order_by('-created_at')
            
            # Paginación
            paginator = Paginator(queryset, page_size)
            total_pages = paginator.num_pages
            
            # Validar página
            if page > total_pages and total_pages > 0:
                return Response({
                    'error': f'Página {page} no existe. Total de páginas: {total_pages}',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            page_obj = paginator.get_page(page)
            
            # Serializar resultados
            serializer = CacaoImageSerializer(page_obj.object_list, many=True, context={'request': request})
            
            # Preparar respuesta
            response_data = {
                'results': serializer.data,
                'count': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'next': None,
                'previous': None
            }
            
            # URLs de paginación
            if page_obj.has_next():
                response_data['next'] = f"{request.build_absolute_uri()}?page={page + 1}&page_size={page_size}"
            
            if page_obj.has_previous():
                response_data['previous'] = f"{request.build_absolute_uri()}?page={page - 1}&page_size={page_size}"
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'error': 'Parámetros de consulta inválidos',
                'status': 'error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error obteniendo lista de imágenes: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImageDetailView(APIView, ImagePermissionMixin):
    """
    Endpoint para obtener detalles de una imagen específica con acceso por owner/admin.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los detalles completos de una imagen específica incluyendo predicción",
        operation_summary="Detalles de imagen",
        responses={
            200: openapi.Response(
                description="Detalles de imagen obtenidos exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def get(self, request, image_id):
        """
        Obtiene los detalles completos de una imagen específica.
        Solo el propietario o un admin pueden acceder.
        """
        try:
            # Obtener imagen
            try:
                image = CacaoImage.objects.select_related('user', 'prediction').get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar permisos de acceso
            if not self.can_access_image(request.user, image):
                return Response({
                    'error': 'No tienes permisos para acceder a esta imagen',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Serializar imagen con predicción
            serializer = CacaoImageDetailSerializer(image, context={'request': request})
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo detalles de imagen {image_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImagesStatsView(APIView, ImagePermissionMixin):
    """
    Endpoint para obtener estadísticas detalladas de imágenes procesadas.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas detalladas de imágenes procesadas por el usuario",
        operation_summary="Estadísticas de imágenes",
        responses={
            200: openapi.Response(
                description="Estadísticas obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            401: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def get(self, request):
        """
        Obtiene estadísticas detalladas de imágenes procesadas.
        """
        try:
            # Obtener queryset base según permisos
            user_images = self.get_user_images_queryset(request.user)
            
            # Estadísticas básicas
            total_images = user_images.count()
            processed_images = user_images.filter(processed=True).count()
            unprocessed_images = total_images - processed_images
            
            # Estadísticas por fecha
            from django.utils import timezone
            from datetime import timedelta
            
            today = timezone.now().date()
            this_week = today - timedelta(days=7)
            this_month = today - timedelta(days=30)
            
            processed_today = user_images.filter(
                created_at__date=today, 
                processed=True
            ).count()
            
            processed_this_week = user_images.filter(
                created_at__date__gte=this_week,
                processed=True
            ).count()
            
            processed_this_month = user_images.filter(
                created_at__date__gte=this_month,
                processed=True
            ).count()
            
            # Estadísticas de predicciones
            predictions = CacaoPrediction.objects.filter(image__user_id=request.user.id)
            
            # Calcular promedio de confidence manualmente ya que es una propiedad
            avg_confidence = 0
            if predictions.exists():
                confidences = []
                for pred in predictions:
                    confidences.append(float(pred.average_confidence))
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            avg_processing_time = predictions.aggregate(
                avg_time=Avg('processing_time_ms')
            )['avg_time'] or 0
            
            # Estadísticas por región
            region_stats = user_images.values('region').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True))
            ).order_by('-count')
            
            # Estadísticas por finca
            finca_stats = user_images.values('finca').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True))
            ).order_by('-count')[:10]  # Top 10 fincas
            
            # Estadísticas de dimensiones promedio
            avg_dimensions = predictions.aggregate(
                avg_alto=Avg('alto_mm'),
                avg_ancho=Avg('ancho_mm'),
                avg_grosor=Avg('grosor_mm'),
                avg_peso=Avg('peso_g')
            )
            
            # Preparar respuesta
            stats = {
                'total_images': total_images,
                'processed_images': processed_images,
                'unprocessed_images': unprocessed_images,
                'processed_today': processed_today,
                'processed_this_week': processed_this_week,
                'processed_this_month': processed_this_month,
                'average_confidence': round(float(avg_confidence), 3),
                'average_processing_time_ms': round(float(avg_processing_time), 0),
                'region_stats': list(region_stats),
                'top_fincas': list(finca_stats),
                'average_dimensions': {
                    'alto_mm': round(float(avg_dimensions['avg_alto'] or 0), 2),
                    'ancho_mm': round(float(avg_dimensions['avg_ancho'] or 0), 2),
                    'grosor_mm': round(float(avg_dimensions['avg_grosor'] or 0), 2),
                    'peso_g': round(float(avg_dimensions['avg_peso'] or 0), 2)
                }
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo estadísticas de imágenes: {e}")
            # Retornar datos vacíos en lugar de 500
            return Response({
                'total_images': 0,
                'processed_images': 0,
                'unprocessed_images': 0,
                'processed_today': 0,
                'processed_this_week': 0,
                'processed_this_month': 0,
                'average_confidence': 0,
                'average_processing_time_ms': 0,
                'region_stats': [],
                'top_fincas': [],
                'average_dimensions': {
                    'alto_mm': 0,
                    'ancho_mm': 0,
                    'grosor_mm': 0,
                    'peso_g': 0
                }
            }, status=status.HTTP_200_OK)


# Vistas de verificación de email
class EmailVerificationView(APIView):
    """
    Endpoint para verificar email con token.
    Soporta tanto POST (con token en body) como GET (con token en URL).
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verifica un email usando el token enviado por correo (POST con token en body)",
        operation_summary="Verificar email (POST)",
        request_body=EmailVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Email verificado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Verificar email con token (POST con token en body).
        """
        serializer = EmailVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            token_uuid = serializer.validated_data['token']
            return self._verify_token(token_uuid)
        
        return create_error_response(
            message='Datos de verificación inválidos',
            error_type='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
        )
    
    @swagger_auto_schema(
        operation_description="Verifica un email usando el token desde la URL (GET con token en path)",
        operation_summary="Verificar email (GET)",
        manual_parameters=[
            openapi.Parameter('token', openapi.IN_PATH, description="Token de verificación", type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        ],
        responses={
            200: openapi.Response(
                description="Email verificado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def get(self, request, token=None):
        """
        Verificar email con token (GET con token en URL).
        """
        if not token:
            return create_error_response(
                message='Token de verificación requerido',
                error_type='missing_token',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        return self._verify_token(token)
    
    def _verify_token(self, token_uuid):
        """Método helper para verificar el token."""
        try:
            import uuid
            token_obj = EmailVerificationToken.get_valid_token(str(token_uuid))
        except (ValueError, TypeError):
            return create_error_response(
                message='Formato de token inválido',
                error_type='invalid_token_format',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if token_obj:
            if token_obj.is_verified:
                return create_error_response(
                    message='Este enlace ya fue utilizado',
                    error_type='token_already_used',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            if token_obj.is_expired:
                return create_error_response(
                    message='El enlace de verificación ha expirado',
                    error_type='token_expired',
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar el token (activa el usuario)
            token_obj.verify()
            
            return create_success_response(
                message='Correo verificado correctamente. Ya puedes iniciar sesión.',
                data={
                    'user': UserSerializer(token_obj.user).data
                }
            )
        else:
            return create_error_response(
                message='Token inválido o expirado',
                error_type='invalid_token',
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationView(APIView):
    """
    Endpoint para reenviar verificación de email.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Reenvía el token de verificación de email",
        operation_summary="Reenviar verificación",
        request_body=ResendVerificationSerializer,
        responses={
            200: openapi.Response(
                description="Token de verificación reenviado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Reenviar token de verificación de email.
        """
        serializer = ResendVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Crear nuevo token de verificación
            token_obj = EmailVerificationToken.create_for_user(user)
            
            # Enviar email de verificación
            try:
                from django.conf import settings
                from .email_service import send_custom_email
                
                verification_url = f"{settings.FRONTEND_URL}/verify-email/{token_obj.token}"
                
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4CAF50;">Verifica tu correo electrónico - CacaoScan</h2>
                        <p>Hola {user.get_full_name() or user.username},</p>
                        <p>Has solicitado un nuevo enlace de verificación. Por favor verifica tu dirección de correo electrónico haciendo clic en el siguiente enlace:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Verificar mi correo</a>
                        </div>
                        <p>O copia y pega este enlace en tu navegador:</p>
                        <p style="word-break: break-all; color: #666;">{verification_url}</p>
                        <p style="margin-top: 30px; font-size: 12px; color: #999;">Este enlace expirará en 24 horas.</p>
                    </div>
                </body>
                </html>
                """
                
                text_content = f"""
Verifica tu correo electrónico - CacaoScan

Hola {user.get_full_name() or user.username},

Has solicitado un nuevo enlace de verificación. Por favor verifica tu dirección de correo electrónico visitando el siguiente enlace:

{verification_url}

Este enlace expirará en 24 horas.
                """
                
                send_custom_email(
                    to_emails=[user.email],
                    subject="Verifica tu correo electrónico - CacaoScan",
                    html_content=html_content,
                    text_content=text_content
                )
                
                logger.info(f"Email de verificación reenviado a {user.email}")
            except Exception as e:
                logger.error(f"Error reenviando email de verificación: {e}")
            
            return create_success_response(
                message=f'Token de verificación enviado a {email}',
                data={
                    'expires_at': token_obj.expires_at.isoformat()
                }
            )
        
        return create_error_response(
            message='Email inválido',
            error_type='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
        )


# Vistas de pre-registro (verificación previa)
class PreRegisterView(APIView):
    """
    Endpoint para pre-registro: guarda datos sin crear usuario hasta verificar correo.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Guarda datos de registro pendientes de verificación de correo",
        operation_summary="Pre-registro de usuario",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['email', 'password']
        ),
        responses={
            201: openapi.Response(
                description="Registro pendiente creado, email de verificación enviado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Crea un registro pendiente y envía email de verificación.
        El usuario NO se crea hasta que verifique el correo.
        """
        from personas.models import PendingRegistration
        from django.contrib.auth.models import User
        from django.template.loader import render_to_string
        from django.conf import settings
        from .email_service import send_custom_email
        
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        # Validaciones básicas
        if not email or not password:
            return create_error_response(
                message='Email y contraseña son requeridos',
                error_type='validation_error',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar que el email no esté registrado
        if User.objects.filter(email=email).exists():
            return create_error_response(
                message='Este email ya está registrado',
                error_type='email_exists',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si ya existe un registro pendiente
        existing_pending = PendingRegistration.objects.filter(email=email, is_verified=False).first()
        if existing_pending:
            # Si el token no ha expirado, reenviar el email
            if not existing_pending.is_expired():
                # Reenviar email de verificación
                verification_url = f"{settings.FRONTEND_URL}/verify-email/{existing_pending.verification_token}"
                
                html_content = render_to_string('emails/verify_email.html', {
                    'verification_url': verification_url,
                    'user_name': first_name or email.split('@')[0],
                    'frontend_url': settings.FRONTEND_URL
                })
                
                text_content = f"""
Bienvenido a CacaoScan, {first_name or email.split('@')[0]}!

Gracias por registrarte. Para completar tu registro, verifica tu correo visitando:
{verification_url}

Este enlace expirará en 24 horas.
                """
                
                try:
                    send_custom_email(
                        to_emails=[email],
                        subject="Verifica tu correo electrónico - CacaoScan",
                        html_content=html_content,
                        text_content=text_content
                    )
                except Exception as e:
                    logger.error(f"Error reenviando email: {e}")
                
                return create_success_response(
                    message='Se ha reenviado el enlace de verificación a tu correo electrónico.',
                    data={'email': email},
                    status_code=status.HTTP_200_OK
                )
            else:
                # Eliminar registro expirado
                existing_pending.delete()
        
        # Crear nuevo registro pendiente
        pending_reg = PendingRegistration.objects.create(
            email=email,
            data={
                'email': email,
                'password': password,
                'first_name': first_name,
                'last_name': last_name,
                **{k: v for k, v in request.data.items() if k not in ['email', 'password', 'first_name', 'last_name']}
            }
        )
        
        # Enviar email de verificación
        verification_url = f"{settings.FRONTEND_URL}/verify-email/{pending_reg.verification_token}"
        
        html_content = render_to_string('emails/verify_email.html', {
            'verification_url': verification_url,
            'user_name': first_name or email.split('@')[0],
            'frontend_url': settings.FRONTEND_URL
        })
        
        text_content = f"""
Bienvenido a CacaoScan, {first_name or email.split('@')[0]}!

Gracias por registrarte en nuestra plataforma. Para completar tu registro, verifica tu dirección de correo electrónico visitando el siguiente enlace:

{verification_url}

Este enlace expirará en 24 horas.

Si no creaste esta cuenta, puedes ignorar este correo.

Equipo CacaoScan · Proyecto SENNOVA · SENA Guaviare
        """
        
        try:
            send_custom_email(
                to_emails=[email],
                subject="Verifica tu correo electrónico - CacaoScan",
                html_content=html_content,
                text_content=text_content
            )
            logger.info(f"Email de verificación enviado a {email}")
        except Exception as e:
            logger.error(f"Error enviando email de verificación: {e}")
            # Eliminar registro pendiente si falla el envío
            pending_reg.delete()
            return create_error_response(
                message='Error al enviar el email de verificación. Por favor intenta nuevamente.',
                error_type='email_send_error',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return create_success_response(
            message='Se ha enviado un enlace de verificación a tu correo electrónico.',
            data={'email': email},
            status_code=status.HTTP_201_CREATED
        )


class VerifyEmailPreRegistrationView(APIView):
    """
    Endpoint para verificar email y crear el usuario final después de pre-registro.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verifica el email y crea el usuario final a partir del registro pendiente",
        operation_summary="Verificar email y crear usuario",
        manual_parameters=[
            openapi.Parameter('token', openapi.IN_PATH, description="Token de verificación", type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID),
        ],
        responses={
            200: openapi.Response(
                description="Usuario creado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def get(self, request, token=None):
        """
        Verifica el token y crea el usuario final.
        """
        from personas.models import PendingRegistration
        from personas.serializers import PersonaRegistroSerializer
        from django.db import transaction
        
        if not token:
            return create_error_response(
                message='Token de verificación requerido',
                error_type='missing_token',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            import uuid
            token_uuid = uuid.UUID(str(token))
        except (ValueError, TypeError):
            return create_error_response(
                message='Formato de token inválido',
                error_type='invalid_token_format',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            pending_reg = PendingRegistration.objects.get(verification_token=token_uuid)
        except PendingRegistration.DoesNotExist:
            return create_error_response(
                message='Token inválido o expirado',
                error_type='invalid_token',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si ya fue verificado
        if pending_reg.is_verified:
            return create_error_response(
                message='Este enlace ya fue utilizado',
                error_type='token_already_used',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar si expiró
        if pending_reg.is_expired():
            pending_reg.delete()
            return create_error_response(
                message='El enlace de verificación ha expirado. Por favor registrate nuevamente.',
                error_type='token_expired',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Crear el usuario final con los datos guardados
        with transaction.atomic():
            user_data = pending_reg.data.copy()
            password = user_data.pop('password')
            
            from django.contrib.auth.models import User
            user = User.objects.create_user(
                username=user_data['email'],
                email=user_data['email'],
                password=password,
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                is_active=True  # Usuario activo desde el inicio
            )
            
            # Si hay datos de persona, crear el registro de persona
            if 'tipo_documento' in user_data or 'numero_documento' in user_data:
                try:
                    persona_data = {k: v for k, v in user_data.items() if k not in ['email', 'password', 'first_name', 'last_name']}
                    persona_data['email'] = user.email
                    persona_data['password'] = password
                    persona_serializer = PersonaRegistroSerializer(data=persona_data)
                    if persona_serializer.is_valid():
                        persona = persona_serializer.save()
                    else:
                        logger.warning(f"Error creando persona para usuario {user.email}: {persona_serializer.errors}")
                except Exception as e:
                    logger.warning(f"Error creando persona: {e}")
            
            # Marcar registro pendiente como verificado
            pending_reg.verify()
            
            logger.info(f"Usuario {user.email} creado exitosamente después de verificación")
            
            return create_success_response(
                message='Correo verificado correctamente. Ya puedes iniciar sesión.',
                data={
                    'user': UserSerializer(user).data
                }
            )
        
        return create_error_response(
            message='Error al crear el usuario',
            error_type='user_creation_error',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Vistas de recuperación de contraseña
class ForgotPasswordView(APIView):
    """
    Endpoint para solicitar recuperación de contraseña.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Envía un email con token para recuperar contraseña",
        operation_summary="Recuperar contraseña",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email')
            },
            required=['email']
        ),
        responses={
            200: openapi.Response(
                description="Email de recuperación enviado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Solicitar recuperación de contraseña.
        """
        email = request.data.get('email')
        
        if not email:
            return create_error_response(
                message='Email es requerido',
                error_type='validation_error',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(email=email)
            
            # Crear token de recuperación (usando el mismo modelo de verificación)
            reset_token = EmailVerificationToken.create_for_user(user)
            
            # Enviar email de restablecimiento de contraseña
            try:
                from .email_service import send_email_notification
                email_context = {
                    'user_name': user.get_full_name() or user.username,
                    'user_email': user.email,
                    'token': str(reset_token.token),
                    'reset_url': f"{request.build_absolute_uri('/')}auth/reset-password/?token={reset_token.token}",
                    'token_expiry_hours': 24  # Token válido por 24 horas
                }
                email_result = send_email_notification(
                    user_email=user.email,
                    notification_type='password_reset',
                    context=email_context
                )
                if email_result['success']:
                    logger.info(f"Email de restablecimiento enviado a {user.email}")
                else:
                    logger.error(f"Error enviando email de restablecimiento: {email_result.get('error')}")
            except Exception as e:
                logger.error(f"Error en envío de email de restablecimiento: {e}")
            
            return create_success_response(
                message=f'Instrucciones de recuperación enviadas a {email}',
                data={
                    'token': str(reset_token.token),  # Solo para desarrollo
                    'expires_at': reset_token.expires_at.isoformat()
                }
            )
            
        except User.DoesNotExist:
            # Por seguridad, no revelar si el email existe o no
            return create_success_response(
                message='Si el email existe, recibirás instrucciones de recuperación'
            )


class ResetPasswordView(APIView):
    """
    Endpoint para restablecer contraseña con token.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Restablece la contraseña usando el token de recuperación",
        operation_summary="Restablecer contraseña",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'token': openapi.Schema(type=openapi.TYPE_STRING),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['token', 'new_password', 'confirm_password']
        ),
        responses={
            200: openapi.Response(
                description="Contraseña restablecida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Restablecer contraseña con token.
        """
        token_uuid = request.data.get('token')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([token_uuid, new_password, confirm_password]):
            return create_error_response(
                message='Token, nueva contraseña y confirmación son requeridos',
                error_type='validation_error',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return create_error_response(
                message='Las contraseñas no coinciden',
                error_type='validation_error',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar fortaleza de contraseña
        if len(new_password) < 8:
            return create_error_response(
                message='La contraseña debe tener al menos 8 caracteres',
                error_type='validation_error',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar token
        token_obj = EmailVerificationToken.get_valid_token(token_uuid)
        if not token_obj:
            return create_error_response(
                message='Token inválido o expirado',
                error_type='invalid_token',
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # Restablecer contraseña
        user = token_obj.user
        user.set_password(new_password)
        user.save()
        
        # Eliminar token usado
        token_obj.delete()
        
        return create_success_response(
            message='Contraseña restablecida exitosamente'
        )


# Vistas de gestión de usuarios (Admin)
class UserListView(APIView):
    """
    Endpoint para listar usuarios con filtros y paginación (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la lista de usuarios con filtros y paginación (solo admins)",
        operation_summary="Lista de usuarios",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página (máximo 100)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('role', openapi.IN_QUERY, description="Filtrar por rol (admin, analyst, farmer)", type=openapi.TYPE_STRING),
            openapi.Parameter('is_active', openapi.IN_QUERY, description="Filtrar por estado activo", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('is_verified', openapi.IN_QUERY, description="Filtrar por estado de verificación", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Buscar en username, email, nombre", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Fecha de registro desde (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Fecha de registro hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Lista de usuarios obtenida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Usuarios']
    )
    def get(self, request):
        """
        Obtiene la lista de usuarios con filtros y paginación.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener parámetros de consulta
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)  # Máximo 100 por página
            role = request.GET.get('role')
            is_active = request.GET.get('is_active')
            is_verified = request.GET.get('is_verified')
            search = request.GET.get('search')
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')
            
            # Construir queryset base (evitar select_related/prefetch a relaciones no garantizadas)
            queryset = User.objects.all().prefetch_related('groups')
            
            # Aplicar filtros
            if role:
                if role == 'admin':
                    queryset = queryset.filter(Q(is_superuser=True) | Q(is_staff=True))
                elif role == 'analyst':
                    queryset = queryset.filter(groups__name='analyst')
                elif role == 'farmer':
                    queryset = queryset.filter(
                        ~Q(is_superuser=True),
                        ~Q(is_staff=True),
                        ~Q(groups__name='analyst')
                    )
            
            if is_active is not None:
                active_bool = is_active.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(is_active=active_bool)
            
            if is_verified is not None:
                verified_bool = is_verified.lower() in ['true', '1', 'yes']
                if verified_bool:
                    queryset = queryset.filter(auth_email_token__is_verified=True)
                else:
                    queryset = queryset.filter(
                        Q(auth_email_token__is_verified=False) | 
                        Q(auth_email_token__isnull=True)
                    )
            
            if search:
                queryset = queryset.filter(
                    Q(username__icontains=search) |
                    Q(email__icontains=search) |
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search)
                )
            
            if date_from:
                queryset = queryset.filter(date_joined__date__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(date_joined__date__lte=date_to)
            
            # Ordenar por fecha de registro (más recientes primero)
            queryset = queryset.order_by('-date_joined')
            
            # Paginación
            paginator = Paginator(queryset, page_size)
            total_pages = paginator.num_pages
            
            # Validar página
            if page > total_pages and total_pages > 0:
                return Response({
                    'error': f'Página {page} no existe. Total de páginas: {total_pages}',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            page_obj = paginator.get_page(page)
            
            # Serializar resultados
            serializer = UserSerializer(page_obj.object_list, many=True)
            
            # Preparar respuesta
            response_data = {
                'results': serializer.data,
                'count': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'next': None,
                'previous': None
            }
            
            # URLs de paginación
            if page_obj.has_next():
                response_data['next'] = f"{request.build_absolute_uri()}?page={page + 1}&page_size={page_size}"
            
            if page_obj.has_previous():
                response_data['previous'] = f"{request.build_absolute_uri()}?page={page - 1}&page_size={page_size}"
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'error': 'Parámetros de consulta inválidos',
                'status': 'error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error obteniendo lista de usuarios: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class UserUpdateView(APIView):
    """
    Endpoint para actualizar información de un usuario (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Actualiza la información de un usuario específico (solo admins)",
        operation_summary="Actualizar usuario",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'is_staff': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'groups': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_STRING))
            }
        ),
        responses={
            200: openapi.Response(
                description="Usuario actualizado exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Usuarios']
    )
    def patch(self, request, user_id):
        """
        Actualiza la información de un usuario específico.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener usuario
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'error': 'Usuario no encontrado',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validar que no se puede desactivar a sí mismo
            if user == request.user and request.data.get('is_active') is False:
                return Response({
                    'error': 'No puedes desactivar tu propia cuenta',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Actualizar campos básicos
            if 'first_name' in request.data:
                user.first_name = request.data['first_name']
            
            if 'last_name' in request.data:
                user.last_name = request.data['last_name']
            
            if 'email' in request.data:
                # Verificar que el email no esté en uso por otro usuario
                if User.objects.filter(email=request.data['email']).exclude(id=user_id).exists():
                    return Response({
                        'error': 'Este email ya está en uso por otro usuario',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
                user.email = request.data['email']
                user.username = request.data['email']  # Mantener username = email
            
            if 'is_active' in request.data:
                user.is_active = request.data['is_active']
            
            if 'is_staff' in request.data:
                user.is_staff = request.data['is_staff']
            
            # Guardar cambios
            user.save()
            
            # Actualizar grupos si se proporcionan
            if 'groups' in request.data:
                group_names = request.data['groups']
                from django.contrib.auth.models import Group
                
                # Limpiar grupos existentes
                user.groups.clear()
                
                # Agregar nuevos grupos
                for group_name in group_names:
                    try:
                        group = Group.objects.get(name=group_name)
                        user.groups.add(group)
                    except Group.DoesNotExist:
                        logger.warning(f"Grupo '{group_name}' no encontrado")
            
            # Serializar usuario actualizado
            serializer = UserSerializer(user)
            
            return Response({
                'message': 'Usuario actualizado exitosamente',
                'user': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error actualizando usuario {user_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class UserDeleteView(APIView):
    """
    Endpoint para eliminar un usuario (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Elimina un usuario del sistema (solo admins)",
        operation_summary="Eliminar usuario",
        responses={
            200: openapi.Response(
                description="Usuario eliminado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'deleted_user': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Usuarios']
    )
    def delete(self, request, user_id):
        """
        Elimina un usuario del sistema.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener usuario
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'error': 'Usuario no encontrado',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Validaciones de seguridad
            if user == request.user:
                return Response({
                    'error': 'No puedes eliminar tu propia cuenta',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if user.is_superuser and not request.user.is_superuser:
                return Response({
                    'error': 'No tienes permisos para eliminar superusuarios',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Guardar información del usuario antes de eliminarlo
            user_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined.isoformat(),
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            }
            
            # Eliminar usuario (esto también eliminará el perfil y tokens relacionados)
            user.delete()
            
            logger.info(f"Usuario {user_data['username']} eliminado por admin {request.user.username}")
            
            return Response({
                'message': 'Usuario eliminado exitosamente',
                'deleted_user': user_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error eliminando usuario {user_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class UserStatsView(APIView):
    """
    Endpoint para obtener estadísticas de usuarios (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas de usuarios del sistema (solo admins)",
        operation_summary="Estadísticas de usuarios",
        responses={
            200: openapi.Response(
                description="Estadísticas obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
        },
        tags=['Usuarios']
    )
    def get(self, request):
        """
        Obtiene estadísticas de usuarios.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            from datetime import timedelta, datetime
            from django.utils import timezone
            from django.db.models import Count, Q
            
            # Estadísticas generales
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            inactive_users = total_users - active_users
            
            # Usuarios registrados hoy
            today = timezone.now().date()
            users_today = User.objects.filter(date_joined__date=today).count()
            
            # Usuarios en línea (últimos 5 minutos)
            five_minutes_ago = timezone.now() - timedelta(minutes=5)
            online_users = User.objects.filter(last_login__gte=five_minutes_ago).count()
            
            # Usuarios por rol
            admin_users = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True)).count()
            analyst_users = User.objects.filter(groups__name='analyst').distinct().count()
            farmer_users = User.objects.filter(
                ~Q(is_superuser=True),
                ~Q(is_staff=True),
                ~Q(groups__name='analyst')
            ).count()
            
            # Usuarios por estado de verificación
            verified_users = User.objects.filter(
                auth_email_token__is_verified=True
            ).count()
            
            # Usuarios nuevos esta semana
            this_week_start = today - timedelta(days=today.weekday())
            users_this_week = User.objects.filter(date_joined__date__gte=this_week_start).count()
            
            # Usuarios nuevos este mes
            this_month_start = today.replace(day=1)
            users_this_month = User.objects.filter(date_joined__date__gte=this_month_start).count()
            
            # Preparar respuesta
            stats = {
                'total': total_users,
                'active': active_users,
                'inactive': inactive_users,
                'online': online_users,
                'new_today': users_today,
                'new_this_week': users_this_week,
                'new_this_month': users_this_month,
                'by_role': {
                    'admin': admin_users,
                    'analyst': analyst_users,
                    'farmer': farmer_users
                },
                'verified': verified_users,
                'generated_at': timezone.now().isoformat()
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de usuarios: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class AdminStatsView(APIView):
    """
    Endpoint para obtener estadísticas globales del sistema (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas globales del sistema (solo admins)",
        operation_summary="Estadísticas del sistema",
        responses={
            200: openapi.Response(
                description="Estadísticas obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
        },
        tags=['Usuarios']
    )
    def get(self, request):
        """
        Obtiene estadísticas globales del sistema.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Estadísticas de usuarios
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            staff_users = User.objects.filter(is_staff=True).count()
            superusers = User.objects.filter(is_superuser=True).count()
            
            logger.info(f"📊 [AdminStatsView] Usuarios - Total: {total_users}, Activos: {active_users}, Staff: {staff_users}, Superusers: {superusers}")
            
            # Usuarios por rol
            analyst_users = User.objects.filter(groups__name='analyst').distinct().count()
            farmer_users = User.objects.filter(
                ~Q(is_superuser=True),
                ~Q(is_staff=True),
                ~Q(groups__name='analyst')
            ).count()
            
            # Usuarios verificados - usar auth_email_token (related_name correcto)
            try:
                verified_users = User.objects.filter(
                    auth_email_token__is_verified=True
                ).count()
            except Exception:
                # Si no existe el campo, contar solo usuarios activos
                verified_users = User.objects.filter(is_active=True).count()
            
            # Estadísticas de imágenes
            total_images = CacaoImage.objects.count()
            processed_images = CacaoImage.objects.filter(processed=True).count()
            unprocessed_images = total_images - processed_images
            logger.info(f"🖼️ [AdminStatsView] Imágenes - Total: {total_images}, Procesadas: {processed_images}, Sin procesar: {unprocessed_images}")
            
            # Estadísticas por fecha
            from datetime import timedelta
            today = timezone.now().date()
            this_week = today - timedelta(days=7)
            this_month = today - timedelta(days=30)
            
            users_this_week = User.objects.filter(date_joined__date__gte=this_week).count()
            users_this_month = User.objects.filter(date_joined__date__gte=this_month).count()
            
            images_this_week = CacaoImage.objects.filter(created_at__date__gte=this_week).count()
            images_this_month = CacaoImage.objects.filter(created_at__date__gte=this_month).count()
            
            # Datos de actividad por día para gráficos
            # Optimizado: usar agregaciones de Django para obtener datos de todos los días de una vez
            max_days_to_check = 30
            
            # Obtener conteos de imágenes por fecha usando agregación (más eficiente)
            from django.db.models import Count
            from django.db.models.functions import TruncDate
            
            # Imágenes por día (últimos 30 días)
            images_by_date = dict(
                CacaoImage.objects
                .filter(created_at__date__gte=today - timedelta(days=max_days_to_check))
                .annotate(date=TruncDate('created_at'))
                .values('date')
                .annotate(count=Count('id'))
                .values_list('date', 'count')
            )
            
            # Usuarios por día (últimos 30 días)
            users_by_date = dict(
                User.objects
                .filter(date_joined__date__gte=today - timedelta(days=max_days_to_check))
                .annotate(date=TruncDate('date_joined'))
                .values('date')
                .annotate(count=Count('id'))
                .values_list('date', 'count')
            )
            
            # Predicciones por día (últimos 30 días)
            predictions_by_date = {}
            if CacaoPrediction is not None:
                predictions_by_date = dict(
                    CacaoPrediction.objects
                    .filter(created_at__date__gte=today - timedelta(days=max_days_to_check))
                    .annotate(date=TruncDate('created_at'))
                    .values('date')
                    .annotate(count=Count('id'))
                    .values_list('date', 'count')
                )
            
            # Contar días únicos con actividad
            all_dates_with_activity = set()
            all_dates_with_activity.update(images_by_date.keys())
            all_dates_with_activity.update(users_by_date.keys())
            all_dates_with_activity.update(predictions_by_date.keys())
            
            days_with_activity_count = len(all_dates_with_activity)
            
            # Determinar cuántos días mostrar
            # Si hay más de 10 días con actividad, mostrar hasta 30 días
            # Si hay 10 o menos, mostrar solo los últimos 7 días
            if days_with_activity_count > 10:
                days_to_show = max_days_to_check  # Mostrar últimos 30 días
                logger.info(f"📊 [AdminStatsView] Más de 10 días con actividad ({days_with_activity_count}), mostrando últimos {days_to_show} días")
            else:
                days_to_show = 7
                logger.info(f"📊 [AdminStatsView] {days_with_activity_count} días con actividad, mostrando últimos 7 días")
            
            activity_by_day = []
            activity_labels = []
            
            for i in range(days_to_show - 1, -1, -1):  # Desde hace N días hasta hoy
                date = today - timedelta(days=i)
                
                # Obtener conteos del diccionario (más eficiente que queries individuales)
                images_count = images_by_date.get(date, 0)
                users_count = users_by_date.get(date, 0)
                predictions_count = predictions_by_date.get(date, 0)
                
                total_activity = images_count + users_count + predictions_count
                
                activity_by_day.append(total_activity)
                
                # Formato de labels: "Hoy", "Ayer", o fecha
                if i == 0:
                    activity_labels.append('Hoy')
                elif i == 1:
                    activity_labels.append('Ayer')
                else:
                    # Para muchos días, usar formato más compacto
                    if days_to_show > 14:
                        activity_labels.append(date.strftime('%d/%m'))
                    else:
                        # Para pocos días, incluir día de la semana
                        day_names = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']
                        day_name = day_names[date.weekday()]
                        activity_labels.append(f"{day_name} {date.strftime('%d/%m')}")
            
            logger.info(f"📊 [AdminStatsView] Actividad por día: {activity_by_day} ({len(activity_by_day)} días mostrados)")
            
            # Estadísticas de fincas
            total_fincas = 0
            fincas_this_week = 0
            fincas_this_month = 0
            if Finca is not None:
                # Contar todas las fincas (no solo activas)
                total_fincas = Finca.objects.count()
                total_activas = Finca.objects.filter(activa=True).count()
                fincas_this_week = Finca.objects.filter(fecha_registro__date__gte=this_week).count()
                fincas_this_month = Finca.objects.filter(fecha_registro__date__gte=this_month).count()
                logger.info(f"🏡 [AdminStatsView] Fincas - Total: {total_fincas}, Activas: {total_activas}, Esta semana: {fincas_this_week}, Este mes: {fincas_this_month}")
            else:
                logger.warning("⚠️ [AdminStatsView] Finca model no está disponible")
            
            # Estadísticas de predicciones
            total_predictions = CacaoPrediction.objects.count()
            
            # Estadísticas por región
            region_stats = CacaoImage.objects.values('region').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True))
            ).order_by('-count')[:10]
            
            # Estadísticas por finca
            finca_stats = CacaoImage.objects.values('finca').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True))
            ).order_by('-count')[:10]
            
            # Estadísticas de dimensiones promedio
            avg_dimensions = CacaoPrediction.objects.aggregate(
                avg_alto=Avg('alto_mm'),
                avg_ancho=Avg('ancho_mm'),
                avg_grosor=Avg('grosor_mm'),
                avg_peso=Avg('peso_g'),
                avg_processing_time=Avg('processing_time_ms')
            )
            
            # Calcular promedio de confidence manualmente
            avg_confidence = 0
            if CacaoPrediction.objects.exists():
                confidences = []
                for pred in CacaoPrediction.objects.all():
                    confidences.append(float(pred.average_confidence))
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Distribución de calidad para gráfico de dona
            # Basado en average_confidence de predicciones
            quality_distribution = {
                'excelente': 0,  # >= 0.8
                'buena': 0,      # 0.6 - 0.79
                'regular': 0,    # 0.4 - 0.59
                'baja': 0        # < 0.4
            }
            
            if CacaoPrediction.objects.exists():
                for pred in CacaoPrediction.objects.all():
                    conf = float(pred.average_confidence)
                    if conf >= 0.8:
                        quality_distribution['excelente'] += 1
                    elif conf >= 0.6:
                        quality_distribution['buena'] += 1
                    elif conf >= 0.4:
                        quality_distribution['regular'] += 1
                    else:
                        quality_distribution['baja'] += 1
            
            logger.info(f"📊 [AdminStatsView] Distribución de calidad: {quality_distribution}")
            
            # Preparar respuesta
            stats = {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'staff': staff_users,
                    'superusers': superusers,
                    'analysts': analyst_users,
                    'farmers': farmer_users,
                    'verified': verified_users,
                    'this_week': users_this_week,
                    'this_month': users_this_month
                },
                'images': {
                    'total': total_images,
                    'processed': processed_images,
                    'unprocessed': unprocessed_images,
                    'this_week': images_this_week,
                    'this_month': images_this_month,
                    'processing_rate': round((processed_images / total_images * 100), 2) if total_images > 0 else 0
                },
                'fincas': {
                    'total': total_fincas,
                    'this_week': fincas_this_week,
                    'this_month': fincas_this_month
                },
                'predictions': {
                    'total': total_predictions,
                    'average_dimensions': {
                        'alto_mm': round(float(avg_dimensions['avg_alto'] or 0), 2),
                        'ancho_mm': round(float(avg_dimensions['avg_ancho'] or 0), 2),
                        'grosor_mm': round(float(avg_dimensions['avg_grosor'] or 0), 2),
                        'peso_g': round(float(avg_dimensions['avg_peso'] or 0), 2)
                    },
                    'average_confidence': round(float(avg_confidence), 3),
                    'average_processing_time_ms': round(float(avg_dimensions['avg_processing_time'] or 0), 0)
                },
                'top_regions': list(region_stats),
                'top_fincas': list(finca_stats),
                'activity_by_day': {
                    'labels': activity_labels,
                    'data': activity_by_day
                },
                'quality_distribution': quality_distribution,
                'generated_at': timezone.now().isoformat()
            }
            
            logger.info(f"✅ [AdminStatsView] Estadísticas generadas - Users: {stats['users']['total']}, Fincas: {stats['fincas']['total']}, Images: {stats['images']['total']}, Quality: {stats['predictions']['average_confidence']}")
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.warning(f"⚠️ Error obteniendo estadísticas del sistema: {e}")
            # Retornar datos vacíos en lugar de 500
            return Response({
                'users': {
                    'total': 0,
                    'active': 0,
                    'staff': 0,
                    'superusers': 0,
                    'analysts': 0,
                    'farmers': 0,
                    'verified': 0,
                    'this_week': 0,
                    'this_month': 0
                },
                'images': {
                    'total': 0,
                    'processed': 0,
                    'unprocessed': 0,
                    'this_week': 0,
                    'this_month': 0,
                    'processing_rate': 0
                },
                'predictions': {
                    'total': 0,
                    'average_dimensions': {
                        'alto_mm': 0,
                        'ancho_mm': 0,
                        'grosor_mm': 0,
                        'peso_g': 0
                    },
                    'average_confidence': 0,
                    'average_processing_time_ms': 0
                },
                'top_regions': [],
                'top_fincas': [],
                'generated_at': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class ImageUpdateView(APIView, ImagePermissionMixin):
    """
    Endpoint para actualizar metadatos de una imagen específica.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Actualiza los metadatos de una imagen específica",
        operation_summary="Actualizar imagen",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'finca': openapi.Schema(type=openapi.TYPE_STRING),
                'region': openapi.Schema(type=openapi.TYPE_STRING),
                'lote_id': openapi.Schema(type=openapi.TYPE_STRING),
                'variedad': openapi.Schema(type=openapi.TYPE_STRING),
                'fecha_cosecha': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'notas': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: openapi.Response(
                description="Imagen actualizada exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def patch(self, request, image_id):
        """
        Actualiza los metadatos de una imagen específica.
        Solo el propietario o un admin pueden actualizar.
        """
        try:
            # Obtener imagen
            try:
                image = CacaoImage.objects.get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar permisos de acceso
            if not self.can_access_image(request.user, image):
                return Response({
                    'error': 'No tienes permisos para actualizar esta imagen',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Actualizar campos permitidos
            allowed_fields = ['finca', 'region', 'lote_id', 'variedad', 'fecha_cosecha', 'notas']
            updated_fields = []
            
            for field in allowed_fields:
                if field in request.data:
                    setattr(image, field, request.data[field])
                    updated_fields.append(field)
            
            # Validar fecha_cosecha si se proporciona
            if 'fecha_cosecha' in request.data and request.data['fecha_cosecha']:
                try:
                    from datetime import datetime
                    fecha_cosecha = datetime.strptime(request.data['fecha_cosecha'], '%Y-%m-%d').date()
                    image.fecha_cosecha = fecha_cosecha
                except ValueError:
                    return Response({
                        'error': 'Formato de fecha inválido. Use YYYY-MM-DD',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Guardar cambios
            image.save()
            
            # Serializar imagen actualizada
            serializer = CacaoImageSerializer(image, context={'request': request})
            
            logger.info(f"Imagen {image_id} actualizada por usuario {request.user.username}. Campos: {updated_fields}")
            
            return Response({
                'message': 'Imagen actualizada exitosamente',
                'updated_fields': updated_fields,
                'image': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error actualizando imagen {image_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImageDeleteView(APIView, ImagePermissionMixin):
    """
    Endpoint para eliminar una imagen y su predicción asociada.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Elimina una imagen y su predicción asociada del sistema",
        operation_summary="Eliminar imagen",
        responses={
            200: openapi.Response(
                description="Imagen eliminada exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'deleted_image': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def delete(self, request, image_id):
        """
        Elimina una imagen y su predicción asociada.
        Solo el propietario o un admin pueden eliminar.
        """
        try:
            # Obtener imagen con predicción
            try:
                image = CacaoImage.objects.select_related('prediction').get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar permisos de acceso
            if not self.can_access_image(request.user, image):
                return Response({
                    'error': 'No tienes permisos para eliminar esta imagen',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Guardar información de la imagen antes de eliminarla
            image_data = {
                'id': image.id,
                'file_name': image.file_name,
                'file_size_mb': image.file_size_mb,
                'finca': image.finca,
                'region': image.region,
                'lote_id': image.lote_id,
                'variedad': image.variedad,
                'fecha_cosecha': image.fecha_cosecha.isoformat() if image.fecha_cosecha else None,
                'processed': image.processed,
                'created_at': image.created_at.isoformat(),
                'user': image.user.username
            }
            
            # Información de la predicción si existe
            prediction_data = None
            if hasattr(image, 'prediction') and image.prediction:
                prediction_data = {
                    'id': image.prediction.id,
                    'alto_mm': float(image.prediction.alto_mm),
                    'ancho_mm': float(image.prediction.ancho_mm),
                    'grosor_mm': float(image.prediction.grosor_mm),
                    'peso_g': float(image.prediction.peso_g),
                    'average_confidence': float(image.prediction.average_confidence),
                    'model_version': image.prediction.model_version,
                    'created_at': image.prediction.created_at.isoformat()
                }
            
            # Eliminar imagen (esto también eliminará la predicción por CASCADE)
            image.delete()
            
            logger.info(f"Imagen {image_id} eliminada por usuario {request.user.username}")
            
            return Response({
                'message': 'Imagen eliminada exitosamente',
                'deleted_image': image_data,
                'deleted_prediction': prediction_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error eliminando imagen {image_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImageDownloadView(APIView, ImagePermissionMixin):
    """
    Endpoint para descargar imágenes originales o procesadas.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Descarga una imagen original o procesada",
        operation_summary="Descargar imagen",
        manual_parameters=[
            openapi.Parameter('type', openapi.IN_QUERY, description="Tipo de imagen: 'original' o 'processed'", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Archivo de imagen descargado",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def get(self, request, image_id):
        """
        Descarga una imagen original o procesada.
        Solo el propietario o un admin pueden descargar.
        """
        try:
            # Obtener imagen
            try:
                image = CacaoImage.objects.get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar permisos de acceso
            if not self.can_access_image(request.user, image):
                return Response({
                    'error': 'No tienes permisos para descargar esta imagen',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener tipo de descarga
            download_type = request.GET.get('type', 'original').lower()
            
            if download_type == 'original':
                # Descargar imagen original
                if not image.image:
                    return Response({
                        'error': 'Imagen original no disponible',
                        'status': 'error'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                file_path = image.image.path
                file_name = image.file_name or f"image_{image_id}.jpg"
                
            elif download_type == 'processed':
                # Descargar imagen procesada (crop)
                if not hasattr(image, 'prediction') or not image.prediction:
                    return Response({
                        'error': 'No hay imagen procesada disponible para esta imagen',
                        'status': 'error'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                crop_url = image.prediction.crop_url
                if not crop_url:
                    return Response({
                        'error': 'URL de imagen procesada no disponible',
                        'status': 'error'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Para imágenes procesadas, redirigir a la URL del crop
                from django.http import HttpResponseRedirect
                return HttpResponseRedirect(crop_url)
                
            else:
                return Response({
                    'error': 'Tipo de descarga inválido. Use "original" o "processed"',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verificar que el archivo existe
            import os
            if not os.path.exists(file_path):
                return Response({
                    'error': 'Archivo de imagen no encontrado en el servidor',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Preparar respuesta de descarga
            from django.http import FileResponse
            from django.utils.encoding import escape_uri_path
            
            # Determinar content type
            if file_name.lower().endswith('.png'):
                content_type = 'image/png'
            elif file_name.lower().endswith('.jpg') or file_name.lower().endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file_name.lower().endswith('.bmp'):
                content_type = 'image/bmp'
            else:
                content_type = 'application/octet-stream'
            
            # Crear respuesta de archivo
            response = FileResponse(
                open(file_path, 'rb'),
                content_type=content_type,
                as_attachment=True,
                filename=escape_uri_path(file_name)
            )
            
            # Agregar headers adicionales
            response['Content-Disposition'] = f'attachment; filename="{escape_uri_path(file_name)}"'
            response['Content-Length'] = os.path.getsize(file_path)
            
            logger.info(f"Imagen {image_id} ({download_type}) descargada por usuario {request.user.username}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error descargando imagen {image_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ImagesExportView(APIView, ImagePermissionMixin):
    """
    Endpoint para exportar resultados de predicciones a CSV.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Exporta los resultados de predicciones a formato CSV",
        operation_summary="Exportar resultados",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'format': openapi.Schema(type=openapi.TYPE_STRING, description="Formato de exportación: 'csv'"),
                'include_images': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Incluir información de imágenes"),
                'include_predictions': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Incluir predicciones"),
                'date_from': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha desde"),
                'date_to': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha hasta"),
                'region': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por región"),
                'finca': openapi.Schema(type=openapi.TYPE_STRING, description="Filtrar por finca"),
                'processed_only': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Solo imágenes procesadas")
            }
        ),
        responses={
            200: openapi.Response(
                description="Archivo CSV generado exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_FILE)
            ),
            400: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def post(self, request):
        """
        Exporta los resultados de predicciones a CSV.
        """
        try:
            # Obtener parámetros de exportación
            export_format = request.data.get('format', 'csv').lower()
            include_images = request.data.get('include_images', True)
            include_predictions = request.data.get('include_predictions', True)
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            region = request.data.get('region')
            finca = request.data.get('finca')
            processed_only = request.data.get('processed_only', False)
            
            if export_format != 'csv':
                return Response({
                    'error': 'Formato de exportación no soportado. Solo se admite CSV',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Construir queryset base según permisos
            queryset = self.get_user_images_queryset(request.user)
            
            # Aplicar filtros
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
            
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
            
            if region:
                queryset = queryset.filter(region__icontains=region)
            
            if finca:
                queryset = queryset.filter(finca__icontains=finca)
            
            if processed_only:
                queryset = queryset.filter(processed=True)
            
            # Solo incluir imágenes con predicciones si se solicitan predicciones
            if include_predictions:
                queryset = queryset.filter(prediction__isnull=False)
            
            # Ordenar por fecha de creación
            queryset = queryset.order_by('-created_at')
            
            # Generar CSV
            import csv
            import io
            from django.http import HttpResponse
            
            # Crear buffer de memoria
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Escribir encabezados
            headers = []
            if include_images:
                headers.extend([
                    'image_id', 'file_name', 'file_size_mb', 'finca', 'region', 
                    'lote_id', 'variedad', 'fecha_cosecha', 'notas', 'processed',
                    'created_at', 'user'
                ])
            
            if include_predictions:
                headers.extend([
                    'prediction_id', 'alto_mm', 'ancho_mm', 'grosor_mm', 'peso_g',
                    'confidence_alto', 'confidence_ancho', 'confidence_grosor', 
                    'confidence_peso', 'average_confidence', 'volume_cm3', 'density_g_cm3',
                    'processing_time_ms', 'model_version', 'device_used', 'prediction_created_at'
                ])
            
            writer.writerow(headers)
            
            # Escribir datos
            for image in queryset.select_related('user', 'prediction'):
                row = []
                
                if include_images:
                    row.extend([
                        image.id,
                        image.file_name or '',
                        image.file_size_mb or 0,
                        image.finca or '',
                        image.region or '',
                        image.lote_id or '',
                        image.variedad or '',
                        image.fecha_cosecha.isoformat() if image.fecha_cosecha else '',
                        image.notas or '',
                        image.processed,
                        image.created_at.isoformat(),
                        image.user.username
                    ])
                
                if include_predictions and hasattr(image, 'prediction') and image.prediction:
                    prediction = image.prediction
                    row.extend([
                        prediction.id,
                        float(prediction.alto_mm),
                        float(prediction.ancho_mm),
                        float(prediction.grosor_mm),
                        float(prediction.peso_g),
                        float(prediction.confidence_alto),
                        float(prediction.confidence_ancho),
                        float(prediction.confidence_grosor),
                        float(prediction.confidence_peso),
                        float(prediction.average_confidence),
                        float(prediction.volume_cm3),
                        float(prediction.density_g_cm3),
                        prediction.processing_time_ms,
                        prediction.model_version,
                        prediction.device_used,
                        prediction.created_at.isoformat()
                    ])
                elif include_predictions:
                    # Si se incluyen predicciones pero no hay predicción, llenar con vacíos
                    row.extend([''] * 16)
                
                writer.writerow(row)
            
            # Preparar respuesta
            output.seek(0)
            response = HttpResponse(output.getvalue(), content_type='text/csv')
            
            # Generar nombre de archivo
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"cacao_predictions_export_{timestamp}.csv"
            
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            logger.info(f"Exportación CSV generada por usuario {request.user.username}. Registros: {queryset.count()}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando exportación CSV: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminImagesListView(APIView):
    """
    Endpoint para listar todas las imágenes del sistema con filtros avanzados (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la lista completa de imágenes del sistema con filtros avanzados (solo admins)",
        operation_summary="Lista global de imágenes",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página (máximo 100)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('user_id', openapi.IN_QUERY, description="Filtrar por ID de usuario", type=openapi.TYPE_INTEGER),
            openapi.Parameter('username', openapi.IN_QUERY, description="Filtrar por nombre de usuario", type=openapi.TYPE_STRING),
            openapi.Parameter('region', openapi.IN_QUERY, description="Filtrar por región", type=openapi.TYPE_STRING),
            openapi.Parameter('finca', openapi.IN_QUERY, description="Filtrar por finca", type=openapi.TYPE_STRING),
            openapi.Parameter('processed', openapi.IN_QUERY, description="Filtrar por estado de procesamiento", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('has_prediction', openapi.IN_QUERY, description="Filtrar por existencia de predicción", type=openapi.TYPE_BOOLEAN),
            openapi.Parameter('search', openapi.IN_QUERY, description="Buscar en notas y metadatos", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Fecha desde (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="Fecha hasta (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('model_version', openapi.IN_QUERY, description="Filtrar por versión del modelo", type=openapi.TYPE_STRING),
            openapi.Parameter('min_confidence', openapi.IN_QUERY, description="Confianza mínima", type=openapi.TYPE_NUMBER),
            openapi.Parameter('max_confidence', openapi.IN_QUERY, description="Confianza máxima", type=openapi.TYPE_NUMBER),
        ],
        responses={
            200: openapi.Response(
                description="Lista global de imágenes obtenida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'page_size': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_pages': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING),
                        'filters_applied': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
        },
        tags=['Admin Dataset']
    )
    def get(self, request):
        """
        Obtiene la lista completa de imágenes del sistema con filtros avanzados.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener parámetros de consulta
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)  # Máximo 100 por página
            user_id = request.GET.get('user_id')
            username = request.GET.get('username')
            region = request.GET.get('region')
            finca = request.GET.get('finca')
            processed = request.GET.get('processed')
            has_prediction = request.GET.get('has_prediction')
            search = request.GET.get('search')
            date_from = request.GET.get('date_from')
            date_to = request.GET.get('date_to')
            model_version = request.GET.get('model_version')
            min_confidence = request.GET.get('min_confidence')
            max_confidence = request.GET.get('max_confidence')
            
            # Construir queryset base con todas las imágenes
            queryset = CacaoImage.objects.all().select_related('user', 'prediction')
            
            # Aplicar filtros
            filters_applied = {}
            
            if user_id:
                queryset = queryset.filter(user_id=user_id)
                filters_applied['user_id'] = user_id
            
            if username:
                queryset = queryset.filter(user__username__icontains=username)
                filters_applied['username'] = username
            
            if region:
                queryset = queryset.filter(region__icontains=region)
                filters_applied['region'] = region
            
            if finca:
                queryset = queryset.filter(finca__icontains=finca)
                filters_applied['finca'] = finca
            
            if processed is not None:
                processed_bool = processed.lower() in ['true', '1', 'yes']
                queryset = queryset.filter(processed=processed_bool)
                filters_applied['processed'] = processed_bool
            
            if has_prediction is not None:
                has_pred_bool = has_prediction.lower() in ['true', '1', 'yes']
                if has_pred_bool:
                    queryset = queryset.filter(prediction__isnull=False)
                else:
                    queryset = queryset.filter(prediction__isnull=True)
                filters_applied['has_prediction'] = has_pred_bool
            
            if search:
                queryset = queryset.filter(
                    Q(notas__icontains=search) |
                    Q(finca__icontains=search) |
                    Q(region__icontains=search) |
                    Q(lote_id__icontains=search) |
                    Q(variedad__icontains=search) |
                    Q(user__username__icontains=search)
                )
                filters_applied['search'] = search
            
            if date_from:
                queryset = queryset.filter(created_at__date__gte=date_from)
                filters_applied['date_from'] = date_from
            
            if date_to:
                queryset = queryset.filter(created_at__date__lte=date_to)
                filters_applied['date_to'] = date_to
            
            if model_version:
                queryset = queryset.filter(prediction__model_version=model_version)
                filters_applied['model_version'] = model_version
            
            if min_confidence is not None:
                queryset = queryset.filter(prediction__average_confidence__gte=min_confidence)
                filters_applied['min_confidence'] = float(min_confidence)
            
            if max_confidence is not None:
                queryset = queryset.filter(prediction__average_confidence__lte=max_confidence)
                filters_applied['max_confidence'] = float(max_confidence)
            
            # Ordenar por fecha de creación (más recientes primero)
            queryset = queryset.order_by('-created_at')
            
            # Paginación
            paginator = Paginator(queryset, page_size)
            total_pages = paginator.num_pages
            
            # Validar página
            if page > total_pages and total_pages > 0:
                return Response({
                    'error': f'Página {page} no existe. Total de páginas: {total_pages}',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            page_obj = paginator.get_page(page)
            
            # Serializar resultados con información extendida
            serializer = CacaoImageDetailSerializer(page_obj.object_list, many=True, context={'request': request})
            
            # Preparar respuesta
            response_data = {
                'results': serializer.data,
                'count': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'next': None,
                'previous': None,
                'filters_applied': filters_applied
            }
            
            # URLs de paginación
            if page_obj.has_next():
                response_data['next'] = f"{request.build_absolute_uri()}?page={page + 1}&page_size={page_size}"
            
            if page_obj.has_previous():
                response_data['previous'] = f"{request.build_absolute_uri()}?page={page - 1}&page_size={page_size}"
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'error': 'Parámetros de consulta inválidos',
                'status': 'error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error obteniendo lista global de imágenes: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class AdminImageDetailView(APIView):
    """
    Endpoint para obtener detalles completos de cualquier imagen del sistema (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los detalles completos de cualquier imagen del sistema (solo admins)",
        operation_summary="Detalles globales de imagen",
        responses={
            200: openapi.Response(
                description="Detalles de imagen obtenidos exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Admin Dataset']
    )
    def get(self, request, image_id):
        """
        Obtiene los detalles completos de cualquier imagen del sistema.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener imagen con información completa
            try:
                image = CacaoImage.objects.select_related(
                    'user', 'prediction'
                ).prefetch_related(
                    'user__groups'
                ).get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Serializar imagen con predicción
            serializer = CacaoImageDetailSerializer(image, context={'request': request})
            image_data = serializer.data
            
            # Agregar información administrativa adicional
            image_data['admin_info'] = {
                'owner_info': {
                    'id': image.user.id,
                    'username': image.user.username,
                    'email': image.user.email,
                    'first_name': image.user.first_name,
                    'last_name': image.user.last_name,
                    'is_active': image.user.is_active,
                    'is_staff': image.user.is_staff,
                    'is_superuser': image.user.is_superuser,
                    'date_joined': image.user.date_joined.isoformat(),
                    'last_login': image.user.last_login.isoformat() if image.user.last_login else None,
                    'groups': [group.name for group in image.user.groups.all()]
                },
                'file_info': {
                    'file_path': image.image.path if image.image else None,
                    'file_exists': image.image and os.path.exists(image.image.path) if image.image else False,
                    'storage_backend': str(type(image.image.storage).__name__) if image.image else None
                },
                'processing_info': {
                    'processing_time_ms': image.prediction.processing_time_ms if hasattr(image, 'prediction') and image.prediction else None,
                    'model_version': image.prediction.model_version if hasattr(image, 'prediction') and image.prediction else None,
                    'device_used': image.prediction.device_used if hasattr(image, 'prediction') and image.prediction else None,
                    'crop_url': image.prediction.crop_url if hasattr(image, 'prediction') and image.prediction else None
                },
                'access_info': {
                    'accessed_by_admin': request.user.username,
                    'access_timestamp': timezone.now().isoformat(),
                    'admin_permissions': {
                        'can_edit': True,
                        'can_delete': True,
                        'can_download': True,
                        'can_view_owner_data': True
                    }
                }
            }
            
            return Response(image_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo detalles administrativos de imagen {image_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class AdminImageUpdateView(APIView):
    """
    Endpoint para actualizar cualquier imagen del sistema (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Actualiza cualquier imagen del sistema (solo admins)",
        operation_summary="Actualizar imagen global",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'finca': openapi.Schema(type=openapi.TYPE_STRING),
                'region': openapi.Schema(type=openapi.TYPE_STRING),
                'lote_id': openapi.Schema(type=openapi.TYPE_STRING),
                'variedad': openapi.Schema(type=openapi.TYPE_STRING),
                'fecha_cosecha': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                'notas': openapi.Schema(type=openapi.TYPE_STRING),
                'processed': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'admin_notes': openapi.Schema(type=openapi.TYPE_STRING, description="Notas administrativas")
            }
        ),
        responses={
            200: openapi.Response(
                description="Imagen actualizada exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            400: ErrorResponseSerializer,
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Admin Dataset']
    )
    def patch(self, request, image_id):
        """
        Actualiza cualquier imagen del sistema.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener imagen
            try:
                image = CacaoImage.objects.get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Actualizar campos permitidos (incluyendo campos administrativos)
            allowed_fields = ['finca', 'region', 'lote_id', 'variedad', 'fecha_cosecha', 'notas', 'processed']
            updated_fields = []
            
            for field in allowed_fields:
                if field in request.data:
                    setattr(image, field, request.data[field])
                    updated_fields.append(field)
            
            # Validar fecha_cosecha si se proporciona
            if 'fecha_cosecha' in request.data and request.data['fecha_cosecha']:
                try:
                    from datetime import datetime
                    fecha_cosecha = datetime.strptime(request.data['fecha_cosecha'], '%Y-%m-%d').date()
                    image.fecha_cosecha = fecha_cosecha
                except ValueError:
                    return Response({
                        'error': 'Formato de fecha inválido. Use YYYY-MM-DD',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Agregar notas administrativas si se proporcionan
            admin_notes = request.data.get('admin_notes')
            if admin_notes:
                # Agregar timestamp y admin info a las notas administrativas
                admin_entry = f"\n[ADMIN {request.user.username} - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}]: {admin_notes}"
                if image.notas:
                    image.notas += admin_entry
                else:
                    image.notas = admin_entry.strip()
                updated_fields.append('admin_notes')
            
            # Guardar cambios
            image.save()
            
            # Serializar imagen actualizada
            serializer = CacaoImageDetailSerializer(image, context={'request': request})
            
            logger.info(f"Imagen {image_id} actualizada por admin {request.user.username}. Campos: {updated_fields}")
            
            return Response({
                'message': 'Imagen actualizada exitosamente por administrador',
                'updated_fields': updated_fields,
                'updated_by': request.user.username,
                'update_timestamp': timezone.now().isoformat(),
                'image': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error actualizando imagen {image_id} por admin: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class AdminImageDeleteView(APIView):
    """
    Endpoint para eliminar cualquier imagen del sistema (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Elimina cualquier imagen del sistema (solo admins)",
        operation_summary="Eliminar imagen global",
        responses={
            200: openapi.Response(
                description="Imagen eliminada exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'deleted_image': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'deleted_by': openapi.Schema(type=openapi.TYPE_STRING),
                        'deletion_timestamp': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Admin Dataset']
    )
    def delete(self, request, image_id):
        """
        Elimina cualquier imagen del sistema.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener imagen con predicción
            try:
                image = CacaoImage.objects.select_related('user', 'prediction').get(id=image_id)
            except CacaoImage.DoesNotExist:
                return Response({
                    'error': 'Imagen no encontrada',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Guardar información completa antes de eliminar
            image_data = {
                'id': image.id,
                'file_name': image.file_name,
                'file_size_mb': image.file_size_mb,
                'finca': image.finca,
                'region': image.region,
                'lote_id': image.lote_id,
                'variedad': image.variedad,
                'fecha_cosecha': image.fecha_cosecha.isoformat() if image.fecha_cosecha else None,
                'notas': image.notas,
                'processed': image.processed,
                'created_at': image.created_at.isoformat(),
                'owner': {
                    'id': image.user.id,
                    'username': image.user.username,
                    'email': image.user.email,
                    'first_name': image.user.first_name,
                    'last_name': image.user.last_name
                }
            }
            
            # Información de la predicción si existe
            prediction_data = None
            if hasattr(image, 'prediction') and image.prediction:
                prediction_data = {
                    'id': image.prediction.id,
                    'alto_mm': float(image.prediction.alto_mm),
                    'ancho_mm': float(image.prediction.ancho_mm),
                    'grosor_mm': float(image.prediction.grosor_mm),
                    'peso_g': float(image.prediction.peso_g),
                    'average_confidence': float(image.prediction.average_confidence),
                    'model_version': image.prediction.model_version,
                    'device_used': image.prediction.device_used,
                    'processing_time_ms': image.prediction.processing_time_ms,
                    'created_at': image.prediction.created_at.isoformat()
                }
            
            # Eliminar imagen (esto también eliminará la predicción por CASCADE)
            image.delete()
            
            logger.info(f"Imagen {image_id} eliminada por admin {request.user.username}. Propietario: {image_data['owner']['username']}")
            
            return Response({
                'message': 'Imagen eliminada exitosamente por administrador',
                'deleted_image': image_data,
                'deleted_prediction': prediction_data,
                'deleted_by': request.user.username,
                'deletion_timestamp': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error eliminando imagen {image_id} por admin: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class AdminBulkUpdateView(APIView):
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
    def post(self, request):
        """
        Realiza actualizaciones masivas en múltiples imágenes.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener parámetros
            image_ids = request.data.get('image_ids', [])
            filters = request.data.get('filters', {})
            updates = request.data.get('updates', {})
            admin_notes = request.data.get('admin_notes', '')
            
            # Validar que se proporcionen actualizaciones
            if not updates:
                return Response({
                    'error': 'No se proporcionaron campos para actualizar',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Construir queryset base
            queryset = CacaoImage.objects.all()
            
            # Aplicar filtros si se proporcionan
            if filters:
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
            
            # Si se proporcionan IDs específicos, filtrar por ellos
            if image_ids:
                queryset = queryset.filter(id__in=image_ids)
            
            # Validar que hay imágenes para actualizar
            total_images = queryset.count()
            if total_images == 0:
                return Response({
                    'error': 'No se encontraron imágenes que coincidan con los criterios',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar fecha_cosecha si se proporciona
            if 'fecha_cosecha' in updates and updates['fecha_cosecha']:
                try:
                    from datetime import datetime
                    fecha_cosecha = datetime.strptime(updates['fecha_cosecha'], '%Y-%m-%d').date()
                    updates['fecha_cosecha'] = fecha_cosecha
                except ValueError:
                    return Response({
                        'error': 'Formato de fecha inválido. Use YYYY-MM-DD',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Campos permitidos para actualización masiva
            allowed_fields = ['finca', 'region', 'lote_id', 'variedad', 'fecha_cosecha', 'notas', 'processed']
            filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
            
            # Agregar notas administrativas si se proporcionan
            if admin_notes:
                admin_entry = f"\n[BULK UPDATE {request.user.username} - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}]: {admin_notes}"
                if 'notas' in filtered_updates:
                    filtered_updates['notas'] += admin_entry
                else:
                    filtered_updates['notas'] = admin_entry.strip()
            
            # Realizar actualización masiva
            updated_count = queryset.update(**filtered_updates)
            
            # Obtener información de las imágenes actualizadas
            updated_images = queryset.values('id', 'file_name', 'user__username', 'finca', 'region')
            
            logger.info(f"Actualización masiva realizada por admin {request.user.username}. Imágenes actualizadas: {updated_count}")
            
            return Response({
                'message': 'Actualización masiva completada exitosamente',
                'updated_count': updated_count,
                'total_images_found': total_images,
                'updated_fields': list(filtered_updates.keys()),
                'updated_by': request.user.username,
                'update_timestamp': timezone.now().isoformat(),
                'updated_images_preview': list(updated_images[:10]),  # Solo primeras 10 para preview
                'filters_applied': filters,
                'admin_notes': admin_notes
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en actualización masiva por admin: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class AdminDatasetStatsView(APIView):
    """
    Endpoint para obtener estadísticas globales del dataset (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas globales detalladas del dataset (solo admins)",
        operation_summary="Estadísticas globales del dataset",
        responses={
            200: openapi.Response(
                description="Estadísticas globales obtenidas exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
        },
        tags=['Admin Dataset']
    )
    def get(self, request):
        """
        Obtiene estadísticas globales detalladas del dataset.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Estadísticas generales del dataset
            total_images = CacaoImage.objects.count()
            processed_images = CacaoImage.objects.filter(processed=True).count()
            unprocessed_images = total_images - processed_images
            
            # Estadísticas por usuarios
            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            users_with_images = User.objects.filter(cacao_images__isnull=False).distinct().count()
            
            # Estadísticas de predicciones
            total_predictions = CacaoPrediction.objects.count()
            
            # Estadísticas por fechas
            from datetime import timedelta
            today = timezone.now().date()
            this_week = today - timedelta(days=7)
            this_month = today - timedelta(days=30)
            this_year = today - timedelta(days=365)
            
            images_this_week = CacaoImage.objects.filter(created_at__date__gte=this_week).count()
            images_this_month = CacaoImage.objects.filter(created_at__date__gte=this_month).count()
            images_this_year = CacaoImage.objects.filter(created_at__date__gte=this_year).count()
            
            # Estadísticas por región
            region_stats = CacaoImage.objects.values('region').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True)),
                unique_users=Count('user', distinct=True)
            ).order_by('-count')[:20]
            
            # Estadísticas por finca
            finca_stats = CacaoImage.objects.values('finca').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True)),
                unique_users=Count('user', distinct=True)
            ).order_by('-count')[:20]
            
            # Estadísticas por variedad
            variedad_stats = CacaoImage.objects.values('variedad').annotate(
                count=Count('id'),
                processed_count=Count('id', filter=Q(processed=True))
            ).order_by('-count')[:15]
            
            # Estadísticas de dimensiones y confianza
            avg_dimensions = CacaoPrediction.objects.aggregate(
                avg_alto=Avg('alto_mm'),
                avg_ancho=Avg('ancho_mm'),
                avg_grosor=Avg('grosor_mm'),
                avg_peso=Avg('peso_g'),
                avg_processing_time=Avg('processing_time_ms')
            )
            
            # Calcular confidence manualmente
            avg_confidence = 0
            min_confidence = 0
            max_confidence = 0
            if CacaoPrediction.objects.exists():
                confidences = []
                for pred in CacaoPrediction.objects.all():
                    conf = float(pred.average_confidence)
                    confidences.append(conf)
                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
                    min_confidence = min(confidences)
                    max_confidence = max(confidences)
            
            # Estadísticas por modelo
            model_stats = []
            for model in CacaoPrediction.objects.values_list('model_version', flat=True).distinct():
                predictions = CacaoPrediction.objects.filter(model_version=model)
                count = predictions.count()
                avg_time = predictions.aggregate(avg=Avg('processing_time_ms'))['avg'] or 0
                model_stats.append({
                    'model_version': model,
                    'count': count,
                    'avg_confidence': avg_confidence,
                    'avg_processing_time_ms': round(float(avg_time), 0)
                })
            model_stats.sort(key=lambda x: x['count'], reverse=True)
            
            # Estadísticas por dispositivo
            device_stats = CacaoPrediction.objects.values('device_used').annotate(
                count=Count('id'),
                avg_processing_time=Avg('processing_time_ms')
            ).order_by('-count')
            
            # Top usuarios por actividad
            top_users = User.objects.annotate(
                image_count=Count('api_cacao_images'),
                processed_count=Count('api_cacao_images', filter=Q(api_cacao_images__processed=True))
            ).order_by('-image_count')[:10]
            
            # Estadísticas de archivos
            total_file_size = CacaoImage.objects.aggregate(
                total_size=Sum('file_size')
            )['total_size'] or 0
            
            avg_file_size = CacaoImage.objects.aggregate(
                avg_size=Avg('file_size')
            )['avg_size'] or 0
            
            # Estadísticas de calidad de datos
            images_with_metadata = CacaoImage.objects.filter(
                Q(finca__isnull=False) & ~Q(finca='') |
                Q(region__isnull=False) & ~Q(region='') |
                Q(variedad__isnull=False) & ~Q(variedad='')
            ).count()
            
            # Preparar respuesta
            stats = {
                'dataset_overview': {
                    'total_images': total_images,
                    'processed_images': processed_images,
                    'unprocessed_images': unprocessed_images,
                    'processing_rate': round((processed_images / total_images * 100), 2) if total_images > 0 else 0,
                    'total_users': total_users,
                    'active_users': active_users,
                    'users_with_images': users_with_images,
                    'total_predictions': total_predictions
                },
                'temporal_stats': {
                    'this_week': images_this_week,
                    'this_month': images_this_month,
                    'this_year': images_this_year,
                    'daily_average_this_month': round(images_this_month / 30, 2),
                    'weekly_average_this_year': round(images_this_year / 52, 2)
                },
                'geographic_stats': {
                    'top_regions': list(region_stats),
                    'top_fincas': list(finca_stats),
                    'unique_regions': CacaoImage.objects.values('region').distinct().count(),
                    'unique_fincas': CacaoImage.objects.values('finca').distinct().count()
                },
                'variety_stats': {
                    'top_varieties': list(variedad_stats),
                    'unique_varieties': CacaoImage.objects.values('variedad').distinct().count()
                },
                'quality_stats': {
                    'average_dimensions': {
                        'alto_mm': round(float(avg_dimensions['avg_alto'] or 0), 2),
                        'ancho_mm': round(float(avg_dimensions['avg_ancho'] or 0), 2),
                        'grosor_mm': round(float(avg_dimensions['avg_grosor'] or 0), 2),
                        'peso_g': round(float(avg_dimensions['avg_peso'] or 0), 2)
                    },
                    'confidence_stats': {
                        'average': round(float(avg_confidence), 3),
                        'minimum': round(float(min_confidence), 3),
                        'maximum': round(float(max_confidence), 3)
                    },
                    'processing_stats': {
                        'average_time_ms': round(float(avg_dimensions['avg_processing_time'] or 0), 0)
                    }
                },
                'model_stats': {
                    'by_version': list(model_stats),
                    'by_device': list(device_stats)
                },
                'user_activity': {
                    'top_users': [
                        {
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'image_count': user.image_count,
                            'processed_count': user.processed_count,
                            'processing_rate': round((user.processed_count / user.image_count * 100), 2) if user.image_count > 0 else 0
                        }
                        for user in top_users
                    ]
                },
                'storage_stats': {
                    'total_file_size_mb': round(total_file_size / (1024 * 1024), 2),
                    'average_file_size_mb': round(avg_file_size / (1024 * 1024), 2),
                    'images_with_metadata': images_with_metadata,
                    'metadata_completeness': round((images_with_metadata / total_images * 100), 2) if total_images > 0 else 0
                },
                'generated_at': timezone.now().isoformat(),
                'generated_by': request.user.username
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas globales del dataset: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class TrainingJobListView(APIView):
    """
    Endpoint para listar trabajos de entrenamiento (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la lista de trabajos de entrenamiento (solo admins)",
        operation_summary="Lista de trabajos de entrenamiento",
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, description="Número de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Tamaño de página", type=openapi.TYPE_INTEGER),
            openapi.Parameter('status', openapi.IN_QUERY, description="Filtrar por estado", type=openapi.TYPE_STRING),
            openapi.Parameter('job_type', openapi.IN_QUERY, description="Filtrar por tipo", type=openapi.TYPE_STRING),
            openapi.Parameter('created_by', openapi.IN_QUERY, description="Filtrar por creador", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: openapi.Response(
                description="Lista de trabajos obtenida exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
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
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener parámetros de consulta
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)
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
            
            # Paginación
            paginator = Paginator(queryset, page_size)
            total_pages = paginator.num_pages
            
            # Validar página
            if page > total_pages and total_pages > 0:
                return Response({
                    'error': f'Página {page} no existe. Total de páginas: {total_pages}',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            page_obj = paginator.get_page(page)
            
            # Serializar resultados
            from .serializers import TrainingJobSerializer
            serializer = TrainingJobSerializer(page_obj.object_list, many=True)
            
            # Preparar respuesta
            response_data = {
                'results': serializer.data,
                'count': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'next': None,
                'previous': None
            }
            
            # URLs de paginación
            if page_obj.has_next():
                response_data['next'] = f"{request.build_absolute_uri()}?page={page + 1}&page_size={page_size}"
            
            if page_obj.has_previous():
                response_data['previous'] = f"{request.build_absolute_uri()}?page={page - 1}&page_size={page_size}"
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except ValueError as e:
            return Response({
                'error': 'Parámetros de consulta inválidos',
                'status': 'error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error obteniendo lista de trabajos de entrenamiento: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class TrainingJobCreateView(APIView):
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
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Validar datos de entrada
            from .serializers import TrainingJobCreateSerializer
            serializer = TrainingJobCreateSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response({
                    'error': 'Datos de entrada inválidos',
                    'status': 'error',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generar ID único para el trabajo
            import uuid
            job_id = f"job_{uuid.uuid4().hex[:12]}"
            
            # Crear trabajo de entrenamiento
            training_job = TrainingJob.objects.create(
                job_id=job_id,
                created_by=request.user,
                **serializer.validated_data
            )
            
            # Simular inicio del entrenamiento (en producción esto sería una tarea asíncrona)
            self._simulate_training_start(training_job)
            
            # Serializar respuesta
            from .serializers import TrainingJobSerializer
            response_serializer = TrainingJobSerializer(training_job)
            
            logger.info(f"Trabajo de entrenamiento {job_id} creado por admin {request.user.username}")
            
            return Response({
                'message': 'Trabajo de entrenamiento creado exitosamente',
                'job': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creando trabajo de entrenamiento: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _simulate_training_start(self, training_job):
        """
        Simular inicio del entrenamiento.
        En producción, esto sería una tarea asíncrona con Celery.
        """
        try:
            # Marcar como iniciado
            training_job.mark_started()
            
            # Simular progreso (en producción esto sería manejado por la tarea de entrenamiento)
            import threading
            import time
            
            def simulate_progress():
                for i in range(1, 101):
                    time.sleep(0.1)  # Simular tiempo de entrenamiento
                    training_job.update_progress(i, f"Epoch {i}/{training_job.epochs}")
                
                # Simular finalización exitosa
                mock_metrics = {
                    'final_loss': 0.123,
                    'accuracy': 0.95,
                    'precision': 0.94,
                    'recall': 0.96,
                    'f1_score': 0.95
                }
                mock_model_path = f"/models/{training_job.job_id}_model.pth"
                
                training_job.mark_completed(mock_metrics, mock_model_path)
            
            # Ejecutar simulación en hilo separado
            thread = threading.Thread(target=simulate_progress)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            logger.error(f"Error iniciando simulación de entrenamiento: {e}")
            training_job.mark_failed(f"Error iniciando entrenamiento: {str(e)}")
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class TrainingJobStatusView(APIView):
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
            # Obtener trabajo de entrenamiento
            try:
                training_job = TrainingJob.objects.get(job_id=job_id)
            except TrainingJob.DoesNotExist:
                return Response({
                    'error': 'Trabajo de entrenamiento no encontrado',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar permisos (solo el creador o admin puede ver)
            if training_job.created_by != request.user and not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para ver este trabajo de entrenamiento',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Serializar estado del trabajo
            from .serializers import TrainingJobStatusSerializer
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
                'error': 'Error interno del servidor',
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
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff


class UserDetailView(APIView):
    """
    Endpoint para obtener detalles de un usuario específico (Admin only).
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los detalles completos de un usuario específico (solo admins)",
        operation_summary="Detalles de usuario",
        responses={
            200: openapi.Response(
                description="Detalles de usuario obtenidos exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            403: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Usuarios']
    )
    def get(self, request, user_id):
        """
        Obtiene los detalles completos de un usuario específico.
        Solo accesible para administradores.
        """
        try:
            # Verificar permisos de administrador
            if not self._is_admin_user(request.user):
                return Response({
                    'error': 'No tienes permisos para acceder a esta funcionalidad',
                    'status': 'error'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Obtener usuario
            try:
                user = User.objects.select_related('api_profile', 'api_email_token').prefetch_related('groups', 'api_cacao_images', 'images_app_cacao_images').get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'error': 'Usuario no encontrado',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Serializar usuario con información extendida
            serializer = UserSerializer(user)
            user_data = serializer.data
            
            # Agregar estadísticas adicionales
            try:
                cacao_images_manager = getattr(user, 'cacao_images', None) or getattr(user, 'api_cacao_images', None) or getattr(user, 'images_app_cacao_images', None)
                total_images = cacao_images_manager.count() if cacao_images_manager is not None else 0
                processed_images = cacao_images_manager.filter(processed=True).count() if cacao_images_manager is not None else 0
            except Exception:
                total_images = 0
                processed_images = 0

            user_data['stats'] = {
                'total_images': total_images,
                'processed_images': processed_images,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'days_since_registration': (timezone.now().date() - user.date_joined.date()).days,
                'has_profile': hasattr(user, 'profile') or hasattr(user, 'api_profile'),
                'groups': [group.name for group in user.groups.all()]
            }

            # Incluir datos de persona (si existe) usando serializers de la app personas
            try:
                from personas.models import Persona
                from personas.serializers import PersonaSerializer
                persona = Persona.objects.select_related('user', 'tipo_documento', 'genero', 'departamento', 'municipio').filter(user=user).first()
                user_data['persona'] = PersonaSerializer(persona).data if persona else None
            except Exception:
                user_data['persona'] = None
            
            return Response(user_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo detalles de usuario {user_id}: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _is_admin_user(self, user):
        """
        Verificar si el usuario es administrador.
        
        Args:
            user: Usuario autenticado
            
        Returns:
            bool: True si es admin, False en caso contrario
        """
        return user.is_superuser or user.is_staff
