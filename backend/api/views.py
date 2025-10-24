"""
Views para la API de CacaoScan.
"""
import time
import logging
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from PIL import Image
import io

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
    CacaoImageDetailSerializer
)
from .utils import create_error_response, create_success_response
from .models import EmailVerificationToken, ExpiringToken, CacaoImage, CacaoPrediction


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
        Autentica un usuario.
        """
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = ExpiringToken.create_for_user(user)
            
            # Login en la sesión
            login(request, user)
            
            return create_success_response(
                message='Login exitoso',
                data={
                    'token': token.key,
                    'user': UserSerializer(user).data,
                    'expires_at': token.expires_at.isoformat()
                }
            )
        
        return create_error_response(
            message='Credenciales inválidas',
            error_type='invalid_credentials',
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=serializer.errors
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
        Registra un nuevo usuario y genera token automáticamente.
        """
        # Log de depuración - datos recibidos
        print(f"🔍 DEBUG RegisterView - Datos recibidos: {request.data}")
        
        # Crear una copia de los datos y eliminar el campo 'role' si viene del frontend
        data = request.data.copy()
        data.pop('role', None)  # Elimina si viene en la solicitud
        
        print(f"🔍 DEBUG RegisterView - Datos procesados: {data}")
        
        serializer = RegisterSerializer(data=data)
        
        if serializer.is_valid():
            print("✅ DEBUG RegisterView - Serializer válido")
            user = serializer.save()
            print(f"✅ DEBUG RegisterView - Usuario creado: {user.username} ({user.email})")
            
            # Crear token de verificación de email
            verification_token = EmailVerificationToken.create_for_user(user)
            print(f"✅ DEBUG RegisterView - Token de verificación creado: {verification_token.token}")
            
            # Generar token automáticamente para auto-login
            token = ExpiringToken.create_for_user(user)
            print(f"✅ DEBUG RegisterView - Token de acceso creado: {token.key[:10]}...")
            
            # Login en la sesión
            login(request, user)
            
            return create_success_response(
                message='Usuario registrado exitosamente',
                data={
                    'token': token.key,
                    'user': UserSerializer(user).data,
                    'verification_token': str(verification_token.token),  # Solo para desarrollo
                    'verification_required': True,
                    'expires_at': token.expires_at.isoformat()
                },
                status_code=status.HTTP_201_CREATED
            )
        
        print(f"❌ DEBUG RegisterView - Errores de validación: {serializer.errors}")
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
        Cierra la sesión del usuario.
        """
        try:
            # Eliminar token
            request.user.auth_token.delete()
            
            # Logout de la sesión
            logout(request)
            
            return Response({
                'message': 'Logout exitoso'
            })
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
    Endpoint para refrescar token de acceso.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Refresca el token de acceso del usuario autenticado",
        operation_summary="Refrescar token",
        responses={
            200: openapi.Response(
                description="Token refrescado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(type=openapi.TYPE_STRING),
                        'user': UserSerializer
                    }
                )
            ),
            401: ErrorResponseSerializer,
        },
        tags=['Autenticación']
    )
    def post(self, request):
        """
        Refresca el token del usuario actual.
        """
        try:
            # Eliminar token actual
            request.user.auth_token.delete()
            
            # Crear nuevo token
            token, created = Token.objects.get_or_create(user=request.user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(request.user).data
            })
            
        except Exception as e:
            return Response({
                'error': f'Error refrescando token: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)


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
            predictions = CacaoPrediction.objects.filter(image__user=request.user)
            
            avg_confidence = predictions.aggregate(
                avg_conf=Avg('average_confidence')
            )['avg_conf'] or 0
            
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
            logger.error(f"Error obteniendo estadísticas de imágenes: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Vistas de verificación de email
class EmailVerificationView(APIView):
    """
    Endpoint para verificar email con token.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verifica un email usando el token enviado por correo",
        operation_summary="Verificar email",
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
        Verificar email con token.
        """
        serializer = EmailVerificationSerializer(data=request.data)
        
        if serializer.is_valid():
            token_uuid = serializer.validated_data['token']
            token_obj = EmailVerificationToken.get_valid_token(token_uuid)
            
            if token_obj:
                token_obj.verify()
                
                return create_success_response(
                    message='Email verificado exitosamente',
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
        
        return create_error_response(
            message='Datos de verificación inválidos',
            error_type='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
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
            
            # TODO: Enviar email con token (implementar en producción)
            # send_verification_email(user, token_obj.token)
            
            return create_success_response(
                message=f'Token de verificación enviado a {email}',
                data={
                    'token': str(token_obj.token),  # Solo para desarrollo
                    'expires_at': token_obj.expires_at.isoformat()
                }
            )
        
        return create_error_response(
            message='Email inválido',
            error_type='validation_error',
            status_code=status.HTTP_400_BAD_REQUEST,
            details=serializer.errors
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
            
            # TODO: Enviar email con token (implementar en producción)
            # send_password_reset_email(user, reset_token.token)
            
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
            
            # Construir queryset base
            queryset = User.objects.all().select_related('profile').prefetch_related('groups')
            
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
                    queryset = queryset.filter(email_verification_token__is_verified=True)
                else:
                    queryset = queryset.filter(
                        Q(email_verification_token__is_verified=False) | 
                        Q(email_verification_token__isnull=True)
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
            
            # Usuarios por rol
            analyst_users = User.objects.filter(groups__name='analyst').distinct().count()
            farmer_users = User.objects.filter(
                ~Q(is_superuser=True),
                ~Q(is_staff=True),
                ~Q(groups__name='analyst')
            ).count()
            
            # Usuarios verificados
            verified_users = User.objects.filter(
                email_verification_token__is_verified=True
            ).count()
            
            # Estadísticas de imágenes
            total_images = CacaoImage.objects.count()
            processed_images = CacaoImage.objects.filter(processed=True).count()
            unprocessed_images = total_images - processed_images
            
            # Estadísticas de predicciones
            total_predictions = CacaoPrediction.objects.count()
            
            # Estadísticas por fecha
            from datetime import timedelta
            today = timezone.now().date()
            this_week = today - timedelta(days=7)
            this_month = today - timedelta(days=30)
            
            users_this_week = User.objects.filter(date_joined__date__gte=this_week).count()
            users_this_month = User.objects.filter(date_joined__date__gte=this_month).count()
            
            images_this_week = CacaoImage.objects.filter(created_at__date__gte=this_week).count()
            images_this_month = CacaoImage.objects.filter(created_at__date__gte=this_month).count()
            
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
                avg_confidence=Avg('average_confidence'),
                avg_processing_time=Avg('processing_time_ms')
            )
            
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
                'predictions': {
                    'total': total_predictions,
                    'average_dimensions': {
                        'alto_mm': round(float(avg_dimensions['avg_alto'] or 0), 2),
                        'ancho_mm': round(float(avg_dimensions['avg_ancho'] or 0), 2),
                        'grosor_mm': round(float(avg_dimensions['avg_grosor'] or 0), 2),
                        'peso_g': round(float(avg_dimensions['avg_peso'] or 0), 2)
                    },
                    'average_confidence': round(float(avg_dimensions['avg_confidence'] or 0), 3),
                    'average_processing_time_ms': round(float(avg_dimensions['avg_processing_time'] or 0), 0)
                },
                'top_regions': list(region_stats),
                'top_fincas': list(finca_stats),
                'generated_at': timezone.now().isoformat()
            }
            
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del sistema: {e}")
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
                user = User.objects.select_related('profile').prefetch_related('groups', 'cacao_images').get(id=user_id)
            except User.DoesNotExist:
                return Response({
                    'error': 'Usuario no encontrado',
                    'status': 'error'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Serializar usuario con información extendida
            serializer = UserSerializer(user)
            user_data = serializer.data
            
            # Agregar estadísticas adicionales
            user_data['stats'] = {
                'total_images': user.cacao_images.count(),
                'processed_images': user.cacao_images.filter(processed=True).count(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'days_since_registration': (timezone.now().date() - user.date_joined.date()).days,
                'has_profile': hasattr(user, 'profile'),
                'groups': [group.name for group in user.groups.all()]
            }
            
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
