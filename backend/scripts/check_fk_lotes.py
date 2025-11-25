"""
Script para verificar y corregir la foreign key de fincas_app_lote.
Ejecutar con: python manage.py shell < scripts/check_fk_lotes.py
o directamente: python scripts/check_fk_lotes.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cacaoscan.settings')
django.setup()

from django.db import connection
from fincas_app.models import Finca, Lote

def check_and_fix_foreign_key():
    """Verificar y corregir la foreign key de lotes."""
    print("=" * 60)
    print("Verificando foreign key de fincas_app_lote")
    print("=" * 60)
    
    # Información del modelo
    print(f"\nTabla Finca: {Finca._meta.db_table}")
    print(f"Tabla Lote: {Lote._meta.db_table}")
    
    with connection.cursor() as cursor:
        # Verificar foreign keys actuales
        cursor.execute("""
            SELECT 
                tc.constraint_name,
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = 'fincas_app_lote'
                AND kcu.column_name = 'finca_id';
        """)
        
        fks = cursor.fetchall()
        
        if not fks:
            print("\n[WARN]  No se encontró foreign key en fincas_app_lote.finca_id")
            print("Creando foreign key...")
            
            # Verificar si la tabla api_finca existe
            cursor.execute("""
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_finca'
            """)
            
            if cursor.fetchone():
                constraint_name = 'fincas_app_lote_finca_id_api_finca_fk'
                cursor.execute(f"""
                    ALTER TABLE fincas_app_lote
                    ADD CONSTRAINT "{constraint_name}"
                    FOREIGN KEY (finca_id)
                    REFERENCES api_finca(id)
                    ON DELETE CASCADE
                """)
                print(f"✅ Foreign key creada: {constraint_name}")
            else:
                print("[ERROR] La tabla api_finca no existe")
                return
        else:
            print(f"\n📋 Foreign keys encontradas: {len(fks)}")
            for fk in fks:
                constraint_name, table_name, column_name, foreign_table, foreign_column = fk
                print(f"  - {constraint_name}: {table_name}.{column_name} -> {foreign_table}.{foreign_column}")
                
                # Verificar si apunta a la tabla correcta
                if foreign_table != 'api_finca':
                    print(f"\n[WARN]  PROBLEMA: FK apunta a '{foreign_table}' pero debería apuntar a 'api_finca'")
                    print(f"Corrigiendo foreign key...")
                    
                    # Eliminar FK incorrecta
                    cursor.execute(f'ALTER TABLE fincas_app_lote DROP CONSTRAINT IF EXISTS "{constraint_name}"')
                    print(f"✅ Eliminada FK incorrecta: {constraint_name}")
                    
                    # Crear FK correcta
                    new_constraint_name = constraint_name.replace(foreign_table, 'api_finca')
                    cursor.execute(f"""
                        ALTER TABLE fincas_app_lote
                        ADD CONSTRAINT "{new_constraint_name}"
                        FOREIGN KEY (finca_id)
                        REFERENCES api_finca(id)
                        ON DELETE CASCADE
                    """)
                    print(f"✅ Creada FK correcta: {new_constraint_name}")
                else:
                    print(f"✅ FK correcta: apunta a {foreign_table}")
    
    # Verificar consistencia de datos
    print("\n" + "=" * 60)
    print("Verificando consistencia de datos")
    print("=" * 60)
    
    # Contar fincas
    total_fincas = Finca.objects.count()
    print(f"\nTotal de fincas en BD: {total_fincas}")
    
    if total_fincas > 0:
        fincas_list = list(Finca.objects.values('id', 'nombre')[:10])
        print("Primeras fincas:")
        for f in fincas_list:
            print(f"  - ID: {f['id']}, Nombre: {f['nombre']}")
    
    # Verificar lotes huérfanos
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT l.id, l.finca_id, f.id as finca_exists
            FROM fincas_app_lote l
            LEFT JOIN api_finca f ON l.finca_id = f.id
            WHERE f.id IS NULL
            LIMIT 10;
        """)
        
        orphaned_lotes = cursor.fetchall()
        
        if orphaned_lotes:
            print(f"\n[WARN]  Lotes huérfanos encontrados: {len(orphaned_lotes)}")
            print("Lotes sin finca válida:")
            for lote in orphaned_lotes:
                print(f"  - Lote ID: {lote[0]}, finca_id: {lote[1]}")
        else:
            print("\n✅ No se encontraron lotes huérfanos")
    
    print("\n" + "=" * 60)
    print("Verificación completada")
    print("=" * 60)

if __name__ == '__main__':
    check_and_fix_foreign_key()

