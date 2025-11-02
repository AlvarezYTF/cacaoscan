# Generated migration to fix foreign key reference
from django.db import migrations


def fix_lote_foreign_key(apps, schema_editor):
    """
    Actualiza la foreign key de fincas_app_lote.finca_id para que apunte a api_finca
    en lugar de fincas_app_finca.
    """
    db_alias = schema_editor.connection.alias
    connection = schema_editor.connection
    
    with connection.cursor() as cursor:
        # Verificar si la tabla fincas_app_lote existe
        cursor.execute("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'fincas_app_lote'
        """)
        
        if not cursor.fetchone():
            print("Tabla fincas_app_lote no existe, saltando actualización de FK")
            return
        
        # Listar todas las foreign keys que apuntan a fincas_app_finca
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
                AND ccu.table_name = 'fincas_app_finca';
        """)
        
        foreign_keys = cursor.fetchall()
        
        for fk in foreign_keys:
            constraint_name, table_name, column_name, foreign_table, foreign_column = fk
            
            # Verificar si la tabla api_finca existe
            cursor.execute("""
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'api_finca'
            """)
            
            if not cursor.fetchone():
                print(f"Tabla api_finca no existe, manteniendo FK {constraint_name}")
                continue
            
            # Verificar si ya existe una FK que apunte a api_finca
            cursor.execute("""
                SELECT constraint_name 
                FROM information_schema.table_constraints
                WHERE constraint_type = 'FOREIGN KEY'
                    AND table_name = 'fincas_app_lote'
                    AND constraint_name LIKE '%finca_id%';
            """)
            
            existing_fk = cursor.fetchone()
            
            if existing_fk:
                # Verificar a qué tabla apunta la FK existente
                cursor.execute("""
                    SELECT ccu.table_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_name = %s;
                """, [existing_fk[0]])
                
                target_table = cursor.fetchone()
                
                if target_table and target_table[0] == 'api_finca':
                    print(f"FK {existing_fk[0]} ya apunta a api_finca, saltando")
                    continue
            
            # Eliminar la FK antigua que apunta a fincas_app_finca
            cursor.execute(f'ALTER TABLE fincas_app_lote DROP CONSTRAINT IF EXISTS "{constraint_name}"')
            print(f"Eliminada FK antigua: {constraint_name}")
            
            # Crear nueva FK que apunte a api_finca
            new_constraint_name = constraint_name.replace('fincas_app_finca', 'api_finca')
            cursor.execute(f"""
                ALTER TABLE fincas_app_lote
                ADD CONSTRAINT "{new_constraint_name}"
                FOREIGN KEY ({column_name})
                REFERENCES api_finca(id)
                ON DELETE CASCADE
                DEFERRABLE INITIALLY DEFERRED
            """)
            print(f"Creada nueva FK: {new_constraint_name}")


def reverse_fix_lote_foreign_key(apps, schema_editor):
    """
    Revierte la foreign key para que apunte a fincas_app_finca.
    """
    db_alias = schema_editor.connection.alias
    connection = schema_editor.connection
    
    with connection.cursor() as cursor:
        # Listar todas las foreign keys que apuntan a api_finca
        cursor.execute("""
            SELECT tc.constraint_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
                AND tc.table_name = 'fincas_app_lote'
                AND ccu.table_name = 'api_finca'
                AND kcu.column_name = 'finca_id';
        """)
        
        foreign_keys = cursor.fetchall()
        
        for fk in foreign_keys:
            constraint_name = fk[0]
            
            # Verificar si la tabla fincas_app_finca existe
            cursor.execute("""
                SELECT 1 FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'fincas_app_finca'
            """)
            
            if not cursor.fetchone():
                print(f"Tabla fincas_app_finca no existe, saltando")
                continue
            
            # Eliminar la FK que apunta a api_finca
            cursor.execute(f'ALTER TABLE fincas_app_lote DROP CONSTRAINT IF EXISTS "{constraint_name}"')
            print(f"Eliminada FK: {constraint_name}")
            
            # Crear nueva FK que apunte a fincas_app_finca
            old_constraint_name = constraint_name.replace('api_finca', 'fincas_app_finca')
            cursor.execute(f"""
                ALTER TABLE fincas_app_lote
                ADD CONSTRAINT "{old_constraint_name}"
                FOREIGN KEY (finca_id)
                REFERENCES fincas_app_finca(id)
                ON DELETE CASCADE
                DEFERRABLE INITIALLY DEFERRED
            """)
            print(f"Creada FK revertida: {old_constraint_name}")


class Migration(migrations.Migration):

    dependencies = [
        ('fincas_app', '0003_rename_fincas_app__agricul_396b5b_idx_api_finca_agricul_f9cee8_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_lote_foreign_key, reverse_fix_lote_foreign_key),
    ]

