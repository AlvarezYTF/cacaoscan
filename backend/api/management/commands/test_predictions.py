"""
Django management command to diagnose model predictions.
"""
import logging
import numpy as np
import torch
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from PIL import Image

logger = logging.getLogger("cacaoscan.management.test_predictions")


class Command(BaseCommand):
    help = 'Diagnostica las predicciones del modelo mostrando valores normalizados vs desnormalizados y comparación con valores reales.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--image-id',
            type=int,
            default=1,
            help='ID de la imagen en el dataset a usar para el diagnóstico (default: 1)'
        )

    def handle(self, *args, **options):
        image_id = options.get('image_id', 1)
        
        logger.info(f"Testing predictions with image_id={image_id}")
        
        try:
            from ml.prediction.predict import CacaoPredictor
            from ml.data.dataset_loader import CacaoDatasetLoader
        except ImportError as e:
            logger.error(f"Error importing ML modules: {e}", exc_info=True)
            raise CommandError(f'Error al importar módulos ML: {str(e)}')
        
        self.stdout.write("=" * 60)
        self.stdout.write("🔍 DIAGNÓSTICO DE PREDICCIONES")
        self.stdout.write("=" * 60)
        
        # Cargar predictor
        self.stdout.write("\n📦 Cargando predictor...")
        try:
            predictor = CacaoPredictor()
            if not predictor.load_artifacts():
                raise CommandError('No se pudieron cargar los artefactos del modelo')
            self.stdout.write(self.style.SUCCESS("✅ Predictor cargado exitosamente"))
            logger.info("Predictor loaded successfully")
        except Exception as e:
            logger.error(f"Error loading predictor: {e}", exc_info=True)
            raise CommandError(f'Error al cargar predictor: {str(e)}')
        
        # Buscar imagen por ID
        self.stdout.write(f"\n🔍 Buscando imagen con ID={image_id}...")
        try:
            loader = CacaoDatasetLoader()
            records = loader.get_valid_records()
            image_record = None
            
            for record in records:
                if record['id'] == image_id:
                    image_record = record
                    break
            
            if not image_record:
                raise CommandError(f'No se encontró imagen con ID={image_id} en el dataset')
            
            self.stdout.write(f"✅ Imagen encontrada: {image_record['image_path']}")
            self.stdout.write(f"\n📊 Valores reales del dataset:")
            self.stdout.write(f"  ALTO: {image_record.get('alto', 'N/A')}")
            self.stdout.write(f"  ANCHO: {image_record.get('ancho', 'N/A')}")
            self.stdout.write(f"  GROSOR: {image_record.get('grosor', 'N/A')}")
            self.stdout.write(f"  PESO: {image_record.get('peso', 'N/A')}")
            
        except Exception as e:
            logger.error(f"Error finding image: {e}", exc_info=True)
            raise CommandError(f'Error al buscar imagen: {str(e)}')
        
        # Cargar imagen
        try:
            image_path_str = str(image_record['image_path'])
            
            # Manejar rutas relativas correctamente
            if image_path_str.startswith('media') or image_path_str.startswith('media\\') or image_path_str.startswith('media/'):
                image_path = Path(image_path_str)
            else:
                image_path = Path('media') / image_path_str
            
            if not image_path.exists():
                # Intentar buscar en diferentes ubicaciones
                alternatives = [
                    Path('media') / image_path_str.replace('media\\', '').replace('media/', ''),
                    Path(image_path_str),
                    Path('media/cacao_images/raw') / Path(image_path_str).name,
                ]
                for alt in alternatives:
                    if alt.exists():
                        self.stdout.write(f"✅ Imagen encontrada en ubicación alternativa: {alt}")
                        image_path = alt
                        break
                else:
                    raise CommandError(f'Imagen no encontrada: {image_path}')
            
            self.stdout.write(f"\n🖼️  Cargando imagen: {image_path}")
            image = Image.open(image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            self.stdout.write(self.style.SUCCESS("✅ Imagen cargada exitosamente"))
            logger.info(f"Image loaded: {image_path}")
            
        except Exception as e:
            logger.error(f"Error loading image: {e}", exc_info=True)
            raise CommandError(f'Error al cargar imagen: {str(e)}')
        
        # Hacer predicción
        self.stdout.write("\n🤖 Haciendo predicción...")
        try:
            result = predictor.predict(image)
            
            self.stdout.write(f"\n📈 Predicciones desnormalizadas:")
            self.stdout.write(f"  alto_mm: {result['alto_mm']:.2f}")
            self.stdout.write(f"  ancho_mm: {result['ancho_mm']:.2f}")
            self.stdout.write(f"  grosor_mm: {result['grosor_mm']:.2f}")
            self.stdout.write(f"  peso_g: {result['peso_g']:.2f}")
            
            # Diagnóstico de escaladores
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("🔬 DIAGNÓSTICO DE ESCALADORES")
            self.stdout.write("=" * 60)
            
            for target in ['alto', 'ancho', 'grosor', 'peso']:
                try:
                    scaler = predictor.scalers.scalers[target]
                    self.stdout.write(f"\n{target.upper()}:")
                    self.stdout.write(f"  Mean: {scaler.mean_[0]:.4f}")
                    self.stdout.write(f"  Scale: {scaler.scale_[0]:.4f}")
                    
                    # Obtener predicción normalizada
                    model = predictor.regression_models[target]
                    image_tensor = predictor._preprocess_image(image)
                    with torch.no_grad():
                        pred_normalized = model(image_tensor).cpu().numpy().flatten()[0]
                    
                    self.stdout.write(f"  Predicción normalizada: {pred_normalized:.4f}")
                    
                    # Desnormalizar manualmente
                    pred_array = np.array([[pred_normalized]])
                    denorm = scaler.inverse_transform(pred_array)[0][0]
                    self.stdout.write(f"  Predicción desnormalizada (manual): {denorm:.4f}")
                    
                    # Valor real normalizado
                    real_value = image_record.get(target, None)
                    if real_value:
                        real_array = np.array([[real_value]])
                        real_normalized = scaler.transform(real_array)[0][0]
                        self.stdout.write(f"  Valor real: {real_value:.4f}")
                        self.stdout.write(f"  Valor real normalizado: {real_normalized:.4f}")
                        error = abs(denorm - real_value)
                        self.stdout.write(f"  Error: {error:.4f}")
                        
                except Exception as e:
                    logger.warning(f"Error processing target {target}: {e}")
                    self.stdout.write(self.style.WARNING(f"  ⚠️  Error procesando {target}: {e}"))
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("✅ DIAGNÓSTICO COMPLETADO"))
            self.stdout.write("=" * 60)
            logger.info("Diagnosis completed successfully")
            
        except Exception as e:
            logger.error(f"Error during prediction diagnosis: {e}", exc_info=True)
            raise CommandError(f'Error durante el diagnóstico: {str(e)}')

