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

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Iniciando calibración del dataset basada en píxeles...'))
        
        output_dir = Path(options['output-dir'])
        calibration_file = Path(options['calibration_file'])
        # Usar directamente la carpeta de crops (cacao_images/crops/{id}.png)
        processed_images_dir = get_crops_dir()
        ensure_dir_exists(output_dir)
        
        # Preparar registros existentes si el archivo ya existe
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
        
        # Cargar dataset
        try:
            dataset_loader = CacaoDatasetLoader()
            df = dataset_loader.load_dataset()
            valid_df, missing_ids = dataset_loader.validate_images_exist(df)
            total_valid_images = len(valid_df)
            self.stdout.write(f'📊 Dataset cargado: {total_valid_images} imágenes válidas')
        except Exception as e:
            raise CommandError(f'Error cargando dataset: {e}')
        
        calibration_data = []
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        # --- USAR EL BACKEND DE SEGMENTACIÓN ---
        seg_method = options['segmentation_backend']
        if seg_method == 'auto':
            seg_method = 'ai' # 'auto' debe usar la cascada 'ai' (U-Net -> rembg)
        
        # Detectar y mostrar dispositivo (GPU/CPU) si se usa AI
        if seg_method == 'ai':
            try:
                import torch
                if torch.cuda.is_available():
                    device_name = torch.cuda.get_device_name(0)
                    memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                    self.stdout.write(f"🚀 Usando GPU: {device_name} ({memory_gb:.1f} GB)")
                else:
                    self.stdout.write(f"🖥️  Usando CPU (GPU no disponible)")
            except ImportError:
                self.stdout.write(f"⚠️  PyTorch no disponible, usando CPU")
        
        self.stdout.write(f"📸 Backend de segmentación: {seg_method}")
        
        for idx, row in valid_df.iterrows():
            if max_images and processed_count >= max_images:
                break

            image_id = int(row['id'])
            record_info = valid_records_map.get(image_id)
            if not record_info:
                self.stdout.write(self.style.ERROR(f'  ❌ Registro {image_id} no encontrado en dataset_loader.get_valid_records()'))
                error_count += 1
                continue

            image_path = Path(record_info['raw_image_path'])
            image_filename = image_path.name
            if not image_path.exists():
                self.stdout.write(self.style.WARNING(f'  [WARN] Imagen no encontrada: {image_path.name}'))
                error_count += 1
                continue
            
            # Verificar si ya está procesada (en carpeta de crops por ID)
            processed_png_path = get_crop_image_path(image_id)
            if options['skip_existing'] and processed_png_path.exists():
                existing_record = existing_records.get(image_id)
                if existing_record:
                    calibration_data.append(existing_record)
                    skipped_count += 1

                    existing_processed_path = existing_records[image_id].get('processed_image_path')
                    if existing_processed_path and not processed_png_path.exists():
                        existing_processed_path = Path(existing_processed_path)
                        if existing_processed_path.exists():
                            ensure_dir_exists(processed_png_path.parent)
                            try:
                                shutil.copy2(existing_processed_path, processed_png_path)
                            except Exception:
                                pass
                    continue

                with Image.open(image_path) as original_image:
                    original_pixels_total = original_image.width * original_image.height

                confidence = 0.0
                try:
                    png_path_str = segment_and_crop_cacao_bean(str(image_path), method=seg_method)
                    if not png_path_str:
                        raise SegmentationError('Segmentación no devolvió ruta de imagen')
                    crop_path = Path(png_path_str)
                    if not crop_path.exists():
                        raise Exception(f"Imagen segmentada no encontrada: {crop_path}")
                    
                    # Cargar imagen segmentada (PNG con alpha)
                    crop_image = Image.open(crop_path)
                    # Guardar/actualizar PNG en carpeta de crops con nombre por ID
                    processed_png_path = get_crop_image_path(image_id)
                    ensure_dir_exists(processed_png_path.parent)
                    crop_image.save(processed_png_path)
                    confidence = 0.95  # Alta confianza si segment_and_crop_cacao_bean funcionó
                    
                except Exception as seg_error:
                    # Fallback: usar cropper directamente si segment_and_crop_cacao_bean falla
                    self.stdout.write(self.style.WARNING(f'  [WARN] Fallback a cropper para {image_id}: {seg_error}'))
                    
                    from ml.segmentation.cropper import create_cacao_cropper
                    cropper = create_cacao_cropper()
                    crop_result = cropper.process_image(
                        image_path,
                        image_id=image_id,
                        force_process=True
                    )
                    
                    if not crop_result.get('success', False):
                        raise Exception(f"Segmentación falló: {crop_result.get('error', 'Error desconocido')}")
                    
                    crop_path_str = crop_result.get('crop_path')
                    if not crop_path_str:
                        raise Exception("No se obtuvo ruta de imagen segmentada")
                    
                    crop_path = Path(crop_path_str)
                    if not crop_path.exists():
                        raise Exception(f"Imagen segmentada no encontrada: {crop_path}")
                    
                    crop_image = Image.open(crop_path)
                    # El cropper ya guarda en cacao_images/crops/{id}.png, pero
                    # aseguramos processed_png_path apuntando allí
                    processed_png_path = get_crop_image_path(image_id)
                    confidence = crop_result.get('confidence', 0.0)
            
            if crop_image is None:
                raise Exception("No se pudo segmentar la imagen")
            
            # Medir píxeles del grano (sin fondo)
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
            
            # Datos reales del CSV
            alto_real = float(row['alto'])
            ancho_real = float(row['ancho'])
            grosor_real = float(row['grosor'])
            peso_real = float(row['peso'])
            
            # Calcular factores de escala (píxeles → mm)
            scale_factor_alto = alto_real / height_pixels if height_pixels > 0 else 0
            scale_factor_ancho = ancho_real / width_pixels if width_pixels > 0 else 0
            scale_factor_promedio = (scale_factor_alto + scale_factor_ancho) / 2 if (height_pixels > 0 and width_pixels > 0) else 0
            
            background_pixels = original_pixels_total - grain_area_pixels
            background_ratio = background_pixels / original_pixels_total if original_pixels_total > 0 else 0
            
            # Crear registro de calibración
            calibration_record = {
                'id': image_id,
                'filename': image_path.name,
                'original_image_path': str(image_path),
                'processed_image_path': str(processed_png_path),
                'real_dimensions': {
                    'alto_mm': alto_real,
                    'ancho_mm': ancho_real,
                    'grosor_mm': grosor_real,
                    'peso_g': peso_real
                },
                'pixel_measurements': {
                    'grain_area_pixels': grain_area_pixels,
                    'width_pixels': width_pixels,
                    'height_pixels': height_pixels,
                    'bbox_area_pixels': width_pixels * height_pixels,
                    'aspect_ratio': width_pixels / height_pixels if height_pixels > 0 else 0
                },
                'background_info': {
                    'original_total_pixels': original_pixels_total,
                    'background_pixels': background_pixels,
                    'background_ratio': float(background_ratio)
                },
                'scale_factors': {
                    'alto_mm_per_pixel': float(scale_factor_alto),
                    'ancho_mm_per_pixel': float(scale_factor_ancho),
                    'average_mm_per_pixel': float(scale_factor_promedio)
                },
                'segmentation_confidence': float(confidence)
            }
            
            calibration_data.append(calibration_record)
            processed_count += 1
            
            if processed_count % 10 == 0:
                self.stdout.write(f'  ✅ Procesadas: {processed_count} imágenes...')
        
        # Guardar archivo de calibración
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
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Calibración completada!'))
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
        
        # Mostrar estadísticas
        stats = calibration_dict['statistics']
        self.stdout.write(f'\n📈 Estadísticas de calibración:')
        if stats and 'scale_factors' in stats and stats.get('scale_factors', {}).get('mean', 0) > 0:
            self.stdout.write(f'   Factor escala promedio: {stats["scale_factors"]["mean"]:.6f} mm/píxel')
            self.stdout.write(f'   Factor escala std: {stats["scale_factors"]["std"]:.6f} mm/píxel')
            self.stdout.write(f'   Rango: {stats["scale_factors"]["min"]:.6f} - {stats["scale_factors"]["max"]:.6f} mm/píxel')
        else:
            self.stdout.write('   Sin estadísticas (no se procesaron imágenes en esta ejecución o los datos son inválidos).')
    
    def _calculate_calibration_statistics(self, calibration_data):
        """Calcula estadísticas agregadas de la calibración."""
        if not calibration_data:
            return {}
        
        # Factores de escala
        scale_factors = [
            record['scale_factors']['average_mm_per_pixel']
            for record in calibration_data
            if 'scale_factors' in record and record['scale_factors']['average_mm_per_pixel'] > 0
        ]
        
        # Dimensiones en píxeles
        pixel_heights = [r['pixel_measurements']['height_pixels'] for r in calibration_data if 'pixel_measurements' in r]
        pixel_widths = [r['pixel_measurements']['width_pixels'] for r in calibration_data if 'pixel_measurements' in r]
        pixel_areas = [r['pixel_measurements']['grain_area_pixels'] for r in calibration_data if 'pixel_measurements' in r]
        
        # Dimensiones reales
        real_heights = [r['real_dimensions']['alto_mm'] for r in calibration_data if 'real_dimensions' in r]
        real_widths = [r['real_dimensions']['ancho_mm'] for r in calibration_data if 'real_dimensions' in r]
        real_weights = [r['real_dimensions']['peso_g'] for r in calibration_data if 'real_dimensions' in r]
        
        stats = {
            'scale_factors': {
                'mean': float(np.mean(scale_factors)) if scale_factors else 0,
                'std': float(np.std(scale_factors)) if scale_factors else 0,
                'min': float(np.min(scale_factors)) if scale_factors else 0,
                'max': float(np.max(scale_factors)) if scale_factors else 0,
                'median': float(np.median(scale_factors)) if scale_factors else 0
            },
            'pixel_dimensions': {
                'height': {
                    'mean': float(np.mean(pixel_heights)) if pixel_heights else 0,
                    'std': float(np.std(pixel_heights)) if pixel_heights else 0,
                    'min': int(np.min(pixel_heights)) if pixel_heights else 0,
                    'max': int(np.max(pixel_heights)) if pixel_heights else 0
                },
                'width': {
                    'mean': float(np.mean(pixel_widths)) if pixel_widths else 0,
                    'std': float(np.std(pixel_widths)) if pixel_widths else 0,
                    'min': int(np.min(pixel_widths)) if pixel_widths else 0,
                    'max': int(np.max(pixel_widths)) if pixel_widths else 0
                },
                'area': {
                    'mean': float(np.mean(pixel_areas)) if pixel_areas else 0,
                    'std': float(np.std(pixel_areas)) if pixel_areas else 0,
                    'min': int(np.min(pixel_areas)) if pixel_areas else 0,
                    'max': int(np.max(pixel_areas)) if pixel_areas else 0
                }
            },
            'real_dimensions': {
                'alto': {
                    'mean': float(np.mean(real_heights)) if real_heights else 0,
                    'std': float(np.std(real_heights)) if real_heights else 0,
                    'min': float(np.min(real_heights)) if real_heights else 0,
                    'max': float(np.max(real_heights)) if real_heights else 0
                },
                'ancho': {
                    'mean': float(np.mean(real_widths)) if real_widths else 0,
                    'std': float(np.std(real_widths)) if real_widths else 0,
                    'min': float(np.min(real_widths)) if real_widths else 0,
                    'max': float(np.max(real_widths)) if real_widths else 0
                },
                'peso': {
                    'mean': float(np.mean(real_weights)) if real_weights else 0,
                    'std': float(np.std(real_weights)) if real_weights else 0,
                    'min': float(np.min(real_weights)) if real_weights else 0,
                    'max': float(np.max(real_weights)) if real_weights else 0
                }
            }
        }
        
        return stats