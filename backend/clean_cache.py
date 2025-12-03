"""
Script para limpiar todos los archivos de caché de Python (__pycache__, .pyc, .pyo)
"""
import os
import shutil
from pathlib import Path


def clean_python_cache(root_dir: str = '.') -> None:
    """
    Elimina todos los archivos de caché de Python recursivamente.
    
    Args:
        root_dir: Directorio raíz desde donde empezar la limpieza
    """
    root_path = Path(root_dir).resolve()
    removed_dirs = 0
    removed_files = 0
    
    print(f"Limpiando archivos de cache de Python en: {root_path}")
    print("-" * 60)
    
    # Eliminar directorios __pycache__
    for pycache_dir in root_path.rglob('__pycache__'):
        try:
            shutil.rmtree(pycache_dir)
            removed_dirs += 1
            rel_path = pycache_dir.relative_to(root_path)
            print(f"[OK] Eliminado: {rel_path}")
        except Exception as e:
            print(f"[ERROR] Error eliminando {pycache_dir}: {e}")
    
    # Eliminar archivos .pyc
    for pyc_file in root_path.rglob('*.pyc'):
        try:
            pyc_file.unlink()
            removed_files += 1
            rel_path = pyc_file.relative_to(root_path)
            print(f"[OK] Eliminado: {rel_path}")
        except Exception as e:
            print(f"[ERROR] Error eliminando {pyc_file}: {e}")
    
    # Eliminar archivos .pyo
    for pyo_file in root_path.rglob('*.pyo'):
        try:
            pyo_file.unlink()
            removed_files += 1
            rel_path = pyo_file.relative_to(root_path)
            print(f"[OK] Eliminado: {rel_path}")
        except Exception as e:
            print(f"[ERROR] Error eliminando {pyo_file}: {e}")
    
    # Eliminar caché de pytest
    pytest_cache = root_path / '.pytest_cache'
    if pytest_cache.exists():
        try:
            shutil.rmtree(pytest_cache)
            removed_dirs += 1
            print(f"[OK] Eliminado: .pytest_cache")
        except Exception as e:
            print(f"[ERROR] Error eliminando .pytest_cache: {e}")
    
    print("-" * 60)
    print(f"Resumen: {removed_dirs} directorios y {removed_files} archivos eliminados")
    print("Limpieza completada")


if __name__ == '__main__':
    clean_python_cache('.')

