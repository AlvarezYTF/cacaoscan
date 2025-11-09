"""
Script para verificar que los modelos entrenados se carguen correctamente.
"""
import os
import sys
import django

# Configurar Django
# Ir al directorio padre (backend/) desde tests/
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
django.setup()

from ml.prediction.predict import get_predictor

def test_models_load():
    """Verifica que los modelos se carguen correctamente."""
    print("Inicializando predictor...")
    predictor = get_predictor()
    
    print("Cargando artefactos...")
    success = predictor.load_artifacts()
    
    if success:
        print("[OK] Modelos cargados exitosamente")
        print(f"[OK] Estado: {'OK' if predictor.models_loaded else 'NO OK'}")
        
        # Verificar que todos los modelos estén cargados
        targets = ['alto', 'ancho', 'grosor', 'peso']
        for target in targets:
            if target in predictor.regression_models:
                print(f"[OK] Modelo {target} cargado")
            else:
                print(f"[FAIL] Modelo {target} NO cargado")
        
        if predictor.scalers:
            print("[OK] Escaladores cargados")
        else:
            print("[FAIL] Escaladores NO cargados")
            
        return True
    else:
        print("[FAIL] Error cargando modelos")
        print(f"Estado: {'OK' if predictor.models_loaded else 'NO OK'}")
        return False

if __name__ == '__main__':
    test_models_load()

