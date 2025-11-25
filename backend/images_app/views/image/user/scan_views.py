"""
User image scan views for CacaoScan API.
"""
import logging
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers import (
    ScanMeasureResponseSerializer,
    ErrorResponseSerializer,
)
from api.utils.decorators import handle_api_errors
from api.services.analysis_service import AnalysisService

logger = logging.getLogger("cacaoscan.api.images")


class ScanMeasureView(APIView):
    """
    Endpoint para medición de granos de cacao.
    """
    permission_classes = [IsAuthenticated]
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
        # Validar que existe el archivo
        if 'image' not in request.FILES:
            return Response({
                'error': 'Campo "image" requerido',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        
        # Usar servicio de análisis para procesar imagen completa
        analysis_service = AnalysisService()
        result = analysis_service.process_image_with_segmentation(image_file, request.user)
        
        if result.success:
            # Validar respuesta con serializer
            serializer = ScanMeasureResponseSerializer(data=result.data)
            if serializer.is_valid():
                # Enviar email de análisis completado (opcional, no crítico)
                try:
                    from api.services.email.email_service import send_email_notification
                    
                    response_data = result.data
                    avg_confidence = sum(response_data['confidences'].values()) / len(response_data['confidences'])
                    
                    if avg_confidence >= 0.8:
                        confidence_level = 'high'
                    elif avg_confidence >= 0.6:
                        confidence_level = 'medium'
                    else:
                        confidence_level = 'low'
                    
                    email_context = {
                        'user_name': request.user.get_full_name() or request.user.username,
                        'user_email': request.user.email,
                        'analysis_id': response_data.get('prediction_id', 'N/A'),
                        'confidence': round(avg_confidence * 100, 1),
                        'confidence_level': confidence_level,
                        'alto_mm': response_data['alto_mm'],
                        'ancho_mm': response_data['ancho_mm'],
                        'grosor_mm': response_data['grosor_mm'],
                        'peso_g': response_data['peso_g'],
                        'confidence_alto': round(response_data['confidences']['alto'] * 100, 1),
                        'confidence_ancho': round(response_data['confidences']['ancho'] * 100, 1),
                        'confidence_grosor': round(response_data['confidences']['grosor'] * 100, 1),
                        'confidence_peso': round(response_data['confidences']['peso'] * 100, 1),
                        'model_version': response_data.get('debug', {}).get('model_version', 'v1.0'),
                        'analysis_date': timezone.now().strftime('%d/%m/%Y %H:%M'),
                        'crop_url': response_data.get('crop_url'),
                        'defects_detected': []
                    }
                    
                    email_result = send_email_notification(
                        user_email=request.user.email,
                        notification_type='analysis_complete',
                        context=email_context
                    )
                    
                    if email_result.get('success'):
                        logger.info(f"Email de análisis completado enviado a {request.user.email}")
                    else:
                        logger.warning(f"Error enviando email de análisis: {email_result.get('error')}")
                except Exception as e:
                    logger.warning(f"Error en envío de email de análisis: {e}")
                
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                logger.error(f"Error de serialización: {serializer.errors}")
                return Response({
                    'error': 'Error interno de serialización',
                    'status': 'error',
                    'details': serializer.errors
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Mapear errores del servicio a códigos HTTP
            if result.error.error_code == 'validation_error':
                status_code = status.HTTP_400_BAD_REQUEST
                if 'file_size' in str(result.error.details.get('field', '')):
                    status_code = status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            elif 'not_available' in result.error.message.lower() or 'no disponible' in result.error.message.lower():
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            else:
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            
            return Response({
                'error': result.error.message,
                'status': 'error',
                'details': result.error.details
            }, status=status_code)

