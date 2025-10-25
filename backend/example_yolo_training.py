#!/usr/bin/env python3
"""
Script de ejemplo para entrenar modelo YOLOv8 personalizado.
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
django.setup()

from ml.segmentation.train_yolo import YOLOTrainingManager, train_cacao_yolo_model


def example_basic_training():
    """Ejemplo de entrenamiento básico."""
    print("=== EJEMPLO: ENTRENAMIENTO BÁSICO ===")
    
    try:
        # Crear entrenador con configuración básica
        trainer = YOLOTrainingManager(
            dataset_size=50,  # Dataset pequeño para prueba
            epochs=10,        # Pocas épocas para prueba rápida
            batch_size=8,     # Batch pequeño para CPU
            image_size=640
        )
        
        # Ejecutar entrenamiento
        results = trainer.run_full_training_pipeline(
            model_name="yolov8n-seg"  # Modelo más pequeño
        )
        
        if results['success']:
            print("✅ Entrenamiento completado exitosamente!")
            print(f"Mejor modelo: {results['model_paths']['best_model']}")
            print(f"Métricas mAP50: {results['validation_metrics']['mAP50']:.3f}")
        else:
            print(f"❌ Error en entrenamiento: {results['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_advanced_training():
    """Ejemplo de entrenamiento avanzado."""
    print("\n=== EJEMPLO: ENTRENAMIENTO AVANZADO ===")
    
    try:
        # Usar función de conveniencia
        results = train_cacao_yolo_model(
            dataset_size=100,
            epochs=50,
            batch_size=16,
            model_name="yolov8s-seg"
        )
        
        if results['success']:
            print("✅ Entrenamiento avanzado completado!")
            print(f"Duración: {results['training_duration']:.2f} segundos")
            print(f"Dataset: {results['dataset_info']['total_images']} imágenes")
            
            metrics = results['validation_metrics']
            print(f"Métricas:")
            print(f"  - mAP50: {metrics['mAP50']:.3f}")
            print(f"  - Precision: {metrics['precision']:.3f}")
            print(f"  - Recall: {metrics['recall']:.3f}")
        else:
            print(f"❌ Error: {results['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def example_dataset_creation():
    """Ejemplo de creación de dataset sin entrenar."""
    print("\n=== EJEMPLO: CREACIÓN DE DATASET ===")
    
    try:
        # Crear entrenador
        trainer = YOLOTrainingManager(dataset_size=30)
        
        # Solo crear dataset (sin entrenar)
        print("Generando anotaciones...")
        annotations = trainer.generate_annotations_from_crops()
        
        print(f"Anotaciones generadas: {len(annotations)}")
        
        print("Creando dataset YOLO...")
        splits = trainer.create_yolo_dataset(annotations)
        
        print(f"Dataset creado:")
        print(f"  - Train: {len(splits['train'])} imágenes")
        print(f"  - Val: {len(splits['val'])} imágenes")
        print(f"  - Test: {len(splits['test'])} imágenes")
        
        print(f"Configuración guardada en: {trainer.dataset_dir / 'dataset.yaml'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_model_validation():
    """Ejemplo de validación de modelo existente."""
    print("\n=== EJEMPLO: VALIDACIÓN DE MODELO ===")
    
    try:
        from ml.utils.paths import get_yolo_artifacts_dir
        
        # Buscar modelo existente
        models_dir = get_yolo_artifacts_dir() / "models"
        
        if not models_dir.exists():
            print("❌ No hay modelos entrenados para validar")
            return
        
        # Encontrar el modelo más reciente
        model_dirs = list(models_dir.glob("cacao_seg_*"))
        if not model_dirs:
            print("❌ No se encontraron modelos de cacao")
            return
        
        latest_model_dir = max(model_dirs, key=lambda x: x.stat().st_mtime)
        best_model_path = latest_model_dir / "weights" / "best.pt"
        
        if not best_model_path.exists():
            print(f"❌ Modelo no encontrado: {best_model_path}")
            return
        
        print(f"Validando modelo: {best_model_path}")
        
        # Crear entrenador para validación
        trainer = YOLOTrainingManager(dataset_size=50)
        
        # Validar modelo
        metrics = trainer.validate_model(best_model_path)
        
        print("✅ Validación completada!")
        print(f"Métricas:")
        print(f"  - mAP50: {metrics['mAP50']:.3f}")
        print(f"  - mAP50-95: {metrics['mAP50-95']:.3f}")
        print(f"  - Precision: {metrics['precision']:.3f}")
        print(f"  - Recall: {metrics['recall']:.3f}")
        print(f"  - F1-Score: {metrics['f1_score']:.3f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Función principal con menú de ejemplos."""
    print("🚀 EJEMPLOS DE ENTRENAMIENTO YOLO PARA CACAOSCAN")
    print("=" * 50)
    
    examples = {
        "1": ("Entrenamiento Básico", example_basic_training),
        "2": ("Entrenamiento Avanzado", example_advanced_training),
        "3": ("Creación de Dataset", example_dataset_creation),
        "4": ("Validación de Modelo", example_model_validation),
        "5": ("Ejecutar Todos", lambda: [example_basic_training(), example_dataset_creation()])
    }
    
    print("Ejemplos disponibles:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    print("\nNota: Estos ejemplos requieren:")
    print("- Dataset CSV en backend/media/datasets/dataset.csv")
    print("- Imágenes BMP en backend/media/cacao_images/raw/")
    print("- Ultralytics instalado: pip install ultralytics")
    
    choice = input("\nSelecciona un ejemplo (1-5) o Enter para salir: ").strip()
    
    if choice in examples:
        name, func = examples[choice]
        print(f"\nEjecutando: {name}")
        print("-" * 30)
        func()
    elif choice == "":
        print("Saliendo...")
    else:
        print("❌ Opción inválida")


if __name__ == "__main__":
    main()
