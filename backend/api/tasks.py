"""
Tareas asíncronas de Celery para CacaoScan.
"""
import logging
from pathlib import Path
from celery import shared_task
from django.utils import timezone
from training.models import TrainingJob
from ml.pipeline.train_all import run_training_pipeline
from ml.utils.paths import get_datasets_dir
from ml.segmentation.train_yolo import train_cacao_yolo_model

logger = logging.getLogger("cacaoscan.api.tasks")


@shared_task(bind=True, name='api.tasks.train_model')
def train_model_task(self, job_id: str, config: dict):
    """
    Tarea asíncrona para entrenar un modelo ML.
    
    Args:
        job_id: ID del TrainingJob
        config: Configuración del entrenamiento
        
    Returns:
        dict: Resultado del entrenamiento
    """
    try:
        job = TrainingJob.objects.get(job_id=job_id)
        job.status = 'running'
        job.started_at = timezone.now()
        job.save()
        
        logger.info(f"Iniciando entrenamiento para job {job_id}")
        job.update_progress(5, "Inicializando pipeline...")
        
        # Asegurar que se use dataset_cacao.clean.csv
        datasets_dir = get_datasets_dir()
        clean_csv_path = datasets_dir / "dataset_cacao.clean.csv"
        
        if not clean_csv_path.exists():
            error_msg = f"Dataset limpio no encontrado: {clean_csv_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        logger.info(f"Usando dataset: {clean_csv_path}")
        job.update_progress(10, f"Cargando dataset: {clean_csv_path.name}")
        
        # Ejecutar entrenamiento con configuración mejorada para alta confianza
        success = run_training_pipeline(
            epochs=config.get('epochs', 150),  # Aumentado de 30 a 150 para mejor aprendizaje
            batch_size=config.get('batch_size', 16),
            learning_rate=config.get('learning_rate', 0.001),
            multi_head=config.get('multi_head', False),
            model_type=config.get('model_type', 'resnet18'),
            img_size=config.get('img_size', 224),
            early_stopping_patience=config.get('early_stopping_patience', 25),  # Más patience
            save_best_only=config.get('save_best_only', True)
        )
        
        if success:
            job.status = 'completed'
            job.completed_at = timezone.now()
            job.progress_percentage = 100.0
            job.logs += "\n[FINALIZADO] Entrenamiento completado exitosamente"
            job.save()
            
            logger.info(f"Entrenamiento completado para job {job_id}")
            return {
                'status': 'completed',
                'job_id': job_id,
                'message': 'Entrenamiento completado exitosamente'
            }
        else:
            raise Exception("El entrenamiento falló")
            
    except TrainingJob.DoesNotExist:
        logger.error(f"TrainingJob {job_id} no encontrado")
        return {
            'status': 'failed',
            'job_id': job_id,
            'error': 'Job no encontrado'
        }
    except Exception as e:
        logger.error(f"Error en entrenamiento para job {job_id}: {e}", exc_info=True)
        if 'job' in locals():
            job.status = 'failed'
            job.logs += f"\n[ERROR] {str(e)}"
            job.save()
        return {
            'status': 'failed',
            'job_id': job_id,
            'error': str(e)
        }


