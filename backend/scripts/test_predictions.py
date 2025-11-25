"""
Script para diagnosticar las predicciones del modelo.
"""
import sys
from pathlib import Path
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
import django
django.setup()

import torch
import joblib
import numpy as np
from PIL import Image
from ml.prediction.predict import CacaoPredictor
from ml.data.dataset_loader import CacaoDatasetLoader

def test_prediction():
    """Prueba una predicción y muestra valores normalizados vs desnormalizados."""
    
    # Cargar predictor
    print("Cargando predictor...")
    predictor = CacaoPredictor()
    if not predictor.load_artifacts():
        print("Error: No se pudieron cargar los artefactos")
        return
    
    # Buscar imagen de ID 1
    loader = CacaoDatasetLoader()
    records = loader.get_valid_records()
    image_record = None
    for record in records:
        if record['id'] == 1:
            image_record = record
            break
    
    if not image_record:
        print("Error: No se encontró imagen con ID=1")
        return
    
    print(f"\nImagen encontrada: {image_record['image_path']}")
    print(f"Valores reales:")
    print(f"  ALTO: {image_record.get('alto', 'N/A')}")
    print(f"  ANCHO: {image_record.get('ancho', 'N/A')}")
    print(f"  GROSOR: {image_record.get('grosor', 'N/A')}")
    print(f"  PESO: {image_record.get('peso', 'N/A')}")
    
    # Cargar imagen - manejar rutas relativas correctamente
    image_path_str = str(image_record['image_path'])
    
    # Si la ruta ya incluye 'media', usarla directamente; si no, agregarlo
    if image_path_str.startswith('media') or image_path_str.startswith('media\\') or image_path_str.startswith('media/'):
        image_path = Path(image_path_str)
    else:
        image_path = Path('media') / image_path_str
    
    if not image_path.exists():
        print(f"Error: Imagen no encontrada: {image_path}")
        print(f"Ruta original del record: {image_record['image_path']}")
        # Intentar buscar en diferentes ubicaciones
        alternatives = [
            Path('media') / image_path_str.replace('media\\', '').replace('media/', ''),
            Path(image_path_str),
            Path('media/cacao_images/raw') / Path(image_path_str).name,
        ]
        for alt in alternatives:
            if alt.exists():
                print(f"Encontrada en ubicación alternativa: {alt}")
                image_path = alt
                break
        else:
            return
    
    print(f"\nCargando imagen: {image_path}")
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Hacer predicción
    print("\nHaciendo predicción...")
    result = predictor.predict(image)
    
    print(f"\nPredicciones desnormalizadas:")
    print(f"  alto_mm: {result['alto_mm']:.2f}")
    print(f"  ancho_mm: {result['ancho_mm']:.2f}")
    print(f"  grosor_mm: {result['grosor_mm']:.2f}")
    print(f"  peso_g: {result['peso_g']:.2f}")
    
    # Verificar valores normalizados antes de desnormalizar
    print("\n=== DIAGNÓSTICO DE ESCALADORES ===")
    for target in ['alto', 'ancho', 'grosor', 'peso']:
        scaler = predictor.scalers.scalers[target]
        print(f"\n{target.upper()}:")
        print(f"  Mean: {scaler.mean_[0]:.4f}")
        print(f"  Scale: {scaler.scale_[0]:.4f}")
        
        # Obtener predicción normalizada
        model = predictor.regression_models[target]
        image_tensor = predictor._preprocess_image(image)
        with torch.no_grad():
            pred_normalized = model(image_tensor).cpu().numpy().flatten()[0]
        
        print(f"  Predicción normalizada: {pred_normalized:.4f}")
        
        # Desnormalizar manualmente
        pred_array = np.array([[pred_normalized]])
        denorm = scaler.inverse_transform(pred_array)[0][0]
        print(f"  Predicción desnormalizada (manual): {denorm:.4f}")
        
        # Valor real normalizado
        real_value = image_record.get(target, None)
        if real_value:
            real_array = np.array([[real_value]])
            real_normalized = scaler.transform(real_array)[0][0]
            print(f"  Valor real: {real_value:.4f}")
            print(f"  Valor real normalizado: {real_normalized:.4f}")
            print(f"  Error: {abs(denorm - real_value):.4f}")
    
    print("\n=== FIN DIAGNÓSTICO ===")

if __name__ == "__main__":
    test_prediction()

