"""
Script de diagnóstico para verificar el soporte de GPU en PyTorch
"""
import sys

print("=" * 60)
print("DIAGNÓSTICO DE GPU PARA ENTRENAMIENTO")
print("=" * 60)

# Verificar PyTorch
try:
    import torch
    print(f"✓ PyTorch instalado: versión {torch.__version__}")
except ImportError:
    print("✗ PyTorch NO está instalado")
    print("\nInstala PyTorch con soporte CUDA:")
    print("  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
    sys.exit(1)

# Verificar CUDA en PyTorch
print(f"\nVerificando soporte CUDA en PyTorch...")
print(f"  torch.cuda.is_available(): {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"✓ CUDA disponible en PyTorch")
    print(f"  Número de GPUs: {torch.cuda.device_count()}")
    print(f"  GPU actual: {torch.cuda.current_device()}")
    print(f"  Nombre GPU: {torch.cuda.get_device_name(0)}")
    print(f"  Versión CUDA (PyTorch): {torch.version.cuda}")
    print(f"  Memoria total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    print(f"  Memoria reservada: {torch.cuda.memory_reserved(0) / 1024**3:.2f} GB")
    print(f"  Memoria asignada: {torch.cuda.memory_allocated(0) / 1024**3:.2f} GB")
    
    # Prueba rápida
    print("\n✓ Prueba rápida: Creando tensor en GPU...")
    try:
        test_tensor = torch.randn(1000, 1000).cuda()
        print("✓ Tensor creado exitosamente en GPU")
        del test_tensor
        torch.cuda.empty_cache()
    except Exception as e:
        print(f"✗ Error al crear tensor en GPU: {e}")
else:
    print("✗ CUDA NO está disponible en PyTorch")
    print("\nPosibles causas:")
    print("  1. PyTorch fue instalado sin soporte CUDA")
    print("  2. Versión de CUDA no compatible")
    print("\nSolución:")
    print("  Desinstala PyTorch actual:")
    print("    pip uninstall torch torchvision")
    print("\n  Instala PyTorch con soporte CUDA 12.1:")
    print("    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
    print("\n  O para CUDA 11.8:")
    print("    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118")

# Verificar Ultralytics
print("\n" + "=" * 60)
print("Verificando Ultralytics...")
try:
    from ultralytics import YOLO
    print("✓ Ultralytics instalado")
    
    # Verificar si puede detectar GPU
    try:
        import torch
        if torch.cuda.is_available():
            print("✓ Ultralytics puede usar GPU (PyTorch CUDA disponible)")
        else:
            print("✗ Ultralytics usará CPU (PyTorch CUDA no disponible)")
    except:
        print("✗ No se pudo verificar soporte GPU en Ultralytics")
except ImportError:
    print("✗ Ultralytics NO está instalado")
    print("  Instala con: pip install ultralytics")

print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)

try:
    import torch
    if torch.cuda.is_available():
        print("✓ Todo está listo para usar GPU en el entrenamiento")
        print(f"  Usa: --device cuda o --device auto")
    else:
        print("✗ GPU no disponible para PyTorch")
        print("  Instala PyTorch con soporte CUDA (ver instrucciones arriba)")
except:
    print("✗ PyTorch no disponible")

print("=" * 60)

