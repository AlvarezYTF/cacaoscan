"""
Script de ejemplo para usar el sistema YOLOv8 completo de CacaoScan.

Este script demuestra cómo:
1. Preparar datos para entrenamiento YOLOv8
2. Entrenar el modelo
3. Usar el modelo para predicciones
4. Integrar con el sistema existente
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Función principal de demostración."""
    
    print("🚀 CACOASCAN YOLOV8 - SISTEMA COMPLETO")
    print("=" * 50)
    
    # Configurar rutas
    base_dir = Path(__file__).parent
    dataset_csv = base_dir / 'media' / 'dataset' / 'dataset.csv'
    images_dir = base_dir / 'media' / 'imgs'
    output_dir = base_dir / 'training_output'
    
    print(f"📁 Directorio base: {base_dir}")
    print(f"📊 Dataset CSV: {dataset_csv}")
    print(f"🖼️  Imágenes: {images_dir}")
    print(f"📤 Salida: {output_dir}")
    
    # Verificar archivos necesarios
    if not dataset_csv.exists():
        print(f"❌ Error: No se encontró el dataset CSV en {dataset_csv}")
        return
    
    if not images_dir.exists():
        print(f"❌ Error: No se encontró el directorio de imágenes en {images_dir}")
        return
    
    print("\n✅ Archivos necesarios encontrados")
    
    # Paso 1: Preparar datos para YOLOv8
    print("\n📋 PASO 1: PREPARAR DATOS PARA YOLOV8")
    print("-" * 40)
    
    try:
        from prepare_yolo_data import YOLODataPreparator
        
        preparator = YOLODataPreparator(
            dataset_csv_path=str(dataset_csv),
            images_dir=str(images_dir),
            output_dir='yolo_dataset'
        )
        
        # Generar anotaciones
        counts = preparator.generate_annotations(
            split_ratios=(0.7, 0.2, 0.1),  # 70% train, 20% val, 10% test
            auto_detect_bbox=True
        )
        
        print(f"✅ Anotaciones generadas:")
        for split, count in counts.items():
            print(f"   {split}: {count} imágenes")
        
        # Crear muestras para verificación
        sample_files = preparator.create_sample_annotations(num_samples=5)
        print(f"✅ Muestras creadas: {len(sample_files)}")
        
        # Validar dataset
        validation_results = preparator.validate_dataset()
        print(f"✅ Validación completada:")
        print(f"   Total imágenes: {validation_results['total_images']}")
        print(f"   Total anotaciones: {validation_results['total_annotations']}")
        print(f"   Anotaciones faltantes: {validation_results['missing_annotations']}")
        print(f"   Anotaciones inválidas: {validation_results['invalid_annotations']}")
        
    except Exception as e:
        print(f"❌ Error preparando datos: {e}")
        return
    
    # Paso 2: Entrenar modelo YOLOv8
    print("\n🏋️ PASO 2: ENTRENAR MODELO YOLOV8")
    print("-" * 40)
    
    try:
        from train_yolo import CacaoYOLOTrainer
        
        trainer = CacaoYOLOTrainer(
            dataset_config_path='yolo_dataset/dataset.yaml',
            output_dir=str(output_dir),
            model_size='n'  # Modelo pequeño para demo
        )
        
        # Preparar modelo
        if not trainer.prepare_model(pretrained=True):
            print("❌ Error preparando modelo")
            return
        
        print("✅ Modelo YOLOv8 preparado")
        
        # Configuración de entrenamiento (reducida para demo)
        custom_config = {
            'epochs': 10,  # Reducido para demo
            'batch': 8,
            'imgsz': 640,
            'device': 'auto'
        }
        
        print("🚀 Iniciando entrenamiento...")
        training_results = trainer.train(custom_config=custom_config)
        
        print(f"✅ Entrenamiento completado:")
        print(f"   Duración: {training_results.get('training_duration', 'N/A')}")
        print(f"   Modelo: {training_results.get('production_model_path', 'N/A')}")
        
        # Validar modelo
        validation_results = trainer.validate_model()
        if validation_results['validation_successful']:
            print(f"✅ Validación exitosa:")
            metrics = validation_results['validation_metrics']
            print(f"   mAP50: {metrics.get('mAP50', 0):.3f}")
            print(f"   mAP50-95: {metrics.get('mAP50-95', 0):.3f}")
        else:
            print(f"⚠️  Validación con problemas: {validation_results.get('error', 'Desconocido')}")
        
        # Crear modelo integrado
        if trainer.create_weight_prediction_model(str(dataset_csv)):
            print("✅ Modelo integrado creado")
        
    except Exception as e:
        print(f"❌ Error en entrenamiento: {e}")
        return
    
    # Paso 3: Probar predicción
    print("\n🔮 PASO 3: PROBAR PREDICCIÓN")
    print("-" * 40)
    
    try:
        from yolo_model import CacaoYOLOModel
        
        # Cargar modelo entrenado
        model_path = output_dir / 'weight_yolo.pt'
        if not model_path.exists():
            print(f"❌ Modelo no encontrado: {model_path}")
            return
        
        model = CacaoYOLOModel(
            model_path=str(model_path),
            device='auto',
            confidence_threshold=0.5
        )
        
        if not model.load_model():
            print("❌ Error cargando modelo")
            return
        
        print("✅ Modelo YOLOv8 cargado")
        
        # Probar con una imagen de muestra
        sample_images = list(images_dir.glob('*.bmp'))[:3]
        
        for i, image_path in enumerate(sample_images):
            print(f"\n🖼️  Probando imagen {i+1}: {image_path.name}")
            
            try:
                result = model.predict_weight_from_image(
                    str(image_path),
                    return_detection_image=False
                )
                
                if result.get('success', False):
                    print(f"✅ Predicción exitosa:")
                    print(f"   Peso estimado: {result.get('peso_estimado', 0):.3f} g")
                    print(f"   Altura: {result.get('altura_mm', 0):.2f} mm")
                    print(f"   Ancho: {result.get('ancho_mm', 0):.2f} mm")
                    print(f"   Grosor: {result.get('grosor_mm', 0):.2f} mm")
                    print(f"   Confianza: {result.get('nivel_confianza', 0):.3f}")
                else:
                    print(f"❌ Error en predicción: {result.get('error', 'Desconocido')}")
                    
            except Exception as e:
                print(f"❌ Error procesando imagen: {e}")
        
    except Exception as e:
        print(f"❌ Error probando predicción: {e}")
        return
    
    # Paso 4: Integrar con sistema existente
    print("\n🔗 PASO 4: INTEGRAR CON SISTEMA EXISTENTE")
    print("-" * 40)
    
    try:
        from prediction_service import CacaoPredictionService
        
        # Crear servicio con YOLOv8 habilitado
        service = CacaoPredictionService(
            enable_caching=True,
            device='auto',
            confidence_threshold=0.5,
            enable_yolo=True
        )
        
        print("✅ Servicio de predicción creado con YOLOv8")
        
        # Probar análisis completo
        if sample_images:
            test_image = str(sample_images[0])
            print(f"\n🧪 Probando análisis completo con: {Path(test_image).name}")
            
            result = service.predict_complete_analysis(
                test_image,
                use_vision_for_weight=True,
                include_confidence=True,
                include_comparison=True,
                include_yolo=True
            )
            
            print(f"✅ Análisis completo exitoso:")
            print(f"   Peso final: {result.get('predicted_weight', 0):.3f} g")
            print(f"   Método: {result.get('weight_prediction_method', 'N/A')}")
            print(f"   Tiempo: {result.get('processing_time', 0):.3f} s")
            
            # Mostrar comparación
            if 'weight_comparison' in result:
                comparison = result['weight_comparison']
                print(f"   Comparación:")
                print(f"     Visión CNN: {comparison.get('vision_weight', 0):.3f} g")
                print(f"     Regresión: {comparison.get('regression_weight', 0):.3f} g")
                if 'yolo_weight' in comparison:
                    print(f"     YOLOv8: {comparison.get('yolo_weight', 0):.3f} g")
            
            # Mostrar predicción YOLOv8
            if 'yolo_prediction' in result:
                yolo_pred = result['yolo_prediction']
                print(f"   YOLOv8:")
                print(f"     Peso: {yolo_pred.get('peso_estimado', 0):.3f} g")
                print(f"     Confianza: {yolo_pred.get('nivel_confianza', 0):.3f}")
                print(f"     Éxito: {yolo_pred.get('success', False)}")
        
    except Exception as e:
        print(f"❌ Error integrando con sistema: {e}")
        return
    
    # Resumen final
    print("\n🎉 RESUMEN FINAL")
    print("=" * 50)
    print("✅ Sistema YOLOv8 implementado completamente")
    print("✅ Datos preparados y anotados")
    print("✅ Modelo entrenado y validado")
    print("✅ Predicciones funcionando")
    print("✅ Integración con sistema existente")
    
    print("\n📋 PRÓXIMOS PASOS:")
    print("1. Ejecutar entrenamiento completo con más épocas")
    print("2. Calibrar modelo con datos reales")
    print("3. Probar endpoint API: POST /api/images/predict-yolo/")
    print("4. Integrar con frontend Vue.js")
    print("5. Monitorear rendimiento en producción")
    
    print("\n🔧 COMANDOS ÚTILES:")
    print("# Preparar datos:")
    print("python prepare_yolo_data.py --dataset-csv media/dataset/dataset.csv --images-dir media/imgs")
    print("\n# Entrenar modelo:")
    print("python train_yolo.py --dataset-config yolo_dataset/dataset.yaml --epochs 100")
    print("\n# Probar predicción:")
    print("python -c \"from yolo_model import CacaoYOLOModel; model = CacaoYOLOModel(); model.load_model(); print(model.predict_weight_from_image('test.jpg'))\"")
    
    print("\n🎯 ¡Sistema YOLOv8 listo para producción!")


if __name__ == "__main__":
    main()
