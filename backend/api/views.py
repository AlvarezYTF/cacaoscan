"""
Views para la API de CacaoScan.
"""
import time
import logging
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
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
    UserSerializer
)


logger = logging.getLogger("cacaoscan.api")


class ScanMeasureView(APIView):
    """
    Endpoint para medición de granos de cacao.
    """
    parser_classes = [MultiPartParser, FormParser]
    
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
            
            # 6. Obtener predictor y hacer predicción
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
                result = predictor.predict(image)
                
                # 7. Preparar respuesta
                response_data = {
                    'alto_mm': result['alto_mm'],
                    'ancho_mm': result['ancho_mm'],
                    'grosor_mm': result['grosor_mm'],
                    'peso_g': result['peso_g'],
                    'confidences': result['confidences'],
                    'crop_url': result['crop_url'],
                    'debug': result['debug']
                }
                
                # Validar respuesta con serializer
                serializer = ScanMeasureResponseSerializer(data=response_data)
                if serializer.is_valid():
                    total_time = time.time() - start_time
                    logger.info(f"Predicción completada en {total_time:.2f}s para imagen {filename}")
                    
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
            token, created = Token.objects.get_or_create(user=user)
            
            # Login en la sesión
            login(request, user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Login exitoso'
            })
        
        return Response({
            'error': 'Credenciales inválidas',
            'status': 'error'
        }, status=status.HTTP_401_UNAUTHORIZED)


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
        Registra un nuevo usuario.
        """
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Usuario creado exitosamente'
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'error': serializer.errors,
            'status': 'error'
        }, status=status.HTTP_400_BAD_REQUEST)


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


class ImagesListView(APIView):
    """
    Endpoint para listar imágenes procesadas.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene la lista de imágenes procesadas por el usuario",
        operation_summary="Lista de imágenes",
        responses={
            200: openapi.Response(
                description="Lista de imágenes obtenida exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'results': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                        'count': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'next': openapi.Schema(type=openapi.TYPE_STRING),
                        'previous': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            401: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def get(self, request):
        """
        Obtiene la lista de imágenes procesadas.
        """
        # Por ahora, devolver una respuesta mock
        return Response({
            'results': [],
            'count': 0,
            'next': None,
            'previous': None,
            'message': 'Endpoint de imágenes en desarrollo'
        })


class ImageDetailView(APIView):
    """
    Endpoint para obtener detalles de una imagen específica.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene los detalles de una imagen específica",
        operation_summary="Detalles de imagen",
        responses={
            200: openapi.Response(
                description="Detalles de imagen obtenidos exitosamente",
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            404: ErrorResponseSerializer,
        },
        tags=['Imágenes']
    )
    def get(self, request, image_id):
        """
        Obtiene los detalles de una imagen específica.
        """
        # Por ahora, devolver una respuesta mock
        return Response({
            'id': image_id,
            'message': 'Endpoint de detalles de imagen en desarrollo'
        })


class ImagesStatsView(APIView):
    """
    Endpoint para obtener estadísticas de imágenes procesadas.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas de imágenes procesadas por el usuario",
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
        Obtiene estadísticas de imágenes procesadas.
        """
        # Por ahora, devolver una respuesta mock
        return Response({
            'total_images': 0,
            'processed_today': 0,
            'average_confidence': 0,
            'message': 'Endpoint de estadísticas en desarrollo'
        })