@shared_task(bind=True, name='api.tasks.auto_train_model')
def auto_train_model_task(self, force: bool = False, config: dict = None):
    """
    Tarea asíncrona para entrenar automáticamente el modelo después de hacer pull.
    Usa el comando existente train_cacao_models con parámetros personalizables.
    
    Args:
        force: Si True, fuerza el entrenamiento aunque no haya cambios detectados
        config: Configuración personalizada del entrenamiento. Si es None, usa valores por defecto.
        
    Returns:
        dict: Resultado del entrenamiento
    """
    try:
        logger.info("Iniciando entrenamiento automático del modelo")
        
        # Verificar que existe el dataset
        datasets_dir = get_datasets_dir()
        clean_csv_path = datasets_dir / "dataset_cacao.clean.csv"
        
        if not clean_csv_path.exists():
            logger.warning(f"Dataset no encontrado en {clean_csv_path}")
            return {
                'status': 'skipped',
                'message': 'Dataset no encontrado. Ejecuta: python manage.py prepare_dataset'
            }
        
        # Verificar que hay imágenes .bmp en raw
        raw_images_dir = Path('media/cacao_images/raw')
        bmp_files = list(raw_images_dir.rglob('*.bmp')) + list(raw_images_dir.rglob('*.BMP'))
        
        if not raw_images_dir.exists() or not bmp_files:
            logger.warning(f"No se encontraron imágenes .bmp en {raw_images_dir}")
            return {
                'status': 'skipped',
                'message': f'No se encontraron imágenes .bmp para entrenar'
            }
        
        logger.info(f"Encontradas {len(bmp_files)} imágenes .bmp para entrenar")
        
        # Usar configuración personalizada si se proporciona, sino valores por defecto
        if config:
            training_config = config
        else:
            training_config = {
                'epochs': 150,
                'batch_size': 16,
                'learning_rate': 0.001,
                'multi_head': False,
                'model_type': 'resnet18',
                'img_size': 224,
                'early_stopping_patience': 25,
                'save_best_only': True
            }
        
        # Ejecutar entrenamiento usando run_training_pipeline
        success = run_training_pipeline(
            epochs=training_config.get('epochs', 150),
            batch_size=training_config.get('batch_size', 16),
            learning_rate=training_config.get('learning_rate', 0.001),
            multi_head=training_config.get('multi_head', False),
            model_type=training_config.get('model_type', 'resnet18'),
            img_size=training_config.get('img_size', 224),
            early_stopping_patience=training_config.get('early_stopping_patience', 25),
            save_best_only=training_config.get('save_best_only', True)
        )
        
        if success:
            logger.info("Entrenamiento automático completado exitosamente")
            return {
                'status': 'completed',
                'message': 'Entrenamiento automático completado exitosamente'
            }
        else:
            return {
                'status': 'failed',
                'message': 'El entrenamiento falló'
            }
            
    except Exception as e:
        logger.error(f"Error en entrenamiento automático: {e}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task(bind=True, name='api.tasks.train_yolo_model')
def train_yolo_model_task(self, config: dict = None):
    """
    Tarea asíncrona para entrenar modelo YOLO personalizado.
    
    Args:
        config: Configuración del entrenamiento YOLO. Si es None, usa valores por defecto.
        
    Returns:
        dict: Resultado del entrenamiento YOLO
    """
    try:
        logger.info("Iniciando entrenamiento de modelo YOLO personalizado")
        
        # Verificar que existe el dataset
        datasets_dir = get_datasets_dir()
        csv_path = datasets_dir / "dataset_cacao.csv"
        
        if not csv_path.exists():
            logger.warning(f"Dataset no encontrado en {csv_path}")
            return {
                'status': 'skipped',
                'message': 'Dataset no encontrado. Ejecuta: python manage.py prepare_dataset'
            }
        
        # Verificar que hay imágenes raw
        from ml.utils.paths import get_raw_images_dir
        raw_images_dir = get_raw_images_dir()
        
        if not raw_images_dir.exists() or len(list(raw_images_dir.glob("*.bmp"))) == 0:
            logger.warning(f"No se encontraron imágenes .bmp en {raw_images_dir}")
            return {
                'status': 'skipped',
                'message': f'No se encontraron imágenes .bmp para entrenar'
            }
        
        # Configuración por defecto
        if config is None:
            config = {
                'dataset_size': 150,
                'epochs': 100,
                'batch_size': 16,
                'model_name': 'yolov8s-seg',
                'image_size': 640,
                'confidence': 0.5,
                'iou_threshold': 0.7
            }
        
        logger.info(f"Configuración YOLO: {config}")
        
        # Ejecutar entrenamiento YOLO
        results = train_cacao_yolo_model(
            dataset_size=config.get('dataset_size', 150),
            epochs=config.get('epochs', 100),
            batch_size=config.get('batch_size', 16),
            model_name=config.get('model_name', 'yolov8s-seg')
        )
        
        if results and results.get('best_model_path'):
            logger.info("Entrenamiento YOLO completado exitosamente")
            return {
                'status': 'completed',
                'message': 'Entrenamiento YOLO completado exitosamente',
                'best_model_path': results.get('best_model_path'),
                'results': results
            }
        else:
            return {
                'status': 'failed',
                'message': 'El entrenamiento YOLO falló'
            }
            
    except Exception as e:
        logger.error(f"Error en entrenamiento YOLO: {e}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(e)
        }


@shared_task(bind=True, name='api.tasks.train_all_models')
def train_all_models_task(self, yolo_config: dict = None, regression_config: dict = None):
    """
    Tarea asíncrona para entrenar TODOS los modelos: YOLO + modelos de regresión.
    
    Args:
        yolo_config: Configuración del entrenamiento YOLO. Si es None, usa valores por defecto.
        regression_config: Configuración del entrenamiento de regresión. Si es None, usa valores por defecto.
        
    Returns:
        dict: Resultado del entrenamiento completo
    """
    try:
        logger.info("Iniciando entrenamiento completo: YOLO + Modelos de Regresión")
        
        results = {
            'yolo': None,
            'regression': None,
            'status': 'running'
        }
        
        # Paso 1: Entrenar YOLO (síncrono dentro de esta tarea)
        logger.info("Paso 1/2: Entrenando modelo YOLO...")
        try:
            # Llamar directamente a la función (no como tarea para mantener orden secuencial)
            from ml.segmentation.train_yolo import train_cacao_yolo_model
            
            # Configuración por defecto para YOLO
            if yolo_config is None:
                yolo_config = {
                    'dataset_size': 150,
                    'epochs': 100,
                    'batch_size': 16,
                    'model_name': 'yolov8s-seg'
                }
            
            yolo_result = train_cacao_yolo_model(
                dataset_size=yolo_config.get('dataset_size', 150),
                epochs=yolo_config.get('epochs', 100),
                batch_size=yolo_config.get('batch_size', 16),
                model_name=yolo_config.get('model_name', 'yolov8s-seg')
            )
            
            if yolo_result and yolo_result.get('best_model_path'):
                results['yolo'] = {
                    'status': 'completed',
                    'message': 'Entrenamiento YOLO completado exitosamente',
                    'best_model_path': yolo_result.get('best_model_path')
                }
                logger.info("✓ Entrenamiento YOLO completado")
            else:
                results['yolo'] = {
                    'status': 'failed',
                    'message': 'El entrenamiento YOLO falló'
                }
                logger.warning("Entrenamiento YOLO falló, pero continuando con regresión...")
        except Exception as e:
            logger.error(f"Error en entrenamiento YOLO: {e}", exc_info=True)
            results['yolo'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # Paso 2: Entrenar modelos de regresión (síncrono dentro de esta tarea)
        logger.info("Paso 2/2: Entrenando modelos de regresión...")
        try:
            # Configuración por defecto para regresión
            if regression_config is None:
                regression_config = {
                    'epochs': 150,
                    'batch_size': 16,
                    'learning_rate': 0.001,
                    'multi_head': False,
                    'model_type': 'resnet18',
                    'img_size': 224,
                    'early_stopping_patience': 25,
                    'save_best_only': True
                }
            
            # Ejecutar entrenamiento de regresión directamente
            regression_success = run_training_pipeline(
                epochs=regression_config.get('epochs', 150),
                batch_size=regression_config.get('batch_size', 16),
                learning_rate=regression_config.get('learning_rate', 0.001),
                multi_head=regression_config.get('multi_head', False),
                model_type=regression_config.get('model_type', 'resnet18'),
                img_size=regression_config.get('img_size', 224),
                early_stopping_patience=regression_config.get('early_stopping_patience', 25),
                save_best_only=regression_config.get('save_best_only', True)
            )
            
            if regression_success:
                results['regression'] = {
                    'status': 'completed',
                    'message': 'Entrenamiento de regresión completado exitosamente'
                }
                logger.info("✓ Entrenamiento de regresión completado")
            else:
                results['regression'] = {
                    'status': 'failed',
                    'message': 'El entrenamiento de regresión falló'
                }
                logger.warning("Entrenamiento de regresión falló")
        except Exception as e:
            logger.error(f"Error en entrenamiento de regresión: {e}", exc_info=True)
            results['regression'] = {
                'status': 'failed',
                'error': str(e)
            }
        
        # Determinar estado final
        yolo_ok = results['yolo'] and results['yolo'].get('status') in ['completed', 'skipped']
        regression_ok = results['regression'] and results['regression'].get('status') in ['completed', 'skipped']
        
        if yolo_ok and regression_ok:
            results['status'] = 'completed'
            results['message'] = 'Entrenamiento completo exitoso'
            logger.info("✓ Entrenamiento completo finalizado exitosamente")
        elif yolo_ok or regression_ok:
            results['status'] = 'partial'
            results['message'] = 'Entrenamiento completado parcialmente'
            logger.warning("Entrenamiento completado parcialmente")
        else:
            results['status'] = 'failed'
            results['message'] = 'Entrenamiento completo falló'
            logger.error("Entrenamiento completo falló")
        
        return results
        
    except Exception as e:
        logger.error(f"Error en entrenamiento completo: {e}", exc_info=True)
        # Inicializar results si no existe
        if 'results' not in locals():
            results = {
                'yolo': None,
                'regression': None,
                'status': 'failed'
            }
        return {
            'status': 'failed',
            'error': str(e),
            'yolo': results.get('yolo'),
            'regression': results.get('regression')
        }
