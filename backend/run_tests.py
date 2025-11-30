"""
Script para ejecutar todos los tests del proyecto CacaoScan.
Uso: python run_tests.py [opciones] o py run_tests.py [opciones]
"""
import sys
import subprocess
import os
import shutil
from pathlib import Path
from typing import Optional, Union, List

# Constants
TESTS_DIR = 'tests/'

# Asegurar que estamos en el directorio correcto
project_root = Path(__file__).parent
os.chdir(project_root)

def _check_python_version(executable: str) -> tuple[bool, str]:
    """Check Python version of an executable."""
    try:
        result = subprocess.run([executable, '--version'], 
                              capture_output=True, text=True, timeout=5)
        version_str = result.stdout.strip()
        return True, version_str
    except Exception:
        return False, ""

def _is_preferred_version(version_str: str) -> bool:
    """Check if version is Python 3.12."""
    return '3.12' in version_str

def _warn_if_python_313(version_str: str) -> None:
    """Warn if Python 3.13 is detected."""
    if '3.13' in version_str:
        print("⚠️  Advertencia: Se detectó Python 3.13. Se recomienda usar Python 3.12.")
        print(f"   Versión detectada: {version_str}")

def _try_sys_executable() -> Optional[str]:
    """Try to use sys.executable if it's Python 3.12."""
    if not (sys.executable and os.path.exists(sys.executable)):
        return None
    
    success, version_str = _check_python_version(sys.executable)
    if not success:
        return None
    
    if _is_preferred_version(version_str):
        return sys.executable
    
    _warn_if_python_313(version_str)
    return None

def _try_command(cmd: str) -> Union[str, List[str], None]:
    """Try a Python command and return it if it's version 3.12."""
    try:
        if ' ' in cmd:
            cmd_parts = cmd.split()
            result = subprocess.run(cmd_parts + ['--version'], 
                                  capture_output=True, text=True, timeout=5)
        else:
            if not shutil.which(cmd):
                return None
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5)
        
        version_str = result.stdout.strip()
        if _is_preferred_version(version_str):
            if ' ' in cmd:
                return cmd.split()
            return cmd
    except Exception:
        pass
    return None

def _find_fallback_command() -> str:
    """Find a fallback Python command."""
    if sys.executable:
        return sys.executable
    
    for cmd in ['py', 'python', 'python3']:
        if shutil.which(cmd):
            return cmd
    
    return 'python'

def get_python_cmd():
    """Detecta el comando de Python correcto para el sistema (preferiblemente 3.12)."""
    result = _try_sys_executable()
    if result:
        return result
    
    for cmd in ['py -3.12', 'python3.12', 'py', 'python', 'python3']:
        result = _try_command(cmd)
        if result:
            return result
    
    return _find_fallback_command()

def run_tests(test_path=None, verbose=True, stop_on_first_error=False):
    """
    Ejecuta los tests usando pytest.
    
    Args:
        test_path: Ruta específica de tests a ejecutar (None para todos)
        verbose: Si mostrar salida detallada
        stop_on_first_error: Si detenerse en el primer error
    """
    python_cmd = get_python_cmd()
    
    # Si python_cmd es una lista (py -3.12), usarla directamente
    if isinstance(python_cmd, list):
        cmd = python_cmd + ['-m', 'pytest']
    else:
        cmd = [python_cmd, '-m', 'pytest']
    
    if test_path:
        cmd.append(test_path)
    else:
        cmd.append(TESTS_DIR)
    
    if verbose:
        cmd.append('-v')
    
    if stop_on_first_error:
        cmd.append('-x')
    
    cmd.extend(['--tb=short', '--color=yes'])
    
    print(f"Ejecutando: {' '.join(cmd)}")
    print("=" * 80)
    
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Ejecutar tests de CacaoScan')
    parser.add_argument('test_path', nargs='?', help='Ruta específica de tests a ejecutar')
    parser.add_argument('-q', '--quiet', action='store_true', help='Modo silencioso')
    parser.add_argument('-x', '--stop-on-first', action='store_true', help='Detenerse en el primer error')
    parser.add_argument('--coverage', action='store_true', help='Ejecutar con cobertura')
    
    args = parser.parse_args()
    
    verbose = not args.quiet
    
    if args.coverage:
        # Ejecutar con cobertura
        python_cmd = get_python_cmd()
        if isinstance(python_cmd, list):
            cmd = python_cmd + ['-m', 'pytest', TESTS_DIR, '-v', '--cov=.', '--cov-report=html', '--cov-report=term']
        else:
            cmd = [python_cmd, '-m', 'pytest', TESTS_DIR, '-v', '--cov=.', '--cov-report=html', '--cov-report=term']
        if args.test_path:
            cmd.insert(-1, args.test_path)
        subprocess.run(cmd, cwd=project_root)
    else:
        exit_code = run_tests(args.test_path, verbose, args.stop_on_first)
        sys.exit(exit_code)

