"""
Comando Django para entrenar todos los modelos: YOLO + Regresión.
ACTUALIZADO:
- Se eliminó la lógica de Celery para una ejecución directa y síncrona.
- Se agregaron los argumentos del "Flujo Mejorado" para el entrenamiento
  del modelo de regresión híbrido.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json
import time
import sys
from pathlib import Path

# Asegurar que el path del proyecto esté configurado para ml
project_root = Path(__file__).resolve().parents[4] # Sube 4 niveles (commands/management/training/backend)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

logger = None


class Command(BaseCommand):
    help = 'Entrena todos los modelos (YOLO + Regresión) de forma directa y síncrona.'
    
    def add_arguments(self, parser):
        # --- Argumentos YOLO ---
        parser.add_argument(
            '--yolo-dataset-size',
            type=int,
            default=150,
            help='Número de imágenes para dataset YOLO (default: 150)'
        )
        parser.add_argument(
            '--yolo-epochs',
            type=int,
            default=100,
            help='Número de épocas para YOLO (default: 100)'
        )
        parser.add_argument(
            '--yolo-batch-size',
            type=int,
            default=16,
            help='Tamaño de batch para YOLO (default: 16)'
        )
        parser.add_argument(
            '--yolo-model-name',
            type=str,
            default='yolov8s-seg',
            choices=['yolov8n-seg', 'yolov8s-seg', 'yolov8m-seg', 'yolov8l-seg', 'yolov8x-seg'],
            help='Modelo base YOLO (default: yolov8s-seg)'
        )
        
        # --- Argumentos Regresión (Flujo Mejorado) ---
        parser.add_argument(
            '--regression-epochs',
            type=int,
            default=150,
            help='Número de épocas para regresión (default: 150)'
        )
        parser.add_argument(
            '--regression-batch-size',
            type=int,
            default=16,
            help='Tamaño de batch para regresión (default: 16)'
        )
        parser.add_argument(
            '--regression-learning-rate',
            type=float,
            default=0.001,
            help='Learning rate para regresión (default: 0.001)'
        )
        parser.add_argument(
            '--regression-model-type',
            type=str,
            default='hybrid', # Default al nuevo modelo híbrido
            choices=['resnet18', 'convnext_tiny', 'hybrid'],
            help='Tipo de modelo de regresión (default: hybrid)'
        )
        parser.add_argument(
            '--regression-hybrid',
            action='store_true',
            default=True, # Default a True
            help='(Recomendado) Usar modelo híbrido (equivale a --regression-model-type hybrid)'
        )
        parser.add_argument(
            '--regression-use-pixel-features',
            action='store_true',
            default=True, # Default a True
            help='(Recomendado) Usar features de píxeles si pixel_calibration.json existe'
        )
        parser.add_argument(
            '--device',
            type=str,
            default='auto',
            choices=['cpu', 'cuda', 'auto'],
            help='Dispositivo para entrenamiento: cpu, cuda (GPU), o auto (detectar automáticamente). Default: auto'
        )

    
    def handle(self, *args, **options):
        """Maneja la ejecución del comando."""
        global logger
        from ml.utils.logs import get_ml_logger
        logger = get_ml_logger("cacaoscan.ml.commands")
        
        start_time = time.time()
        
        device = self._determine_device(options['device'])
        is_hybrid = self._determine_hybrid_mode(options)
        yolo_config = self._prepare_yolo_config(options, device)
        regression_config = self._prepare_regression_config(options, is_hybrid, device)
        
        self._print_startup_message(yolo_config, regression_config)
        
        try:
            results = {
                'yolo': None,
                'regression': None,
                'status': 'running'
            }
            
            results['yolo'] = self._train_yolo(yolo_config)
            results['regression'] = self._train_regression(regression_config)
            self._determine_final_status(results)
            self._display_results(results, start_time)
            
        except Exception as e:
            self._handle_fatal_error(e)

    def _determine_device(self, device_option: str) -> str:
        """Determina el dispositivo a usar para entrenamiento."""
        if device_option == 'auto':
            import torch
            if torch.cuda.is_available():
                device = 'cuda'
                self.stdout.write(self.style.SUCCESS(f"🚀 GPU detectada: {torch.cuda.get_device_name(0)}"))
            else:
                device = 'cpu'
                self.stdout.write(self.style.WARNING("🖥️  GPU no disponible, usando CPU"))
        else:
            device = device_option
            if device == 'cuda':
                import torch
                if not torch.cuda.is_available():
                    self.stdout.write(self.style.ERROR("⚠️  GPU solicitada pero no disponible, usando CPU"))
                    device = 'cpu'
                else:
                    self.stdout.write(self.style.SUCCESS(f"🚀 Usando GPU: {torch.cuda.get_device_name(0)}"))
            else:
                self.stdout.write(self.style.WARNING("🖥️  Usando CPU"))
        return device

    def _determine_hybrid_mode(self, options):
        """Determina si el modo es híbrido."""
        return options['regression_hybrid'] or options['regression_model_type'] == 'hybrid'

    def _prepare_yolo_config(self, options, device: str):
        """Prepara la configuración de YOLO."""
        return {
            'dataset_size': options['yolo_dataset_size'],
            'epochs': options['yolo_epochs'],
            'batch_size': options['yolo_batch_size'],
            'model_name': options['yolo_model_name'],
            'device': device
        }

    def _prepare_regression_config(self, options, is_hybrid: bool, device: str):
        """Prepara la configuración de regresión."""
        return {
            'epochs': options['regression_epochs'],
            'batch_size': options['regression_batch_size'],
            'learning_rate': options['regression_learning_rate'],
            'model_type': 'hybrid' if is_hybrid else options['regression_model_type'],
            'multi_head': is_hybrid,
            'hybrid': is_hybrid,
            'use_pixel_features': options['regression_use_pixel_features'] and is_hybrid,
            'img_size': 224,
            'early_stopping_patience': 25,
            'save_best_only': True,
            'device': device
        }

    def _print_startup_message(self, yolo_config, regression_config):
        """Imprime mensaje de inicio y configuraciones."""
        self.stdout.write(
            self.style.SUCCESS(
                "Iniciando entrenamiento completo: YOLO + Modelos de Regresión"
            )
        )
        self.stdout.write(f"Configuración YOLO: {json.dumps(yolo_config, indent=2)}")
        self.stdout.write(f"Configuración Regresión: {json.dumps(regression_config, indent=2)}")
        self.stdout.write("Ejecutando entrenamiento directamente (síncrono)...")
        self.stdout.write("Esto puede tomar varias horas. Por favor, sea paciente...")

    def _check_yolo_model_exists(self) -> bool:
        """Verifica si ya existe un modelo YOLO entrenado."""
        from ml.utils.paths import get_yolo_artifacts_dir
        from pathlib import Path
        
        artifacts_dir = get_yolo_artifacts_dir()
        models_dir = artifacts_dir / "models"
        
        if not models_dir.exists():
            return False
        
        # Buscar el mejor modelo en subdirectorios de entrenamiento
        # Los modelos se guardan en: models/cacao_seg_YYYYMMDD_HHMMSS/weights/best.pt
        for train_dir in models_dir.iterdir():
            if train_dir.is_dir():
                weights_dir = train_dir / "weights"
                best_model = weights_dir / "best.pt"
                if best_model.exists():
                    return True
        
        return False

    def _train_yolo(self, yolo_config):
        """Entrena el modelo YOLO."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("PASO 1/2: ENTRENANDO MODELO YOLO")
        self.stdout.write("="*60)
        
        # Verificar si ya existe un modelo YOLO entrenado
        if self._check_yolo_model_exists():
            self.stdout.write(
                self.style.WARNING("⚠ Modelo YOLO ya existe. Omitiendo entrenamiento.")
            )
            self.stdout.write("Si deseas reentrenar, elimina los modelos existentes en:")
            from ml.utils.paths import get_yolo_artifacts_dir
            yolo_dir = get_yolo_artifacts_dir() / "models"
            self.stdout.write(f"  {yolo_dir}")
            return {
                'status': 'skipped',
                'message': 'Modelo YOLO ya existe, entrenamiento omitido'
            }
        
        try:
            from ml.segmentation.train_yolo import train_cacao_yolo_model
            
            self.stdout.write(f"Configuración YOLO: {json.dumps(yolo_config, indent=2)}")
            self.stdout.write("Iniciando entrenamiento YOLO...")
            self.stdout.write("(Esto puede tomar 30-60 minutos)")
            
            yolo_result = train_cacao_yolo_model(
                dataset_size=yolo_config.get('dataset_size', 150),
                epochs=yolo_config.get('epochs', 100),
                batch_size=yolo_config.get('batch_size', 16),
                model_name=yolo_config.get('model_name', 'yolov8s-seg'),
                device=yolo_config.get('device', 'auto')
            )
            
            return self._process_yolo_result(yolo_result)
        except Exception as e:
            return self._handle_yolo_error(e)

    def _process_yolo_result(self, yolo_result):
        """Procesa el resultado del entrenamiento YOLO."""
        if yolo_result and yolo_result.get('status') == 'skipped':
            return yolo_result
        
        if yolo_result and yolo_result.get('success', False):
            self.stdout.write(
                self.style.SUCCESS("✓ Entrenamiento YOLO completado")
            )
            self.stdout.write(f"Modelo guardado en: {yolo_result.get('best_model_path')}")
            return {
                'status': 'completed',
                'message': 'Entrenamiento YOLO completado exitosamente',
                'best_model_path': yolo_result.get('best_model_path')
            }
        else:
            self.stdout.write(
                self.style.ERROR(f"✗ Entrenamiento YOLO falló: {yolo_result.get('error')}")
            )
            return {
                'status': 'failed',
                'message': 'El entrenamiento YOLO falló',
                'error': yolo_result.get('error', 'Error desconocido')
            }

    def _handle_yolo_error(self, e):
        """Maneja errores en el entrenamiento YOLO."""
        import traceback
        logger.error(f"Error en entrenamiento YOLO: {e}", exc_info=True)
        error_traceback = traceback.format_exc()
        
        self.stdout.write(self.style.ERROR(f"\n✗ ERROR EN ENTRENAMIENTO YOLO: {str(e)}"))
        self.stdout.write(error_traceback)
        
        return {
            'status': 'failed',
            'error': str(e),
            'traceback': error_traceback
        }

    def _check_regression_model_exists(self, is_hybrid: bool) -> bool:
        """Verifica si ya existe un modelo de regresión entrenado."""
        from ml.utils.paths import get_regressors_artifacts_dir
        from pathlib import Path
        
        artifacts_dir = get_regressors_artifacts_dir()
        
        if is_hybrid:
            model_file = artifacts_dir / "hybrid.pt"
        else:
            model_file = artifacts_dir / "multihead.pt"
        
        return model_file.exists()

    def _train_regression(self, regression_config):
        """Entrena los modelos de regresión."""
        self.stdout.write("\n" + "="*60)
        self.stdout.write("PASO 2/2: ENTRENANDO MODELOS DE REGRESIÓN")
        self.stdout.write("="*60)
        
        is_hybrid = regression_config.get('hybrid', False)
        
        # Verificar si ya existe un modelo de regresión entrenado
        if self._check_regression_model_exists(is_hybrid):
            model_name = "híbrido" if is_hybrid else "multi-head"
            self.stdout.write(
                self.style.WARNING(f"⚠ Modelo de regresión {model_name} ya existe. Omitiendo entrenamiento.")
            )
            self.stdout.write("Si deseas reentrenar, elimina el modelo existente:")
            from ml.utils.paths import get_regressors_artifacts_dir
            reg_dir = get_regressors_artifacts_dir()
            model_file = "hybrid.pt" if is_hybrid else "multihead.pt"
            self.stdout.write(f"  {reg_dir / model_file}")
            return {
                'status': 'skipped',
                'message': f'Modelo de regresión {model_name} ya existe, entrenamiento omitido'
            }
        
        try:
            from ml.pipeline.train_all import run_training_pipeline
            
            self.stdout.write(f"Configuración Regresión: {json.dumps(regression_config, indent=2)}")
            self.stdout.write("Iniciando entrenamiento de regresión...")
            self.stdout.write("(Esto puede tomar 1-3 horas)")
            
            regression_success = run_training_pipeline(
                epochs=regression_config.get('epochs', 150),
                batch_size=regression_config.get('batch_size', 16),
                learning_rate=regression_config.get('learning_rate', 0.001),
                multi_head=regression_config.get('multi_head', False),
                model_type=regression_config.get('model_type', 'resnet18'),
                img_size=regression_config.get('img_size', 224),
                early_stopping_patience=regression_config.get('early_stopping_patience', 25),
                save_best_only=regression_config.get('save_best_only', True),
                hybrid=regression_config.get('hybrid', False),
                use_pixel_features=regression_config.get('use_pixel_features', False),
                device=regression_config.get('device', 'auto')
            )
            
            return self._process_regression_result(regression_success)
        except Exception as e:
            return self._handle_regression_error(e)

    def _process_regression_result(self, regression_result):
        """Procesa el resultado del entrenamiento de regresión."""
        # Si es un diccionario con status skipped, retornarlo directamente
        if isinstance(regression_result, dict) and regression_result.get('status') == 'skipped':
            return regression_result
        
        # Compatibilidad con valor booleano
        if regression_result:
            self.stdout.write(
                self.style.SUCCESS("✓ Entrenamiento de regresión completado")
            )
            return {
                'status': 'completed',
                'message': 'Entrenamiento de regresión completado exitosamente'
            }
        else:
            self.stdout.write(
                self.style.ERROR("✗ Entrenamiento de regresión falló")
            )
            return {
                'status': 'failed',
                'message': 'El entrenamiento de regresión falló'
            }

    def _handle_regression_error(self, e):
        """Maneja errores en el entrenamiento de regresión."""
        import traceback
        logger.error(f"Error en entrenamiento de regresión: {e}", exc_info=True)
        error_traceback = traceback.format_exc()
        
        self.stdout.write(self.style.ERROR(f"\n✗ ERROR EN ENTRENAMIENTO DE REGRESIÓN: {str(e)}"))
        self.stdout.write(error_traceback)
        
        return {
            'status': 'failed',
            'error': str(e),
            'traceback': error_traceback
        }

    def _determine_final_status(self, results):
        """Determina el estado final del entrenamiento."""
        yolo_status = results['yolo'].get('status') if results['yolo'] else 'unknown'
        regression_status = results['regression'].get('status') if results['regression'] else 'unknown'
        
        yolo_ok = yolo_status in ('completed', 'skipped')
        regression_ok = regression_status in ('completed', 'skipped')
        
        if yolo_ok and regression_ok:
            if yolo_status == 'skipped' or regression_status == 'skipped':
                results['status'] = 'completed'
                results['message'] = 'Entrenamiento completo (algunos modelos ya existían)'
            else:
                results['status'] = 'completed'
                results['message'] = 'Entrenamiento completo exitoso'
        elif yolo_ok or regression_ok:
            results['status'] = 'partial'
            results['message'] = 'Entrenamiento completado parcialmente'
        else:
            results['status'] = 'failed'
            results['message'] = 'Entrenamiento completo falló'

    def _handle_fatal_error(self, e):
        """Maneja errores fatales en el entrenamiento."""
        import traceback
        logger.error(f"Error en entrenamiento completo: {e}", exc_info=True)
        error_traceback = traceback.format_exc()
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.ERROR("ERROR FATAL EN ENTRENAMIENTO"))
        self.stdout.write("="*60)
        self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
        self.stdout.write(error_traceback)
        self.stdout.write("="*60)
        
        raise CommandError(f"Error en entrenamiento: {e}\n\nTraceback completo:\n{error_traceback}")
    
    def _display_results(self, results: dict, start_time: float) -> None:
        """Muestra los resultados del entrenamiento."""
        end_time = time.time()
        total_time = end_time - start_time
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("RESULTADOS DEL ENTRENAMIENTO COMPLETO")
        self.stdout.write("="*60)
        
        self._display_yolo_results(results)
        self._display_regression_results(results)
        self._display_final_status(results)
        
        self.stdout.write(f"\nTiempo total: {total_time:.2f} segundos ({total_time/60:.2f} minutos)")
        self.stdout.write("="*60)

    def _display_yolo_results(self, results: dict) -> None:
        """Muestra los resultados del entrenamiento YOLO."""
        self.stdout.write("\n--- Entrenamiento YOLO ---")
        yolo_result = results.get('yolo')
        
        if not yolo_result:
            self.stdout.write(self.style.WARNING("⊘ YOLO: No se ejecutó"))
            return
        
        status = yolo_result.get('status', 'unknown')
        if status == 'completed':
            self._display_yolo_success(yolo_result)
        elif status == 'skipped':
            self._display_yolo_success(yolo_result)
        else:
            self._display_yolo_failure(yolo_result)

    def _display_yolo_success(self, yolo_result: dict) -> None:
        """Muestra el resultado exitoso de YOLO."""
        self.stdout.write(self.style.SUCCESS(f"✓ YOLO: {yolo_result.get('message', 'Completado')}"))
        best_model_path = yolo_result.get('best_model_path')
        if best_model_path:
            self.stdout.write(f"  Modelo guardado en: {best_model_path}")

    def _display_yolo_failure(self, yolo_result: dict) -> None:
        """Muestra el resultado fallido de YOLO."""
        self.stdout.write(self.style.ERROR(f"✗ YOLO: {yolo_result.get('message', 'Falló')}"))
        error = yolo_result.get('error')
        if error:
            self.stdout.write(self.style.ERROR(f"  Error: {error}"))

    def _display_regression_results(self, results: dict) -> None:
        """Muestra los resultados del entrenamiento de regresión."""
        self.stdout.write("\n--- Entrenamiento Regresión ---")
        regression_result = results.get('regression')
        
        if not regression_result:
            self.stdout.write(self.style.WARNING("⊘ Regresión: No se ejecutó"))
            return
        
        status = regression_result.get('status', 'unknown')
        if status == 'completed':
            self._display_regression_success(regression_result)
        elif status == 'skipped':
            self._display_regression_success(regression_result)
        else:
            self._display_regression_failure(regression_result)

    def _display_regression_success(self, regression_result: dict) -> None:
        """Muestra el resultado exitoso de regresión."""
        status = regression_result.get('status', 'unknown')
        if status == 'skipped':
            self.stdout.write(self.style.WARNING(f"⊘ Regresión: {regression_result.get('message', 'Omitido')}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✓ Regresión: {regression_result.get('message', 'Completado')}"))

    def _display_regression_failure(self, regression_result: dict) -> None:
        """Muestra el resultado fallido de regresión."""
        self.stdout.write(self.style.ERROR(f"✗ Regresión: {regression_result.get('message', 'Falló')}"))
        error = regression_result.get('error')
        if error:
            self.stdout.write(self.style.ERROR(f"  Error: {error}"))

    def _display_final_status(self, results: dict) -> None:
        """Muestra el estado final del entrenamiento."""
        self.stdout.write("\n--- Estado Final ---")
        final_status = results.get('status', 'unknown')
        
        if final_status == 'completed':
            self._display_completed_status(results)
        elif final_status == 'partial':
            self._display_partial_status(results)
        else:
            self._display_failed_status(results)

    def _display_completed_status(self, results: dict) -> None:
        """Muestra el estado de completado."""
        message = results.get('message', 'Entrenamiento completo exitoso')
        self.stdout.write(self.style.SUCCESS(f"✓ {message}"))

    def _display_partial_status(self, results: dict) -> None:
        """Muestra el estado parcial."""
        message = results.get('message', 'Entrenamiento completado parcialmente')
        self.stdout.write(self.style.WARNING(f"⚠ {message}"))

    def _display_failed_status(self, results: dict) -> None:
        """Muestra el estado fallido."""
        message = results.get('message', 'Entrenamiento falló')
        self.stdout.write(self.style.ERROR(f"✗ {message}"))
        error = results.get('error')
        if error:
            self.stdout.write(f"  Error: {error}")