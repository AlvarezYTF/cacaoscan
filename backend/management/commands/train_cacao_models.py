"""
Comando Django para entrenar modelos de regresiÃ³n de cacao.
"""
import time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path
from typing import List

from ml.pipeline.train_all import CacaoTrainingPipeline
from ml.utils.logs import get_ml_logger


logger = get_ml_logger("cacaoscan.ml.commands")


class Command(BaseCommand):
    help = 'Entrena modelos de regresiÃ³n para dimensiones y peso de granos de cacao'
    
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
            choices=['resnet18', 'convnext_tiny'],
            help='Tipo de modelo a usar (default: resnet18)'
        )
        
        # Argumentos de entrenamiento
        parser.add_argument(
            '--epochs',
            type=int,
            default=50,
            help='NÃºmero de Ã©pocas de entrenamiento (default: 50)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=32,
            help='TamaÃ±o de batch (default: 32)'
        )
        parser.add_argument(
            '--img-size',
            type=int,
            default=224,
            help='TamaÃ±o de imagen de entrada (default: 224)'
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
        
        # Argumentos de configuraciÃ³n
        parser.add_argument(
            '--resume',
            action='store_true',
            help='Resumir entrenamiento desde checkpoint (no implementado aÃºn)'
        )
        parser.add_argument(
            '--num-workers',
            type=int,
            default=2,
            help='NÃºmero de workers para data loading (default: 2)'
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
        
        # Argumentos de validaciÃ³n
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Solo validar datos sin entrenar modelos'
        )
        parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Modo de prueba con configuraciÃ³n reducida'
        )
    
    def handle(self, *args, **options):
        """Maneja la ejecuciÃ³n del comando."""
        start_time = time.time()
        
        # Configurar parÃ¡metros
        config = self._create_config(options)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Iniciando entrenamiento de modelos de cacao"
            )
        )
        
        try:
            # Validar configuraciÃ³n
            self._validate_config(config)
            
            # Mostrar configuraciÃ³n
            self._display_config(config)
            
            if options['validate_only']:
                self._validate_data_only()
                return
            
            # Crear pipeline
            pipeline = CacaoTrainingPipeline(config)
            
            # Ejecutar pipeline
            results = pipeline.run_pipeline(config['multi_head'])
            
            # Mostrar resultados
            self._display_results(results, start_time)
            
        except Exception as e:
            raise CommandError(f"Error durante el entrenamiento: {e}")
    
    def _create_config(self, options: dict) -> dict:
        """Crea la configuraciÃ³n del entrenamiento."""
        config = {
            'multi_head': options['multihead'],
            'model_type': options['model_type'],
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
                self.style.WARNING("Modo de prueba activado - configuraciÃ³n reducida")
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
                raise ValueError(f"Target invÃ¡lido: {target}. Targets vÃ¡lidos: {valid_targets}")
        
        return targets
    
    def _validate_config(self, config: dict) -> None:
        """Valida la configuraciÃ³n."""
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
        
        # Validar configuraciÃ³n de modelo
        if config['multi_head'] and config['model_type'] == 'convnext_tiny':
            try:
                import timm
            except ImportError:
                raise CommandError(
                    "timm es requerido para ConvNeXt. Instalar con: pip install timm"
                )
        
        # Validar parÃ¡metros de entrenamiento
        if config['epochs'] < 1:
            raise CommandError("NÃºmero de Ã©pocas debe ser >= 1")
        
        if config['batch_size'] < 1:
            raise CommandError("TamaÃ±o de batch debe ser >= 1")
        
        if config['learning_rate'] <= 0:
            raise CommandError("Learning rate debe ser > 0")
    
    def _display_config(self, config: dict) -> None:
        """Muestra la configuraciÃ³n del entrenamiento."""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("CONFIGURACIÃ“N DE ENTRENAMIENTO")
        self.stdout.write("="*50)
        
        self.stdout.write(f"Modelo: {config['model_type']}")
        self.stdout.write(f"Multi-head: {config['multi_head']}")
        self.stdout.write(f"Targets: {config['targets']}")
        self.stdout.write(f"Ã‰pocas: {config['epochs']}")
        self.stdout.write(f"Batch size: {config['batch_size']}")
        self.stdout.write(f"TamaÃ±o de imagen: {config['img_size']}")
        self.stdout.write(f"Learning rate: {config['learning_rate']}")
        self.stdout.write(f"Dropout rate: {config['dropout_rate']}")
        self.stdout.write(f"Early stopping patience: {config['early_stopping_patience']}")
        self.stdout.write(f"Workers: {config['num_workers']}")
        
        # Mostrar informaciÃ³n de datos
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
                raise CommandError("No se encontraron registros vÃ¡lidos")
            
            # Contar crops disponibles
            crops_available = 0
            for record in valid_records:
                if record['crop_image_path'] and record['crop_image_path'].exists():
                    crops_available += 1
            
            self.stdout.write(f"Registros vÃ¡lidos: {len(valid_records)}")
            self.stdout.write(f"Crops disponibles: {crops_available}")
            
            if crops_available < 10:
                raise CommandError(
                    f"Muy pocos crops disponibles: {crops_available}. "
                    "Se necesitan al menos 10 para entrenamiento."
                )
            
            # Mostrar estadÃ­sticas
            stats = loader.get_dataset_stats()
            self.stdout.write("\nEstadÃ­sticas del dataset:")
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
                self.style.SUCCESS("ValidaciÃ³n de datos completada exitosamente")
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
        
        # Mostrar resultados de evaluaciÃ³n
        if 'evaluation_results' in results:
            eval_results = results['evaluation_results']
            self.stdout.write("\nMÃ©tricas de evaluaciÃ³n:")
            
            if results['config']['multi_head'] and 'multihead' in eval_results:
                multihead_results = eval_results['multihead']
                for target in ['alto', 'ancho', 'grosor', 'peso']:
                    if target in multihead_results:
                        metrics = multihead_results[target]
                        self.stdout.write(
                            f"  {target.upper()}: "
                            f"MAE={metrics['mae']:.4f}, "
                            f"RMSE={metrics['rmse']:.4f}, "
                            f"RÂ²={metrics['r2']:.4f}"
                        )
            else:
                for target in ['alto', 'ancho', 'grosor', 'peso']:
                    if target in eval_results:
                        metrics = eval_results[target]
                        self.stdout.write(
                            f"  {target.upper()}: "
                            f"MAE={metrics['mae']:.4f}, "
                            f"RMSE={metrics['rmse']:.4f}, "
                            f"RÂ²={metrics['r2']:.4f}"
                        )
        
        # Mostrar ubicaciÃ³n de archivos
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
            self.style.SUCCESS("Â¡Entrenamiento completado exitosamente!")
        )


