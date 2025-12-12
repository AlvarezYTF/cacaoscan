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
    def _validate_image_file(self, request):
        """Valida que existe el archivo de imagen."""
        if 'image' not in request.FILES:
            return None, Response({
                'error': 'Campo "image" requerido',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        return request.FILES['image'], None
    
    def _calculate_confidence_level(self, avg_confidence: float) -> str:
        """Calcula el nivel de confianza."""
        if avg_confidence >= 0.8:
            return 'high'
        if avg_confidence >= 0.6:
            return 'medium'
        return 'low'
    
    def _build_email_context(self, response_data: dict, user) -> dict:
        """Construye el contexto para el email."""
        avg_confidence = sum(response_data['confidences'].values()) / len(response_data['confidences'])
        
        return {
            'user_name': user.get_full_name() or user.username,
            'user_email': user.email,
            'analysis_id': response_data.get('prediction_id', 'N/A'),
            'confidence': round(avg_confidence * 100, 1),
            'confidence_level': self._calculate_confidence_level(avg_confidence),
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
    
    def _send_analysis_email(self, user, response_data: dict):
        """Envía el email de análisis completado (opcional, no crítico)."""
        try:
            from api.services.email.email_service import send_email_notification
            
            email_context = self._build_email_context(response_data, user)
            email_result = send_email_notification(
                user_email=user.email,
                notification_type='analysis_complete',
                context=email_context
            )
            
            if email_result.get('success'):
                logger.info(f"Email de análisis completado enviado a {user.email}")
            else:
                logger.warning(f"Error enviando email de análisis: {email_result.get('error')}")
        except Exception as e:
            logger.warning(f"Error en envío de email de análisis: {e}")
    
    def _map_error_to_status_code(self, result) -> int:
        """Mapea errores del servicio a códigos HTTP."""
        if result.error.error_code == 'validation_error':
            if 'file_size' in str(result.error.details.get('field', '')):
                return status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            return status.HTTP_400_BAD_REQUEST
        
        error_msg_lower = str(result.error.message).lower() if result.error.message else ''
        if 'not_available' in error_msg_lower or 'no disponible' in error_msg_lower or 'service not available' in error_msg_lower:
            return status.HTTP_503_SERVICE_UNAVAILABLE
        
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def post(self, request):
        """
        Procesa una imagen y devuelve mediciones del grano.
        
        Request:
            - multipart/form-data con campo 'image' (jpg/png/bmp)
            - Límite de tamaño: 8MB
        
        Response:
            - JSON con predicciones de dimensiones y peso
        """
        try:
            image_file, error_response = self._validate_image_file(request)
            if error_response:
                return error_response
            
            analysis_service = AnalysisService()
            result = analysis_service.process_image_with_segmentation(image_file, request.user)
            
            if result.success:
                serializer = ScanMeasureResponseSerializer(data=result.data)
                if serializer.is_valid():
                    self._send_analysis_email(request.user, result.data)
                    return Response(serializer.validated_data, status=status.HTTP_200_OK)
                
                logger.error(f"Error de serialización: {serializer.errors}")
                return Response({
                    'error': 'Error interno de serialización',
                    'status': 'error',
                    'details': serializer.errors
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            status_code = self._map_error_to_status_code(result)
            return Response({
                'error': result.error.message,
                'status': 'error',
                'details': result.error.details
            }, status=status_code)
        except Exception as e:
            logger.error(f"Error inesperado en análisis de imagen: {e}", exc_info=True)
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

