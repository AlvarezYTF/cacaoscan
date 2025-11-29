""" 
Comando Django para entrenar modelos de regresión de cacao.
ACTUALIZADO:
- Añadido '--segmentation-backend' para controlar cómo se generan los crops.
"""
import time
import platform
import subprocess
import signal
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path
from typing import List, Optional, Dict, Union

# Asegurar que el path del proyecto esté configurado para ml
import sys
project_root = Path(__file__).resolve().parents[4] # Sube 4 niveles (commands/management/training/backend)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ml.pipeline.train_all import CacaoTrainingPipeline
from ml.utils.logs import get_ml_logger
from ml.utils.paths import get_raw_images_dir, get_regressors_artifacts_dir

logger = get_ml_logger("cacaoscan.ml.commands")


class Command(BaseCommand):
    help = 'Entrena modelos de regresión para dimensiones y peso de granos de cacao'
    
    def add_arguments(self, parser):
        # --- Argumentos del Modelo (Mejorados) ---
        parser.add_argument(
            '--multihead',
            action='store_true',
            help='Usar modelo multi-head (un solo modelo para todos los targets)'
        )
        parser.add_argument(
            '--model-type',
            type=str,
            default='resnet18',
            choices=['resnet18', 'convnext_tiny', 'hybrid'],
            help='Tipo de modelo a usar: resnet18, convnext_tiny, o hybrid (fusiona ResNet18 + ConvNeXt + Píxeles)'
        )
        parser.add_argument(
            '--hybrid',
            action='store_true',
            help='(Recomendado) Usar modelo híbrido que fusiona CNN + Features de Píxeles (equivale a --model-type hybrid)'
        )
        parser.add_argument(
            '--hybrid-v2',
            action='store_true',
            help='Usar nuevo modelo híbrido mejorado v2 con RobustScaler, log-transform para peso, y pixel features mejorados'
        )
        parser.add_argument(
            '--use-pixel-features',
            action='store_true',
            default=True,
            help='(Recomendado) Usar features de píxeles del dataset si pixel_calibration.json existe (default: True)'
        )
        parser.add_argument(
            '--use-mixed-precision',
            action='store_true',
            default=False,
            help='Usar mixed precision training (requiere GPU NVIDIA)'
        )
        
        # --- Argumentos de Entrenamiento ---
        parser.add_argument(
            '--epochs',
            type=int,
            default=50,
            help='Número de épocas de entrenamiento (default: 50)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=32,
            help='Tamaño de batch (default: 32)'
        )
        parser.add_argument(
            '--img-size',
            type=int,
            default=224,
            help='Tamaño de imagen de entrada (default: 224)'
        )
        parser.add_argument(
            '--learning-rate',
            type=float,
            default=1e-4,  # Aumentado de 1e-5 a 1e-4 para mejor aprendizaje
            help='Learning rate (default: 1e-4, optimizado para mejor convergencia)'
        )
        parser.add_argument(
            '--loss-type',
            type=str,
            default='smooth_l1',
            choices=['mse', 'smooth_l1', 'huber'],
            help='Tipo de loss function: mse, smooth_l1 (recomendado), o huber (default: smooth_l1)'
        )
        parser.add_argument(
            '--scheduler-type',
            type=str,
            default='cosine_warmup',
            choices=['reduce_on_plateau', 'cosine', 'cosine_warmup', 'onecycle'],
            help='Tipo de scheduler: reduce_on_plateau, cosine, cosine_warmup (recomendado), o onecycle (default: cosine_warmup)'
        )
        parser.add_argument(
            '--warmup-epochs',
            type=int,
            default=None,
            help='Número de épocas de warmup para cosine_warmup scheduler (default: 5, o 10 si se usa --hybrid --use-pixel-features)'
        )
        parser.add_argument(
            '--max-grad-norm',
            type=float,
            default=1.0,
            help='Máxima norma de gradiente para clipping (default: 1.0)'
        )
        
        # --- Argumentos de Targets ---
        parser.add_argument(
            '--targets',
            type=str,
            default='all',
            help='Targets a entrenar: alto,ancho,grosor,peso o "all" (default: all)'
        )
        
        # --- Argumentos de Configuración ---
        parser.add_argument(
            '--resume',
            action='store_true',
            help='Resumir entrenamiento desde checkpoint (no implementado aún)'
        )
        parser.add_argument(
            '--num-workers',
            type=int,
            default=2,
            help='Número de workers para data loading (default: 2). Usar 0 en Windows si hay problemas.'
        )
        parser.add_argument(
            '--early-stopping-patience',
            type=int,
            default=15,
            help='Paciencia para early stopping (default: 15, aumentado para entrenamiento más robusto)'
        )
        parser.add_argument(
            '--dropout-rate',
            type=float,
            default=0.25,
            help='Tasa de dropout (default: 0.25, aumentado para mejor regularización)'
        )
        parser.add_argument(
            '--use-raw-images',
            action='store_true',
            help='Usar únicamente las imágenes BMP originales (sin generar nuevos crops).'
        )
        
        # --- INICIO DE CORRECCIÓN ---
        parser.add_argument(
            '--segmentation-backend',
            type=str,
            default='auto',
            choices=['auto', 'opencv'],
            help="Backend para generar crops: 'auto' (YOLO/rembg) o 'opencv' (fallback rembg/opencv)"
        )
        # --- FIN DE CORRECCIÓN ---
        
        # --- Argumentos de Validación y Pruebas ---
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Solo validar datos sin entrenar modelos'
        )
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Modo de prueba con configuración reducida (epochs=5, batch=16)'
        )
        
        # Nuevo argumento para entrenamiento por dimensión separada
        parser.add_argument(
            '--train-separate-dimensions',
            action='store_true',
            help='Entrenar cada dimensión (alto, ancho, grosor, peso) por separado usando pixel_calibration.json'
        )
    
    def handle(self, *args, **options):
        """Maneja la ejecución del comando."""
        start_time = time.time()
        
        config = self._create_config(options)
        
        self.stdout.write(
            self.style.SUCCESS(
                "Iniciando entrenamiento de modelos de cacao"
            )
        )
        
        try:
            self._validate_config(config)
            self._display_config(config)
            
            if options['validate_only']:
                self._validate_data_only()
                return
            
            # Use new hybrid-v2 pipeline if requested
            if options.get('hybrid_v2', False):
                from ml.pipeline.hybrid_v2_training import train_hybrid_v2
                results = train_hybrid_v2(config)
                self._display_results_v2(results, start_time)
            else:
                pipeline = CacaoTrainingPipeline(config)
                results = pipeline.run_pipeline()
                self._display_results(results, start_time)
            
        except Exception as e:
            import traceback
            logger.error(f"Error fatal durante el entrenamiento: {e}\n{traceback.format_exc()}")
            raise CommandError(f"Error durante el entrenamiento: {e}")
    
    def _create_config(self, options: dict) -> dict:
        """Crea la configuración del entrenamiento."""
        
        use_hybrid = options.get('hybrid', False) or options.get('model_type') == 'hybrid'
        use_hybrid_v2 = options.get('hybrid_v2', False)
        train_separate_dimensions = options.get('train_separate_dimensions', False)
        use_pixel_features = options.get('use_pixel_features', True)
        
        # Detectar si se está usando la configuración optimizada (--hybrid --use-pixel-features)
        is_optimized_hybrid = use_hybrid and use_pixel_features and not use_hybrid_v2
        
        is_windows = platform.system() == 'Windows'
        num_workers = options['num_workers']
        if is_windows and num_workers > 0:
            logger.warning("Windows detectado: Se usará --num-workers 0 para evitar problemas de multiprocessing.")
            num_workers = 0

        # En contenedores Docker es frecuente quedarse sin memoria compartida (shm)
        # al usar múltiples workers del DataLoader. Forzamos 0 workers salvo que
        # el usuario lo haya fijado explícitamente en 0.
        if num_workers != 0:
            logger.warning(
                "Forzando num_workers=0 para evitar errores de shared memory en DataLoader."
            )
            num_workers = 0

        # Si se usa --hybrid --use-pixel-features, aplicar configuración optimizada automáticamente
        if is_optimized_hybrid:
            # Aplicar valores optimizados solo si el usuario no los especificó explícitamente
            optimized_epochs = options['epochs'] if options['epochs'] != 50 else 100
            optimized_lr = options['learning_rate'] if abs(options['learning_rate'] - 1e-4) >= 1e-6 else 5e-5
            optimized_patience = options['early_stopping_patience'] if options['early_stopping_patience'] != 15 else 25
            optimized_dropout = options['dropout_rate'] if abs(options['dropout_rate'] - 0.25) >= 1e-6 else 0.3
            optimized_loss = options.get('loss_type', 'huber') if 'loss_type' in options else 'huber'
            optimized_scheduler = options.get('scheduler_type', 'cosine_warmup') if 'scheduler_type' in options else 'cosine_warmup'
            
            # Mostrar mensaje informativo
            if optimized_epochs == 100 or abs(optimized_lr - 5e-5) < 1e-6 or optimized_patience == 25:
                self.stdout.write(
                    self.style.SUCCESS(
                        "✅ Configuración optimizada detectada (--hybrid --use-pixel-features)\n"
                        "   Aplicando valores optimizados automáticamente:\n"
                        f"   - Épocas: {optimized_epochs}\n"
                        f"   - Learning Rate: {optimized_lr}\n"
                        f"   - Early Stopping Patience: {optimized_patience}\n"
                        f"   - Dropout: {optimized_dropout}\n"
                        f"   - Loss: {optimized_loss}\n"
                        f"   - Scheduler: {optimized_scheduler}"
                    )
                )
        else:
            # Valores normales si no es configuración optimizada
            optimized_epochs = options['epochs']
            optimized_lr = options['learning_rate']
            optimized_patience = options['early_stopping_patience']
            optimized_dropout = options['dropout_rate']
            optimized_loss = options.get('loss_type', 'smooth_l1')
            optimized_scheduler = options.get('scheduler_type', 'cosine_warmup')

        config = {
            'multi_head': options['multihead'] or use_hybrid or use_hybrid_v2,
            'model_type': 'hybrid' if (use_hybrid or use_hybrid_v2) else options['model_type'],
            'hybrid': use_hybrid,
            'hybrid_v2': use_hybrid_v2,
            'use_pixel_features': use_pixel_features and (use_hybrid or use_hybrid_v2 or train_separate_dimensions),
            'train_separate_dimensions': train_separate_dimensions,  # Nuevo flag
            'epochs': optimized_epochs,
            'batch_size': options['batch_size'],
            'img_size': options['img_size'],
            'learning_rate': optimized_lr,
            'num_workers': num_workers,
            'early_stopping_patience': optimized_patience,
            'dropout_rate': optimized_dropout,
            'use_raw_images': options.get('use_raw_images', False),
            'segmentation_backend': options.get('segmentation_backend', 'auto'), # <-- AÑADIR
            'pretrained': True,
            'weight_decay': 1e-4,
            'min_lr': 1e-7,  # Reducido para mejor fine-tuning
            'loss_type': optimized_loss,
            'scheduler_type': optimized_scheduler,
            'max_grad_norm': options.get('max_grad_norm', 1.0),
            'use_mixed_precision': options.get('use_mixed_precision', False),
            'targets': self._parse_targets(options['targets']),
            'warmup_epochs': self._get_warmup_epochs(options, is_optimized_hybrid)
        }
        
        if options['test_mode']:
            config.update({
                'epochs': min(config['epochs'], 5),
                'batch_size': min(config['batch_size'], 16),
                'early_stopping_patience': 3
            })
            self.stdout.write(
                self.style.WARNING("Modo de prueba activado - configuración reducida")
            )
        
        return config
    
    def _get_warmup_epochs(self, options: Dict, is_optimized_hybrid: bool) -> int:
        """Get warmup epochs from options or use default based on model type."""
        warmup_epochs = options.get('warmup_epochs')
        if warmup_epochs is not None:
            return warmup_epochs
        
        return 10 if is_optimized_hybrid else 5
    
    def _parse_targets(self, targets_str: str) -> List[str]:
        """Parsea la lista de targets."""
        if targets_str.lower() == 'all':
            return ['alto', 'ancho', 'grosor', 'peso']
        
        targets = [t.strip().lower() for t in targets_str.split(',')]
        valid_targets = ['alto', 'ancho', 'grosor', 'peso']
        
        for target in targets:
            if target not in valid_targets:
                raise ValueError(f"Target inválido: {target}. Targets válidos: {valid_targets}")
        
        return targets
    
    def _validate_config(self, config: dict) -> None:
        """Valida la configuración."""
        raw_dir = get_raw_images_dir()
        if not raw_dir.exists():
            raise CommandError(f"Directorio de imágenes raw no encontrado: {raw_dir}")
        
        raw_files = list(raw_dir.glob("*.bmp"))
        if len(raw_files) < 10:
            raise CommandError(
                f"Muy pocas imágenes raw disponibles: {len(raw_files)}. "
                "Se necesitan al menos 10 para entrenamiento."
            )
        
        from ml.data.dataset_loader import CacaoDatasetLoader
        try:
            loader = CacaoDatasetLoader()
            df = loader.load_dataset()
            if len(df) < 10:
                raise CommandError(
                    f"Muy pocos registros en el CSV: {len(df)}. "
                    "Se necesitan al menos 10 para entrenamiento."
                )
        except Exception as e:
            raise CommandError(f"Error cargando dataset: {e}")

        try:
            loader = CacaoDatasetLoader()
            valid_records = loader.get_valid_records()
            if len(valid_records) < 10:
                raise CommandError(
                    f"Muy pocos registros válidos (CSV + Imagen): {len(valid_records)}. "
                    "Se necesitan al menos 10 para entrenamiento."
                )
            logger.info(f"✅ {len(valid_records)} registros válidos encontrados. Los crops se generarán automáticamente si faltan.")
        except Exception as e:
            raise CommandError(f"Error validando registros: {e}")
        
        if config['model_type'] == 'convnext_tiny' or config['hybrid']:
            try:
                import timm
            except ImportError:
                raise CommandError(
                    "timm es requerido para ConvNeXt o Modelos Híbridos. Instalar con: pip install timm"
                )
        
        if config['epochs'] < 1:
            raise CommandError("Número de épocas debe ser >= 1")
        if config['batch_size'] < 1:
            raise CommandError("Tamaño de batch debe ser >= 1")
        if config['learning_rate'] <= 0:
            raise CommandError("Learning rate debe ser > 0")
    
    def _display_config(self, config: dict) -> None:
        """Muestra la configuración del entrenamiento."""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("CONFIGURACIÓN DE ENTRENAMIENTO")
        self.stdout.write("="*50)
        
        self.stdout.write(f"Modelo: {config['model_type']}")
        if config.get('hybrid'):
            self.stdout.write(self.style.SUCCESS("  → Modelo HÍBRIDO: ResNet18 + ConvNeXt + Features de Píxeles"))
        self.stdout.write(f"Multi-head: {config['multi_head']}")
        self.stdout.write(f"Usar features de píxeles: {config.get('use_pixel_features', False)}")
        self.stdout.write(f"Targets: {config['targets']}")
        self.stdout.write(f"Épocas: {config['epochs']}")
        self.stdout.write(f"Batch size: {config['batch_size']}")
        self.stdout.write(f"Tamaño de imagen: {config['img_size']}")
        self.stdout.write(f"Learning rate: {config['learning_rate']}")
        self.stdout.write(f"Dropout rate: {config['dropout_rate']}")
        self.stdout.write(f"Early stopping patience: {config['early_stopping_patience']}")
        self.stdout.write(f"Workers: {config['num_workers']}")
        self.stdout.write(f"Usar imágenes raw sin crops: {config.get('use_raw_images', False)}")
        self.stdout.write(f"Backend de segmentación: {config.get('segmentation_backend', 'auto')}") # <-- AÑADIR
        self.stdout.write(f"Entrenar por dimensiones separadas: {config.get('train_separate_dimensions', False)}") # <-- AÑADIR
        
        raw_dir = get_raw_images_dir()
        raw_files = list(raw_dir.glob("*.bmp"))
        self.stdout.write(f"Imágenes raw disponibles: {len(raw_files)}")
        
        self.stdout.write("="*50)
    
    def _validate_data_only(self) -> None:
        """Solo valida los datos sin entrenar."""
        self.stdout.write("Validando datos...")
        
        try:
            from ml.data.dataset_loader import CacaoDatasetLoader
            
            loader = CacaoDatasetLoader()
            valid_records = loader.get_valid_records()
            
            if not valid_records:
                raise CommandError("No se encontraron registros válidos")
            
            crops_available = 0
            for record in valid_records:
                crop_path = Path(record['crop_image_path'])
                if not crop_path.is_absolute():
                    crop_path = Path(settings.MEDIA_ROOT) / crop_path
                if crop_path.exists():
                    crops_available += 1
            
            self.stdout.write(f"Registros válidos (CSV + Imagen raw): {len(valid_records)}")
            self.stdout.write(f"Crops ya generados: {crops_available}")
            self.stdout.write(f"Crops a generar: {len(valid_records) - crops_available}")
            
            stats = loader.get_dataset_stats()
            self.stdout.write("\nEstadísticas del dataset:")
            for target in ['alto', 'ancho', 'grosor', 'peso']:
                if target in stats.get('dimensions_stats', {}):
                    target_stats = stats['dimensions_stats'][target]
                    self.stdout.write(
                        f"  {target.upper()}: "
                        f"min={target_stats['min']:.2f}, "
                        f"max={target_stats['max']:.2f}, "
                        f"mean={target_stats['mean']:.2f}"
                    )
            
            self.stdout.write(
                self.style.SUCCESS("Validación de datos completada exitosamente")
            )
            
        except Exception as e:
            raise CommandError(f"Error validando datos: {e}")
    
    def _display_results(self, results: dict, start_time: float) -> None:
        """Muestra los resultados del entrenamiento."""
        total_time = time.time() - start_time
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write("RESULTADOS DEL ENTRENAMIENTO")
        self.stdout.write("="*50)
        
        self.stdout.write(f"Tiempo total: {total_time:.2f} segundos")
        
        if 'evaluation_results' in results:
            eval_results = results['evaluation_results']
            self.stdout.write("\nMétricas de evaluación:")
            
            if (results['config']['multi_head'] or results['config']['hybrid']) and 'multihead' in eval_results:
                multihead_results = eval_results['multihead']
                for target in ['alto', 'ancho', 'grosor', 'peso']:
                    if target in multihead_results:
                        metrics = multihead_results[target]
                        self.stdout.write(
                            f"  {target.upper()}: "
                            f"MAE={metrics['mae']:.4f}, "
                            f"RMSE={metrics['rmse']:.4f}, "
                            f"R²={metrics['r2']:.4f}"
                        )
            else:
                for target in ['alto', 'ancho', 'grosor', 'peso']:
                    if target in eval_results:
                        metrics = eval_results[target]
                        self.stdout.write(
                            f"  {target.upper()}: "
                            f"MAE={metrics['mae']:.4f}, "
                            f"RMSE={metrics['rmse']:.4f}, "
                            f"R²={metrics['r2']:.4f}"
                        )
        
        artifacts_dir = get_regressors_artifacts_dir()
        self.stdout.write(f"\nModelos guardados en: {artifacts_dir}")
        
        if artifacts_dir.exists():
            model_files = list(artifacts_dir.glob("*.pt"))
            scaler_files = list(artifacts_dir.glob("*.pkl"))
            
            self.stdout.write(f"Archivos de modelo: {len(model_files)}")
            self.stdout.write(f"Archivos de escaladores: {len(scaler_files)}")
        
        self.stdout.write("="*50)
        self.stdout.write(
            self.style.SUCCESS("¡Entrenamiento completado exitosamente!")
        )
    
    def _display_results_v2(self, results: dict, start_time: float) -> None:
        """Muestra los resultados del entrenamiento v2."""
        total_time = time.time() - start_time
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write("RESULTADOS DEL ENTRENAMIENTO HÍBRIDO V2")
        self.stdout.write("="*50)
        
        self.stdout.write(f"Tiempo total: {total_time:.2f} segundos")
        self.stdout.write(f"Mejor epoch: {results.get('best_epoch', 'N/A')}")
        self.stdout.write(f"Mejor val_loss: {results.get('best_val_loss', 'N/A'):.4f}")
        self.stdout.write(f"Test loss: {results.get('test_loss', 'N/A'):.4f}")
        
        if 'test_metrics' in results:
            self.stdout.write("\nMétricas de test (desnormalizadas):")
            for target in ['alto', 'ancho', 'grosor', 'peso']:
                if target in results['test_metrics']:
                    metrics = results['test_metrics'][target]
                    self.stdout.write(
                        f"  {target.upper()}: "
                        f"R²={metrics['r2']:.4f}, "
                        f"MAE={metrics['mae']:.4f}, "
                        f"RMSE={metrics['rmse']:.4f}"
                    )
        
        artifacts_dir = get_regressors_artifacts_dir()
        self.stdout.write(f"\nModelos guardados en: {artifacts_dir}")
        self.stdout.write(f"Modelo final: {results.get('model_path', 'N/A')}")
        
        self.stdout.write("="*50)
        self.stdout.write(
            self.style.SUCCESS("¡Entrenamiento híbrido v2 completado exitosamente!")
        )
    
    def _run_with_celery(self, config: dict, options: dict) -> None:
        """Ejecuta el entrenamiento usando Celery, iniciando servicios si es necesario."""
        try:
            from api.tasks import auto_train_model_task
            from celery import current_app
            import time as time_module
            
            self.stdout.write(
                self.style.SUCCESS(
                    "Iniciando entrenamiento con Celery (asíncrono)..."
                )
            )
            
            # Verificar y configurar Redis/Celery
            celery_process = None
            redis_started = False
            
            # Verificar si Redis está disponible
            try:
                if not self._check_redis_available():
                    self.stdout.write(
                        self.style.WARNING(
                            "Redis no está disponible. Intentando iniciarlo..."
                        )
                    )
                    redis_started = self._start_redis()
                    if not redis_started:
                        self.stdout.write(
                            self.style.WARNING(
                                "\n[ERROR] No se pudo iniciar Redis automáticamente."
                            )
                        )
                        self.stdout.write(
                            self.style.WARNING(
                                "Ejecutando entrenamiento directo (sin Celery)..."
                            )
                        )
                        # Cambiar a modo directo
                        pipeline = CacaoTrainingPipeline(config)
                        results = pipeline.run_pipeline(config['multi_head'])
                        self._display_results(results, time_module.time())
                        return
                    
                    # Esperar a que Redis esté listo
                    self.stdout.write("Esperando a que Redis esté listo...")
                    time_module.sleep(2)
                    
                    # Verificar nuevamente que Redis está disponible
                    max_retries = 10
                    for _ in range(max_retries):
                        if self._check_redis_available():
                            self.stdout.write(
                                self.style.SUCCESS("Redis está disponible")
                            )
                            break
                        time_module.sleep(1)
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                "\n[ERROR] Redis no está disponible después de intentar iniciarlo."
                            )
                        )
                        self.stdout.write(
                            self.style.WARNING(
                                "Ejecutando entrenamiento directo (sin Celery)..."
                            )
                        )
                        # Cambiar a modo directo
                        pipeline = CacaoTrainingPipeline(config)
                        results = pipeline.run_pipeline(config['multi_head'])
                        self._display_results(results, time_module.time())
                        return
                
                # Verificar si el worker de Celery está corriendo
                if not self._check_celery_worker_running():
                    self.stdout.write(
                        self.style.WARNING(
                            "Worker de Celery no está corriendo. Iniciándolo..."
                        )
                    )
                    celery_process = self._start_celery_worker()
                    if not celery_process:
                        raise CommandError(
                            "No se pudo iniciar el worker de Celery."
                        )
                    # Esperar a que el worker esté listo
                    self.stdout.write("Esperando a que el worker de Celery esté listo...")
                    import time as time_module
                    time_module.sleep(5)  # Dar más tiempo al worker para iniciar
                    
                    # Verificar que el worker está corriendo
                    max_retries = 10
                    for _ in range(max_retries):
                        if self._check_celery_worker_running():
                            self.stdout.write(
                                self.style.SUCCESS("Worker de Celery está corriendo")
                            )
                            break
                        time_module.sleep(1)
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                "Worker de Celery iniciado pero aún no responde. "
                                "Continuando..."
                            )
                        )
                
                # Preparar configuración para Celery
                celery_config = {
                    'epochs': config.get('epochs', 50),
                    'batch_size': config.get('batch_size', 32),
                    'learning_rate': config.get('learning_rate', 1e-5),  # REDUCIDO de 1e-4 a 1e-5
                    'multi_head': config.get('multi_head', False),
                    'model_type': config.get('model_type', 'resnet18'),
                    'img_size': config.get('img_size', 224),
                    'early_stopping_patience': config.get('early_stopping_patience', 10),
                    'save_best_only': True
                }
                
                # Verificar que Redis está disponible antes de enviar tarea
                if not self._check_redis_available():
                    self.stdout.write(
                        self.style.WARNING(
                            "\n[ERROR] Redis no está disponible. Cambiando a entrenamiento directo..."
                        )
                    )
                    # Cambiar a modo directo
                    pipeline = CacaoTrainingPipeline(config)
                    results = pipeline.run_pipeline(config['multi_head'])
                    self._display_results(results, time_module.time())
                    return
                
                # Enviar tarea a Celery con configuración personalizada
                task_result = auto_train_model_task.delay(force=False, config=celery_config)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Tarea enviada a Celery. Task ID: {task_result.id}"
                    )
                )
                self.stdout.write(
                    "Puedes monitorear el progreso con: "
                    f"celery -A cacaoscan inspect task {task_result.id}"
                )
                self.stdout.write(
                    "\nEsperando resultado... (presiona Ctrl+C para salir sin esperar)"
                )
                
                # Esperar resultado (bloqueante)
                try:
                    result = task_result.get(timeout=None)
                    
                    if result.get('status') == 'completed':
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Entrenamiento completado: {result.get('message', 'OK')}"
                            )
                        )
                    elif result.get('status') == 'skipped':
                        self.stdout.write(
                            self.style.WARNING(
                                f"Entrenamiento omitido: {result.get('message', '')}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Entrenamiento falló: {result.get('message', 'Error desconocido')}"
                            )
                        )
                        if 'error' in result:
                            self.stdout.write(f"Error: {result['error']}")
                            
                except KeyboardInterrupt:
                    self.stdout.write(
                        self.style.WARNING(
                            "\nSaliendo... La tarea seguirá ejecutándose en Celery."
                        )
                    )
                    self.stdout.write(
                        "Para monitorear: celery -A cacaoscan inspect active"
                    )
                except Exception as e:
                    raise CommandError(f"Error esperando resultado de Celery: {e}")
                finally:
                    # Limpiar procesos iniciados si es necesario
                    if celery_process:
                        self.stdout.write(
                            self.style.WARNING(
                                "\nCerrando worker de Celery iniciado automáticamente..."
                            )
                        )
                        self._stop_celery_worker(celery_process)
            except CommandError:
                raise
            except Exception as e:
                raise CommandError(f"Error configurando Celery: {e}")
                    
        except ImportError:
            raise CommandError(
                "Celery no está disponible. Instala con: pip install celery"
            )
        except Exception as e:
            raise CommandError(f"Error ejecutando con Celery: {e}")
    
    def _check_redis_available(self) -> bool:
        """Verifica si Redis está disponible."""
        try:
            from django.core.cache import cache
            cache.set('test_key', 'test_value', 1)
            cache.get('test_key')
            return True
        except Exception:
            try:
                import redis
                r = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=1)
                r.ping()
                return True
            except Exception:
                return False
    
    def _start_redis(self) -> bool:
        """Intenta iniciar Redis."""
        try:
            # Intentar usar Docker si está disponible
            try:
                # Verificar si el contenedor ya existe
                check_result = subprocess.run(
                    ['docker', 'ps', '-a', '--filter', 'name=redis-cacaoscan', '--format', '{{.Names}}'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if check_result.returncode == 0 and 'redis-cacaoscan' in check_result.stdout:
                    # Contenedor existe, intentar iniciarlo
                    self.stdout.write("Iniciando contenedor Redis existente...")
                    subprocess.run(
                        ['docker', 'start', 'redis-cacaoscan'],
                        capture_output=True,
                        timeout=5
                    )
                    import time as time_module
                    time_module.sleep(2)
                    if self._check_redis_available():
                        self.stdout.write(
                            self.style.SUCCESS("Redis iniciado desde contenedor existente")
                        )
                        return True
                
                # Intentar crear nuevo contenedor
                result = subprocess.run(
                    ['docker', 'ps'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    # Docker está disponible, intentar iniciar Redis en Docker
                    self.stdout.write("Intentando iniciar Redis con Docker...")
                    subprocess.run(
                        ['docker', 'run', '-d', '-p', '6379:6379', '--name', 'redis-cacaoscan', 'redis'],
                        capture_output=True,
                        timeout=10
                    )
                    import time as time_module
                    time_module.sleep(3)  # Esperar más tiempo
                    if self._check_redis_available():
                        self.stdout.write(
                            self.style.SUCCESS("Redis iniciado con Docker")
                        )
                        return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Intentar iniciar redis-server directamente
            if platform.system() == 'Windows':
                redis_paths = [
                    'redis-server.exe',
                    r'C:\Program Files\Redis\redis-server.exe',
                    r'C:\redis\redis-server.exe',
                ]
                # Intentar como servicio de Windows
                try:
                    result = subprocess.run(
                        ['sc', 'query', 'Redis'],
                        capture_output=True,
                        timeout=2
                    )
                    if result.returncode == 0:
                        # Servicio existe, intentar iniciarlo
                        self.stdout.write("Intentando iniciar servicio Redis de Windows...")
                        subprocess.run(
                            ['sc', 'start', 'Redis'],
                            capture_output=True,
                            timeout=5
                        )
                        import time as time_module
                        time_module.sleep(2)
                        if self._check_redis_available():
                            self.stdout.write(
                                self.style.SUCCESS("Redis iniciado como servicio de Windows")
                            )
                            return True
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass
            else:
                redis_paths = ['redis-server', '/usr/local/bin/redis-server', '/usr/bin/redis-server']
            
            for redis_path in redis_paths:
                try:
                    # En Windows, ejecutar en segundo plano sin mostrar ventana
                    if platform.system() == 'Windows':
                        process = subprocess.Popen(
                            [redis_path],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                    else:
                        subprocess.Popen(
                            [redis_path],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            start_new_session=True
                        )
                    import time as time_module
                    time_module.sleep(3)  # Esperar más tiempo
                    if self._check_redis_available():
                        self.stdout.write(
                            self.style.SUCCESS(f"Redis iniciado: {redis_path}")
                        )
                        return True
                except (FileNotFoundError, OSError):
                    continue
            
            return False
        except (FileNotFoundError, OSError) as e:
            self.stdout.write(
                self.style.ERROR(f"No se pudo iniciar Redis: {e}")
            )
            return False
    
    def _check_celery_worker_running(self) -> bool:
        """Verifica si hay un worker de Celery corriendo."""
        try:
            from celery import current_app
            inspect = current_app.control.inspect()
            active = inspect.active()
            return active is not None and len(active) > 0
        except Exception:
            return False
    
    def _start_celery_worker(self) -> Optional[subprocess.Popen]:
        """Inicia un worker de Celery en segundo plano."""
        try:
            celery_cmd = [
                sys.executable,
                '-m', 'celery',
                '-A', 'cacaoscan',
                'worker',
                '--loglevel=info'
            ]
            
            if platform.system() == 'Windows':
                process = subprocess.Popen(
                    celery_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                subprocess.Popen(
                    celery_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Worker de Celery iniciado (PID: {process.pid})"
                )
            )
            return process
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error iniciando worker de Celery: {e}")
            )
            return None
    
    def _check_models_exist(self) -> bool:
        """Verifica si existen modelos entrenados."""
        try:
            from ml.utils.paths import get_regressors_artifacts_dir
            
            artifacts_dir = get_regressors_artifacts_dir()
            targets = ['alto', 'ancho', 'grosor', 'peso']
            
            # Verificar que todos los modelos y escaladores existan
            all_models_exist = all(
                (artifacts_dir / f"{target}.pt").exists()
                for target in targets
            )
            
            all_scalers_exist = all(
                (artifacts_dir / f"{target}_scaler.pkl").exists()
                for target in targets
            )
            
            if all_models_exist and all_scalers_exist:
                # Verificar que los archivos no estén vacíos
                all_valid = all(
                    (artifacts_dir / f"{target}.pt").stat().st_size > 0 and
                    (artifacts_dir / f"{target}_scaler.pkl").stat().st_size > 0
                    for target in targets
                )
                return all_valid
            
            return False
        except Exception as e:
            logger.debug(f"Error verificando modelos: {e}")
            return False
    
    def _stop_celery_worker(self, process: subprocess.Popen) -> None:
        """Detiene el worker de Celery iniciado automáticamente."""
        try:
            if platform.system() == 'Windows':
                process.terminate()
            else:
                import os
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
            
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Error deteniendo worker: {e}")
            )

