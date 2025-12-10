"""
Image export views for CacaoScan API.
"""
import logging
import io
import csv
from datetime import datetime
from typing import Optional
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.serializers import ErrorResponseSerializer
from ..mixins import ImagePermissionMixin

logger = logging.getLogger("cacaoscan.api.images")


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
    def _validate_export_format(self, export_format: str) -> Optional[Response]:
        """Valida el formato de exportación."""
        if export_format != 'csv':
            return Response({
                'error': 'Formato de exportación no soportado. Solo se admite CSV',
                'status': 'error'
            }, status=status.HTTP_400_BAD_REQUEST)
        return None
    
    def _apply_export_filters(self, queryset, date_from: str, date_to: str, region: str, finca: str, processed_only: bool):
        """Aplica los filtros de exportación."""
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
        return queryset
    
    def _build_csv_headers(self, include_images: bool, include_predictions: bool) -> list:
        """Construye los encabezados del CSV."""
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
        return headers
    
    def _build_image_row(self, image) -> list:
        """Construye la fila de datos de imagen."""
        return [
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
        ]
    
    def _build_prediction_row(self, prediction) -> list:
        """Construye la fila de datos de predicción."""
        return [
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
            prediction.model_version.codigo if prediction.model_version else None,
            prediction.device_used.codigo if prediction.device_used else None,
            prediction.created_at.isoformat()
        ]
    
    def _write_csv_data(self, writer, queryset, include_images: bool, include_predictions: bool):
        """Escribe los datos al CSV."""
        for image in queryset.select_related('user', 'prediction'):
            row = []
            
            if include_images:
                row.extend(self._build_image_row(image))
            
            if include_predictions:
                if hasattr(image, 'prediction') and image.prediction:
                    row.extend(self._build_prediction_row(image.prediction))
                else:
                    row.extend([''] * 16)
            
            writer.writerow(row)
    
    def _create_csv_response(self, output, queryset) -> HttpResponse:
        """Crea la respuesta HTTP con el CSV."""
        output.seek(0)
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"cacao_predictions_export_{timestamp}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        logger.info(f"Exportación CSV generada por usuario. Registros: {queryset.count()}")
        return response
    
    def post(self, request):
        """
        Exporta los resultados de predicciones a CSV.
        """
        try:
            from api.utils.model_imports import get_models_safely
            get_models_safely({'CacaoImage': 'images_app.models.CacaoImage'})
            
            export_format = request.data.get('format', 'csv').lower()
            include_images = request.data.get('include_images', True)
            include_predictions = request.data.get('include_predictions', True)
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            region = request.data.get('region')
            finca = request.data.get('finca')
            processed_only = request.data.get('processed_only', False)
            
            error_response = self._validate_export_format(export_format)
            if error_response:
                return error_response
            
            queryset = self.get_user_images_queryset(request.user)
            queryset = self._apply_export_filters(queryset, date_from, date_to, region, finca, processed_only)
            
            if include_predictions:
                queryset = queryset.filter(prediction__isnull=False)
            
            queryset = queryset.order_by('-created_at')
            
            output = io.StringIO()
            writer = csv.writer(output)
            headers = self._build_csv_headers(include_images, include_predictions)
            writer.writerow(headers)
            
            self._write_csv_data(writer, queryset, include_images, include_predictions)
            
            return self._create_csv_response(output, queryset)
            
        except Exception as e:
            logger.error(f"Error generando exportación CSV: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

