"""
Script para ejecutar todos los tests del proyecto CacaoScan.
Uso: python run_tests.py [opciones] o py run_tests.py [opciones]
"""
import sys
import subprocess
import os
import shutil
from pathlib import Path

# Asegurar que estamos en el directorio correcto
project_root = Path(__file__).parent
os.chdir(project_root)

def get_python_cmd():
    """Detecta el comando de Python correcto para el sistema (preferiblemente 3.12)."""
    # Si sys.executable funciona, verificar versión
    if sys.executable and os.path.exists(sys.executable):
        try:
            result = subprocess.run([sys.executable, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            version_str = result.stdout.strip()
            # Verificar que sea Python 3.12
            if '3.12' in version_str:
                return sys.executable
            elif '3.13' in version_str:
                print(f"⚠️  Advertencia: Se detectó Python 3.13. Se recomienda usar Python 3.12.")
                print(f"   Versión detectada: {version_str}")
        except Exception:
            pass
    
    # Intentar diferentes comandos de Python, priorizando 3.12
    for cmd in ['py -3.12', 'python3.12', 'py', 'python', 'python3']:
        try:
            if ' ' in cmd:
                # Comando con espacio (py -3.12)
                cmd_parts = cmd.split()
                result = subprocess.run(cmd_parts + ['--version'], 
                                      capture_output=True, text=True, timeout=5)
            else:
                if not shutil.which(cmd):
                    continue
                result = subprocess.run([cmd, '--version'], 
                                      capture_output=True, text=True, timeout=5)
            
            version_str = result.stdout.strip()
            if '3.12' in version_str:
                if ' ' in cmd:
                    return cmd.split()  # Retornar lista para subprocess
                return cmd
        except Exception:
            continue
    
    # Fallback: usar sys.executable o el primer comando disponible
    if sys.executable:
        return sys.executable
    
    for cmd in ['py', 'python', 'python3']:
        if shutil.which(cmd):
            return cmd
    
    return 'python'

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
        cmd.append('tests/')
    
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
            cmd = python_cmd + ['-m', 'pytest', 'tests/', '-v', '--cov=.', '--cov-report=html', '--cov-report=term']
        else:
            cmd = [python_cmd, '-m', 'pytest', 'tests/', '-v', '--cov=.', '--cov-report=html', '--cov-report=term']
        if args.test_path:
            cmd.insert(-1, args.test_path)
        subprocess.run(cmd, cwd=project_root)
    else:
        exit_code = run_tests(args.test_path, verbose, args.stop_on_first)
        sys.exit(exit_code)

