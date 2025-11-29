"""
Script para verificar que se esté usando Python 3.12.
"""
import sys
import subprocess
import shutil

def check_python_version():
    """Verifica la versión de Python y sugiere comandos alternativos."""
    current_version = sys.version_info
    print(f"Versión de Python actual: {current_version.major}.{current_version.minor}.{current_version.micro}")
    print(f"Ejecutable: {sys.executable}")
    print()
    
    if current_version.major == 3 and current_version.minor == 12:
        print("✅ Versión correcta: Python 3.12")
        return True
    elif current_version.major == 3 and current_version.minor == 13:
        print("⚠️  ADVERTENCIA: Se detectó Python 3.13")
        print("   Se recomienda usar Python 3.12 para mejor compatibilidad con dependencias.")
        print()
        print("Opciones para usar Python 3.12:")
        print("  1. py -3.12 run_tests.py")
        print("  2. python3.12 run_tests.py")
        print("  3. Instalar Python 3.12 y configurarlo como predeterminado")
        return False
    else:
        print(f"⚠️  Versión detectada: Python {current_version.major}.{current_version.minor}")
        print("   Se recomienda usar Python 3.12")
        return False

def find_python312():
    """Intenta encontrar Python 3.12 en el sistema."""
    print("\nBuscando Python 3.12 en el sistema...")
    
    commands_to_try = [
        ['py', '-3.12', '--version'],
        ['python3.12', '--version'],
        ['python', '--version'],
        ['py', '--version'],
    ]
    
    found_312 = False
    
    for cmd in commands_to_try:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                print(f"  ✅ {' '.join(cmd)}: {version_str}")
                if '3.12' in version_str:
                    found_312 = True
                    print(f"     → Usa: {' '.join(cmd[:-1])} run_tests.py")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    
    if not found_312:
        print("  ❌ No se encontró Python 3.12")
        print("     Instala Python 3.12 desde: https://www.python.org/downloads/")
    
    return found_312

if __name__ == '__main__':
    print("="*60)
    print("Verificación de Versión de Python para CacaoScan")
    print("="*60)
    print()
    
    is_correct = check_python_version()
    
    if not is_correct:
        find_python312()
        print()
        print("="*60)
        sys.exit(1)
    else:
        print()
        print("="*60)
        print("✅ Todo listo para ejecutar los tests")
        print("="*60)

