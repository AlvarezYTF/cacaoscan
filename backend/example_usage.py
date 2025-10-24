"""
Ejemplo de uso del módulo ML de CacaoScan.
"""
import os
import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')

import django
django.setup()

from ml.data.dataset_loader import CacaoDatasetLoader
from ml.segmentation.cropper import create_cacao_cropper


def example_dataset_validation():
    """Ejemplo de validación del dataset."""
    print("=== Ejemplo: Validación del Dataset ===")
    
    try:
        loader = CacaoDatasetLoader()
        stats = loader.get_dataset_stats()
        
        print(f"Total de registros: {stats['total_records']}")
        print(f"Registros válidos: {stats['valid_records']}")
        print(f"Imágenes faltantes: {stats['missing_images']}")
        
        if stats['missing_images'] > 0:
            print(f"IDs faltantes: {stats['missing_ids']}")
        
        # Mostrar estadísticas de dimensiones
        dim_stats = stats['dimensions_stats']
        for dimension, stats_dim in dim_stats.items():
            print(f"\n{dimension.upper()}:")
            print(f"  Min: {stats_dim['min']:.2f}")
            print(f"  Max: {stats_dim['max']:.2f}")
            print(f"  Media: {stats_dim['mean']:.2f}")
            print(f"  Std: {stats_dim['std']:.2f}")
        
    except Exception as e:
        print(f"Error validando dataset: {e}")


def example_crop_processing():
    """Ejemplo de procesamiento de crops."""
    print("\n=== Ejemplo: Procesamiento de Crops ===")
    
    try:
        # Cargar registros válidos
        loader = CacaoDatasetLoader()
        valid_records = loader.get_valid_records()
        
        if not valid_records:
            print("No hay registros válidos para procesar")
            return
        
        print(f"Encontrados {len(valid_records)} registros válidos")
        
        # Crear procesador de crops
        cropper = create_cacao_cropper(
            confidence_threshold=0.5,
            crop_size=512,
            padding=10,
            save_masks=True,  # Guardar máscaras para debug
            overwrite=False
        )
        
        # Procesar solo los primeros 3 registros como ejemplo
        example_records = valid_records[:3]
        print(f"Procesando {len(example_records)} imágenes de ejemplo...")
        
        stats = cropper.process_batch(example_records, limit=0)
        
        print(f"\nResultados:")
        print(f"  Total: {stats['total']}")
        print(f"  Procesadas: {stats['processed']}")
        print(f"  Exitosas: {stats['successful']}")
        print(f"  Fallidas: {stats['failed']}")
        print(f"  Saltadas: {stats['skipped']}")
        
        if stats['errors']:
            print(f"\nErrores:")
            for error in stats['errors']:
                print(f"  ID {error['id']}: {error['error']}")
        
    except Exception as e:
        print(f"Error procesando crops: {e}")


def main():
    """Función principal."""
    print("CacaoScan ML - Ejemplo de Uso")
    print("=" * 40)
    
    # Verificar que el dataset existe
    dataset_path = Path("media/datasets/dataset.csv")
    if not dataset_path.exists():
        print(f"Dataset no encontrado en {dataset_path}")
        print("Crea el archivo dataset.csv con las columnas: ID, ALTO, ANCHO, GROSOR, PESO")
        print("Y coloca las imágenes BMP en media/cacao_images/raw/")
        return
    
    # Ejecutar ejemplos
    example_dataset_validation()
    example_crop_processing()
    
    print("\n=== Ejemplo Completado ===")
    print("Para procesar todas las imágenes, usa:")
    print("python manage.py make_cacao_crops")


if __name__ == "__main__":
    main()
