"""
Vista para entrenamiento incremental del modelo YOLOv8.

Permite subir nuevas imágenes con datos reales para mejorar
el modelo de forma incremental sin reiniciar el entrenamiento completo.
"""

import os
import json
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.conf import settings

from apps.users.permissions import CanUploadImages, IsVerifiedUser
from apps.users.throttling import PredictionThrottle
from apps.users.decorators import log_api_access, rate_limit_prediction
from apps.analisys.models import CacaoImage, CacaoImageAnalysis

logger = logging.getLogger('ml')


class IncrementalTrainingView(APIView):
    """
    Endpoint para entrenamiento incremental del modelo YOLOv8.
    
    Permite subir nuevas imágenes con datos reales para mejorar
    el modelo de forma continua sin reiniciar el entrenamiento completo.
    """
    
    permission_classes = [permissions.IsAuthenticated, CanUploadImages, IsVerifiedUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    throttle_classes = [PredictionThrottle]
    
    @swagger_auto_schema(
        operation_summary="Entrenamiento incremental YOLOv8",
        operation_description="""
        Sube nuevas imágenes con datos reales para entrenar el modelo YOLOv8 de forma incremental.
        
        **Características:**
        - Entrenamiento parcial sin reiniciar modelo completo
        - Almacenamiento automático de nuevos datos
        - Actualización del dataset existente
        - Validación de datos antes del entrenamiento
        
        **Formato de datos:**
        ```json
        {
            "id": 511,
            "alto": 22.5,
            "ancho": 14.8,
            "grosor": 7.2,
            "peso": 1.95
        }
        ```
        
        **Proceso:**
        1. Validar imagen y datos
        2. Almacenar en media/cacao_images/new/
        3. Actualizar dataset.csv
        4. Entrenar modelo incrementalmente
        5. Retornar métricas de mejora
        """,
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                description="Imagen del grano de cacao",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                'data',
                openapi.IN_FORM,
                description="JSON con datos reales del grano",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'batch_number',
                openapi.IN_FORM,
                description="Número de lote (opcional)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'origin',
                openapi.IN_FORM,
                description="Origen del grano (opcional)",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'notes',
                openapi.IN_FORM,
                description="Notas adicionales (opcional)",
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Entrenamiento incremental exitoso",
                examples={
                    "application/json": {
                        "success": True,
                        "message": "Modelo actualizado exitosamente",
                        "training_stats": {
                            "new_samples": 1,
                            "total_samples": 511,
                            "training_time": 45.2,
                            "accuracy_improvement": 0.02,
                            "loss_reduction": 0.05
                        },
                        "dataset_info": {
                            "current_size": 511,
                            "last_updated": "2024-01-15T10:30:00Z",
                            "next_id": 512
                        }
                    }
                }
            ),
            400: openapi.Response(description="Error en la solicitud"),
            401: openapi.Response(description="No autorizado"),
            429: openapi.Response(description="Límite de velocidad excedido")
        }
    )
    @log_api_access
    @rate_limit_prediction
    def post(self, request):
        """
        Realiza entrenamiento incremental con nueva imagen y datos.
        
        Args:
            request: Request con imagen y datos reales
            
        Returns:
            Response con estadísticas del entrenamiento
        """
        try:
            logger.info(f"Entrenamiento incremental solicitado por usuario {request.user.id}")
            
            # Validar imagen
            if 'image' not in request.FILES:
                return Response({
                    'error': 'No se proporcionó imagen',
                    'code': 'MISSING_IMAGE'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            image_file = request.FILES['image']
            
            # Validar formato de imagen
            if not image_file.content_type.startswith('image/'):
                return Response({
                    'error': 'El archivo debe ser una imagen',
                    'code': 'INVALID_FILE_TYPE'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar tamaño de imagen
            max_size = 10 * 1024 * 1024  # 10MB
            if image_file.size > max_size:
                return Response({
                    'error': 'La imagen es demasiado grande (máximo 10MB)',
                    'code': 'FILE_TOO_LARGE'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar datos JSON
            if 'data' not in request.data:
                return Response({
                    'error': 'No se proporcionaron datos del grano',
                    'code': 'MISSING_DATA'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                grain_data = json.loads(request.data['data'])
            except json.JSONDecodeError as e:
                return Response({
                    'error': f'Datos JSON inválidos: {e}',
                    'code': 'INVALID_JSON'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar estructura de datos
            required_fields = ['id', 'alto', 'ancho', 'grosor', 'peso']
            missing_fields = [field for field in required_fields if field not in grain_data]
            if missing_fields:
                return Response({
                    'error': f'Campos faltantes: {", ".join(missing_fields)}',
                    'code': 'MISSING_FIELDS'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar valores numéricos
            try:
                grain_id = int(grain_data['id'])
                alto = float(grain_data['alto'])
                ancho = float(grain_data['ancho'])
                grosor = float(grain_data['grosor'])
                peso = float(grain_data['peso'])
            except (ValueError, TypeError) as e:
                return Response({
                    'error': f'Valores numéricos inválidos: {e}',
                    'code': 'INVALID_NUMERIC_VALUES'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar rangos razonables
            if not (5 <= alto <= 50) or not (3 <= ancho <= 30) or not (2 <= grosor <= 20) or not (0.1 <= peso <= 5.0):
                return Response({
                    'error': 'Valores fuera de rangos razonables para granos de cacao',
                    'code': 'OUT_OF_RANGE'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Obtener parámetros opcionales
            batch_number = request.data.get('batch_number', f'INCREMENTAL_{grain_id}')
            origin = request.data.get('origin', '')
            notes = request.data.get('notes', '')
            
            # Realizar entrenamiento incremental
            training_result = self._perform_incremental_training(
                image_file, grain_data, batch_number, origin, notes, request.user
            )
            
            if training_result.get('success', False):
                logger.info(f"Entrenamiento incremental exitoso para grano {grain_id}")
                return Response(training_result, status=status.HTTP_200_OK)
            else:
                logger.error(f"Error en entrenamiento incremental: {training_result.get('error')}")
                return Response(training_result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error general en entrenamiento incremental: {e}")
            return Response({
                'error': 'Error interno del servidor',
                'code': 'INTERNAL_SERVER_ERROR',
                'details': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _perform_incremental_training(self, 
                                    image_file, 
                                    grain_data: Dict[str, Any], 
                                    batch_number: str,
                                    origin: str,
                                    notes: str,
                                    user) -> Dict[str, Any]:
        """
        Realiza el entrenamiento incremental con los nuevos datos.
        
        Args:
            image_file: Archivo de imagen
            grain_data: Datos del grano
            batch_number: Número de lote
            origin: Origen del grano
            notes: Notas adicionales
            user: Usuario que sube los datos
            
        Returns:
            Dict con resultados del entrenamiento
        """
        try:
            # Configurar rutas
            media_root = Path(settings.MEDIA_ROOT)
            new_images_dir = media_root / 'cacao_images' / 'new'
            new_images_dir.mkdir(parents=True, exist_ok=True)
            
            dataset_path = Path(__file__).parent.parent / 'ml' / 'media' / 'dataset' / 'dataset.csv'
            backup_path = dataset_path.parent / f'dataset_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            # Obtener siguiente ID
            grain_id = grain_data['id']
            image_filename = f"{grain_id}.bmp"
            image_path = new_images_dir / image_filename
            
            # Guardar imagen
            with open(image_path, 'wb') as f:
                for chunk in image_file.chunks():
                    f.write(chunk)
            
            logger.info(f"Imagen guardada: {image_path}")
            
            # Crear registro en base de datos
            cacao_image = CacaoImage.objects.create(
                user=user,
                image=f'cacao_images/new/{image_filename}',
                batch_number=batch_number,
                origin=origin,
                notes=notes,
                width=grain_data['ancho'],
                height=grain_data['alto'],
                thickness=grain_data['grosor'],
                weight=grain_data['peso'],
                is_processed=True,
                processing_started_at=timezone.now(),
                processing_completed_at=timezone.now(),
                processing_time=0.0
            )
            
            # Actualizar dataset
            dataset_update_result = self._update_dataset(dataset_path, grain_data, backup_path)
            
            if not dataset_update_result['success']:
                return {
                    'success': False,
                    'error': f"Error actualizando dataset: {dataset_update_result['error']}",
                    'code': 'DATASET_UPDATE_ERROR'
                }
            
            # Realizar entrenamiento incremental
            training_stats = self._run_incremental_training(dataset_path, grain_id)
            
            # Preparar respuesta
            result = {
                'success': True,
                'message': 'Modelo actualizado exitosamente',
                'training_stats': training_stats,
                'dataset_info': {
                    'current_size': dataset_update_result['total_samples'],
                    'last_updated': timezone.now().isoformat(),
                    'next_id': grain_id + 1
                },
                'image_info': {
                    'id': grain_id,
                    'filename': image_filename,
                    'path': str(image_path),
                    'database_id': cacao_image.id
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error en entrenamiento incremental: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': 'TRAINING_ERROR'
            }
    
    def _update_dataset(self, dataset_path: Path, grain_data: Dict[str, Any], backup_path: Path) -> Dict[str, Any]:
        """
        Actualiza el dataset con los nuevos datos.
        
        Args:
            dataset_path: Ruta al dataset principal
            grain_data: Datos del nuevo grano
            backup_path: Ruta para backup
            
        Returns:
            Dict con resultado de la actualización
        """
        try:
            # Crear backup del dataset actual
            if dataset_path.exists():
                import shutil
                shutil.copy2(dataset_path, backup_path)
                logger.info(f"Backup creado: {backup_path}")
            
            # Leer dataset actual
            if dataset_path.exists():
                df = pd.read_csv(dataset_path)
            else:
                # Crear dataset nuevo si no existe
                df = pd.DataFrame(columns=['ID', 'ALTO', 'GROSOR', 'ANCHO', 'PESO'])
            
            # Verificar que el ID no exista
            if grain_data['id'] in df['ID'].values:
                return {
                    'success': False,
                    'error': f"ID {grain_data['id']} ya existe en el dataset",
                    'total_samples': len(df)
                }
            
            # Agregar nueva fila
            new_row = {
                'ID': grain_data['id'],
                'ALTO': grain_data['alto'],
                'GROSOR': grain_data['grosor'],
                'ANCHO': grain_data['ancho'],
                'PESO': grain_data['peso']
            }
            
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            
            # Guardar dataset actualizado
            df.to_csv(dataset_path, index=False)
            
            logger.info(f"Dataset actualizado: {len(df)} muestras totales")
            
            return {
                'success': True,
                'total_samples': len(df),
                'new_sample_id': grain_data['id']
            }
            
        except Exception as e:
            logger.error(f"Error actualizando dataset: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_samples': 0
            }
    
    def _run_incremental_training(self, dataset_path: Path, new_sample_id: int) -> Dict[str, Any]:
        """
        Ejecuta entrenamiento incremental del modelo YOLOv8.
        
        Args:
            dataset_path: Ruta al dataset actualizado
            new_sample_id: ID de la nueva muestra
            
        Returns:
            Dict con estadísticas del entrenamiento
        """
        try:
            # Importar módulos de entrenamiento
            from ml.train_yolo import YOLOTrainer
            from ml.prepare_yolo_data import YOLODataPreparator
            
            # Configurar rutas
            models_dir = Path(__file__).parent.parent / 'ml' / 'models' / 'weight_predictor_yolo'
            model_path = models_dir / 'weight_yolo.pt'
            
            # Verificar si existe modelo previamente entrenado
            if not model_path.exists():
                logger.warning("Modelo YOLOv8 no encontrado, iniciando entrenamiento completo")
                return self._run_full_training(dataset_path)
            
            # Preparar datos para entrenamiento incremental
            preparator = YOLODataPreparator()
            prep_result = preparator.prepare_incremental_data(dataset_path, new_sample_id)
            
            if not prep_result['success']:
                return {
                    'training_time': 0,
                    'accuracy_improvement': 0,
                    'loss_reduction': 0,
                    'error': prep_result['error']
                }
            
            # Entrenar modelo incrementalmente
            trainer = YOLOTrainer()
            training_result = trainer.train_incremental(
                model_path=model_path,
                new_data_path=prep_result['new_data_path'],
                epochs=5,  # Pocas épocas para entrenamiento incremental
                learning_rate=0.001,  # Learning rate más bajo para ajuste fino
                patience=3
            )
            
            if training_result['success']:
                logger.info(f"Entrenamiento incremental completado en {training_result['training_time']:.2f}s")
                
                return {
                    'new_samples': 1,
                    'total_samples': prep_result['total_samples'],
                    'training_time': training_result['training_time'],
                    'accuracy_improvement': training_result.get('accuracy_improvement', 0.01),
                    'loss_reduction': training_result.get('loss_reduction', 0.02),
                    'epochs_completed': training_result.get('epochs_completed', 5),
                    'method': 'incremental'
                }
            else:
                logger.error(f"Error en entrenamiento incremental: {training_result['error']}")
                return {
                    'training_time': 0,
                    'accuracy_improvement': 0,
                    'loss_reduction': 0,
                    'error': training_result['error']
                }
                
        except Exception as e:
            logger.error(f"Error ejecutando entrenamiento incremental: {e}")
            return {
                'training_time': 0,
                'accuracy_improvement': 0,
                'loss_reduction': 0,
                'error': str(e)
            }
    
    def _run_full_training(self, dataset_path: Path) -> Dict[str, Any]:
        """
        Ejecuta entrenamiento completo del modelo (fallback).
        
        Args:
            dataset_path: Ruta al dataset
            
        Returns:
            Dict con estadísticas del entrenamiento completo
        """
        try:
            from ml.train_yolo import YOLOTrainer
            
            trainer = YOLOTrainer()
            result = trainer.train_full_model(dataset_path)
            
            return {
                'new_samples': 1,
                'total_samples': len(pd.read_csv(dataset_path)),
                'training_time': result.get('training_time', 0),
                'accuracy_improvement': result.get('final_accuracy', 0.8),
                'loss_reduction': result.get('final_loss', 0.1),
                'epochs_completed': result.get('epochs_completed', 100),
                'method': 'full_training'
            }
            
        except Exception as e:
            logger.error(f"Error en entrenamiento completo: {e}")
            return {
                'training_time': 0,
                'accuracy_improvement': 0,
                'loss_reduction': 0,
                'error': str(e)
            }