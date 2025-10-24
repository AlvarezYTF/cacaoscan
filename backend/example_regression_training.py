"""
Ejemplo de uso del módulo de regresión de CacaoScan.
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

from ml.regression.models import create_model, TARGETS, get_model_info
from ml.regression.scalers import create_scalers_from_data
from ml.regression.train import get_device
import torch
import numpy as np


def example_model_creation():
    """Ejemplo de creación de modelos."""
    print("=== Ejemplo: Creación de Modelos ===")
    
    # Crear modelo individual para un target
    print("\n1. Modelo individual (ResNet18):")
    model_individual = create_model(
        model_type="resnet18",
        num_outputs=1,
        pretrained=True,
        dropout_rate=0.2,
        multi_head=False
    )
    
    print(f"Modelo individual creado: {type(model_individual).__name__}")
    print(f"Información del modelo: {get_model_info(model_individual)}")
    
    # Crear modelo multi-head
    print("\n2. Modelo multi-head:")
    model_multihead = create_model(
        model_type="resnet18",
        num_outputs=4,
        pretrained=True,
        dropout_rate=0.2,
        multi_head=True
    )
    
    print(f"Modelo multi-head creado: {type(model_multihead).__name__}")
    print(f"Información del modelo: {get_model_info(model_multihead)}")
    
    # Test de forward pass
    print("\n3. Test de forward pass:")
    device = get_device()
    model_individual = model_individual.to(device)
    model_multihead = model_multihead.to(device)
    
    # Crear datos de prueba
    batch_size = 2
    x = torch.randn(batch_size, 3, 224, 224).to(device)
    
    # Test modelo individual
    model_individual.eval()
    with torch.no_grad():
        output_individual = model_individual(x)
        print(f"Output modelo individual: {output_individual.shape}")
    
    # Test modelo multi-head
    model_multihead.eval()
    with torch.no_grad():
        outputs_multihead = model_multihead(x)
        print("Outputs modelo multi-head:")
        for target in TARGETS:
            print(f"  {target}: {outputs_multihead[target].shape}")


def example_scalers():
    """Ejemplo de uso de escaladores."""
    print("\n=== Ejemplo: Escaladores ===")
    
    # Crear datos de ejemplo
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'alto': np.random.normal(10, 2, n_samples),
        'ancho': np.random.normal(8, 1.5, n_samples),
        'grosor': np.random.normal(6, 1, n_samples),
        'peso': np.random.normal(2.5, 0.5, n_samples)
    }
    
    print(f"Datos originales (primeras 5 muestras):")
    for target in TARGETS:
        print(f"  {target}: {data[target][:5]}")
    
    # Crear y ajustar escaladores
    print("\n1. Creando escaladores...")
    scalers = create_scalers_from_data(data, scaler_type="standard")
    
    # Mostrar estadísticas
    stats = scalers.get_scaler_stats()
    print("\n2. Estadísticas de los escaladores:")
    for target in TARGETS:
        target_stats = stats[target]
        print(f"  {target}: mean={target_stats['mean']:.3f}, std={target_stats['std']:.3f}")
    
    # Transformar datos
    print("\n3. Transformando datos...")
    transformed_data = scalers.transform(data)
    
    print(f"Datos transformados (primeras 5 muestras):")
    for target in TARGETS:
        print(f"  {target}: {transformed_data[target][:5]}")
    
    # Verificar normalización
    print("\n4. Verificando normalización:")
    for target in TARGETS:
        mean = np.mean(transformed_data[target])
        std = np.std(transformed_data[target])
        print(f"  {target}: mean={mean:.3f}, std={std:.3f}")
    
    # Transformar de vuelta
    print("\n5. Transformando de vuelta...")
    original_data = scalers.inverse_transform(transformed_data)
    
    print(f"Datos originales (primeras 5 muestras):")
    for target in TARGETS:
        print(f"  {target}: {original_data[target][:5]}")
    
    # Verificar que son iguales (con tolerancia numérica)
    print("\n6. Verificando transformación inversa:")
    for target in TARGETS:
        max_diff = np.max(np.abs(original_data[target] - data[target]))
        print(f"  {target}: diferencia máxima = {max_diff:.10f}")


def example_device_info():
    """Ejemplo de información del dispositivo."""
    print("\n=== Ejemplo: Información del Dispositivo ===")
    
    device = get_device()
    print(f"Dispositivo seleccionado: {device}")
    
    if device.type == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        print(f"Memoria GPU total: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
        print(f"Memoria GPU disponible: {torch.cuda.memory_reserved(0) / 1e9:.1f} GB")
    else:
        print("Usando CPU para entrenamiento")


def example_model_comparison():
    """Ejemplo de comparación de modelos."""
    print("\n=== Ejemplo: Comparación de Modelos ===")
    
    models_to_test = [
        ("ResNet18 Individual", create_model("resnet18", num_outputs=1, multi_head=False)),
        ("ResNet18 Multi-head", create_model("resnet18", multi_head=True))
    ]
    
    # Intentar ConvNeXt si está disponible
    try:
        models_to_test.append(("ConvNeXt Tiny", create_model("convnext_tiny", multi_head=True)))
    except ImportError:
        print("ConvNeXt no disponible (uta instalar timm)")
    
    print("\nComparación de modelos:")
    print("-" * 60)
    print(f"{'Modelo rate':<20} {'Parámetros':<15} {'Tipo':<20}")
    print("-" * 60)
    
    for name, model in models_to_test:
        info = get_model_info(model)
        param_count = info['total_parameters']
        
        # Formatear número de parámetros
        if param_count >= 1e6:
            param_str = f"{param_count/1e6:.1f}M"
        elif param_count >= 1e3:
            param_str = f"{param_count/1e3:.1f}K"
        else:
            param_str = str(param_count)
        
        print(f"{name:<20} {param_str:<15} {info['model_type']:<20}")


def main():
    """Función principal."""
    print("CacaoScan ML - Ejemplo de Módulo de Regresión")
    print("=" * 60)
    
    try:
        # Ejecutar ejemplos
        example_model_creation()
        example_scalers()
        example_device_info()
        example_model_comparison()
        
        print("\n" + "=" * 60)
        print("=== Ejemplos Completados ===")
        print("Para entrenar modelos reales, usa:")
        print("python manage.py train_cacao_models --epochs 10 --test-mode")
        print("\nPara entrenamiento completo:")
        print("python manage.py train_cacao_models --epochs 50 --multihead")
        
    except Exception as e:
        print(f"Error ejecutando ejemplos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
