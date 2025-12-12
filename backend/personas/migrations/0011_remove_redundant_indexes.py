# Remove redundant indexes on unique columns
# UNIQUE constraint already creates an index that covers equality searches
# Normal indexes on unique columns (numero_documento, telefono) are redundant
# -*- coding: utf-8 -*-
from django.db import migrations, connection


def remove_redundant_indexes(apps, schema_editor):
    """
    Remove redundant normal indexes on unique columns.
    
    When a column has unique=True, PostgreSQL automatically creates a UNIQUE index
    that already covers equality searches. A normal B-tree index on the same column
    is redundant and wastes space.
    
    We keep:
    - UNIQUE indexes (created automatically by unique=True)
    - LIKE indexes (if they exist, useful for pattern searches)
    - user index (not unique, so normal index is needed)
    
    We remove:
    - Normal B-tree indexes on numero_documento (redundant with UNIQUE)
    - Normal B-tree indexes on telefono (redundant with UNIQUE)
    """
    db_engine = connection.settings_dict.get('ENGINE', '')
    
    if 'postgresql' not in db_engine:
        print("Skipping index removal - not PostgreSQL")
        return
    
    with connection.cursor() as cursor:
        # List of redundant indexes to remove
        redundant_indexes = [
            'personas_pe_numero__8c4625_idx',  # Normal index on numero_documento
            'personas_pe_telefon_c9eac3_idx',  # Normal index on telefono
        ]
        
        removed_count = 0
        skipped_count = 0
        
        for index_name in redundant_indexes:
            try:
                # Check if index exists
                cursor.execute("""
                    SELECT 1 FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND indexname = %s
                """, [index_name])
                
                if cursor.fetchone():
                    # Check if it's a UNIQUE index (we don't want to remove those)
                    cursor.execute("""
                        SELECT i.indexrelid, i.indisunique
                        FROM pg_indexes pgi
                        JOIN pg_class c ON c.relname = pgi.indexname
                        JOIN pg_index i ON i.indexrelid = c.oid
                        WHERE pgi.schemaname = 'public' 
                        AND pgi.indexname = %s
                    """, [index_name])
                    
                    result = cursor.fetchone()
                    if result and not result[1]:  # Not unique, safe to remove
                        cursor.execute(f'DROP INDEX IF EXISTS {index_name}')
                        print(f"✅ Removed redundant index: {index_name}")
                        removed_count += 1
                    else:
                        print(f"⚠️  Skipped {index_name} - it's a UNIQUE index (should not be removed)")
                        skipped_count += 1
                else:
                    print(f"ℹ️  Index {index_name} does not exist (already removed)")
            except Exception as e:
                print(f"⚠️  Error processing index {index_name}: {e}")
        
        print(f"\nSummary: Removed {removed_count} redundant indexes, skipped {skipped_count}")


def reverse_remove_indexes(apps, schema_editor):
    """
    Reverse migration - recreate the indexes.
    Note: This is not recommended as the indexes are redundant,
    but included for migration reversibility.
    """
    db_engine = connection.settings_dict.get('ENGINE', '')
    
    if 'postgresql' not in db_engine:
        return
    
    with connection.cursor() as cursor:
        # Recreate the indexes (not recommended, but for reversibility)
        indexes_to_recreate = [
            ('personas_pe_numero__8c4625_idx', 'numero_documento'),
            ('personas_pe_telefon_c9eac3_idx', 'telefono'),
        ]
        
        for index_name, column_name in indexes_to_recreate:
            try:
                # Check if index already exists
                cursor.execute("""
                    SELECT 1 FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND indexname = %s
                """, [index_name])
                
                if not cursor.fetchone():
                    cursor.execute(f"""
                        CREATE INDEX {index_name} 
                        ON personas_persona ({column_name})
                    """)
                    print(f"Recreated index: {index_name}")
            except Exception as e:
                print(f"Error recreating index {index_name}: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('personas', '0010_alter_persona_municipio'),
    ]

    operations = [
        # Remove redundant indexes from database
        migrations.RunPython(
            remove_redundant_indexes,
            reverse_remove_indexes,
        ),
        # Update Django's state to reflect the removed indexes
        migrations.RemoveIndex(
            model_name='persona',
            name='personas_pe_numero__8c4625_idx',
        ),
        migrations.RemoveIndex(
            model_name='persona',
            name='personas_pe_telefon_c9eac3_idx',
        ),
    ]

