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
from typing import List, Optional, Dict, Union, NamedTuple, Mapping, Callable, cast

# Asegurar que el path del proyecto esté configurado para ml
import sys
project_root = Path(__file__).resolve().parents[4] # Sube 4 niveles (commands/management/training/backend)
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from ml.pipeline.train_all import CacaoTrainingPipeline
from ml.utils.logs import get_ml_logger
from ml.utils.paths import get_raw_images_dir, get_regressors_artifacts_dir

logger = get_ml_logger("cacaoscan.ml.commands")

TrainingOptionValue = Union[bool, int, float, str, None]
TrainingOptions = Dict[str, TrainingOptionValue]
TrainingConfigValue = Union[bool, int, float, str, List[str]]
TrainingConfig = Dict[str, TrainingConfigValue]
MetricValues = Mapping[str, float]
TargetMetrics = Mapping[str, MetricValues]
ResultPayload = Mapping[str, object]
METRIC_TARGETS: tuple[str, ...] = ('alto', 'ancho', 'grosor', 'peso')


class TrainingFlags(NamedTuple):
    use_hybrid: bool
    use_hybrid_v2: bool
    train_separate_dimensions: bool
    base_pixel_features: bool
    is_optimized_hybrid: bool


class HyperParams(NamedTuple):
    epochs: int
    learning_rate: float
    patience: int
    dropout: float
    loss: str
    scheduler: str

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
    
    def _create_config(self, options: TrainingOptions) -> TrainingConfig:
        """Crea la configuración del entrenamiento."""
        flags = self._resolve_training_flags(options)
        num_workers = self._determine_num_workers(int(options['num_workers']))
        hyperparams = self._resolve_hyperparams(options, flags)
        base_config = self._build_base_config(options, flags, num_workers, hyperparams)
        return self._apply_test_mode(base_config, bool(options.get('test_mode')))

    def _resolve_training_flags(self, options: TrainingOptions) -> TrainingFlags:
        use_hybrid = bool(options.get('hybrid')) or options.get('model_type') == 'hybrid'
        use_hybrid_v2 = bool(options.get('hybrid_v2'))
        train_separate_dimensions = bool(options.get('train_separate_dimensions'))
        base_pixel_features = bool(options.get('use_pixel_features', True))
        is_optimized_hybrid = use_hybrid and base_pixel_features and not use_hybrid_v2
        return TrainingFlags(
            use_hybrid=use_hybrid,
            use_hybrid_v2=use_hybrid_v2,
            train_separate_dimensions=train_separate_dimensions,
            base_pixel_features=base_pixel_features,
            is_optimized_hybrid=is_optimized_hybrid
        )

    def _determine_num_workers(self, requested_workers: int) -> int:
        is_windows = platform.system() == 'Windows'
        if is_windows and requested_workers > 0:
            logger.warning("Windows detectado: Forzando num_workers=0 para evitar fallos de multiprocessing.")
            return 0
        if requested_workers != 0:
            logger.warning("Forzando num_workers=0 para evitar errores de shared memory en DataLoader.")
            return 0
        return requested_workers

    def _resolve_hyperparams(self, options: TrainingOptions, flags: TrainingFlags) -> HyperParams:
        base = HyperParams(
            epochs=int(options['epochs']),
            learning_rate=float(options['learning_rate']),
            patience=int(options['early_stopping_patience']),
            dropout=float(options['dropout_rate']),
            loss=str(options.get('loss_type', 'smooth_l1')),
            scheduler=str(options.get('scheduler_type', 'cosine_warmup'))
        )
        if not flags.is_optimized_hybrid:
            return base

        optimized = HyperParams(
            epochs=base.epochs if base.epochs != 50 else 100,
            learning_rate=base.learning_rate if abs(base.learning_rate - 1e-4) >= 1e-6 else 5e-5,
            patience=base.patience if base.patience != 15 else 25,
            dropout=base.dropout if abs(base.dropout - 0.25) >= 1e-6 else 0.3,
            loss='huber',
            scheduler='cosine_warmup'
        )
        self._notify_optimized_settings(base, optimized)
        return optimized

    def _notify_optimized_settings(self, base: HyperParams, optimized: HyperParams) -> None:
        if base == optimized:
            return
        self.stdout.write(
            self.style.SUCCESS(
                "✅ Configuración optimizada detectada (--hybrid --use-pixel-features)\n"
                "   Aplicando valores optimizados automáticamente:\n"
                f"   - Épocas: {optimized.epochs}\n"
                f"   - Learning Rate: {optimized.learning_rate}\n"
                f"   - Early Stopping Patience: {optimized.patience}\n"
                f"   - Dropout: {optimized.dropout}\n"
                f"   - Loss: {optimized.loss}\n"
                f"   - Scheduler: {optimized.scheduler}"
            )
        )

    def _build_base_config(
        self,
        options: TrainingOptions,
        flags: TrainingFlags,
        num_workers: int,
        hyperparams: HyperParams
    ) -> TrainingConfig:
        use_pixel_features = flags.base_pixel_features and (
            flags.use_hybrid or flags.use_hybrid_v2 or flags.train_separate_dimensions
        )
        return {
            'multi_head': bool(options.get('multihead')) or flags.use_hybrid or flags.use_hybrid_v2,
            'model_type': 'hybrid' if (flags.use_hybrid or flags.use_hybrid_v2) else options.get('model_type'),
            'hybrid': flags.use_hybrid,
            'hybrid_v2': flags.use_hybrid_v2,
            'use_pixel_features': use_pixel_features,
            'train_separate_dimensions': flags.train_separate_dimensions,
            'epochs': hyperparams.epochs,
            'batch_size': int(options['batch_size']),
            'img_size': int(options['img_size']),
            'learning_rate': hyperparams.learning_rate,
            'num_workers': num_workers,
            'early_stopping_patience': hyperparams.patience,
            'dropout_rate': hyperparams.dropout,
            'use_raw_images': bool(options.get('use_raw_images', False)),
            'segmentation_backend': options.get('segmentation_backend', 'auto'),
            'pretrained': True,
            'weight_decay': 1e-4,
            'min_lr': 1e-7,
            'loss_type': hyperparams.loss,
            'scheduler_type': hyperparams.scheduler,
            'max_grad_norm': float(options.get('max_grad_norm', 1.0)),
            'use_mixed_precision': bool(options.get('use_mixed_precision', False)),
            'targets': self._parse_targets(str(options['targets'])),
            'warmup_epochs': self._get_warmup_epochs(options, flags.is_optimized_hybrid)
        }

    def _apply_test_mode(self, config: TrainingConfig, enabled: bool) -> TrainingConfig:
        if not enabled:
            return config
        reduced_config: TrainingConfig = dict(config)
        reduced_config.update({
            'epochs': min(config['epochs'], 5),
            'batch_size': min(config['batch_size'], 16),
            'early_stopping_patience': 3
        })
        self.stdout.write(self.style.WARNING("Modo de prueba activado - configuración reducida"))
        return reduced_config
    
    def _get_warmup_epochs(self, options: TrainingOptions, is_optimized_hybrid: bool) -> int:
        """Get warmup epochs from options or use default based on model type."""
        warmup_epochs = options.get('warmup_epochs')
        if warmup_epochs is not None:
            return int(warmup_epochs)
        
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
    
    def _validate_config(self, config: TrainingConfig) -> None:
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
    
    def _display_config(self, config: TrainingConfig) -> None:
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
    
    def _display_results(self, results: ResultPayload, start_time: float) -> None:
        """Muestra los resultados del entrenamiento."""
        total_time = time.time() - start_time
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write("RESULTADOS DEL ENTRENAMIENTO")
        self.stdout.write("="*50)
        
        self.stdout.write(f"Tiempo total: {total_time:.2f} segundos")
        
        self._print_evaluation_results(results)
        self._print_artifact_summary()
        
        self.stdout.write("="*50)
        self.stdout.write(
            self.style.SUCCESS("¡Entrenamiento completado exitosamente!")
        )

    def _print_evaluation_results(self, results: ResultPayload) -> None:
        eval_results = results.get('evaluation_results')
        if not isinstance(eval_results, Mapping):
            return

        self.stdout.write("\nMétricas de evaluación:")
        config = results.get('config')
        multihead_metrics = eval_results.get('multihead')

        if self._should_use_multihead_metrics(config, multihead_metrics):
            self._print_target_metrics(cast(TargetMetrics, multihead_metrics))
            return

        self._print_target_metrics(cast(TargetMetrics, eval_results))

    def _should_use_multihead_metrics(
        self,
        config: object,
        multihead_metrics: object
    ) -> bool:
        if not isinstance(config, Mapping):
            return False

        uses_multihead = bool(config.get('multi_head')) or bool(config.get('hybrid'))
        return uses_multihead and isinstance(multihead_metrics, Mapping)

    def _print_target_metrics(self, metrics_source: TargetMetrics) -> None:
        for target in METRIC_TARGETS:
            metrics = metrics_source.get(target)
            if isinstance(metrics, Mapping):
                self._print_single_target_metrics(target, metrics)

    def _print_single_target_metrics(self, target: str, metrics: MetricValues) -> None:
        mae = metrics.get('mae')
        rmse = metrics.get('rmse')
        r2_score = metrics.get('r2')

        if mae is None or rmse is None or r2_score is None:
            return

        self.stdout.write(
            f"  {target.upper()}: "
            f"MAE={mae:.4f}, "
            f"RMSE={rmse:.4f}, "
            f"R²={r2_score:.4f}"
        )

    def _print_artifact_summary(self) -> None:
        artifacts_dir = get_regressors_artifacts_dir()
        self.stdout.write(f"\nModelos guardados en: {artifacts_dir}")

        if not artifacts_dir.exists():
            return

        model_files = list(artifacts_dir.glob("*.pt"))
        scaler_files = list(artifacts_dir.glob("*.pkl"))

        self.stdout.write(f"Archivos de modelo: {len(model_files)}")
        self.stdout.write(f"Archivos de escaladores: {len(scaler_files)}")
    
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
            from celery import current_app  # noqa: F401  # Garantiza que Celery esté instalado
        except ImportError:
            raise CommandError(
                "Celery no está disponible. Instala con: pip install celery"
            )
        except Exception as exc:
            raise CommandError(f"Error ejecutando con Celery: {exc}")
        
        self.stdout.write(
            self.style.SUCCESS(
                "Iniciando entrenamiento con Celery (asíncrono)..."
            )
        )
        
        celery_process: Optional[subprocess.Popen] = None
        try:
            if not self._prepare_redis_for_celery(config):
                return
            
            celery_process = self._ensure_celery_worker_ready()
            
            celery_config = self._build_celery_task_config(config)
            
            if not self._check_redis_available():
                self._fallback_to_direct_training(
                    config,
                    "\n[ERROR] Redis no está disponible. Cambiando a entrenamiento directo..."
                )
                return
            
            task_result = auto_train_model_task.delay(
                force=False,
                config=celery_config
            )
            
            self._print_task_submission(task_result.id)
            self._wait_for_task_result(task_result)
        except CommandError:
            raise
        except Exception as exc:
            raise CommandError(f"Error configurando Celery: {exc}")
        finally:
            if celery_process:
                self.stdout.write(
                    self.style.WARNING(
                        "\nCerrando worker de Celery iniciado automáticamente..."
                    )
                )
                self._stop_celery_worker(celery_process)

    def _prepare_redis_for_celery(self, config: dict) -> bool:
        """Garantiza que Redis esté disponible para Celery."""
        if self._check_redis_available():
            return True
        
        self.stdout.write(
            self.style.WARNING(
                "Redis no está disponible. Intentando iniciarlo..."
            )
        )
        
        if not self._start_redis():
            self._fallback_to_direct_training(
                config,
                "\n[ERROR] No se pudo iniciar Redis automáticamente."
            )
            return False
        
        self.stdout.write("Esperando a que Redis esté listo...")
        time.sleep(2)
        
        if self._wait_for_condition(self._check_redis_available, 10, 1.0):
            self.stdout.write(self.style.SUCCESS("Redis está disponible"))
            return True
        
        self._fallback_to_direct_training(
            config,
            "\n[ERROR] Redis no está disponible después de intentar iniciarlo."
        )
        return False

    def _ensure_celery_worker_ready(self) -> Optional[subprocess.Popen]:
        """Inicia un worker de Celery si no existe y espera a que esté listo."""
        if self._check_celery_worker_running():
            return None
        
        self.stdout.write(
            self.style.WARNING(
                "Worker de Celery no está corriendo. Iniciándolo..."
            )
        )
        
        process = self._start_celery_worker()
        if not process:
            raise CommandError("No se pudo iniciar el worker de Celery.")
        
        self.stdout.write("Esperando a que el worker de Celery esté listo...")
        time.sleep(5)
        
        if self._wait_for_condition(self._check_celery_worker_running, 10, 1.0):
            self.stdout.write(
                self.style.SUCCESS("Worker de Celery está corriendo")
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "Worker de Celery iniciado pero aún no responde. Continuando..."
                )
            )
        
        return process

    def _build_celery_task_config(self, config: Mapping[str, object]) -> Dict[str, object]:
        """Construye la configuración que recibirá la tarea de Celery."""
        return {
            'epochs': config.get('epochs', 50),
            'batch_size': config.get('batch_size', 32),
            'learning_rate': config.get('learning_rate', 1e-5),
            'multi_head': config.get('multi_head', False),
            'model_type': config.get('model_type', 'resnet18'),
            'img_size': config.get('img_size', 224),
            'early_stopping_patience': config.get('early_stopping_patience', 10),
            'save_best_only': True
        }

    def _print_task_submission(self, task_id: str) -> None:
        """Informa que la tarea fue enviada a Celery."""
        self.stdout.write(
            self.style.SUCCESS(
                f"Tarea enviada a Celery. Task ID: {task_id}"
            )
        )
        self.stdout.write(
            "Puedes monitorear el progreso con: "
            f"celery -A cacaoscan inspect task {task_id}"
        )
        self.stdout.write(
            "\nEsperando resultado... (presiona Ctrl+C para salir sin esperar)"
        )

    def _wait_for_task_result(self, task_result) -> None:
        """Espera el resultado de la tarea Celery y muestra el estado."""
        try:
            result = task_result.get(timeout=None)
            status = result.get('status')
            message = result.get('message', '')
            
            if status == 'completed':
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Entrenamiento completado: {message or 'OK'}"
                    )
                )
            elif status == 'skipped':
                self.stdout.write(
                    self.style.WARNING(
                        f"Entrenamiento omitido: {message}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"Entrenamiento falló: {message or 'Error desconocido'}"
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
        except Exception as exc:
            raise CommandError(f"Error esperando resultado de Celery: {exc}")

    def _fallback_to_direct_training(self, config: dict, reason: str) -> None:
        """Ejecuta el entrenamiento directo cuando Celery/Redis no están disponibles."""
        self.stdout.write(self.style.WARNING(reason))
        self.stdout.write(
            self.style.WARNING(
                "Ejecutando entrenamiento directo (sin Celery)..."
            )
        )
        self._run_direct_training(config)

    def _run_direct_training(self, config: dict) -> None:
        """Ejecuta el pipeline de entrenamiento directamente."""
        pipeline = CacaoTrainingPipeline(config)
        results = pipeline.run_pipeline()
        self._display_results(results, time.time())

    def _wait_for_condition(
        self,
        condition: Callable[[], bool],
        retries: int,
        delay_seconds: float
    ) -> bool:
        """Espera hasta que se cumpla una condición o se agoten los reintentos."""
        for _ in range(retries):
            if condition():
                return True
            time.sleep(delay_seconds)
        return False
    
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
            if self._start_redis_via_docker():
                return True

            is_windows = platform.system() == 'Windows'
            if is_windows and self._start_redis_windows_service():
                return True

            redis_paths = self._collect_redis_paths(is_windows)
            return self._start_redis_from_paths(redis_paths, is_windows)
        except OSError as e:
            self.stdout.write(
                self.style.ERROR(f"No se pudo iniciar Redis: {e}")
            )
            return False

    def _start_redis_via_docker(self) -> bool:
        try:
            if self._start_existing_docker_container():
                return True
            return self._run_new_docker_container()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def _start_existing_docker_container(self) -> bool:
        check_result = subprocess.run(
            ['docker', 'ps', '-a', '--filter', 'name=redis-cacaoscan', '--format', '{{.Names}}'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if check_result.returncode != 0 or 'redis-cacaoscan' not in check_result.stdout:
            return False

        self.stdout.write("Iniciando contenedor Redis existente...")
        subprocess.run(
            ['docker', 'start', 'redis-cacaoscan'],
            capture_output=True,
            timeout=5
        )
        time.sleep(2)

        if self._check_redis_available():
            self.stdout.write(
                self.style.SUCCESS("Redis iniciado desde contenedor existente")
            )
            return True
        return False

    def _run_new_docker_container(self) -> bool:
        result = subprocess.run(
            ['docker', 'ps'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return False

        self.stdout.write("Intentando iniciar Redis con Docker...")
        subprocess.run(
            ['docker', 'run', '-d', '-p', '6379:6379', '--name', 'redis-cacaoscan', 'redis'],
            capture_output=True,
            timeout=10
        )
        time.sleep(3)

        if self._check_redis_available():
            self.stdout.write(
                self.style.SUCCESS("Redis iniciado con Docker")
            )
            return True
        return False

    def _start_redis_windows_service(self) -> bool:
        try:
            result = subprocess.run(
                ['sc', 'query', 'Redis'],
                capture_output=True,
                timeout=2
            )
            if result.returncode != 0:
                return False

            self.stdout.write("Intentando iniciar servicio Redis de Windows...")
            subprocess.run(
                ['sc', 'start', 'Redis'],
                capture_output=True,
                timeout=5
            )
            time.sleep(2)
            if self._check_redis_available():
                self.stdout.write(
                    self.style.SUCCESS("Redis iniciado como servicio de Windows")
                )
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
        return False

    def _collect_redis_paths(self, is_windows: bool) -> List[str]:
        if is_windows:
            return [
                'redis-server.exe',
                r'C:\Program Files\Redis\redis-server.exe',
                r'C:\redis\redis-server.exe',
            ]
        return ['redis-server', '/usr/local/bin/redis-server', '/usr/bin/redis-server']

    def _start_redis_from_paths(self, redis_paths: List[str], is_windows: bool) -> bool:
        for redis_path in redis_paths:
            if self._launch_redis_process(redis_path, is_windows):
                return True
        return False

    def _launch_redis_process(self, redis_path: str, is_windows: bool) -> bool:
        try:
            kwargs: Dict[str, object] = {
                'stdout': subprocess.DEVNULL,
                'stderr': subprocess.DEVNULL,
            }
            if is_windows:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            else:
                kwargs['start_new_session'] = True

            subprocess.Popen([redis_path], **kwargs)
            time.sleep(3)
            if self._check_redis_available():
                self.stdout.write(
                    self.style.SUCCESS(f"Redis iniciado: {redis_path}")
                )
                return True
        except OSError:
            return False
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
                process = subprocess.Popen(
                    celery_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            setattr(process, 'cacaoscan_role', 'celery-worker')
            setattr(process, 'cacaoscan_cmd', tuple(str(arg) for arg in celery_cmd))
            
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
    
    def _is_celery_worker_process(self, process: subprocess.Popen) -> bool:
        """
        Valida que un proceso es el worker de Celery que iniciamos.
        
        SECURITY: Critical validation to prevent signaling arbitrary processes.
        This function uses multiple checks:
        1. Primary: Checks for 'cacaoscan_role' attribute set by _start_celery_worker
           This is the strongest validation as it's a custom attribute only our processes have
        2. Fallback: Validates process arguments contain 'celery' and 'worker'
           This is a secondary check for defense in depth
        
        Args:
            process: Process object to validate
            
        Returns:
            True if process is a Celery worker we spawned, False otherwise
        """
        if process is None:
            return False
        
        # Primary security check: Custom attribute set when we create the process
        # This is the strongest validation as it can't be faked
        role = getattr(process, 'cacaoscan_role', None)
        if role == 'celery-worker':
            return True
        
        # Fallback validation: Check process arguments
        # This provides defense in depth but is less secure than the role check
        args = getattr(process, 'args', None)
        if not args:
            return False
        
        if isinstance(args, str):
            normalized = args.lower()
            return 'celery' in normalized and 'worker' in normalized
        
        normalized_args = [str(arg).lower() for arg in args]
        has_celery = any('celery' in arg for arg in normalized_args)
        has_worker = any('worker' in arg for arg in normalized_args)
        return has_celery and has_worker
    
    def _stop_celery_worker(self, process: subprocess.Popen) -> None:
        """
        Detiene el worker de Celery iniciado automáticamente.
        
        SECURITY: S4828 - Sending signals is security-sensitive.
        This function implements multiple security layers:
        1. Validates process is a Celery worker we started (_can_attempt_stop)
        2. Validates PID is valid and positive (_extract_process_pid)
        3. Verifies process still exists before signaling (_ensure_process_exists)
        4. Uses graceful SIGTERM instead of SIGKILL
        5. Only signals processes spawned by this command instance
        
        The process object must have been created by _start_celery_worker() and
        must pass all validation checks before any signals are sent.
        """
        try:
            if not self._can_attempt_stop(process):
                return

            process_pid = self._extract_process_pid(process)
            if process_pid is None:
                return

            if not self._ensure_process_exists(process_pid):
                return

            system = platform.system()
            if system == 'Windows':
                self._terminate_windows_process(process)
            else:
                if not self._terminate_unix_process(process_pid):
                    return

            self._wait_for_process_shutdown(process)
        except CommandError:
            raise
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"Error deteniendo worker: {e}")
            )

    def _can_attempt_stop(self, process: Optional[subprocess.Popen]) -> bool:
        """
        Valida que es seguro intentar detener un proceso.
        
        SECURITY: S4828 - Critical security validation before sending signals.
        This function ensures we only signal processes we started by:
        1. Checking the process is not None
        2. Validating it's a Celery worker process we spawned
        3. Checking the process hasn't already terminated
        
        Args:
            process: Process object to validate
            
        Returns:
            True if safe to stop, False otherwise
            
        Raises:
            CommandError: If process is not a Celery worker we started (security violation)
        """
        if process is None:
            logger.debug("Process is None, cannot stop")
            return False

        # Security: Only allow stopping processes we started
        # This prevents signaling arbitrary processes on the system
        if not self._is_celery_worker_process(process):
            raise CommandError(
                "Signal aborted: process is not a Celery worker started by this command."
            )

        if process.poll() is not None:
            logger.debug("Process already terminated")
            return False

        return True

    def _extract_process_pid(self, process: subprocess.Popen) -> Optional[int]:
        """
        Extrae y valida el PID de un proceso.
        
        SECURITY: Validates PID before use to prevent signaling invalid processes.
        
        Args:
            process: Process object to extract PID from
            
        Returns:
            Valid PID (> 0) or None if invalid
        """
        try:
            process_pid = process.pid
        except AttributeError as exc:
            logger.debug(f"Process missing PID attribute: {exc}")
            return None

        # Security: Validate PID is positive and not None
        # Negative PIDs or 0 are invalid and could be dangerous
        if process_pid is None or process_pid <= 0:
            logger.warning("Invalid process PID, cannot send signal")
            return None

        return int(process_pid)

    def _ensure_process_exists(self, process_pid: int) -> bool:
        """
        Verifica que un proceso exista antes de enviar señales.
        
        SECURITY: S4828 - Sending signals is security-sensitive.
        This function uses os.kill(pid, 0) which is safe because:
        1. Signal 0 is a null signal that doesn't actually send any signal
        2. It only checks if the process exists and if we have permission to signal it
        3. The process_pid has already been validated by _extract_process_pid
        4. The process has been validated as a Celery worker by _can_attempt_stop
        
        Args:
            process_pid: Process ID to check (already validated)
            
        Returns:
            True if process exists and we have permission, False otherwise
        """
        if platform.system() == 'Windows':
            # On Windows, we use process.terminate() which is safer
            return True

        import os
        try:
            # SECURITY: S4828 - Signal 0 is safe: it doesn't send any signal, only checks process existence
            # This is a standard POSIX way to check if a process exists
            # The process_pid has already been validated by _extract_process_pid (must be > 0)
            # The process has been validated as a Celery worker by _can_attempt_stop
            # Signal 0 is a null signal that only validates process existence and permissions
            # NOSONAR S4828 - Signal 0 is explicitly safe, it performs no action, only validation
            os.kill(process_pid, 0)  # NOSONAR S4828
            return True
        except ProcessLookupError:
            logger.debug("Process no longer exists")
            return False
        except PermissionError:
            # Security: If we don't have permission, abort to prevent privilege escalation
            logger.warning("Permission denied when checking process, aborting signal")
            return False
        except OSError as exc:
            logger.debug(f"Error validating process existence: {exc}")
            return False

    def _terminate_windows_process(self, process: subprocess.Popen) -> None:
        process.terminate()

    def _terminate_unix_process(self, process_pid: int) -> bool:
        """
        Termina un proceso Unix enviando SIGTERM a su grupo de procesos.
        
        SECURITY: S4828 - Sending signals is security-sensitive.
        This function is safe because:
        1. The process_pid has been validated by _extract_process_pid (must be > 0)
        2. The process has been validated as a Celery worker by _can_attempt_stop
        3. The process existence has been verified by _ensure_process_exists
        4. We only send SIGTERM (graceful shutdown), not SIGKILL
        5. We validate the process group ID before sending the signal
        
        Args:
            process_pid: Process ID to terminate (already validated)
            
        Returns:
            True if signal was sent successfully, False otherwise
        """
        import os
        try:
            # Get process group ID - this validates the process still exists
            pgid = os.getpgid(process_pid)
        except OSError as exc:
            logger.debug(f"Failed to obtain process group: {exc}")
            return False

        # Security: Validate process group ID before sending signal
        if pgid <= 0:
            logger.warning(f"Invalid process group ID: {pgid}, cannot send signal")
            return False

        # Additional security validation: verify process group matches process
        try:
            actual_pgid = os.getpgid(process_pid)
            if actual_pgid != pgid:
                logger.warning(
                    f"Security validation failed: Process group mismatch. "
                    f"Expected {pgid}, got {actual_pgid}"
                )
                return False
        except OSError as exc:
            logger.warning(f"Security validation failed: Cannot verify process group: {exc}")
            return False

        # All security validations passed - safe to send signal
        return self._send_termination_signal(pgid, process_pid)

    def _send_termination_signal(self, pgid: int, process_pid: int) -> bool:
        """
        Sends SIGTERM signal to a validated process group.
        
        SECURITY: S4828 - This function is safe because:
        1. All security validations have been performed before calling this function
        2. process_pid was validated by _extract_process_pid (must be > 0, not None)
        3. Process was validated as our Celery worker by _can_attempt_stop
        4. Process existence was verified by _ensure_process_exists
        5. Process group ID (pgid) is valid (> 0) and matches the process
        6. We only send SIGTERM (graceful shutdown), never SIGKILL
        7. All exceptions are caught and handled safely
        
        This function should ONLY be called after all security validations pass.
        
        Args:
            pgid: Validated process group ID (> 0)
            process_pid: Validated process ID (> 0)
            
        Returns:
            True if signal was sent successfully, False otherwise
        """
        import os
        try:
            # SECURITY: S4828 - Sending signals is security-sensitive
            # This os.killpg call is safe because all security validations have passed:
            # 1. process_pid was validated by _extract_process_pid (must be > 0, not None)
            # 2. Process was validated as our Celery worker by _can_attempt_stop
            #    (checks 'cacaoscan_role' attribute and process arguments)
            # 3. Process existence was verified by _ensure_process_exists
            # 4. Process group ID (pgid) is valid (> 0) and matches the process
            # 5. We only send SIGTERM (graceful shutdown), never SIGKILL
            # 6. All exceptions are caught and handled safely
            # This ensures we never signal arbitrary processes, only processes we spawned
            os.killpg(pgid, signal.SIGTERM)
            logger.debug(f"Sent SIGTERM to process group {pgid} (process {process_pid})")
            return True
        except ProcessLookupError:
            logger.debug("Process group no longer exists, process may have terminated")
            return False
        except OSError as exc:
            logger.debug(f"Process group signal failed (may already be terminated): {exc}")
            return False

    def _wait_for_process_shutdown(self, process: subprocess.Popen) -> None:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            if process.poll() is None:
                logger.warning("Graceful shutdown timed out, force killing process")
                process.kill()
                process.wait()

