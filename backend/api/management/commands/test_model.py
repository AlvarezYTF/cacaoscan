"""
Django management command to test the trained model with a specific image.
"""
import logging
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from PIL import Image

logger = logging.getLogger("cacaoscan.management.test_model")


class Command(BaseCommand):
    help = 'Prueba el modelo entrenado con una imagen específica. Puede usar un ID del dataset o una ruta de archivo.'

    def add_arguments(self, parser):
        parser.add_argument(
            'image_id',
            type=str,
            nargs='?',
            help='ID de la imagen en el dataset (ej: 497) o ruta a una imagen (ej: media/cacao_images/raw/497.bmp)'
        )
        parser.add_argument(
            '--image-path',
            type=str,
            help='Ruta directa a una imagen (alternativa a image_id)'
        )

    def handle(self, *args, **options):
        image_id = options.get('image_id')
        image_path = options.get('image_path')
        
        logger.info(f"Testing model with image_id={image_id}, image_path={image_path}")
        
        try:
            from ml.prediction.predict import CacaoPredictor
            from ml.data.dataset_loader import CacaoDatasetLoader
        except ImportError as e:
            logger.error(f"Error importing ML modules: {e}", exc_info=True)
            raise CommandError(f'Error al importar módulos ML: {str(e)}')
        
        self.stdout.write("=" * 60)
        self.stdout.write("🧪 PRUEBA DEL MODELO ENTRENADO")
        self.stdout.write("=" * 60)
        
        # Cargar predictor
        self.stdout.write("\n📦 Cargando predictor y artefactos...")
        try:
            predictor = CacaoPredictor()
            if not predictor.load_artifacts():
                raise CommandError('No se pudieron cargar los artefactos del modelo. Asegúrate de que el entrenamiento se completó correctamente.')
            self.stdout.write(self.style.SUCCESS("✅ Modelo cargado exitosamente"))
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}", exc_info=True)
            raise CommandError(f'Error al cargar el modelo: {str(e)}')
        
        # Determinar qué imagen usar
        image = None
        image_record = None
        final_image_path = None
        
        if image_path:
            final_image_path = Path(image_path)
        elif image_id:
            # Intentar como ID primero
            if image_id.isdigit():
                image_record, final_image_path = self._find_image_by_id(int(image_id))
            else:
                # Tratar como ruta
                final_image_path = Path(image_id)
        else:
            raise CommandError('Debes proporcionar image_id o --image-path. Usa --help para más información.')
        
        # Verificar que la imagen existe
        if not final_image_path or not final_image_path.exists():
            # Intentar diferentes extensiones
            if final_image_path:
                for ext in ['.bmp', '.png', '.jpg', '.jpeg']:
                    alt_path = final_image_path.with_suffix(ext)
                    if alt_path.exists():
                        final_image_path = alt_path
                        break
            
            if not final_image_path or not final_image_path.exists():
                raise CommandError(f'Imagen no encontrada: {final_image_path or "N/A"}')
        
        self.stdout.write(f"✅ Imagen encontrada: {final_image_path}")
        
        # Mostrar valores reales si están disponibles
        if image_record:
            self.stdout.write(f"\n📊 Valores reales del dataset:")
            self.stdout.write(f"   ALTO:   {image_record.get('alto', 'N/A')} mm")
            self.stdout.write(f"   ANCHO:  {image_record.get('ancho', 'N/A')} mm")
            self.stdout.write(f"   GROSOR: {image_record.get('grosor', 'N/A')} mm")
            self.stdout.write(f"   PESO:   {image_record.get('peso', 'N/A')} g")
        
        # Cargar imagen
        self.stdout.write(f"\n🖼️  Cargando imagen...")
        try:
            image = Image.open(final_image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            self.stdout.write(self.style.SUCCESS(f"✅ Imagen cargada: {image.size[0]}x{image.size[1]} pixels"))
            logger.info(f"Image loaded: {image.size}")
        except Exception as e:
            logger.error(f"Error loading image: {e}", exc_info=True)
            raise CommandError(f'Error al cargar imagen: {str(e)}')
        
        # Hacer predicción
        self.stdout.write(f"\n🤖 Ejecutando predicción...")
        try:
            result = predictor.predict(image)
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("📈 RESULTADOS DE LA PREDICCIÓN")
            self.stdout.write("=" * 60)
            self.stdout.write(f"\n   ALTO:   {result['alto_mm']:.2f} mm")
            self.stdout.write(f"   ANCHO:  {result['ancho_mm']:.2f} mm")
            self.stdout.write(f"   GROSOR: {result['grosor_mm']:.2f} mm")
            self.stdout.write(f"   PESO:   {result['peso_g']:.2f} g")
            
            # Mostrar confianzas si están disponibles
            if 'confidences' in result:
                self.stdout.write(f"\n📊 Confianzas:")
                confidences = result['confidences']
                self.stdout.write(f"   ALTO:   {confidences.get('alto', 0):.2%}")
                self.stdout.write(f"   ANCHO:  {confidences.get('ancho', 0):.2%}")
                self.stdout.write(f"   GROSOR: {confidences.get('grosor', 0):.2%}")
                self.stdout.write(f"   PESO:   {confidences.get('peso', 0):.2%}")
            
            # Comparar con valores reales si están disponibles
            if image_record:
                self.stdout.write(f"\n📊 Comparación con valores reales:")
                targets = ['alto', 'ancho', 'grosor', 'peso']
                for target in targets:
                    real = image_record.get(target)
                    if target == 'peso':
                        pred = result.get('peso_g')
                    else:
                        pred = result.get(f'{target}_mm')
                    
                    if real is not None:
                        error = abs(pred - real)
                        error_pct = (error / real) * 100 if real > 0 else 0
                        self.stdout.write(
                            f"   {target.upper():6s}: Real={real:6.2f}, Pred={pred:6.2f}, "
                            f"Error={error:6.2f} ({error_pct:5.1f}%)"
                        )
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("✅ Predicción completada exitosamente"))
            self.stdout.write("=" * 60)
            logger.info("Prediction completed successfully")
            
        except Exception as e:
            logger.error(f"Error during prediction: {e}", exc_info=True)
            raise CommandError(f'Error durante la predicción: {str(e)}')

    def _find_image_by_id(self, image_id: int) -> tuple:
        """Find image by ID in the dataset."""
        try:
            from ml.data.dataset_loader import CacaoDatasetLoader
            loader = CacaoDatasetLoader()
            records = loader.get_valid_records()
            
            for record in records:
                if record['id'] == image_id:
                    # Construir ruta de imagen
                    image_path_str = str(record['image_path'])
                    if image_path_str.startswith('media'):
                        image_path = Path(image_path_str)
                    else:
                        image_path = Path('media') / image_path_str
                    
                    # Intentar diferentes extensiones
                    if not image_path.exists():
                        for ext in ['.bmp', '.png', '.jpg', '.jpeg']:
                            alt_path = image_path.with_suffix(ext)
                            if alt_path.exists():
                                image_path = alt_path
                                break
                    
                    return record, image_path
            
            raise CommandError(f'No se encontró imagen con ID={image_id} en el dataset')
            
        except Exception as e:
            logger.error(f"Error finding image by ID: {e}", exc_info=True)
            raise CommandError(f'Error al buscar imagen por ID: {str(e)}')

