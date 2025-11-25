"""
Django management command to verify that training code correctly reads
images from raw directory and data from CSV.
"""
import logging
from django.core.management.base import BaseCommand, CommandError
from pathlib import Path
from ml.data.dataset_loader import CacaoDatasetLoader
from ml.utils.paths import get_raw_images_dir, get_datasets_dir

logger = logging.getLogger("cacaoscan.management.verify_training_data")


class Command(BaseCommand):
    help = 'Verifica que el código de entrenamiento lee correctamente las imágenes desde raw y los datos del CSV'

    def handle(self, *args, **options):
        logger.info("Verifying training data")
        self.stdout.write("=" * 60)
        self.stdout.write("VERIFICACIÓN DE DATOS PARA ENTRENAMIENTO")
        self.stdout.write("=" * 60)
        
        # 1. Verificar directorio de imágenes raw
        self.stdout.write("\n1. Verificando directorio de imágenes raw...")
        raw_dir = get_raw_images_dir()
        self.stdout.write(f"   Directorio raw: {raw_dir}")
        self.stdout.write(f"   Existe: {raw_dir.exists()}")
        
        bmp_files = []
        if raw_dir.exists():
            bmp_files = list(raw_dir.glob("*.bmp"))
            self.stdout.write(f"   Archivos .bmp encontrados: {len(bmp_files)}")
            if bmp_files:
                self.stdout.write(f"   Ejemplos: {[f.name for f in bmp_files[:5]]}")
        
        # 2. Verificar CSV
        self.stdout.write("\n2. Verificando archivo CSV...")
        datasets_dir = get_datasets_dir()
        csv_files = list(datasets_dir.glob("*.csv"))
        self.stdout.write(f"   Directorio datasets: {datasets_dir}")
        self.stdout.write(f"   Archivos CSV encontrados: {len(csv_files)}")
        for csv_file in csv_files:
            self.stdout.write(f"   - {csv_file.name}")
        
        # 3. Cargar dataset
        self.stdout.write("\n3. Cargando dataset...")
        try:
            loader = CacaoDatasetLoader()
            self.stdout.write(f"   CSV usado: {loader.csv_path}")
            
            df = loader.load_dataset()
            self.stdout.write(f"   Total registros en CSV: {len(df)}")
            self.stdout.write(f"   Columnas: {list(df.columns)}")
            self.stdout.write(f"\n   Primeros 5 registros:")
            self.stdout.write(str(df.head()[['id', 'alto', 'ancho', 'grosor', 'peso']]))
            
            # 4. Validar imágenes
            self.stdout.write("\n4. Validando existencia de imágenes...")
            valid_df, missing_ids = loader.validate_images_exist(df)
            self.stdout.write(f"   Imágenes válidas: {len(valid_df)}")
            self.stdout.write(f"   Imágenes faltantes: {len(missing_ids)}")
            
            if missing_ids:
                self.stdout.write(f"   IDs faltantes (primeros 10): {missing_ids[:10]}")
            
            if len(valid_df) > 0:
                self.stdout.write(f"\n   Primeras 5 imágenes válidas:")
                self.stdout.write(str(valid_df.head()[['id', 'alto', 'ancho', 'grosor', 'peso', 'image_path']]))
                
                # Verificar que las rutas apuntan a raw
                self.stdout.write("\n5. Verificando rutas de imágenes...")
                sample_paths = valid_df.head()['image_path'].tolist()
                for path_str in sample_paths:
                    path = Path(path_str)
                    exists = path.exists()
                    is_raw = 'raw' in str(path)
                    self.stdout.write(f"   {path.name}: existe={exists}, es_raw={is_raw}")
            
            # 6. Obtener registros válidos
            self.stdout.write("\n6. Obteniendo registros válidos completos...")
            valid_records = loader.get_valid_records()
            self.stdout.write(f"   Total registros válidos: {len(valid_records)}")
            
            if valid_records:
                self.stdout.write(f"\n   Ejemplo de registro válido:")
                sample = valid_records[0]
                self.stdout.write(f"   ID: {sample['id']}")
                self.stdout.write(f"   Alto: {sample['alto']}, Ancho: {sample['ancho']}, Grosor: {sample['grosor']}, Peso: {sample['peso']}")
                self.stdout.write(f"   Ruta imagen raw: {sample['raw_image_path']}")
                self.stdout.write(f"   Existe imagen raw: {Path(sample['raw_image_path']).exists()}")
                self.stdout.write(f"   Ruta crop: {sample['crop_image_path']}")
                self.stdout.write(f"   Existe crop: {Path(sample['crop_image_path']).exists()}")
            
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write(self.style.SUCCESS("VERIFICACIÓN COMPLETADA"))
            self.stdout.write("=" * 60)
            self.stdout.write(f"\nResumen:")
            self.stdout.write(f"  - Imágenes raw disponibles: {len(bmp_files)}")
            self.stdout.write(f"  - Registros en CSV: {len(df)}")
            self.stdout.write(f"  - Registros válidos (con imagen): {len(valid_df)}")
            self.stdout.write(f"  - Registros con crops: {sum(1 for r in valid_records if Path(r['crop_image_path']).exists())}")
            self.stdout.write(f"  - Registros sin crops: {sum(1 for r in valid_records if not Path(r['crop_image_path']).exists())}")
            
            # Verificación final
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("VERIFICACIÓN DE CONFIGURACIÓN")
            self.stdout.write("=" * 60)
            
            # Verificar que el código lee desde raw
            raw_count = sum(1 for r in valid_records if 'raw' in str(r['raw_image_path']))
            self.stdout.write(f"\n✓ Registros que apuntan a imágenes raw: {raw_count}/{len(valid_records)}")
            
            # Verificar que los datos del CSV están presentes
            has_data = all('alto' in r and 'ancho' in r and 'grosor' in r and 'peso' in r for r in valid_records)
            self.stdout.write(f"✓ Datos del CSV presentes en registros: {has_data}")
            
            if raw_count == len(valid_records) and has_data:
                self.stdout.write(self.style.SUCCESS("\n✅ TODO CORRECTO: El código está configurado para leer imágenes desde raw con datos del CSV"))
            else:
                self.stdout.write(self.style.WARNING("\n⚠️ ADVERTENCIA: Algunos registros no apuntan a raw o faltan datos"))
            
        except Exception as e:
            logger.error(f"Error verifying training data: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"\n❌ ERROR: {e}"))
            import traceback
            self.stdout.write(traceback.format_exc())
            raise CommandError(f'Error al verificar datos de entrenamiento: {str(e)}')

