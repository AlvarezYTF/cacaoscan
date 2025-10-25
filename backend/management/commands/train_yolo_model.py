"""
Comando Django para entrenar modelo YOLOv8-seg personalizado.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json
import time
from pathlib import Path

from ml.segmentation.train_yolo import YOLOTrainingManager, train_cacao_yolo_model


class Command(BaseCommand):
    help = 'Entrena modelo YOLOv8-seg personalizado para segmentación de granos de cacao'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dataset-size',
            type=int,
            default=150,
            help='Número de imágenes para el dataset (default: 150)'
        )
        parser.add_argument(
            '--epochs',
            type=int,
            default=100,
            help='Número de épocas de entrenamiento (default: 100)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=16,
            help='Tamaño del batch (default: 16)'
        )
        parser.add_argument(
            '--model-name',
            type=str,
            default='yolov8s-seg',
            choices=['yolov8n-seg', 'yolov8s-seg', 'yolov8m-seg', 'yolov8l-seg', 'yolov8x-seg'],
            help='Modelo base YOLO a usar (default: yolov8s-seg)'
        )
        parser.add_argument(
            '--image-size',
            type=int,
            default=640,
            help='Tamaño de imagen para entrenamiento (default: 640)'
        )
        parser.add_argument(
            '--confidence',
            type=float,
            default=0.5,
            help='Umbral de confianza (default: 0.5)'
        )
        parser.add_argument(
            '--iou-threshold',
            type=float,
            default=0.7,
            help='Umbral de IoU (default: 0.7)'
        )
        parser.add_argument(
            '--train-split',
            type=float,
            default=0.7,
            help='Proporción para entrenamiento (default: 0.7)'
        )
        parser.add_argument(
            '--val-split',
            type=float,
            default=0.2,
            help='Proporción para validación (default: 0.2)'
        )
        parser.add_argument(
            '--test-split',
            type=float,
            default=0.1,
            help='Proporción para testing (default: 0.1)'
        )
        parser.add_argument(
            '--device',
            type=str,
            default='cpu',
            choices=['cpu', 'cuda', 'auto'],
            help='Dispositivo para entrenamiento (default: cpu)'
        )
        parser.add_argument(
            '--workers',
            type=int,
            default=4,
            help='Número de workers para data loading (default: 4)'
        )
        parser.add_argument(
            '--patience',
            type=int,
            default=20,
            help='Paciencia para early stopping (default: 20)'
        )
        parser.add_argument(
            '--learning-rate',
            type=float,
            default=0.01,
            help='Learning rate inicial (default: 0.01)'
        )
        parser.add_argument(
            '--weight-decay',
            type=float,
            default=0.0005,
            help='Weight decay (default: 0.0005)'
        )
        parser.add_argument(
            '--momentum',
            type=float,
            default=0.937,
            help='Momentum (default: 0.937)'
        )
        parser.add_argument(
            '--warmup-epochs',
            type=int,
            default=3,
            help='Épocas de warmup (default: 3)'
        )
        parser.add_argument(
            '--save-period',
            type=int,
            default=10,
            help='Período para guardar checkpoints (default: 10)'
        )
        parser.add_argument(
            '--cache',
            action='store_true',
            help='Cachear imágenes en memoria'
        )
        parser.add_argument(
            '--plots',
            action='store_true',
            help='Generar gráficos de entrenamiento'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Salida verbose'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo mostrar configuración sin entrenar'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            help='Directorio de salida personalizado'
        )

    def handle(self, *args, **options):
        """Ejecuta el comando de entrenamiento."""
        
        # Validar argumentos
        self._validate_arguments(options)
        
        # Mostrar configuración
        self._display_configuration(options)
        
        if options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS('Dry run completado. No se realizó entrenamiento.')
            )
            return
        
        # Confirmar antes de continuar
        if not self._confirm_training(options):
            self.stdout.write(
                self.style.WARNING('Entrenamiento cancelado por el usuario.')
            )
            return
        
        try:
            # Crear entrenador
            trainer = YOLOTrainingManager(
                dataset_size=options['dataset_size'],
                train_split=options['train_split'],
                val_split=options['val_split'],
                test_split=options['test_split'],
                image_size=options['image_size'],
                epochs=options['epochs'],
                batch_size=options['batch_size'],
                confidence_threshold=options['confidence'],
                iou_threshold=options['iou_threshold']
            )
            
            # Ejecutar entrenamiento
            self.stdout.write(
                self.style.SUCCESS('Iniciando entrenamiento...')
            )
            
            start_time = time.time()
            results = trainer.run_full_training_pipeline(
                model_name=options['model_name']
            )
            end_time = time.time()
            
            # Mostrar resultados
            self._display_results(results, end_time - start_time)
            
            # Guardar resultados en archivo
            self._save_results(results, options)
            
        except Exception as e:
            raise CommandError(f'Error durante el entrenamiento: {e}')
    
    def _validate_arguments(self, options):
        """Valida los argumentos del comando."""
        
        # Validar splits
        total_split = options['train_split'] + options['val_split'] + options['test_split']
        if abs(total_split - 1.0) > 0.001:
            raise CommandError(
                f'Los splits deben sumar 1.0, actual: {total_split:.3f}'
            )
        
        # Validar dataset size
        if options['dataset_size'] < 10:
            raise CommandError(
                f'Dataset size debe ser al menos 10, actual: {options["dataset_size"]}'
            )
        
        # Validar epochs
        if options['epochs'] < 1:
            raise CommandError(
                f'Épocas debe ser al menos 1, actual: {options["epochs"]}'
            )
        
        # Validar batch size
        if options['batch_size'] < 1:
            raise CommandError(
                f'Batch size debe ser al menos 1, actual: {options["batch_size"]}'
            )
        
        # Validar learning rate
        if options['learning_rate'] <= 0:
            raise CommandError(
                f'Learning rate debe ser positivo, actual: {options["learning_rate"]}'
            )
    
    def _display_configuration(self, options):
        """Muestra la configuración del entrenamiento."""
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('CONFIGURACIÓN DE ENTRENAMIENTO YOLO'))
        self.stdout.write('='*60)
        
        config_items = [
            ('Dataset Size', options['dataset_size']),
            ('Modelo Base', options['model_name']),
            ('Épocas', options['epochs']),
            ('Batch Size', options['batch_size']),
            ('Image Size', options['image_size']),
            ('Device', options['device']),
            ('Workers', options['workers']),
            ('Learning Rate', options['learning_rate']),
            ('Weight Decay', options['weight_decay']),
            ('Momentum', options['momentum']),
            ('Warmup Epochs', options['warmup_epochs']),
            ('Patience', options['patience']),
            ('Confidence Threshold', options['confidence']),
            ('IoU Threshold', options['iou_threshold']),
            ('Train Split', f"{options['train_split']:.1%}"),
            ('Val Split', f"{options['val_split']:.1%}"),
            ('Test Split', f"{options['test_split']:.1%}"),
            ('Cache', 'Sí' if options['cache'] else 'No'),
            ('Plots', 'Sí' if options['plots'] else 'No'),
            ('Verbose', 'Sí' if options['verbose'] else 'No'),
        ]
        
        for key, value in config_items:
            self.stdout.write(f'{key:20}: {value}')
        
        self.stdout.write('='*60)
    
    def _confirm_training(self, options):
        """Solicita confirmación antes de entrenar."""
        
        self.stdout.write('\n' + self.style.WARNING('⚠️  ADVERTENCIA:'))
        self.stdout.write('El entrenamiento puede tomar varias horas.')
        self.stdout.write('Asegúrate de tener suficientes recursos disponibles.')
        
        response = input('\n¿Continuar con el entrenamiento? (y/N): ')
        return response.lower() in ['y', 'yes', 'sí', 'si']
    
    def _display_results(self, results, duration):
        """Muestra los resultados del entrenamiento."""
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('RESULTADOS DEL ENTRENAMIENTO'))
        self.stdout.write('='*60)
        
        if results['success']:
            # Información del dataset
            dataset_info = results['dataset_info']
            self.stdout.write(f'Dataset Size: {dataset_info["total_images"]} imágenes')
            self.stdout.write(f'  - Train: {dataset_info["train_images"]} imágenes')
            self.stdout.write(f'  - Val: {dataset_info["val_images"]} imágenes')
            self.stdout.write(f'  - Test: {dataset_info["test_images"]} imágenes')
            
            # Duración
            self.stdout.write(f'Duración: {duration:.2f} segundos ({duration/60:.1f} minutos)')
            
            # Métricas de validación
            if 'validation_metrics' in results:
                metrics = results['validation_metrics']
                self.stdout.write('\nMétricas de Validación:')
                self.stdout.write(f'  mAP50: {metrics["mAP50"]:.3f}')
                self.stdout.write(f'  mAP50-95: {metrics["mAP50-95"]:.3f}')
                self.stdout.write(f'  Precision: {metrics["precision"]:.3f}')
                self.stdout.write(f'  Recall: {metrics["recall"]:.3f}')
                self.stdout.write(f'  F1-Score: {metrics["f1_score"]:.3f}')
                
                if metrics['mask_mAP50'] > 0:
                    self.stdout.write(f'  Mask mAP50: {metrics["mask_mAP50"]:.3f}')
                    self.stdout.write(f'  Mask mAP50-95: {metrics["mask_mAP50-95"]:.3f}')
            
            # Rutas de modelos
            model_paths = results['model_paths']
            self.stdout.write('\nArchivos Generados:')
            self.stdout.write(f'  Mejor Modelo: {model_paths["best_model"]}')
            self.stdout.write(f'  Último Modelo: {model_paths["last_model"]}')
            self.stdout.write(f'  Config Dataset: {model_paths["dataset_config"]}')
            
            self.stdout.write('\n' + self.style.SUCCESS('✅ Entrenamiento completado exitosamente!'))
            
        else:
            self.stdout.write(self.style.ERROR('❌ Entrenamiento falló'))
            self.stdout.write(f'Error: {results.get("error", "Error desconocido")}')
            self.stdout.write(f'Duración: {duration:.2f} segundos')
        
        self.stdout.write('='*60)
    
    def _save_results(self, results, options):
        """Guarda los resultados en un archivo JSON."""
        
        try:
            # Crear directorio de resultados
            results_dir = Path(settings.BASE_DIR) / 'ml' / 'artifacts' / 'training_results'
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # Nombre del archivo con timestamp
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'yolo_training_results_{timestamp}.json'
            results_path = results_dir / filename
            
            # Preparar datos para guardar
            save_data = {
                'timestamp': timestamp,
                'options': options,
                'results': results
            }
            
            # Guardar archivo
            with open(results_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, default=str, ensure_ascii=False)
            
            self.stdout.write(f'\nResultados guardados en: {results_path}')
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'No se pudieron guardar los resultados: {e}')
            )
