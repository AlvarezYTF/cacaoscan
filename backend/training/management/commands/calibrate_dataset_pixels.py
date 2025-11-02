"""
Comando para calibrar el dataset basándose en mediciones directas de píxeles.

Proceso:
1. Lee todas las imágenes .bmp del directorio raw
2. Para cada imagen que existe en el CSV:
   - Segmenta (quita fondo)
   - Mide píxeles del grano (área, ancho, alto)
   - Guarda imagen segmentada en PNG
   - Calcula factores de escala usando datos reales del CSV
3. Guarda todo en un archivo de calibración JSON
4. Usa esas relaciones para mejorar entrenamiento y predicción
"""
import os
import sys
import json
import numpy as np
from pathlib import Path
from PIL import Image
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# Importar utilidades de ML
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from ml.data.dataset_loader import CacaoDatasetLoader
from ml.prediction.predict import CacaoPredictor
from ml.utils.paths import get_raw_images_dir, ensure_dir_exists
from ml.utils.logs import get_ml_logger

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
            help='Saltar imágenes ya procesadas'
        )
        parser.add_argument(
            '--max-images',
            type=int,
            default=None,
            help='Máximo número de imágenes a procesar (para pruebas)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔧 Iniciando calibración del dataset basada en píxeles...'))
        
        # Directorios
        output_dir = Path(options['output_dir'])
        calibration_file = Path(options['calibration_file'])
        processed_images_dir = output_dir / 'processed_png'
        ensure_dir_exists(output_dir)
        ensure_dir_exists(processed_images_dir)
        
        # Cargar dataset
        try:
            dataset_loader = CacaoDatasetLoader()
            df = dataset_loader.load_dataset()
            valid_df, missing_ids = dataset_loader.validate_images_exist(df)
            self.stdout.write(f'📊 Dataset cargado: {len(valid_df)} imágenes válidas')
        except Exception as e:
            raise CommandError(f'Error cargando dataset: {e}')
        
        # Función de segmentación se carga dinámicamente cuando se necesita
        
        # Procesar cada imagen
        calibration_data = []
        raw_images_dir = get_raw_images_dir()
        
        max_images = options['max_images']
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        for idx, row in valid_df.iterrows():
            if max_images and processed_count >= max_images:
                break
            
            image_id = int(row['id'])
            image_filename = row.get('filename', f'{image_id}.bmp')
            image_path = raw_images_dir / image_filename
            
            if not image_path.exists():
                self.stdout.write(self.style.WARNING(f'  ⚠️ Imagen no encontrada: {image_filename}'))
                error_count += 1
                continue
            
            # Verificar si ya está procesada
            processed_png_path = processed_images_dir / f'{image_id}.png'
            if options['skip_existing'] and processed_png_path.exists():
                skipped_count += 1
                continue
            
            try:
                # Cargar imagen original para medir píxeles totales
                image = Image.open(image_path).convert('RGB')
                original_pixels_total = image.width * image.height
                
                # Segmentar (quitar fondo) usando función existente
                from ml.segmentation.processor import segment_and_crop_cacao_bean
                
                try:
                    # Usar función existente que convierte BMP → PNG segmentado
                    png_path_str = segment_and_crop_cacao_bean(str(image_path), method="ai")
                    
                    if not png_path_str:
                        raise Exception("Segmentación no devolvió ruta de imagen")
                    
                    crop_path = Path(png_path_str)
                    if not crop_path.exists():
                        raise Exception(f"Imagen segmentada no encontrada: {crop_path}")
                    
                    # Cargar imagen segmentada (PNG con alpha)
                    crop_image = Image.open(crop_path)
                    confidence = 0.95  # Alta confianza si segment_and_crop_cacao_bean funcionó
                    
                except Exception as seg_error:
                    # Fallback: usar cropper directamente si segment_and_crop_cacao_bean falla
                    self.stdout.write(self.style.WARNING(f'  ⚠️ Fallback a cropper para {image_id}: {seg_error}'))
                    
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
                    confidence = crop_result.get('confidence', 0.0)
                
                if crop_image is None:
                    raise Exception("No se pudo segmentar la imagen")
                
                # Medir píxeles del grano (sin fondo)
                crop_array = np.array(crop_image)
                if crop_array.shape[2] == 4:  # RGBA
                    alpha = crop_array[:, :, 3]
                    mask = (alpha > 128).astype(np.uint8)
                else:
                    # Si no tiene alpha, toda la imagen es el grano
                    mask = np.ones(crop_array.shape[:2], dtype=np.uint8) * 255
                
                # Área del grano en píxeles
                grain_area_pixels = int(np.sum(mask > 0))
                
                # Bounding box del grano
                y_coords, x_coords = np.where(mask > 0)
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
                
                # Copiar imagen procesada al directorio de calibración (ya está en PNG)
                # Si el crop_image viene de segment_and_crop_cacao_bean, ya está guardado
                # Solo necesitamos copiarlo o referenciarlo
                processed_png_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Si la imagen procesada ya existe en otro lugar, copiarla
                if crop_path != processed_png_path and crop_path.exists():
                    from shutil import copy2
                    copy2(crop_path, processed_png_path)
                else:
                    # Si no existe, guardarla directamente
                    crop_image.save(processed_png_path, 'PNG')
                
                # Píxeles eliminados (fondo)
                background_pixels = original_pixels_total - grain_area_pixels
                background_ratio = background_pixels / original_pixels_total if original_pixels_total > 0 else 0
                
                # Crear registro de calibración
                calibration_record = {
                    'id': image_id,
                    'filename': image_filename,
                    'original_image_path': str(image_path),
                    'processed_image_path': str(processed_png_path),
                    # Datos reales (del CSV)
                    'real_dimensions': {
                        'alto_mm': alto_real,
                        'ancho_mm': ancho_real,
                        'grosor_mm': grosor_real,
                        'peso_g': peso_real
                    },
                    # Medidas en píxeles (después de quitar fondo)
                    'pixel_measurements': {
                        'grain_area_pixels': grain_area_pixels,
                        'width_pixels': width_pixels,
                        'height_pixels': height_pixels,
                        'bbox_area_pixels': width_pixels * height_pixels,
                        'aspect_ratio': width_pixels / height_pixels if height_pixels > 0 else 0
                    },
                    # Píxeles eliminados (fondo)
                    'background_info': {
                        'original_total_pixels': original_pixels_total,
                        'background_pixels': background_pixels,
                        'background_ratio': float(background_ratio)
                    },
                    # Factores de escala calculados
                    'scale_factors': {
                        'alto_mm_per_pixel': float(scale_factor_alto),
                        'ancho_mm_per_pixel': float(scale_factor_ancho),
                        'average_mm_per_pixel': float(scale_factor_promedio)
                    },
                    # Confianza de segmentación
                    'segmentation_confidence': float(confidence)
                }
                
                calibration_data.append(calibration_record)
                processed_count += 1
                
                if processed_count % 10 == 0:
                    self.stdout.write(f'  ✅ Procesadas: {processed_count} imágenes...')
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  ❌ Error procesando {image_filename}: {e}'))
                error_count += 1
                continue
        
        # Guardar archivo de calibración
        calibration_dict = {
            'total_images': len(calibration_data),
            'processed_count': processed_count,
            'skipped_count': skipped_count,
            'error_count': error_count,
            'calibration_records': calibration_data,
            # Estadísticas agregadas
            'statistics': self._calculate_calibration_statistics(calibration_data)
        }
        
        calibration_file.parent.mkdir(parents=True, exist_ok=True)
        with open(calibration_file, 'w', encoding='utf-8') as f:
            json.dump(calibration_dict, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Calibración completada!'))
        self.stdout.write(f'   📊 Total procesadas: {processed_count}')
        self.stdout.write(f'   ⏭️  Saltadas: {skipped_count}')
        self.stdout.write(f'   ❌ Errores: {error_count}')
        self.stdout.write(f'   💾 Archivo de calibración: {calibration_file}')
        self.stdout.write(f'   📁 Imágenes procesadas: {processed_images_dir}')
        
        # Mostrar estadísticas
        stats = calibration_dict['statistics']
        self.stdout.write(f'\n📈 Estadísticas de calibración:')
        self.stdout.write(f'   Factor escala promedio: {stats["scale_factors"]["mean"]:.6f} mm/píxel')
        self.stdout.write(f'   Factor escala std: {stats["scale_factors"]["std"]:.6f} mm/píxel')
        self.stdout.write(f'   Rango: {stats["scale_factors"]["min"]:.6f} - {stats["scale_factors"]["max"]:.6f} mm/píxel')
    
    def _calculate_calibration_statistics(self, calibration_data):
        """Calcula estadísticas agregadas de la calibración."""
        if not calibration_data:
            return {}
        
        # Factores de escala
        scale_factors = [
            record['scale_factors']['average_mm_per_pixel']
            for record in calibration_data
            if record['scale_factors']['average_mm_per_pixel'] > 0
        ]
        
        # Dimensiones en píxeles
        pixel_heights = [r['pixel_measurements']['height_pixels'] for r in calibration_data]
        pixel_widths = [r['pixel_measurements']['width_pixels'] for r in calibration_data]
        pixel_areas = [r['pixel_measurements']['grain_area_pixels'] for r in calibration_data]
        
        # Dimensiones reales
        real_heights = [r['real_dimensions']['alto_mm'] for r in calibration_data]
        real_widths = [r['real_dimensions']['ancho_mm'] for r in calibration_data]
        real_weights = [r['real_dimensions']['peso_g'] for r in calibration_data]
        
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
                    'mean': float(np.mean(pixel_heights)),
                    'std': float(np.std(pixel_heights)),
                    'min': int(np.min(pixel_heights)),
                    'max': int(np.max(pixel_heights))
                },
                'width': {
                    'mean': float(np.mean(pixel_widths)),
                    'std': float(np.std(pixel_widths)),
                    'min': int(np.min(pixel_widths)),
                    'max': int(np.max(pixel_widths))
                },
                'area': {
                    'mean': float(np.mean(pixel_areas)),
                    'std': float(np.std(pixel_areas)),
                    'min': int(np.min(pixel_areas)),
                    'max': int(np.max(pixel_areas))
                }
            },
            'real_dimensions': {
                'alto': {
                    'mean': float(np.mean(real_heights)),
                    'std': float(np.std(real_heights)),
                    'min': float(np.min(real_heights)),
                    'max': float(np.max(real_heights))
                },
                'ancho': {
                    'mean': float(np.mean(real_widths)),
                    'std': float(np.std(real_widths)),
                    'min': float(np.min(real_widths)),
                    'max': float(np.max(real_widths))
                },
                'peso': {
                    'mean': float(np.mean(real_weights)),
                    'std': float(np.std(real_weights)),
                    'min': float(np.min(real_weights)),
                    'max': float(np.max(real_weights))
                }
            }
        }
        
        return stats

