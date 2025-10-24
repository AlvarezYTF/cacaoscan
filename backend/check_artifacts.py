#!/usr/bin/env python
"""
Script para verificar el estado de los artefactos de entrenamiento.
"""
import os
import sys
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')

import django
django.setup()

def check_artifacts_status():
    """Verifica el estado actual de los artefactos."""
    try:
        from ml.utils.paths import get_regressors_artifacts_dir
        from ml.regression.models import TARGETS
        
        artifacts_dir = get_regressors_artifacts_dir()
        
        print("🔍 Verificando estado de artefactos...")
        print(f"📁 Directorio: {artifacts_dir}")
        
        if not artifacts_dir.exists():
            print("❌ El directorio de artefactos no existe aún")
            return False
        
        print(f"\n📊 Estado actual:")
        
        # Verificar modelos
        models_status = {}
        for target in TARGETS:
            model_path = artifacts_dir / f"{target}.pt"
            if model_path.exists():
                size_mb = model_path.stat().st_size / 1024 / 1024
                models_status[target] = f"✅ {size_mb:.2f} MB"
            else:
                models_status[target] = "❌ No encontrado"
        
        # Verificar escaladores
        scalers_status = {}
        for target in TARGETS:
            scaler_path = artifacts_dir / f"{target}_scaler.pkl"
            if scaler_path.exists():
                size_kb = scaler_path.stat().st_size / 1024
                scalers_status[target] = f"✅ {size_kb:.2f} KB"
            else:
                scalers_status[target] = "❌ No encontrado"
        
        # Mostrar estado
        print("\n🤖 Modelos:")
        for target in TARGETS:
            print(f"  {target}: {models_status[target]}")
        
        print("\n📏 Escaladores:")
        for target in TARGETS:
            print(f"  {target}: {scalers_status[target]}")
        
        # Verificar si todo está completo
        all_models_exist = all(
            (artifacts_dir / f"{target}.pt").exists() for target in TARGETS
        )
        all_scalers_exist = all(
            (artifacts_dir / f"{target}_scaler.pkl").exists() for target in TARGETS
        )
        
        if all_models_exist and all_scalers_exist:
            print("\n🎉 ¡Todos los artefactos están guardados correctamente!")
            
            # Calcular tamaño total
            total_size = sum(
                (artifacts_dir / f"{target}.pt").stat().st_size + 
                (artifacts_dir / f"{target}_scaler.pkl").stat().st_size
                for target in TARGETS
            )
            print(f"📊 Tamaño total: {total_size / 1024 / 1024:.2f} MB")
            return True
        else:
            print("\n⏳ Algunos artefactos aún no están listos...")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando artefactos: {e}")
        return False

if __name__ == "__main__":
    check_artifacts_status()
