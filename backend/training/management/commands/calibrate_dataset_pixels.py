"""
Comando para calibrar el dataset basándose en mediciones directas de píxeles.
ACTUALIZADO:
- Corregida la lógica de '--skip-existing' para que cargue y reutilice
  correctamente los datos de un JSON existente, evitando el 'KeyError'.
- Corregido el 'SyntaxError' reestructurando los bloques try/except.
- Llama a la cascada de segmentación (rembg/opencv) directamente.
"""
import os
import sys
import json
import numpy as np
import shutil
from pathlib import Path
from PIL import Image
from django.core.management.base import BaseCommand, CommandError

# Asegurar que el path del proyecto esté configurado
project_root = Path(__file__).resolve().parents[4] # Sube 4 niveles
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
import django
try:
    django.setup()
    from django.conf import settings
    MEDIA_ROOT = Path(settings.MEDIA_ROOT)
except Exception as e:
    print(f"Warning: Django setup failed (normal if not in Django context). Error: {e}")
    MEDIA_ROOT = project_root / "media" # Fallback

from ml.data.dataset_loader import CacaoDatasetLoader
from ml.utils.paths import (
    get_raw_images_dir,
    ensure_dir_exists,
    get_datasets_dir,
    get_crop_image_path,
    get_crops_dir,
)
from ml.utils.logs import get_ml_logger
# Importar el procesador de segmentación que SÍ funciona (rembg/opencv)
from ml.segmentation.processor import segment_and_crop_cacao_bean, SegmentationError

logger = get_ml_logger("cacaoscan.training.calibrate")


