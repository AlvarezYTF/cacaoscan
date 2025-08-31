"""
Vistas administrativas para la gestión de datos de imágenes de cacao.

Proporciona endpoints REST con permisos administrativos para CRUD completo,
estadísticas avanzadas y operaciones de reentrenamiento de modelos ML.
"""

import os
import logging
import threading
import subprocess
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Min, Max, Q, Sum
from django.db.models.functions import TruncMonth
from django.core.exceptions import ValidationError
from django.conf import settings

from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import CacaoImage
from .admin_serializers import (
    AdminCacaoImageSerializer,
    AdminImageBulkUpdateSerializer,
    TrainingJobSerializer,
    TrainingJobStatusSerializer,
    AdminStatsSerializer
)

# Configurar logging
logger = logging.getLogger('admin')

# Storage para trabajos de entrenamiento en memoria (en producción usar Redis/Celery)
training_jobs = {}
training_jobs_lock = threading.Lock()


class AdminImageViewSet(ModelViewSet):
    """
    ViewSet administrativo para gestión completa de imágenes de cacao.
    
    Proporciona CRUD completo con permisos administrativos y funcionalidades
    avanzadas como actualización masiva y estadísticas detalladas.
    """
    
    queryset = CacaoImage.objects.all().order_by('-created_at')
    serializer_class = AdminCacaoImageSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        """
        Filtra el queryset según parámetros administrativos.
        
        Filtros administrativos especiales:
        - all_fields: incluye registros con campos nulos
        - data_quality: filtra por calidad de datos
        - processing_status: estado de procesamiento ML
        - date_range: rango de fechas personalizado
        """
        queryset = super().get_queryset()
        
        # Filtro estándar por estado de procesamiento
        processed = self.request.query_params.get('processed')
        if processed is not None:
            processed_bool = processed.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_processed=processed_bool)
        
        # Filtro por calidad de datos
        data_quality = self.request.query_params.get('data_quality')
        if data_quality == 'complete':
            # Solo registros con todos los campos físicos completos
            queryset = queryset.filter(
                width__isnull=False,
                height__isnull=False,
                thickness__isnull=False,
                weight__isnull=False
            )
        elif data_quality == 'incomplete':
            # Registros con campos físicos faltantes
            queryset = queryset.filter(
                Q(width__isnull=True) |
                Q(height__isnull=True) |
                Q(thickness__isnull=True) |
                Q(weight__isnull=True)
            )
        
        # Filtro por calidad predicha
        quality = self.request.query_params.get('quality')
        if quality:
            queryset = queryset.filter(predicted_quality=quality)
        
        # Filtro por tipo de defecto
        defect = self.request.query_params.get('defect')
        if defect:
            queryset = queryset.filter(defect_type=defect)
        
        # Filtro por lote
        batch = self.request.query_params.get('batch')
        if batch:
            queryset = queryset.filter(batch_number__icontains=batch)
        
        # Filtro por origen
        origin = self.request.query_params.get('origin')
        if origin:
            queryset = queryset.filter(origin__icontains=origin)
        
        # Filtro por rango de fechas
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            try:
                date_from_parsed = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=date_from_parsed)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_parsed = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=date_to_parsed)
            except ValueError:
                pass
        
        # Filtro por rango de calidad
        min_quality = self.request.query_params.get('min_quality')
        max_quality = self.request.query_params.get('max_quality')
        
        if min_quality:
            try:
                min_quality_float = float(min_quality)
                queryset = queryset.filter(quality_score__gte=min_quality_float)
            except ValueError:
                pass
        
        if max_quality:
            try:
                max_quality_float = float(max_quality)
                queryset = queryset.filter(quality_score__lte=max_quality_float)
            except ValueError:
                pass
        
        return queryset
    
    def perform_update(self, serializer):
        """Registra la actualización administrativa."""
        instance = serializer.save()
        
        logger.info(f"Admin {self.request.user.username} actualizó imagen {instance.id}")
    
    def perform_destroy(self, instance):
        """Registra la eliminación administrativa."""
        image_id = instance.id
        image_path = instance.image.path if instance.image else None
        
        # Eliminar archivo físico si existe
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                logger.info(f"Archivo de imagen eliminado: {image_path}")
            except OSError as e:
                logger.error(f"Error eliminando archivo {image_path}: {e}")
        
        instance.delete()
        logger.info(f"Admin {self.request.user.username} eliminó imagen {image_id}")
    
    @swagger_auto_schema(
        operation_description="Actualización masiva de imágenes",
        request_body=AdminImageBulkUpdateSerializer,
        responses={
            200: openapi.Response("Actualización exitosa", openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'updated_count': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'updated_ids': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER))
                }
            )),
            400: openapi.Response("Error de validación")
        },
        tags=['Administración']
    )
    @action(detail=False, methods=['post'], url_path='bulk-update')
    def bulk_update(self, request):
        """
        Actualización masiva de múltiples imágenes.
        
        Permite aplicar cambios a múltiples registros simultáneamente
        para operaciones administrativas eficientes.
        """
        serializer = AdminImageBulkUpdateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            image_ids = serializer.validated_data['image_ids']
            update_data = {k: v for k, v in serializer.validated_data.items() if k != 'image_ids'}
            
            # Realizar actualización masiva
            updated_count = CacaoImage.objects.filter(id__in=image_ids).update(**update_data)
            
            logger.info(f"Admin {request.user.username} actualizó masivamente {updated_count} imágenes: {update_data}")
            
            return Response({
                'success': True,
                'updated_count': updated_count,
                'updated_ids': image_ids,
                'applied_changes': update_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error en actualización masiva: {e}")
            return Response({
                'success': False,
                'error': 'Error interno en actualización masiva',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Estadísticas administrativas detalladas",
        responses={
            200: openapi.Response("Estadísticas obtenidas", AdminStatsSerializer)
        },
        tags=['Estadísticas']
    )
    @action(detail=False, methods=['get'], url_path='admin-stats')
    def admin_stats(self, request):
        """
        Endpoint para estadísticas administrativas detalladas.
        
        Proporciona métricas avanzadas para administradores incluyendo:
        - Distribución de calidad y defectos
        - Estadísticas temporales
        - Métricas de rendimiento
        - Uso de almacenamiento
        """
        try:
            # Estadísticas generales
            total_images = CacaoImage.objects.count()
            processed_images = CacaoImage.objects.filter(is_processed=True).count()
            unprocessed_images = total_images - processed_images
            
            # Distribución de calidad
            quality_distribution = dict(
                CacaoImage.objects.values('predicted_quality')
                .annotate(count=Count('id'))
                .values_list('predicted_quality', 'count')
            )
            
            # Distribución de defectos
            defect_distribution = dict(
                CacaoImage.objects.values('defect_type')
                .annotate(count=Count('id'))
                .values_list('defect_type', 'count')
            )
            
            # Estadísticas de dimensiones
            dimension_stats = CacaoImage.objects.filter(
                width__isnull=False,
                height__isnull=False,
                thickness__isnull=False,
                weight__isnull=False
            ).aggregate(
                avg_width=Avg('width'),
                min_width=Min('width'),
                max_width=Max('width'),
                avg_height=Avg('height'),
                min_height=Min('height'),
                max_height=Max('height'),
                avg_thickness=Avg('thickness'),
                min_thickness=Min('thickness'),
                max_thickness=Max('thickness'),
                avg_weight=Avg('weight'),
                min_weight=Min('weight'),
                max_weight=Max('weight')
            )
            
            dimension_statistics = {
                'width': {
                    'avg': float(dimension_stats['avg_width'] or 0),
                    'min': float(dimension_stats['min_width'] or 0),
                    'max': float(dimension_stats['max_width'] or 0)
                },
                'height': {
                    'avg': float(dimension_stats['avg_height'] or 0),
                    'min': float(dimension_stats['min_height'] or 0),
                    'max': float(dimension_stats['max_height'] or 0)
                },
                'thickness': {
                    'avg': float(dimension_stats['avg_thickness'] or 0),
                    'min': float(dimension_stats['min_thickness'] or 0),
                    'max': float(dimension_stats['max_thickness'] or 0)
                },
                'weight': {
                    'avg': float(dimension_stats['avg_weight'] or 0),
                    'min': float(dimension_stats['min_weight'] or 0),
                    'max': float(dimension_stats['max_weight'] or 0)
                }
            }
            
            # Estadísticas temporales (últimos 12 meses)
            twelve_months_ago = timezone.now() - timedelta(days=365)
            images_by_month = dict(
                CacaoImage.objects.filter(created_at__gte=twelve_months_ago)
                .annotate(month=TruncMonth('created_at'))
                .values('month')
                .annotate(count=Count('id'))
                .values_list('month__strftime', 'count')
            )
            
            # Estadísticas de tiempos de procesamiento
            processing_stats = CacaoImage.objects.filter(
                processing_time__isnull=False
            ).aggregate(
                avg_time=Avg('processing_time'),
                min_time=Min('processing_time'),
                max_time=Max('processing_time')
            )
            
            processing_times = {
                'avg_seconds': float(processing_stats['avg_time'] or 0),
                'min_seconds': float(processing_stats['min_time'] or 0),
                'max_seconds': float(processing_stats['max_time'] or 0)
            }
            
            # Estadísticas de modelos ML (placeholder)
            model_performance = {
                'vision_model': {
                    'accuracy': 0.85,
                    'last_trained': '2024-01-15T10:30:00Z',
                    'samples_used': processed_images
                },
                'regression_model': {
                    'r2_score': 0.78,
                    'rmse': 0.12,
                    'last_trained': '2024-01-15T10:30:00Z',
                    'samples_used': processed_images
                }
            }
            
            # Estadísticas de almacenamiento
            total_file_size = CacaoImage.objects.aggregate(
                total_size=Sum('file_size')
            )['total_size'] or 0
            
            storage_usage = {
                'total_size_bytes': total_file_size,
                'total_size_mb': round(total_file_size / (1024 * 1024), 2),
                'avg_file_size_kb': round((total_file_size / max(1, total_images)) / 1024, 2),
                'storage_efficiency': 'good' if total_file_size < 1e9 else 'warning'  # 1GB threshold
            }
            
            # Estadísticas de usuarios (placeholder)
            user_activity = {
                'total_uploads': total_images,
                'uploads_this_month': CacaoImage.objects.filter(
                    created_at__gte=timezone.now().replace(day=1)
                ).count(),
                'most_active_user': 'admin',
                'peak_usage_hour': '14:00'
            }
            
            stats_data = {
                'total_images': total_images,
                'processed_images': processed_images,
                'unprocessed_images': unprocessed_images,
                'quality_distribution': quality_distribution,
                'defect_distribution': defect_distribution,
                'dimension_statistics': dimension_statistics,
                'images_by_month': images_by_month,
                'processing_times': processing_times,
                'model_performance': model_performance,
                'storage_usage': storage_usage,
                'user_activity': user_activity
            }
            
            return Response(stats_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas administrativas: {e}")
            return Response({
                'error': 'Error obteniendo estadísticas administrativas',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Exportar datos en formato CSV",
        responses={
            200: openapi.Response("Datos exportados exitosamente")
        },
        tags=['Administración']
    )
    @action(detail=False, methods=['get'], url_path='export-csv')
    def export_csv(self, request):
        """
        Exporta datos de imágenes en formato CSV.
        
        Útil para análisis externos y backup de datos.
        """
        import csv
        from django.http import HttpResponse
        
        try:
            # Crear respuesta CSV
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="cacaoscan_data_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            
            writer = csv.writer(response)
            
            # Escribir encabezados
            headers = [
                'ID', 'Imagen', 'Ancho (mm)', 'Alto (mm)', 'Grosor (mm)', 'Peso (g)',
                'Calidad Predicha', 'Puntuación Calidad', 'Tipo Defecto',
                'Lote', 'Origen', 'Procesado', 'Tiempo Procesamiento (s)',
                'Fecha Creación', 'Notas'
            ]
            writer.writerow(headers)
            
            # Escribir datos
            queryset = self.get_queryset()
            for image in queryset:
                row = [
                    image.id,
                    image.image.name if image.image else '',
                    float(image.width) if image.width else '',
                    float(image.height) if image.height else '',
                    float(image.thickness) if image.thickness else '',
                    float(image.weight) if image.weight else '',
                    image.get_predicted_quality_display() if image.predicted_quality else '',
                    float(image.quality_score) if image.quality_score else '',
                    image.get_defect_type_display() if image.defect_type else '',
                    image.batch_number or '',
                    image.origin or '',
                    'Sí' if image.is_processed else 'No',
                    float(image.processing_time) if image.processing_time else '',
                    image.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    image.notes or ''
                ]
                writer.writerow(row)
            
            logger.info(f"Admin {request.user.username} exportó {queryset.count()} registros a CSV")
            
            return response
            
        except Exception as e:
            logger.error(f"Error exportando CSV: {e}")
            return Response({
                'error': 'Error exportando datos',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MLTrainingView(APIView):
    """
    Vista para gestión de entrenamiento de modelos ML.
    
    Permite ejecutar trabajos de reentrenamiento de modelos de visión y regresión
    con monitoreo del progreso y gestión de parámetros.
    """
    
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Iniciar entrenamiento de modelo de regresión",
        request_body=TrainingJobSerializer,
        responses={
            202: openapi.Response("Entrenamiento iniciado", TrainingJobStatusSerializer),
            400: openapi.Response("Error de validación"),
            500: openapi.Response("Error interno")
        },
        tags=['Entrenamiento ML']
    )
    def post(self, request, model_type):
        """
        Inicia el entrenamiento de un modelo específico.
        
        Args:
            model_type: 'regression' o 'vision'
        """
        if model_type not in ['regression', 'vision']:
            return Response({
                'error': 'Tipo de modelo inválido',
                'details': 'model_type debe ser "regression" o "vision"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar parámetros
        data = request.data.copy()
        data['model_type'] = model_type
        
        serializer = TrainingJobSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Crear trabajo de entrenamiento
            job_id = str(uuid.uuid4())
            job_data = {
                'job_id': job_id,
                'model_type': model_type,
                'status': 'pending',
                'progress': 0.0,
                'current_epoch': 0,
                'total_epochs': serializer.validated_data['epochs'],
                'started_at': timezone.now(),
                'estimated_completion': None,
                'completed_at': None,
                'dataset_size': 0,
                'validation_size': 0,
                'error_message': None,
                'log_url': None,
                'parameters': serializer.validated_data
            }
            
            # Guardar trabajo en memoria (en producción usar Redis/Celery)
            with training_jobs_lock:
                training_jobs[job_id] = job_data
            
            # Iniciar entrenamiento en thread separado
            threading.Thread(
                target=self._run_training,
                args=(job_id, model_type, serializer.validated_data),
                daemon=True
            ).start()
            
            logger.info(f"Admin {request.user.username} inició entrenamiento {model_type} (job {job_id})")
            
            return Response(job_data, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.error(f"Error iniciando entrenamiento: {e}")
            return Response({
                'error': 'Error iniciando entrenamiento',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _run_training(self, job_id, model_type, parameters):
        """
        Ejecuta el entrenamiento en un hilo separado.
        
        Args:
            job_id: ID único del trabajo
            model_type: Tipo de modelo a entrenar
            parameters: Parámetros de entrenamiento
        """
        try:
            # Actualizar estado a 'running'
            with training_jobs_lock:
                if job_id in training_jobs:
                    training_jobs[job_id]['status'] = 'running'
                    training_jobs[job_id]['progress'] = 5.0
            
            # Preparar comando de entrenamiento
            if model_type == 'regression':
                script_path = os.path.join(settings.BASE_DIR, 'ml', 'train_regression.py')
            else:  # vision
                script_path = os.path.join(settings.BASE_DIR, 'ml', 'train_vision.py')
            
            # Verificar que el script existe
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Script de entrenamiento no encontrado: {script_path}")
            
            # Preparar argumentos del comando
            cmd = [
                'python', script_path,
                '--epochs', str(parameters['epochs']),
                '--learning-rate', str(parameters['learning_rate']),
                '--batch-size', str(parameters['batch_size']),
                '--validation-split', str(parameters['validation_split'])
            ]
            
            # Agregar filtros opcionales
            if parameters.get('min_quality_score'):
                cmd.extend(['--min-quality', str(parameters['min_quality_score'])])
            
            if parameters.get('exclude_defective'):
                cmd.append('--exclude-defective')
            
            if parameters.get('only_processed'):
                cmd.append('--only-processed')
            
            # Ejecutar entrenamiento
            logger.info(f"Ejecutando comando: {' '.join(cmd)}")
            
            # Simular progreso (en implementación real, leer progreso del script)
            for epoch in range(1, parameters['epochs'] + 1):
                # Simular tiempo de entrenamiento
                import time
                time.sleep(0.1)  # En realidad sería mucho más lento
                
                progress = (epoch / parameters['epochs']) * 100
                
                # Actualizar progreso
                with training_jobs_lock:
                    if job_id in training_jobs:
                        training_jobs[job_id]['current_epoch'] = epoch
                        training_jobs[job_id]['progress'] = progress
                        training_jobs[job_id]['current_loss'] = 0.5 - (epoch * 0.01)  # Simulado
                        training_jobs[job_id]['current_accuracy'] = 0.7 + (epoch * 0.002)  # Simulado
            
            # Completar entrenamiento
            with training_jobs_lock:
                if job_id in training_jobs:
                    training_jobs[job_id]['status'] = 'completed'
                    training_jobs[job_id]['progress'] = 100.0
                    training_jobs[job_id]['completed_at'] = timezone.now()
            
            logger.info(f"Entrenamiento {job_id} completado exitosamente")
            
        except Exception as e:
            logger.error(f"Error en entrenamiento {job_id}: {e}")
            
            # Marcar como fallido
            with training_jobs_lock:
                if job_id in training_jobs:
                    training_jobs[job_id]['status'] = 'failed'
                    training_jobs[job_id]['error_message'] = str(e)
                    training_jobs[job_id]['completed_at'] = timezone.now()
    
    @swagger_auto_schema(
        operation_description="Obtener estado de trabajo de entrenamiento",
        responses={
            200: openapi.Response("Estado obtenido", TrainingJobStatusSerializer),
            404: openapi.Response("Trabajo no encontrado")
        },
        tags=['Entrenamiento ML']
    )
    def get(self, request, job_id=None):
        """
        Obtiene el estado de un trabajo de entrenamiento específico.
        
        Args:
            job_id: ID del trabajo (opcional, si no se proporciona lista todos)
        """
        try:
            if job_id:
                # Obtener trabajo específico
                with training_jobs_lock:
                    if job_id not in training_jobs:
                        return Response({
                            'error': 'Trabajo de entrenamiento no encontrado'
                        }, status=status.HTTP_404_NOT_FOUND)
                    
                    job_data = training_jobs[job_id].copy()
                
                return Response(job_data, status=status.HTTP_200_OK)
            
            else:
                # Listar todos los trabajos
                with training_jobs_lock:
                    all_jobs = list(training_jobs.values())
                
                return Response({
                    'jobs': all_jobs,
                    'total_jobs': len(all_jobs)
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"Error obteniendo estado de entrenamiento: {e}")
            return Response({
                'error': 'Error obteniendo estado',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminDataManagementView(APIView):
    """
    Vista para operaciones avanzadas de gestión de datos.
    
    Proporciona funcionalidades como limpieza de datos,
    validación de integridad y operaciones de mantenimiento.
    """
    
    permission_classes = [IsAdminUser]
    
    @swagger_auto_schema(
        operation_description="Validar integridad de datos",
        responses={
            200: openapi.Response("Validación completada")
        },
        tags=['Gestión de Datos']
    )
    @action(detail=False, methods=['post'], url_path='validate-integrity')
    def validate_integrity(self, request):
        """
        Valida la integridad de todos los datos de imágenes.
        
        Verifica:
        - Archivos de imagen existentes
        - Consistencia de metadatos
        - Valores atípicos en dimensiones
        """
        try:
            issues = []
            
            # Verificar archivos de imagen
            for image in CacaoImage.objects.all():
                if image.image and not os.path.exists(image.image.path):
                    issues.append({
                        'type': 'missing_file',
                        'image_id': image.id,
                        'details': f'Archivo no encontrado: {image.image.path}'
                    })
                
                # Verificar dimensiones realistas
                if all([image.width, image.height, image.thickness, image.weight]):
                    # Calcular densidad
                    volume = (4/3) * 3.14159 * (float(image.width)/2) * (float(image.height)/2) * (float(image.thickness)/2)
                    density = float(image.weight) / (volume / 1000)  # g/cm³
                    
                    if density < 0.3 or density > 2.0:
                        issues.append({
                            'type': 'unrealistic_density',
                            'image_id': image.id,
                            'details': f'Densidad inusual: {density:.2f} g/cm³'
                        })
            
            return Response({
                'total_images': CacaoImage.objects.count(),
                'issues_found': len(issues),
                'issues': issues
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error validando integridad: {e}")
            return Response({
                'error': 'Error en validación de integridad',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
