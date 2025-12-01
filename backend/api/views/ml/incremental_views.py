"""
Endpoints API para entrenamiento incremental de modelos de cacao.
"""
import logging
from pathlib import Path
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from typing import Dict, List, Any

from ...services import analysis_service
from core.utils import create_error_response, create_success_response, validate_target
from .mixins.incremental_mixin import IncrementalViewMixin
from .mixins.swagger_helpers import (
    create_incremental_swagger_decorator,
    create_incremental_success_response_schema
)
# Importar desde apps modulares
from ...utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'TrainingJob': 'training.models.TrainingJob',
    'CacaoPrediction': 'images_app.models.CacaoPrediction',
    'CacaoImage': 'images_app.models.CacaoImage'
})
TrainingJob = models['TrainingJob']
CacaoPrediction = models['CacaoPrediction']
CacaoImage = models['CacaoImage']

logger = logging.getLogger("cacaoscan.api")


class IncrementalTrainingStatusView(IncrementalViewMixin, APIView):
    """
    Endpoint para obtener el estado del sistema de entrenamiento incremental.
    """
    permission_classes = [IsAuthenticated]
    
    @create_incremental_swagger_decorator(
        operation_description="Obtiene el estado del sistema de entrenamiento incremental",
        operation_summary="Estado del entrenamiento incremental",
        responses={
            200: openapi.Response(
                description="Estado obtenido exitosamente",
                schema=create_incremental_success_response_schema()
            )
        }
    )
    def get(self, request):
        """
        Obtiene el estado del sistema de entrenamiento incremental.
        """
        try:
            from ml.pipeline.train_all import get_incremental_training_status
            
            status_data = get_incremental_training_status()
            
            return create_success_response(
                data=status_data,
                message="Estado del entrenamiento incremental obtenido exitosamente",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_incremental_error(e, "obteniendo estado incremental")


class IncrementalTrainingView(IncrementalViewMixin, APIView):
    """
    Endpoint para ejecutar entrenamiento incremental.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [JSONParser]
    
    
    @create_incremental_swagger_decorator(
        operation_description="Ejecuta entrenamiento incremental con nuevos datos",
        operation_summary="Entrenamiento incremental",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'new_data': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'image_path': openapi.Schema(type=openapi.TYPE_STRING),
                            'alto': openapi.Schema(type=openapi.TYPE_NUMBER),
                            'ancho': openapi.Schema(type=openapi.TYPE_NUMBER),
                            'grosor': openapi.Schema(type=openapi.TYPE_NUMBER),
                            'peso': openapi.Schema(type=openapi.TYPE_NUMBER)
                        }
                    )
                ),
                'target': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['alto', 'ancho', 'grosor', 'peso'],
                    default='alto'
                ),
                'epochs': openapi.Schema(type=openapi.TYPE_INTEGER, default=20),
                'batch_size': openapi.Schema(type=openapi.TYPE_INTEGER, default=16),
                'learning_rate': openapi.Schema(type=openapi.TYPE_NUMBER, default=1e-4),
                'strategy_type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['elastic_weight_consolidation', 'l2', 'replay', 'mixed'],
                    default='elastic_weight_consolidation'
                ),
                'ewc_lambda': openapi.Schema(type=openapi.TYPE_NUMBER, default=1000.0),
                'replay_ratio': openapi.Schema(type=openapi.TYPE_NUMBER, default=0.3)
            },
            required=['new_data', 'target']
        ),
        responses={
            200: openapi.Response(
                description="Entrenamiento incremental completado",
                schema=create_incremental_success_response_schema()
            )
        }
    )
    def post(self, request):
        """
        Ejecuta entrenamiento incremental con nuevos datos.
        """
        try:
            # Validar datos de entrada
            new_data = request.data.get('new_data')
            target = request.data.get('target', 'alto')
            
            if not new_data:
                return self.handle_validation_error("new_data es requerido")
            
            validation_error = validate_target(target)
            if validation_error:
                return validation_error
            
            # Validar estructura de datos
            for i, record in enumerate(new_data):
                if not isinstance(record, dict):
                    return self.handle_validation_error(f"Registro {i} debe ser un diccionario")
                
                required_fields = ['id', 'image_path', target]
                missing_fields = [field for field in required_fields if field not in record]
                if missing_fields:
                    return self.handle_validation_error(
                        f"Registro {i} faltan campos: {', '.join(missing_fields)}"
                    )
            
            # Crear job de entrenamiento
            training_job = TrainingJob.objects.create(
                user=request.user,
                job_type='incremental_training',
                status='running',
                config={
                    'target': target,
                    'epochs': request.data.get('epochs', 20),
                    'batch_size': request.data.get('batch_size', 16),
                    'learning_rate': request.data.get('learning_rate', 1e-4),
                    'strategy_type': request.data.get('strategy_type', 'elastic_weight_consolidation'),
                    'ewc_lambda': request.data.get('ewc_lambda', 1000.0),
                    'replay_ratio': request.data.get('replay_ratio', 0.3),
                    'samples_count': len(new_data)
                },
                started_at=timezone.now()
            )
            
            # Ejecutar entrenamiento incremental
            from ml.pipeline.train_all import run_incremental_training_pipeline
            
            success = run_incremental_training_pipeline(
                new_data=new_data,
                target=target,
                epochs=request.data.get('epochs', 20),
                batch_size=request.data.get('batch_size', 16),
                learning_rate=request.data.get('learning_rate', 1e-4),
                strategy_type=request.data.get('strategy_type', 'elastic_weight_consolidation'),
                ewc_lambda=request.data.get('ewc_lambda', 1000.0),
                replay_ratio=request.data.get('replay_ratio', 0.3)
            )
            
            # Actualizar job
            if success:
                training_job.status = 'completed'
                training_job.completed_at = timezone.now()
                training_job.results = {
                    'success': True,
                    'samples_processed': len(new_data),
                    'target': target
                }
            else:
                training_job.status = 'failed'
                training_job.completed_at = timezone.now()
                training_job.results = {
                    'success': False,
                    'error': 'Entrenamiento incremental falló'
                }
            
            training_job.save()
            
            if success:
                return create_success_response(
                    data={
                        'job_id': training_job.id,
                        'target': target,
                        'samples_processed': len(new_data),
                        'status': 'completed'
                    },
                    message="Entrenamiento incremental completado exitosamente",
                    status_code=status.HTTP_200_OK
                )
            else:
                return self.handle_validation_error("Error en entrenamiento incremental")
                
        except Exception as e:
            # Actualizar job si existe
            if 'training_job' in locals():
                training_job.status = 'failed'
                training_job.completed_at = timezone.now()
                training_job.results = {'success': False, 'error': str(e)}
                training_job.save()
            
            return self.handle_incremental_error(e, "entrenamiento incremental")


class IncrementalDataUploadView(IncrementalViewMixin, APIView):
    """
    Endpoint para subir datos para entrenamiento incremental.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    
    @create_incremental_swagger_decorator(
        operation_description="Sube datos para entrenamiento incremental",
        operation_summary="Subir datos incrementales",
        manual_parameters=[
            openapi.Parameter(
                'csv_file',
                openapi.IN_FORM,
                description="Archivo CSV con nuevos datos",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'images_zip',
                openapi.IN_FORM,
                description="Archivo ZIP con imágenes correspondientes",
                type=openapi.TYPE_FILE,
                required=False
            ),
            openapi.Parameter(
                'target',
                openapi.IN_FORM,
                description="Target específico",
                type=openapi.TYPE_STRING,
                enum=['alto', 'ancho', 'grosor', 'peso'],
                default='alto'
            )
        ],
        responses={
            200: openapi.Response(
                description="Datos subidos exitosamente",
                schema=create_incremental_success_response_schema()
            )
        }
    )
    def post(self, request):
        """
        Sube datos para entrenamiento incremental.
        """
        try:
            csv_file = request.FILES.get('csv_file')
            images_zip = request.FILES.get('images_zip')
            target = request.POST.get('target', 'alto')
            
            if not csv_file:
                return self.handle_validation_error("csv_file es requerido")
            
            validation_error = validate_target(target)
            if validation_error:
                return validation_error
            
            # Procesar archivo CSV
            import pandas as pd
            import io
            
            # Leer CSV
            csv_content = csv_file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(csv_content))
            
            # Validar columnas requeridas
            required_columns = ['ID', 'ALTO', 'ANCHO', 'GROSOR', 'PESO']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return self.handle_validation_error(
                    f"Columnas faltantes en CSV: {', '.join(missing_columns)}"
                )
            
            # Convertir a formato esperado
            new_data = []
            for _, row in df.iterrows():
                record = {
                    'id': int(row['ID']),
                    'image_path': f"backend/media/cacao_images/raw/{int(row['ID'])}.bmp",
                    'alto': float(row['ALTO']),
                    'ancho': float(row['ANCHO']),
                    'grosor': float(row['GROSOR']),
                    'peso': float(row['PESO'])
                }
                new_data.append(record)
            
            # Procesar imágenes ZIP si se proporciona
            if images_zip:
                import zipfile
                import tempfile
                import os
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    with zipfile.ZipFile(images_zip, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    # Mover imágenes a directorio correcto
                    images_dir = Path("backend/media/cacao_images/raw")
                    images_dir.mkdir(parents=True, exist_ok=True)
                    
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                                src_path = os.path.join(root, file)
                                dst_path = images_dir / f"{file}"
                                os.rename(src_path, dst_path)
            
            # Guardar datos en sistema incremental
            from ml.regression.incremental_train import IncrementalDataManager
            
            data_manager = IncrementalDataManager()
            version = data_manager.add_new_data(new_data, f"upload_{target}_{timezone.now().strftime('%Y%m%d_%H%M%S')}")
            
            return create_success_response(
                data={
                    'version': version,
                    'samples_count': len(new_data),
                    'target': target,
                    'data_preview': new_data[:5]  # Primeros 5 registros como preview
                },
                message=f"Datos subidos exitosamente. Versión {version} creada con {len(new_data)} muestras",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_incremental_error(e, "subiendo datos incrementales")


class IncrementalModelVersionsView(IncrementalViewMixin, APIView):
    """
    Endpoint para obtener versiones de modelos incrementales.
    """
    permission_classes = [IsAuthenticated]
    
    @create_incremental_swagger_decorator(
        operation_description="Obtiene información de versiones de modelos incrementales",
        operation_summary="Versiones de modelos incrementales",
        manual_parameters=[
            openapi.Parameter(
                'target',
                openapi.IN_QUERY,
                description="Target específico",
                type=openapi.TYPE_STRING,
                enum=['alto', 'ancho', 'grosor', 'peso']
            ),
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Límite de versiones a retornar",
                type=openapi.TYPE_INTEGER,
                default=10
            )
        ],
        responses={
            200: openapi.Response(
                description="Versiones obtenidas exitosamente",
                schema=create_incremental_success_response_schema()
            )
        }
    )
    def get(self, request):
        """
        Obtiene información de versiones de modelos incrementales.
        """
        try:
            target = request.GET.get('target')
            limit = int(request.GET.get('limit', 10))
            
            from ml.regression.incremental_train import IncrementalModelManager
            
            model_manager = IncrementalModelManager()
            versions = model_manager.list_model_versions()
            
            # Filtrar por target si se especifica
            if target:
                filtered_versions = []
                for version in versions:
                    if target in version.get('performance_metrics', {}):
                        filtered_versions.append(version)
                versions = filtered_versions
            
            # Limitar resultados
            versions = versions[-limit:] if limit > 0 else versions
            
            return create_success_response(
                data={
                    'versions': versions,
                    'total_versions': len(model_manager.model_metadata["versions"]),
                    'current_version': model_manager.current_version,
                    'best_performance': model_manager.model_metadata.get("best_performance", {})
                },
                message="Versiones de modelos obtenidas exitosamente",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_incremental_error(e, "obteniendo versiones de modelos")


class IncrementalDataVersionsView(IncrementalViewMixin, APIView):
    """
    Endpoint para obtener versiones de datos incrementales.
    """
    permission_classes = [IsAuthenticated]
    
    @create_incremental_swagger_decorator(
        operation_description="Obtiene información de versiones de datos incrementales",
        operation_summary="Versiones de datos incrementales",
        manual_parameters=[
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Límite de versiones a retornar",
                type=openapi.TYPE_INTEGER,
                default=10
            )
        ],
        responses={
            200: openapi.Response(
                description="Versiones obtenidas exitosamente",
                schema=create_incremental_success_response_schema()
            )
        }
    )
    def get(self, request):
        """
        Obtiene información de versiones de datos incrementales.
        """
        try:
            limit = int(request.GET.get('limit', 10))
            
            from ml.regression.incremental_train import IncrementalDataManager
            
            data_manager = IncrementalDataManager()
            versions = data_manager.list_versions()
            
            # Limitar resultados
            versions = versions[-limit:] if limit > 0 else versions
            
            return create_success_response(
                data={
                    'versions': versions,
                    'total_versions': len(data_manager.dataset_metadata["versions"]),
                    'current_version': data_manager.current_version,
                    'total_samples': data_manager.dataset_metadata.get("total_samples", 0)
                },
                message="Versiones de datos obtenidas exitosamente",
                status_code=status.HTTP_200_OK
            )
            
        except Exception as e:
            return self.handle_incremental_error(e, "obteniendo versiones de datos")


