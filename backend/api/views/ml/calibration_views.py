"""
Vistas de calibración para CacaoScan.
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ...serializers import ErrorResponseSerializer

logger = logging.getLogger("cacaoscan.api")


class CalibrationStatusView(APIView):
    """
    Endpoint para consultar el estado de la calibración.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Obtiene el estado actual de la calibración del sistema",
        operation_summary="Estado de calibración",
        responses={
            200: openapi.Response(
                description="Estado de calibración obtenido",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'calibration_enabled': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'calibration_loaded': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'pixels_per_mm': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'method': openapi.Schema(type=openapi.TYPE_STRING),
                        'confidence': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'timestamp': openapi.Schema(type=openapi.TYPE_STRING),
                        'validation_score': openapi.Schema(type=openapi.TYPE_NUMBER)
                    }
                )
            ),
            500: ErrorResponseSerializer,
        },
        tags=['Calibración']
    )
    def get(self, request):
        """
        Obtiene el estado actual de la calibración.
        """
        try:
            from ml.prediction.calibrated_predict import get_calibrated_predictor
            
            predictor = get_calibrated_predictor(use_calibration=True)
            calibration_status = predictor.get_calibration_status()
            
            return Response(calibration_status)
            
        except Exception as e:
            logger.error(f"Error obteniendo estado de calibración: {e}")
            return Response({
                'error': f'Error obteniendo estado de calibración: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CalibrationView(APIView):
    """
    Endpoint para calibrar el sistema usando una imagen de referencia.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Calibra el sistema usando una imagen con objeto de referencia conocido",
        operation_summary="Calibrar sistema",
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="Imagen con objeto de referencia (moneda, regla, etc.)",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'method',
                openapi.IN_FORM,
                description="Método de calibración",
                type=openapi.TYPE_STRING,
                enum=['coin_detection', 'ruler_detection', 'manual_points', 'auto_reference'],
                required=False
            ),
            openapi.Parameter(
                'reference_object',
                openapi.IN_FORM,
                description="Objeto de referencia específico",
                type=openapi.TYPE_STRING,
                enum=['COIN_1000_COP', 'COIN_500_COP', 'COIN_200_COP', 'COIN_100_COP', 'RULER_1CM', 'RULER_2CM', 'RULER_5CM'],
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Calibración exitosa",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'pixels_per_mm': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'confidence': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'method': openapi.Schema(type=openapi.TYPE_STRING),
                        'reference_object': openapi.Schema(type=openapi.TYPE_STRING),
                        'calibration_image_path': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['Calibración']
    )
    def post(self, request):
        """
        Calibra el sistema usando una imagen de referencia.
        """
        try:
            # Validar archivo de imagen
            if 'image' not in request.FILES:
                return Response({
                    'error': 'No se proporcionó archivo de imagen',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            image_file = request.FILES['image']
            
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp']
            if image_file.content_type not in allowed_types:
                return Response({
                    'error': 'Tipo de archivo no válido. Use JPEG, PNG o BMP',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar tamaño del archivo (20MB máximo)
            max_size = 20 * 1024 * 1024
            if image_file.size > max_size:
                return Response({
                    'error': 'Archivo demasiado grande. Máximo 20MB permitido',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener parámetros de calibración
            method_str = request.data.get('method', 'coin_detection')
            reference_object_str = request.data.get('reference_object')
            
            # Convertir parámetros
            from ml.measurement.calibration import CalibrationMethod, ReferenceObject
            
            try:
                method = CalibrationMethod(method_str)
            except ValueError:
                return Response({
                    'error': f'Método de calibración no válido: {method_str}',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            reference_object = None
            if reference_object_str:
                try:
                    reference_object = ReferenceObject(reference_object_str)
                except ValueError:
                    return Response({
                        'error': f'Objeto de referencia no válido: {reference_object_str}',
                        'status': 'error'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Cargar imagen
            from PIL import Image
            import io
            
            image_data = image_file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Realizar calibración
            from ml.prediction.calibrated_predict import get_calibrated_predictor
            
            predictor = get_calibrated_predictor(use_calibration=True)
            calibration_result = predictor.calibrate_image(image, method, reference_object)
            
            if calibration_result['success']:
                logger.info(f"Calibración exitosa: {calibration_result['pixels_per_mm']:.3f} pixels/mm")
                return Response(calibration_result)
            else:
                return Response({
                    'error': calibration_result.get('error', 'Error desconocido en calibración'),
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error en calibración: {e}")
            return Response({
                'error': f'Error en calibración: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CalibratedScanMeasureView(APIView):
    """
    Endpoint para medición de granos de cacao con calibración.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Procesa una imagen de grano de cacao y devuelve predicciones calibradas en milímetros",
        operation_summary="Medir grano de cacao (calibrado)",
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
            200: openapi.Response(
                description="Predicción calibrada exitosa",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'predictions': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'alto_mm': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'ancho_mm': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'grosor_mm': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'peso_g': openapi.Schema(type=openapi.TYPE_NUMBER)
                            }
                        ),
                        'confidences': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'calibration_info': openapi.Schema(type=openapi.TYPE_OBJECT),
                        'processing_time_ms': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'crop_url': openapi.Schema(type=openapi.TYPE_STRING),
                        'model_version': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: ErrorResponseSerializer,
            413: ErrorResponseSerializer,
            503: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['Medición']
    )
    def post(self, request):
        """
        Procesa una imagen de grano de cacao y devuelve predicciones calibradas.
        """
        try:
            # Validar archivo de imagen
            if 'image' not in request.FILES:
                return Response({
                    'error': 'No se proporcionó archivo de imagen',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            image_file = request.FILES['image']
            
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp']
            if image_file.content_type not in allowed_types:
                return Response({
                    'error': 'Tipo de archivo no válido. Use JPEG, PNG o BMP',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar tamaño del archivo (20MB máximo)
            max_size = 20 * 1024 * 1024
            if image_file.size > max_size:
                return Response({
                    'error': 'Archivo demasiado grande. Máximo 20MB permitido',
                    'status': 'error'
                }, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
            
            # Cargar imagen
            from PIL import Image
            import io
            
            image_data = image_file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Obtener predictor calibrado
            from ml.prediction.calibrated_predict import get_calibrated_predictor
            
            predictor = get_calibrated_predictor(use_calibration=True)
            
            # Cargar artefactos si no están cargados
            if not predictor.models_loaded:
                logger.info("Modelos no cargados. Cargando artefactos...")
                success = predictor.load_artifacts()
                
                if not success:
                    return Response({
                        'error': 'Error cargando modelos. Ejecutar inicialización automática primero.',
                        'status': 'error',
                        'suggestion': 'POST /api/v1/auto-initialize/ para inicializar el sistema'
                    }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Realizar predicción calibrada
            result = predictor.predict(image)
            
            if result['success']:
                logger.info(f"Predicción calibrada exitosa: {result['predictions']}")
                return Response(result)
            else:
                return Response({
                    'error': result.get('error', 'Error desconocido en predicción'),
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Error en predicción calibrada: {e}")
            return Response({
                'error': f'Error en predicción calibrada: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


