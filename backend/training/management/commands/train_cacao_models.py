"""
Comando Django para entrenar modelos de regresión de cacao.
"""
import time
import subprocess
import sys
import platform
import signal
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path
from typing import List, Optional

from ml.pipeline.train_all import CacaoTrainingPipeline
from ml.utils.logs import get_ml_logger


logger = get_ml_logger("cacaoscan.ml.commands")


class Command(BaseCommand):
    help = 'Entrena modelos de regresión para dimensiones y peso de granos de cacao'
    
    def add_arguments(self, parser):
        # Argumentos del modelo
        parser.add_argument(
            '--multihead',
            action='store_true',
            help='Usar modelo multi-head en lugar de modelos individuales'
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
            help='Usar modelo híbrido que fusiona ResNet18 + ConvNeXt + Features de píxeles (equivalente a --model-type hybrid)'
        )
        parser.add_argument(
            '--use-pixel-features',
            action='store_true',
            default=True,
            help='Usar features de píxeles del dataset si pixel_calibration.json existe (default: True)'
        )
        
        # Argumentos de entrenamiento
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
            default=1e-4,
            help='Learning rate (default: 1e-4)'
        )
        
        # Argumentos de targets
        parser.add_argument(
            '--targets',
            type=str,
            default='all',
            help='Targets a entrenar: alto,ancho,grosor,peso o "all" (default: all)'
        )
        
        # Argumentos de configuración
        parser.add_argument(
            '--resume',
            action='store_true',
            help='Resumir entrenamiento desde checkpoint (no implementado aún)'
        )
        parser.add_argument(
            '--num-workers',
            type=int,
            default=2,
            help='Número de workers para data loading (default: 2)'
        )
        parser.add_argument(
            '--early-stopping-patience',
            type=int,
            default=10,
            help='Paciencia para early stopping (default: 10)'
        )
        parser.add_argument(
            '--dropout-rate',
            type=float,
            default=0.2,
            help='Tasa de dropout (default: 0.2)'
        )
        
        # Argumentos de validación
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Solo validar datos sin entrenar modelos'
        )
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Modo de prueba con configuración reducida'
        )
        parser.add_argument(
            '--use-celery',
            action='store_true',
            help='Ejecutar entrenamiento con Celery (asíncrono)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar reentrenamiento aunque ya existan modelos entrenados'
        )
    
    def handle(self, *args, **options):
        """Maneja la ejecución del comando."""
        start_time = time.time()
        
        # Configurar parámetros
        config = self._create_config(options)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Iniciando entrenamiento de modelos de cacao"
            )
        )
        
        try:
            # Validar configuración
            self._validate_config(config)
            
            # Mostrar configuración
            self._display_config(config)
            
            if options['validate_only']:
                self._validate_data_only()
                return
            
            # Verificar si hay modelos entrenados (a menos que se fuerce el reentrenamiento)
            if not options.get('force'):
                models_exist = self._check_models_exist()
                
                if models_exist:
                    self.stdout.write(
                        self.style.SUCCESS(
                            "✅ Modelos entrenados encontrados. No es necesario entrenar."
                        )
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            "💡 Para forzar el reentrenamiento, usa la opción --force"
                        )
                    )
                    return
            else:
                models_exist = self._check_models_exist()
                if models_exist:
                    self.stdout.write(
                        self.style.WARNING(
                            "⚠️  Modelos entrenados encontrados, pero se fuerza el reentrenamiento (--force activado)"
                        )
                    )
            
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Modelos entrenados no encontrados. Iniciando entrenamiento..."
                )
            )
            
            # Ejecutar con Celery si se solicita
            if options.get('use_celery'):
                self._run_with_celery(config, options)
                return
            
            # Ejecución directa (sin Celery)
            pipeline = CacaoTrainingPipeline(config)
            results = pipeline.run_pipeline(config['multi_head'])
            self._display_results(results, start_time)
            
        except Exception as e:
            raise CommandError(f"Error durante el entrenamiento: {e}")
    
    def _create_config(self, options: dict) -> dict:
        """Crea la configuración del entrenamiento."""
        # Determinar si usar modelo híbrido
        use_hybrid = options.get('hybrid', False) or options.get('model_type') == 'hybrid'
        
        config = {
            'multi_head': options['multihead'] or use_hybrid,  # Híbrido es multi-output por defecto
            'model_type': 'hybrid' if use_hybrid else options['model_type'],
            'hybrid': use_hybrid,
            'use_pixel_features': options.get('use_pixel_features', True),
            'epochs': options['epochs'],
            'batch_size': options['batch_size'],
            'img_size': options['img_size'],
            'learning_rate': options['learning_rate'],
            'num_workers': options['num_workers'],
            'early_stopping_patience': options['early_stopping_patience'],
            'dropout_rate': options['dropout_rate'],
            'pretrained': True,
            'weight_decay': 1e-4,
            'min_lr': 1e-6,
            'targets': self._parse_targets(options['targets'])
        }
        
        # Modo de prueba
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
        # Validar que los crops existan
        crops_dir = Path(settings.MEDIA_ROOT) / "cacao_images" / "crops"
        if not crops_dir.exists():
            raise CommandError(f"Directorio de crops no encontrado: {crops_dir}")
        
        # Contar crops disponibles
        crop_files = list(crops_dir.glob("*.png"))
        if len(crop_files) < 10:
            raise CommandError(
                f"Muy pocos crops disponibles: {len(crop_files)}. "
                "Se necesitan al menos 10 para entrenamiento."
            )
        
        # Validar configuración de modelo
        if config['multi_head'] and config['model_type'] == 'convnext_tiny':
            try:
                import timm
            except ImportError:
                raise CommandError(
                    "timm es requerido para ConvNeXt. Instalar con: pip install timm"
                )
        
        # Validar parámetros de entrenamiento
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
            self.stdout.write("  → Modelo HÍBRIDO: ResNet18 + ConvNeXt + Features de Píxeles")
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
        
        # Mostrar información de datos
        crops_dir = Path(settings.MEDIA_ROOT) / "cacao_images" / "crops"
        crop_files = list(crops_dir.glob("*.png"))
        self.stdout.write(f"Crops disponibles: {len(crop_files)}")
        
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
            
            # Contar crops disponibles
            crops_available = 0
            for record in valid_records:
                if record['crop_image_path'] and record['crop_image_path'].exists():
                    crops_available += 1
            
            self.stdout.write(f"Registros válidos: {len(valid_records)}")
            self.stdout.write(f"Crops disponibles: {crops_available}")
            
            if crops_available < 10:
                raise CommandError(
                    f"Muy pocos crops disponibles: {crops_available}. "
                    "Se necesitan al menos 10 para entrenamiento."
                )
            
            # Mostrar estadísticas
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
        
        # Mostrar resultados de evaluación
        if 'evaluation_results' in results:
            eval_results = results['evaluation_results']
            self.stdout.write("\nMétricas de evaluación:")
            
            if results['config']['multi_head'] and 'multihead' in eval_results:
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
        
        # Mostrar ubicación de archivos
        artifacts_dir = Path(settings.MEDIA_ROOT).parent / "ml" / "artifacts" / "regressors"
        self.stdout.write(f"\nModelos guardados en: {artifacts_dir}")
        
        # Listar archivos generados
        if artifacts_dir.exists():
            model_files = list(artifacts_dir.glob("*.pt"))
            scaler_files = list(artifacts_dir.glob("*.pkl"))
            
            self.stdout.write(f"Archivos de modelo: {len(model_files)}")
            self.stdout.write(f"Archivos de escaladores: {len(scaler_files)}")
        
        self.stdout.write("="*50)
        
        self.stdout.write(
            self.style.SUCCESS("¡Entrenamiento completado exitosamente!")
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
                                "\n❌ No se pudo iniciar Redis automáticamente."
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
                    for i in range(max_retries):
                        if self._check_redis_available():
                            self.stdout.write(
                                self.style.SUCCESS("Redis está disponible")
                            )
                            break
                        time_module.sleep(1)
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                "\n❌ Redis no está disponible después de intentar iniciarlo."
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
                    for i in range(max_retries):
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
                    'learning_rate': config.get('learning_rate', 1e-4),
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
                            "\n❌ Redis no está disponible. Cambiando a entrenamiento directo..."
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
                        f"Para monitorear: celery -A cacaoscan inspect active"
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
                        process = subprocess.Popen(
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
        except Exception as e:
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
                process = subprocess.Popen(
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

