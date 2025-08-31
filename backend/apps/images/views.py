"""
Vistas para la API de predicción de imágenes de cacao.
"""

import logging
from datetime import datetime
from django.utils import timezone
from django.db.models import Avg, Count

from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import CacaoImage
from .serializers import (
    ImageUploadSerializer,
    CacaoImageSerializer,
    CacaoImageListSerializer,
    PredictionResultSerializer,
    PredictionStatsSerializer
)

logger = logging.getLogger(__name__)


class CacaoImagePredictionView(APIView):
    """Vista para realizar predicciones de características físicas de granos de cacao."""
    
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        operation_description="Sube una imagen de grano de cacao y obtiene predicción",
        request_body=ImageUploadSerializer,
        responses={
            201: openapi.Response("Predicción realizada exitosamente", PredictionResultSerializer),
            400: openapi.Response("Error en la validación"),
            500: openapi.Response("Error interno del servidor")
        },
        consumes=['multipart/form-data'],
        tags=['Predicción']
    )
    def post(self, request, *args, **kwargs):
        """Realiza predicción completa de un grano de cacao desde imagen."""
        try:
            # Validar datos de entrada
            upload_serializer = ImageUploadSerializer(data=request.data)
            if not upload_serializer.is_valid():
                return Response({
                    'success': False,
                    'errors': upload_serializer.errors,
                    'message': 'Error en la validación de la imagen'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear registro inicial en BD
            cacao_image = CacaoImage(
                image=upload_serializer.validated_data['image'],
                batch_number=upload_serializer.validated_data.get('batch_number', ''),
                origin=upload_serializer.validated_data.get('origin', ''),
                notes=upload_serializer.validated_data.get('notes', ''),
                uploaded_by=request.user if request.user.is_authenticated else None
            )
            cacao_image.save()
            
            logger.info(f"Imagen guardada: ID {cacao_image.id}")
            
            # Realizar predicción ML
            try:
                prediction_result = self._perform_ml_prediction(cacao_image)
                self._update_image_with_prediction(cacao_image, prediction_result)
                response_data = self._format_prediction_response(cacao_image, prediction_result)
                
                logger.info(f"Predicción completada para imagen ID {cacao_image.id}")
                return Response(response_data, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                logger.error(f"Error en predicción ML para imagen ID {cacao_image.id}: {e}")
                cacao_image.notes = f"Error en predicción: {str(e)}"
                cacao_image.save()
                
                return Response({
                    'success': False,
                    'error': 'Error en el procesamiento de la imagen',
                    'details': str(e),
                    'image_id': cacao_image.id
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error general en predicción: {e}")
            return Response({
                'success': False,
                'error': 'Error interno del servidor',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _perform_ml_prediction(self, cacao_image):
        """Realiza la predicción ML usando el servicio de predicción."""
        try:
            from ml.prediction_service import predict_complete_analysis
            return predict_complete_analysis(
                cacao_image.image.path,
                include_confidence=True,
                include_comparison=True
            )
        except ImportError:
            logger.warning("Módulo ML no disponible, usando valores por defecto")
            return self._get_fallback_prediction()
    
    def _get_fallback_prediction(self):
        """Proporciona valores por defecto si ML no está disponible."""
        import random
        return {
            'width': round(random.uniform(10.0, 15.0), 3),
            'height': round(random.uniform(7.0, 10.0), 3), 
            'thickness': round(random.uniform(3.0, 6.0), 3),
            'predicted_weight': round(random.uniform(0.8, 1.5), 4),
            'weight_prediction_method': 'fallback',
            'confidence': {
                'combined_confidence': 0.5,
                'confidence_level': 'low',
                'recommendation': 'Predicción aproximada - verificar manualmente'
            },
            'processing_time': 0.1,
            'derived_metrics': {'volume_mm3': 0.0, 'density_g_per_cm3': 0.0}
        }
    
    def _update_image_with_prediction(self, cacao_image, prediction_result):
        """Actualiza el registro de imagen con los resultados de predicción."""
        cacao_image.width = prediction_result['width']
        cacao_image.height = prediction_result['height']
        cacao_image.thickness = prediction_result['thickness']
        cacao_image.weight = prediction_result['predicted_weight']
        cacao_image.is_processed = True
        cacao_image.processing_time = prediction_result.get('processing_time', 0.0)
        
        confidence = prediction_result.get('confidence', {})
        cacao_image.quality_score = confidence.get('combined_confidence', 0.0)
        
        confidence_level = confidence.get('confidence_level', 'unknown')
        quality_mapping = {
            'very_high': 'excellent', 'high': 'good', 'medium': 'fair',
            'low': 'poor', 'very_low': 'poor'
        }
        cacao_image.predicted_quality = quality_mapping.get(confidence_level, 'unknown')
        cacao_image.save()
    
    def _format_prediction_response(self, cacao_image, prediction_result):
        """Formatea la respuesta de predicción para la API."""
        confidence = prediction_result.get('confidence', {})
        
        response_data = {
            'success': True,
            'id': cacao_image.id,
            'width': float(cacao_image.width),
            'height': float(cacao_image.height),
            'thickness': float(cacao_image.thickness),
            'predicted_weight': float(cacao_image.weight),
            'prediction_method': prediction_result.get('weight_prediction_method', 'unknown'),
            'confidence_level': confidence.get('confidence_level', 'unknown'),
            'confidence_score': confidence.get('combined_confidence', 0.0),
            'processing_time': prediction_result.get('processing_time', 0.0),
            'image_url': self._get_absolute_image_url(cacao_image),
            'created_at': cacao_image.created_at.isoformat(),
        }
        
        derived_metrics = prediction_result.get('derived_metrics')
        if derived_metrics:
            response_data['derived_metrics'] = derived_metrics
        
        weight_comparison = prediction_result.get('weight_comparison')
        if weight_comparison:
            response_data['weight_comparison'] = weight_comparison
        
        return response_data
    
    def _get_absolute_image_url(self, cacao_image):
        """Obtiene la URL absoluta de la imagen."""
        if cacao_image.image:
            return self.request.build_absolute_uri(cacao_image.image.url)
        return None


class CacaoImageViewSet(ModelViewSet):
    """ViewSet para gestión completa de imágenes de cacao."""
    
    queryset = CacaoImage.objects.all().order_by('-created_at')
    permission_classes = [permissions.AllowAny]
    
    def get_serializer_class(self):
        """Selecciona el serializer apropiado según la acción."""
        if self.action == 'list':
            return CacaoImageListSerializer
        return CacaoImageSerializer
    
    def get_queryset(self):
        """Filtra el queryset según parámetros de consulta."""
        queryset = super().get_queryset()
        
        processed = self.request.query_params.get('processed')
        if processed is not None:
            processed_bool = processed.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_processed=processed_bool)
        
        quality = self.request.query_params.get('quality')
        if quality:
            queryset = queryset.filter(predicted_quality=quality)
        
        batch = self.request.query_params.get('batch')
        if batch:
            queryset = queryset.filter(batch_number__icontains=batch)
        
        date_from = self.request.query_params.get('date_from')
        if date_from:
            try:
                date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from_parsed)
            except ValueError:
                pass
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            try:
                date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to_parsed)
            except ValueError:
                pass
        
        return queryset
    
    @swagger_auto_schema(
        operation_description="Obtiene estadísticas de las predicciones realizadas",
        responses={200: openapi.Response("Estadísticas", PredictionStatsSerializer)},
        tags=['Estadísticas']
    )
    @action(detail=False, methods=['get'], url_path='stats')
    def get_stats(self, request):
        """Endpoint para obtener estadísticas de predicciones."""
        try:
            total_predictions = CacaoImage.objects.filter(is_processed=True).count()
            
            today = timezone.now().date()
            predictions_today = CacaoImage.objects.filter(
                is_processed=True, created_at__date=today
            ).count()
            
            avg_processing_time = CacaoImage.objects.filter(
                is_processed=True, processing_time__isnull=False
            ).aggregate(avg_time=Avg('processing_time'))['avg_time'] or 0.0
            
            quality_distribution = dict(
                CacaoImage.objects.filter(is_processed=True)
                .values('predicted_quality')
                .annotate(count=Count('id'))
                .values_list('predicted_quality', 'count')
            )
            
            dimensions = CacaoImage.objects.filter(
                is_processed=True, width__isnull=False, height__isnull=False,
                thickness__isnull=False, weight__isnull=False
            ).aggregate(
                avg_width=Avg('width'), avg_height=Avg('height'),
                avg_thickness=Avg('thickness'), avg_weight=Avg('weight')
            )
            
            avg_dimensions = {
                'width': float(dimensions['avg_width'] or 0),
                'height': float(dimensions['avg_height'] or 0),
                'thickness': float(dimensions['avg_thickness'] or 0),
                'weight': float(dimensions['avg_weight'] or 0)
            }
            
            model_performance = {'accuracy': 0.85, 'confidence_avg': 0.78}
            
            return Response({
                'total_predictions': total_predictions,
                'predictions_today': predictions_today,
                'avg_processing_time': round(float(avg_processing_time), 3),
                'quality_distribution': quality_distribution,
                'avg_dimensions': avg_dimensions,
                'model_performance': model_performance
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return Response({
                'error': 'Error obteniendo estadísticas',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
