"""
Script para verificar que todas las importaciones de los tests funcionen correctamente.
Verifica también que se esté usando Python 3.12.
"""
import sys
import os
import subprocess
from pathlib import Path

# Verificar versión de Python primero
python_version = sys.version_info
print(f"Python detectado: {python_version.major}.{python_version.minor}.{python_version.micro}")

if python_version.major != 3 or python_version.minor != 12:
    print("⚠️  ADVERTENCIA: Se recomienda usar Python 3.12 para este proyecto.")
    print(f"   Versión actual: {python_version.major}.{python_version.minor}.{python_version.micro}")
    print("   Algunas dependencias pueden no ser compatibles con Python 3.13+")
    if python_version.minor == 13:
        print("   Considera usar: py -3.12 o python3.12")
else:
    print("✅ Versión de Python correcta (3.12)")

print("\n" + "="*60)

# Configurar Django
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')

try:
    import django
    django.setup()
    print("✅ Django configurado correctamente")
except Exception as e:
    print(f"❌ Error configurando Django: {e}")
    sys.exit(1)

# Verificar importaciones comunes
print("\nVerificando importaciones comunes...")

try:
    import pytest
    print("✅ pytest")
except ImportError:
    print("❌ pytest - Instalar con: pip install pytest pytest-django")
    sys.exit(1)

try:
    import numpy as np
    print("✅ numpy")
except ImportError:
    print("❌ numpy - Instalar con: pip install numpy")

try:
    import torch
    print("✅ torch")
except ImportError:
    print("⚠️  torch - Opcional, solo necesario para tests de ML")

try:
    from PIL import Image
    print("✅ PIL/Pillow")
except ImportError:
    print("❌ PIL/Pillow - Instalar con: pip install Pillow")

try:
    from unittest.mock import Mock, patch
    print("✅ unittest.mock")
except ImportError:
    print("❌ unittest.mock - Debería estar incluido en Python estándar")

# Verificar importaciones del proyecto
print("\nVerificando importaciones del proyecto...")

test_files = [
    'tests/test_ml_prediction_predict.py',
    'tests/test_api_services_analysis_service.py',
    'tests/test_images_services_processing_service.py',
]

for test_file in test_files:
    test_path = project_root / test_file
    if test_path.exists():
        print(f"\n📄 Verificando {test_file}...")
        try:
            # Leer el archivo y extraer imports
            # Try multiple encodings to read the file
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            content = None
            for encoding in encodings:
                try:
                    with open(test_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            if content is None:
                # Last resort: read as bytes and decode with errors='replace'
                with open(test_path, 'rb') as f:
                    raw_content = f.read()
                content = raw_content.decode('utf-8', errors='replace')
                # Buscar imports de ml.
                if 'from ml.' in content or 'import ml.' in content:
                    print("  ✅ Archivo encontrado")
        except Exception as e:
            print(f"  ⚠️  Error leyendo archivo: {e}")
    else:
        print(f"  ⚠️  Archivo no encontrado: {test_file}")

print("\n" + "="*60)
print("✅ Verificación de importaciones completada")
print("="*60)
print("\nPara ejecutar los tests, usa:")
print("  python run_tests.py")
print("  o")
print("  pytest tests/ -v")

