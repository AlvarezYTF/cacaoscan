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
    predictor = _load_predictor()
    if not predictor:
        return
    
    image_record = _find_image_record(1)
    if not image_record:
        return
    
    _print_image_info(image_record)
    image_path = _resolve_image_path(image_record)
    if not image_path:
        return
    
    image = _load_and_prepare_image(image_path)
    result = _make_prediction(predictor, image)
    _print_predictions(result)
    _diagnose_scalers(predictor, image, image_record)


def _load_predictor():
    """Carga el predictor y verifica que los artefactos se carguen correctamente."""
    print("Cargando predictor...")
    predictor = CacaoPredictor()
    if not predictor.load_artifacts():
        print("Error: No se pudieron cargar los artefactos")
        return None
    return predictor


def _find_image_record(image_id):
    """Busca un registro de imagen por ID."""
    loader = CacaoDatasetLoader()
    records = loader.get_valid_records()
    for record in records:
        if record['id'] == image_id:
            return record
    print(f"Error: No se encontró imagen con ID={image_id}")
    return None


def _print_image_info(image_record):
    """Imprime información de la imagen encontrada."""
    print(f"\nImagen encontrada: {image_record['image_path']}")
    print("Valores reales:")
    print(f"  ALTO: {image_record.get('alto', 'N/A')}")
    print(f"  ANCHO: {image_record.get('ancho', 'N/A')}")
    print(f"  GROSOR: {image_record.get('grosor', 'N/A')}")
    print(f"  PESO: {image_record.get('peso', 'N/A')}")


def _resolve_image_path(image_record):
    """Resuelve la ruta de la imagen, intentando diferentes ubicaciones si es necesario."""
    image_path_str = str(image_record['image_path'])
    
    if _starts_with_media(image_path_str):
        image_path = Path(image_path_str)
    else:
        image_path = Path('media') / image_path_str
    
    if image_path.exists():
        return image_path
    
    print(f"Error: Imagen no encontrada: {image_path}")
    print(f"Ruta original del record: {image_record['image_path']}")
    
    alternatives = _get_alternative_paths(image_path_str)
    for alt in alternatives:
        if alt.exists():
            print(f"Encontrada en ubicación alternativa: {alt}")
            return alt
    
    return None


def _starts_with_media(path_str):
    """Verifica si la ruta comienza con 'media'."""
    return path_str.startswith(('media', 'media\\', 'media/'))


def _get_alternative_paths(image_path_str):
    """Genera rutas alternativas para buscar la imagen."""
    return [
        Path('media') / image_path_str.replace('media\\', '').replace('media/', ''),
        Path(image_path_str),
        Path('media/cacao_images/raw') / Path(image_path_str).name,
    ]


def _load_and_prepare_image(image_path):
    """Carga y prepara la imagen para predicción."""
    print(f"\nCargando imagen: {image_path}")
    image = Image.open(image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    return image


def _make_prediction(predictor, image):
    """Realiza la predicción con el predictor."""
    print("\nHaciendo predicción...")
    return predictor.predict(image)


def _print_predictions(result):
    """Imprime las predicciones desnormalizadas."""
    print("\nPredicciones desnormalizadas:")
    print(f"  alto_mm: {result['alto_mm']:.2f}")
    print(f"  ancho_mm: {result['ancho_mm']:.2f}")
    print(f"  grosor_mm: {result['grosor_mm']:.2f}")
    print(f"  peso_g: {result['peso_g']:.2f}")


def _diagnose_scalers(predictor, image, image_record):
    """Diagnostica los escaladores mostrando valores normalizados vs desnormalizados."""
    print("\n=== DIAGNÓSTICO DE ESCALADORES ===")
    for target in ['alto', 'ancho', 'grosor', 'peso']:
        _diagnose_single_target(predictor, image, image_record, target)
    print("\n=== FIN DIAGNÓSTICO ===")


def _diagnose_single_target(predictor, image, image_record, target):
    """Diagnostica un objetivo específico."""
    scaler = predictor.scalers.scalers[target]
    print(f"\n{target.upper()}:")
    print(f"  Mean: {scaler.mean_[0]:.4f}")
    print(f"  Scale: {scaler.scale_[0]:.4f}")
    
    pred_normalized = _get_normalized_prediction(predictor, image, target)
    print(f"  Predicción normalizada: {pred_normalized:.4f}")
    
    denorm = _denormalize_prediction(scaler, pred_normalized)
    print(f"  Predicción desnormalizada (manual): {denorm:.4f}")
    
    _print_real_value_comparison(scaler, image_record, target, denorm)


def _get_normalized_prediction(predictor, image, target):
    """Obtiene la predicción normalizada para un objetivo."""
    model = predictor.regression_models[target]
    image_tensor = predictor._preprocess_image(image)
    with torch.no_grad():
        return model(image_tensor).cpu().numpy().flatten()[0]


def _denormalize_prediction(scaler, pred_normalized):
    """Desnormaliza una predicción."""
    pred_array = np.array([[pred_normalized]])
    return scaler.inverse_transform(pred_array)[0][0]


def _print_real_value_comparison(scaler, image_record, target, denorm):
    """Imprime comparación con valores reales."""
    real_value = image_record.get(target, None)
    if not real_value:
        return
    
    real_array = np.array([[real_value]])
    real_normalized = scaler.transform(real_array)[0][0]
    print(f"  Valor real: {real_value:.4f}")
    print(f"  Valor real normalizado: {real_normalized:.4f}")
    print(f"  Error: {abs(denorm - real_value):.4f}")

if __name__ == "__main__":
    test_prediction()
