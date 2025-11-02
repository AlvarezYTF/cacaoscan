"""
Comando Django para generar recortes de granos de cacao.
"""
import time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path

from ml.data.dataset_loader import CacaoDatasetLoader
from ml.segmentation.cropper import create_cacao_cropper
from ml.utils.logs import get_ml_logger


logger = get_ml_logger("cacaoscan.ml.commands")


class Command(BaseCommand):
    help = 'Genera recortes de granos de cacao usando segmentaciÃ³n YOLOv8-seg'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--conf',
            type=float,
            default=0.5,
            help='Umbral de confianza para YOLO (default: 0.5)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='LÃ­mite de imÃ¡genes a procesar (0 = todas, default: 0)'
        )
        parser.add_argument(
            '--input-dir',
            type=str,
            help='Directorio de imÃ¡genes de entrada (default: media/cacao_images/raw)'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            help='Directorio de salida para crops (default: media/cacao_images/crops)'
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Sobrescribir crops existentes'
        )
        parser.add_argument(
            '--save-masks',
            action='store_true',
            help='Guardar mÃ¡scaras para debug'
        )
        parser.add_argument(
            '--crop-size',
            type=int,
            default=512,
            help='TamaÃ±o del crop cuadrado (default: 512)'
        )
        parser.add_argument(
            '--padding',
            type=int,
            default=10,
            help='Padding adicional para el recorte (default: 10)'
        )
        parser.add_argument(
            '--validate-only',
            action='store_true',
            help='Solo validar dataset sin procesar imÃ¡genes'
        )
    
    def handle(self, *args, **options):
        """Maneja la ejecuciÃ³n del comando."""
        start_time = time.time()
        
        # Configurar parÃ¡metros
        confidence = options['conf']
        limit = options['limit']
        overwrite = options['overwrite']
        save_masks = options['save_masks']
        crop_size = options['crop_size']
        padding = options['padding']
        validate_only = options['validate_only']
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Iniciando procesamiento de crops de cacao con confianza {confidence}"
            )
        )
        
        # Debug info
        self.stdout.write(f"DEBUG: ParÃ¡metros - conf={confidence}, limit={limit}, overwrite={overwrite}")
        self.stdout.write(f"DEBUG: crop_size={crop_size}, padding={padding}, validate_only={validate_only}")
        
        try:
            # Inicializar cargador de dataset
            dataset_loader = CacaoDatasetLoader()
            
            # Validar dataset
            self.stdout.write("Validando dataset...")
            try:
                stats = dataset_loader.get_dataset_stats()
                self.stdout.write(
                    f"Dataset stats: {stats['total_records']} total, "
                    f"{stats['valid_records']} vÃ¡lidos, "
                    f"{stats['missing_images']} imÃ¡genes faltantes"
                )
                
                if stats['missing_images'] > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f"IDs con imÃ¡genes faltantes: {stats['missing_ids']}"
                        )
                    )
                
            except Exception as e:
                raise CommandError(f"Error validando dataset: {e}")
            
            if validate_only:
                self.stdout.write(
                    self.style.SUCCESS("ValidaciÃ³n completada. No se procesaron imÃ¡genes.")
                )
                return
            
            # Obtener registros vÃ¡lidos
            self.stdout.write("Obteniendo registros vÃ¡lidos...")
            valid_records = dataset_loader.get_valid_records()
            
            if not valid_records:
                raise CommandError("No se encontraron registros vÃ¡lidos para procesar")
            
            # Aplicar lÃ­mite si se especifica
            if limit > 0:
                valid_records = valid_records[:limit]
                self.stdout.write(f"Limitando procesamiento a {limit} imÃ¡genes")
            
            # Crear procesador de crops
            self.stdout.write("Inicializando procesador de crops...")
            try:
                self.stdout.write(f"DEBUG: Creando cropper con confidence={confidence}, crop_size={crop_size}")
                cropper = create_cacao_cropper(
                    confidence_threshold=confidence,
                    crop_size=crop_size,
                    padding=padding,
                    save_masks=save_masks,
                    overwrite=overwrite
                )
                self.stdout.write(f"DEBUG: Cropper creado exitosamente: {type(cropper)}")
            except Exception as e:
                self.stdout.write(f"DEBUG: Error creando cropper: {e}")
                raise CommandError(f"Error inicializando procesador: {e}")
            
            # Procesar imÃ¡genes
            self.stdout.write(f"Procesando {len(valid_records)} imÃ¡genes...")
            
            def progress_callback(current, total, result):
                if current % 10 == 0 or current == total:
                    status = "âœ“" if result.get('success', False) else "âœ—"
                    self.stdout.write(f"Procesadas {current}/{total} imÃ¡genes {status}")
            
            try:
                processing_stats = cropper.process_batch(
                    valid_records,
                    limit=0,  # Ya aplicamos el lÃ­mite arriba
                    progress_callback=progress_callback
                )
                
            except Exception as e:
                raise CommandError(f"Error durante el procesamiento: {e}")
            
            # Mostrar resultados
            end_time = time.time()
            processing_time = end_time - start_time
            
            self.stdout.write("\n" + "="*50)
            self.stdout.write("RESULTADOS DEL PROCESAMIENTO")
            self.stdout.write("="*50)
            self.stdout.write(f"Total de imÃ¡genes: {processing_stats['total']}")
            self.stdout.write(f"Procesadas: {processing_stats['processed']}")
            self.stdout.write(f"Exitosas: {processing_stats['successful']}")
            self.stdout.write(f"Fallidas: {processing_stats['failed']}")
            self.stdout.write(f"Saltadas: {processing_stats['skipped']}")
            
            success_rate = (
                processing_stats['successful'] / processing_stats['processed'] * 100
                if processing_stats['processed'] > 0 else 0
            )
            self.stdout.write(f"Tasa de Ã©xito: {success_rate:.2f}%")
            self.stdout.write(f"Tiempo total: {processing_time:.2f} segundos")
            
            if processing_stats['failed'] > 0:
                self.stdout.write("\nErrores encontrados:")
                for error in processing_stats['errors'][:10]:  # Mostrar solo los primeros 10
                    self.stdout.write(
                        self.style.ERROR(f"  ID {error['id']}: {error['error']}")
                    )
                if len(processing_stats['errors']) > 10:
                    self.stdout.write(
                        self.style.WARNING(f"  ... y {len(processing_stats['errors']) - 10} errores mÃ¡s")
                    )
            
            # Mostrar ubicaciÃ³n de archivos
            crops_dir = Path(settings.MEDIA_ROOT) / "cacao_images" / "crops"
            self.stdout.write(f"\nCrops guardados en: {crops_dir}")
            
            if save_masks:
                masks_dir = Path(settings.MEDIA_ROOT) / "cacao_images" / "masks"
                self.stdout.write(f"MÃ¡scaras guardadas en: {masks_dir}")
            
            # Mensaje final
            if processing_stats['failed'] == 0:
                self.stdout.write(
                    self.style.SUCCESS("Â¡Procesamiento completado exitosamente!")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"Procesamiento completado con {processing_stats['failed']} errores"
                    )
                )
            
        except CommandError:
            raise
        except Exception as e:
            raise CommandError(f"Error inesperado: {e}")


