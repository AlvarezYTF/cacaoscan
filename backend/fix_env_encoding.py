#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corregir la codificación del archivo .env
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / ".env"

if not env_path.exists():
    print(f"❌ Archivo .env no encontrado en: {env_path}")
    exit(1)

print(f"📄 Leyendo archivo .env desde: {env_path}")

# Leer el archivo como bytes primero
with open(env_path, 'rb') as f:
    raw_content = f.read()

print(f"📊 Tamaño del archivo: {len(raw_content)} bytes")
print("🔍 Buscando byte problemático 0xf3...")

# Buscar el byte 0xf3
if b'\xf3' in raw_content:
    positions = [i for i, b in enumerate(raw_content) if b == 0xf3]
    print(f"⚠️  Encontrado byte 0xf3 en posiciones: {positions[:10]}...")  # Mostrar solo las primeras 10
    
    # Mostrar contexto alrededor de la posición 85
    if len(raw_content) > 85:
        start = max(0, 75)
        end = min(len(raw_content), 95)
        context = raw_content[start:end]
        print(f"\n📋 Contexto alrededor de la posición 85 (bytes {start}-{end}):")
        print(f"   Hex: {context.hex()}")
        try:
            print(f"   Como UTF-8: {repr(context.decode('utf-8', errors='replace'))}")
        except Exception:
            pass

# Intentar múltiples codificaciones
encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1', 'windows-1252']
decoded_content = None
used_encoding = None

for encoding in encodings:
    try:
        decoded_content = raw_content.decode(encoding)
        used_encoding = encoding
        print(f"\n✅ Archivo decodificado exitosamente como: {encoding}")
        break
    except UnicodeDecodeError as e:
        print(f"❌ Error decodificando como {encoding}: {e}")
        continue

if decoded_content is None:
    # Último recurso: usar utf-8 con reemplazo de errores
    print("\n⚠️  Todos los intentos de decodificación fallaron. Usando UTF-8 con reemplazo de errores...")
    decoded_content = raw_content.decode('utf-8', errors='replace')
    used_encoding = 'utf-8 (con errores reemplazados)'

# Reescribir el archivo como UTF-8 limpio
print("\n💾 Reescribiendo archivo .env como UTF-8...")
try:
    with open(env_path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(decoded_content)
    print("✅ Archivo .env reescrito exitosamente como UTF-8")
    print(f"   Tamaño original: {len(raw_content)} bytes")
    print(f"   Tamaño nuevo: {len(decoded_content.encode('utf-8'))} bytes")
except Exception as e:
    print(f"❌ Error reescribiendo archivo: {e}")
    exit(1)

# Verificar que el archivo se puede leer correctamente ahora
print("\n🔍 Verificando que el archivo se puede leer correctamente...")
try:
    with open(env_path, 'r', encoding='utf-8') as f:
        test_content = f.read()
    print("✅ Archivo se puede leer correctamente como UTF-8")
    print(f"   Longitud: {len(test_content)} caracteres")
except Exception as e:
    print(f"❌ Error verificando archivo: {e}")
    exit(1)

print("\n✨ ¡Proceso completado! El archivo .env ahora está en UTF-8.")

