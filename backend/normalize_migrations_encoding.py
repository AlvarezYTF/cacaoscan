#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para normalizar encoding de todos los archivos de migración a UTF-8 sin BOM.

Este script:
1. Lee todos los archivos .py en directorios migrations/
2. Los normaliza a UTF-8 sin BOM
3. Agrega header de encoding si falta
4. NO modifica la lógica, solo el encoding
"""

import os
import sys
from pathlib import Path


def normalize_file_encoding(file_path: Path) -> tuple:
    """
    Normaliza un archivo a UTF-8 sin BOM.
    
    Returns:
        (success: bool, message: str)
    """
    try:
        # Leer archivo como bytes
        with open(file_path, 'rb') as f:
            raw_content = f.read()
        
        # Remover BOM UTF-8 si existe
        if raw_content.startswith(b'\xef\xbb\xbf'):
            raw_content = raw_content[3:]
        
        # Remover byte problemático 0xf3 si existe
        if b'\xf3' in raw_content:
            raw_content = raw_content.replace(b'\xf3', b'')
        
        # Decodificar a string
        try:
            content = raw_content.decode('utf-8', errors='replace')
        except Exception:
            # Intentar otros encodings como fallback
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    content = raw_content.decode(encoding, errors='replace')
                    break
                except Exception:
                    continue
            else:
                return False, "No se pudo decodificar el archivo"
        
        # Asegurar que termina con newline
        if not content.endswith('\n'):
            content += '\n'
        
        # Verificar/agregar header de encoding
        lines = content.splitlines(keepends=True)
        has_encoding_header = False
        
        for i, line in enumerate(lines[:5]):  # Buscar en las primeras 5 líneas
            if 'coding' in line.lower() or 'encoding' in line.lower():
                has_encoding_header = True
                break
        
        # Si no tiene header y tiene caracteres no-ASCII, agregarlo
        has_non_ascii = any(ord(c) > 127 for c in content)
        if not has_encoding_header and has_non_ascii:
            # Buscar la primera línea de comentario
            insert_pos = 0
            if lines and lines[0].startswith('#'):
                # Insertar después del primer comentario
                insert_pos = 1
                # Si el primer comentario no tiene coding, agregar uno
                if 'coding' not in lines[0].lower():
                    lines.insert(insert_pos, '# -*- coding: utf-8 -*-\n')
                    has_encoding_header = True
            else:
                # Agregar al inicio
                lines.insert(0, '# -*- coding: utf-8 -*-\n')
                has_encoding_header = True
        
        content = ''.join(lines)
        
        # Escribir archivo normalizado (UTF-8 sin BOM)
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        return True, "Normalizado a UTF-8 sin BOM"
        
    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Función principal."""
    base_dir = Path(__file__).parent if len(sys.argv) <= 1 else Path(sys.argv[1])
    
    if not base_dir.exists():
        print(f"Error: El directorio {base_dir} no existe")
        sys.exit(1)
    
    # Buscar todos los archivos .py en directorios migrations/
    migration_files = []
    for root, dirs, files in os.walk(base_dir):
        if 'migrations' in root and '__pycache__' not in root:
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    migration_files.append(Path(root) / file)
    
    print(f"Normalizando encoding de {len(migration_files)} archivos de migración...")
    print("=" * 60)
    
    fixed = 0
    failed = 0
    
    for file_path in sorted(migration_files):
        relative_path = file_path.relative_to(base_dir)
        success, message = normalize_file_encoding(file_path)
        
        if success:
            fixed += 1
            print(f"✅ {relative_path}")
        else:
            failed += 1
            print(f"❌ {relative_path}: {message}")
    
    print("\n" + "=" * 60)
    print(f"RESUMEN: {fixed} normalizados, {failed} con errores")
    
    sys.exit(0 if failed == 0 else 1)


if __name__ == '__main__':
    main()

