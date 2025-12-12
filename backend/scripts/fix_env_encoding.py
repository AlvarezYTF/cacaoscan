"""
Script para diagnosticar y corregir problemas de codificación en el archivo .env
"""
import os
import sys
from pathlib import Path

def check_env_file():
    """Verifica el archivo .env por problemas de codificación."""
    base_dir = Path(__file__).parent.parent
    env_path = base_dir / '.env'
    
    if not env_path.exists():
        print("[ERROR] Archivo .env no encontrado")
        return False
    
    print(f"[INFO] Analizando archivo: {env_path}")
    
    # Leer como bytes primero
    try:
        with open(env_path, 'rb') as f:
            raw_bytes = f.read()
        
        # Detectar encoding
        encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']
        content = None
        detected_encoding = None
        
        for encoding in encodings_to_try:
            try:
                content = raw_bytes.decode(encoding)
                detected_encoding = encoding
                print(f"✅ Archivo decodificado como: {encoding}")
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            print("❌ No se pudo decodificar el archivo con ningún encoding conocido")
            # Forzar decodificación con replace
            content = raw_bytes.decode('utf-8', errors='replace')
            detected_encoding = 'utf-8 (con reemplazo)'
            print(f"⚠️  Usando decodificación forzada: {detected_encoding}")
        
        # Buscar bytes problemáticos
        problematic_bytes = []
        for i, byte in enumerate(raw_bytes):
            if byte in [0xab, 0xbb, 0xf3, 0xef, 0x00]:
                problematic_bytes.append((i, hex(byte), byte))
        
        if problematic_bytes:
            print(f"\n⚠️  Se encontraron {len(problematic_bytes)} bytes problemáticos:")
            for pos, hex_val, byte_val in problematic_bytes[:10]:  # Mostrar solo los primeros 10
                print(f"   Posición {pos}: {hex_val} (0x{hex_val[2:]})")
            if len(problematic_bytes) > 10:
                print(f"   ... y {len(problematic_bytes) - 10} más")
        else:
            print("✅ No se encontraron bytes problemáticos")
        
        # Verificar líneas con problemas
        lines_with_issues = []
        for i, line in enumerate(content.splitlines(), 1):
            try:
                line.encode('utf-8', errors='strict')
            except UnicodeEncodeError:
                lines_with_issues.append(i)
        
        if lines_with_issues:
            print(f"\n⚠️  Líneas con problemas de codificación: {lines_with_issues}")
            for line_num in lines_with_issues[:5]:
                line = content.splitlines()[line_num - 1]
                print(f"   Línea {line_num}: {line[:80]}...")
        else:
            print("✅ Todas las líneas son UTF-8 válidas")
        
        # Crear backup y archivo limpio
        if problematic_bytes or lines_with_issues:
            print("\n🔧 Creando archivo .env limpio...")
            backup_path = base_dir / '.env.backup'
            
            # Crear backup
            with open(backup_path, 'wb') as f:
                f.write(raw_bytes)
            print(f"✅ Backup creado: {backup_path}")
            
            # Limpiar contenido
            cleaned_lines = []
            for line in content.splitlines():
                # Remover bytes problemáticos
                cleaned_line = line
                for char_code in [0xab, 0xbb, 0xf3]:
                    try:
                        char = chr(char_code)
                        cleaned_line = cleaned_line.replace(char, '')
                    except (ValueError, TypeError):
                        pass
                
                # Asegurar UTF-8 válido
                try:
                    cleaned_line.encode('utf-8', errors='strict')
                    cleaned_lines.append(cleaned_line)
                except UnicodeEncodeError:
                    # Limpiar línea problemática
                    cleaned_line = cleaned_line.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                    cleaned_lines.append(cleaned_line)
            
            # Escribir archivo limpio
            with open(env_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write('\n'.join(cleaned_lines))
                f.write('\n')
            
            print(f"✅ Archivo .env limpiado y guardado")
            print(f"💡 Revisa el archivo y verifica que los valores sean correctos")
            return True
        else:
            print("\n✅ El archivo .env está bien codificado")
            return True
            
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = check_env_file()
    sys.exit(0 if success else 1)

