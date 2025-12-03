#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para detectar y corregir problemas de encoding en archivos de migración.

Este script:
1. Escanea todos los archivos .py en directorios migrations/
2. Detecta problemas de encoding (bytes inválidos, BOM, caracteres corruptos)
3. Corrige los problemas normalizando a UTF-8 sin BOM
4. Solo modifica encoding, NO cambia lógica
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Optional


def detect_encoding_issues(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Detecta problemas de encoding en un archivo.
    
    Returns:
        (has_issues, list_of_issues)
    """
    issues = []
    has_issues = False
    
    try:
        # Intentar leer como UTF-8 primero
        with open(file_path, 'rb') as f:
            raw_content = f.read()
        
        # Verificar BOM UTF-8
        if raw_content.startswith(b'\xef\xbb\xbf'):
            issues.append("Contiene BOM UTF-8")
            has_issues = True
        
        # Verificar byte problemático 0xf3
        if b'\xf3' in raw_content:
            issues.append("Contiene byte problemático 0xf3")
            has_issues = True
        
        # Verificar otros bytes problemáticos comunes
        problematic_bytes = [b'\xef', b'\xbb', b'\xbf', b'\x00']
        for pb in problematic_bytes:
            if pb in raw_content and pb != b'\xf3':  # Ya verificamos 0xf3
                issues.append(f"Contiene byte problemático {pb.hex()}")
                has_issues = True
        
        # Intentar decodificar como UTF-8
        try:
            content = raw_content.decode('utf-8')
        except UnicodeDecodeError as e:
            issues.append(f"Error de decodificación UTF-8: {e}")
            has_issues = True
            return has_issues, issues
        
        # Buscar caracteres corruptos comunes (ej: "RazÃ³n" en lugar de "Razón")
        corrupt_patterns = [
            r'Ã¡',  # á corrupto
            r'Ã©',  # é corrupto
            r'Ã­',  # í corrupto
            r'Ã³',  # ó corrupto
            r'Ãº',  # ú corrupto
            r'Ã±',  # ñ corrupto
            r'Ã',   # A con tilde corrupto general
        ]
        
        for pattern in corrupt_patterns:
            if re.search(pattern, content):
                issues.append(f"Contiene patrón corrupto: {pattern}")
                has_issues = True
        
        # Verificar caracteres no imprimibles problemáticos
        for i, char in enumerate(content):
            if ord(char) > 127:
                # Es un carácter no-ASCII, verificar que sea válido UTF-8
                try:
                    char.encode('utf-8').decode('utf-8')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    issues.append(f"Carácter inválido en posición {i}: {repr(char)}")
                    has_issues = True
        
    except Exception as e:
        issues.append(f"Error al analizar archivo: {e}")
        has_issues = True
    
    return has_issues, issues


def fix_encoding(file_path: Path) -> Tuple[bool, str]:
    """
    Corrige problemas de encoding en un archivo.
    
    Returns:
        (success, message)
    """
    try:
        # Leer archivo como bytes
        with open(file_path, 'rb') as f:
            raw_content = f.read()
        
        # Eliminar BOM UTF-8 si existe
        if raw_content.startswith(b'\xef\xbb\xbf'):
            raw_content = raw_content[3:]
        
        # Eliminar byte problemático 0xf3
        raw_content = raw_content.replace(b'\xf3', b'')
        
        # Intentar decodificar con diferentes encodings
        content = None
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings_to_try:
            try:
                content = raw_content.decode(encoding, errors='replace')
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            return False, "No se pudo decodificar el archivo con ningún encoding"
        
        # Corregir patrones corruptos comunes (ISO-8859-1 interpretado como UTF-8)
        # Note: Some replacements use double quotes to avoid syntax issues
        replacements = {
            'Ã¡': 'á',
            'Ã©': 'é',
            'Ã­': 'í',
            'Ã³': 'ó',
            'Ãº': 'ú',
            'Ã±': 'ñ',
            'Ã': 'Á',
            'Ã‰': 'É',
            'Ã': 'Í',
            'Ã"': 'Ó',
            'Ãš': 'Ú',
            "Ã'": 'Ñ',  # Use double quotes for string containing single quote
            'Â¿': '¿',
            'Â¡': '¡',
        }
        
        for corrupt, correct in replacements.items():
            content = content.replace(corrupt, correct)
        
        # Eliminar caracteres de control problemáticos (excepto \n, \r, \t)
        cleaned_lines = []
        for line in content.splitlines(keepends=True):
            cleaned_line = []
            for char in line:
                ord_val = ord(char)
                # Mantener caracteres imprimibles, saltos de línea, tabs
                if (32 <= ord_val <= 126) or char in '\n\r\t' or ord_val > 127:
                    # Verificar que sea válido UTF-8
                    try:
                        char.encode('utf-8')
                        cleaned_line.append(char)
                    except UnicodeEncodeError:
                        # Reemplazar caracteres inválidos
                        cleaned_line.append('?')
                # Eliminar caracteres de control problemáticos
            cleaned_lines.append(''.join(cleaned_line))
        
        content = ''.join(cleaned_lines)
        
        # Asegurar que el contenido es válido UTF-8
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            # Forzar encoding reemplazando caracteres problemáticos
            content = content.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
        
        # Verificar que tenemos el header de encoding si hay caracteres no-ASCII
        has_non_ascii = any(ord(c) > 127 for c in content)
        lines = content.splitlines()
        
        # Agregar header de encoding si no existe y hay caracteres no-ASCII
        if has_non_ascii and lines:
            first_line = lines[0]
            if not first_line.startswith('#') or 'coding' not in first_line.lower():
                # Agregar header después de la primera línea si es un comentario de migración
                if lines[0].startswith('#'):
                    lines.insert(1, '# -*- coding: utf-8 -*-')
                else:
                    lines.insert(0, '# -*- coding: utf-8 -*-')
                content = '\n'.join(lines) + '\n' if not content.endswith('\n') else '\n'.join(lines)
        
        # Escribir archivo corregido (sin BOM, UTF-8)
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        return True, "Archivo corregido exitosamente"
        
    except Exception as e:
        return False, f"Error al corregir archivo: {e}"


def scan_and_fix_migrations(base_dir: Path) -> dict:
    """
    Escanea y corrige todos los archivos de migración.
    
    Returns:
        dict con estadísticas
    """
    stats = {
        'scanned': 0,
        'with_issues': 0,
        'fixed': 0,
        'failed': 0,
        'files': []
    }
    
    # Buscar todos los archivos .py en directorios migrations/
    migration_files = []
    for root, dirs, files in os.walk(base_dir):
        if 'migrations' in root and '__pycache__' not in root:
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    migration_files.append(Path(root) / file)
    
    print(f"Encontrados {len(migration_files)} archivos de migración para analizar...")
    
    for file_path in sorted(migration_files):
        stats['scanned'] += 1
        relative_path = file_path.relative_to(base_dir)
        
        has_issues, issues = detect_encoding_issues(file_path)
        
        if has_issues:
            stats['with_issues'] += 1
            print(f"\n⚠️  {relative_path}")
            for issue in issues:
                print(f"   - {issue}")
            
            # Preguntar si corregir (en modo automático, siempre corregir)
            print(f"   Corrigiendo...")
            success, message = fix_encoding(file_path)
            
            if success:
                stats['fixed'] += 1
                print(f"   ✅ {message}")
                stats['files'].append({
                    'file': str(relative_path),
                    'status': 'fixed',
                    'issues': issues
                })
            else:
                stats['failed'] += 1
                print(f"   ❌ {message}")
                stats['files'].append({
                    'file': str(relative_path),
                    'status': 'failed',
                    'issues': issues,
                    'error': message
                })
    
    return stats


def main():
    """Función principal."""
    if len(sys.argv) > 1:
        base_dir = Path(sys.argv[1])
    else:
        # Asumir que se ejecuta desde el directorio backend
        base_dir = Path(__file__).parent
    
    if not base_dir.exists():
        print(f"Error: El directorio {base_dir} no existe")
        sys.exit(1)
    
    print(f"Escaneando archivos de migración en: {base_dir}")
    print("=" * 60)
    
    stats = scan_and_fix_migrations(base_dir)
    
    print("\n" + "=" * 60)
    print("RESUMEN:")
    print(f"  Archivos escaneados: {stats['scanned']}")
    print(f"  Archivos con problemas: {stats['with_issues']}")
    print(f"  Archivos corregidos: {stats['fixed']}")
    print(f"  Archivos con errores: {stats['failed']}")
    
    if stats['fixed'] > 0:
        print("\n✅ Archivos corregidos exitosamente:")
        for file_info in stats['files']:
            if file_info['status'] == 'fixed':
                print(f"  - {file_info['file']}")
    
    if stats['failed'] > 0:
        print("\n❌ Archivos con errores:")
        for file_info in stats['files']:
            if file_info['status'] == 'failed':
                print(f"  - {file_info['file']}: {file_info.get('error', 'Unknown error')}")
    
    sys.exit(0 if stats['failed'] == 0 else 1)


if __name__ == '__main__':
    main()