class Command(BaseCommand):
    help = 'Calibra el dataset procesando imágenes, midiendo píxeles y creando relaciones píxeles→mm'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='media/datasets/calibration',
            help='Directorio para guardar imágenes procesadas y calibración'
        )
        parser.add_argument(
            '--calibration-file',
            type=str,
            default='media/datasets/pixel_calibration.json',
            help='Archivo JSON donde guardar la calibración'
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Saltar imágenes ya procesadas (reutiliza JSON existente si es válido)'
        )
        parser.add_argument(
            '--max-images',
            type=int,
            default=None,
            help='Máximo número de imágenes a procesar (para pruebas)'
        )
        parser.add_argument(
            '--segmentation-backend',
            type=str,
            default='ai',
            choices=['ai', 'opencv'],
            help="Backend para quitar fondo: 'ai' (U-Net/rembg) o 'opencv' (GrabCut)"
        )

    def _load_existing_records(self, calibration_file):
        """Load existing calibration records from file."""
        existing_records = {}
        if calibration_file.exists():
            try:
                with open(calibration_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                for record in existing_data.get('calibration_records', []):
                    existing_records[record['id']] = record
                self.stdout.write(f'📚 Cargados {len(existing_records)} registros de calibración existentes')
            except Exception as e:
                logger.warning(f'No se pudo cargar calibración existente: {e}')
        return existing_records
    
    def _load_dataset(self):
        """Load and validate dataset."""
        dataset_loader = CacaoDatasetLoader()
        df = dataset_loader.load_dataset()
        valid_df, _ = dataset_loader.validate_images_exist(df)
        self.stdout.write(f'📊 Dataset cargado: {len(valid_df)} imágenes válidas')
        return dataset_loader, valid_df
    
    def _setup_segmentation_method(self, seg_method):
        """Setup and display segmentation method info."""
        if seg_method == 'auto':
            seg_method = 'ai'
        
        if seg_method == 'ai':
            try:
                import torch
                if torch.cuda.is_available():
                    device_name = torch.cuda.get_device_name(0)
                    memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    self.stdout.write(f"🚀 Usando GPU: {device_name} ({memory_gb:.1f} GB)")
                else:
                    self.stdout.write("🖥️  Usando CPU (GPU no disponible)")
            except ImportError:
                self.stdout.write("⚠️  PyTorch no disponible, usando CPU")
        
        self.stdout.write(f"📸 Backend de segmentación: {seg_method}")
        return seg_method
    
    def _handle_existing_image(self, image_id, existing_records, processed_png_path):
        """Handle case when image is already processed."""
        existing_record = existing_records.get(image_id)
        if existing_record:
            existing_processed_path = existing_record.get('processed_image_path')
            if existing_processed_path and not processed_png_path.exists():
                existing_processed_path = Path(existing_processed_path)
                if existing_processed_path.exists():
                    ensure_dir_exists(processed_png_path.parent)
                    try:
                        shutil.copy2(existing_processed_path, processed_png_path)
                    except Exception:
                        pass
            return existing_record
        return None
    
    def _segment_image_primary(self, image_path, seg_method, image_id):
        """Primary segmentation method using segment_and_crop_cacao_bean."""
        png_path_str = segment_and_crop_cacao_bean(str(image_path), method=seg_method)
        if not png_path_str:
            raise SegmentationError('Segmentación no devolvió ruta de imagen')
        
        crop_path = Path(png_path_str)
        if not crop_path.exists():
            raise SegmentationError(f"Imagen segmentada no encontrada: {crop_path}")
        
        crop_image = Image.open(crop_path)
        processed_png_path = get_crop_image_path(image_id)
        ensure_dir_exists(processed_png_path.parent)
        crop_image.save(processed_png_path)
        
        return crop_image, processed_png_path, 0.95
    
    def _segment_image_fallback(self, image_path, image_id):
        """Fallback segmentation method using cropper."""
        from ml.segmentation.cropper import create_cacao_cropper
        cropper = create_cacao_cropper()
        crop_result = cropper.process_image(
            image_path,
            image_id=image_id,
            force_process=True
        )
        
        if not crop_result.get('success', False):
            raise SegmentationError(f"Segmentación falló: {crop_result.get('error', 'Error desconocido')}")
        
        crop_path_str = crop_result.get('crop_path')
        if not crop_path_str:
            raise SegmentationError("No se obtuvo ruta de imagen segmentada")
        
        crop_path = Path(crop_path_str)
        if not crop_path.exists():
            raise SegmentationError(f"Imagen segmentada no encontrada: {crop_path}")
        
        crop_image = Image.open(crop_path)
        processed_png_path = get_crop_image_path(image_id)
        confidence = crop_result.get('confidence', 0.0)
        
        return crop_image, processed_png_path, confidence
    
    def _segment_image(self, image_path, seg_method, image_id):
        """Segment image using primary or fallback method."""
        try:
            return self._segment_image_primary(image_path, seg_method, image_id)
        except Exception as seg_error:
            self.stdout.write(self.style.WARNING(f'  [WARN] Fallback a cropper para {image_id}: {seg_error}'))
            return self._segment_image_fallback(image_path, image_id)
    
    def _measure_pixels(self, crop_image, original_pixels_total):
        """Measure pixel dimensions from segmented image."""
        crop_array = np.array(crop_image)
        if crop_array.shape[2] == 4:  # RGBA
            alpha = crop_array[:, :, 3]
            mask = (alpha > 128).astype(np.uint8)
        else:
            mask = np.ones(crop_array.shape[:2], dtype=np.uint8) * 255
        
        grain_area_pixels = int(np.sum(mask > 0))
        
        y_coords, x_coords = np.nonzero(mask > 0)
        if len(x_coords) > 0:
            width_pixels = int(x_coords.max() - x_coords.min() + 1)
            height_pixels = int(y_coords.max() - y_coords.min() + 1)
        else:
            width_pixels = crop_image.width
            height_pixels = crop_image.height
        
        background_pixels = original_pixels_total - grain_area_pixels
        background_ratio = background_pixels / original_pixels_total if original_pixels_total > 0 else 0
        
        return {
            'grain_area_pixels': grain_area_pixels,
            'width_pixels': width_pixels,
            'height_pixels': height_pixels,
            'background_pixels': background_pixels,
            'background_ratio': background_ratio
        }
    
    def _calculate_scale_factors(self, pixel_measurements, real_dimensions):
        """Calculate scale factors from pixels to millimeters."""
        height_pixels = pixel_measurements['height_pixels']
        width_pixels = pixel_measurements['width_pixels']
        alto_real = real_dimensions['alto']
        ancho_real = real_dimensions['ancho']
        
        scale_factor_alto = alto_real / height_pixels if height_pixels > 0 else 0
        scale_factor_ancho = ancho_real / width_pixels if width_pixels > 0 else 0
        scale_factor_promedio = (scale_factor_alto + scale_factor_ancho) / 2 if (height_pixels > 0 and width_pixels > 0) else 0
        
        return {
            'alto_mm_per_pixel': float(scale_factor_alto),
            'ancho_mm_per_pixel': float(scale_factor_ancho),
            'average_mm_per_pixel': float(scale_factor_promedio)
        }
    
    def _create_calibration_record(self, image_id, image_path, processed_png_path, pixel_measurements, 
                                   real_dimensions, scale_factors, original_pixels_total, confidence):
        """Create calibration record dictionary."""
        return {
            'id': image_id,
            'filename': image_path.name,
            'original_image_path': str(image_path),
            'processed_image_path': str(processed_png_path),
            'real_dimensions': {
                'alto_mm': real_dimensions['alto'],
                'ancho_mm': real_dimensions['ancho'],
                'grosor_mm': real_dimensions['grosor'],
                'peso_g': real_dimensions['peso']
            },
            'pixel_measurements': {
                'grain_area_pixels': pixel_measurements['grain_area_pixels'],
                'width_pixels': pixel_measurements['width_pixels'],
                'height_pixels': pixel_measurements['height_pixels'],
                'bbox_area_pixels': pixel_measurements['width_pixels'] * pixel_measurements['height_pixels'],
                'aspect_ratio': pixel_measurements['width_pixels'] / pixel_measurements['height_pixels'] if pixel_measurements['height_pixels'] > 0 else 0
            },
            'background_info': {
                'original_total_pixels': original_pixels_total,
                'background_pixels': pixel_measurements['background_pixels'],
                'background_ratio': float(pixel_measurements['background_ratio'])
            },
            'scale_factors': scale_factors,
            'segmentation_confidence': float(confidence)
        }
    
    def _process_single_image(self, image_id, image_path, row, seg_method, existing_records, options):
        """Process a single image and return calibration record."""
        processed_png_path = get_crop_image_path(image_id)
        
        if options['skip_existing'] and processed_png_path.exists():
            existing_record = self._handle_existing_image(image_id, existing_records, processed_png_path)
            if existing_record:
                return existing_record, True
        
        with Image.open(image_path) as original_image:
            original_pixels_total = original_image.width * original_image.height
        
        crop_image, processed_png_path, confidence = self._segment_image(image_path, seg_method, image_id)
        
        if crop_image is None:
            raise SegmentationError("No se pudo segmentar la imagen")
        
        pixel_measurements = self._measure_pixels(crop_image, original_pixels_total)
        
        real_dimensions = {
            'alto': float(row['alto']),
            'ancho': float(row['ancho']),
            'grosor': float(row['grosor']),
            'peso': float(row['peso'])
        }
        
        scale_factors = self._calculate_scale_factors(pixel_measurements, real_dimensions)
        
        calibration_record = self._create_calibration_record(
            image_id, image_path, processed_png_path, pixel_measurements,
            real_dimensions, scale_factors, original_pixels_total, confidence
        )
        
        return calibration_record, False
    
    def _save_calibration_file(self, calibration_file, calibration_data, processed_count, skipped_count, error_count):
        """Save calibration data to JSON file."""
        calibration_dict = {
            'total_images': len(calibration_data),
            'processed_count': processed_count,
            'skipped_count': skipped_count,
            'error_count': error_count,
            'calibration_records': calibration_data,
            'statistics': self._calculate_calibration_statistics(calibration_data)
        }
        
        calibration_file.parent.mkdir(parents=True, exist_ok=True)
        with open(calibration_file, 'w', encoding='utf-8') as f:
            json.dump(calibration_dict, f, indent=2, ensure_ascii=False)
        
        return calibration_dict
    
    def _print_summary(self, calibration_data, processed_count, skipped_count, error_count, 
                       calibration_file, processed_images_dir, valid_df, max_images):
        """Print calibration summary and statistics."""
        self.stdout.write(self.style.SUCCESS('\n✅ Calibración completada!'))
        self.stdout.write(f'   📊 Total registros en JSON: {len(calibration_data)}')
        self.stdout.write(f'   ✨ Nuevas procesadas: {processed_count}')
        self.stdout.write(f'   ⏭️  Saltadas/Reutilizadas: {skipped_count}')
        self.stdout.write(f'   ❌ Errores: {error_count}')
        self.stdout.write(f'   💾 Archivo de calibración: {calibration_file}')
        self.stdout.write(f'   📁 Imágenes procesadas: {processed_images_dir}')
        
        expected = len(valid_df) if max_images is None else min(max_images, len(valid_df))
        handled = processed_count + skipped_count + error_count
        if handled < expected:
            self.stdout.write(self.style.WARNING(
                f'⚠️ Calibración interrumpida ({handled}/{expected}). Relanza con --skip-existing para continuar.'
            ))
        
        stats = self._calculate_calibration_statistics(calibration_data)
        self.stdout.write('\n📈 Estadísticas de calibración:')
        if stats and 'scale_factors' in stats and stats.get('scale_factors', {}).get('mean', 0) > 0:
            self.stdout.write(f'   Factor escala promedio: {stats["scale_factors"]["mean"]:.6f} mm/píxel')
            self.stdout.write(f'   Factor escala std: {stats["scale_factors"]["std"]:.6f} mm/píxel')
            self.stdout.write(f'   Rango: {stats["scale_factors"]["min"]:.6f} - {stats["scale_factors"]["max"]:.6f} mm/píxel')
        else:
            self.stdout.write('   Sin estadísticas (no se procesaron imágenes en esta ejecución o los datos son inválidos).')
    
    def _validate_image_record(self, image_id, record_info, image_path):
        """Validate image record and path."""
        if not record_info:
            self.stdout.write(self.style.ERROR(f'  ❌ Registro {image_id} no encontrado'))
            return False
        if not image_path.exists():
            self.stdout.write(self.style.WARNING(f'  [WARN] Imagen no encontrada: {image_path.name}'))
            return False
        return True
    
    def _process_single_image_record(self, image_id, image_path, row, seg_method, existing_records, options):
        """Process single image record and return result."""
        try:
            calibration_record, was_skipped = self._process_single_image(
                image_id, image_path, row, seg_method, existing_records, options
            )
            return calibration_record, was_skipped, False
        except Exception as e:
            logger.error(f'Error procesando imagen {image_id}: {e}')
            return None, False, True
    
    def _handle_processed_image(self, calibration_record, was_skipped, processed_count):
        """Handle successfully processed image."""
        if was_skipped:
            return 0, 1, 0
        
        new_count = processed_count + 1
        if new_count % 10 == 0:
            self.stdout.write(f'  ✅ Procesadas: {new_count} imágenes...')
        return new_count, 0, 0
    
    def _process_single_row(self, row, valid_records_map, seg_method, existing_records, options):
        """Process a single row from dataframe."""
        image_id = int(row['id'])
        record_info = valid_records_map.get(image_id)
        if not record_info:
            self.stdout.write(self.style.ERROR(f'  ❌ Registro {image_id} no encontrado'))
            return None, None, True
        
        image_path = Path(record_info['raw_image_path'])
        if not image_path.exists():
            self.stdout.write(self.style.WARNING(f'  [WARN] Imagen no encontrada: {image_path.name}'))
            return None, None, True
        
        calibration_record, was_skipped, had_error = self._process_single_image_record(
            image_id, image_path, row, seg_method, existing_records, options
        )
        
        if had_error:
            return None, None, True
        
        return calibration_record, was_skipped, False
    
    def _process_images_loop(self, valid_df, valid_records_map, seg_method, existing_records, options, max_images):
        """Process all images in the loop."""
        calibration_data = []
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        for idx, row in valid_df.iterrows():
            if max_images and processed_count >= max_images:
                break

            calibration_record, was_skipped, had_error = self._process_single_row(
                row, valid_records_map, seg_method, existing_records, options
            )
            
            if had_error:
                error_count += 1
                continue
            
            calibration_data.append(calibration_record)
            processed_count, skipped_inc, _ = self._handle_processed_image(
                calibration_record, was_skipped, processed_count
            )
            skipped_count += skipped_inc
        
        return calibration_data, processed_count, skipped_count, error_count
    
    def handle(self, *args, **options):
        """Main handler for calibration command."""
        self.stdout.write(self.style.SUCCESS('🔧 Iniciando calibración del dataset basada en píxeles...'))
        
        output_dir = Path(options['output-dir'])
        calibration_file = Path(options['calibration_file'])
        processed_images_dir = get_crops_dir()
        ensure_dir_exists(output_dir)
        
        existing_records = self._load_existing_records(calibration_file)
        
        try:
            dataset_loader, valid_df = self._load_dataset()
        except Exception as e:
            raise CommandError(f'Error cargando dataset: {e}')
        
        max_images = options.get('max_images')
        
        try:
            valid_records = dataset_loader.get_valid_records()
            valid_records_map = {record['id']: record for record in valid_records}
        except Exception as e:
            raise CommandError(f'Error obteniendo registros válidos: {e}')
        
        seg_method = self._setup_segmentation_method(options['segmentation_backend'])
        
        calibration_data, processed_count, skipped_count, error_count = self._process_images_loop(
            valid_df, valid_records_map, seg_method, existing_records, options, max_images
        )
        
        self._save_calibration_file(
            calibration_file, calibration_data, processed_count, skipped_count, error_count
        )
        
        self._print_summary(
            calibration_data, processed_count, skipped_count, error_count,
            calibration_file, processed_images_dir, valid_df, max_images
        )
    
    def _calculate_basic_stats(self, values, use_int_min_max=False):
        """Calculate basic statistics for a list of values."""
        if not values:
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0}
        
        min_func = int if use_int_min_max else float
        return {
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': min_func(np.min(values)),
            'max': min_func(np.max(values))
        }
    
    def _calculate_scale_factor_stats(self, calibration_data):
        """Calculate statistics for scale factors."""
        scale_factors = [
            record['scale_factors']['average_mm_per_pixel']
            for record in calibration_data
            if 'scale_factors' in record and record['scale_factors']['average_mm_per_pixel'] > 0
        ]
        
        if not scale_factors:
            return {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'median': 0}
        
        stats = self._calculate_basic_stats(scale_factors)
        stats['median'] = float(np.median(scale_factors))
        return stats
    
    def _calculate_pixel_dimension_stats(self, calibration_data):
        """Calculate statistics for pixel dimensions."""
        pixel_heights = [r['pixel_measurements']['height_pixels'] for r in calibration_data if 'pixel_measurements' in r]
        pixel_widths = [r['pixel_measurements']['width_pixels'] for r in calibration_data if 'pixel_measurements' in r]
        pixel_areas = [r['pixel_measurements']['grain_area_pixels'] for r in calibration_data if 'pixel_measurements' in r]
        
        return {
            'height': self._calculate_basic_stats(pixel_heights, use_int_min_max=True),
            'width': self._calculate_basic_stats(pixel_widths, use_int_min_max=True),
            'area': self._calculate_basic_stats(pixel_areas, use_int_min_max=True)
        }
    
    def _calculate_real_dimension_stats(self, calibration_data):
        """Calculate statistics for real dimensions."""
        real_heights = [r['real_dimensions']['alto_mm'] for r in calibration_data if 'real_dimensions' in r]
        real_widths = [r['real_dimensions']['ancho_mm'] for r in calibration_data if 'real_dimensions' in r]
        real_weights = [r['real_dimensions']['peso_g'] for r in calibration_data if 'real_dimensions' in r]
        
        return {
            'alto': self._calculate_basic_stats(real_heights),
            'ancho': self._calculate_basic_stats(real_widths),
            'peso': self._calculate_basic_stats(real_weights)
        }
    
    def _calculate_calibration_statistics(self, calibration_data):
        """Calcula estadísticas agregadas de la calibración."""
        if not calibration_data:
            return {}
        
        return {
            'scale_factors': self._calculate_scale_factor_stats(calibration_data),
            'pixel_dimensions': self._calculate_pixel_dimension_stats(calibration_data),
            'real_dimensions': self._calculate_real_dimension_stats(calibration_data)
        }